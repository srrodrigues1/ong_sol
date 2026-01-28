from django.shortcuts import render
from functools import wraps
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone

from .models import Waitlist, Person
from equipments.models import Equipment
from datetime import datetime, date

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect(reverse('login:index'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def index(request):
    return render(request, 'waitlist/index.html', {})

@login_required
def waitlist_parciais(request):
    waitlists = Waitlist.objects.select_related("person", "equipment").order_by("contact_date")

    data = []
    for w in waitlists:
        data.append({
            "id": w.id,
            "person_name": w.person.name,
            "person_phone": w.person.phone if hasattr(w.person, 'phone') else '',
            "person_ddd": w.person.ddd if hasattr(w.person, 'ddd') else '',
            "equipment_name": w.equipment.name + ' (' + (getattr(w.equipment.type, 'name', '') if w.equipment.type else '') + ')',
            "dt_contact": w.contact_date.strftime("%d/%m/%Y") if w.contact_date else "",
            "create_date": w.create_date.strftime("%d/%m/%Y %H:%M") if w.create_date else "",
        })
        
    return render(request, 'waitlist/tabela_waitlist.html', {
        'waitlists': data
    })


@login_required
def criar_waitlist(request):
    if request.method == 'POST':

        person_id = request.POST.get('person')
        equipment_id = request.POST.get('equipment')
        dt_contact = request.POST.get('dt_contact')

        person = get_object_or_404(Person, id=person_id)
        equipment = get_object_or_404(Equipment, id=equipment_id)

        Waitlist.objects.create(
            person=person,
            equipment=equipment,
            contact_date=datetime.strptime(dt_contact, '%d/%m/%Y'),
        )

        return JsonResponse({'success': f"Espera para {person.name} criada com sucesso!"})

    return JsonResponse({'error': 'Método inválido'}, status=405)

@login_required
def dados_waitlist(request, waitlist_id):
    try:
        waitlist = Waitlist.objects.prefetch_related("person", "equipment").get(id=waitlist_id)

        data = {
            "id": waitlist.id,
            "person_id": waitlist.person.id,
            "equipment_id": waitlist.equipment.id,
            "name": waitlist.person.name,
            "dt_contact": waitlist.contact_date.strftime("%d/%m/%Y")
        }
        return JsonResponse(data)
    except Waitlist.DoesNotExist:
        return JsonResponse({'error': 'Espera não encontrada'}, status=404)

@login_required
@require_POST
def atualizar_waitlist(request, waitlist_id):
    if request.method == 'POST':
        person_id = request.POST.get('person_edit')
        equipment_id = request.POST.get('equipment_edit')
        dt_contact = request.POST.get('dt_contact_edit')

        waitlist = get_object_or_404(Waitlist, id=waitlist_id)

        if person_id:
            waitlist.person = Person.objects.get(id=person_id)
        if equipment_id:
            waitlist.equipment = Equipment.objects.get(id=equipment_id)
        if dt_contact:
            waitlist.contact_date = datetime.strptime(dt_contact, '%d/%m/%Y')
            
        waitlist.save()
        return JsonResponse({'success': f"Espera atualizada com sucesso!"})

    return JsonResponse({'error': 'Métoexcluir_waitlistdo não permitido'}, status=405)

@login_required
def excluir_waitlist(request, waitlist_id):
    waitlist = get_object_or_404(Waitlist, id=waitlist_id)
    waitlist.delete()
    return JsonResponse({'success': f"Espera excluída com sucesso!"})

@login_required
def obter_informacoes_formulario(request):
    persons = Person.objects.all().order_by("name")
    equipments = Equipment.objects.select_related("type").order_by("name")

    person_data = []
    equipment_data = []
    
    for p in persons:
        person_data.append({
            "id": p.id,
            "name": p.name
        })

    for e in equipments:
        equipment_data.append({
            "id": e.id,
            "name": e.name,
            "type": e.type.name if e.type else None
        })

    return JsonResponse({
        "persons": person_data,
        "equipments": equipment_data
    })