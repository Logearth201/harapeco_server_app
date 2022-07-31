from django.urls import path
from rootbox import views

urlpatterns = [
    path('draw', views.rootbox_draw, name='rootbox_draw'),
    path('list/<slug:term_id>', views.rootbox_drawable_list, name='rootbox_drawable_list'),
]

