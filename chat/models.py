# chat/models.py
# Location: C:\private_chat_app\private_chat_app\chat\models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoom(models.Model):
    """Model for chat rooms (private or group chats)"""
    
    ROOM_TYPES = [
        ('private', 'Private Chat'),
        ('group', 'Group Chat'),
    ]
    
    name = models.CharField(max_length=255)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='private')
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.room_type})"
    
    def get_participant_names(self):
        """Get comma-separated list of participant names"""
        return ", ".join([user.username for user in self.participants.all()])


class Message(models.Model):
    """Model for storing encrypted chat messages"""
    
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('file', 'File'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('document', 'Document'),
    ]

    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    encrypted_content = models.TextField()
    file = models.URLField(max_length=500, blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} in {self.chat_room.name} - {self.message_type}"
    
    def get_file_size_display(self):
        """Convert file size to human-readable format"""
        if not self.file_size:
            return "N/A"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"


class MessageReadReceipt(models.Model):
    """Model for tracking when users read messages"""
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_read_receipts')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Message Read Receipt'
        verbose_name_plural = 'Message Read Receipts'
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.username} read message {self.message.id}"