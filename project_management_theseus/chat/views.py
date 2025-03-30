from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from django.db.models import Max
@login_required
def index(request):
    """Главная страница чатов"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Используем annotate для добавления времени последнего сообщения
    chats = ChatRoom.objects.filter(
        participants=request.user
    ).annotate(
        last_msg_time=Max('messages__timestamp')
    ).order_by('-last_msg_time')
    
    return render(request, 'chat/index.html', {'chats': chats})
def create_direct_chat(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    User = get_user_model()
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            other_user = User.objects.get(id=user_id)
            
            existing_chat = ChatRoom.objects.filter(
                type='direct',
                participants=request.user
            ).filter(
                participants=other_user
            ).first()
            
            if existing_chat:
                return redirect('chat:room', room_id=existing_chat.id)
            
            new_chat = ChatRoom.objects.create(type='direct', creator=request.user)  # Устанавливаем создателя
            new_chat.participants.add(request.user, other_user)
            return redirect('chat:room', room_id=new_chat.id)
            
        except User.DoesNotExist:
            return redirect('chat:create_direct')
    
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/create_direct.html', {'users': users})
def room_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user not in room.participants.all():
        return HttpResponseForbidden()

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                room=room,
                sender=request.user,
                content=content
            )
            return redirect('chat:room', room_id=room.id)

    messages = room.messages.all().order_by('timestamp')
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages
    })