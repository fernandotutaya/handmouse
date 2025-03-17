"""
Módulo para el manejo de movimientos y acciones del ratón.
"""
import pyautogui
import numpy as np
import time
from collections import deque

def smooth_movement(history, new_pos, max_len=7):
    """
    Suaviza el movimiento del cursor utilizando una media ponderada.
    
    Args:
        history: Deque con historial de posiciones
        new_pos: Nueva posición (x, y)
        max_len: Longitud máxima del historial
        
    Returns:
        tuple: Posición suavizada (x, y)
    """
    history.append(new_pos)
    if len(history) > max_len:
        history.popleft()
    
    # Asignar pesos mayores a las posiciones más recientes
    weights = np.linspace(0.5, 1.0, len(history))
    weighted_sum_x = sum(w * x for (x, _), w in zip(history, weights))
    weighted_sum_y = sum(w * y for (_, y), w in zip(history, weights))
    weighted_sum = sum(weights)
    
    avg_x = int(weighted_sum_x / weighted_sum)
    avg_y = int(weighted_sum_y / weighted_sum)
    return avg_x, avg_y

def perform_action(gesture, position, region, screen_size, prev_area=None, area=None):
    """
    Ejecuta la acción correspondiente al gesto detectado.
    
    Args:
        gesture: Nombre del gesto detectado
        position: Tupla (x, y) de la posición actual
        region: String indicando la región ('left', 'right', 'center')
        screen_size: Tupla (width, height) del tamaño de pantalla
        prev_area: Área del contorno en el frame anterior
        area: Área actual del contorno
        
    Returns:
        int: Área actual para actualizar el valor previo
    """
    screen_width, screen_height = screen_size
    x, y = position
    
    # Acciones según la región y el gesto
    if region == 'left':
        if gesture == "pinch":
            pyautogui.hotkey('ctrl', '-')  # Zoom out
            time.sleep(0.2)
            return area
        elif gesture == "rotate":
            pyautogui.hotkey('ctrl', 'alt', 'left')  # Rotar izquierda
            time.sleep(0.2)
            return area
            
    elif region == 'right':
        if gesture == "pinch":
            pyautogui.hotkey('ctrl', '+')  # Zoom in
            time.sleep(0.2)
            return area
        elif gesture == "rotate":
            pyautogui.hotkey('ctrl', 'alt', 'right')  # Rotar derecha
            time.sleep(0.2)
            return area
            
    else:  # Región central
        pyautogui.moveTo(x, y)
        if gesture == "hand_closed":
            pyautogui.click()
            time.sleep(0.2)
            return area
        elif gesture == "hand_open":
            pyautogui.scroll(50)  # Scroll arriba
            time.sleep(0.2)
            return area
        elif prev_area is not None and area is not None:
            area_diff = area - prev_area
            if abs(area_diff) > 2000:
                scroll_dir = 50 if area_diff > 0 else -50
                pyautogui.scroll(scroll_dir)
                time.sleep(0.2)
                
    return area

def handle_center_region(gesture, area, prev_area):
    """
    Maneja las acciones para la región central basadas en el gesto detectado.
    
    Args:
        gesture: Nombre del gesto detectado
        area: Área actual del contorno
        prev_area: Área del contorno en el frame anterior
        
    Returns:
        str: Acción realizada
    """
    if gesture == "hand_closed":
        pyautogui.click()
        time.sleep(0.2)
        return "click"
    elif gesture == "hand_open":
        pyautogui.scroll(50)  # Scroll arriba
        time.sleep(0.2)
        return "scroll_up"
    elif prev_area is not None and area is not None:
        area_diff = area - prev_area
        if abs(area_diff) > 2000:
            scroll_dir = 50 if area_diff > 0 else -50
            pyautogui.scroll(scroll_dir)
            time.sleep(0.2)
            return "scroll_down" if scroll_dir < 0 else "scroll_up"
    return None

def handle_left_region(gesture):
    """
    Maneja las acciones para la región izquierda basadas en el gesto detectado.
    
    Args:
        gesture: Nombre del gesto detectado
        
    Returns:
        str: Acción realizada
    """
    if gesture == "pinch":
        pyautogui.hotkey('ctrl', '-')  # Zoom out
        time.sleep(0.2)
        return "zoom_out"
    elif gesture == "rotate":
        pyautogui.hotkey('ctrl', 'alt', 'left')  # Rotar izquierda
        time.sleep(0.2)
        return "rotate_left"
    return None

def handle_right_region(gesture):
    """
    Maneja las acciones para la región derecha basadas en el gesto detectado.
    
    Args:
        gesture: Nombre del gesto detectado
        
    Returns:
        str: Acción realizada
    """
    if gesture == "pinch":
        pyautogui.hotkey('ctrl', '+')  # Zoom in
        time.sleep(0.2)
        return "zoom_in"
    elif gesture == "rotate":
        pyautogui.hotkey('ctrl', 'alt', 'right')  # Rotar derecha
        time.sleep(0.2)
        return "rotate_right"
    return None