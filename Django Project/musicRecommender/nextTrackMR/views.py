from django.shortcuts import render
from django.http import HttpResponseRedirect

# fetching track data from Spotify API
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Create your views here.
def index(request):

    input_tracks = request.session.get('input_tracks', [])
    return render(request, 'nextTrackMR/index.html', {'tracks': input_tracks})


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


# def removeTrack(request, track_id):
#     if 'input_tracks' in request.session:
#         if track_id in request.session['input_tracks']:

#             request.session['input_tracks'].remove(track)
#             request.session.modified = True
#         else:
#             print("Your track is not in the input list of tracks")
#     return HttpResponseRedirect("/")
        

def removeTrack(request, track_id):
    if 'input_tracks' in request.session:
        for track in request.session['input_tracks']:
            if track.get('id') == track_id:     #remove the matching track
                request.session['input_tracks'].remove(track)
                request.session.modified = True
        else:
            print("Your track is not in the input list of tracks")
    return HttpResponseRedirect("/")
