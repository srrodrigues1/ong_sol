from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("novo", views.criar_equipamento, name="criar_equipamento"),
    path("list", views.exportar_equipamento_csv, name="exportar_equipamento_csv"),
    path("<int:equipment_id>/", views.dados_equipamento, name="dados_equipamento"),
    path("update/<int:equipment_id>/", views.atualizar_equipamento, name="atualizar_equipamento"),
    path("delete/<int:equipment_id>/", views.excluir_equipamento, name="excluir_equipamento"),
    path("loan/<int:equipment_id>/", views.dados_emprestimo, name="dados_emprestimo"),
    path("loan/save/<int:equipment_id>/", views.fazer_emprestimo, name="fazer_emprestimo"),
    path("partials", views.equipamentos_parciais, name="equipamentos_parciais")
]