from django.contrib import admin
from .models import *


class TrackArtistLinkInLine(admin.TabularInline):
    model = TrackArtistLink
    extra = 2

class TrackAdmin(admin.ModelAdmin):
    list_display = ('track_id', 'track_name', 'danceability', 'energy', 'valence', 'acousticness', 'tempo', 'instrumentalness', 'loudness', 'normalized_vector', 'finalized_vector')
    
    inlines = [TrackArtistLinkInLine]

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('artist_id', 'artist_name')

admin.site.register(Track, TrackAdmin)
admin.site.register(Artist, ArtistAdmin)


