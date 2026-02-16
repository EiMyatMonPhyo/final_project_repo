from django.shortcuts import render
from django.db.models import Case, When, Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
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
    preferences = request.session.get('preferences', {'energy_weight': "Medium", 'tempo_weight': "Medium"})       #set to medium if nothing is selected
    print ("Current values : \n Input Tracks : " , input_tracks,"\n Recommended track : ", recommended_track,"\n Preference : ", preferences)
    return render(request, 'nextTrackMR/home.html', {'all_tracks': all_tracks,'input_tracks': input_tracks, 'recommended_track': recommended_track, 'preferences': preferences})
    
    # delete if new UI is working
    # return render(request, 'nextTrackMR/index.html', {'tracks': input_tracks, 'recommended_track': recommended_track, 'preferences': preferences})


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

def convert_weight_input(value):
    if value == 'High':
        weight = 1.2
    elif value == 'Medium':
        weight = 1.0
    elif value == 'Low':
        weight = 0.8
    print ("weight convert to ", weight)
    return weight

#  preference settings
def updatePreference(request):
    # create sesssion var for preferences if not done yet.
    if 'preferences' not in request.session:
        request.session['preferences'] = {'energy_weight': "Medium", 'tempo_weight': "Medium"}

    preferences = request.session['preferences'].copy()
    # get energy value
    if 'energy_weight'in request.POST:
        preferences['energy_weight'] = convert_weight_input(request.POST['energy_weight'])
        print('energy: ', preferences['energy_weight'])

    # get tempo value
    if 'tempo_weight' in request.POST:
        preferences['tempo_weight'] = convert_weight_input(request.POST['tempo_weight'])
        print('tempo: ', preferences['tempo_weight'])
    
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
            else:
                print("Your track is not in the input list of tracks")
    return redirect(request.META.get('HTTP_REFERER', '/'))


############## to delete ############
# # get a list of track ids from a list of input tracks details(dict)
# def get_input_track_id_list(input_tracks_list):
#     input_track_ids = []
#     for track in input_tracks_list:
#         trackId = track.get('id')
#         input_track_ids.append(trackId)
#     return input_track_ids


# get artists of the recommended track
def get_artists_list(recommendation):
    linkedArtistIds = TrackArtistLink.objects.filter(track=recommendation.track_id).values_list('artist', flat=True)      # get the track's artist id
    artists = Artist.objects.filter(artist_id__in=linkedArtistIds).values_list('artist_name', flat=True)
    return list(artists)

def recommend(request):
    print("recommend")
    
    # create session variable 'recommended_track' 
    if 'recommended_track' not in request.session: 
        request.session['recommended_track'] = {}

    # create session variable 'preferences' with default values (in case, user does not give any input for preferences) 
    if 'preferences' not in request.session:
        request.session['preferences'] = {'energy_weight' : 1.0, 'tempo_weight': 1.0} 

    # get input track data from session storage
    
    input_track_ids = request.session['input_tracks']


    # get input user preference from session storage
    if 'preferences' in request.session:
        preferences = request.session['preferences']
    
    # recommender logic 
    recommendation = recommend_Euclidean(input_track_ids, preferences)

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

    return redirect(request.META.get('HTTP_REFERER', '/'))



# # add track 
# def addTrack(request):
#     # get the input (track id) from the form (frontend UI)
#     trackId = request.POST.get("input_track_id")

#     input_track_ids = None       

#     # spotify object
#     sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
#         client_id="47dc85eef7e04cd1bc31b8eeff714f8d",
#         client_secret="2b2b7edc77c44b79b63db43deba0fce8"
#     ))

#     # create session variable for 'input_tracks' 
#     if 'input_tracks' not in request.session: 
#         request.session['input_tracks'] = []       #set empty list if session variable 'input_tracks' is defined yet
    
#     # to avoid (no input of trackId and click Add button) case
#     if trackId:
#         # need to fetch data from spotify
#         try: 
#             ############################################################################
#             # need to check if the track id is valid id ?? and handle unvalid id well.#
#             ############################################################################
#             # fetch artist data
            
#             track = sp.track(trackId)
#             # fetch track artists
#             artist_names = [artist['name'] for artist in track['artists']]       # list of artists of the track

#             # fetch track name 
#             track_name = track['name']

#             #fetch track audio features
#             ###########################Track analysis from RapidAPI - https://rapidapi.com/soundnet-soundnet-default/api/track-analysis/####
#             # url = "https://track-analysis.p.rapidapi.com/pktx/spotify/" + trackId

#             # headers = {
#             #     "x-rapidapi-host": "track-analysis.p.rapidapi.com",
#             #     "x-rapidapi-key": "6e52410f81msh22e5b8dfb5de60ap1faf36jsnf5281c13f3e1"
#             # }

#             # response = requests.get(url, headers=headers)

#             # print(response.json())
#             # print(response.status_code)
#             ##############################################################################################################################
           
#             print(artist_names)
#             print(track_name)

#             # the data we need for displaying on the UI
#             trackDetails = {
#                 'id' : trackId,
#                 'name' : track['name'],
#                 'first_artist': track['artists'][0]['name']
#                 # more feature to be added 
#             }

#         except Exception as e:
#             print("Error:", e)

#         # if not able to fetch, say wrong input

#         request.session['input_tracks'].append(trackDetails)        # add to input_tracks
#         request.session.modified = True

#     print (request.session['input_tracks'])
#     input_track_ids = request.session['input_tracks']
#     return HttpResponseRedirect('/')

        
# # remove track
# def removeTrack(request, track_id):
#     if 'input_tracks' in request.session:
#         for track in request.session['input_tracks']:
#             if track.get('id') == track_id:     #remove the matching track
#                 request.session['input_tracks'].remove(track)
#                 request.session.modified = True
#             else:
#                 print("Your track is not in the input list of tracks")
#     return HttpResponseRedirect("/")