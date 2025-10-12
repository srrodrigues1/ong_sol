from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("novo", views.criar_pessoa, name="criar_pessoa"),
    # path("list", views.exportar_equipamento_csv, name="exportar_equipamento_csv"),
    path("<int:person_id>/", views.dados_pessoa, name="dados_pessoa"),
    path("update/<int:person_id>/", views.atualizar_pessoa, name="atualizar_pessoa"),
    path("delete/<int:person_id>/", views.excluir_pessoa, name="excluir_pessoa"),
    path("partials", views.pessoas_parciais, name="pessoas_parciais")
]