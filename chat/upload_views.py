# chat/upload_views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import ChatRoom, Message
import cloudinary.uploader
import uuid

@login_required
@require_POST
def upload_file(request, room_id):
    """Handle file uploads for chat messages"""
    
    try:
        room = ChatRoom.objects.get(id=room_id, participants=request.user)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'error': 'Chat room not found'}, status=404)
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    file = request.FILES['file']
    
    # Validate file size
    if file.size > settings.MAX_FILE_SIZE:
        return JsonResponse({
            'error': f'File too large. Max size: {settings.MAX_FILE_SIZE / (1024*1024)}MB'
        }, status=400)
    
    # Validate file extension
    ext = file.name.split('.')[-1].lower()
    if ext not in settings.ALLOWED_FILE_EXTENSIONS:
        return JsonResponse({
            'error': f'File type not allowed. Allowed: {", ".join(settings.ALLOWED_FILE_EXTENSIONS)}'
        }, status=400)
    
    # Determine message type and Cloudinary resource type
    message_type = 'file'
    resource_type = 'raw'  # Default for documents/files
    
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        message_type = 'image'
        resource_type = 'image'
    elif ext in ['mp4', 'mov', 'avi']:
        message_type = 'video'
        resource_type = 'video'
    elif ext in ['mp3', 'wav']:
        message_type = 'audio'
        resource_type = 'raw'
    
    # Generate unique filename
    unique_name = f"{uuid.uuid4()}.{ext}"
    
    try:
        # Upload to Cloudinary with correct resource_type
        upload_result = cloudinary.uploader.upload(
            file,
            folder=f"chat_files/{room_id}",
            public_id=unique_name.rsplit('.', 1)[0],  # Remove extension from public_id
            resource_type=resource_type
        )
        
        file_url = upload_result['secure_url']
        
    except Exception as e:
        return JsonResponse({
            'error': f'Upload failed: {str(e)}'
        }, status=500)
    
    # Create message (store Cloudinary URL in file field)
    message = Message.objects.create(
        chat_room=room,
        sender=request.user,
        message_type=message_type,
        encrypted_content=file.name,
        file=file_url,  # Store Cloudinary URL
        file_name=file.name,
        file_size=file.size
    )
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
        'file_url': file_url,
        'file_name': message.file_name,
        'file_size': message.file_size,
        'message_type': message_type
    })
