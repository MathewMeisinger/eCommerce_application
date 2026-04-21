from django.urls import path
from stores.api.views import create_store, list_stores

urlpatterns = [
    path('', list_stores, name='api-store-list'),
    path('create/', create_store, name='api-store-create'),
]
