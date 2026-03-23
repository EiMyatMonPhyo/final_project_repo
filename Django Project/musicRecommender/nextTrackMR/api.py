import json
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

from .recommenderLogic import recommend_Euclidean_topk, recommend_Cosine_topk, recommend_random_by_artist_topk, recommend_random_topk

def make_recommendation(request, recommend_function, use_pref=True):
    try:        # k must be integer, other values are not allowed
        k = int(request.query_params.get("k",1))        #getting k for evaluation to be passed to recommender logic (1 for no pararms passed. k if param is passed)
    except: 
        return Response({"error" : "The URL param top k 'k' must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = RecommenderInputSerializer(data=request.data)

    if k <= 0:
        return Response({"error" : "The URL param top k 'k' must be an integer greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        input_track_ids = serializer.validated_data.get('track_ids')

       
        try:
            if use_pref:        # for Euclidean or Cosine only (Other models are for evaluation purpose and don't need preference for that)
                input_preferences = serializer.validated_data.get('preferences')
                if input_preferences:        # if pref is inputted, get the data
                    input_preferences = {
                        "energy_input" : input_preferences.get('energy'), 
                        "tempo_input" : input_preferences.get('tempo')
                    }
                else:      # if pref is not inputted, set pref to None
                    input_preferences = None
                track = recommend_function(input_track_ids, input_preferences, k=k)
            else: 
                track = recommend_function(input_track_ids, k=k)

        except ValueError as e: 
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # put output to serializer
        serializer_output = TrackIdRecommendationSerializer(track, many=True)
        return Response(serializer_output.data)
    return Response (serializer.errors, status= status.HTTP_400_BAD_REQUEST)


# Main model : Euclidean
@api_view(['POST'])
def recommendTrackIdCosine(request):
    return make_recommendation(request, recommend_Cosine_topk)


# Baseline : Cosine
@api_view(['POST'])
def recommendTrackIdEuclidean(request):
    return make_recommendation(request, recommend_Euclidean_topk)

# baseline : random by artist
@api_view(['POST'])
def recommendTrackIdRandomByArtist(request):
    return make_recommendation(request, recommend_random_by_artist_topk, use_pref=False)

# baseline : random 
@api_view(['POST'])
def recommendTrackIdRandom(request):
    return make_recommendation(request, recommend_random_topk, use_pref=False)
