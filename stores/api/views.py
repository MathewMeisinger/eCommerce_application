from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework import status

from stores.models import Store
from stores.api.serializers import StoreSerializer
from integrations.twitter import tweet_new_store


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def create_store(request):
    """Create a store through the API for an authenticated vendor."""
    if not request.user.is_vendor:
        return Response(
            {"error": "Only vendors may create stores"},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = StoreSerializer(data=request.data)
    if serializer.is_valid():
        store = serializer.save(owner=request.user)

        # Post to X/Twitter after a store is created successfully via the API.
        tweet_new_store(store.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_stores(request):
    """Return all stores as serialized API data."""
    stores = Store.objects.all()
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)
