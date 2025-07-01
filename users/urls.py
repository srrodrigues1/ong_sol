from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("novo", views.criar_usuario, name="criar_usuario"),
    path("<int:user_id>/", views.dados_usuario, name="dados_usuario"),
    path("update/<int:user_id>/", views.atualizar_usuario, name="atualizar_usuario")
]