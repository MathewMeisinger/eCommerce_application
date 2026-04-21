from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework import status

from products.models import Product
from products.api.serializers import ProductSerializer
from stores.models import Store
from integrations.twitter import tweet_new_product

from products.models import Review
from products.api.serializers import ReviewSerializer


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def create_product(request, store_id):
    """Create a new product through the API for a vendor-owned store."""
    if not request.user.is_vendor:
        return Response({"error": "Vendors only"}, status=403)

    store = Store.objects.filter(id=store_id, owner=request.user).first()
    if not store:
        return Response({"error": "Invalid store"}, status=404)

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save(store=store)

        # Post to X/Twitter after a product is created successfully via the API.
        tweet_new_product(product.id)

        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['GET'])
def list_products(request):
    """Return all active products as serialized API data."""
    products = Product.objects.filter(is_active=True)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def list_reviews(request, product_id):
    """Return all reviews for a specific product."""
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    reviews = product.reviews.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
