from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Users
import json
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.models import User

@csrf_exempt
def update_theme(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            theme = data.get('theme')
            username = data.get('username')
            
            if theme in ['light', 'dark']:
                # Сохраняем тему в сессии
                request.session['user_theme'] = theme
                
                # Если нужно, можно сохранить тему в профиле пользователя
                try:
                    user = Users.objects.get(Username=username)
                    user.theme = theme
                    user.save()
                except Users.DoesNotExist:
                    pass
                    
                return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            pass
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def get_user_theme(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            # Проверяем тему в сессии
            if 'user_theme' in request.session:
                return JsonResponse({'theme': request.session['user_theme']})
                
            # Если нет в сессии, проверяем в профиле пользователя
            try:
                user = Users.objects.get(Username=username)
                if hasattr(user, 'theme') and user.theme in ['light', 'dark']:
                    return JsonResponse({'theme': user.theme})
            except Users.DoesNotExist:
                pass
                
            # Возвращаем тему по умолчанию
            return JsonResponse({'theme': 'light'})
            
        except json.JSONDecodeError:
            pass
    return JsonResponse({'status': 'error'}, status=400)

def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language', settings.LANGUAGE_CODE)
        if language in [lang[0] for lang in settings.LANGUAGES]:
            request.session['django_language'] = language
            activate(language)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def vhod(request):
    # Проверяем, передаёт ли пользователь данные (например, POST-запрос при логине)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Если данные введены, проверяем их
        if username and password:
            try:
                user = Users.objects.get(Username=username)
                if user.check_password(password):
                    request.session['username'] = username
                    request.session['email'] = user.Email
                    return redirect('/diagrams/main_menu/')  # Перенаправление после успешного входа
            except Users.DoesNotExist:
                pass  # Ошибка пользователя, но не редиректим сразу

    # Если данных нет — просто отображаем страницу входа
    return render(request, 'vhod.html')


@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if Users.objects.filter(Username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        if Users.objects.filter(Email=Users.hash_value(email)).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        # Создаем пользователя
        user = Users(Username=username)
        user.set_email(email)
        user.set_password(password)
        user.save()

        # Генерируем и отправляем OTP
        otp = generate_otp()
        request.session['otp'] = otp
        request.session['email'] = email
        request.session['username'] = username  # Сохраняем для последующей верификации

        try:
            send_otp_email(email, otp)
            return JsonResponse({
                'success': True,
                'message': 'User registered successfully. OTP sent to your email!',
                'next_step': 'verify_otp'  # Фронтенд переключится на форму OTP
            }, status=201)
        except Exception as e:
            user.delete()  # Откатываем регистрацию при ошибке отправки
            return JsonResponse({'error': f'Failed to send OTP: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Обработка авторизации
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try:
            user = Users.objects.get(Username=username)
        except Users.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        if not user.check_password(password):
            return JsonResponse({'error': 'Invalid password'}, status=400)

        # Сохраняем данные пользователя в сессии
        request.session['username'] = username
        request.session['email'] = user.Email

        return JsonResponse({'success': True, 'message': 'Login successful'})

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
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        raise


@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        otp = generate_otp()

        request.session['otp'] = otp
        request.session['email'] = email

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

        stored_otp = request.session.get('otp')
        email = request.session.get('email')

        if not stored_otp or not email:
            return JsonResponse({'error': 'OTP expired or not sent'}, status=400)

        if user_otp == stored_otp:
            # Очищаем сессию
            del request.session['otp']

            # Активируем пользователя (если нужно)
            try:
                user = Users.objects.get(Email=Users.hash_value(email))
                user.is_active = True  # Если у вас есть поле активации
                user.save()

                return JsonResponse({
                    'success': True,
                    'message': 'OTP verification successful',
                    'redirect_url': '/diagrams/main_menu/'
                }, status=200)
            except Users.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid OTP'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def auto_login(request):
    if 'username' in request.session and 'email' in request.session:
        return JsonResponse({'success': True, 'message': 'Auto login successful'})

    return JsonResponse({'success': False, 'message': 'Auto login failed'}, status=401)

def get_session_data(request):
    username = request.session.get('username')
    email = request.session.get('email')

    if username and email:
        return JsonResponse({'username': username, 'email': email})
    else:
        return JsonResponse({'error': 'No session data found'}, status=400)


def account_modal(request):
    username = request.session.get('username', None)
    email = request.session.get('email', None)

    # If no data in session, return an error
    if not username or not email:
        return JsonResponse({'success': False})

    # Return session data as JSON
    return JsonResponse({
        'success': True,
        'username': username,
        'email': email
    })


def generate_reset_code():
    """Генерация 6-значного кода"""
    return str(random.randint(100000, 999999))


def send_reset_email(email, code):
    """Отправка кода подтверждения на email"""
    subject = "Восстановление пароля"
    message = f"Ваш код для сброса пароля: {code}"

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


@csrf_exempt
def request_password_reset(request):
    """Запрос на восстановление пароля (получение кода)"""
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")

        try:
            user = Users.objects.get(Username=username, Email=Users.hash_value(email))
        except Users.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        # Генерируем и сохраняем код в сессии
        reset_code = generate_reset_code()
        request.session["reset_code"] = reset_code
        request.session["reset_email"] = email

        # Отправляем код на email
        send_reset_email(email, reset_code)

        return JsonResponse({"success": True, "message": "Reset code sent to your email."}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def verify_reset_code(request):
    """Проверка введённого пользователем кода"""
    if request.method == "POST":
        data = json.loads(request.body)
        user_code = data.get("code")
        stored_code = request.session.get("reset_code")

        if not stored_code:
            return JsonResponse({"error": "Reset code expired or not found"}, status=400)

        if user_code == stored_code:
            return JsonResponse({"success": True, "message": "Code verified, you can reset your password."}, status=200)
        else:
            return JsonResponse({"error": "Invalid code"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def reset_password(request):
    """Сброс пароля после подтверждения кода"""
    if request.method == "POST":
        data = json.loads(request.body)
        new_password = data.get("new_password")
        email = request.session.get("reset_email")

        if not email:
            return JsonResponse({"error": "Session expired or invalid request"}, status=400)

        try:
            user = Users.objects.get(Email=Users.hash_value(email))
        except Users.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        # Сохраняем новый пароль
        user.set_password(new_password)
        user.save()

        # Очищаем сессию
        del request.session["reset_code"]
        del request.session["reset_email"]

        return JsonResponse({"success": True, "message": "Password reset successfully."}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def admin_login(request):
    """Обработка входа администратора"""
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        try:
            # Ищем пользователя по username и email
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Проверяем пароль
        if not user.check_password(password):
            return JsonResponse({'error': 'Invalid password'}, status=400)

        # Проверяем, является ли пользователь администратором
        if not user.is_staff:
            return JsonResponse({'error': 'You do not have admin privileges'}, status=403)

        # Генерация и отправка OTP
        otp = generate_otp()
        request.session['otp'] = otp
        request.session['email'] = email

        try:
            send_otp_email(email, otp)
            return JsonResponse({'success': True, 'message': 'OTP sent to your email!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def verify_admin_otp(request):
    """Проверка OTP для администратора"""
    if request.method == 'POST':
        data = json.loads(request.body)
        user_otp = data.get('otp')

        stored_otp = request.session.get('otp')
        email = request.session.get('email')

        if not stored_otp or not email:
            return JsonResponse({'error': 'OTP expired or not sent'}, status=400)

        if user_otp == stored_otp:
            del request.session['otp']
            del request.session['email']

            try:
                # Ищем пользователя по email
                user = User.objects.get(email=email)
                if user.is_staff:
                    return JsonResponse({
                        'success': True,
                        'message': 'OTP verification successful',
                        'redirect_url': 'http://127.0.0.1:8000/admin/'  # Перенаправление в панель администратора
                    }, status=200)
                else:
                    return JsonResponse({
                        'error': 'You do not have admin privileges'
                    }, status=403)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid OTP'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)