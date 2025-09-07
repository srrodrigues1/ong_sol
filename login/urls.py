from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("logar", views.fazer_login, name="logar"),
]