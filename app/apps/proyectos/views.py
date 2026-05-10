from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.usuarios.permissions import tiene_rol

from .models import PeriodoAcademico, Proyecto
from .serializers import (
    PeriodoAcademicoSerializer,
    ProyectoCreateSerializer,
    ProyectoSerializer,
)
from .services import crear_proyecto, obtener_proyectos_por_rol


def ok(mensaje, datos=None, status_code=status.HTTP_200_OK):
    return Response({"mensaje": mensaje, "datos": datos}, status=status_code)


def error(mensaje, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"error": mensaje}, status=status_code)


class ProyectoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        proyectos = obtener_proyectos_por_rol(request.user)
        return ok("Proyectos consultados correctamente.", ProyectoSerializer(proyectos, many=True).data)

    def post(self, request):
        if not tiene_rol(request.user, "COMITE"):
            return error("Solo el comite puede crear proyectos.", status.HTTP_403_FORBIDDEN)
        serializer = ProyectoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(f"Datos invalidos para crear proyecto. {serializer.errors}")
        try:
            proyecto = crear_proyecto(serializer.validated_data, request.user)
        except IntegrityError:
            return error(
                "No se pudo crear el proyecto por una restriccion de integridad. "
                "Verifica que los estudiantes no esten asignados a otro proyecto."
            )
        return ok("Proyecto creado correctamente.", ProyectoSerializer(proyecto).data, status.HTTP_201_CREATED)


class ProyectoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        proyecto = Proyecto.objects.get(id=id)
        return ok("Proyecto consultado correctamente.", ProyectoSerializer(proyecto).data)

    def put(self, request, id):
        if not tiene_rol(request.user, "COMITE"):
            return error("Solo el comite puede actualizar proyectos.", status.HTTP_403_FORBIDDEN)
        proyecto = Proyecto.objects.get(id=id)
        serializer = ProyectoCreateSerializer(proyecto, data=request.data, partial=False)
        if not serializer.is_valid():
            return error("Datos invalidos para actualizar proyecto.")
        serializer.save()
        return ok("Proyecto actualizado correctamente.", ProyectoSerializer(proyecto).data)


class PeriodoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return ok("Periodos consultados correctamente.", PeriodoAcademicoSerializer(PeriodoAcademico.objects.all(), many=True).data)

    def post(self, request):
        if not tiene_rol(request.user, "COMITE"):
            return error("Solo el comite puede crear periodos.", status.HTTP_403_FORBIDDEN)
        serializer = PeriodoAcademicoSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Datos invalidos para crear periodo.")
        serializer.save()
        return ok("Periodo creado correctamente.", serializer.data, status.HTTP_201_CREATED)
