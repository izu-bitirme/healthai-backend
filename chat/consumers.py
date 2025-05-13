import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from user_profile.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist
from chat.models import Message

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    group_name = "chats"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room_name = None
        self.room_group_name = None
        self.user_profile = None

    async def connect(self):
        try:
            token = await self.get_token_from_scope()
            if not token:
                logger.warning("No token provided in WebSocket connection")
                await self.close(code=4001)
                return

            self.user = await self.authenticate_user(token)
            if not self.user:
                logger.warning(f"Authentication failed for token: {token}")
                await self.close(code=4001)
                return

            try:
                self.user_profile = await self.get_user_profile()
            except ObjectDoesNotExist:
                logger.error(f"User profile not found for user {self.user.id}")
                await self.close(code=4003)
                return

            await self.channel_layer.group_add(
                "user_" + str(self.user.id), self.channel_name
            )

            await self.accept()

        except Exception as e:
            logger.error(f"Connection error: {str(e)}", exc_info=True)
            await self.close(code=4002)

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name") and self.user:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
            await self.send_online_status(False)
            logger.info(
                f"User {self.user.username} disconnected from room {self.room_name}"
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if data.get("type") == "auth":
                token = data.get("token")
                if token:
                    self.user = await self.authenticate_user(token)
                    if self.user:
                        await self.send(text_data=json.dumps({"type": "auth_success"}))
                        self.user_profile = await self.get_user_profile()
                        return
                    else:
                        await self.close(code=4001)
                        return

            message_type = data.get("type", "text")

            if message_type == "text":
                await self.handle_text_message(data)
            elif message_type == "image":
                await self.handle_image_message(data)
            elif message_type == "call":
                await self.handle_call_message(data)
            elif message_type == "typing":
                await self.handle_typing_indicator(data)
            else:
                raise ValueError("Invalid message type")

        except json.JSONDecodeError:
            await self.send_error_message("Invalid JSON format")
        except KeyError as e:
            await self.send_error_message(f"Missing required field: {str(e)}")
        except Exception as e:
            await self.send_error_message(str(e))
            logger.error(f"Message handling error: {str(e)}", exc_info=True)

    async def handle_text_message(self, data):
        receiver_id = data["receiver_id"]
        content = data["message"]

        message = await self.save_message(
            content=content, receiver_id=receiver_id, message_type=Message.TEXT
        )

        data = {
            "type": "chat_message",
            "text": message.content,
            "sender_name": self.user.first_name + " " + self.user.last_name,
            "is_sender": False,
            "sender_image": self.user_profile.photo.url,
            "patient_id": receiver_id,
            "date": message.created_at.strftime("%d-%m-%Y %H:%M:%S"),
            "message_type": Message.TEXT,
            "status": "delivered",
        }

        # send message to receiver room
        await self.channel_layer.group_send("user_" + str(receiver_id), data)

        data["is_sender"] = True
        await self.channel_layer.group_send("user_" + str(self.user.id), data)

    async def handle_image_message(self, data):
        receiver_id = data["receiver_id"]
        image_url = data["image_url"]
        caption = data.get("caption", "")

        message = await self.save_message(
            content=caption,
            receiver_id=receiver_id,
            message_type=Message.IMAGE,
            image_url=image_url,
        )

        await self.broadcast_message(
            {
                "type": "chat_message",
                "message_id": message.id,
                "content": caption,
                "image_url": image_url,
                "sender_id": self.user.id,
                "receiver_id": receiver_id,
                "message_type": Message.IMAGE,
                "timestamp": str(message.created_at),
                "status": "delivered",
            }
        )

    async def handle_call_message(self, data):
        call_type = data["call_type"]
        receiver_id = data["receiver_id"]
        action = data["action"]

        if action == "start":
            call_log = await self.create_call_log(
                receiver_id=receiver_id, call_type=call_type, started_at=datetime.now()
            )

            await self.broadcast_message(
                {
                    "type": "call_message",
                    "action": "start",
                    "call_id": call_log.id,
                    "call_type": call_type,
                    "sender_id": self.user.id,
                    "receiver_id": receiver_id,
                    "timestamp": str(datetime.now()),
                }
            )
        elif action in ["end", "missed"]:
            call_log = await self.update_call_log(
                call_id=data["call_id"], action=action
            )

            await self.broadcast_message(
                {
                    "type": "call_message",
                    "action": action,
                    "call_id": call_log.id,
                    "duration": call_log.duration() if action == "end" else 0,
                    "sender_id": self.user.id,
                    "receiver_id": receiver_id,
                    "timestamp": str(datetime.now()),
                }
            )

    async def handle_typing_indicator(self, data):
        await self.broadcast_message(
            {
                "type": "typing",
                "sender_id": self.user.id,
                "receiver_id": data["receiver_id"],
                "is_typing": data["is_typing"],
            }
        )

    async def broadcast_message(self, message_data):
        await self.channel_layer.group_send(self.room_group_name, message_data)

    async def chat_message(self, event):
        await self.send_message(event, "chat_message")

    async def call_message(self, event):
        await self.send_message(event, "call_message")

    async def typing(self, event):
        await self.send_message(event, "typing")

    async def status_message(self, event):
        await self.send_message(event, "status_update")

    async def send_message(self, event, message_type):
        await self.send(
            text_data=json.dumps(
                {
                    "type": message_type,
                    **{k: v for k, v in event.items() if k != "type"},
                }
            )
        )

    async def send_error_message(self, error_msg):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "error",
                    "message": error_msg,
                    "timestamp": str(datetime.now()),
                }
            )
        )

    async def send_online_status(self, is_online):
        await self.broadcast_message(
            {
                "type": "status_message",
                "user_id": self.user.id,
                "is_online": is_online,
                "timestamp": str(datetime.now()),
            }
        )

    @database_sync_to_async
    def get_token_from_scope(self):
        query_string = self.scope.get("query_string", b"").decode()
        if "token=" in query_string:
            return query_string.split("token=")[1].split("&")[0]

        headers = dict(self.scope.get("headers", {}))
        if b"token" in headers:
            auth_header = headers[b"token"].decode()
            if auth_header.startswith("Bearer "):
                return auth_header.split(" ")[1]
        return None

    @database_sync_to_async
    def authenticate_user(self, token) -> User | None:
        try:
            access_token = AccessToken(token)
            user_id = access_token.payload.get("user_id")
            if not user_id:
                return None
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            logger.warning(f"Authentication failed: {str(e)}")
            return None

    @database_sync_to_async
    def get_user_profile(self):
        return UserProfile.objects.get(user=self.user)

    @database_sync_to_async
    def save_message(self, content, receiver_id, message_type, image_url=None):
        receiver = UserProfile.objects.get(user__id=receiver_id)
        message = Message(
            sender=self.user_profile,
            receiver=receiver,
            message_type=message_type,
            content=content,
        )
        if image_url:
            message.image = image_url
        message.save()
        return message
