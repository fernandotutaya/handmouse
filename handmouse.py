import cv2
import numpy as np
import pyautogui
import time
from collections import deque

def calibrate_background(cap, frames=30):
    print("Calibrando fondo... mantén la cámara libre por 3 segundos")
    background = None
    for _ in range(frames):
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if background is None:
            background = gray.astype("float")
        cv2.accumulateWeighted(gray, background, 0.5)
    return background

def smooth_movement(history, new_pos, max_len=5):
    history.append(new_pos)
    if len(history) > max_len:
        history.popleft()
    avg_x = int(sum(x for x, _ in history) / len(history))
    avg_y = int(sum(y for _, y in history) / len(history))
    return avg_x, avg_y

def detect_gestures(contour):
    # Calcular casco convexo y defectos
    hull = cv2.convexHull(contour, returnPoints=False)
    defects = cv2.convexityDefects(contour, hull)
    
    if defects is None:
        return None
    
    # Contar dedos levantados
    finger_count = 0
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        if d > 10000:  # Distancia mínima para considerar un defecto
            finger_count += 1
    
    # Detectar pinch (dos dedos juntos)
    if finger_count == 1:
        return "pinch"
    # Detectar rotación (tres dedos)
    elif finger_count == 2:
        return "rotate"
    return None

def main():
    # Inicializar captura y calibración
    cap = cv2.VideoCapture(0)
    background = calibrate_background(cap)
    time.sleep(3)  # Tiempo para posicionarse después de calibración
    
    # Variables
    prev_area = 0
    screen_width, screen_height = pyautogui.size()
    pos_history = deque()  # Para suavizado
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    
    # Definir regiones (en porcentaje del ancho)
    LEFT_REGION = frame_width * 0.3
    RIGHT_REGION = frame_width * 0.7

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Diferencia con el fondo
        fg = cv2.absdiff(background.astype(np.uint8), gray)
        blurred = cv2.GaussianBlur(fg, (21, 21), 0)
        _, thresh = cv2.threshold(blurred, 30, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            max_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(max_contour)
            
            if area > 1000:
                M = cv2.moments(max_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Mapeo con suavizado
                    screen_x = int(np.interp(cx, [0, frame.shape[1]], [0, screen_width]))
                    screen_y = int(np.interp(cy, [0, frame.shape[0]], [0, screen_height]))
                    smooth_x, smooth_y = smooth_movement(pos_history, (screen_x, screen_y))
                    
                    # Gestos
                    gesture = detect_gestures(max_contour)
                    
                    # Regiones específicas
                    if cx < LEFT_REGION:  # Región izquierda
                        if gesture == "pinch":
                            pyautogui.hotkey('ctrl', '-')  # Zoom out
                        elif gesture == "rotate":
                            pyautogui.hotkey('ctrl', 'alt', 'left')  # Rotar izquierda
                            
                    elif cx > RIGHT_REGION:  # Región derecha
                        if gesture == "pinch":
                            pyautogui.hotkey('ctrl', '+')  # Zoom in
                        elif gesture == "rotate":
                            pyautogui.hotkey('ctrl', 'alt', 'right')  # Rotar derecha
                            
                    else:  # Región central
                        pyautogui.moveTo(smooth_x, smooth_y)
                        if area < 5000 and prev_area > 7000:
                            pyautogui.click()
                            time.sleep(0.2)
                        area_diff = area - prev_area
                        if abs(area_diff) > 2000:
                            pyautogui.scroll(50 if area_diff > 0 else -50)
                    
                    prev_area = area
                    
                    # Visualización
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                    cv2.putText(frame, f"Gesture: {gesture or 'none'}", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Dibujar regiones
        cv2.line(frame, (int(LEFT_REGION), 0), (int(LEFT_REGION), frame.shape[0]), (255, 0, 0), 2)
        cv2.line(frame, (int(RIGHT_REGION), 0), (int(RIGHT_REGION), frame.shape[0]), (255, 0, 0), 2)
        
        cv2.imshow('Hand Mouse', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()