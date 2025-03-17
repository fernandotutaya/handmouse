"""
Módulo para la detección de gestos a partir de contornos de la mano.
"""
import cv2
import numpy as np
from config import DEFECT_THRESHOLD, HAND_RATIO_THRESHOLD

def detect_gestures(contour, frame):
    """
    Detecta gestos basados en el análisis de contornos y defectos de convexidad.
    
    Args:
        contour: Contorno de la mano
        frame: Frame para visualización
        
    Returns:
        str: Nombre del gesto detectado, o None si no se detecta ninguno
    """
    try:
        if contour is None or len(contour) < 5:
            return None
            
        # Calcular el rectángulo mínimo que contiene el contorno
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
        
        # Calcular el ratio largo/ancho para análisis de la forma
        width, height = rect[1]
        aspect_ratio = max(width, height) / (min(width, height) + 0.01)
        
        # Calcular casco convexo y defectos
        hull = cv2.convexHull(contour, returnPoints=False)
        defects = cv2.convexityDefects(contour, hull)
        
        finger_count = 0
        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])
                
                cv2.circle(frame, far, 5, [0, 0, 255], -1)
                if d > DEFECT_THRESHOLD:
                    finger_count += 1
                    cv2.line(frame, start, end, [0, 255, 0], 2)
        
        # Información de depuración
        cv2.putText(frame, f"Defectos: {finger_count}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Ratio: {aspect_ratio:.2f}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Lógica de detección según cantidad de defectos y ratio
        if finger_count == 1 and aspect_ratio < HAND_RATIO_THRESHOLD:
            return "pinch"  # Dos dedos juntos
        elif finger_count == 2:
            return "rotate"  # Tres dedos levantados
        elif finger_count >= 3:
            return "hand_open"  # Mano abierta
        elif finger_count == 0 and aspect_ratio < HAND_RATIO_THRESHOLD:
            return "hand_closed"  # Mano cerrada
            
        return None
    except Exception as e:
        print(f"Error en detect_gestures: {e}")
        return None