from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect   

urlpatterns = [
    path("", lambda request: redirect("login:index")),
    path("login/", include("login.urls")),
    path("users/", include("users.urls")),
    path("equipments/", include("equipments.urls")),
    path("persons/", include("persons.urls")),
    path("admin/", admin.site.urls),
]