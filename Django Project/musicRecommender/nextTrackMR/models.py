from django.db import models

# Create your models here.

class Track(models.Model):
    track_id = models.CharField(max_length=22, primary_key=True)   # number of char in Spotify track id is 22. (ref : https://stackoverflow.com/questions/37980664/spotify-track-id-features))
    track_name = models.CharField(max_length=500)       # to store original track name in dataset
    fixed_track_name = models.CharField(max_length=500)         # to store processed track name in dataset (this is done for simpler UI display)
    danceability = models.FloatField()
    energy = models.FloatField()
    valence = models.FloatField()
    acousticness = models.FloatField()
    tempo = models.FloatField()
    instrumentalness = models.FloatField()
    loudness = models.FloatField()
    normalized_vector = models.JSONField()
    finalized_vector = models.JSONField()

    def __str__(self):
        return self.track_id + " : " + self.track_name

class Artist(models.Model):
    artist_id = models.CharField(max_length=22, primary_key=True) 
    artist_name = models.CharField(max_length=50)
    track = models.ManyToManyField(Track, through='TrackArtistLink')

    def __str__(self):
        return self.artist_id + " : " + self.artist_name

class TrackArtistLink(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)