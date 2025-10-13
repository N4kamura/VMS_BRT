import cv2
import numpy as np
from ultralytics import YOLO
import os

def _detect_people_in_image(image_path, weights_path='weight/yolov8n.pt'):
    """
    Detecta personas en una imagen usando YOLOv8n y devuelve la imagen con bounding boxes
    y el número de personas detectadas.
    
    Args:
        image_path (str): Ruta a la imagen de entrada
        weights_path (str): Ruta a los pesos del modelo YOLOv8n
    
    Returns:
        tuple: (imagen con bounding boxes dibujados, número de personas detectadas)
    """
    # Cargar el modelo YOLOv8n
    # Si el archivo de pesos existe localmente, lo usamos; si no, usamos el modelo preentrenado
    if os.path.exists(weights_path):
        model = YOLO(weights_path)
    else:
        print(f"Archivo de pesos no encontrado en {weights_path}, usando modelo preentrenado de ultralytics...")
        model = YOLO('yolov8n.pt')  # Esto descargará el modelo si no está presente
    
    # Leer la imagen
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"No se pudo leer la imagen desde {image_path}")
    
    # Realizar inferencia
    results = model(image)
    
    # Contador de personas detectadas (clase 0 en COCO es 'person')
    person_count = 0
    
    # Dibujar bounding boxes solo para personas
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Verificar si la clase detectada es 'person' (clase 0 en COCO dataset)
                if int(box.cls[0]) == 0:  # Clase 0 corresponde a 'person' en COCO
                    # Obtener coordenadas del bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Dibujar el bounding box en la imagen
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Etiquetar el bounding box como 'person'
                    cv2.putText(image, 'person', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # Incrementar contador de personas
                    person_count += 1
    
    return image, person_count

def process_image(image_path: str):
    try:
        # Detectar personas en la imagen
        result_image, count = _detect_people_in_image(image_path)
        
        print(f"PASSENGERS: Se detectaron {count} personas en la imagen.")
        
        # Guardar la imagen con bounding boxes (opcional)
        output_path = image_path.rsplit('.', 1)[0] + '_detected.png'
        cv2.imwrite(output_path, result_image)
        print(f"PASSENGERS: Imagen con bounding boxes guardada como {output_path}")

        return count
        
    except Exception as e:
        print(f"Error: {e}")
