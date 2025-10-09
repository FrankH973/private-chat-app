# accounts/urls.py
# Location: C:\private_chat_app\private_chat_app\accounts\urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
]