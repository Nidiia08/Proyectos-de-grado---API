from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.plantillas.models import Plantilla
from apps.usuarios.permissions import tiene_rol

from .models import DocumentoCulminacion, DocumentoInscripcion
from .serializers import DocumentoCulminacionSerializer, DocumentoInscripcionSerializer, PlantillaSerializer
from .services import actualizar_documento, crear_documento_culminacion, crear_documento_inscripcion


def ok(mensaje, datos=None, status_code=status.HTTP_200_OK):
    return Response({"mensaje": mensaje, "datos": datos}, status=status_code)


def error(mensaje, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"error": mensaje}, status=status_code)


class DocumentoInscripcionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        docs = DocumentoInscripcion.objects.filter(fase_inscripcion__proyecto_id=id)
        return ok("Documentos de inscripcion consultados.", DocumentoInscripcionSerializer(docs, many=True).data)

    def post(self, request, id):
        payload = dict(request.data)
        serializer = DocumentoInscripcionSerializer(data=payload)
        if not serializer.is_valid():
            return error("Datos invalidos para documento de inscripcion.")
        documento = crear_documento_inscripcion(serializer.validated_data)
        return ok("Documento de inscripcion creado.", DocumentoInscripcionSerializer(documento).data, status.HTTP_201_CREATED)


class DocumentoInscripcionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        documento = actualizar_documento(DocumentoInscripcion, id, request.data)
        return ok("Documento de inscripcion actualizado.", DocumentoInscripcionSerializer(documento).data)


class DocumentoCulminacionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        docs = DocumentoCulminacion.objects.filter(fase_culminacion__proyecto_id=id)
        return ok("Documentos de culminacion consultados.", DocumentoCulminacionSerializer(docs, many=True).data)

    def post(self, request, id):
        serializer = DocumentoCulminacionSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Datos invalidos para documento de culminacion.")
        documento = crear_documento_culminacion(serializer.validated_data)
        return ok("Documento de culminacion creado.", DocumentoCulminacionSerializer(documento).data, status.HTTP_201_CREATED)


class DocumentoCulminacionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        documento = actualizar_documento(DocumentoCulminacion, id, request.data)
        return ok("Documento de culminacion actualizado.", DocumentoCulminacionSerializer(documento).data)


class PlantillaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return ok("Plantillas consultadas.", PlantillaSerializer(Plantilla.objects.all(), many=True).data)

    def post(self, request):
        if not tiene_rol(request.user, "COMITE"):
            return error("Solo el comite puede crear plantillas.", status.HTTP_403_FORBIDDEN)
        serializer = PlantillaSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Datos invalidos para plantilla.")
        serializer.save()
        return ok("Plantilla creada.", serializer.data, status.HTTP_201_CREATED)


class PlantillaDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        if not tiene_rol(request.user, "COMITE"):
            return error("Solo el comite puede eliminar plantillas.", status.HTTP_403_FORBIDDEN)
        Plantilla.objects.filter(id=id).delete()
        return ok("Plantilla eliminada.")
