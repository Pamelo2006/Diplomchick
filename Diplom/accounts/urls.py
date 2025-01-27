from django.urls import path
from . import views

urlpatterns = [
    path('', views.vhod, name='vhod'),  # Страница входа
    path('da/', views.da, name='da'),  # Страница после успешной авторизации
    path('register/', views.register, name='register'),  # Обработка регистрации
    path('login/', views.login, name='login'),  # Обработка авторизации
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
]