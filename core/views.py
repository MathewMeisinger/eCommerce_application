from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from stores.models import Store
from products.models import Product


@login_required
def home(request):
    """Route authenticated users to the correct dashboard by role."""
    user = request.user

    if not request.user.is_authenticated:
        products = Product.objects.filter(is_active=True)
        return render(request, 'index.html', {
            'is_authenticated': False,
            'products': products,
        })

    # Vendors see only the stores they own.
    if user.role == 'vendor':
        stores = Store.objects.filter(owner=user)
        return render(request, 'vendor/vendor_home.html', {
            'stores': stores,
        })

    # Buyers see active products and can optionally filter by a search term.
    if user.role == 'buyer':
        query = request.GET.get('q')
        if query:
            products = Product.objects.filter(name__icontains=query,
                                              is_active=True)
        else:
            products = Product.objects.filter(is_active=True)
        return render(request, "buyer/buyer_home.html", {
            'products': products,
        })
