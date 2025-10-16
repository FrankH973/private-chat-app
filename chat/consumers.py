# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        print(f"========== WebSocket Connect Attempt ==========")
        print(f"Room ID: {self.room_id}")
        print(f"User: {self.user}")
        print(f"User type: {type(self.user)}")
        print(f"Is authenticated: {self.user.is_authenticated}")
        print(f"===============================================")

        if not self.user.is_authenticated:
            print("❌ CLOSING: User not authenticated")
            await self.close()
            return

        # Add try-except to catch errors
        try:
            print(f"Checking if user is participant in room {self.room_id}...")
            is_participant = await self.check_participant()
            print(f"✅ Is participant: {is_participant}")
        except Exception as e:
            print(f"❌ ERROR checking participant: {e}")
            import traceback
            traceback.print_exc()
            await self.close()
            return
        
        if not is_participant:
            print("❌ CLOSING: User not a participant")
            await self.close()
            return

        print(f"Adding to group: {self.room_group_name}")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        print("Accepting connection...")
        await self.accept()
        
        print("✅ WebSocket connection accepted!")
        
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to chat room'
        }))
        print("Sent connection confirmation message")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'text')
        
        if message_type == 'text':
            message = text_data_json.get('message', '')
            if not message.strip():
                return

            saved_message = await self.save_message(message, 'text')
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'message_type': 'text',
                    'sender': self.user.username,
                    'sender_id': self.user.id,
                    'timestamp': saved_message['timestamp'],
                    'message_id': saved_message['id']
                }
            )
        
        elif message_type == 'file':
            # File message (already saved by upload view)
            message_id = text_data_json.get('message_id')
            file_info = await self.get_file_message(message_id)
            
            if file_info:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': file_info['file_name'],
                        'message_type': file_info['message_type'],
                        'sender': self.user.username,
                        'sender_id': self.user.id,
                        'timestamp': file_info['timestamp'],
                        'message_id': file_info['id'],
                        'file_url': file_info['file_url'],
                        'file_name': file_info['file_name'],
                        'file_size': file_info['file_size']
                    }
                )

    async def chat_message(self, event):
        message_data = {
            'type': 'message',
            'message': event['message'],
            'message_type': event['message_type'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }
        
        # Add file info if it's a file message
        if event['message_type'] in ['file', 'image', 'video', 'audio']:
            message_data['file_url'] = event.get('file_url')
            message_data['file_name'] = event.get('file_name')
            message_data['file_size'] = event.get('file_size')
        
        await self.send(text_data=json.dumps(message_data))

    @database_sync_to_async
    def check_participant(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message, message_type):
        room = ChatRoom.objects.get(id=self.room_id)
        msg = Message.objects.create(
            chat_room=room,
            sender=self.user,
            encrypted_content=message,
            message_type=message_type
        )
        return {
            'id': msg.id,
            'timestamp': msg.timestamp.isoformat()
        }
    
    @database_sync_to_async
    def get_file_message(self, message_id):
        try:
            msg = Message.objects.get(id=message_id, chat_room_id=self.room_id)
            return {
                'id': msg.id,
                'message_type': msg.message_type,
                'file_url': msg.file if msg.file else None,
                'file_name': msg.file_name,
                'file_size': msg.file_size,
                'timestamp': msg.timestamp.isoformat()
            }
        except Message.DoesNotExist:
            return None
