from django.db import transaction

from apps.plantillas.models import Plantilla
from .models import DocumentoCulminacion, DocumentoInscripcion


@transaction.atomic
def crear_documento_inscripcion(datos):
    """Crea un documento de inscripcion."""
    return DocumentoInscripcion.objects.create(**datos)


@transaction.atomic
def crear_documento_culminacion(datos):
    """Crea un documento de culminacion."""
    return DocumentoCulminacion.objects.create(**datos)


@transaction.atomic
def actualizar_documento(modelo, documento_id, datos):
    """Actualiza documento de forma parcial."""
    documento = modelo.objects.get(id=documento_id)
    for campo, valor in datos.items():
        setattr(documento, campo, valor)
    documento.save()
    return documento


@transaction.atomic
def crear_plantilla(datos):
    """Crea una plantilla institucional."""
    return Plantilla.objects.create(**datos)
