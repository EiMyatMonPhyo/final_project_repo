from rest_framework import serializers
from .models import *

class PreferenceSerializer(serializers.Serializer):
    energy_weight = serializers.FloatField(required=False, min_value=0.5, max_value=1.5, default=1.0)
    tempo_weight = serializers.FloatField(required=False, min_value=0.5, max_value=1.5, default=1.0)

class RecommenderInputSerializer(serializers.Serializer):
    track_ids = serializers.ListField(child=serializers.CharField(required=True, allow_blank=False, max_length=22))
    preferences = PreferenceSerializer(required=False)

class TrackIdRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['track_id']

# example api input##
# {
#   "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2"],
#   "preferences": {
#     "energy_weight": 1.2,
#     "tempo_weight": 1.0
#   }
# }