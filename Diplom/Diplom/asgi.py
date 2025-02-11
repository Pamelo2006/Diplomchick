import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from diagrams.routing import websocket_urlpatterns  # импорт маршрутов WebSocket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Diplom.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # подключение маршрутов WebSocket
    ),
})
