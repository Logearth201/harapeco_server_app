from django.urls import path
from rootbox import views

urlpatterns = [
    path('draw', views.rootbox_draw, name='rootbox_draw'),
]

