from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from functools import wraps
from django.http import JsonResponse
from .models import Person, Documents

import re

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