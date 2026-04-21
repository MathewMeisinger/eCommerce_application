from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (CreateView, UpdateView, DeleteView,
                                  DetailView, ListView, View)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product
from stores.models import Store
from .forms import ProductForm, ReviewForm
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from integrations.twitter import tweet_new_product


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Allow a vendor to create a product for one of their stores."""
    model = Product
    fields = ['name', 'description', 'price', 'stock']
    template_name = 'products/product_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Only the owner of the store may add products to it.
        store = get_object_or_404(Store, id=self.kwargs['store_id'])
        if store.owner != request.user:
            return redirect('permission_denied')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Attach the product to the store from the URL, then trigger the X post.
        form.instance.store_id = self.kwargs['store_id']
        response = super().form_valid(form)
        tweet_new_product(self.object.id)
        return response

    def get_success_url(self):
        return redirect('store-detail', pk=self.kwargs['store_id']).url


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Allow the owning vendor to edit an existing product."""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Prevent users from editing products they do not own.
        product = self.get_object()
        if product.store.owner != request.user:
            return redirect('permission_denied')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('product-detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(LoginRequiredMixin, View):
    """Soft-delete a product by marking it inactive."""
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        # Only the owning vendor can remove a product from public listings.
        if product.store.owner != request.user:
            return redirect('permission_denied')

        # Soft-delete the product instead of removing the database record.
        product.is_active = False
        product.save()

        return redirect('store-detail', pk=product.store.pk)


class ProductListView(ListView):
    """List active products, optionally filtered by a search query."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(name__icontains=query)
        return qs


class ProductDetailView(FormMixin, DetailView):
    """
    Display product details, reviews, and role-specific actions.

    Buyers can add the product to their cart and leave reviews, while vendors
    who own the product can edit or soft-delete it.
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    form_class = ReviewForm

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_success_url(self):
        return reverse('product-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = self.get_object()
        context['reviews'] = product.reviews.select_related('user').all()

        # Provide a blank review form when one is not already in context.
        if 'form' not in context:
            context['form'] = self.get_form()

        # Vendors may edit or delete only products that belong to their store.
        context['can_edit'] = (
            self.request.user.is_authenticated and
            self.request.user.is_vendor and
            product.store and
            product.store.owner == self.request.user
        )

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle review submission for buyers viewing the product page.
        """
        self.object = self.get_object()
        form = self.get_form()

        if not request.user.is_buyer:
            return redirect('product-detail', pk=self.object.pk)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = self.object
            review.user = self.request.user
            review.save()
            return redirect(self.get_success_url())

        # Re-render the detail page with validation errors when submission fails.
        return self.form_invalid(form)
