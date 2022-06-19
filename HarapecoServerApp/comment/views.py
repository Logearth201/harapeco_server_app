from django.shortcuts import render
from .models import UserComment, GroupTopic, GroupTopicComment
from app.models import User, UserManager, Group
from util import apiutil, util
from .forms import CommentCreationForm

# Create your views here.
def user_comment_submit(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = CommentCreationForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # 投稿対象のユーザーを特定する
        target_user = User.objects.get_or_none(id=form.cleaned_data["id"])
        if user is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})
    
        # コメントを追加する
        comment = UserComment()
        comment.user = user
        comment.submit_user = target_user
        comment.text = form.cleaned_data["text"]
        comment.save()

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def get_user_comment(request, user_id):
    try:
        # ユーザーを特定する
        user = User.objects.get_or_none(id=user_id)
        if user is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # コメントを取得
        comments = UserComment.objects.filter(user=user, is_delete=False)
        comments_obj = []
        for comment in comments:
            comments_obj.append({
                "ID": comment.id,
                "Text": comment.text,
                "FromUser": comment.submit_user.id,
                "Good": comment.good_cnt,
                "Bad": comment.bad_cnt
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Comments": comments_obj})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def get_group_topics(request, group_id):
    try:
        # ユーザーを特定する
        group = Group.objects.get_or_none(id=group_id)
        if group is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # トピックを取得
        topics = GroupTopic.objects.filter(group=group, is_delete=False)
        topics_json = []
        for topic in topics:
            topics_json.append({
                "ID": topic.id,
                "Name": topic.topic_name,
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Topics": topics_json})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})