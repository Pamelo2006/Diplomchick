from django.urls import path
from . import views
from .views import auto_login, get_session_data, request_password_reset, verify_reset_code, reset_password, admin_login, verify_admin_otp, set_language, update_theme, get_user_theme

urlpatterns = [
    path('', views.vhod, name='vhod'),  # Страница входа
    path('register/', views.register, name='register'),  # Обработка регистрации
    path('login/', views.login, name='login'),  # Обработка авторизации
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('auto_login/', auto_login, name='auto_login'),
    path('get_session_data/', get_session_data, name='get_session_data'),
    path('account_modal/', views.account_modal, name='account_modal'),
    path("request-reset/", request_password_reset, name="request_reset"),
    path("verify-code/", verify_reset_code, name="verify_reset_code"),
    path("reset-password/", reset_password, name="reset_password"),
    path('admin-login/', admin_login, name='admin_login'),
    path('verify-admin-otp/', verify_admin_otp, name='verify_admin_otp'),
    path('set_language/', set_language, name='set_language'),
    path('update_theme/', update_theme, name='update_theme'),
    path('get_user_theme/',get_user_theme, name='get_user_theme'),

]