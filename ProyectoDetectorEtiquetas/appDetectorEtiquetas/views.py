import os
from django.http import JsonResponse
import base64
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Imagen
from .serializers import ImagenSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import detectar_etiquetas

class HistorialAPI(APIView):
    def get(self, request):
        imagenes = Imagen.objects.all()
        data = [
            {
                "id": imagen.id,
                "etiquetas": imagen.etiquetas,
                "imagen": imagen.imagen.url if hasattr(imagen.imagen, 'url') else f"{settings.MEDIA_URL}{imagen.imagen}",
                "fecha_procesamiento": imagen.fecha_procesamiento,
            }
            for imagen in imagenes
        ]
        return Response(data)

class CargarImagenAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        print(f"DEBUG - Request data: {request.data}")
        imagen = request.FILES.get('imagen')
        if not imagen:
            print("DEBUG - No se proporcionó una imagen.")
            return Response({'error': 'No se proporcionó una imagen'}, status=400)

        # Guardar la imagen y obtener su ruta absoluta
        full_path = self.guardar_imagen(imagen)

        # Procesar y detectar etiquetas
        try:
            resultados = detectar_etiquetas(full_path, umbral_confianza=0.35)
        except FileNotFoundError as e:
            return Response({'error': f'Archivo no encontrado: {str(e)}'}, status=500)

        # Guardar en la base de datos
        nueva_imagen = Imagen.objects.create(imagen=full_path, etiquetas=resultados)

        return Response({'id': nueva_imagen.id, 'resultados': resultados})


    def guardar_imagen(self, imagen):
        carpeta_imagenes = os.path.join(settings.MEDIA_ROOT, "imagenes")
        if not os.path.exists(carpeta_imagenes):
            os.makedirs(carpeta_imagenes)

        full_path = os.path.join(carpeta_imagenes, imagen.name)
        with open(full_path, 'wb') as f:
            for chunk in imagen.chunks():
                f.write(chunk)

        return full_path
    
class CapturaCamaraAPI(APIView):
    def post(self, request):
        # Depuración: imprimir datos de la solicitud
        print(f"DEBUG - Request data: {request.data}")

        # Obtener la imagen en formato base64
        image_data = request.data.get('image')
        if not image_data:
            return JsonResponse({'error': 'No se proporcionó ninguna imagen'}, status=400)

        try:
            # Dividir formato y datos
            format, imgstr = image_data.split(';base64,')
            print(f"DEBUG - Format: {format}, Data (first 50 chars): {imgstr[:50]}...")

            # Decodificar la imagen base64
            img_data = base64.b64decode(imgstr)
            
            # Guardar la imagen en el sistema de archivos
            carpeta_imagenes = os.path.join(settings.MEDIA_ROOT, "imagenes")
            if not os.path.exists(carpeta_imagenes):
                os.makedirs(carpeta_imagenes)

            temp_path = os.path.join(carpeta_imagenes, "captura.jpg")
            with open(temp_path, 'wb') as f:
                f.write(img_data)
            
            print(f"DEBUG - Imagen guardada en: {temp_path}")

            # Detectar etiquetas en la imagen
            resultados = detectar_etiquetas(temp_path, umbral_confianza=0.35)
            print(f"DEBUG - Resultados: {resultados}")

            # Devolver la respuesta con etiquetas detectadas
            return JsonResponse({
                'message': 'Imagen procesada correctamente',
                'path': temp_path,
                'resultados': resultados  # Asegúrate de que sea una lista de diccionarios
            })
        
        except Exception as e:
            print(f"DEBUG - Error procesando la imagen: {str(e)}")
            return JsonResponse({'error': f'Error procesando la imagen: {str(e)}'}, status=500)

class ResultadosAPI(APIView):
    def get(self, request, id=None):
        if id is not None:
            # Devolver un resultado específico
            try:
                resultado = Imagen.objects.get(id=id)
                data = {
                    "id": resultado.id,
                    "etiquetas": resultado.etiquetas,
                    "imagen": f"{settings.MEDIA_URL}{resultado.imagen}",  # Construye la URL completa
                    "fecha_procesamiento": resultado.fecha_procesamiento
                }
                return Response(data)
            except Imagen.DoesNotExist:
                return Response({"error": "No se encontró el resultado con el ID especificado."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Devolver todos los resultados
            resultados = Imagen.objects.values('id', 'etiquetas', 'imagen', 'fecha_procesamiento')
            return Response(resultados)
        
