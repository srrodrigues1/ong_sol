from django.shortcuts import render
from functools import wraps
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

import csv

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
    

@login_required
@require_POST
def atualizar_equipamento(request, equipment_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        location = request.POST.get('location')
        status = request.POST.get('status')

        erros = {}

        equipment = get_object_or_404(Equipment, id=equipment_id)

        equipment.name = name
        equipment.type = type
        equipment.location = location
        equipment.status = status

        equipment.save()
        return JsonResponse({'success': f"Equipamento {name} atualizado com sucesso!"})

    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required
def exportar_equipamento_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="equipamento.csv"'

    writer = csv.writer(response)

    writer.writerow(["ID", "Nome", "Tipo", "Localização", "Status"])

    equipments = Equipment.objects.all().order_by("id").values_list("id", "name", "type", "location", "status")
    for equipment in equipments:
        writer.writerow(equipment)

    return response

@login_required
@require_POST
def excluir_equipamento(request, equipment_id):
    equipamento = get_object_or_404(Equipment, id=equipment_id)

    try:
        nome = equipamento.name
        equipamento.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return JsonResponse({'success': f"Equipamento {nome} excluído com sucesso!"})

    except ProtectedError:
        msg = 'Não foi possível excluir este equipamento: existem registros vinculados a ele.'
        return JsonResponse({'error': msg}, status=400)