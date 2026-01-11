import factory
import string
import random

from .models import *

def randomTrackId():
    chars = string.ascii_letters + string.digits
    randomStr = ''      #empty
    for index in range(22):
        randomStr += random.choice(chars)
    return randomStr

def randomVector():
    randomVector = []
    for index in range(7):
        randomVector.append(random.uniform(0,1))
    return randomVector

class TrackFactory(factory.django.DjangoModelFactory):

    track_id = randomTrackId()
    track_name = "name" + track_id
    fixed_track_name = "fixed Name" + track_id
    danceability = random.uniform(0, 1)
    energy = random.uniform(0, 1)
    valence = random.uniform(0, 1)
    acousticness = random.uniform(0, 1)
    tempo = random.uniform(0, 180)
    instrumentalness = random.uniform(0, 1)
    loudness = random.uniform(-60,0)
    normalized_vector = randomVector()
    finalized_vector = randomVector()

    class Meta:
        model = Track