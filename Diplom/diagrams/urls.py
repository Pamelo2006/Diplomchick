from django.urls import path
from . import views
from .views import peculiarities_view
from django.conf.urls.static import static
from django.conf import settings
from .views import my_diagrams
from .views import get_bpmn_xml, save_bpmn_xml, templates, view_diagram, view_diagram1

urlpatterns = [
    path('main_menu/', views.main_menu, name='main_menu'),
    path('peculiarities/', peculiarities_view, name='peculiarities'),
    path('solutions/', views.solutions, name='solutions'),
    path('block/', views.block, name='block'),
    path('activity/', views.activity, name='activity'),
    path('sipoc/', views.sipoc, name='sipoc'),
    path('swim/', views.swim, name='swim'),
    path('account_modal/', views.account_modal, name='account_modal'),
    path('my_diagrams/', my_diagrams, name='my_diagrams'),
    path('<int:pk>/get_xml/', get_bpmn_xml, name='get_bpmn_xml'),
    path('save_bpmn/', views.save_bpmn_xml, name='save_bpmn_xml'),
    path('create_bpmn/', views.create_bpmn, name='create_bpmn'),
    path('bpmn-editor/<int:pk>/', views.bpmn_editor, name='bpmn_editor'),  # Редактирование диаграммы по pk
    path('editor/', views.bpmn_editor, name='bpmn_editor_new'),
    path('builder/save/', views.save_bpmn_xml, name='save_bpmn_xml'),
    path('templates/', templates, name='templates'),
    path('diagrams/view/<int:id>/', view_diagram, name='view_diagram'),
    path('diagrams/view1/<int:id>/', view_diagram1, name='view_diagram1'),
    path('builder/save1/', views.save_diagram, name='save_diagram'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)