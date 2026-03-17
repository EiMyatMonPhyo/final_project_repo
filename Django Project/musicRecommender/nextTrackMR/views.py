from django.shortcuts import render
from django.db.models import Case, When, Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib import messages
from .models import *
from .recommenderLogic import *

# fetching track data from Spotify API
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials 


# get the input tracks from db, based on the ipnut_tracks order.
def get_input_tracks_in_order(input_track_ids):
    
    # eg : https://www.geeksforgeeks.org/python/how-to-fetch-database-records-in-the-same-order-as-an-array-of-ids-in-django/
    # Create a list of When conditions based on the input_track_ids list 
    whens = [When(track_id=id_val, then=pos) for pos, id_val in enumerate(input_track_ids)]

    # Fetch the records and order them using Case and When
    input_tracks = Track.objects.filter(track_id__in=input_track_ids).order_by(Case(*whens))
    return list(input_tracks)


# get all the tracks in the database to display them
def getAllTracks(input_track_ids):

    # get all the tracks with their artists without the tracks already selected, Order the tracks by its fixed track name
    tracks = Track.objects.all().exclude(track_id__in = input_track_ids).prefetch_related('artist_set').order_by('fixed_track_name')
 
    return list(tracks)

# update left side's All Tracks section with updated list of all tracks (AJAX, partial html update for asynchoronous service)
def update_all_tracks_html(request, search_keyword = ''):
    # get all_tracks to send json data to frontend. (update for all Tracks section)
        
    if search_keyword:       # if anything is typed in the form
        searchResults = Track.objects.filter(
            Q(fixed_track_name__icontains=search_keyword) |        # track name filtering
            Q(artist__artist_name__icontains=search_keyword)       # artist name filtering
        ).exclude(  
            track_id__in=request.session.get('input_tracks', [])      # no input id included
        ).distinct()            # only distinct, no duplicate
        tracks_list_shown = searchResults
    else:
        all_tracks = getAllTracks(request.session.get('input_tracks', []))
        tracks_list_shown = all_tracks
    all_tracks_html = render_to_string("nextTrackMR/all_tracks.html", {"all_tracks": tracks_list_shown}, request=request)
    
    return all_tracks_html

# update right side's Your Playlist section with updated list of input tracks (AJAX, partial html update for asynchoronous service)
def update_input_tracks_html(request):
    # get input tracks data for frontend (update for "Your Playlist" section)
    input_track_ids = request.session.get('input_tracks', [])
    input_tracks = get_input_tracks_in_order(input_track_ids)
    input_tracks_html = render_to_string("nextTrackMR/input_tracks.html", {"input_tracks": input_tracks}, request=request)
    
    return input_tracks_html

# Create your views here.
def index(request):
    # request.session.flush()
    
    input_track_ids = request.session.get('input_tracks', [])
    all_tracks = getAllTracks(input_track_ids)      # get all avaiable tracks
    input_tracks = get_input_tracks_in_order(input_track_ids)

    recommended_track = request.session.get('recommended_track', None)
    preferences = request.session.get('preferences', {'energy_input': None, 'tempo_input': None})       #set to None if nothing is selected
    print ("Current values : \n Input Tracks : " , input_tracks,"\n Recommended track : ", recommended_track,"\n Preference : ", preferences)
    return render(request, 'nextTrackMR/home.html', {'all_tracks': all_tracks,'input_tracks': input_tracks, 'recommended_track': recommended_track, 'preferences': preferences})
    

def searchTracks(request):
   
    keyword = request.GET.get('q')  #get form input
    return JsonResponse({
        "search_tracks_html" : update_all_tracks_html(request, keyword)
    })





# add track 
def addTrack(request, track_id):

    # create session variable for 'input_tracks' 
    if 'input_tracks' not in request.session: 
        request.session['input_tracks'] = []       #set empty list if session variable 'input_tracks' is defined yet
    
    # eligible track ids to add
    
    # if the track id is in Track table, and is not included in input_tracks list 
    if Track.objects.filter(track_id = track_id).exists() and track_id not in request.session['input_tracks']:
        request.session['input_tracks'].append(track_id)        # add to input_tracks
        request.session.modified = True

    print (request.session['input_tracks'])
    search_keyword = request.GET.get('q')  #get form url

    response_to_frontend = {
                            "all_tracks_html": update_all_tracks_html(request, search_keyword),
                            "input_tracks_html": update_input_tracks_html(request)
                            }
    return JsonResponse(response_to_frontend)


#  preference settings
def updatePreference(request):
    # create sesssion var for preferences if not done yet.
    if 'preferences' not in request.session:
        request.session['preferences'] = {'energy_input': "None", 'tempo_input': "None"}

    preferences = request.session['preferences'].copy()

    energy = request.POST.get('energy_pref')
    tempo = request.POST.get('tempo_pref')

    preferences['energy_input'] = None if energy == "None" else energy
    preferences['tempo_input'] = None if tempo == "None" else tempo

    # update to session storage
    request.session['preferences'] = preferences
    request.session.modified = True
    return JsonResponse(preferences)
    
        
# remove track
def removeTrack(request, track_id):
    if 'input_tracks' in request.session:
        for id in request.session['input_tracks']:
            if id == track_id:     #remove the matching track
                request.session['input_tracks'].remove(id)
                request.session.modified = True

    search_keyword = request.GET.get('q')  #get form url

    response_to_frontend = {
                            "all_tracks_html": update_all_tracks_html(request, search_keyword),
                            "input_tracks_html": update_input_tracks_html(request)
                            }
    return JsonResponse(response_to_frontend)

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
            request.session['preferences'] = {'energy_input' : None, 'tempo_input': None} 
        

        # get input user preference from session storage, change it to numerical number
        preferences = request.session['preferences']

        try: 
            # recommender logic 
            recommendation = recommend_Cosine_topk(input_track_ids, preferences)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)

        # get artists of the recommended track
        artists = get_artists_list(recommendation[0])
        print ("YOUR TARGET PREF : ", "ENERGY : ", preferences["energy_input"], "TEMPO : ", preferences["tempo_input"])
        print ("RECOMMENDED TRACK'S PREF : ", "ENERGY : ", recommendation[0].energy, "TEMPO", recommendation[0].tempo)
        recommended_track = {
            'trackId' : recommendation[0].track_id,
            'trackName': recommendation[0].fixed_track_name,
            'artists' :  artists
        }

        print ("recommended : ",recommended_track)

        request.session['recommended_track'] = recommended_track            # use session to store recommended track
        request.session.modified = True

        print(recommended_track['trackId'], "& ", recommended_track['trackName'] )
        for artist in recommended_track['artists']:
            print ("artist : ", artist)
        
        recommendation_html = render_to_string("nextTrackMR/recommendation.html", {"recommended_track": recommended_track}, request=request)
        response_to_frontend = {
            "recommendation_html": recommendation_html
        }
        return JsonResponse(response_to_frontend)

    else:   # no input tracks are selected yet & recommend btn is clicked. show Error msg.
        return JsonResponse({"error": "Add tracks to playlist before recommendation."}, status=400)

# for "show all tracks" btn clicked
def reset_all_tracks (request):
    response_to_frontend = {
                            "all_tracks_html": update_all_tracks_html(request)
                            }
    return JsonResponse(response_to_frontend)