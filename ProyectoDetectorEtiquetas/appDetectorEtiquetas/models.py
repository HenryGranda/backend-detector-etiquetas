from django.db import models  # Asegúrate de que esta línea esté incluida

class Imagen(models.Model):
    imagen = models.CharField(max_length=255)  # Incrementar a un tamaño adecuado
    etiquetas = models.JSONField(blank=True, null=True)
    fecha_procesamiento = models.DateTimeField(auto_now_add=True)  # Fecha del análisis

    def __str__(self):
        return self.imagen.name
