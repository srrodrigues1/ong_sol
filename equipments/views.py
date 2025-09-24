from django.shortcuts import render
from functools import wraps
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect(reverse('login:index'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

from .models import Equipment

@login_required
def index(request):
    equipments = Equipment.objects.all().order_by("id")
    return render(request, 'equipments/index.html', {
        'equipment': equipments
    })

@login_required
def criar_equipamento(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        location = request.POST.get('location')
        status = request.POST.get('status')

        erros = {}
        Equipment.objects.create(
            name=name,
            type=type,
            location=location,
            status=status
        )

        return JsonResponse({"status": "success", "message": "Equipamento cadastrado com sucesso!"})

@login_required
def equipamentos_parciais(request):
    equipments = Equipment.objects.all().order_by("id")
    return render(request, 'equipments/tabela_equipamentos.html', {
        'equipments': equipments
    })

@login_required
def dados_equipamento(request, equipment_id):
    try:
        equipment = Equipment.objects.get(id=equipment_id)
        data = {
            'id': equipment.id,
            'name': equipment.name,
            'type': equipment.type,
            'location': equipment.location,
            'requester': 1,# equipment.requester,
            'status': equipment.status,
            'create_date': equipment.create_date,
        }
        return JsonResponse(data)
    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado'}, status=404)