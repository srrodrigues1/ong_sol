from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect   
from django.conf import settings
from django.conf.urls.static import static
from login.views import protected_media

urlpatterns = [
    path("", lambda request: redirect("login:index")),
    path("login/", include("login.urls")),
    path("users/", include("users.urls")),
    path("equipments/", include("equipments.urls")),
    path("persons/", include("persons.urls")),
    path("admin/", admin.site.urls),
    path('media/<path:path>', protected_media, name='protected_media')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)