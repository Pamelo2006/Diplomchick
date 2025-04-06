from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import render
from docx import Document
from .models import Document
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import BPMNFile, BPMNDiagrams
from .models import ChatMessage
from django.contrib.admin.views.decorators import staff_member_required
from builder.models import BPMNDiagram
from django.utils.translation import activate, get_language


def chat_history(request):
    messages = ChatMessage.objects.all().order_by('-timestamp')[:50]  # Последние 50 сообщений
    data = [
        {
            'username': msg.user.Username,
            'message': msg.message,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for msg in messages
    ]
    return JsonResponse(data, safe=False)

@staff_member_required
def chat_admin(request):
    return render(request, 'diagrams/admin/chat.html')

def my_diagrams(request):
    # Получаем имя пользователя из сессии
    username = request.session.get('username')

    # Фильтруем диаграммы по имени пользователя
    diagrams = BPMNDiagram.objects.filter(username=username)

    # Формируем контекст для передачи в шаблон
    context = {
        'username': username,
        'diagrams': diagrams,
    }

    # Рендерим шаблон с контекстом
    return render(request, 'diagrams/my_diagrams.html', context)

def main_menu(request):
    username = request.session.get('username')
    context = {
        'username': username,
    }
    return render(request, 'diagrams/main_menu.html', context)
def peculiarities(request):
    return render(request, 'diagrams/peculiarities.html')
def solutions(request):
    return render(request, 'diagrams/solutions.html')

def block(request):
    username = request.session.get('username')
    # Получаем язык из сессии или используем 'ru' по умолчанию
    language = request.session.get('language', 'ru')
    context = {
        'username': username,
        'language': language,  # Передаем язык в контекст шаблона
    }
    return  render(request, 'builder/block_diagrams.html', context)
    
def activity(request):
    username = request.session.get('username')
    # Получаем язык и тему из сессии или используем значения по умолчанию
    language = request.session.get('language', 'ru')
    theme = request.session.get('theme', 'light')
    
    context = {
        'username': username,
        'language': language,
        'theme': theme,  # Передаем тему в контекст шаблона
    }
    return render(request, 'builder/activity.html', context)

def sipoc(request):
    username = request.session.get('username')
    # Получаем язык из сессии или используем 'ru' по умолчанию
    language = request.session.get('language', 'ru')
    context = {
        'username': username,
        'language': language,  # Передаем язык в контекст шаблона
    }
    return  render(request, 'builder/SIPOC_diagram.html', context)
def swim(request):
    username = request.session.get('username')
    # Получаем язык из сессии или используем 'ru' по умолчанию
    language = request.session.get('language', 'ru')
    context = {
        'username': username,
        'language': language,  # Передаем язык в контекст шаблона
    }
    return  render(request, 'builder/Swim_lane_diagram.html', context)

def templates(request):
    username = request.session.get('username')
    context = {
        'username': username,
    }
    # Получаем все диаграммы из таблицы BPMNDiagrams, сортируем по дате создания
    diagrams = BPMNDiagram.objects.filter(username='админ').order_by('-created_at')

    return render(request, 'diagrams/templates.html', {'diagrams': diagrams, **context})

def view_diagram(request, id):
    username = request.session.get('username')
    context = {
        'username': username,
    }
    diagram = get_object_or_404(BPMNDiagram, id=id)  # Получаем диаграмму по id
    return render(request, 'builder/use_templates.html', {'diagram': diagram, **context})


def view_diagram1(request, id):
    username = request.session.get('username')
    context = {
        'username': username,
    }
    diagram = get_object_or_404(BPMNDiagram, id=id)
    return render(request, 'builder/use_templates.html', {'diagram': diagram, **context})

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

def get_bpmn_xml(request, pk):
    bpmn_file = get_object_or_404(BPMNFile, pk=pk)
    return JsonResponse({'xml_data': bpmn_file.xml_data})

@csrf_exempt  # Отключает проверку CSRF для тестирования (лучше использовать CSRF-токен)
def save_bpmn_xml(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', 'Новая диаграмма')
            xml = data.get('bpmn', '')
            bpmn_file = BPMNFile.objects.create(name=name, xml_data=xml)
            return JsonResponse({'status': 'success', 'id': bpmn_file.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def create_bpmn(request):
    new_diagram = BPMNFile.objects.create()
    return redirect('bpmn_editor', pk=new_diagram.pk)

def bpmn_editor(request, pk=None):
    if pk:
        diagram = get_object_or_404(BPMNFile, pk=pk)
    else:
        diagram = BPMNFile.objects.create(name="Новая диаграмма")  # Создаём новую, если pk нет
        return redirect('bpmn_editor', pk=diagram.pk)  # Перенаправляем на редактирование с pk
    return render(request, 'diagrams/editor.html', {'diagram': diagram})

@csrf_exempt
def set_language(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lang = data.get('language', 'ru')
            activate(lang)
            request.session['django_language'] = lang
            return JsonResponse({'status': 'success', 'language': get_language()})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

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