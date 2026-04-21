from django import forms
from .models import Product, Review


class ProductForm(forms.ModelForm):
    """
    Form used by vendors to create or update a product
    """
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock']


class ReviewForm(forms.ModelForm):
    '''
    A view that allows the user to write a review for the product
    Provides a size and placeholder
    '''
    class Meta:
        model = Review
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your review here...'})
        }
