from django.shortcuts import render, redirect
from django.http import JsonResponse

def main_menu(request):
    return render(request, 'diagrams/main_menu.html')
def peculiarities(request):
    return render(request, 'diagrams/peculiarities.html')
def solutions(request):
    return render(request, 'diagrams/solutions.html')
def block(request):
    return  render(request, 'builder/block_diagrams.html')
def activity(request):
    return  render(request, 'builder/activity.html')
def sipoc(request):
    return  render(request, 'builder/SIPOC_diagram.html')
def swim(request):
    return  render(request, 'builder/Swim_lane_diagram.html')
def log_in(request):
    return render(request, 'login.html')
def sig_in(request):
    return render(request, 'vhod.html')

def account_modal(request):
    username = request.session.get('username', None)
    email = request.session.get('email', None)

    # Если данных нет в сессии, возвращаем ошибку
    if not username or not email:
        return JsonResponse({'success': False})

    # Передаем данные в формате JSON
    return JsonResponse({
        'success': True,
        'username': username,
        'email': email
    })