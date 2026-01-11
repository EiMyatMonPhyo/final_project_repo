import json
import numpy as np
from rest_framework.response import Response
from rest_framework import status
from .models import *

"""
    input : list of input track ids
    output : list of finalized vectors of those tracks
    function : find the corresponding vectors of the track ids in the database. put them in a list and return that list
"""
def get_track_vectors_from_database(input_track_ids):
    
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
            raise ValueError("One or more track IDs not found")

        input_vectors.append(np.array(json.loads(track.finalized_vector)))            # json array to python list

    print ("hellow i am hrere : ", input_vectors)
    return input_vectors

"""
    input : average vector (of all input tracks' vectors), input energy weight value, input tempo weight value
    output : the weighted vector 
    function : average vector is applied weighting with energy and tempo weight input, and return the resulting weighted vector
"""
def weight_vector(avg_vector, energy_weight, tempo_weight):
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
    return avg_vector

"""
    input : two vectors
    output : euclidean distance between them
    function : euclidean distance calculation
"""
def calculate_Euclidean(vector1, vector2):
    result = np.linalg.norm(vector1 - vector2)
    return result 

# def get_Euclidean_distance(all_tracks, target_vector):
#     comparison_results = []     # comparison results to be stored in this array
    
#     # for every track (excluding the ones the user inputs), check the similarity with Euclidean
#     for track in all_tracks:        
#         vector = track.finalized_vector     # vector of the current track of the database
#         euclidean = calculate_Euclidean(target_vector, np.array(json.loads(vector)))
#         comparison_results.append(euclidean)        # store to the array

#     print (comparison_results)
#     return comparison_results

"""
    input : list of calculated Euclidean distances 
    output : the index number with minimum Euclidean distance value
    function : find index with minimum distance and return index
"""
def get_track_index_with_minimum_distance(comparison_results):
    
    # minimum Euclidean value
    min_Euclidean = np.min(comparison_results)
    print ("Minimum value is ", min_Euclidean)

    # finding the index with minimum value of euclidean result
    for index, result in enumerate(comparison_results):
        if (result == min_Euclidean):
            print("minimun value is found at index ", index , " : ", result)
            min_index = index
            break
    
    return min_index
    
  

def recommend_Euclidean(input_track_ids, input_preferences):

    # for null input tracks
    if not input_track_ids:
        raise ValueError("No input tracks provided")
    
    # for null input preferences 
    if input_preferences is None:
        input_preferences = {"energy_weight": 1.0, "tempo_weight": 1.0}
    
    print ("YOUR INPUTS ARE AS FOLLOWS : ")
    print ("input tracks : ")
    
    for trackId in input_track_ids:
        print (trackId)

    print ("User Preference", input_preferences["energy_weight"], " energy weight , ", input_preferences["tempo_weight"], " tempo weight.")
    print ("==================================")

    ########## recommender logic (Euclidean) ##############

    # find finalized vectors of the input track ids in the database
    input_vectors = get_track_vectors_from_database(input_track_ids)



    # find average vector
    avg_vector = np.mean(input_vectors, axis=0)      #column wise
    print (avg_vector)



    # get preferences
    energy_weight = input_preferences["energy_weight"]
    tempo_weight = input_preferences["tempo_weight"]
    
    # weighting with user preferences
    target_vector = weight_vector(avg_vector, energy_weight, tempo_weight)
    


    # Euclidean (find the matching track)
    # Find the other valid songs in the database (excluding input tracks)
    all_tracks = Track.objects.exclude(track_id__in = input_track_ids)      # the list of all tracks in the database to be compared to the target vector
    


    # get the list of distances between each valid song and target vector
    comparison_results = []     # comparison results to be stored in this array
    # for every track (excluding the ones the user inputs), check the similarity with Euclidean
    for track in all_tracks:        
        vector = track.finalized_vector     # vector of the current track of the database
        euclidean = calculate_Euclidean(target_vector, np.array(json.loads(vector)))
        comparison_results.append(euclidean)        # store to the array
    print (comparison_results)
    


    # get index of track with minimum distance
    min_index = get_track_index_with_minimum_distance(comparison_results)
    


    # find the matching track's data in database
    print ("the matching track : ", all_tracks[min_index])      # the same index of all tracks list
    track = all_tracks[min_index]



    # choose random track
    # # track = Track.objects.order_by('?').first()
    return track



# baseline models

"""
    input : 2 vectors (target and other song vector)
    output : cosine similarity value output
    function : calculate Cosine Similarity and return the result
"""
def calculate_Cosine(vector1, vector2):
    result = np.dot(vector1, vector2)/ (np.linalg.norm(vector1) * np.linalg.norm(vector2))
    return result


"""
    input : list of distances (cosine)
    output : index with closest to 1 cosine distance value
    function : find the index with closest to 1 cosine distance value and returns that index
"""
def get_closest_to_one_index(comparison_results):
    closestToOne = 0
    closestToOneIndex = None
    for index, result in enumerate(comparison_results):
        if (result >= 0 and result <= 1):       #within the range 0-1
            if (closestToOne < result):         # if new value is larger than closestToOne, 
                closestToOne = result           # replace closestToOne with larger new value
                closestToOneIndex = index       # replace closestToOneIndex with index
    return closestToOneIndex


# Cosine similarity based recommendation logic
def recommend_Cosine(input_track_ids, input_preferences):
    # for null input tracks
    if not input_track_ids:
        raise ValueError("No input tracks provided")
    
    # for null input preferences 
    if input_preferences is None:
        input_preferences = {"energy_weight": 1.0, "tempo_weight": 1.0}



    # find finalized vectors of the input track ids in the database
    input_vectors = get_track_vectors_from_database(input_track_ids)



    # find average vector
    avg_vector = np.mean(input_vectors, axis=0)      #column wise
    print (avg_vector)



    # get preferences
    energy_weight = input_preferences["energy_weight"]
    tempo_weight = input_preferences["tempo_weight"]
    
    # weighting with user preferences
    target_vector = weight_vector(avg_vector, energy_weight, tempo_weight)


    # Find the other valid songs in the database (excluding input tracks)
    all_tracks = Track.objects.exclude(track_id__in = input_track_ids)      # the list of all tracks in the database to be compared to the target vector
    

    
    # get the list of distances between each valid song and target vector
    comparison_results = []     # comparison results to be stored in this array
    # for every track (excluding the ones the user inputs), check the similarity with Euclidean
    for track in all_tracks:        
        vector = track.finalized_vector     # vector of the current track of the database
        cosine = calculate_Cosine(target_vector, np.array(json.loads(vector)))
        comparison_results.append(cosine)        # store to the array
    print (comparison_results)

    # get the index with cosine distance closest to 1
    closestToOneIndex = get_closest_to_one_index(comparison_results)

   
    # find the matching track's data in database
    print ("the matching track : ", all_tracks[closestToOneIndex])      # the same index of all tracks list
    track = all_tracks[closestToOneIndex]



    # choose random track
    # # track = Track.objects.order_by('?').first()
    return track 


def recommend_random_by_artist(input_track_ids, input_preferences):
    pass