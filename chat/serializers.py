# serializers.py
from rest_framework import serializers
from .models import Message, VideoCall

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "sender", "receiver", "message_type", "content", "image", "created_at"]

class VideoCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoCall
        fields = []  #