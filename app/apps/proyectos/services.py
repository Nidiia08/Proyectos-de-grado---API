from django.db import transaction
from django.utils import timezone

from apps.fases.models import (
    EstadoFase,
    FaseAprobacion,
    FaseCulminacion,
    FaseDesarrollo,
    FaseEvaluacion,
    FaseInscripcion,
)
from apps.notificaciones.services import crear_notificacion
from apps.seguimiento.models import HistorialAccion
from apps.usuarios.permissions import tiene_rol

from .models import Proyecto, ProyectoEstudiante

ORDEN_FASES = [
    Proyecto.FaseActual.INSCRIPCION,
    Proyecto.FaseActual.APROBACION,
    Proyecto.FaseActual.DESARROLLO,
    Proyecto.FaseActual.CULMINACION,
    Proyecto.FaseActual.EVALUACION,
]


def registrar_historial(proyecto, usuario, accion, descripcion, fase=None):
    """Registra una accion importante en el historial."""
    HistorialAccion.objects.create(
        proyecto=proyecto,
        usuario=usuario,
        accion=accion,
        descripcion=descripcion,
        fase=fase,
        fecha=timezone.now(),
    )


@transaction.atomic
def crear_proyecto(datos, creado_por):
    """Crea un proyecto y sus cinco fases iniciales."""
    estudiantes = datos.pop("estudiantes", [])
    datos.setdefault("estado", Proyecto.Estado.ACTIVO)
    datos.setdefault("fase_actual", Proyecto.FaseActual.INSCRIPCION)

    proyecto = Proyecto.objects.create(**datos)

    for estudiante in estudiantes:
        ProyectoEstudiante.objects.get_or_create(
            proyecto=proyecto,
            estudiante_id=estudiante["estudiante_id"],
            defaults={"es_autor_principal": estudiante.get("es_autor_principal", False)},
        )

    FaseInscripcion.objects.create(proyecto=proyecto, estado=EstadoFase.PENDIENTE)
    FaseAprobacion.objects.create(proyecto=proyecto, estado=EstadoFase.PENDIENTE, max_iteraciones=3)
    FaseDesarrollo.objects.create(proyecto=proyecto, estado=EstadoFase.PENDIENTE)
    FaseCulminacion.objects.create(proyecto=proyecto, estado=EstadoFase.PENDIENTE)
    FaseEvaluacion.objects.create(proyecto=proyecto, estado=EstadoFase.PENDIENTE)
    registrar_historial(proyecto, creado_por, "CREAR_PROYECTO", "Se creo el proyecto.", proyecto.fase_actual)
    return proyecto


def obtener_proyectos_por_rol(usuario):
    """Retorna proyectos segun el rol del usuario autenticado."""
    if tiene_rol(usuario, "ESTUDIANTE"):
        return Proyecto.objects.filter(proyectoestudiante__estudiante__usuario=usuario).distinct()
    if tiene_rol(usuario, "DOCENTE"):
        return Proyecto.objects.filter(asesor__usuario=usuario).distinct()
    if tiene_rol(usuario, "JURADO"):
        return Proyecto.objects.filter(asignacionjurado__jurado__usuario=usuario).distinct()
    return Proyecto.objects.all()


@transaction.atomic
def avanzar_fase(proyecto_id, nueva_fase, usuario):
    """Avanza el proyecto de fase validando el orden secuencial."""
    proyecto = Proyecto.objects.get(id=proyecto_id)
    actual_i = ORDEN_FASES.index(proyecto.fase_actual)
    nueva_i = ORDEN_FASES.index(nueva_fase)
    if nueva_i != actual_i + 1:
        raise ValueError("No se puede avanzar a esa fase sin completar la anterior.")
    proyecto.fase_actual = nueva_fase
    proyecto.save()
    registrar_historial(proyecto, usuario, "AVANZAR_FASE", f"Proyecto avanzo a {nueva_fase}.", nueva_fase)

    for rel in proyecto.proyectoestudiante_set.select_related("estudiante__usuario").all():
        crear_notificacion(
            rel.estudiante.usuario_id,
            proyecto.id,
            "CAMBIO_FASE",
            f"El proyecto ahora esta en fase {nueva_fase}.",
            f"/proyectos/{proyecto.id}",
        )
    return proyecto
