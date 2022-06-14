"""
Definition of views.
"""

from django.shortcuts import render, redirect, get_object_or_404, \
    get_list_or_404, Http404, HttpResponse
import json
from datetime import datetime, timedelta
from django.db import transaction
from django.http import HttpRequest
from .models import User, UserManager, Group, AttributeGroupInfo, MailInformation
from .forms import MailInformationForm
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
    user = User.objects.filter(email=form.cleaned_data["email"]).first()
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
    mailInfo.hash_address = hash_address
    mailInfo.tmp_password = pass1 + pass2 + pass3
    mailInfo.username = form.cleaned_data["username"]
    mailInfo.save()

    body = "一時用パスワードを配布します。ここに記載されているパスワードをフォームに入力してください。セキュリティの都合から、制限時間は10分とします。\r\n\r\n" \
           "パスコード：\r\n" + pass2 + pass3 + "\r\n\r\n" \
                                          "注意：別端末でログインを試行しようとした場合はリセットされます。その場合は再度最初からやり直してください。\r\n\r\n" \
                                          "重要：ログイン処理を行なっていないのにメールが確認できた場合、外部からの不正なログイン試行の可能性があります。メールアドレスの変更を推奨します。"

    subject = "Kanatalk ユーザー登録の確認"

    util.send_mail(body, subject, mailInfo.email)

    return HttpResponse(json.dumps({"Result": "OK", "ErrorCode": "200", "data": {
        "PassPrefix": pass1,
        "PassCenter": pass2,
        "Id": mailInfo.id
    }}))
