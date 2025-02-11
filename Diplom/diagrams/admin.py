from django.contrib import admin
from django import forms
from .models import Document, BPMNFile
from docx import Document as DocxDocument
from django.utils.html import mark_safe
from django.urls import path
from .consumers import ChatConsumer
from django.shortcuts import render



class BPMNFileForm(forms.ModelForm):
    class Meta:
        model = BPMNFile
        fields = []  # Удалили поля 'name' и 'xml_data' из формы


@admin.register(BPMNFile)
class BPMNFileAdmin(admin.ModelAdmin):
    form = BPMNFileForm
    list_display = ('name','created_at',)
    readonly_fields = ('created_at',)  # Дата создания только для чтения
    change_form_template = 'diagrams/admin/bpmnfile_form.html'

    class Media:
        css = {
            'all': (
                'https://unpkg.com/bpmn-js@14.0.0/dist/assets/diagram-js.css',
                'https://unpkg.com/bpmn-js@14.0.0/dist/assets/bpmn-font/css/bpmn-embedded.css'
            )
        }

    def save_model(self, request, obj, form, change):
        """Создает пустую BPMN-диаграмму при создании нового объекта."""
        super().save_model(request, obj, form, change)

        if not obj.xml_data:  # Если XML отсутствует, записываем более сложный шаблон
            obj.xml_data = '''
            <?xml version="1.0" encoding="UTF-8"?>
            <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                              xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                              xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                              xmlns:di="http://www.omg.org/spec/DD/20100524/DI">
                <bpmn:process id="Process_1" isExecutable="false">
                    <bpmn:startEvent id="StartEvent_1">
                        <bpmn:outgoing>Flow_1</bpmn:outgoing>
                    </bpmn:startEvent>
                    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_1"/>
                    <bpmn:task id="Task_1">
                        <bpmn:incoming>Flow_1</bpmn:incoming>
                    </bpmn:task>
                </bpmn:process>
                <bpmndi:BPMNDiagram id="BPMNDiagram_1">
                    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
                        <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
                            <dc:Bounds x="150" y="150" width="36" height="36"/>
                        </bpmndi:BPMNShape>
                        <bpmndi:BPMNShape id="Task_1_di" bpmnElement="Task_1">
                            <dc:Bounds x="250" y="135" width="100" height="80"/>
                        </bpmndi:BPMNShape>
                    </bpmndi:BPMNPlane>
                </bpmndi:BPMNDiagram>
            </bpmn:definitions>
            '''
            obj.save()

    def get_change_form_initial(self, request, obj=None):
        """Добавляем начальные данные для формы."""
        initial = super().get_change_form_initial(request, obj)
        if obj and obj.xml_data:
            initial['xml_data'] = obj.xml_data  # Загружаем XML-данные для редактирования

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file', 'content']

    def save(self, commit=True):
        document = super().save(commit=False)

        if 'file' in self.changed_data:  # Проверяем, изменился ли файл
            doc = DocxDocument(document.file)
            document.content = "\n".join([p.text for p in doc.paragraphs])

        if commit:
            document.save()
        return document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    form = DocumentForm
    list_display = ['name', 'file', 'content']
    search_fields = ['name']
    readonly_fields = []  # Разрешаем редактирование content

    def save_model(self, request, obj, form, change):
        """Перезаписываем content только если загружен новый файл"""
        if 'file' in form.changed_data:
            obj.content = obj.read_docx(obj.file.path)
        super().save_model(request, obj, form, change)

