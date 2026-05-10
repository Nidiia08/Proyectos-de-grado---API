from django.db import transaction
from rest_framework import serializers

from .models import Docente, Estudiante, Usuario, UsuarioRol
from .services import autenticar_usuario, registrar_docente, registrar_estudiante


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer base de datos de usuario."""

    roles = serializers.SerializerMethodField()
    codigo_estudiante = serializers.SerializerMethodField()
    programa = serializers.SerializerMethodField()
    promedio_acumulado = serializers.SerializerMethodField()
    creditos_aprobados = serializers.SerializerMethodField()
    codigo_docente = serializers.SerializerMethodField()
    area_conocimiento = serializers.SerializerMethodField()
    max_proyectos_asesor = serializers.SerializerMethodField()
    max_proyectos_jurado = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = (
            "id",
            "nombre",
            "apellido",
            "correo",
            "tipo_documento",
            "numero_documento",
            "celular",
            "roles",
            "activo",
            "fecha_registro",
            "codigo_estudiante",
            "programa",
            "promedio_acumulado",
            "creditos_aprobados",
            "codigo_docente",
            "area_conocimiento",
            "max_proyectos_asesor",
            "max_proyectos_jurado",
        )

    def get_roles(self, obj):
        return list(obj.roles.values_list("rol", flat=True))

    def get_codigo_estudiante(self, obj):
        return getattr(getattr(obj, "estudiante", None), "codigo_estudiante", None)

    def get_programa(self, obj):
        return getattr(getattr(obj, "estudiante", None), "programa", None)

    def get_promedio_acumulado(self, obj):
        return getattr(getattr(obj, "estudiante", None), "promedio_acumulado", None)

    def get_creditos_aprobados(self, obj):
        return getattr(getattr(obj, "estudiante", None), "creditos_aprobados", None)

    def get_codigo_docente(self, obj):
        return getattr(getattr(obj, "docente", None), "codigo_docente", None)

    def get_area_conocimiento(self, obj):
        return getattr(getattr(obj, "docente", None), "area_conocimiento", None)

    def get_max_proyectos_asesor(self, obj):
        return getattr(getattr(obj, "docente", None), "max_proyectos_asesor", None)

    def get_max_proyectos_jurado(self, obj):
        return getattr(getattr(obj, "docente", None), "max_proyectos_jurado", None)


class EstudianteSerializer(serializers.ModelSerializer):
    """Serializer de estudiante con usuario anidado."""

    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Estudiante
        fields = "__all__"


class DocenteSerializer(serializers.ModelSerializer):
    """Serializer de docente con usuario anidado."""

    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Docente
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    """Valida credenciales para autenticacion."""

    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    rol = serializers.ChoiceField(choices=UsuarioRol.Rol.choices)

    def validate(self, attrs):
        try:
            return autenticar_usuario(attrs["correo"], attrs["password"], attrs["rol"])
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))


class RegistroEstudianteSerializer(serializers.Serializer):
    """Crea usuario y estudiante en una sola transaccion."""

    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    tipo_documento = serializers.ChoiceField(choices=Usuario.TipoDocumento.choices)
    numero_documento = serializers.CharField(max_length=20)
    celular = serializers.CharField(max_length=10)
    codigo_estudiante = serializers.CharField(max_length=50)
    programa = serializers.CharField(max_length=150)
    promedio_acumulado = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    creditos_aprobados = serializers.IntegerField(required=False)

    def validate_numero_documento(self, value):
        if Usuario.objects.filter(numero_documento=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este número de documento.")
        return value

    def validate_celular(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("El celular debe tener exactamente 10 dígitos numéricos.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        return registrar_estudiante(validated_data)


class RegistroDocenteSerializer(serializers.Serializer):
    """Crea usuario y docente en una sola transaccion."""

    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    tipo_documento = serializers.ChoiceField(choices=Usuario.TipoDocumento.choices)
    numero_documento = serializers.CharField(max_length=20)
    celular = serializers.CharField(max_length=10)
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=[UsuarioRol.Rol.DOCENTE, UsuarioRol.Rol.JURADO]),
        required=False,
    )
    codigo_docente = serializers.CharField(max_length=50)
    area_conocimiento = serializers.CharField(max_length=150, required=False, allow_blank=True)
    max_proyectos_asesor = serializers.IntegerField(required=False)
    max_proyectos_jurado = serializers.IntegerField(required=False)

    def validate_numero_documento(self, value):
        if Usuario.objects.filter(numero_documento=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este número de documento.")
        return value

    def validate_celular(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("El celular debe tener exactamente 10 dígitos numéricos.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        return registrar_docente(validated_data)


class CambioPasswordSerializer(serializers.Serializer):
    """Valida el cambio de contrasena de un usuario."""

    password_actual = serializers.CharField(write_only=True)
    password_nuevo = serializers.CharField(write_only=True, min_length=8)
    confirmar_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password_nuevo"] != attrs["confirmar_password"]:
            raise serializers.ValidationError("La confirmacion de contrasena no coincide.")
        return attrs


class ActualizarPerfilSerializer(serializers.ModelSerializer):
    """Permite actualizar solo los datos personales del usuario autenticado."""

    class Meta:
        model = Usuario
        fields = (
            "nombre",
            "apellido",
            "tipo_documento",
            "numero_documento",
            "celular",
        )

    def validate_numero_documento(self, value):
        queryset = Usuario.objects.filter(numero_documento=value)
        if self.instance is not None:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un usuario con este número de documento.")
        return value

    def validate_celular(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("El celular debe tener exactamente 10 dígitos numéricos.")
        return value
