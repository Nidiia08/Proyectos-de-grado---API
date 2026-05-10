from django.contrib import admin

from .models import DocumentoCulminacion, DocumentoInscripcion


@admin.register(DocumentoInscripcion)
class DocumentoInscripcionAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre_documento", "tipo_documento", "estado", "fecha_carga")
    list_filter = ("estado", "fecha_carga")
    search_fields = ("nombre_documento", "tipo_documento")
    ordering = ("-fecha_carga",)


@admin.register(DocumentoCulminacion)
class DocumentoCulminacionAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre_documento", "tipo_documento", "estado", "fecha_carga")
    list_filter = ("estado", "fecha_carga")
    search_fields = ("nombre_documento", "tipo_documento")
    ordering = ("-fecha_carga",)

