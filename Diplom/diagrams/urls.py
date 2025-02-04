from django.urls import path
from . import views
from .views import peculiarities_view
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.main_menu, name='main_menu'),
    path('peculiarities/', peculiarities_view, name='peculiarities'),
    path('solutions/', views.solutions, name='solutions'),
    path('block/', views.block, name='block'),
    path('activity/', views.activity, name='activity'),
    path('sipoc/', views.sipoc, name='sipoc'),
    path('swim/', views.swim, name='swim'),
    path('log_in/', views.log_in, name='log_in'),
    path('sig_in/', views.sig_in, name='sig_in'),
    path('accountModal/', views.account_modal, name='accountModal'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)