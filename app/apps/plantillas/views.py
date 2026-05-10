from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from .models import Plantilla
from .serializers import PlantillaSerializer
from .services import generar_docx_prellenado


class PlantillaPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if view.action in ['list', 'retrieve', 'descargar']:
            return True
        return self.es_comite_curricular(request.user)

    def es_comite_curricular(self, usuario):
        roles = list(usuario.roles.values_list('rol', flat=True))
        return 'COMITE_CURRICULAR' in roles or 'COMITE' in roles


class PlantillaViewSet(viewsets.ModelViewSet):
    queryset = Plantilla.objects.all()
    serializer_class = PlantillaSerializer
    permission_classes = [PlantillaPermission]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        fase = self.request.query_params.get('fase')
        if fase:
            qs = qs.filter(fase=fase)
        modalidad = self.request.query_params.get('modalidad')
        if modalidad:
            qs = qs.filter(modalidad_aplica=modalidad)
        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria=categoria)
        return qs.order_by('-fecha_actualizacion')

    @action(detail=True, methods=['get'])
    def descargar(self, request, pk=None):
        """
        Descarga una plantilla prellenada con los datos del usuario.
        
        El reemplazo de marcadores se hace según la categoría de la plantilla:
        - Estudiante: datos del proyecto, estudiante, asesor, coasesor
        - Asesor: datos personales del asesor
        - Jurado: datos personales del jurado
        - General: solo datos básicos
        """
        plantilla = self.get_object()
        
        try:
            buffer = generar_docx_prellenado(plantilla, request.user)
            
            nombre_base = plantilla.nombre.replace(' ', '_')
            nombre_archivo = f"{nombre_base}_prellenado.docx"
            
            response = FileResponse(
                buffer,
                as_attachment=True,
                filename=nombre_archivo,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error al generar documento: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )