from rest_framework import generics
from apps.characters.views import IsOwner
from .models import Chat, Room
from .serializers import RoomSerializer, ChatSerializer


class RoomLView(generics.ListAPIView):
    permission_classes = [IsOwner]
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.filter(user=self.request.user)


class ChatLView(generics.ListAPIView):
    permission_classes = [IsOwner]
    serializer_class = ChatSerializer

    def get_queryset(self):
        rooms = Room.objects.filter(user=self.request.user)
        chats = Chat.objects.filter(room__in=rooms)
        return chats