from django.urls import path
from .views import save_bpmn, load_bpmn, list_diagrams

urlpatterns = [
    path('save/', save_bpmn),
    path('load/<int:diagram_id>/', load_bpmn),
    path('list/', list_diagrams),
]