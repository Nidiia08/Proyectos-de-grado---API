"""Rutas principales del proyecto."""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.usuarios.urls")),
    path("api/", include("apps.proyectos.urls")),
    path("api/", include("apps.fases.urls")),
    # Keep dedicated template API before documentos to avoid /api/plantillas/ route shadowing.
    path("api/", include("apps.plantillas.urls")),
    path("api/", include("apps.documentos.urls")),
    path("api/", include("apps.evaluacion.urls")),
    path("api/", include("apps.seguimiento.urls")),
    path("api/", include("apps.notificaciones.urls")),
    path("api/", include("apps.chat.urls")),
    path("api/", include("apps.configuracion.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
