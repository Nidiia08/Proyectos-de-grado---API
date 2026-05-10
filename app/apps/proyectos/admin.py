from django.contrib import admin

from .models import PeriodoAcademico, Proyecto, ProyectoEstudiante


@admin.register(PeriodoAcademico)
class PeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "fecha_inicio", "fecha_fin", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    ordering = ("-fecha_inicio",)


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "modalidad", "estado", "fase_actual", "fecha_inicio")
    list_filter = ("modalidad", "estado", "fase_actual")
    search_fields = ("nombre",)
    ordering = ("-id",)


@admin.register(ProyectoEstudiante)
class ProyectoEstudianteAdmin(admin.ModelAdmin):
    list_display = ("id", "proyecto", "estudiante", "es_autor_principal")
    list_filter = ("es_autor_principal",)
    search_fields = ("proyecto__nombre", "estudiante__codigo_estudiante")
    ordering = ("-id",)
