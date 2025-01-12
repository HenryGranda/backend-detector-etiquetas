import os
from ultralytics import YOLO  # Librería para trabajar con YOLO
from django.conf import settings

# Ruta del modelo YOLO
modelo_path = os.path.join(settings.BASE_DIR, "appDetectorEtiquetas", "static", "appDetectorEtiquetas", "modelo", "best.pt")

# Validar si el modelo existe
if not os.path.exists(modelo_path):
    raise FileNotFoundError(f"No se encontró el archivo del modelo en la ruta: {modelo_path}")

# Cargar el modelo YOLO
modelo = YOLO(modelo_path)

def detectar_etiquetas(imagen_path, umbral_confianza=0.5):
    """
    Detectar etiquetas en una imagen utilizando el modelo YOLO cargado.
    Filtra las detecciones con confianza inferior al umbral_confianza.
    
    Args:
        imagen_path (str): Ruta de la imagen a analizar.
        umbral_confianza (float): Umbral mínimo de confianza para aceptar detecciones.
        
    Returns:
        list: Lista de diccionarios con las etiquetas, confianza y coordenadas.
    """
    # Realizar la predicción con YOLO
    resultados = modelo(imagen_path)  # Retorna los resultados como objetos de clase ultralytics.engine.results.Results

    # Extraer las detecciones en la primera imagen
    detecciones = resultados[0].boxes  # Detecciones en la imagen
    etiquetas = detecciones.cls.cpu().numpy()  # Clases predichas (índices)
    confidencias = detecciones.conf.cpu().numpy()  # Confianzas
    coordenadas = detecciones.xyxy.cpu().numpy()  # Coordenadas de los cuadros delimitadores

    # Obtener nombres de las clases (definidas en el modelo YOLO)
    nombres_clases = modelo.names

    # Formatear los resultados como una lista de diccionarios
    resultados_list = [
        {
            "etiqueta": nombres_clases[int(etiqueta)],
            "confianza": float(confianza),
            "coordenadas": [float(x) for x in coord]  # [xmin, ymin, xmax, ymax]
        }
        for etiqueta, confianza, coord in zip(etiquetas, confidencias, coordenadas)
        if confianza >= umbral_confianza  # Filtrar por confianza
    ]

    return resultados_list


