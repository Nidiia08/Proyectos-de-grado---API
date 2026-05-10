from django.contrib import admin
from .models import Plantilla


@admin.register(Plantilla)
class PlantillaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'fase', 'modalidad_aplica', 'fecha_actualizacion', 'subida_por']
    list_filter = ['fase', 'modalidad_aplica', 'categoria']
    search_fields = ['nombre', 'categoria']
    readonly_fields = ['fecha_actualizacion']
    ordering = ['-fecha_actualizacion']