from django.urls import path
from election import views

urlpatterns = [
    path('list', views.get_can_election_list, name='get_can_election_list'),
]

