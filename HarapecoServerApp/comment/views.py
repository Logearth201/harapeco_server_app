from django.shortcuts import render
from .models import UserComment, GroupTopic, GroupTopicComment, GroupTopicCommentEvaluate, UserCommentEvaluate
from app.models import User, UserManager, Group, AttributeGroupInfo
from util import apiutil, util
from .forms import CommentCreationForm, GroupTopicCreationForm, GroupTopicCommentCreationForm, GroupTopicCommentEditForm, GroupTopicEditForm, GroupTopicDeleteForm, CommentDeleteForm, GroupTopicCommentEvaluateForm, CommentEvaluateForm
from django.utils import timezone
from django.db import transaction

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
        target_user = User.objects.get_or_none(id=form.cleaned_data["id"], is_active=True)
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

def user_comment_delete(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = CommentDeleteForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # 投稿コメントを特定する
        target_comment = UserComment.objects.get_or_none(id=form.cleaned_data["id"], is_delete=False)
        if target_comment is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # 投稿ユーザーor送信先ユーザーのいずれも満たさない場合はNG
        if not (target_comment.user == user or target_comment.submit_user == user):
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # コメントを追加する
        target_comment.is_delete = True
        target_comment.save()

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

def user_comment_evaluate(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = CommentEvaluateForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # セットする評価内容
        score = form.cleaned_data["score"]

        # 編集対象のコメントを特定する
        comment = UserComment.objects.get_or_none(id=form.cleaned_data["user_comment_id"], is_delete=False)
        if comment is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})
        
        # トランザクション
        transaction.set_autocommit(False)

        try:
            # 条件によって評価を変える
            evaluate = UserCommentEvaluate.objects.get_or_none(user=user, user_comment=comment)
            if evaluate is None:
                # スコアオブジェクト
                if score != "0":
                    evaluate = UserCommentEvaluate()
                    if score == "1":
                        evaluate.is_good = True
                    else:
                        evaluate.is_good = False
                    evaluate.user_comment = comment
                    evaluate.user = user
                    evaluate.save()

                # 点数評価（追加されたので）
                if score == "1":
                    comment.good_cnt += 1
                    comment.save()
                elif score == "-1":
                    comment.bad_cnt += 1
                    comment.save()
            else:
                # 事前評価を保存
                before_evaluate = evaluate.is_good

                if score == "1":
                    evaluate.is_good = True
                    evaluate.save()
                elif score == "0":
                    evaluate.delete()
                else:
                    evaluate.is_good = False
                    evaluate.save()

                # 事前評価と比較
                if score != "0":
                    if before_evaluate != evaluate.is_good:
                        if score == "1":
                            comment.good_cnt += 1
                            comment.bad_cnt -= 1
                            comment.save()
                        elif score == "-1":
                            comment.good_cnt -= 1
                            comment.bad_cnt += 1
                            comment.save()
                else:
                    if before_evaluate:
                        comment.good_cnt -= 1
                        comment.save()
                    else:
                        comment.bad_cnt -= 1
                        comment.save()
        except Exception as e:
            print(e)
            transaction.rollback()
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
        finally:
            transaction.commit()
            transaction.set_autocommit(True)
        
        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def get_group_topics(request, group_id):
    try:
        # ユーザーを特定する
        group = Group.objects.get_or_none(id=group_id, is_delete=False)
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

def edit_group_topic(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = GroupTopicEditForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # 対象のトピックを取得
        topic = GroupTopic.objects.get_or_none(id=form.cleaned_data["topic_id"], is_delete=False)
        if topic is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # 編集権限のチェック
        edit_authentication = AttributeGroupInfo.objects.get_or_none(user=user, group=topic.group, authentication=0)
        if edit_authentication is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
    
        # トピックを編集する
        topic.topic_name = form.cleaned_data["topic_name"]
        topic.is_not_belong_viewable = form.cleaned_data["free_viewable"] == "1"
        topic.save()

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def add_topic(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = GroupTopicCreationForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
        
        # 追加対象のグループを特定する
        target_group = Group.objects.get_or_none(id=form.cleaned_data["group_id"], is_delete=False)
        if target_group is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # 編集権限のチェック
        edit_authentication = AttributeGroupInfo.objects.get_or_none(user=user, group=target_group, authentication=0)
        if edit_authentication is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
    
        # トピックを追加する
        topic = GroupTopic()
        topic.group = target_group
        topic.topic_name = form.cleaned_data["topic_name"]
        topic.is_not_belong_viewable = form.cleaned_data["free_viewable"] == "1"
        topic.save()

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def delete_topic(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = GroupTopicDeleteForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # 対象のトピックを取得
        topic = GroupTopic.objects.get_or_none(id=form.cleaned_data["topic_id"], is_delete=False)
        if topic is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # 編集権限のチェック
        edit_authentication = AttributeGroupInfo.objects.get_or_none(user=user, group=topic.group, authentication=0)
        if edit_authentication is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
    
        # トピックを消す
        topic.is_delete = True
        topic.save()

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def group_topic_comment_submit(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = GroupTopicCommentCreationForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
        
        # 追加対象のグループトピックを特定する
        target_group_topic = GroupTopic.objects.get_or_none(id=form.cleaned_data["group_topic_id"], is_delete=False)
        if target_group_topic is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # 追加対象のグループを特定する
        if target_group_topic.group.is_delete:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # グループにいるかのチェック
        edit_authentication = AttributeGroupInfo.objects.get_or_none(user=user, group=target_group_topic.group)
        if edit_authentication is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
    
        # コメントを追加する
        topic_comment = GroupTopicComment()
        topic_comment.topic = target_group_topic
        topic_comment.fromuser = user
        topic_comment.text = form.cleaned_data["text"]
        topic_comment.save()

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def group_topic_comment_nonoffset(request, group_topic_id):
    return group_topic_comment(request, group_topic_id, 0)

def group_topic_comment(request, group_topic_id, offset):
    try:
        # 追加対象のグループトピックを特定する
        group_topic = GroupTopic.objects.get_or_none(id=group_topic_id, is_delete=False)
        if group_topic is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # 追加対象のグループを特定する
        if group_topic.group.is_delete:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # グループにいるかのチェック（自由に見れるようにしているなら別）
        if not group_topic.is_not_belong_viewable:
            # 未ログインは拒否
            user = request.user
            if not user.is_authenticated:
                return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
            
            # 所属してなければ拒否
            edit_authentication = AttributeGroupInfo.objects.get_or_none(user=user, group=group_topic.group)
            if edit_authentication is None:
                return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # トピックを取得
        # 順番はIDから
        offset_unit_value = 30
        comments = GroupTopicComment.objects.filter(topic=group_topic, is_delete=False).order_by("id").reverse()[int(offset):int(offset) + offset_unit_value]
        comments_json = []
        for comment in comments:
            comments_json.append({
                "ID": comment.id,
                "UserID": comment.fromuser.id,
                "UserName": comment.fromuser.username,
                "Text": comment.text,
                "GoodCnt": comment.good_cnt,
                "BadCnt": comment.bad_cnt,
                "IsEdit": comment.is_edit,
                "SubmitDateTime": comment.date_submited.strftime("%Y/%m/%d %H:%M:%S"),
                })

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "Comments": comments_json})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def group_topic_comment_edit(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = GroupTopicCommentEditForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
        
        # 編集対象のコメントを特定する
        comment = GroupTopicComment.objects.get_or_none(id=form.cleaned_data["group_topic_comment_id"], is_delete=False)
        if comment is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # グループに属していない場合は削除不可
        edit_authentication = AttributeGroupInfo.objects.get_or_none(user=user, group=comment.topic.group)
        if edit_authentication is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
        
        # ユーザーIDが不一致ならエラー
        if comment.fromuser.id != user.id:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
    
        # コメントを編集する
        comment.is_edit = True
        comment.text = form.cleaned_data["text"]
        comment.date_edited = timezone.now()
        comment.save()

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def group_topic_comment_delete(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = GroupTopicCommentEditForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
        
        # 編集対象のコメントを特定する
        comment = GroupTopicComment.objects.get_or_none(id=form.cleaned_data["group_topic_comment_id"], is_delete=False)
        if comment is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})

        # グループに属していない場合は削除不可
        edit_authentication = AttributeGroupInfo.objects.get_or_none(user=user, group=comment.topic.group)
        if edit_authentication is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
        
        # ユーザーIDが不一致なら、グループに関する管理者権限を探す。リーダーかどうかも見る。
        # それも満たさなければ削除させない。
        if comment.fromuser.id != user.id and edit_authentication.authentication != 0:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
    
        # コメントを編集する
        comment.is_delete = True
        comment.save()

        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

def group_topic_comment_evaluate(request):
    try:
        # GETは拒否
        if request.method != "POST":
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "405"})

        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # フォームを取得
        form = GroupTopicCommentEvaluateForm(request.POST)
        if not form.is_valid():
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})

        # セットする評価内容
        score = form.cleaned_data["score"]

        # 編集対象のコメントを特定する
        comment = GroupTopicComment.objects.get_or_none(id=form.cleaned_data["group_topic_comment_id"], is_delete=False)
        if comment is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "404"})
        
        # グループに属していない場合は編集不可
        edit_authentication = AttributeGroupInfo.objects.get_or_none(user=user, group=comment.topic.group)
        if edit_authentication is None:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "403"})
        
        # トランザクション
        transaction.set_autocommit(False)

        try:
            # 条件によって評価を変える
            evaluate = GroupTopicCommentEvaluate.objects.get_or_none(user=user, group_topic_comment=comment)
            if evaluate is None:
                # スコアオブジェクト
                if score != "0":
                    evaluate = GroupTopicCommentEvaluate()
                    if score == "1":
                        evaluate.is_good = True
                    else:
                        evaluate.is_good = False
                    evaluate.group_topic_comment = comment
                    evaluate.user = user
                    evaluate.save()

                # 点数評価（追加されたので）
                if score == "1":
                    comment.good_cnt += 1
                    comment.save()
                elif score == "-1":
                    comment.bad_cnt += 1
                    comment.save()
            else:
                # 事前評価を保存
                before_evaluate = evaluate.is_good

                if score == "1":
                    evaluate.is_good = True
                    evaluate.save()
                elif score == "0":
                    evaluate.delete()
                else:
                    evaluate.is_good = False
                    evaluate.save()

                # 事前評価と比較
                if score != "0":
                    if before_evaluate != evaluate.is_good:
                        if score == "1":
                            comment.good_cnt += 1
                            comment.bad_cnt -= 1
                            comment.save()
                        elif score == "-1":
                            comment.good_cnt -= 1
                            comment.bad_cnt += 1
                            comment.save()
                else:
                    if before_evaluate:
                        comment.good_cnt -= 1
                        comment.save()
                    else:
                        comment.bad_cnt -= 1
                        comment.save()
        except Exception as e:
            print(e)
            transaction.rollback()
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})
        finally:
            transaction.commit()
            transaction.set_autocommit(True)
        
        return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200"})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})

# WSから呼ばれるAPI
def is_belong_group_ws(request, group_id):
    try:
        # 未ログインは拒否
        user = request.user
        if not user.is_authenticated:
            return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "401"})
        
        # グループがなければ未所属とみなす
        group = Group.objects.get_or_none(id=group_id)
        if group is None:
            return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "IsBelong": False})
        
        # グループに属していない場合は編集不可
        edit_authentication = AttributeGroupInfo.objects.get_or_none(user=user, group=group)
        if edit_authentication is None:
            return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "IsBelong": False})
        else:
            return apiutil.convert_json_result(request, {"Result": "OK", "ErrorCode": "200", "IsBelong": True})
    except Exception as e:
        print(e)
        return apiutil.convert_json_result(request, {"Result": "NG", "ErrorCode": "500"})