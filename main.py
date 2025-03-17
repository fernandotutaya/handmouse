"""
Punto de entrada principal para el programa de control por gestos.
"""
import cv2
import numpy as np
import pyautogui
import time
import sys
from collections import deque

# Importar módulos del proyecto
import config
import calibration
import gesture_detection
import movement
import utils

def main():
    """
    Función principal del programa.
    """
    try:
        # Configurar el manejador de señales para Ctrl+C
        utils.setup_exit_handler()
        
        # Inicializar configuración de PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = config.PYAUTOGUI_PAUSE
        
        # Imprimir información del sistema
        utils.print_system_info()
        
        # Inicializar captura de video
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: No se pudo abrir la cámara. Verifica que esté conectada.")
            return
            
        print("Cámara inicializada correctamente.")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        
        # Realizar calibración inicial
        try:
            background = calibration.calibrate_background(cap)
            print("Calibración completada. Posiciónate para comenzar...")
            time.sleep(2)
        except Exception as e:
            print(f"Error durante la calibración: {e}")
            cap.release()
            cv2.destroyAllWindows()
            return
        
        # Variables para seguimiento
        prev_area = 0
        screen_width, screen_height = pyautogui.size()
        pos_history = deque()
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Definir regiones de la pantalla
        left_region = frame_width * config.LEFT_REGION_FACTOR
        right_region = frame_width * config.RIGHT_REGION_FACTOR
        
        # Inicializar variables para detección de gestos
        last_gesture = None
        gesture_counter = 0
        
        # Crear panel de control
        control_area = utils.create_control_panel()
        
        print("Iniciando captura de movimiento. Presiona 'q' para salir o 'r' para recalibrar.")
        
        # Bucle principal
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Error: No se pudo leer frame")
                break
                
            # Voltear horizontalmente para una interfaz tipo espejo
            frame = cv2.flip(frame, 1)
            
            # Procesar frame para extraer silueta
            thresh, display_frame = utils.process_frame(frame, background)
            
            # Dibujar guías de interfaz
            display_frame = utils.draw_interface_guides(
                display_frame, left_region, right_region, 
                frame_height, frame_width
            )
            
            # Mostrar imagen umbralizada
            cv2.imshow('Threshold', thresh)
            
            # Encontrar contornos en la imagen umbralizada
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Procesar contornos si existen
            if contours:
                max_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(max_contour)
                
                # Procesar solo si el contorno supera el área mínima
                if area > config.MIN_AREA:
                    cv2.drawContours(display_frame, [max_contour], 0, (0, 255, 0), 2)
                    
                    # Calcular centro del contorno
                    M = cv2.moments(max_contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        cv2.circle(display_frame, (cx, cy), 5, (0, 0, 255), -1)
                        
                        # Detectar gestos
                        current_gesture = gesture_detection.detect_gestures(max_contour, display_frame)
                        
                        # Estabilizar gestos
                        if current_gesture == last_gesture:
                            gesture_counter += 1
                        else:
                            gesture_counter = 0
                            last_gesture = current_gesture
                        
                        # Aplicar gestos solo si son estables
                        is_gesture_applied = gesture_counter >= config.GESTURE_STABILITY
                        action = None
                        
                        if is_gesture_applied:
                            # Mapear coordenadas de la cámara a coordenadas de pantalla
                            screen_x = int(np.interp(cx, [0, frame_width], 
                                                   [config.SCREEN_MARGIN, screen_width - config.SCREEN_MARGIN]))
                            screen_y = int(np.interp(cy, [0, frame_height], 
                                                   [config.SCREEN_MARGIN, screen_height - config.SCREEN_MARGIN]))
                            
                            # Suavizar movimiento
                            smooth_x, smooth_y = movement.smooth_movement(pos_history, (screen_x, screen_y))
                            
                            # Acciones por región y gesto
                            if cx < left_region:  # Región izquierda
                                action = movement.handle_left_region(current_gesture)
                            elif cx > right_region:  # Región derecha
                                action = movement.handle_right_region(current_gesture)
                            else:  # Región central
                                pyautogui.moveTo(smooth_x, smooth_y)
                                action = movement.handle_center_region(current_gesture, area, prev_area)
                            
                            prev_area = area
                        
                        # Actualizar panel de control
                        control_area = utils.update_control_panel(
                            control_area, area, (cx, cy), 
                            current_gesture, action, is_gesture_applied
                        )
            
            # Mostrar frames
            cv2.imshow('Hand Mouse', display_frame)
            cv2.imshow('Control Area', control_area)
            
            # Procesar teclas
            key = cv2.waitKey(1)
            if key == ord('q'):
                print("Saliendo del programa por tecla 'q'.")
                break
            elif key == ord('r'):
                print("Recalibrando...")
                background = calibration.calibrate_background(cap)
                print("Recalibración completada.")
        
        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error en main: {e}")
    finally:
        print("Programa terminado.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error crítico: {e}")
        sys.exit(1)