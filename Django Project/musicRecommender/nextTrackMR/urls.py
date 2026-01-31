from django.urls import include, path
from . import views
from . import api

urlpatterns = [
    path('', views.index, name='index'),
    path('add_to_inputs/', views.addTrack, name='add_track'),
    path('remove_from_inputs/<str:track_id>', views.removeTrack, name='remove_track'),
    path('recommend/', views.recommend, name='recommend_track'),
    path('update_preference/', views.updatePreference, name='update_preference'),

    path('api/recommend/', api.recommendTrackId, name='recommend_track_api'),
    # baseline
    path('api/recommend/baseline/cosine/', api.recommendTrackIdCosine, name='recommend_track_cosine_api'),
    path('api/recommend/baseline/random/', api.recommendTrackIdRandom, name='recommend_track_random_api')
]