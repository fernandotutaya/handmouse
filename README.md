# Control de Mouse con Gestos de Mano

Este proyecto permite controlar el cursor del mouse y realizar acciones como clics, zoom y rotación utilizando gestos de mano captados por una cámara web. Está desarrollado en Python y utiliza las bibliotecas OpenCV y `pyautogui` para el procesamiento de imágenes y la automatización del mouse.

## Descripción

El sistema detecta la mano a través de la cámara, calibra el fondo para aislar el movimiento y reconoce gestos específicos para controlar el cursor y ejecutar acciones. Los gestos se detectan en tres regiones de la pantalla: izquierda, central y derecha, cada una con funcionalidades distintas.

### Características

- Control del cursor con el movimiento de la mano.
- Gestos para clic, zoom in/out y rotación.
- Calibración automática del fondo.
- Visualización en tiempo real de la detección y acciones.

## Requisitos

- **Python**: 3.7 o superior.
- **Bibliotecas**:
  - `opencv-python`
  - `numpy`
  - `pyautogui`

## Instalación

1. **Clona o descarga este repositorio**:
   ```bash
   git clone https://github.com/fernadnotutaya/handmouse.git
   cd handmouse
   ```

2. **Instala las dependencias**:
   ```bash
   pip install opencv-python numpy pyautogui
   ```

3. **Conecta una cámara web compatible con tu sistema**.

## Uso

1. **Ejecuta el script**:
   ```bash
   python hand_mouse.py
   ```

2. **Calibración del fondo**:
   - Mantén la cámara libre de movimiento durante 3 segundos mientras se calibra el fondo.
   - Verás una ventana con el progreso de la calibración.

3. **Control con gestos**:
   - **Región izquierda (azul)**: Gestos para zoom out y rotar a la izquierda.
   - **Región central**: Mueve el cursor, realiza clics y scroll.
   - **Región derecha (azul)**: Gestos para zoom in y rotar a la derecha.

### Teclas de control:
- Presiona `q` para salir del programa.
- Presiona `r` para recalibrar el fondo en cualquier momento.

## Gestos Reconocidos

El sistema detecta los siguientes gestos basados en la forma y posición de la mano:

- **Pinch**: Dos dedos juntos (pulgar e índice).
  - **Izquierda**: Zoom out (`Ctrl + -`).
  - **Derecha**: Zoom in (`Ctrl + +`).

- **Rotate**: Tres dedos levantados.
  - **Izquierda**: Rotar a la izquierda (`Ctrl + Alt + Left`).
  - **Derecha**: Rotar a la derecha (`Ctrl + Alt + Right`).

- **Hand Open**: Mano completamente abierta.
  - **Central**: Desplaza la página hacia arriba.

- **Hand Closed**: Mano cerrada (puño).
  - **Central**: Realiza un clic del mouse.

- **Movimiento de la mano**: Controla la posición del cursor en la región central.

## Configuración Adicional

- **Resolución de la cámara**: El sistema ajusta la cámara a `640x480` para un rendimiento óptimo. Si deseas cambiarla, modifica los valores en:
  ```python
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
  ```

- **Umbrales de detección**: Puedes ajustar los umbrales en el código (como `MIN_AREA`, `DEFECT_THRESHOLD`, `HAND_RATIO_THRESHOLD`) para adaptarlos a tu entorno o tamaño de mano.

## Solución de Problemas

- **La cámara no se detecta**:
  - Verifica que la cámara esté conectada y no esté en uso por otra aplicación.
  - Prueba con otro índice de cámara en `cv2.VideoCapture(0)` (por ejemplo, `1` o `2`).

- **Gestos no se detectan correctamente**:
  - Asegúrate de tener buena iluminación y un fondo estable.
  - Ajusta los umbrales en el código si es necesario.

- **El cursor se mueve de forma errática**:
  - Aumenta el valor de `max_len` en `smooth_movement` para un suavizado más fuerte.

- **Acciones repetidas rápidamente**:
  - Ajusta el valor de `time.sleep(0.2)` después de cada acción para controlar la frecuencia.

## Licencia

Este proyecto se distribuye bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

**Autor**: [Tutaya Rivera Clider Fernando]  
**Contacto**: [clidertutayarivera@gmail.com]

