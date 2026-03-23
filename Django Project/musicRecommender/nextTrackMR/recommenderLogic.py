import json
import numpy as np

from collections import Counter #for frequency of artist ids
import random
from rest_framework.response import Response
from rest_framework import status
from .models import *


################### Euclidean model related ############################
"""
    input : list of input track ids
    output : list of finalized vectors of those tracks
    function : find the corresponding vectors of the track ids in the database. put them in a list and return that list
"""
def get_track_vectors_from_database(input_track_ids):
    
    input_vectors = []

    # find the songs in the database
    for track_id in input_track_ids:
        try:
            track = Track.objects.get(track_id = track_id)       # track 
    
        except Track.DoesNotExist:
            raise ValueError("One or more track IDs not found")

        input_vectors.append(np.array(json.loads(track.finalized_vector)))            # json array to python list

    return input_vectors

"""
    input : two vectors
    output : euclidean distance between them
    function : euclidean distance calculation
"""
def calculate_Euclidean(vector1, vector2):
    result = np.linalg.norm(vector1 - vector2)
    return result 
    

"""
    input : comparison_results (list of tuples (Track obj, its comparison result), k value(amount of recommendations), higher (higher to lower order[Cosine] or lower to higher order[Euclidean]))
    output : a list of recommended tracks by the model
    function : sort the comparison results in descending order (descending (higher to lower where higher : True) : 10 to 1 & ascending (lower to higher where higher : False)), 
                take k (if k is greater than the available tracks in db, just take only the amount of exisitng available numbers of tracks)
                find the top 10 tracks obj from the sorted comparison_results list
                return that list of top 10
"""
# top 10 track objects
def get_top_tracks(comparison_results, k, higher=True):
    comparison_results.sort(key=lambda x: x[1], reverse=higher)       # sort it in descending order
    k = min(k, len(comparison_results))     # rare but just incase, the number of comparison results (number of availble tracks) is less then k
    top_k_tracks = [comparison_results[i][0] for i in range(k)] # ith tuple's 0 index (track obj)
    return top_k_tracks


"""
    input : all_dist_scores (the list of all tracks' similarity scores)
    output: the list of normalized scores
    function : apply min-max normalization to input list
"""
def normalize_Euclidean(all_dist_scores):
    if not all_dist_scores:
        raise ValueError("No distance scores provided")
    
    maximum = max(all_dist_scores)
    minimum = min(all_dist_scores)
    norm_scores_list = []
    for score in all_dist_scores:
        if maximum == minimum:
            norm_scores_list.append(1.0)
        else: 
            min_max = (score - minimum)/ (maximum - minimum)            # use min-max normalization formula
            norm_scores_list.append(1-min_max)      # since the smaller euclidean score, the better, applying (1 - min-max) mean larger euclidean will have smaller reward & smaller euclidean will have larger reward.
    return norm_scores_list



"""
    input : candidate artists (a list of a candidate track's artists), input_artists_frequency (a Counter obj/ dict of artist id as key and its frequency as value)
    output : candidate score (how many of input artists are matched?)
    function : for each candidate artist, if matching artist is in input_tracks, reward that artist based on artist frequency in input artists. return how many of input artists are matched 
"""
# reward the track with matching artists
def reward_track_by_matching_artists(candidate_artists, input_artists_frequency):
    # edge case handling (in case input_artists_frequency is empty)
    if not input_artists_frequency:
        return 0
       
    score = 0
    # for every artist in candidate_artists list, 
    for candidate_artist in candidate_artists:
        # check the frequency in input_artists_frequency, 
        if candidate_artist in input_artists_frequency:
            #if the artist is in input_artists_frequency, the artist appears in input_artists, so reward that based on its frequency
            score += input_artists_frequency[candidate_artist] 

    # the number of input tracks artists
    sum_of_all_freq = sum(input_artists_frequency.values())
    
    # handling rare edge case, (denominator to be non zero)
    if sum_of_all_freq == 0:
        return 0
    
    # number of matching artists / number of all input artists = (how many of input artists are matched)
    score_by_candidate_artist = score/sum_of_all_freq
    return score_by_candidate_artist

"""
    input : pref (pref input dict), eligible_tracks (the list of all tracks objects in database)
    output : the list of eligible tracks after filtering based on preferences
    function : take pref, filter based on the preferences, return the list of eligible track objects
"""
# pref filtering 
def filter_tracks_by_pref(pref, eligible_tracks):
    # get the data from dict
    energy_input = pref.get("energy_input")    
    tempo_input = pref.get("tempo_input")

    # ranges for High, Medium, Low for energy and tempo
    energy_range = {        # range defined in dict
        'High' : (0.7, 1.0),      # pref as key , tuple as value
        'Medium' : (0.3, 0.7),
        'Low' : (0, 0.3)
    }

    tempo_range = {
        'High' : (130, 200),
        'Medium' : (100, 130),
        'Low' : (0, 100)
    }

    # filtering based on energy and tempo pref input 
    if energy_input:   # if energy_input exists, filter
        eligible_tracks = eligible_tracks.filter(energy__range=energy_range[energy_input])        # based on input, filter the tracks to only include the tracks in input range

    if tempo_input:     # if tempo_input exists, filter
        eligible_tracks = eligible_tracks.filter(tempo__range=tempo_range[tempo_input])        # based on input, filter the tracks to only include the tracks in input range

    return eligible_tracks


"""
    input : input_track_ids (the list of input track ids), input_preferences (the dictionary of preference input), k (the number recommendation to be made)
    output : the list of recommended track objects
    function : recommender logic using Euclidean
"""
################### Euclidean model related (Used in api.py)############################
def recommend_Euclidean_topk(input_track_ids, input_preferences = None, k = 1):

    valid_pref = ['High', 'Medium', 'Low']

    # for null input tracks
    if not input_track_ids:
        raise ValueError("No input tracks provided")
    
    #list of artist ids of every input tracks (for artist similarity)
    artist_ids = get_artist_ids_list(input_track_ids)

    
    # get the artist ids and their corresponding frequency    
    artist_frequency = get_artist_id_freq(artist_ids)


    # find finalized vectors of the input track ids in the database
    input_vectors = get_track_vectors_from_database(input_track_ids)

    # find average vector
    avg_vector = np.mean(input_vectors, axis=0)      #column wise

    # Euclidean (find the matching track)
    # Find the other valid songs in the database (excluding input tracks)
    all_tracks = Track.objects.exclude(track_id__in = input_track_ids)      # the list of all tracks in the database to be compared to the target vector
    eligible_tracks = all_tracks        # if not defined, later eligible_tracks may not exist (due to pref if cases)

    # if the preference is inputted, filter the tracks based on input
    if input_preferences: 
        energy = input_preferences.get("energy_input")
        tempo = input_preferences.get("tempo_input")

        # check if input_pref energy and tempo are valid values
        if energy and energy not in valid_pref:
            raise ValueError("Invalid energy preference")

        if tempo and tempo not in valid_pref:
            raise ValueError("Invalid tempo preference")

        eligible_tracks = filter_tracks_by_pref(input_preferences, eligible_tracks)
        
    # if filtering is too strict and no track left, raise error
    if not eligible_tracks.exists():
        raise ValueError("No tracks match the given preferences. No recommendation Available")

    # get the list of distances between each valid song and target vector
    comparison_results = []     # comparison results to be stored in this array
    
    euclidean_scores = [] # euclidean scores to be stored in this list, (needed to normalize with min-max normalization)
    # for every track (excluding the ones the user inputs), check the similarity with Euclidean
    for t in eligible_tracks:        
        vector = t.finalized_vector     # vector of the current track of the database
        euclidean = calculate_Euclidean(avg_vector, np.array(json.loads(vector)))
        euclidean_scores.append(euclidean)

    # normalization of euclidean scores
    normalized_E_scores = normalize_Euclidean(euclidean_scores)

    for index, t in enumerate(eligible_tracks):    
        normalized_euclidean =  normalized_E_scores[index]       
        # calculate artist similarity
        # get list of candidate artist ids
        links = TrackArtistLink.objects.filter(track= t)        # link table objects
        candidate_artists = list(links.values_list('artist_id', flat=True))     #candidate artist ids in a list
        artist_score = reward_track_by_matching_artists(candidate_artists, artist_frequency)       # get artist score

        euclidean_weight = 0.75    # (75%)
        artist_weight = 0.25      # (25%)
        final_score = normalized_euclidean * euclidean_weight + artist_score * artist_weight


        comparison_results.append((t, final_score))        # store to the array

    top_tracks = get_top_tracks(comparison_results, k)

    return top_tracks


# baseline models

################################ Cosine model related############################################

"""
    input : 2 vectors (target and other song vector)
    output : cosine similarity value output
    function : calculate Cosine Similarity and return the result
"""
def calculate_Cosine(vector1, vector2):
    result = np.dot(vector1, vector2)/ (np.linalg.norm(vector1) * np.linalg.norm(vector2))
    return result



# Cosine similarity based recommendation logic
def recommend_Cosine_topk(input_track_ids, input_preferences = None, k=1):

    valid_pref = ['High', 'Medium', 'Low']
    # for null input tracks
    if not input_track_ids:
        raise ValueError("No input tracks provided")
    
  

    #list of artist ids of every input tracks (for artist similarity)
    artist_ids = get_artist_ids_list(input_track_ids)

    
    # get the artist ids and their corresponding frequency    
    artist_frequency = get_artist_id_freq(artist_ids)


    # find finalized vectors of the input track ids in the database
    input_vectors = get_track_vectors_from_database(input_track_ids)



    # find average vector
    avg_vector = np.mean(input_vectors, axis=0)      #column wise
    
    # Find the other valid songs in the database (excluding input tracks)
    all_tracks = Track.objects.exclude(track_id__in = input_track_ids)      # the list of all tracks in the database to be compared to the target vector
    eligible_tracks = all_tracks

    
    
    # if the preference is inputted, filter the tracks based on input
    if input_preferences: 
        energy = input_preferences.get("energy_input")
        tempo = input_preferences.get("tempo_input")

        # check if input_pref energy and tempo are valid values
        if energy and energy not in valid_pref:
            raise ValueError("Invalid energy preference")

        if tempo and tempo not in valid_pref:
            raise ValueError("Invalid tempo preference")

        eligible_tracks = filter_tracks_by_pref(input_preferences, eligible_tracks)

    # if filtering is too strict and no track left, raise error
    if not eligible_tracks.exists():
        raise ValueError("No tracks match the given preferences")



    # get the list of distances between each valid song and target vector
    comparison_results = []     # comparison results to be stored in this array
    # for every track (excluding the ones the user inputs), check the similarity with Euclidean
    for t in eligible_tracks:    
        # calculate cosine similarity
        vector = t.finalized_vector     # vector of the current track of the database
        cosine = calculate_Cosine(avg_vector, np.array(json.loads(vector)))

        # calculate artist similarity
        # get list of candidate artist ids
        links = TrackArtistLink.objects.filter(track= t)        # link table objects
        candidate_artists = list(links.values_list('artist_id', flat=True))     #candidate artist ids in a list
        artist_score = reward_track_by_matching_artists(candidate_artists, artist_frequency)       # get artist score

        cosine_weight = 0.75        # (75%)
        artist_weight = 0.25       # (25%)
        final_score = cosine * cosine_weight + artist_score * artist_weight

        comparison_results.append((t,final_score))        # store (track_obj, its result) tuple to the array


    # for evaluation, top 10 tracks will be used, so, here, we will recommend 10 tracks
    top_tracks = get_top_tracks(comparison_results, k)
    
    return top_tracks 


#################### Random by artist model related ############################
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
            trackArtistLinks = TrackArtistLink.objects.filter(track = track)     # link table instance
            # for each instance of trackArtistLink, we put the corresponding artist id to the artistIds
            for link in trackArtistLinks:
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
        # get artist ids and their corresponding frequency
        artist_frequency = Counter(artist_ids)          # returned : like a dict ->  {artistId : frequency, artistId : frequency, ...}
        return artist_frequency
    else:       # no artist ids in the input list, None is returned as (artist: frequency) pair
        return None


"""
    input : artist_frequency (Counter object (dictionary) : {"artist_id" : freq, "artist_id" : freq})
    output : ranking by freq : a list of tuples [("artist_id" : freq),("artist_id" : freq)]
    function : take a counter obj, find the ranking of frequency using Counter's most_common method, and return the result (list of tuple)
"""
# get the ranking of artist frequency
def get_artist_frequency_ranking(artist_frequency):
    sorted_artist = artist_frequency.most_common()      # get descending order of ranking for artist frequemcy (most_common is Counter's method)
    return sorted_artist

"""
    input : chosen_artist_id (string of artist id), input_track_ids (a list track ids user inputted), recommended_tracks(a list of Track objects which are already in the recommendation list)
    output : a list of tracks by the chosen_artist_id
    function : get the artist instance via artist id, 
                get the Track instances of that artist
                but exclude the tracks that are already in the input_track_ids and recommended_tracks
"""
# get a random track object related to the input artist id
def get_list_of_random_track_rows_of_chosen_artist(chosen_artist_id, input_track_ids, recommended_tracks):
    try: 
        # find tracks of the chosen artist
        chosen_artist_object = Artist.objects.get(artist_id = chosen_artist_id)     # get artist row with chosen artist id
        #get Track instances whose related artist rows have chosen artist id (not include the tracks in user input tracks list and tracks already included in recommended_tracks list
        tracks_by_chosen_artist = Track.objects.filter(trackartistlink__artist = chosen_artist_object).exclude(track_id__in = input_track_ids).exclude(track_id__in = [t.track_id for t in recommended_tracks])  

        return list(tracks_by_chosen_artist)

    except Exception as e:
        raise ValueError(f"Error getting track : {e}")

"""
    input : tracks (a list of tracks eligible to be added to the recommended_tracks), recommended_tracks(a list of recommended tracks (Num of tracks in it does not reach to k yet), k (the amount of tracks to be recommended))
    output : the list of recommended tracks (amount of tracks may or may not reach k)
    function : check if the number of tracks in recommended_tracks has reached k, if not, add tracks from tracks to recommended_tracks
"""
# add tracks to recommended_tracks list
def add_tracks_to_recommended_tracks_list(tracks, recommended_tracks, k):
    for t in tracks:
        if len(recommended_tracks) < k:     # it does not reach k , so, add more
            recommended_tracks.append(t)
        else:       # if k is reached, stop adding to the list
            break
    return recommended_tracks       # return the recommended tracks list

"""
    input : input_tracks_id (the list of input tracks user gives), recommended_tracks (the list of recommended tracks)
    output : list of tracks in database (excluding input tracks and recommended tracks)
    function : get Track instances which are not included in user input tracks and tracks already in recommended_tracks, return the list of those Track instances
"""
# get random tracks (non repeating : no user input tracks , no recommended tracks)
def get_non_repeating_random_tracks(input_tracks_id, recommended_tracks):
    # exclude the tracks in input , and tracks already in recommended tracks list, get other tracks 
    remaining_tracks = Track.objects.exclude(track_id__in = input_tracks_id).exclude(track_id__in = [t.track_id for t in recommended_tracks]).order_by('?')
    return list(remaining_tracks)


# get random Track object of most frequent artist by input tracks list
def recommend_random_by_artist_topk(input_track_ids, k=1):

    # for null input tracks
    if not input_track_ids:
        raise ValueError("No input tracks provided")
    
    #list of artist ids of every input tracks
    artist_ids = get_artist_ids_list(input_track_ids)

    # get the artist ids and their corresponding frequency    
    artist_frequency = get_artist_id_freq(artist_ids)

    recommended_tracks = [] # to store the recommendations

    if artist_frequency:
        # get descending order of ranking for artist frequemcy (most freq => at the top)
        sorted_artist_freq = get_artist_frequency_ranking(artist_frequency)

        for artist_id, freq in sorted_artist_freq:

            if (len(recommended_tracks) >= k):
                break
            
            # get the songs by current artist  
            tracks_by_artist = get_list_of_random_track_rows_of_chosen_artist(artist_id, input_track_ids, recommended_tracks)
            
            random.shuffle(tracks_by_artist)        # shuffle the tracks cuz it may be the same song for the artist 
            
            # add the elements from tracks_by_artists to recommended tracks list
            recommended_tracks = add_tracks_to_recommended_tracks_list(tracks_by_artist, recommended_tracks, k)

    # if we are here (all artists are looped, so all of their tracks are added to the recommended_tracks),
    # and recommended_tracks does not have k-amount of tracks,
    # then just add random tracks

    # check if length of recommended_tracks does not reach to k
    if (len(recommended_tracks) < k):
        remaining_tracks = get_non_repeating_random_tracks(input_track_ids, recommended_tracks)

        recommended_tracks = add_tracks_to_recommended_tracks_list(remaining_tracks, recommended_tracks, k)
    return recommended_tracks
    

############################ random model related ################################
def recommend_random_topk(input_track_ids, k=1):
    # for null input tracks
    if not input_track_ids:
        raise ValueError("No input tracks provided")
    
    for track_id in input_track_ids:
        if not Track.objects.filter(track_id= track_id).exists():        # if input track is not in database, shows error
            raise ValueError("Track not found")
        
    recommended_tracks = []

    if(len(recommended_tracks) < k):
        remaining_tracks = get_non_repeating_random_tracks(input_track_ids, recommended_tracks)
        recommended_tracks = add_tracks_to_recommended_tracks_list(remaining_tracks, recommended_tracks, k)
    return recommended_tracks


