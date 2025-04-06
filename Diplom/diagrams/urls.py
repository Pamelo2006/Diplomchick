from django.urls import path
from . import views
from .views import peculiarities_view
from django.conf.urls.static import static
from django.conf import settings
from .views import my_diagrams
from .views import my_diagrams
from .views import get_bpmn_xml, templates, view_diagram, view_diagram1
from builder.views import save_bpmn_admin

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
    path('create_bpmn/', views.create_bpmn, name='create_bpmn'),
    path('bpmn-editor/<int:pk>/', views.bpmn_editor, name='bpmn_editor'),
    path('editor/', views.bpmn_editor, name='bpmn_editor_new'),
    path('save_bpmn/', views.save_bpmn_xml, name='save_bpmn_xml'),
    path('templates/', templates, name='templates'),
    path('view/<int:id>/', view_diagram, name='view_diagram'),  # Изменено
    path('view1/<int:id>/', view_diagram1, name='view_diagram1'),  # Изменено
    path('admin/chat/', views.chat_admin, name='chat_admin'),
    path('chat/history/', views.chat_history, name='chat_history'),
    path('admin/chat/history/', views.chat_history, name='chat_history'),
    path('set_language/', views.set_language, name='set_language'),
    path('update_theme/', views.update_theme, name='update_theme'),
    path('get_user_theme/', views.get_user_theme, name='get_user_theme'),
    path('editor/', views.bpmn_editor, name='bpmn_editor_new'),
    path('builder/save/', views.save_bpmn_xml, name='save_bpmn_xml'),  # Для админки
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)