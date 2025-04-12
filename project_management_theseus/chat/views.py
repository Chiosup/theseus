from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from django.db.models import Max,Subquery, OuterRef, Q, Count
from django.http import JsonResponse
from django.db import models

@login_required
def index(request):
    chats = ChatRoom.objects.filter(
        participants=request.user
    ).annotate(
        last_msg_time=Max('messages__timestamp'),
        last_message_content=Subquery(
            Message.objects.filter(room=OuterRef('pk'))
            .order_by('-timestamp')
            .values('content')[:1]
        ),
        last_message_sender=Subquery(
            Message.objects.filter(room=OuterRef('pk'))
            .order_by('-timestamp')
            .values('sender__username')[:1]
        )
    ).order_by('-last_msg_time').prefetch_related('participants')
    
    return render(request, 'chat/index.html', {
        'chats': chats,
        'current_user': request.user
    })

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
def chat_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.order_by('timestamp').values(
        'content',
        'timestamp',
        sender_name=models.F('sender__username'),
        is_my=models.ExpressionWrapper(
            models.Q(sender=request.user),
            output_field=models.BooleanField()
        )
    )
    return JsonResponse(list(messages), safe=False)

def search_chats(request):
    query = request.GET.get('q', '')
    chats = ChatRoom.objects.filter(
        participants=request.user,
        display_name__icontains=query
    ).annotate(
        last_msg_time=Max('messages__timestamp'),
        last_message=Subquery(
            Message.objects.filter(room=models.OuterRef('pk'))
            .order_by('-timestamp')
            .values('content')[:1]
        )
    )
    return JsonResponse([
        {
            'id': chat.id,
            'name': chat.get_display_name(),
            'last_message': chat.last_message,
            'time': chat.last_msg_time.strftime("%H:%M")
        } for chat in chats
    ], safe=False)


def send_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    message = Message.objects.create(
        room=room,
        sender=request.user,
        content=request.POST.get('content')
    )
    
    if 'file' in request.FILES:
        Attachment.objects.create(
            message=message,
            file=request.FILES['file']
        )
    
    return JsonResponse({'status': 'ok'})