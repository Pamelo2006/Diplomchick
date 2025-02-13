# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from diagrams.models import ChatMessage
from accounts.models import Users


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat_group"  # Общая группа для всех
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        username = data.get('username', 'Гость')  # Имя пользователя или администратора

        # Сохраняем сообщение в базе данных
        user_instance = await self.get_user(username)
        if user_instance:
            await self.save_message_to_db(user_instance, message)

        # Отправляем сообщение в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'message': message,
            }
        )

    async def chat_message(self, event):
        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message']
        }))

    @sync_to_async
    def get_user(self, username):
        try:
            return Users.objects.get(Username=username)
        except Users.DoesNotExist:
            return None

    @sync_to_async
    def save_message_to_db(self, user, message):
        if user:
            ChatMessage.objects.create(user=user, message=message)