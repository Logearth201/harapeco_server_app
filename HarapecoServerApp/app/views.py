"""
Definition of views.
"""

from django.shortcuts import render, redirect, get_object_or_404, \
    get_list_or_404, Http404, HttpResponse
import json
from datetime import datetime
from django.http import HttpRequest
from .models import User, UserManager, Group, AttributeGroupInfo

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

        return HttpResponse(json.dumps({"Result": "OK", "ErrorCode": "200", "Groups": groups_json_grouptag}))
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({"Result": "NG", "ErrorCode": "500"}))
    
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

        return HttpResponse(json.dumps({"Result": "OK", "ErrorCode": "200", "Groups": groups_json_grouptag}))
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({"Result": "NG", "ErrorCode": "500"}))

# グループを表示する
def groups_show(request, group_id):
    try:
        group = Group.objects.get_or_none(id=group_id, is_delete=False)
        if group is None:
            return HttpResponse(json.dumps({"Result": "NG", "ErrorCode": "404"}))

        return HttpResponse(json.dumps({"Result": "OK", "ErrorCode": "200", "Group": {
            "Name": group.name,
            "Explain": group.explain,
            "Score": group.score
            }}))
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({"Result": "NG", "ErrorCode": "500"}))