from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from functools import wraps

import csv
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

def validar_senha(senha):
    tem_especial = re.search(r'[^a-zA-Z0-9]', senha) 
    return len(senha) >= 6 and tem_especial

from .models import User, Role

@login_required
def index(request):
    return render(request, 'users/index.html', {})

@login_required
def criar_usuario(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
        senha = request.POST.get('password')
        status = 1
        funcao_id = request.POST.get('funcao')

        erros = {}
        formated_cpf = cpf.replace('.', '')
        formated_cpf = formated_cpf.replace('-', '')

        if User.objects.filter(cpf=formated_cpf).exists():
            erros["cpf"] = f"O CPF <b>{cpf}</b> já está cadastrado."

        if len(formated_cpf) < 11:
            erros["cpf"] = f"O CPF <b>{cpf}</b> não é válido."

        if User.objects.filter(email=email).exists():
            erros["email"] = f"O e-mail <b>{email}</b> já está cadastrado."

        if senha:
            if not validar_senha(senha):
                erros["senha"] = "A senha deve ter no mínimo 6 caracteres e conter letras e números."

        if erros:
            return JsonResponse({'error': erros}, status=400)
        
        senha_hash = make_password(senha)
        funcao = Role.objects.get(id = funcao_id) if funcao_id else None

        User.objects.create(
            username=username,
            cpf=formated_cpf,
            email=email,
            password=senha_hash,
            status=status,
            role=funcao
        )

        return JsonResponse({'success': f"Usuário {username} criado com sucesso!"})

    return JsonResponse({'error': 'Método inválido'}, status=405)

@login_required
def dados_usuario(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        data = {
            'id': user.id,
            'username': user.username,
            'cpf': format_cpf(user.cpf),
            'email': user.email,
            'status': user.status,
            'funcao': user.role_id,
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado'}, status=404)

@login_required
@require_POST
def atualizar_usuario(request, user_id):
    if request.method == 'POST':
        username = request.POST.get('username')
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
        senha = request.POST.get('password')
        status = request.POST.get('status')
        funcao_id = request.POST.get('funcao')

        erros = {}

        usuario = get_object_or_404(User, id=user_id)

        formated_cpf = cpf.replace('.', '')
        formated_cpf = formated_cpf.replace('-', '')
        
        if User.objects.filter(cpf=formated_cpf).exclude(id=usuario.id).exists():
            erros["cpf"] = f"O CPF <b>{cpf}</b> já está cadastrado."

        if len(formated_cpf) < 11:
            erros["cpf"] = f"O CPF <b>{cpf}</b> não é válido."

        if User.objects.filter(email=email).exclude(id=usuario.id).exists():
            erros["email"] = f"O e-mail <b>{email}</b> já está cadastrado."

        if senha:
            if not validar_senha(senha):
                erros["senha"] = "A senha deve ter no mínimo 6 caracteres e conter um caractere especial"

        if erros:
            return JsonResponse({'error': erros}, status=400)

        usuario.username = username
        usuario.cpf = formated_cpf
        usuario.email = email
        usuario.status = status

        if senha:
            usuario.password = make_password(senha)

        if funcao_id:
            usuario.role = Role.objects.get(id=funcao_id)

        usuario.save()
        return JsonResponse({'success': f"Usuário {username} atualizado com sucesso!"})

    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required
@require_POST
def excluir_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    
    if usuario.id == request.session.get('user_id'):
        return JsonResponse({'error': 'Você não pode excluir a si mesmo.'}, status=400)

    try:
        nome = usuario.username
        usuario.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return JsonResponse({'success': f"Usuário {nome} excluído com sucesso!"})

    except ProtectedError:
        msg = 'Não foi possível excluir este usuário: existem registros vinculados a ele.'
        return JsonResponse({'error': msg}, status=400)

@login_required
def exportar_usuario_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'

    writer = csv.writer(response)

    writer.writerow(["ID", "Username", "Email", "CPF", "Status", "Função"])

    users = User.objects.all().order_by("id").values_list("id", "username", "email", "cpf", "status", "role_name")
    for user in users:
        writer.writerow(user)

    return response

@login_required
def usuarios_parciais(request):
    users = User.objects.all().order_by("id")
    for user in users:
        user.formatted_cpf = format_cpf(user.cpf)
    return render(request, 'users/tabela_usuarios.html', {
        'users': users
    })

