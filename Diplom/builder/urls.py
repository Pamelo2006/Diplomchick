from django.urls import path
from .views import save_bpmn, load_bpmn, list_diagrams, back_to_diagrams, export_diagram

urlpatterns = [
    path('save/', save_bpmn),
    path('load/<int:diagram_id>/', load_bpmn),
    path('list/', list_diagrams),
    path('back-to-diagrams/', back_to_diagrams, name='back_to_diagrams'),
    path('export/', export_diagram, name='export_diagram'),
]