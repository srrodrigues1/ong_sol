
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password

from users.models import User

def index(request):
    return render(request, 'login/index.html', {})

def logar(request):
    if request.method == "POST":
        cpf = request.POST.get("cpf")
        password = request.POST.get("senha")

        formated_cpf = cpf.replace('.', '')
        formated_cpf = formated_cpf.replace('-', '')

        user = User.objects.filter(cpf=formated_cpf, status=1).first()

        if user:
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                return JsonResponse({"success": True, "message": "Usuário logado com sucesso!"})
            else:
                return JsonResponse({"success": False, "message": "Usuário ou senha inválidos!"})
        else:                
            return JsonResponse({"success": False, "message": "Usuário ou senha inválidos!"})

    return render(request, "login/index.html")

def deslogar(request):
    if request.method == "POST":
        request.session.flush()
        return JsonResponse({"success": True, "message": "Deslogando usuário"})
    
    return render(request, "login/index.html")

def obter_usuario(request):
    user_id = request.session.get("user_id")
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            user_data = {
                'username': user.username,
            }
            return JsonResponse({"success": True, "user": user_data, "message": "Usuário logado"})
        except User.DoesNotExist:
            pass
    
    return JsonResponse({"success": False, "message": "Usuário não está autenticado"})

def check_session(request):
    logged_in = bool(request.session.get('user_id'))
    return JsonResponse({'logged_in': logged_in})