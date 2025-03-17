import cv2
import numpy as np
import pyautogui
import time
from collections import deque
import sys
import signal

# Configuración de pyautogui para evitar excepciones
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  # Reduce la pausa entre comandos

# Configuración global para el reconocimiento de gestos
MIN_AREA = 1000  # Área mínima para considerar un contorno
DEFECT_THRESHOLD = 12000  # Umbral para detectar defectos en la convexidad
HAND_RATIO_THRESHOLD = 1.5  # Ajustado para mejor detección de mano abierta/cerrada

def signal_handler(sig, frame):
    print("\nPrograma interrumpido por el usuario (Ctrl+C)")
    sys.exit(0)

# Registrar el manejador de señales
signal.signal(signal.SIGINT, signal_handler)

def calibrate_background(cap, frames=30):
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
            
            cv2.accumulateWeighted(gray, background, 0.5)
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

def smooth_movement(history, new_pos, max_len=7):
    """Suaviza el movimiento usando una ventana más grande para mayor estabilidad"""
    history.append(new_pos)
    if len(history) > max_len:
        history.popleft()
    
    weights = np.linspace(0.5, 1.0, len(history))
    weighted_sum_x = sum(w * x for (x, _), w in zip(history, weights))
    weighted_sum_y = sum(w * y for (_, y), w in zip(history, weights))
    weighted_sum = sum(weights)
    
    avg_x = int(weighted_sum_x / weighted_sum)
    avg_y = int(weighted_sum_y / weighted_sum)
    return avg_x, avg_y

def detect_gestures(contour, frame):
    """Versión mejorada de la detección de gestos con visualización"""
    try:
        if contour is None or len(contour) < 5:
            return None
            
        # Calcular el rectángulo mínimo que contiene el contorno
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
        
        # Calcular el ratio largo/ancho
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
        
        # Lógica de detección mejorada
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

def main():
    try:
        # Inicializar captura
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: No se pudo abrir la cámara. Verifica que esté conectada.")
            return
            
        print("Cámara inicializada correctamente.")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Calibración
        try:
            background = calibrate_background(cap)
            print("Calibración completada. Posiciónate para comenzar...")
            time.sleep(2)
        except Exception as e:
            print(f"Error durante la calibración: {e}")
            cap.release()
            cv2.destroyAllWindows()
            return
        
        # Variables
        prev_area = 0
        screen_width, screen_height = pyautogui.size()
        pos_history = deque()
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        LEFT_REGION = frame_width * 0.3
        RIGHT_REGION = frame_width * 0.7
        
        last_gesture = None
        gesture_counter = 0
        GESTURE_STABILITY = 5
        SCREEN_MARGIN = 50
        
        control_area = np.zeros((300, 400, 3), np.uint8)
        
        print("Iniciando captura de movimiento. Presiona 'q' para salir o 'r' para recalibrar.")
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Error: No se pudo leer frame")
                break
                
            frame = cv2.flip(frame, 1)
            display_frame = frame.copy()
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            fg = cv2.absdiff(background, gray)
            _, thresh = cv2.threshold(fg, 25, 255, cv2.THRESH_BINARY)
            
            kernel = np.ones((5, 5), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
            
            cv2.imshow('Threshold', thresh)
            
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            cv2.line(display_frame, (int(LEFT_REGION), 0), (int(LEFT_REGION), frame_height), (255, 0, 0), 2)
            cv2.line(display_frame, (int(RIGHT_REGION), 0), (int(RIGHT_REGION), frame_height), (255, 0, 0), 2)
            
            cv2.rectangle(display_frame, (0, frame_height-30), (frame_width, frame_height), (0, 0, 0), -1)
            cv2.putText(display_frame, "Presiona 'q' para salir o 'r' para recalibrar", (10, frame_height-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            if contours:
                max_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(max_contour)
                
                if area > MIN_AREA:
                    cv2.drawContours(display_frame, [max_contour], 0, (0, 255, 0), 2)
                    
                    M = cv2.moments(max_contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        cv2.circle(display_frame, (cx, cy), 5, (0, 0, 255), -1)
                        
                        current_gesture = detect_gestures(max_contour, display_frame)
                        
                        if current_gesture == last_gesture:
                            gesture_counter += 1
                        else:
                            gesture_counter = 0
                            last_gesture = current_gesture
                        
                        # Actualizar control_area
                        control_area.fill(0)
                        cv2.putText(control_area, f"Área: {int(area)}", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        cv2.putText(control_area, f"Posición: ({cx}, {cy})", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        cv2.putText(control_area, f"Gesto: {current_gesture}", (10, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        
                        if gesture_counter >= GESTURE_STABILITY:
                            cv2.putText(control_area, "GESTO APLICADO", (10, 120),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            screen_x = int(np.interp(cx, [0, frame_width], [SCREEN_MARGIN, screen_width - SCREEN_MARGIN]))
                            screen_y = int(np.interp(cy, [0, frame_height], [SCREEN_MARGIN, screen_height - SCREEN_MARGIN]))
                            smooth_x, smooth_y = smooth_movement(pos_history, (screen_x, screen_y))
                            
                            # Acciones por región y gesto
                            if cx < LEFT_REGION:  # Región izquierda
                                if current_gesture == "pinch":
                                    cv2.putText(control_area, "ACCIÓN: Zoom Out", (10, 150),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    pyautogui.hotkey('ctrl', '-')
                                    time.sleep(0.2)
                                elif current_gesture == "rotate":
                                    cv2.putText(control_area, "ACCIÓN: Rotar Izquierda", (10, 150),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    pyautogui.hotkey('ctrl', 'alt', 'left')
                                    time.sleep(0.2)
                            elif cx > RIGHT_REGION:  # Región derecha
                                if current_gesture == "pinch":
                                    cv2.putText(control_area, "ACCIÓN: Zoom In", (10, 150),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    pyautogui.hotkey('ctrl', '+')
                                    time.sleep(0.2)
                                elif current_gesture == "rotate":
                                    cv2.putText(control_area, "ACCIÓN: Rotar Derecha", (10, 150),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    pyautogui.hotkey('ctrl', 'alt', 'right')
                                    time.sleep(0.2)
                            else:  # Región central
                                pyautogui.moveTo(smooth_x, smooth_y)
                                if current_gesture == "hand_closed":
                                    cv2.putText(control_area, "ACCIÓN: Clic", (10, 150),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    pyautogui.click()
                                    time.sleep(0.2)
                                elif current_gesture == "hand_open":
                                    cv2.putText(control_area, "ACCIÓN: Scroll Arriba", (10, 150),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    pyautogui.scroll(50)
                                    time.sleep(0.2)
                                else:
                                    area_diff = area - prev_area
                                    if abs(area_diff) > 2000:
                                        scroll_dir = 50 if area_diff > 0 else -50
                                        cv2.putText(control_area, f"ACCIÓN: Scroll {'Arriba' if area_diff > 0 else 'Abajo'}",
                                                    (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                        pyautogui.scroll(scroll_dir)
                                        time.sleep(0.2)
                            
                            prev_area = area
            
            cv2.imshow('Hand Mouse', display_frame)
            cv2.imshow('Control Area', control_area)
            
            key = cv2.waitKey(1)
            if key == ord('q'):
                print("Saliendo del programa por tecla 'q'.")
                break
            elif key == ord('r'):
                print("Recalibrando...")
                background = calibrate_background(cap)
                print("Recalibración completada.")
        
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error en main: {e}")
    finally:
        print("Programa terminado.")

if __name__ == "__main__":
    try:
        print("Iniciando programa Hand Mouse...")
        print(f"OpenCV versión: {cv2.__version__}")
        print(f"NumPy versión: {np.__version__}")
        print(f"PyAutoGUI versión: {pyautogui.__version__}")
        main()
    except Exception as e:
        print(f"Error crítico: {e}")
        sys.exit(1)
    