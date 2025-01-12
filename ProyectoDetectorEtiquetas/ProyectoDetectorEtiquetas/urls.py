from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from appDetectorEtiquetas import views
from django.urls import path
from appDetectorEtiquetas.views import HistorialAPI, CargarImagenAPI, CapturaCamaraAPI, ResultadosAPI

urlpatterns = [
    path('api/historial/', HistorialAPI.as_view(), name='historial_api'),
    path('api/cargar-imagen/', CargarImagenAPI.as_view(), name='cargar_imagen_api'),
    path('api/captura-camara/', CapturaCamaraAPI.as_view(), name='captura_camara_api'),
    path('api/resultados/', ResultadosAPI.as_view(), name='resultados_api'), 
    path('api/resultados/<int:id>/', ResultadosAPI.as_view(), name='resultados_detalle_api'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
