from django.urls import path
from . import views

app_name = 'chat'
urlpatterns = [
    path('room/<uuid:room_id>/', views.room_view, name='room'),
    path('', views.index, name='index'),
    path('create-direct/', views.create_direct_chat, name='create_direct'),  
    path('room/<int:room_id>/', views.room_view, name='room'),
]