from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Users
import json
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect

def vhod(request):
    return render(request, 'vhod.html')

# Страница после успешной авторизации
def da(request):
    return redirect('/diagrams/main_menu/')

# Обработка регистрации
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Проверяем, существует ли пользователь с таким username или email
        if Users.objects.filter(Username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        if Users.objects.filter(Email=Users.hash_value(email)).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        # Создаем нового пользователя
        user = Users(Username=username)
        user.set_email(email)  # Хэшируем email
        user.set_password(password)  # Хэшируем пароль
        user.save()

        # Возвращаем успешный ответ
        return JsonResponse({'success': True, 'message': 'User registered successfully'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Обработка авторизации
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        # Ищем пользователя по username
        try:
            user = Users.objects.get(Username=username)
        except Users.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Проверяем пароль
        if not user.check_password(password):
            return JsonResponse({'error': 'Invalid password'}, status=400)

        # Если авторизация успешна, возвращаем успешный ответ
        return JsonResponse({'success': True, 'message': 'Login successful'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    try:
        subject = 'Ваш код для двухфакторной аутентификации'
        message = f'Ваш одноразовый код: {otp}'
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Отправитель
            [email],  # Получатель
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")  # Логируем ошибку
        raise  # Повторно выбрасываем исключение

@csrf_exempt
@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        # Генерация OTP
        otp = generate_otp()

        # Сохранение OTP в сессии
        request.session['otp'] = otp
        request.session['email'] = email

        # Отправка OTP на email
        try:
            send_otp_email(email, otp)
            return JsonResponse({'success': True, 'message': 'OTP sent to your email!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_otp = data.get('otp')

        # Получение OTP из сессии
        stored_otp = request.session.get('otp')
        email = request.session.get('email')

        if not stored_otp or not email:
            return JsonResponse({'error': 'OTP expired or not sent'}, status=400)

        # Проверка OTP
        if user_otp == stored_otp:
            # Очистка сессии
            del request.session['otp']
            del request.session['email']

            # Поиск пользователя по email
            try:
                user = Users.objects.get(Email=Users.hash_value(email))
                # Перенаправляем на main_menu.html
                return JsonResponse({
                    'success': True,
                    'message': 'OTP verification successful',
                    'redirect_url': '/diagrams/main_menu/'  # Укажите правильный URL
                }, status=200)
            except Users.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid OTP'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)