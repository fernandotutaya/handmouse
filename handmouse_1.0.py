import cv2
import numpy as np
import pyautogui
import time
from collections import deque
import mediapipe as mp

# Función para suavizar el movimiento del mouse
def smooth_movement(history, new_pos, max_len=5):
    history.append(new_pos)
    if len(history) > max_len:
        history.popleft()
    avg_x = int(sum(x for x, _ in history) / len(history))
    avg_y = int(sum(y for _, y in history) / len(history))
    return avg_x, avg_y

# Función para detectar gestos simples
def detect_gestures(landmarks):
    thumb_tip = landmarks[4]  # Pulgar
    index_tip = landmarks[8]  # Índice
    distance = np.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)
    if distance < 0.05:  # Umbral para "pinch"
        return "pinch"
    if (landmarks[8][1] < landmarks[6][1] and 
        landmarks[12][1] < landmarks[10][1] and 
        landmarks[16][1] < landmarks[14][1]):
        return "rotate"
    return None

# Función principal
def main():
    print("Iniciando el programa...")

    # Inicializar captura de video
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara. Verifica que esté conectada y no esté en uso por otra aplicación.")
        input("Presiona Enter para salir...")
        return

    print("Cámara inicializada correctamente.")

    # Configurar MediaPipe Hands
    try:
        mp_hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        print("MediaPipe Hands configurado correctamente.")
    except Exception as e:
        print(f"Error al inicializar MediaPipe: {e}")
        cap.release()
        input("Presiona Enter para salir...")
        return

    # Dimensiones de pantalla y video
    screen_width, screen_height = pyautogui.size()
    pos_history = deque()
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    LEFT_REGION = frame_width * 0.3
    RIGHT_REGION = frame_width * 0.7

    print(f"Dimensiones del frame: {frame_width}x{frame_height}")
    print("Programa listo. Usa 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame de la cámara.")
            break

        print("Frame leído correctamente.")

        # Espejar la imagen y convertir a RGB
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar con MediaPipe
        try:
            results = mp_hands.process(rgb_frame)
            print("Frame procesado por MediaPipe.")
        except Exception as e:
            print(f"Error al procesar el frame con MediaPipe: {e}")
            break

        # Si se detecta una mano
        if results.multi_hand_landmarks:
            print("Mano detectada.")
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = [(lm.x * frame_width, lm.y * frame_height) for lm in hand_landmarks.landmark]
                wrist = hand_landmarks.landmark[0]  # Muñeca como punto de referencia
                cx = int(wrist.x * frame_width)
                cy = int(wrist.y * frame_height)

                # Mapeo a pantalla
                screen_x = int(np.interp(cx, [0, frame_width], [0, screen_width]))
                screen_y = int(np.interp(cy, [0, frame_height], [0, screen_height]))
                smooth_x, smooth_y = smooth_movement(pos_history, (screen_x, screen_y))

                # Detectar gestos
                gesture = detect_gestures([(lm.x, lm.y) for lm in hand_landmarks.landmark])

                # Acciones según regiones
                if cx < LEFT_REGION:
                    if gesture == "pinch":
                        pyautogui.hotkey('ctrl', '-')
                    elif gesture == "rotate":
                        pyautogui.hotkey('ctrl', 'alt', 'left')
                elif cx > RIGHT_REGION:
                    if gesture == "pinch":
                        pyautogui.hotkey('ctrl', '+')
                    elif gesture == "rotate":
                        pyautogui.hotkey('ctrl', 'alt', 'right')
                else:
                    pyautogui.moveTo(smooth_x, smooth_y)
                    if landmarks[8][1] > landmarks[6][1]:  # Índice hacia abajo para clic
                        pyautogui.click()
                        time.sleep(0.2)

                # Visualización
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"Gesture: {gesture or 'none'}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            print("No se detectó ninguna mano.")

        # Dibujar regiones
        cv2.line(frame, (int(LEFT_REGION), 0), (int(LEFT_REGION), frame_height), (255, 0, 0), 2)
        cv2.line(frame, (int(RIGHT_REGION), 0), (int(RIGHT_REGION), frame_height), (255, 0, 0), 2)

        # Mostrar frame
        cv2.imshow('Hand Mouse', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Saliendo del programa por tecla 'q'.")
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    mp_hands.close()
    print("Programa terminado.")
    input("Presiona Enter para cerrar...")

if __name__ == "__main__":
    main()