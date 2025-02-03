from tkinter.font import names

from django.urls import path
from . import views

urlpatterns = [
    path('main_menu/', views.main_menu, name='main_menu'),
    path('peculiarities/', views.peculiarities, name='peculiarities'),
    path('solutions/', views.solutions, name='solutions'),
    path('block/', views.block, name='block'),
    path('activity/', views.activity, name='activity'),
    path('sipoc/', views.sipoc, name='sipoc'),
    path('swim/', views.swim, name='swim'),
    path('log_in/', views.log_in, name='log_in'),
    path('sig_in/', views.sig_in, name='sig_in'),
    path('accountModal/', views.account_modal, name='accountModal'),

]