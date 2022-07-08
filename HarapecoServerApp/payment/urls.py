from django.urls import path
from payment import views

urlpatterns = [
    path('diamond/get', views.get_diamonds, name='get_diamonds'),
    path('diamond/buy/menu/<slug:platform_id>', views.get_buy_menu, name='get_buy_menu'),
]

