from django.shortcuts import render
from django.http import HttpResponseRedirect

# Create your views here.
def index(request):
    input_track_ids = request.session.get('input_ids', [])
    return render(request, 'nextTrackMR/index.html', {'tracks': input_track_ids})


# add track 
def addTrack(request):
    trackId = request.POST.get("input_track_id")
    input_track_ids = None

    if 'input_ids' not in request.session: 
        request.session['input_ids'] = []       #set empty list if session variable 'input_ids' is defined yet
    
    # need to fetch data from spotify
    
    
    # if not able to fetch, say wrong input



    if trackId:
        request.session['input_ids'].append(trackId)        # add to input_ids
        request.session.modified = True

    print (request.session['input_ids'])
    input_track_ids = request.session['input_ids']
    return HttpResponseRedirect('/')


def removeTrack(request, trackId):
    if 'input_ids' in request.session:
        if trackId in request.session['input_ids']:
            request.session['input_ids'].remove(trackId)
            request.session.modified = True
        else:
            print("Your track is not in the input list of tracks")
    return HttpResponseRedirect("/")
        

