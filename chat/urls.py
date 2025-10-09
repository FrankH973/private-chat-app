# chat/urls.py
# Location: C:\private_chat_app\private_chat_app\chat\urls.py

from django.urls import path
from . import views, upload_views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('create-room/', views.create_room, name='create_room'),
    path('upload/<int:room_id>/', upload_views.upload_file, name='upload_file'),  # New
]