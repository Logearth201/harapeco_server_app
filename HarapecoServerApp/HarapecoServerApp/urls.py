"""
Definition of urls for HarapecoServerApp.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views, views_group


urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    path('signup/api', views.register_mail_api, name='register_mail_api'),
    path('groups/all', views_group.groups_all, name='groups_all'),
    path('groups/show/<slug:group_id>', views_group.groups_show, name='groups_show'),
    path('groups/member/<slug:group_id>', views_group.groups_member, name='groups_member'),
    path('groups/create', views_group.groups_create, name='groups_create'),
    path('groups/delete', views_group.groups_delete, name='groups_delete'),
    path('groups/join/member', views_group.group_join_register, name='group_join_register'),
    path('groups/join/admin', views_group.group_join_admin, name='group_join_admin'),
]
