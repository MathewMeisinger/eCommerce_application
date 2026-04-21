from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView,
    DeleteView
)
from django.urls import reverse_lazy
from .models import Store
from .forms import StoreForm
from integrations.twitter import tweet_new_store


@method_decorator(login_required, name='dispatch')
class VendorStoreListView(ListView):
    """
    List all stores that belong to the logged-in vendor.
    """
    model = Store
    template_name = 'stores/store_list.html'
    context_object_name = 'stores'

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)


@method_decorator(login_required, name='dispatch')
class StoreCreateView(CreateView):
    """
    Create a new store for the logged-in vendor.
    """
    model = Store
    form_class = StoreForm
    template_name = 'stores/store_form.html'
    success_url = reverse_lazy('vendor-stores')

    def dispatch(self, request, *args, **kwargs):
        # Only vendor accounts may create stores.
        if not request.user.is_vendor:
            return redirect('permission_denied')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Attach the logged-in vendor as owner, then trigger the X post.
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        tweet_new_store(self.object.id)
        return response


@method_decorator(login_required, name='dispatch')
class StoreDetailView(DetailView):
    """
    Display one vendor-owned store and its active products.
    """
    model = Store
    template_name = 'stores/store_detail.html'
    context_object_name = 'store'

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        # Include only active products belonging to this store.
        context = super().get_context_data(**kwargs)
        store = self.get_object()
        context['products'] = store.products.filter(is_active=True)
        return context


@method_decorator(login_required, name='dispatch')
class StoreUpdateView(UpdateView):
    """
    Allow vendors to edit their own stores.
    """
    model = Store
    form_class = StoreForm
    template_name = 'stores/store_form.html'
    success_url = reverse_lazy('vendor-stores')

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)


@method_decorator(login_required, name='dispatch')
class StoreDeleteView(DeleteView):
    """Delete a store after first soft-deleting its products."""
    model = Store
    template_name = 'stores/store_confirm_delete.html'
    success_url = reverse_lazy('vendor-stores')

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Soft-delete the store's products before deleting the store itself.
        self.object.products.update(is_active=False)

        # Remove the store record once its products have been hidden.
        return super().delete(request, *args, **kwargs)
