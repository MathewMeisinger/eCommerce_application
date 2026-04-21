from django import forms


class CartAddForm(forms.Form):
    """
    Class for updating item quantity in the cart
    Default set to 1
    """
    product_id = forms.IntegerField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(min_value=1, initial=1)
