from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Limpia completamente la base de datos y la deja lista para usar."

    tablas = [
        "MENSAJE",
        "CONVERSACION",
        "CONFIGURACION_SISTEMA",
        "HISTORIAL_ACCION",
        "NOTIFICACION",
        "PLANTILLA",
        "REVISTA_INDEXADA",
        "CALIFICACION_JURADO",
        "REVISION_JURADO_REVISOR",
        "ASIGNACION_JURADO",
        "FASE_EVALUACION",
        "DOCUMENTO_CULMINACION",
        "FASE_CULMINACION",
        "INFORME_TRIMESTRAL",
        "PRORROGA",
        "FASE_DESARROLLO",
        "ITERACION_APROBACION",
        "FASE_APROBACION",
        "DOCUMENTO_INSCRIPCION",
        "FASE_INSCRIPCION",
        "ACUERDO",
        "PROYECTO_ESTUDIANTE",
        "PROYECTO",
        "PERIODO_ACADEMICO",
        "DOCENTE",
        "ESTUDIANTE",
        "USUARIO_ROL",
        "USUARIO",
        "django_migrations",
        "django_content_type",
        "django_admin_log",
        "auth_permission",
        "auth_group",
        "auth_group_permissions",
        "auth_user",
        "auth_user_groups",
        "auth_user_user_permissions",
    ]

    def handle(self, *args, **options):
        confirmar_1 = input("Estas seguro de que deseas eliminar TODOS los datos? (si/no): ").strip().lower()
        if confirmar_1 != "si":
            self.stdout.write("Operacion cancelada. No se realizaron cambios.")
            return

        confirmar_2 = input(
            "Confirmas que se perderan TODOS los datos incluyendo el usuario del Comite? (si/no): "
        ).strip().lower()
        if confirmar_2 != "si":
            self.stdout.write("Operacion cancelada. No se realizaron cambios.")
            return

        with connection.cursor() as cursor:
            for tabla in self.tablas:
                cursor.execute(f"DROP TABLE IF EXISTS {tabla} CASCADE;")

        self.stdout.write("Base de datos limpiada exitosamente")
        # `usuarios.Usuario` usa `PermissionsMixin`, asi que necesitamos las
        # tablas de `contenttypes` y `auth` antes de sincronizar las apps
        # locales. Luego, con `usuario` ya creado, aplicamos las migraciones
        # que dependen del AUTH_USER_MODEL, como `admin` y `token_blacklist`.
        call_command("migrate", "contenttypes", interactive=False)
        call_command("migrate", "auth", interactive=False)
        call_command("migrate", run_syncdb=True, interactive=False)
        call_command("migrate", "admin", interactive=False)
        call_command("migrate", "sessions", interactive=False)
        call_command("migrate", "token_blacklist", interactive=False)
        self.stdout.write("Migraciones y sincronizacion de tablas ejecutadas exitosamente")
        call_command("crear_comite")
        self.stdout.write("Base de datos lista para usar")
