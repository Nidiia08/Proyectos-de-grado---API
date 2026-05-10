from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import Usuario
from .permissions import EsComite, EsPropioUsuarioOComite, tiene_rol
from .serializers import (
    CambioPasswordSerializer,
    DocenteSerializer,
    EstudianteSerializer,
    LoginSerializer,
    RegistroDocenteSerializer,
    RegistroEstudianteSerializer,
    UsuarioSerializer,
)
from .services import (
    actualizar_usuario,
    actualizar_perfil,
    cambiar_password,
    desactivar_usuario,
    obtener_perfil_usuario,
)


def ok(mensaje, datos=None, status_code=status.HTTP_200_OK):
    return Response({"mensaje": mensaje, "datos": datos}, status=status_code)


def error(mensaje, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"error": mensaje}, status=status_code)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            detalle = serializer.errors.get("non_field_errors", ["Credenciales incorrectas"])[0]
            return error(detalle, status.HTTP_400_BAD_REQUEST)
        return ok("Login exitoso", serializer.validated_data)


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        if "refresh" not in data and "refresh_token" in data:
            data["refresh"] = data["refresh_token"]
        request._full_data = data
        response = super().post(request, *args, **kwargs)
        if response.status_code != 200:
            return error("Token invalido.", response.status_code)
        return ok("Token actualizado.", {"access": response.data["access"]})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("refresh") or request.data.get("refresh_token")
        if not token:
            return error("Debe enviar refresh.")
        try:
            RefreshToken(token).blacklist()
            return ok("Sesion cerrada correctamente.")
        except Exception:
            return error("No fue posible cerrar sesion.")


class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        perfil = obtener_perfil_usuario(request.user.id)
        if tiene_rol(request.user, "ESTUDIANTE") and perfil["perfil"]:
            perfil_data = EstudianteSerializer(perfil["perfil"]).data
        elif perfil["perfil"]:
            perfil_data = DocenteSerializer(perfil["perfil"]).data
        else:
            perfil_data = None
        return ok("Perfil consultado correctamente.", {"usuario": UsuarioSerializer(perfil["usuario"]).data, "perfil": perfil_data})

    def patch(self, request):
        try:
            datos = actualizar_perfil(request.user.id, request.data)
        except ValidationError as exc:
            return Response({"error": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return error(str(exc))
        return ok("Perfil actualizado exitosamente", datos)


class CambioPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = CambioPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error("Datos invalidos para cambio de contrasena.")
        try:
            cambiar_password(
                request.user.id,
                serializer.validated_data["password_actual"],
                serializer.validated_data["password_nuevo"],
            )
        except ValueError as exc:
            return error(str(exc))
        return ok("Contrasena actualizada correctamente.")


class ListaUsuariosView(APIView):
    permission_classes = [IsAuthenticated, EsComite]

    def get(self, request):
        usuarios = Usuario.objects.select_related("estudiante", "docente").all()
        return ok("Usuarios consultados correctamente.", UsuarioSerializer(usuarios, many=True).data)


class RegistroEstudianteView(APIView):
    permission_classes = [IsAuthenticated, EsComite]

    def post(self, request):
        serializer = RegistroEstudianteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        estudiante = serializer.save()
        return ok("Estudiante creado correctamente.", EstudianteSerializer(estudiante).data, status.HTTP_201_CREATED)


class RegistroDocenteView(APIView):
    permission_classes = [IsAuthenticated, EsComite]

    def post(self, request):
        serializer = RegistroDocenteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        docente = serializer.save()
        return ok("Docente creado correctamente.", DocenteSerializer(docente).data, status.HTTP_201_CREATED)


class DetalleUsuarioView(APIView):
    permission_classes = [IsAuthenticated, EsPropioUsuarioOComite]

    def get_object(self, usuario_id):
        return Usuario.objects.get(id=usuario_id)

    def get(self, request, id):
        try:
            usuario = self.get_object(id)
        except Usuario.DoesNotExist:
            return error("Usuario no encontrado.", status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, usuario)
        return ok("Usuario consultado correctamente.", UsuarioSerializer(usuario).data)

    def put(self, request, id):
        if not tiene_rol(request.user, "COMITE"):
            return error("No tiene permisos para actualizar usuarios.", status.HTTP_403_FORBIDDEN)
        try:
            usuario = actualizar_usuario(id, request.data)
        except Usuario.DoesNotExist:
            return error("Usuario no encontrado.", status.HTTP_404_NOT_FOUND)
        return ok("Usuario actualizado correctamente.", UsuarioSerializer(usuario).data)


class DesactivarUsuarioView(APIView):
    permission_classes = [IsAuthenticated, EsComite]

    def patch(self, request, id):
        try:
            usuario = desactivar_usuario(id)
        except Usuario.DoesNotExist:
            return error("Usuario no encontrado.", status.HTTP_404_NOT_FOUND)
        return ok("Usuario desactivado correctamente.", UsuarioSerializer(usuario).data)
