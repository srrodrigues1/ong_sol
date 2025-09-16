
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password

from users.models import User

def index(request):
    return render(request, 'login/index.html', {
    })

def logar(request):
    if request.method == "POST":
        cpf = request.POST.get("cpf")
        password = request.POST.get("senha")

        formated_cpf = cpf.replace('.', '')
        formated_cpf = cpf.replace('-', '')

        user = User.objects.filter(cpf=cpf).first()

        if user:
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                return JsonResponse({"success": True, "message": "Usuário encontrado"})
            else:
                return JsonResponse({"success": False, "message": "Usuário ou senha inválidos!"})
        else:                
            return JsonResponse({"success": False, "message": "Usuário ou senha inválidos!"})

    # Se for GET, só renderiza a página de login
    return render(request, "login/index.html")