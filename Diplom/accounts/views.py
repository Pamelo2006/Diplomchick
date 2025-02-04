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

        user = Users(Username=username)
        user.set_email(email)
        user.set_password(password)
        user.save()

        # Сохраняем данные в сессии
        request.session['username'] = username
        request.session['email'] = email
        request.session.set_expiry(30 * 24 * 60 * 60)  # 30 дней

        return JsonResponse({'success': True, 'message': 'User registered successfully'}, status=201)

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
            del request.session['otp']
            del request.session['email']

            try:
                user = Users.objects.get(Email=Users.hash_value(email))
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