import json
import numpy as np

from collections import Counter #for frequency of artist ids
import random
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

    # print (input_vectors)
    return input_vectors

"""
    input : average vector (of all input tracks' vectors), input energy weight value, input tempo weight value
    output : the weighted vector 
    function : average vector is applied weighting with energy and tempo weight input, and return the resulting weighted vector
"""
def weight_vector(avg_vector, energy_weight, tempo_weight):
    # index 1: energy
    # print ("Before weighting energy : " , avg_vector[1])
    avg_vector[1] = avg_vector[1] * energy_weight
    # print ("After weighting energy : " , avg_vector[1])


    # index 4: tempo
    # print ("Before weighting tempo : " , avg_vector[4])
    avg_vector[4] = avg_vector[4] * tempo_weight
    # print ("After weighting tempo : " , avg_vector[4])

    # this is now target vector
    # print ("After weighting : ", avg_vector)
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
    # print ("Minimum value is ", min_Euclidean)

    # finding the index with minimum value of euclidean result
    for index, result in enumerate(comparison_results):
        if (result == min_Euclidean):
            # print("minimun value is found at index ", index , " : ", result)
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
    
    # print ("YOUR INPUTS ARE AS FOLLOWS : ")
    # print ("input tracks : ")
    
    # for trackId in input_track_ids:
        # print (trackId)

    # print ("User Preference", input_preferences["energy_weight"], " energy weight , ", input_preferences["tempo_weight"], " tempo weight.")
    # print ("==================================")

    ########## recommender logic (Euclidean) ##############

    # find finalized vectors of the input track ids in the database
    input_vectors = get_track_vectors_from_database(input_track_ids)



    # find average vector
    avg_vector = np.mean(input_vectors, axis=0)      #column wise
    # print (avg_vector)



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
    # print (comparison_results)
    


    # get index of track with minimum distance
    min_index = get_track_index_with_minimum_distance(comparison_results)
    


    # find the matching track's data in database
    # print ("the matching track : ", all_tracks[min_index])      # the same index of all tracks list
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
        if (result >= -1 and result <= 1):       #within the range -1 to 1
            if (closestToOne < result):         # if new value is larger than closestToOne, 
                closestToOne = result           # replace closestToOne with larger new value
                closestToOneIndex = index       # replace closestToOneIndex with index

    if closestToOneIndex is None:
        raise ValueError("No valid cosine similarity found")
    
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
    # print (avg_vector)



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
    # print (comparison_results)

    # get the index with cosine distance closest to 1
    closestToOneIndex = get_closest_to_one_index(comparison_results)

   
    # find the matching track's data in database
    # print ("the matching track : ", all_tracks[closestToOneIndex])      # the same index of all tracks list
    track = all_tracks[closestToOneIndex]



    # choose random track
    # # track = Track.objects.order_by('?').first()
    return track 

"""
    input : list of input track ids
    output : list of related artist ids
    function : find artist ids related to the input tracks through link table and return list of artist ids
"""
def get_artist_ids_list(input_track_ids):
    artist_ids = []
    # get the list of artist ids of every input track ids
    for track_id in input_track_ids:        #for every track, find the artists. (1 track can have many artist)
        try:
            track = Track.objects.get(track_id = track_id)       # track
            print ("track is ", track)
            trackArtistLinks = TrackArtistLink.objects.filter(track = track)     # link table instance
            print ("track artist links : " , trackArtistLinks)
            # for each instance of trackArtistLink, we put the corresponding artist id to the artistIds
            for link in trackArtistLinks:
                print ("artist id is : ", link.artist_id)
                artist_ids.append(link.artist_id)

        except Track.DoesNotExist:
            raise ValueError("Track not found")
        
        except TrackArtistLink.DoesNotExist:
            raise ValueError("Artist ID not found")
    
    return artist_ids

"""
    input : list of artist ids
    output : dict of artist as key, its frequency as value
    function : use Counter obj to know how many time each artist occurs in input artist ids and returns the resulting (artist: frequency) dict
"""
# get the artist ids and their corresponding frequency
def get_artist_id_freq(artist_ids):
    # only find artists and their frequencies if input artist ids list is not null, else return None for (artist : frequency)
    if len(artist_ids) != 0:
        print ("Artist id : ", artist_ids)
        # get artist ids and their corresponding frequency
        artist_frequency = Counter(artist_ids)          # returned : like a dict ->  {artistId : frequency, artistId : frequency, ...}
        print ("Artist frequency is ", artist_frequency)
        return artist_frequency
    else:       # no artist ids in the input list, None is returned as (artist: frequency) pair
        return None

"""
    input : dict (artist : frequency)
    output : maximum frequency value an artist has in the input
    function : find max value of frequency (value part of the dict) and return the maximum freq value
"""
# get maximum frequency an artist/artists occur
def get_max_freq_of_artist(artist_frequency):
    # find max freq only when artist_frequency is not Empty. If empty, return max_frequency as 0
    if artist_frequency is not None:
        max_frequency = max(artist_frequency.values())      #find the maximum frequecy value
        print ("max : ", max_frequency)
        return max_frequency
    else:       # no freqeuncy
        return 0

"""
    input : artist_ids (a list of artist id related to input tracks), 
            artist_frequency(a dict(artist : frequency) which shows artists and their number of occurence),
            max_frequency (the biggest number an artist has appeared)
    output : list of most frequent artist ids (non-repeating)
    function : check if the artist id has the max frequency value for each artist id in the input list, if yes, add the artist id to the list to be returned. (no artist_id is repeated in the list)
"""
# get a list of top most occurring artist ids
def get_most_frequent_artists(artist_ids, artist_frequency, max_frequency):
    top_artists = []
    if len(artist_ids) != 0:    # if empty list is input, return None
        for artist_id in artist_ids:    # among artists related to input tracks
        # if an artist has max_frequency, put its id to top_artists
            if artist_frequency[artist_id] == max_frequency:
                if artist_id not in top_artists:        # only add if the artist id is not already in top_artists
                    print ("valid artist : ",artist_id)
                    top_artists.append(artist_id)
        print ("top artists : ", top_artists)
        return top_artists
    return None

"""
    input : chosen_artist_id (randomly chosen artist id), input_track_ids (list of user input tracks)
    output : random track of that chosen artist
    function : find Artist obj (related to chosen artist id), then find Track objs related to that Artist obj through link table (no user input tracks included),
               randomly choose a Track obj from those Track objs, and return that Track obj.
"""
# get a random track object related to the input artist id
def get_random_track_row_of_chosen_artist(chosen_artist_id, input_track_ids):
    try: 
        # find tracks of the chosen artist
        chosen_artist_object = Artist.objects.get(artist_id = chosen_artist_id)     # get artist row with chosen artist id
        tracks_by_chosen_artist = Track.objects.filter(trackartistlink__artist = chosen_artist_object).exclude(track_id__in = input_track_ids)  #get Track instances whose related artist rows have chosen artist id (not include the tracks in user input tracks list)

        # # choose random track from tracks of chosen artist
        track = tracks_by_chosen_artist.order_by('?').first()
        print ("track chosen : ", track)
        return track

    except:
        raise ValueError("Artist does not exist")


"""
    input : list of user input tracks (input_track_ids)
    output : random Track of most frequent artist
    function : get artist ids of input track ids, find most frequent artist, randomly choose a Track of that most frequent artist, and return that Track obj
"""
# get random Track object of most frequent artist by input tracks list
def recommend_random_by_artist(input_track_ids):

    #list of artist ids of every input tracks
    artist_ids = get_artist_ids_list(input_track_ids)

    # get the artist ids and their corresponding frequency    
    artist_frequency = get_artist_id_freq(artist_ids)

    # get most occurring artist ids
    max_frequency = get_max_freq_of_artist(artist_frequency)
    
    # get a list of top most occurring artist ids
    top_artists = get_most_frequent_artists(artist_ids, artist_frequency, max_frequency)     # list to store top occurring artists
    
    if top_artists is not None:
        # random choice from top_artists
        chosen_artist_id = random.choice(top_artists)
        print ("chosen artist id : ", chosen_artist_id) 
    else: 
        chosen_artist_id = None

    # get a random Track obj (excluding user input tracks) of the chosen artist 
    track = get_random_track_row_of_chosen_artist(chosen_artist_id, input_track_ids)

    return track