from rest_framework import serializers
from .models import Room, Chat

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'user', 'character', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'room', 'content', 'sender_type', 'created_at']
        read_only_fields = ['id', 'created_at']