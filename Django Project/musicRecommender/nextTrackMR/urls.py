from django.urls import include, path
from . import views
from . import api

urlpatterns = [
    path('', views.index, name='index'),
    path('add_to_inputs/<str:track_id>/', views.addTrack, name='add_track'),
    path('remove_from_inputs/<str:track_id>/', views.removeTrack, name='remove_track'),
    path('recommend/', views.recommend, name='recommend_track'),
    path('update_preference/', views.updatePreference, name='update_preference'),
    path('search_tracks/', views.searchTracks, name='search_tracks'),
    path('reset_all_tracks/', views.reset_all_tracks, name='reset_all_tracks'),
    path('api/recommend/', api.recommendTrackId, name='recommend_track_api'),

    # baseline
    path('api/recommend/baseline/cosine/', api.recommendTrackIdCosine, name='recommend_track_cosine_api'),
    path('api/recommend/baseline/random_by_artist/', api.recommendTrackIdRandomByArtist, name='recommend_track_random_api'),
    path('api/recommend/baseline/random/', api.recommendTrackIdRandom, name='recommend_track_random1_api'),
    
]