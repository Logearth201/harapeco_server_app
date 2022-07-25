from django.urls import path
from election import views

urlpatterns = [
    path('list', views.get_can_election_list, name='get_can_election_list'),
    path('candidates/<slug:election_unit_id>', views.get_election_unit_candidate, name="get_election_unit_candidate"),
    path('submit', views.set_election_state, name='set_election_state'),
]

