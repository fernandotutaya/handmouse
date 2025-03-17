"""
Utilidades varias para el programa de control por gestos.
"""
import cv2
import numpy as np
import sys
import signal

def signal_handler(sig, frame):
    """
    Manejador de señales para terminar el programa con Ctrl+C.
    """
    print("\nPrograma interrumpido por el usuario (Ctrl+C)")
    sys.exit(0)

def setup_exit_handler():
    """
    Configura el manejador de señales para poder salir con Ctrl+C.
    """
    signal.signal(signal.SIGINT, signal_handler)

def process_frame(frame, background):
    """
    Procesa el frame para extraer la silueta de la mano.
    
    Args:
        frame: Frame capturado
        background: Fondo calibrado
        
    Returns:
        thresh: Imagen binaria con la silueta
        display_frame: Frame para visualización
    """
    display_frame = frame.copy()
    
    # Convertir a escala de grises y aplicar blur
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    
    # Restar el fondo para obtener el primer plano
    fg = cv2.absdiff(background, gray)
    
    # Binarizar la imagen
    _, thresh = cv2.threshold(fg, 25, 255, cv2.THRESH_BINARY)
    
    # Operaciones morfológicas para limpiar la imagen
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    return thresh, display_frame

def create_control_panel():
    """
    Crea un panel de control para mostrar información.
    
    Returns:
        control_area: Imagen negra para mostrar información
    """
    return np.zeros((300, 400, 3), np.uint8)

def update_control_panel(control_area, area=0, position=(0, 0), gesture=None, action=None, is_gesture_applied=False):
    """
    Actualiza el panel de control con la información actual.
    
    Args:
        control_area: Panel de control a actualizar
        area: Área del contorno de la mano
        position: Posición (x, y) del centro de la mano
        gesture: Gesto detectado actualmente
        action: Acción realizada
        is_gesture_applied: Indica si el gesto se está aplicando
        
    Returns:
        control_area: Panel de control actualizado
    """
    # Limpiar el panel
    control_area.fill(0)
    
    # Mostrar información de área y posición
    cv2.putText(control_area, f"Área: {int(area)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cx, cy = position
    cv2.putText(control_area, f"Posición: ({cx}, {cy})", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
    # Mostrar información de gesto
    cv2.putText(control_area, f"Gesto: {gesture}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
    # Indicador de gesto aplicado
    if is_gesture_applied:
        cv2.putText(control_area, "GESTO APLICADO", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Acción realizada
    if action:
        cv2.putText(control_area, f"ACCIÓN: {action}", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return control_area

def draw_interface_guides(frame, left_region, right_region, frame_height, frame_width):
    """
    Dibuja guías de la interfaz en el frame.
    
    Args:
        frame: Frame donde dibujar las guías
        left_region: Coordenada x de la región izquierda
        right_region: Coordenada x de la región derecha
        frame_height: Altura del frame
        frame_width: Anchura del frame
        
    Returns:
        frame: Frame con las guías dibujadas
    """
    # Líneas de división de regiones
    cv2.line(frame, (int(left_region), 0), (int(left_region), frame_height), (255, 0, 0), 2)
    cv2.line(frame, (int(right_region), 0), (int(right_region), frame_height), (255, 0, 0), 2)
    
    # Barra de instrucciones
    cv2.rectangle(frame, (0, frame_height-30), (frame_width, frame_height), (0, 0, 0), -1)
    cv2.putText(frame, "Presiona 'q' para salir o 'r' para recalibrar", (10, frame_height-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return frame

def print_system_info():
    """
    Imprime información del sistema al iniciar el programa.
    """
    print("Iniciando programa Hand Mouse...")
    print(f"OpenCV versión: {cv2.__version__}")
    print(f"NumPy versión: {np.__version__}")
    
    try:
        import pyautogui
        print(f"PyAutoGUI versión: {pyautogui.__version__}")
    except ImportError:
        print("PyAutoGUI no está instalado correctamente.")