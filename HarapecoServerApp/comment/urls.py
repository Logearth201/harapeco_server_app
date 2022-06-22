from django.urls import path
from comment import views

urlpatterns = [
    path('user/submit', views.user_comment_submit, name='user_comment_submit'),
    path('user/get/<slug:user_id>', views.get_user_comment, name='get_user_comment'),
    path('group/topic/get/<slug:group_id>', views.get_group_topics, name='get_group_topics'),
    path('group/topic/create', views.add_topic, name='add_topic'),
    path('group/topic/submit', views.group_topic_comment_submit, name='group_topic_comment_submit'),
]