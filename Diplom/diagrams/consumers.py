import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        username = data.get('username', 'Аноним')  # Получаем имя пользователя
        message = data.get('message', '')

        await self.send(text_data=json.dumps({
            'username': username,
            'message': message
        }))

    async def chat_message(self, event):
        """ Отправка сообщения всем в группе """
        message = event["message"]

        # Отправляем сообщение клиентам
        await self.send(text_data=json.dumps({"message": message, "is_admin": event["is_admin"]}))
