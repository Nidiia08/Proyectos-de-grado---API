from django.db import models


class DocumentoInscripcion(models.Model):
    """Archivos cargados durante la fase de inscripcion."""

    fase_inscripcion = models.ForeignKey("fases.FaseInscripcion", models.DO_NOTHING)
    estudiante = models.ForeignKey("usuarios.Estudiante", models.DO_NOTHING)
    nombre_documento = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=100)
    archivo_url = models.CharField(max_length=500, blank=True, null=True)
    estado = models.CharField(max_length=30)
    es_requerido = models.BooleanField(blank=True, null=True)
    fecha_carga = models.DateTimeField(blank=True, null=True)
    observacion_rechazo = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "documento_inscripcion"

    def __str__(self):
        return self.nombre_documento


class DocumentoCulminacion(models.Model):
    """Archivos cargados durante la fase de culminacion."""

    fase_culminacion = models.ForeignKey("fases.FaseCulminacion", models.DO_NOTHING)
    estudiante = models.ForeignKey("usuarios.Estudiante", models.DO_NOTHING)
    nombre_documento = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=100)
    archivo_url = models.CharField(max_length=500, blank=True, null=True)
    estado = models.CharField(max_length=30)
    es_requerido = models.BooleanField(blank=True, null=True)
    fecha_carga = models.DateTimeField(blank=True, null=True)
    observacion_rechazo = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "documento_culminacion"

    def __str__(self):
        return self.nombre_documento


