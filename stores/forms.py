from django import forms
from .models import Store


class StoreForm(forms.ModelForm):
    """
    Form for completing the store information
    """

    class Meta:
        model = Store
        fields = ['name', 'description']
