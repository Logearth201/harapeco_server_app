from django.urls import path
from comment import views

urlpatterns = [
    path('user/comment/submit', views.user_comment_submit, name='user_comment_submit'),
    path('user/comment/delete', views.user_comment_delete, name='user_comment_delete'),
    path('user/comment/evaluate', views.user_comment_evaluate, name='user_comment_evaluate'),
    path('user/get/<slug:user_id>', views.get_user_comment, name='get_user_comment'),
    path('group/topic/get/<slug:group_id>', views.get_group_topics, name='get_group_topics'),
    path('group/topic/comments/<slug:group_topic_id>', views.group_topic_comment_nonoffset, name='group_topic_comment_nonoffset'),
    path('group/topic/comments/<slug:group_topic_id>/<slug:offset>', views.group_topic_comment, name='group_topic_comment'),
    path('group/topic/create', views.add_topic, name='add_topic'),
    path('group/topic/edit', views.edit_group_topic, name='edit_group_topic'),
    path('group/topic/delete', views.delete_topic, name='delete_topic'),
    path('group/topic/comment/submit', views.group_topic_comment_submit, name='group_topic_comment_submit'),
    path('group/topic/comment/edit', views.group_topic_comment_edit, name='group_topic_comment_edit'),
    path('group/topic/comment/delete', views.group_topic_comment_delete, name='group_topic_comment_delete'),
    path('group/topic/comment/evaluate', views.group_topic_comment_evaluate, name='group_topic_comment_evaluate'),
    path('group/check/belong/<slug:group_id>', views.is_belong_group_ws, name='is_belong_group_ws'),
]