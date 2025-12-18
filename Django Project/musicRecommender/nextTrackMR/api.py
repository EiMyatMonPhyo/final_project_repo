from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

@api_view(['POST'])
def recommendTrackId(request):
    serializer = RecommenderInputSerializer(data=request.data)

    if serializer.is_valid():
        serializer.validated_data.get('track_ids')
        serializer.validated_data.get('preferences')

        # choose random track
        track = Track.objects.order_by('?').first()

        # put output to serializer
        serializer_output = TrackIdRecommendationSerializer(track)
        return Response(serializer_output.data)
    return Response (serializer.errors, status= status.HTTP_400_BAD_REQUEST)