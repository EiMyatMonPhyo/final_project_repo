import json
import numpy as np
from rest_framework.response import Response
from rest_framework import status
from .models import *


def recommend_Euclidean(input_track_ids, input_preferences):
    print ("YOUR INPUTS ARE AS FOLLOWS : ")
    print ("input tracks : ")
    for trackId in input_track_ids:
        print (trackId)

    print ("User Preference", input_preferences["energy_weight"], " energy weight , ", input_preferences["tempo_weight"], " tempo weight.")
    print ("==================================")

    ########## recommender logic (Euclidean) ##############

    input_vectors = []

    # if, later, features are fetched from API, 
    # 1. fetch the features ['danceability', 'energy', 'valence', 'acousticness', 'tempo', 'instrumentalness', 'loudness']

    # 2. Normalize and weight (Vectors) 
    # weight_list = np.array([
    #                 1.1,  # danceability
    #                 1.4,  # energy
    #                 1.3,  # valence     
    #                 1.3,  # acousticness
    #                 1.1,  # tempo
    #                 1.2,  # instrumentalness
    #                 1.2   # loudness
    # ])


    # find the songs in the database
    for track_id in input_track_ids:
        try:
            track = Track.objects.get(track_id = track_id)       # track 
    
        except Track.DoesNotExist:
            return Response({"error": "One or more track IDs not found"}, status=status.HTTP_400_BAD_REQUEST)

        input_vectors.append(np.array(json.loads(track.finalized_vector)))            # json array to python list

    print (input_vectors)


    # find average vector
    avg_vector = np.mean(input_vectors, axis=0)      #column wise
    print (avg_vector)

    # get preferences
    energy_weight = input_preferences["energy_weight"]
    tempo_weight = input_preferences["tempo_weight"]

    # weighting with user preferences

    # index 1: energy
    print ("Before weighting energy : " , avg_vector[1])
    avg_vector[1] = avg_vector[1] * energy_weight
    print ("After weighting energy : " , avg_vector[1])


    # index 4: tempo
    print ("Before weighting tempo : " , avg_vector[4])
    avg_vector[4] = avg_vector[4] * tempo_weight
    print ("After weighting tempo : " , avg_vector[4])

    # this is now target vector
    print ("After weighting : ", avg_vector)

    # Euclidean (find the matching track)
    all_tracks = Track.objects.exclude(track_id__in = input_track_ids)      # the list of all tracks in the database to be compared to the target vector
    
    comparison_results = []     # comparison results to be stored in this array
    
    # for every track (excluding the ones the user inputs), check the similarity with Euclidean
    for track in all_tracks:        
        vector = track.finalized_vector     # vector of the current track of the database
        euclidean = np.linalg.norm(avg_vector - np.array(json.loads(vector)))     #the euclidean formula
        comparison_results.append(euclidean)        # store to the array

    print (comparison_results)

    # minimum Euclidean value
    min_Euclidean = np.min(comparison_results)
    print ("Minimum value is ", min_Euclidean)
    # finding the index with minimum value of euclidean result
    for index, result in enumerate(comparison_results):
        if (result == min_Euclidean):
            print("minimun value is found at index ", index , " : ", result)
            min_index = index
            break
    # find the matching track's data in database
    print ("the matching track : ", all_tracks[index])      # the same index of all tracks list
    track = all_tracks[index]
    return track