import json
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

from .recommenderLogic import recommend_Euclidean, recommend_Cosine, recommend_random_by_artist

@api_view(['POST'])
def recommendTrackId(request):
    serializer = RecommenderInputSerializer(data=request.data)

    if serializer.is_valid():
        input_track_ids = serializer.validated_data.get('track_ids')
        input_preferences = serializer.validated_data.get('preferences') or {"energy_weight" : 1.0, "tempo_weight" : 1.0}

        
        try:
            track = recommend_Euclidean(input_track_ids, input_preferences)

        except ValueError as e: 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # put output to serializer
        serializer_output = TrackIdRecommendationSerializer(track)
        return Response(serializer_output.data)
    return Response (serializer.errors, status= status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def recommendTrackIdCosine(request):
    serializer = RecommenderInputSerializer(data=request.data)

    if serializer.is_valid():
        input_track_ids = serializer.validated_data.get('track_ids')
        input_preferences = serializer.validated_data.get('preferences') or {"energy_weight" : 1.0, "tempo_weight" : 1.0}

        
        try:
            track = recommend_Cosine(input_track_ids, input_preferences)

        except ValueError as e: 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # put output to serializer
        serializer_output = TrackIdRecommendationSerializer(track)
        return Response(serializer_output.data)
    return Response (serializer.errors, status= status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def recommendTrackIdRandom(request):
    serializer = RecommenderInputSerializer(data=request.data)

    if serializer.is_valid():
        input_track_ids = serializer.validated_data.get('track_ids')

        
        try:
            track = recommend_random_by_artist(input_track_ids)

        except ValueError as e: 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # put output to serializer
        serializer_output = TrackIdRecommendationSerializer(track)
        return Response(serializer_output.data)
    return Response (serializer.errors, status= status.HTTP_400_BAD_REQUEST)

