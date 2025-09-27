from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from functools import wraps

from .models import Person

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect(reverse('login:index'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def index(request):
    persons = Person.objects.all().order_by("id")
    return render(request, 'persons/index.html', {
        'persons': persons
    })

def criar_pessoa(request):
    return None

@login_required
def pessoas_parciais(request):
    persons = Person.objects.all().order_by("id")
    return render(request, 'persons/tabela_pessoas.html', {
        'persons': persons
    })