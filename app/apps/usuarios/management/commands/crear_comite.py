from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from apps.usuarios.models import Usuario, UsuarioRol


class Command(BaseCommand):
    help = "Crea el usuario inicial del Comite Curricular."

    def add_arguments(self, parser):
        parser.add_argument("--correo", default="admin@udenar.edu.co")
        parser.add_argument("--password", default="Admin2024*")
        parser.add_argument("--nombre", default="Administrador")
        parser.add_argument("--apellido", default="Sistema")

    def handle(self, *args, **options):
        correo = options["correo"]
        password = options["password"]
        nombre = options["nombre"]
        apellido = options["apellido"]

        if Usuario.objects.filter(correo=correo).exists():
            self.stdout.write("El usuario del Comite Curricular ya existe")
            return

        usuario = Usuario.objects.create(
            correo=correo,
            password=make_password(password),
            nombre=nombre,
            apellido=apellido,
            tipo_documento="CEDULA_CIUDADANIA",
            numero_documento="0000000001",
            celular="3000000001",
            activo=True,
            is_superuser=True,
        )
        UsuarioRol.objects.get_or_create(usuario=usuario, rol=UsuarioRol.Rol.COMITE)
        self.stdout.write("Usuario del Comite Curricular creado exitosamente")
        self.stdout.write(f"Correo: {correo}")
        self.stdout.write(f"Contrasena: {password}")
        self.stdout.write("Por favor cambie la contrasena despues del primer login")
