from django.shortcuts import render, redirect
from django.http import JsonResponse
import os
from django.conf import settings
from django.shortcuts import render
from docx import Document
from .models import Document

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

def read_docx(file_path):
    """Функция для чтения содержимого .doc файла"""
    try:
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        return f"Ошибка при чтении файла: {str(e)}"

def peculiarities_view(request):
    # Загружаем актуальные данные из базы данных
    russian_doc = Document.objects.filter(name='russian_doc').first()
    english_doc = Document.objects.filter(name='english_doc').first()

    return render(request, "diagrams/peculiarities.html", {
        "russian_text": russian_doc.content if russian_doc else "Файл не найден",
        "english_text": english_doc.content if english_doc else "Файл не найден"
    })