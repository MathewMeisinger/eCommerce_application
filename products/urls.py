from django.urls import path
from .views import (
    ProductCreateView, ProductUpdateView, ProductDeleteView,
    ProductDetailView, ProductListView
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('store/<int:store_id>/add/', ProductCreateView.as_view(), name='product-add'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product-edit'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
]
