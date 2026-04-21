from rest_framework import serializers
from products.models import Product
from products.models import Review


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'store', 'name', 'description', 'price', 'stock']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'comment', 'is_verified']
