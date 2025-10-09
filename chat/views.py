# chat/views.py
# Location: C:\private_chat_app\private_chat_app\chat\views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from django.db.models import Q

User = get_user_model()


@login_required
def chat_list(request):
    """Display list of chat rooms for the current user"""
    chat_rooms = ChatRoom.objects.filter(
        participants=request.user,
        is_active=True
    ).order_by('-updated_at')
    
    return render(request, 'chat/chat_list.html', {
        'chat_rooms': chat_rooms
    })


@login_required
def chat_room(request, room_id):
    """Display a specific chat room with messages"""
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    # Get all messages in this room
    messages_list = Message.objects.filter(chat_room=room).select_related('sender')
    
    # Get other participants
    other_participants = room.participants.exclude(id=request.user.id)
    
    return render(request, 'chat/chat_room.html', {
        'room': room,
        'messages': messages_list,
        'other_participants': other_participants,
    })


@login_required
def create_room(request):
    """Create a new chat room"""
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_type = request.POST.get('room_type', 'private')
        participant_emails = request.POST.getlist('participants')
        
        # Create the room
        room = ChatRoom.objects.create(
            name=room_name,
            room_type=room_type,
            created_by=request.user
        )
        
        # Add creator as participant
        room.participants.add(request.user)
        
        # Add other participants
        for email in participant_emails:
            try:
                user = User.objects.get(email=email)
                room.participants.add(user)
            except User.DoesNotExist:
                messages.warning(request, f'User with email {email} not found.')
        
        messages.success(request, f'Chat room "{room_name}" created successfully!')
        return redirect('chat:chat_room', room_id=room.id)
    
    # Get all users except current user for the participant list
    users = User.objects.exclude(id=request.user.id)
    
    return render(request, 'chat/create_room.html', {
        'users': users
    })