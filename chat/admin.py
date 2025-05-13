from django.contrib import admin

from .models import Message, VideoCall

admin.site.register(Message)
admin.site.register(VideoCall)