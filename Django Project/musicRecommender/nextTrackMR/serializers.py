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


# example api input##
# {
#   "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2","5q21u5TzhSaJPslac3xce8", "5Klo65Y9uouLjNVDV3pqh7"],
#   "preferences": {
#     "energy_weight": 1.2,
#     "tempo_weight": 1.0
#   }
# }

# new serializer input
# {
#   "track_ids": ["4qEoqyPbLYnLOii6mKlIjI", "5lz0NiPw32Gq4kMIUJvuw2","5q21u5TzhSaJPslac3xce8", "5Klo65Y9uouLjNVDV3pqh7"],
#   "preferences": {
#     "energy": "High",
#     "tempo": "Low"
#   }
# }

# {
#   "track_ids": ["2hBJgz4Ye9MkkmBbaDTTKx", "4xkOaSrkexMciUUogZKVTS","7pFydJbDEToJHtvl6g579k"],
#   "preferences": {
#     "energy": "High",
#     "tempo": "Low"
#   }
# }

# feedback input sample
# {
#   "track_ids": ["5lWFrW5T3JtxVCLDb7etPu", "0ZfM5XfJTtFPhOxAERRnNY"],
#   "preferences": {
#     "energy_weight": 0.8,
#     "tempo_weight": 1.0
#   }
# }