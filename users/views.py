from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash

from services.models import ServiceCategory
from .models import Profile
from .forms import SignupForm, ProfileForm

# Home view
def home(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'home.html', {'categories': categories})

# Signup view
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Signup successful. Please login!")
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Try to authenticate by username
        user = authenticate(request, username=email, password=password)

        # If username fails, try email lookup
        if not user:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Wrong username or password!")

    return render(request, 'login.html')

# Logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

# Profile
@login_required
def profile_view(request):
    bookings = request.user.booking_set.all()
    return render(request, 'profile.html', {'bookings': bookings})

# Edit profile
@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Update User fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = email  # Keep username same as email
        user.save()

        # Update Profile fields
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        profile_form = ProfileForm(instance=profile)

    context = {
        'profile_form': profile_form,
        'user': request.user,
    }
    return render(request, 'edit_profile.html', context)

# Change password
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Wrong old password or passwords do not match!")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})
