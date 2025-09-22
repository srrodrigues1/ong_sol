from django.shortcuts import render
from functools import wraps
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

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
def equipamentos_parciais(request):
    users = Equipment.objects.all().order_by("id")
    return render(request, 'equipments/tabela_equipamentos.html', {
        'users': users
    })
