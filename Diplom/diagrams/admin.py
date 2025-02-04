from django.contrib import admin
from django import forms
from .models import Document
from docx import Document as DocxDocument

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

admin.site.register(Document, DocumentAdmin)
