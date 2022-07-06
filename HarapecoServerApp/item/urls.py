from django.urls import path
from item import views

urlpatterns = [
    path('stamp/list', views.stamp_list, name='stamp_list'),
]
