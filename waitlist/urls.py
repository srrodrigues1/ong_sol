from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("novo", views.criar_waitlist, name="criar_waitlist"),
    path("info_form", views.obter_informacoes_formulario, name="obter_informacoes_formulario"),
    # path("list", views.exportar_equipamento_csv, name="exportar_equipamento_csv"),
    path("<int:waitlist_id>/", views.dados_waitlist, name="dados_waitlist"),
    path("update/<int:waitlist_id>/", views.atualizar_waitlist, name="atualizar_waitlist"),
    path("delete/<int:waitlist_id>/", views.excluir_waitlist, name="excluir_waitlist"),
    path("partials", views.waitlist_parciais, name="waitlist_parciais")
]