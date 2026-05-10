from django.db import models
from apps.usuarios.models import Usuario


class Plantilla(models.Model):

    class Fase(models.TextChoices):
        INSCRIPCION = 'INSCRIPCION', 'Inscripción'
        APROBACION = 'APROBACION', 'Aprobación'
        DESARROLLO = 'DESARROLLO', 'Desarrollo'
        CULMINACION = 'CULMINACION', 'Culminación'
        EVALUACION = 'EVALUACION', 'Evaluación'

    class Modalidad(models.TextChoices):
        TODAS = 'TODAS', 'Todas'
        INVESTIGACION = 'INVESTIGACION', 'Investigación'
        INTERACCION_SOCIAL = 'INTERACCION_SOCIAL', 'Interacción Social'
        PASANTIA = 'PASANTIA', 'Pasantía'

    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    fase = models.CharField(max_length=30, choices=Fase.choices)
    modalidad_aplica = models.CharField(
        max_length=30, choices=Modalidad.choices, default=Modalidad.TODAS
    )
    archivo_url = models.FileField(upload_to='plantillas/')
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    subida_por = models.ForeignKey(
        Usuario,
        on_delete=models.RESTRICT,
        related_name='plantillas_subidas',
        db_column='subida_por'
    )

    class Meta:
        db_table = 'plantilla'

    def __str__(self):
        return f"{self.nombre} - {self.fase}"