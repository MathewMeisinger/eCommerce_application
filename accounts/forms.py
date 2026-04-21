from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class RegistrationForm(UserCreationForm):
    """
    A custom form that will allow users to register as either a 
    vendor or a buyer and will assign a role to them based
    on this choice. This role will dictate the permissions within 
    the webapplication moving forward.
    """
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(UserChangeForm):
    """
    A form that will allow a user to change information on the profile page
    if they are viewing it
    """
    password = None

    class Meta:
        model = User
        fields = ['username', 'email']
