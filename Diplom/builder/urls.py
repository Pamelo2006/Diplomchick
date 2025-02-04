from django.urls import path
from .views import save_bpmn, load_bpmn

urlpatterns = [
    path('builder/save/', save_bpmn, name='save_bpmn'),
    path('builder/load/<int:diagram_id>/', load_bpmn, name='load_bpmn'),
]