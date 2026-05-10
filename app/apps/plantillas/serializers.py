from rest_framework import serializers
from .models import Plantilla


class PlantillaSerializer(serializers.ModelSerializer):
    fecha_actualizacion = serializers.DateTimeField(read_only=True)
    subida_por_nombre = serializers.SerializerMethodField()
    archivo_url = serializers.FileField(required=False)

    class Meta:
        model = Plantilla
        fields = [
            'id', 'nombre', 'categoria', 'fase', 'modalidad_aplica',
            'archivo_url', 'fecha_actualizacion', 'subida_por',
            'subida_por_nombre'
        ]
        read_only_fields = ['fecha_actualizacion', 'subida_por']

    def get_subida_por_nombre(self, obj):
        return f"{obj.subida_por.nombre} {obj.subida_por.apellido}"

    def create(self, validated_data):
        validated_data['subida_por'] = self.context['request'].user
        return super().create(validated_data)