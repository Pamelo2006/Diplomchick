from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import render
from docx import Document
from .models import Document
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import BPMNFile, BPMNDiagrams


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
def my_diagrams(request):
    diagrams = BPMNDiagrams.objects.all()  # Получаем все диаграммы из базы данных
    return render(request, 'diagrams/my_diagrams.html', {'diagrams': diagrams})
def templates(request):
    diagrams = BPMNFile.objects.all().order_by('-created_at')  # Получаем все диаграммы, сортируем по дате создания
    return render(request, 'diagrams/templates.html', {'diagrams': diagrams})

def view_diagram(request, id):
    diagram = get_object_or_404(BPMNFile, id=id)
    return render(request, 'builder/use_templates.html', {'diagram': diagram})

def view_diagram1(request, id):
    diagram = get_object_or_404(BPMNDiagrams, id=id)
    return render(request, 'builder/use_templates.html', {'diagram': diagram})

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
def save_diagram(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            diagram_id = data.get("id")  # ID диаграммы (если передан)
            name = data.get("name", "Новая диаграмма")  # Название диаграммы
            xml = data.get("bpmn")  # XML-данные

            if diagram_id:
                # Обновляем существующую диаграмму
                diagram = get_object_or_404(BPMNDiagrams, id=diagram_id)
                diagram.name = name
                diagram.xml_data = xml
            else:
                # Создаём новую диаграмму
                diagram = BPMNDiagrams(name=name, xml_data=xml)

            diagram.save()  # Сохраняем изменения
            return JsonResponse({"status": "success", "id": diagram.id})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)