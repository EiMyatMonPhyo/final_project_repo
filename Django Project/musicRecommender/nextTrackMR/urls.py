from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_to_inputs/', views.addTrack, name='add_track'),
    path('remove_from_inputs/<str:track_id>', views.removeTrack, name='remove_track'),
]