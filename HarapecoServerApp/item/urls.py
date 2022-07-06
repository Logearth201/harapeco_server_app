from django.urls import path
from item import views

urlpatterns = [
    path('stamp/list', views.stamp_list, name='stamp_list'),
    path('diamond/get', views.get_diamonds, name='get_diamonds'),
]
