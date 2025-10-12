from django.urls import path

from . import views

app_name = "login"

urlpatterns = [
    path("", views.index, name="index"),
    path("logar", views.logar, name="logar"),
    path("deslogar", views.deslogar, name="deslogar"),
    path("obter_usuario", views.obter_usuario, name="obter_usuario"),
    path("check_session", views.check_session, name="check_session"),
]