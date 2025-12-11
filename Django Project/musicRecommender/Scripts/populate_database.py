import os 
import sys
import django
import csv 
import ast
from collections import defaultdict



project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          #project root folder (musicRecommender)
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','musicRecommender.settings')
django.setup()

from nextTrackMR.models import *
track_data_file = os.path.join(project_root, 'tracks.csv')  # the csv file we will use to add data to database

tracks = defaultdict(list)
artists = defaultdict()
track_artists = defaultdict(set)

# read file
with open (track_data_file) as tracks_file:
    csv_reader = csv.reader(tracks_file,delimiter=',')
    header = csv_reader.__next__()      

    for index, row in enumerate(csv_reader):
        tracks[index] = row[0:9] + row[11:14]       # col 0 to 8 and col 11 to 13

        artist_ids = ast.literal_eval(row[9])            # [id, id, id]
        artist_names = ast.literal_eval(row[10])         # [name, name, name]

        for i, id in enumerate(artist_ids):
            artists[id] = artist_names[i]           #{id: name}
        
        track_artists[index] = set(artist_ids)      # {index : {artistID1, artistID2}}

Artist.objects.all().delete()
Track.objects.all().delete()
TrackArtistLink.objects.all().delete()

artist_rows = {}
track_rows = {}

# key (id), name (value)
for id, name in artists.items():
    row = Artist.objects.create(artist_id=id, artist_name=name)
    row.save()
    artist_rows[id] = row

for index, track in tracks.items():
    row = Track.objects.create(track_id=track[0], track_name=track[1], fixed_track_name=track[9],
                               danceability=track[2], energy=track[3], valence=track[4],
                               acousticness=track[5], tempo=track[6], instrumentalness=track[7],
                               loudness=track[8], normalized_vector=track[10], finalized_vector=track[11])
    
    row.save()
    track_rows[index] = row

for index, artist_ids in track_artists.items():
    for artist_id in artist_ids:
        row = TrackArtistLink.objects.create(track= track_rows[index], artist=artist_rows[artist_id])
        row.save()
