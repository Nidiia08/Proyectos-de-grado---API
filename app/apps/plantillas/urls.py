from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PlantillaViewSet

router = DefaultRouter()
router.register(r'plantillas', PlantillaViewSet, basename='plantilla')

urlpatterns = router.urls