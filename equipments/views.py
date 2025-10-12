from functools import wraps
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone

import csv
import re
from datetime import datetime, date

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except (ValueError, TypeError):
        return False

def format_cpf(cpf: str) -> str:
    cpf = re.sub(r'\D', '', cpf)  # só números
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

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

    days_loaned = None
    equipamentos_com_requester = []
    for eq in equipments:
        loan = eq.loans.filter(status=1, return_date__isnull=True).first()
        requester_name = loan.requester.name if loan else ""
        if loan and loan.loan_date:
            days_loaned = (date.today() - loan.loan_date.date()).days
        else:
            days_loaned = None
        
        equipamentos_com_requester.append({
            "id": eq.id,
            "name": eq.name,
            "requester": requester_name,
            "location": eq.location,
            "status": eq.status,
            'days_loaned': days_loaned,
            "create_date": eq.create_date
        })

    return render(request, 'equipments/tabela_equipamentos.html', {
        'equipments': equipamentos_com_requester
    })

@login_required
def dados_equipamento(request, equipment_id):
    try:
        equipment = Equipment.objects.prefetch_related("loans__requester").get(id=equipment_id)

        loaned = False
        loan = equipment.loans.filter(status=1, return_date__isnull=True).first()
        if loan:
            loaned = True

        data = {
            'id': equipment.id,
            'name': equipment.name,
            'type': equipment.type,
            'location': equipment.location,
            'loaned': loaned,
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

        equipment = get_object_or_404(Equipment, id=equipment_id)

        if name:
            equipment.name = name
        if type:
            equipment.type = type
        if location:        
            equipment.location = location
        if status:
            equipment.status = status

        equipment.save()
        return JsonResponse({'success': f"Equipamento {equipment.name} atualizado com sucesso!"})

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
        return JsonResponse({'error': msg})

@login_required
def fazer_emprestimo(request, equipment_id):
    if request.method == "POST":
        requester_id = request.POST.get('requester_id')
        loan_date = request.POST.get('loan_date')

        if not is_valid_date(loan_date):
            errors = {"dt_loaned_loan": "A data precisa estar no formato dd/mm/aaaa!"}
            return JsonResponse({"status": "warning", "error": errors})

        try:
            equipment = Equipment.objects.get(id=equipment_id)
            requester = Person.objects.get(id=requester_id)

            Loans.objects.create(
                equipment=equipment,
                requester=requester,
                loan_date=datetime.strptime(loan_date, '%d/%m/%Y'),
                status=1 
            )
    
            equipment.location = f"{requester.street}, {requester.st_number} - {requester.district} - {requester.city}"
            equipment.status = 2
            equipment.save()

            return JsonResponse({"status": "success", "message": f"Equipamento {equipment.name} emprestado com sucesso para {requester.name}!"})
        except (Equipment.DoesNotExist, Person.DoesNotExist):
            return JsonResponse({"error": "Dados inválidos"}, status=400)

def dados_emprestimo(request, equipment_id):
    try:
        equipment = Equipment.objects.prefetch_related("loans__requester").get(id=equipment_id)

        loan = equipment.loans.filter(status=1, return_date__isnull=True).first()
        requester_id = loan.requester.id if loan else None

        persons = Person.objects.all().order_by("name")
        persons_data = [
            {"id": p.id, "name": p.name, "cpf": format_cpf(p.cpf)} 
            for p in persons
        ]

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
                "requester_cpf": format_cpf(loan.requester.cpf) if loan else None,
                "loan_date": loan.loan_date.strftime("%d/%m/%Y") if loan and loan.loan_date else None,
            },
            "persons": persons_data,
        }
        return JsonResponse(data)

    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Equipamento não encontrado'}, status=404)
    
@login_required
def remover_emprestimo(request, equipment_id):
    if request.method != "POST":
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    return_date = request.POST.get("returnDate")
    if not is_valid_date(return_date):
        errors = {"dt_return_loan": "A data precisa estar no formato dd/mm/aaaa!"}
        return JsonResponse({"status": "warning", "error": errors})

    try:
        equipment = Equipment.objects.prefetch_related("loans__requester").get(id=equipment_id)

        with transaction.atomic():
            active_loan = Loans.objects.filter(
                equipment=equipment,
                status=1,
                return_date__isnull=True
            ).first()

            if not active_loan:
                return JsonResponse({'error': 'Nenhum empréstimo ativo encontrado.'}, status=404)

            active_loan.return_date = datetime.strptime(return_date, '%d/%m/%Y')
            active_loan.status = 2
            active_loan.save()

            equipment.status = 1
            equipment.location = "Ong Sol"
            equipment.save()

        return JsonResponse({"status": "success", "message": "Empréstimo removido com sucesso." })

    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Equipamento não encontrado.'}, status=404)

    except Exception as e:
        return JsonResponse({'error': f'Erro ao remover empréstimo: {str(e)}'}, status=500)

