"""
Funciones relacionadas con la calibración del fondo para detección de movimiento.
"""
import cv2
import numpy as np
from config import CALIBRATION_FRAMES

def calibrate_background(cap, frames=CALIBRATION_FRAMES):
    """
    Calibra el fondo capturando varios frames y calculando un promedio ponderado.
    
    Args:
        cap: Objeto de captura de video
        frames: Número de frames a utilizar para la calibración
        
    Returns:
        background: Imagen de fondo calibrada
    """
    try:
        print("Calibrando fondo... mantén la cámara libre por 3 segundos")
        background = None
        
        for i in range(frames):
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Error: No se pudo leer frame durante la calibración")
                continue
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if background is None:
                background = gray.astype("float")
            
            # Acumular frames con peso
            cv2.accumulateWeighted(gray, background, 0.5)
            
            # Mostrar progreso
            progress = int((i / frames) * 100)
            cv2.putText(frame, f"Calibrando: {progress}%", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Calibración', frame)
            cv2.waitKey(1)
            
        if background is None:
            raise Exception("No se pudo calibrar el fondo - no se capturaron frames válidos")
            
        cv2.destroyWindow('Calibración')
        return background.astype(np.uint8)
    except Exception as e:
        print(f"Error en calibrate_background: {e}")
        raise