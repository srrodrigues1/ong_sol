from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from functools import wraps
from django.http import JsonResponse
from .models import Person, Documents

import re
from datetime import datetime

def format_cep(cep):
    digits = re.sub(r'\D', '', cep)

    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    else:
        return cep

def format_phone(phone):
    digits = re.sub(r'\D', '', phone)

    if len(digits) == 9:
        return f"{digits[0]} {digits[1:5]}-{digits[5:]}"
    elif len(digits) == 8:  # caso não tenha o 9 inicial
        return f"9 {digits[0:4]}-{digits[4:]}"
    else:
        return phone
    
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

@login_required
def index(request):
    return render(request, 'persons/index.html', {})

@login_required
def criar_pessoa(request):
    if request.method == "POST":

        name = request.POST.get("name")
        cpf = request.POST.get("cpf")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        erros = {}
        formated_cpf = cpf.replace('.', '')
        formated_cpf = formated_cpf.replace('-', '')

        formated_phone = phone.replace('-', '')
        formated_phone = formated_phone.strip()
        formated_phone = formated_phone.replace(" ", "")

        if Person.objects.filter(cpf=formated_cpf).exists():
            erros["cpf"] = f"O CPF <b>{cpf}</b> já está cadastrado."

        if len(formated_cpf) < 11:
            erros["cpf"] = f"O CPF <b>{cpf}</b> não é válido."

        if Person.objects.filter(email=email).exists():
            erros["email"] = f"O e-mail <b>{email}</b> já está cadastrado."

        if erros:
            return JsonResponse({'error': erros}, status=400)

        person = Person.objects.create(
            name=name,
            cpf=formated_cpf,
            email=email,
            phone=formated_phone,
            ddd=request.POST.get("ddd"),
            state=request.POST.get("state"),
            city=request.POST.get("city"),
            district=request.POST.get("district"),
            street=request.POST.get("street"),
            st_number=request.POST.get("st_number"),
            cep=request.POST.get("cep"),
            birth_date=datetime.strptime(request.POST.get("birth_date"), '%d/%m/%Y'),
        )

        for f in request.FILES.getlist("documents[]"):
            Documents.objects.create(person=person, image=f)

        return JsonResponse({'success': f"Pessoa {name} criado com sucesso!"})

    return JsonResponse({'error': 'Método inválido'}, status=405)

@login_required
def pessoas_parciais(request):
    persons = Person.objects.all().order_by("id")
    for person in persons:
        person.cpf = format_cpf(person.cpf)

    return render(request, 'persons/tabela_pessoas.html', {
        'persons': persons
    })

@login_required
def dados_pessoa(request, person_id):
    try:
        person = Person.objects.prefetch_related("loans__requester").get(id=person_id)

        loaned = False
        loan = person.loans.filter(status=1, return_date__isnull=True).first()
        if loan:
            loaned = True

        person.cpf = format_cpf(person.cpf)
        person.phone = format_phone(person.phone)
        person.cep = format_cep(person.cep)

        documents = [
            {
                "id": doc.id,
                "url": doc.image.url,
                "name": doc.image.name.split('/')[-1],
            }
            for doc in Documents.objects.filter(person_id=person_id)
        ]

        data = {
            'id': person.id,
            'name': person.name,
            'cpf': person.cpf,
            'phone': person.phone,
            'email': person.email,
            'ddd': person.ddd,
            'state': person.state,
            'city': person.city,
            'district': person.district,
            'street': person.street,
            'st_number': person.st_number,
            'cep': person.cep,
            'status': person.status,
            'birth_date': person.birth_date.strftime("%d/%m/%Y"),
            'create_date': person.create_date,
            'loaned': loaned,
            'documents': documents,
        }
        return JsonResponse(data)

    except Person.DoesNotExist:
        return JsonResponse({'error': 'Pessoa não encontrada'}, status=404)