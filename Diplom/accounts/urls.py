from django.urls import path
from . import views
from .views import auto_login, get_session_data

urlpatterns = [
    path('', views.vhod, name='vhod'),  # Страница входа
    path('register/', views.register, name='register'),  # Обработка регистрации
    path('login/', views.login, name='login'),  # Обработка авторизации
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('auto_login/', auto_login, name='auto_login'),
    path('get_session_data/', get_session_data, name='get_session_data'),
    path('account_modal/', views.account_modal, name='account_modal'),
]