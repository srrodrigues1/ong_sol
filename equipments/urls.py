from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("novo", views.criar_equipamento, name="criar_equipamento"),
    # path("list", views.exportar_equipamento_csv, name="exportar_equipamento_csv"),
    # path("<int:equipment_id>/", views.dados_equipamento, name="dados_equipamento"),
    # path("update/<int:equipment_id>/", views.atualizar_equipamento, name="atualizar_equipamento"),
    # path("delete/<int:equipment_id>/", views.excluir_equipamento, name="excluir_equipamento"),
    # path("<int:equipment_id>/", views.emprestar_equipamento, name="emprestar_equipamento")
]