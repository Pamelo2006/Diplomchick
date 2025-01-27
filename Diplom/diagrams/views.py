from django.shortcuts import render

def main_menu(request):
    return render(request, 'diagrams/main_menu.html')
def peculiarities(request):
    return render(request, 'diagrams/peculiarities.html')
