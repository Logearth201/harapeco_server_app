from django.urls import path
from comment import views

urlpatterns = [
    path('user/submit', views.user_comment_submit, name='user_comment_submit'),
    path('user/get/<slug:user_id>', views.get_user_comment, name='get_user_comment'),
]