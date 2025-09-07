from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
import re

def validar_senha(senha):
    tem_letra = re.search(r'[a-zA-Z]', senha)
    tem_numero = re.search(r'\d', senha)
    return len(senha) >= 6 and tem_letra and tem_numero

from .models import User, Role

def index(request):
    users = User.objects.all().order_by("id")
    return render(request, 'users/index.html', {
        'users': users
    })

def criar_usuario(request):
    if request.method == 'POST':
                  
        username = request.POST.get('username')
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
        senha = request.POST.get('password')
        status = 1
        funcao_id = request.POST.get('funcao')

        erros = {}
        formated_cpf = cpf.replace('.', '');
        formated_cpf = cpf.replace('-', '');

        if User.objects.filter(cpf=cpf).exists():
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

        messages.success(request, f"Usuário '{username}' criado com sucesso!")

        User.objects.create(
            username=username,
            cpf=cpf,
            email=email,
            password=senha_hash,
            status=status,
            role=funcao
        )
        return redirect('users/index.html')
        # return JsonResponse({'success': f"Usuário {username} criado com sucesso!"})

    return JsonResponse({'error': 'Método inválido'}, status=405)

def dados_usuario(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        data = {
            'id': user.id,
            'username': user.username,
            'cpf': user.cpf,
            'email': user.email,
            'status': user.status,
            'funcao': user.role_id,
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado'}, status=404)

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

        if User.objects.filter(cpf=cpf).exclude(id=usuario.id).exists():
            erros["cpf"] = f"O CPF <b>{cpf}</b> já está cadastrado."

        formated_cpf = cpf.replace('.', '');
        formated_cpf = cpf.replace('-', '');

        if len(formated_cpf) < 11:
            erros["cpf"] = f"O CPF <b>{cpf}</b> não é válido."

        if User.objects.filter(email=email).exclude(id=usuario.id).exists():
            erros["email"] = f"O e-mail <b>{email}</b> já está cadastrado."

        if senha:
            if not validar_senha(senha):
                erros["senha"] = "A senha deve ter no mínimo 6 caracteres e conter letras e números."

        if erros:
            return JsonResponse({'error': erros}, status=400)

        usuario.username = username
        usuario.cpf = cpf
        usuario.email = email
        usuario.status = status

        if senha:
            usuario.password = make_password(senha)

        if funcao_id:
            usuario.role = Role.objects.get(id=funcao_id)

        usuario.save()

        messages.success(request, f"Usuário '{username}' atualizado com sucesso!")
        return redirect('/users')  # ou ajuste conforme a sua URL

    return JsonResponse({'error': 'Método não permitido'}, status=405)

# views.py
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .models import User   # ajuste o import conforme a sua estrutura


@require_POST
def excluir_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if usuario == request.user:
        return JsonResponse({'error': 'Você não pode excluir a si mesmo.'}, status=400)
    if usuario.is_superuser:
        return JsonResponse({'error': 'Não é permitido excluir um superusuário.'}, status=400)

    try:
        nome = usuario.username
        usuario.delete()

        messages.success(request, f"Usuário '{nome}' excluído com sucesso!")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('/users')

    except ProtectedError:
        msg = 'Não foi possível excluir este usuário: existem registros vinculados a ele.'
        return JsonResponse({'error': msg}, status=400)
