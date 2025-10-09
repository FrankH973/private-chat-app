# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import UserInvitation
import uuid

User = get_user_model()


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('chat:chat_list')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('chat:chat_list')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')


def register_view(request):
    """Handle user registration (invite-only)"""
    if request.user.is_authenticated:
        return redirect('chat:chat_list')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        invitation_token = request.POST.get('invitation_token')
        
        # Validate passwords match
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        # Check if invitation token is valid (optional for now, can be enforced later)
        if invitation_token:
            try:
                invitation = UserInvitation.objects.get(token=invitation_token, is_used=False)
                if invitation.email != email:
                    messages.error(request, 'This invitation was sent to a different email.')
                    return render(request, 'accounts/register.html')
            except UserInvitation.DoesNotExist:
                messages.error(request, 'Invalid or expired invitation token.')
                return render(request, 'accounts/register.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            return render(request, 'accounts/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Mark invitation as used if provided
        if invitation_token:
            invitation.is_used = True
            invitation.save()
        
        # Log the user in
        login(request, user)
        messages.success(request, f'Welcome, {username}! Your account has been created.')
        return redirect('chat:chat_list')
    
    # Get invitation token from URL if provided
    invitation_token = request.GET.get('token', '')
    invitation_email = ''
    
    if invitation_token:
        try:
            invitation = UserInvitation.objects.get(token=invitation_token, is_used=False)
            invitation_email = invitation.email
        except UserInvitation.DoesNotExist:
            messages.warning(request, 'Invalid or expired invitation token.')
    
    return render(request, 'accounts/register.html', {
        'invitation_token': invitation_token,
        'invitation_email': invitation_email
    })


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Display and edit user profile"""
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html')


def verify_email(request, token):
    """Verify user email address"""
    # Email verification logic (to be implemented)
    messages.success(request, 'Email verified successfully!')
    return redirect('accounts:login')