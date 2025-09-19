from django.shortcuts import render
from .models import Equipment

def index(request):
    equipments = Equipment.objects.all().order_by("id")
    return render(request, 'equipment/index.html', {
        'equipment': equipments
    })