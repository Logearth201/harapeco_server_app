from time import process_time
from django.shortcuts import render, redirect, get_object_or_404, \
    get_list_or_404, Http404, HttpResponse
import json, base64
from datetime import datetime, timedelta
from django.contrib.auth import login, authenticate, logout
from django.db import transaction
from django.http import HttpRequest
from .models import User, UserManager, Group, AttributeGroupInfo, MailInformation, UserDeviceLogin, ProcessSaver, Invitation
from .forms import MailInformationForm, RegisterCompleteForm, SetTemporaryPassForm, UserLoginForm, AutoLoginForm, UserLogoutForm, UserInfoChangeForm, UserInfoChangeCompleteForm, InviteTokenForm
from util import apiutil, util

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

def register_mail_api(request):
    message = "メールアドレスを入力してください。"

    if request.method != "POST":
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

    form = MailInformationForm(request.POST)
    if not form.is_valid():
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

    # すでに登録してあるAddressがあるかどうかを判定する
    user = User.objects.filter(email=form.cleaned_data["email"], is_active=True).first()
    if user is not None:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "E001"})

    # いらないのは消す(再登録関連）
    MailInformation.objects.filter(email=form.cleaned_data["email"]).delete()

    # パスフレーズの生成
    pass1 = util.randomname(10)  # アプリを通して渡されます。
    pass2 = util.randomname(3)  # アプリ、メールを通して渡されます。
    pass3 = util.randomname(7)  # メールを通して渡されます。
    hash_address = util.randomname(100)

    mailInfo = MailInformation()
    mailInfo.email = form.cleaned_data["email"]
    mailInfo.valid_time = datetime.now() + timedelta(minutes=30)
    mailInfo.hash_address = hash_address # 使われていない
    mailInfo.tmp_password = pass1 + pass2 + pass3
    mailInfo.username = form.cleaned_data["username"]
    mailInfo.save()

    body = "一時用パスワードを配布します。ここに記載されているパスワードをフォームに入力してください。セキュリティの都合から、制限時間は10分とします。\r\n\r\n" \
           "パスコード：\r\n" + pass2 + pass3 + "\r\n\r\n" \
                                          "注意：別端末でログインを試行しようとした場合はリセットされます。その場合は再度最初からやり直してください。\r\n\r\n" \
                                          "重要：ログイン処理を行なっていないのにメールが確認できた場合、外部からの不正なログイン試行の可能性があります。メールアドレスの変更を推奨します。"

    subject = "Kanatalk ユーザー登録の確認"

    util.send_mail(body, subject, mailInfo.email)

    return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "data": {
        "PassPrefix": pass1,
        "PassCenter": pass2,
        "Id": mailInfo.id
    }})

# ユーザー登録
def register_complete_api(request):
    # POST以外は禁止に
    if request.method != 'POST':
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

    # フォームを取得
    form = RegisterCompleteForm(request.POST)
    if not form.is_valid():
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

    password = form.cleaned_data["password"]
    id = form.cleaned_data["id"]

    sign_up_info = MailInformation.objects.get_or_none(id=id)
    if sign_up_info is None:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

    # サインアップ情報の存在性をチェック
    sign_up_info = MailInformation.objects.filter(id=id, tmp_password=password).first()
    if sign_up_info is None:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "E002"})

    # すでに登録してあるAddressがあるかどうかを再度判定する
    user = User.objects.filter(email=sign_up_info.email, is_active=True).first()
    if user is not None:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "E001"})

    # トランザクション
    transaction.set_autocommit(False)

    try:
        # フォームのチェック
        user = User()
        user.email = sign_up_info.email
        user.username = sign_up_info.username + "#" + util.randomname(6)
        user.save()

        # いらない仮登録情報はすべて消す。
        # 同一メールアドレスのも含めて。
        sign_up_info.delete()
        MailInformation.objects.filter(email=sign_up_info.email).delete()
    except Exception as e:
        print(e)
        transaction.rollback()
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    finally:
        transaction.commit()
        transaction.set_autocommit(True)

    # TODO：ログインさせることに！
    return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})

# 一時パスワードセット用サービス。たいていのサービスで影響があるので注意。
# メールにパスワードを一旦セットさせる。
def prepare_login_api(request):
    if request.method != "POST":
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

    form = SetTemporaryPassForm(request.POST)

    if not form.is_valid():
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

    email = form.cleaned_data.get("email")
    pass1 = util.randomname(10) # アプリを通して渡されます。
    pass2 = util.randomname(3) # アプリ、メールを通して渡されます。
    pass3 = util.randomname(8) # メール、アプリを通して渡されます。

    user = User.objects.get_or_none(email=email, is_active=True)
    if user is None:
        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "data": {"PassPrefix": pass1, "PassCenter": pass2}})

    user.set_password(pass1 + pass2 + pass3)
    user.save()

    body = "一時用パスワードを配布します。ここに記載されているパスワードをフォームに入力してください。セキュリティの都合から、制限時間は10分とします。\r\n\r\n" \
           "パスコード：\r\n" + pass2 + pass3 + "\r\n\r\n" \
           "注意：別端末でログインを試行しようとした場合はリセットされます。その場合は再度最初からやり直してください。\r\n\r\n" \
                                          "重要：ログイン処理を行なっていないのにメールが確認できた場合、外部からの不正なログイン試行の可能性があります。メールアドレスの変更を推奨します。"

    subject = "Kanatalk メールログインパスワード"

    util.send_mail(body, subject, email)

    return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "data": {"PassPrefix": pass1, "PassCenter": pass2}})

# このまま残す
def end_login_api(request):
    if request.method != "POST":
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

    form = UserLoginForm(request.POST)

    if not form.is_valid():
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

    email = form.cleaned_data.get("email")
    password = form.cleaned_data.get("password")
    push_notification_token = form.cleaned_data.get("push_notification_token")

    user = User.objects.filter(email=email, is_active=True).first()

    if user is None:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

    user = authenticate(username=user.username, password=password)
    if user is None:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
    else:
        login(request, user=user)

        # ログインが終わったら、パスワードを強制的に別のものにさせる。ただし、「１」ならば例外とする。
        if password != "1":
            user.set_password(util.randomname(500))

        # 自動ログインに必要な情報を渡す
        user_id = user.id
        auth_key = util.randomname(150)

        userDeviceLogin = UserDeviceLogin()
        userDeviceLogin.user = user
        userDeviceLogin.auth_key = auth_key
        userDeviceLogin.push_notification_token = push_notification_token
        userDeviceLogin.save()

        response = apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "data": {
            "userID": user_id,
            "authKey": auth_key
        }})

        return response

# 各イベントに実装させる自動ログインの仕組み(user/isauthenticateを継承させる)
def auto_login(request):
    if request.method != "POST":
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

    form = AutoLoginForm(request.POST)

    if not form.is_valid():
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

    # formから値をセット
    user_id = form.cleaned_data["user_id"]
    auth_key = form.cleaned_data["auth_key"]
    push_notification_token = form.cleaned_data["push_notification_token"]

    # ユーザー情報の確認
    user = User.objects.filter(id=user_id, is_active=True).first()
    if user is None:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

    # 自動ログイン記録があるかどうかを調査する
    user_device_login = None
    user_device_login_list = UserDeviceLogin.objects.filter(user=user)
    user_auto_login_exist = False

    for auto_login in user_device_login_list:
        if auto_login.user.id == user.id and auth_key == auto_login.auth_key:
            user_device_login = auto_login
            break
    if user_device_login is None:
        # もしなければ例外処理
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

    # push通知のキーを書き換える
    if push_notification_token != user_device_login.push_notification_token:
        user_device_login.push_notification_token = push_notification_token
        user_device_login.save()

    # OKならば(この時点でログインは成功済み)、そのまま続行させる
    login(request, user)

    # 成功レスポンス
    response = apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "data": {
        "userID": user_id
    }})

    return response

# ログアウト用
def user_logout(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})

        # ログアウト処理
        logout(request)

        # ユーザー認証情報を消す
        form = UserLogoutForm(request.POST)

        if form.is_valid():
            auth_key = form.cleaned_data["auth_key"]

            user_device_login = UserDeviceLogin.objects.filter(user=user, auth_key=auth_key)
            user_device_login.delete()
    
        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

# ユーザー情報変更
def user_modify_begin(request):
    # POST以外は禁止に
    if request.method != 'POST':
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

    # フォームを取得
    form = UserInfoChangeForm(request.POST)
    if not form.is_valid():
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

    # 現在のユーザーの取得
    user = request.user
    if not user.is_authenticated:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
    
    # パスコードを発行
    pass1_1 = util.randomname(10)  # アプリを通して渡されます。
    pass1_2 = util.randomname(3)  # アプリ、メールを通して渡されます。
    pass1_3 = util.randomname(7)  # メールを通して渡されます。
    pass2_1 = util.randomname(10)  # アプリを通して渡されます。渡されないパターンもあります。
    pass2_2 = util.randomname(3)  # アプリ、メールを通して渡されます。渡されないパターンもあります。
    pass2_3 = util.randomname(7)  # メールを通して渡されます。渡されないパターンもあります。

    # トランザクション
    transaction.set_autocommit(False)

    try:
        # ユーザー変更情報を一旦データとして保存する
        process_saver = ProcessSaver.objects.get_or_none(user=user)
        if process_saver is None:
            process_saver = ProcessSaver()
            process_saver.user = user

        # 変更情報
        email = form.cleaned_data["email"]
        process_saver.valid_time = datetime.now() + timedelta(minutes=30)
        process_saver.data = json.dumps({
            "Email": email,
            "UserName": form.cleaned_data["username"]
            })
        process_saver.process_type = "ModifyUser"
        process_saver.password = pass1_1 + pass1_2 + pass1_3 + pass2_1 + pass2_2 + pass2_3
        process_saver.save()

        # メールアドレスの確認をせよ！
        usermail = User.objects.get_or_none(email=email)
        if usermail is not None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "E003"})

        # メールを提出する（メイン）
        body = "一時用パスワードを配布します。ここに記載されているパスワードをフォームに入力してください。セキュリティの都合から、制限時間は10分とします。\r\n\r\n" \
               "パスコード：\r\n" + pass1_2 + pass1_3 + "\r\n\r\n" \
                                              "注意：別端末でログインを試行しようとした場合はリセットされます。その場合は再度最初からやり直してください。\r\n\r\n" \
                                              "重要：ログイン処理を行なっていないのにメールが確認できた場合、外部からの不正なログイン試行の可能性があります。メールアドレスの変更を推奨します。"
        subject = "Kanatalk ユーザー情報変更の確認（メイン）"
        util.send_mail(body, subject, user.email)

        # メールアドレスが異なっているケースでは
        if user.email != email and email.strip() != "":
            body = "一時用パスワードを配布します。ここに記載されているパスワードをフォームに入力してください。セキュリティの都合から、制限時間は10分とします。\r\n\r\n" \
               "パスコード：\r\n" + pass1_2 + pass1_3 + "\r\n\r\n" \
                                              "注意：別端末でログインを試行しようとした場合はリセットされます。その場合は再度最初からやり直してください。\r\n\r\n" \
                                              "重要：ログイン処理を行なっていないのにメールが確認できた場合、外部からの不正なログイン試行の可能性があります。メールアドレスの変更を推奨します。"
            subject = "Kanatalk ユーザー情報変更の確認（サブ）"
            util.send_mail(body, subject, email)

            return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "data": {
                "PassPrefix": pass1_1,
                "PassCenter": pass1_2,
                "PassSuffix": pass2_1,
                "Id": process_saver.id,
                "IsMailAddressChange": True
            }})
        else:
            return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "data": {
                "PassPrefix": pass1_1,
                "PassCenter": pass1_2,
                "PassSuffix": pass2_1 + pass2_2 + pass2_3,
                "Id": process_saver.id,
                "IsMailAddressChange": False
            }})
    except Exception as e:
        print(e)
        transaction.rollback()
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    finally:
        transaction.commit()
        transaction.set_autocommit(True)

# ユーザー情報変更（確定）
def user_modify_end(request):
    # 現在のユーザーの取得
    user = request.user
    if not user.is_authenticated:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

    # POST以外は拒否
    if request.method != "POST":
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

    # formの正当性チェック
    form = UserInfoChangeCompleteForm(request.POST)
    if not form.is_valid():
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

    # ユーザー編集オブジェクトを取得
    process_saver = ProcessSaver.objects.get_or_none(user=user, process_type="ModifyUser")
    if process_saver is None:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

    # パスワードチェック
    if process_saver.password != form.cleaned_data["password"]:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

    # トランザクション
    transaction.set_autocommit(False)

    try:
        # ユーザー情報を強制変更
        dic = json.loads(process_saver.data)
        username = dic["UserName"]
        email = dic["Email"]

        # メールアドレスの確認をせよ！
        usermail = User.objects.get_or_none(email=email)
        if usermail is not None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "E003"})

        if username.strip() != "":
            user.username = username

        if email.strip() != "":
            user.email = email

        # 編集完了時
        user.save()

        # 編集完了したので不要なデータは削除
        process_saver.delete()
    except Exception as e:
        print(e)
        transaction.rollback()
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    finally:
        transaction.commit()
        transaction.set_autocommit(True)

    return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})

# ユーザー登録
def invitation_create(request):
    try:
        # 現在のユーザーの取得
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # invitationの追加
        # ※batchにより定期的に消されることを想定
        invitation = Invitation()
        invitation.inviter_user = user
        invitation.invite_token = util.randomname(15)
        invitation.save()

        # 招待コード(ID + USERID + TOKEN)を返す。これはbase64.b64decodeで復元可能。
        token = base64.b64encode((str(invitation.id) + "_" + str(invitation.inviter_user.id) + "_" + invitation.invite_token).encode())
        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "InvitationToken": token.decode()})
    except Exception as e:
        print(e)
        transaction.rollback()
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    finally:
        transaction.commit()
        transaction.set_autocommit(True)

def invitation_apply_afterinput(request):
    try:
        # POST以外は禁止に
        if request.method != 'POST':
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # フォームを取得
        form = InviteTokenForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # 現在のユーザーの取得
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

        # TODO：作りかけです。
        # sessionに招待コードを記録させる
        # note:ロードバランサーによるサーバー切り替えは想定しないこと。
        # note2:形式ミスや発行コードミスはエラーにすること。
        try:
            token = base64.b64decode(form.cleaned_data["token"].encode()).decode()
        except:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "400"})
        
        spliter = token.split("_")
        if len(token.split("_")) != 3:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "400"})

        invitation_id = spliter[0]
        user_id = spliter[1]
        invitation_token = spliter[2]

        invitation = Invitation.objects.get_or_none(id=invitation_id)
        if invitation is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})
        elif invitation.invite_token != invitation_token or str(invitation.inviter_user.id) != user_id:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "400"})

        # 以降、招待コード情報を適用させる


        # 成功したら招待コードを削除
        invitation.delete()
        
        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        transaction.rollback()
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    finally:
        transaction.commit()
        transaction.set_autocommit(True)


# token入力 => after token input, redirect to page.
def invitation_record(request, input_token):
    try:
        # GET以外は禁止に
        if request.method != 'GET':
            return apiutil.convert_http_result(request, {"Result": "NG", "ErrorCode": "405"})
        
        # 現在のユーザーの取得
        user = request.user
        if user.is_authenticated:
            return apiutil.convert_http_result(request, {"Result": "NG", "ErrorCode": "403"})

        # TODO：作りかけです。
        # sessionに招待コードを記録させる
        # note:ロードバランサーによるサーバー切り替えは想定しないこと。
        # note2:形式ミスや発行コードミスはエラーにすること。
        try:
            token = base64.b64decode(input_token.encode()).decode()
        except:
            return apiutil.convert_http_result(request, {"Result": "NG", "ErrorCode": "400"})
        
        spliter = token.split("_")
        if len(token.split("_")) != 3:
            return apiutil.convert_http_result(request, {"Result": "NG", "ErrorCode": "400"})

        invitation_id = spliter[0]
        user_id = spliter[1]
        invitation_token = spliter[2]

        invitation = Invitation.objects.get_or_none(id=invitation_id)
        if invitation is None:
            return apiutil.convert_http_result(request, {"Result": "NG", "ErrorCode": "404"})
        elif invitation.invite_token != invitation_token or str(invitation.inviter_user.id) != user_id:
            return apiutil.convert_http_result(request, {"Result": "NG", "ErrorCode": "400"})

        # セッションに招待コードを記録する
        request.session["invite_token"] = token
        
        return apiutil.convert_http_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        transaction.rollback()
        return apiutil.convert_http_result(request, {"Result": "NG", "ErrorCode": "500"})
    finally:
        transaction.commit()
        transaction.set_autocommit(True)