from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import *
from .recommenderLogic import *

# fetching track data from Spotify API
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Create your views here.
def index(request):
    # request.session.flush()
    input_tracks = request.session.get('input_tracks', [])
    recommended_track = request.session.get('recommended_track', None)
    preferences = request.session.get('preferences', {'energy_weight': "Medium", 'tempo_weight': "Medium"})       #set to medium if nothing is selected
    print ("Current values : " , input_tracks, recommended_track, preferences)
    return render(request, 'nextTrackMR/index.html', {'tracks': input_tracks, 'recommended_track': recommended_track, 'preferences': preferences})


# add track 
def addTrack(request):
    trackId = request.POST.get("input_track_id")
    input_track_ids = None


    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id="47dc85eef7e04cd1bc31b8eeff714f8d",
        client_secret="2b2b7edc77c44b79b63db43deba0fce8"
    ))

    if 'input_tracks' not in request.session: 
        request.session['input_tracks'] = []       #set empty list if session variable 'input_tracks' is defined yet
    
    # to avoid (no input of trackId and click Add button) case
    if trackId:
        # need to fetch data from spotify
        try: 
            ############################################################################
            # need to check if the track id is valid id ?? and handle unvalid id well.#
            ############################################################################
            # fetch artist data
            
            track = sp.track(trackId)
            artist_names = [artist['name'] for artist in track['artists']]       # list of artists of the track

            # fetch track name 
            track_name = track['name']

            #fetch track audio features
            ###########################Track analysis from RapidAPI - https://rapidapi.com/soundnet-soundnet-default/api/track-analysis/####
            # url = "https://track-analysis.p.rapidapi.com/pktx/spotify/" + trackId

            # headers = {
            #     "x-rapidapi-host": "track-analysis.p.rapidapi.com",
            #     "x-rapidapi-key": "6e52410f81msh22e5b8dfb5de60ap1faf36jsnf5281c13f3e1"
            # }

            # response = requests.get(url, headers=headers)

            # print(response.json())
            # print(response.status_code)
            ##############################################################################################################################
           
            print(artist_names)
            print(track_name)

            trackDetails = {
                'id' : trackId,
                'name' : track['name'],
                'first_artist': track['artists'][0]['name']
                # more feature to be added 
            }

        except Exception as e:
            print("Error:", e)

        # if not able to fetch, say wrong input

        request.session['input_tracks'].append(trackDetails)        # add to input_tracks
        request.session.modified = True

    print (request.session['input_tracks'])
    input_track_ids = request.session['input_tracks']
    return HttpResponseRedirect('/')

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
    
    return HttpResponseRedirect('/')
    
        
# remove track
def removeTrack(request, track_id):
    if 'input_tracks' in request.session:
        for track in request.session['input_tracks']:
            if track.get('id') == track_id:     #remove the matching track
                request.session['input_tracks'].remove(track)
                request.session.modified = True
        else:
            print("Your track is not in the input list of tracks")
    return HttpResponseRedirect("/")


def recommend(request):
    print("recommend")
    
    if 'recommended_track' not in request.session: 
        request.session['recommeded_track'] = {}

    if 'preferences' not in request.session:
        request.session['preferences'] = {'energy_weight' : 1.0, 'tempo_weight': 1.0} 

    # get input track data from session storage
    if 'input_tracks' in request.session:
        input_track_ids = []
        for track in request.session['input_tracks']:
            trackId = track.get('id')
            input_track_ids.append(trackId)
            print("trackId : ", trackId)
    
    else: 
        return HttpResponseRedirect('/')

    # get input user preference from session storage
    if 'preferences' in request.session:
        preferences = request.session['preferences']
        print("preferences passed to Recommendation : ", preferences['energy_weight'], preferences['tempo_weight'])

    
    # recommender logic here
    recommendation = recommend_Euclidean(input_track_ids, preferences)

    # ranndom recommendation
    # recommendation = Track.objects.order_by('?').first()        # randomly shuffle the rows and select first one.
    linkedArtistIds = TrackArtistLink.objects.filter(track=recommendation.track_id).values_list('artist', flat=True)      # get the track's artist id
    artists = Artist.objects.filter(artist_id__in=linkedArtistIds).values_list('artist_name', flat=True)

    recommended_track = {
        'trackId' : recommendation.track_id,
        'trackName': recommendation.fixed_track_name,
        'artists' :  list(artists)
    }

    request.session['recommended_track'] = recommended_track            # use session to store recommended track

    print(recommended_track['trackId'], "& ", recommended_track['trackName'] )
    for artist in recommended_track['artists']:
        print ("artist : ", artist)

    return HttpResponseRedirect('/')

