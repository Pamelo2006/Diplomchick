from django.urls import path
from .views import save_bpmn, load_bpmn, list_diagrams, back_to_diagrams

urlpatterns = [
    path('save/', save_bpmn),
    path('load/<int:diagram_id>/', load_bpmn),
    path('list/', list_diagrams),
    path('back-to-diagrams/', back_to_diagrams, name='back_to_diagrams'),
]