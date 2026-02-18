from django.shortcuts import render
from django.db.models import Case, When, Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
from .models import *
from .recommenderLogic import *

# fetching track data from Spotify API
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials 

# get the input tracks from db, based on the ipnut_tracks order.
def get_input_tracks_in_order(request):
    
    input_track_ids = request.session.get('input_tracks', [])      # get input track ids

    # eg : https://www.geeksforgeeks.org/python/how-to-fetch-database-records-in-the-same-order-as-an-array-of-ids-in-django/
    # Create a list of When conditions based on the input_track_ids list 
    whens = [When(track_id=id_val, then=pos) for pos, id_val in enumerate(input_track_ids)]

    # Fetch the records and order them using Case and When
    input_tracks = Track.objects.filter(track_id__in=input_track_ids).order_by(Case(*whens))
    return input_tracks

# Create your views here.
def index(request):
    # request.session.flush()
    all_tracks = getAllTracks(request)      # get all avaiable tracks

    input_tracks = get_input_tracks_in_order(request)


    recommended_track = request.session.get('recommended_track', None)
    print("##################", type(recommended_track))
    preferences = request.session.get('preferences', {'energy_weight': "Medium", 'tempo_weight': "Medium"})       #set to medium if nothing is selected
    print ("Current values : \n Input Tracks : " , input_tracks,"\n Recommended track : ", recommended_track,"\n Preference : ", preferences)
    return render(request, 'nextTrackMR/home.html', {'all_tracks': all_tracks,'input_tracks': input_tracks, 'recommended_track': recommended_track, 'preferences': preferences})
    

def searchTracks(request):
    # create input_tracks sessionVar if not exists, get value in it.
    input_track_ids = request.session.get('input_tracks', [])
    input_tracks = get_input_tracks_in_order(request)
    recommended_track = request.session.get('recommended_track', None)
    preferences = request.session.get('preferences', {'energy_weight': "Medium", 'tempo_weight': "Medium"})       #set to medium if nothing is selected

    if request.method == 'GET':
        keyword = request.GET.get('q')  #get form input
        if keyword != '':       # if anything is typed in the form
            searchResults = Track.objects.filter(
                Q(fixed_track_name__icontains=keyword) |        # track name filtering
                Q(artist__artist_name__icontains=keyword)       # artist name filtering
            ).exclude(  
                track_id__in=input_track_ids        # no input id included
            ).distinct()            # only distinct, no duplicate
        else:
            searchResults = getAllTracks(request)
        
    
        return render(request, 'nextTrackMR/home.html', {'all_tracks': searchResults,'input_tracks': input_tracks, 'recommended_track': recommended_track, 'preferences': preferences})


# get all the tracks in the database to display them
def getAllTracks(request):

    # create input_tracks sessionVar if not exists, get value in it.
    input_track_ids = request.session.get('input_tracks', [])

    # get all the tracks with their artists without the tracks already selected, Order the tracks by its fixed track name
    tracks = Track.objects.all().exclude(track_id__in = input_track_ids).prefetch_related('artist_set').order_by('fixed_track_name')
 
    return tracks 


# add track 
def addTrack(request, track_id):

    # create session variable for 'input_tracks' 
    if 'input_tracks' not in request.session: 
        request.session['input_tracks'] = []       #set empty list if session variable 'input_tracks' is defined yet
    
    request.session['input_tracks'].append(track_id)        # add to input_tracks
    request.session.modified = True

    print (request.session['input_tracks'])
    return redirect(request.META.get('HTTP_REFERER', '/'))


#  preference settings
def updatePreference(request):
    # create sesssion var for preferences if not done yet.
    if 'preferences' not in request.session:
        request.session['preferences'] = {'energy_weight': "Medium", 'tempo_weight': "Medium"}

    preferences = request.session['preferences'].copy()

    preferences['energy_weight'] = request.POST['energy_weight']
    preferences['tempo_weight'] = request.POST['tempo_weight']

    # update to session storage
    request.session['preferences'] = preferences
    request.session.modified = True
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
    
        
# remove track
def removeTrack(request, track_id):
    if 'input_tracks' in request.session:
        for id in request.session['input_tracks']:
            if id == track_id:     #remove the matching track
                request.session['input_tracks'].remove(id)
                request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', '/'))

# get artists of the recommended track
def get_artists_list(recommendation):
    linkedArtistIds = TrackArtistLink.objects.filter(track=recommendation.track_id).values_list('artist', flat=True)      # get the track's artist id
    artists = Artist.objects.filter(artist_id__in=linkedArtistIds).values_list('artist_name', flat=True)
    return list(artists)


def recommend(request):
    print("recommend")

    # create session variable 'input_tracks' 
    input_track_ids = request.session.get('input_tracks', [])
   
    # input track ids are inputted.
    if input_track_ids: 
        

        # create session variable 'preferences' with default values (in case, user does not give any input for preferences) 
        if 'preferences' not in request.session:
            request.session['preferences'] = {'energy_weight' : "Medium", 'tempo_weight': "Medium"} 
        # get input track data from session storage
        
        

        # get input user preference from session storage, change it to numerical number
        if 'preferences' in request.session:
            preferences = request.session['preferences']

            pref_mapping = {
                "High": 1.2,
                "Medium": 1.0,
                "Low": 0.8
            }

            numeric_preferences = {
                "energy_weight": pref_mapping[preferences["energy_weight"]],
                "tempo_weight": pref_mapping[preferences["tempo_weight"]],
            }

            print ("Numeric Preference : ", numeric_preferences)
            print("PREFERENCES:", preferences)
            print("TYPE:", type(preferences["energy_weight"]))

        # recommender logic 
        recommendation = recommend_Euclidean(input_track_ids, numeric_preferences)

        # get artists of the recommended track
        artists = get_artists_list(recommendation)

        recommended_track = {
            'trackId' : recommendation.track_id,
            'trackName': recommendation.fixed_track_name,
            'artists' :  artists
        }

        print ("recommended : ",recommended_track)

        request.session['recommended_track'] = recommended_track            # use session to store recommended track

        print(recommended_track['trackId'], "& ", recommended_track['trackName'] )
        for artist in recommended_track['artists']:
            print ("artist : ", artist)
    else:   # no input tracks are selected yet & recommend btn is clicked. show Error msg.
        messages.error(request, "Add tracks to playlist before recommendation.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

