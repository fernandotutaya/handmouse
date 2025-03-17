"""
Configuraciones globales para el sistema de control por gestos.
Centraliza todas las constantes y configuraciones del programa.
"""
import pyautogui

# Configuración de pyautogui
pyautogui.FAILSAFE = True
PYAUTOGUI_PAUSE = 0.1  # Pausa entre comandos en segundos

# Configuración para reconocimiento de gestos
MIN_AREA = 1000  # Área mínima para considerar un contorno
DEFECT_THRESHOLD = 12000  # Umbral para detectar defectos en la convexidad
HAND_RATIO_THRESHOLD = 1.5  # Umbral para detección de mano abierta/cerrada

# Configuración de estabilidad
GESTURE_STABILITY = 5  # Cuadros necesarios para confirmar un gesto
SCREEN_MARGIN = 50  # Margen en píxeles para evitar llegar a los bordes de la pantalla

# Configuración de la cámara
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CALIBRATION_FRAMES = 30  # Número de frames para calibrar
FRAME_WIDTH = 640  # Ancho de la ventana de visualización
FRAME_HEIGHT = 480  # Alto de la ventana de visualización
LEFT_REGION_FACTOR = 0.25  # Factor para determinar región izquierda
RIGHT_REGION_FACTOR = 0.75  # Factor para determinar región derecha
GESTURE_STABILITY = 5  # Cuadros necesarios para confirmar un gesto