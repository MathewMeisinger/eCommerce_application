from django.urls import path
from products.api.views import create_product, list_products, list_reviews

urlpatterns = [
    path('', list_products),
    path('<int:product_id>/reviews/', list_reviews, name='api-list-reviews'),
    path('create/<int:store_id>/', create_product),
]
