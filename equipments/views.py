from functools import wraps
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone

import csv
import json

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect(reverse('login:index'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

from .models import Equipment, Loans
from persons.models import Person

@login_required
def index(request):
    return render(request, 'equipments/index.html', {})

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
    equipments = Equipment.objects.prefetch_related("loans__requester").order_by("id")

    equipamentos_com_requester = []
    for eq in equipments:
        loan = eq.loans.filter(status=0, return_date__isnull=True).first()
        requester_name = loan.requester.name if loan else ""
        
        equipamentos_com_requester.append({
            "id": eq.id,
            "name": eq.name,
            "requester": requester_name,
            "location": eq.location,
            "status": eq.status,
            "create_date": eq.create_date
        })

    return render(request, 'equipments/tabela_equipamentos.html', {
        'equipments': equipamentos_com_requester
    })

@login_required
def dados_equipamento(request, equipment_id):
    try:
        equipment = Equipment.objects.get(id=equipment_id)# Equipment.objects.prefetch_related("loans__requester").get(id=equipment_id)

        # loan = equipment.loans.first()
        # requester_name = loan.requester.name if loan else None

        data = {
            'id': equipment.id,
            'name': equipment.name,
            'type': equipment.type,
            'location': equipment.location,
            # 'requester': requester_name,
            'status': equipment.status,
            'create_date': equipment.create_date
        }
        return JsonResponse(data)

    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Equipamento não encontrado'}, status=404)
    
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

@login_required
def fazer_emprestimo(request, equipment_id):
    if request.method == "POST":
        requester_id = request.POST.get('requester_id')

        try:
            equipment = Equipment.objects.get(id=equipment_id)
            requester = Person.objects.get(id=requester_id)

            with transaction.atomic():
                active_loan = Loans.objects.filter(equipment=equipment, return_date__isnull=True).first()

                if active_loan:
                    active_loan.return_date = timezone.now()
                    active_loan.status = 1
                    active_loan.save()

            loan = Loans.objects.create(
                equipment=equipment,
                requester=requester,
                status=0
            )
    
            equipment.location = f"{requester.street}, {requester.st_number} - {requester.district} - {requester.city}"
            equipment.status = 2
            equipment.save()

            return JsonResponse({"success": True, "loan_id": loan.id})
        except (Equipment.DoesNotExist, Person.DoesNotExist):
            return JsonResponse({"error": "Dados inválidos"}, status=400)

def dados_emprestimo(request, equipment_id):
    try:
        equipment = Equipment.objects.prefetch_related("loans__requester").get(id=equipment_id)

        # Pega o empréstimo ativo (se houver)
        loan = equipment.loans.filter(status=1).first()  # supondo que tenha campo "active"
        requester_id = loan.requester.id if loan else None

        # Lista de todas as pessoas (para popular o select no form)
        persons = Person.objects.all().order_by("name")
        persons_data = [{"id": p.id, "name": p.name} for p in persons]

        data = {
            "equipment": {
                "id": equipment.id,
                "name": equipment.name,
                "type": equipment.type,
                "location": equipment.location,
                "status": equipment.status,
                "create_date": equipment.create_date,
            },
            "loan": {
                "id": loan.id if loan else None,
                "requester_id": requester_id,
                "requester_name": loan.requester.name if loan else None,
            },
            "persons": persons_data,
        }
        return JsonResponse(data)

    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Equipamento não encontrado'}, status=404)