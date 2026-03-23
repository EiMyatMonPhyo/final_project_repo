from rest_framework import serializers
from .models import *

class PreferenceSerializer(serializers.Serializer):
    choices = ['High', 'Medium', 'Low']
    energy = serializers.ChoiceField(choices=choices, required=False)
    tempo = serializers.ChoiceField(choices=choices, required=False)

class RecommenderInputSerializer(serializers.Serializer):
    track_ids = serializers.ListField(child=serializers.CharField(required=True, allow_blank=False, max_length=22),min_length=1)
    preferences = PreferenceSerializer(required=False)

class TrackIdRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['track_id']

