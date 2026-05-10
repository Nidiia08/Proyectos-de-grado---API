from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Manager personalizado para crear usuarios y superusuarios."""

    def create_user(self, correo, password, roles=None, **extra_fields):
        """Crea un usuario y asigna uno o varios roles."""
        if not correo:
            raise ValueError("El correo es obligatorio")
        correo = self.normalize_email(correo)
        usuario = self.model(correo=correo, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        if roles:
            for rol in roles:
                UsuarioRol.objects.get_or_create(usuario=usuario, rol=rol)
        return usuario

    def create_superuser(self, correo, password, roles=None, **extra_fields):
        """Crea un superusuario y por defecto le asigna rol COMITE."""
        extra_fields.setdefault("activo", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(
            correo=correo,
            password=password,
            roles=roles or [UsuarioRol.Rol.COMITE],
            **extra_fields,
        )


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Representa un usuario base del sistema."""

    class TipoDocumento(models.TextChoices):
        CEDULA_CIUDADANIA = "CEDULA_CIUDADANIA", "Cédula de Ciudadanía"
        TARJETA_IDENTIDAD = "TARJETA_IDENTIDAD", "Tarjeta de Identidad"
        CEDULA_EXTRANJERIA = "CEDULA_EXTRANJERIA", "Cédula de Extranjería"
        PASAPORTE = "PASAPORTE", "Pasaporte"

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.CharField(unique=True, max_length=150)
    tipo_documento = models.CharField(
        max_length=30,
        choices=TipoDocumento.choices,
        default=TipoDocumento.CEDULA_CIUDADANIA,
    )
    numero_documento = models.CharField(unique=True, max_length=20)
    celular = models.CharField(max_length=10)
    password = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre", "apellido"]

    class Meta:
        managed = True
        db_table = "usuario"

    def tiene_rol(self, rol):
        """Valida si el usuario posee un rol especifico."""
        return self.roles.filter(rol=rol).exists()

    @property
    def roles_lista(self):
        """Retorna la lista de roles del usuario."""
        return list(self.roles.values_list("rol", flat=True))

    @property
    def is_staff(self):
        """Permite admin para superusuario o rol COMITE."""
        return self.is_superuser or self.tiene_rol(UsuarioRol.Rol.COMITE)

    @property
    def is_active(self):
        return self.activo

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.correo})"


class UsuarioRol(models.Model):
    """Relacion de roles para permitir multiperfil por usuario."""

    class Rol(models.TextChoices):
        ESTUDIANTE = "ESTUDIANTE", "Estudiante"
        DOCENTE = "DOCENTE", "Docente"
        JURADO = "JURADO", "Jurado"
        COMITE = "COMITE", "Comite Curricular"

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="roles")
    rol = models.CharField(max_length=20, choices=Rol.choices)

    class Meta:
        managed = True
        db_table = "usuario_rol"
        unique_together = ("usuario", "rol")

    def __str__(self):
        return f"{self.usuario.correo} - {self.rol}"


class Estudiante(models.Model):
    """Perfil academico para usuarios que pueden actuar como estudiantes."""

    usuario = models.OneToOneField(
        Usuario,
        models.CASCADE,
        db_column="usuario_id",
        related_name="estudiante",
    )
    codigo_estudiante = models.CharField(unique=True, max_length=50)
    programa = models.CharField(max_length=150)
    promedio_acumulado = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    creditos_aprobados = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "estudiante"

    def __str__(self):
        return f"Estudiante {self.codigo_estudiante}"


class Docente(models.Model):
    """Perfil academico para usuarios que pueden actuar como docentes o jurados."""

    usuario = models.OneToOneField(
        Usuario,
        models.CASCADE,
        db_column="usuario_id",
        related_name="docente",
    )
    codigo_docente = models.CharField(unique=True, max_length=50)
    area_conocimiento = models.CharField(max_length=150, blank=True, null=True)
    max_proyectos_asesor = models.IntegerField(blank=True, null=True)
    max_proyectos_jurado = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "docente"

    def __str__(self):
        return f"Docente {self.codigo_docente}"
