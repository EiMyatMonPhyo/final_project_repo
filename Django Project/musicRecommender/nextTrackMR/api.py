import json
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

from .recommenderLogic import recommend_Euclidean, recommend_Cosine, recommend_Euclidean_topk, recommend_Cosine_topk, recommend_random_by_artist_topk, recommend_random_topk

# Main model : Euclidean
@api_view(['POST'])
def recommendTrackId(request):
    k = int(request.query_params.get("k",1))        #getting k for evaluation to be passed to recommender logic (1 for no pararms passed. k if param is passed)
    serializer = RecommenderInputSerializer(data=request.data)

    if serializer.is_valid():
        input_track_ids = serializer.validated_data.get('track_ids')
        input_preferences = serializer.validated_data.get('preferences') or {"energy_weight" : 1.0, "tempo_weight" : 1.0}

        
        try:
            track = recommend_Euclidean_topk(input_track_ids, input_preferences, k=k)

        except ValueError as e: 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # put output to serializer
        serializer_output = TrackIdRecommendationSerializer(track, many = True)
        return Response(serializer_output.data)
    return Response (serializer.errors, status= status.HTTP_400_BAD_REQUEST)

# Baseline : Cosine
@api_view(['POST'])
def recommendTrackIdCosine(request):
    k = int(request.query_params.get("k", 1))       #getting k for evaluation to be passed to recommender logic (1 for no pararms passed. k if param is passed)
    serializer = RecommenderInputSerializer(data=request.data)

    if serializer.is_valid():
        input_track_ids = serializer.validated_data.get('track_ids')
        input_preferences = serializer.validated_data.get('preferences') or {"energy_weight" : 1.0, "tempo_weight" : 1.0}

        
        try:
            track = recommend_Cosine_topk(input_track_ids, input_preferences, k=k)
            # track = recommend_Cosine(input_track_ids, input_preferences)      # one track only output (if use thing, remove many=True in serializer_output below)

        except ValueError as e: 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # put output to serializer
        serializer_output = TrackIdRecommendationSerializer(track, many=True)
        return Response(serializer_output.data)
    return Response (serializer.errors, status= status.HTTP_400_BAD_REQUEST)

# baseline : random by artist
@api_view(['POST'])
def recommendTrackIdRandom(request):
    k = int(request.query_params.get("k", 1))       #getting k for evaluation to be passed to recommender logic (1 for no pararms passed. k if param is passed)
    serializer = RecommenderInputSerializer(data=request.data)

    if serializer.is_valid():
        input_track_ids = serializer.validated_data.get('track_ids')

        
        try:
            track = recommend_random_by_artist_topk(input_track_ids, k = k)

        except ValueError as e: 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # put output to serializer
        serializer_output = TrackIdRecommendationSerializer(track, many = True)
        return Response(serializer_output.data)
    return Response (serializer.errors, status= status.HTTP_400_BAD_REQUEST)

# baseline : random 
@api_view(['POST'])
def recommendTrackIdRandom1(request):
    k = int(request.query_params.get("k", 1))       #getting k for evaluation to be passed to recommender logic (1 for no pararms passed. k if param is passed)
    serializer = RecommenderInputSerializer(data=request.data)

    if serializer.is_valid():
        input_track_ids = serializer.validated_data.get('track_ids')

        
        try:
            track = recommend_random_topk(input_track_ids, k = k)

        except ValueError as e: 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # put output to serializer
        serializer_output = TrackIdRecommendationSerializer(track, many = True)
        return Response(serializer_output.data)
    return Response (serializer.errors, status= status.HTTP_400_BAD_REQUEST)

