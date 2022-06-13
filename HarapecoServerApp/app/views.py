"""
Definition of views.
"""

from django.shortcuts import render, redirect, get_object_or_404, \
    get_list_or_404, Http404, HttpResponse
import json
from datetime import datetime
from django.db import transaction
from django.http import HttpRequest
from .models import User, UserManager, Group, AttributeGroupInfo
from .forms import GroupCreateForm, GroupDeleteForm, GroupJoinForm, GroupJoinAllowForm
from util import apiutil

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

# グループ全体を取得する
def groups_all(request):
    try:
        groups = Group.objects.filter(is_delete=False)
        groups_json_grouptag = []
        for group in groups:
            groups_json_grouptag.append({
                "Name": group.name,
                "Explain": group.explain,
                "Score": group.score
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Groups": groups_json_grouptag})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    
# ログインメンバーのグループの情報を取得する
def groups_user(request):
    try:
        # 現在のユーザーの取得
        user = request.user
        if not user.is_authenticated:
            return HttpResponse(json.dumps({"result": "NG", "errorCode": "401"}))
        
        # ユーザー単位でオブジェクトを検索
        group_join_infos = AttributeGroupInfo.objects.filter(user=user)

        # 所属情報.ラウンジ情報を検索する
        groups_json_grouptag = []
        for group_join_info in group_join_infos:
            if group_join_info.group.is_delete:
                continue

            groups_json_grouptag.append({
                "Name": group_join_info.group.name,
                "Explain": group_join_info.group.explain,
                "Score": group_join_info.group.score
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Groups": groups_json_grouptag})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

# グループを表示する
def groups_show(request, group_id):
    try:
        # グループを探索
        group = Group.objects.get_or_none(id=group_id, is_delete=False)
        if group is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Group": {
            "Name": group.name,
            "Explain": group.explain,
            "Score": group.score
            }})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

# グループに所属しているメンバーをすべて取得する
def groups_member(request, group_id):
    try:
        # グループを探索
        group = Group.objects.get_or_none(id=group_id, is_delete=False)
        if group is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})
        
        # グループ単位でオブジェクトを検索
        group_join_infos = AttributeGroupInfo.objects.filter(group=group)

        # 所属情報.ラウンジ情報を検索する
        groups_json_grouptag = []
        for group_join_info in group_join_infos:
            groups_json_grouptag.append({
                "ID": group_join_info.user.id,
                "UserName": group_join_info.user.username,
                "IsJoinAllowed": group_join_info.group_join_waitconfirm
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Members": groups_json_grouptag})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

# グループを作成
def groups_create(request):
    # 現在のユーザーの取得
    user = request.user
    if not user.is_authenticated:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

    # POST以外は拒否
    if request.method != "POST":
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

    # formの正当性チェック
    form = GroupCreateForm(request.POST)
    if not form.is_valid():
        return apiutil.convert_json_result(request, {"result": "NG", "ErrorCode": "403"})

    # トランザクション
    transaction.set_autocommit(False)

    try:
        # ラウンジを作成、自身をリーダーにさせる
        group = Group()
        group.name = form.cleaned_data["name"]
        group.explain = form.cleaned_data["explain"]
        group.auto_belong_group = form.cleaned_data["auto_belong"] == "1"
        group.save()

        belongs_data = AttributeGroupInfo()
        belongs_data.group_join_waitconfirm = False # 自分自身なので
        belongs_data.authentication = 0 # Master
        belongs_data.group = group
        belongs_data.user = user
        belongs_data.save()
    except Exception as e:
        print(e)
        transaction.rollback()
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    finally:
        transaction.commit()
        transaction.set_autocommit(True)

    return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Data": {"GroupID": group.id}})

# グループの削除
def groups_delete(request):
    # 現在のユーザーの取得
    user = request.user
    if not user.is_authenticated:
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})

    # POST以外は拒否
    if request.method != "POST":
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

    # formの正当性チェック
    form = GroupDeleteForm(request.POST)
    if not form.is_valid():
        return apiutil.convert_json_result(request, {"result": "NG", "ErrorCode": "403"})

    # Groupの取得
    group = Group.objects.get_or_none(id=form.cleaned_data["id"], is_delete=False)
    if group is None:
        return apiutil.convert_json_result(request, {"result": "NG", "ErrorCode": "404"})

    # トランザクション
    transaction.set_autocommit(False)

    try:
        # ラウンジを作成、自身をリーダーにさせる
        group.is_delete = True
        group.save()

        # 所属情報をすべて捨てる
        AttributeGroupInfo.objects.filter(group=group).delete()
    except Exception as e:
        print(e)
        transaction.rollback()
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
    finally:
        transaction.commit()
        transaction.set_autocommit(True)

    return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
