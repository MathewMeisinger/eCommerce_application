from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from .forms import ProfileUpdateForm


def register(request):
    """
    Display and process registration for buyer and vendor accounts.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """
    Display the profile of the currently logged-in user.
    """
    return render(request, 'accounts/profile.html', {'user_obj': request.user})


@login_required
def profile_update(request):
    """Allow the logged-in user to update their profile details."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile_update.html', {'form': form})


@login_required
def profile_delete(request):
    """Delete the logged-in user's account after confirmation."""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('home')

    return render(request, 'accounts/profile_delete_confirm.html')
