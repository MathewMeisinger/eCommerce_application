from django.urls import path
from .views import (
    VendorStoreListView, StoreCreateView, StoreUpdateView,
    StoreDeleteView, StoreDetailView
)

urlpatterns = [
    path('vendor/', VendorStoreListView.as_view(), name='vendor-stores'),
    path('vendor/create/', StoreCreateView.as_view(), name='store-create'),
    path('vendor/<int:pk>/', StoreDetailView.as_view(), name='store-detail'),
    path('vendor/<int:pk>/edit/', StoreUpdateView.as_view(), name='store-edit'),
    path('vendor/<int:pk>/delete/', StoreDeleteView.as_view(), name='store-delete'),
]
