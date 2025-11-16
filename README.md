# VR Filtro

Aplicación de filtros faciales con OpenCV y MediaPipe.

## Requisitos
- macOS (Intel o Apple Silicon)
- Python 3.10 (fijado para este proyecto) 

Se fuerza el uso de Python 3.10 porque algunas dependencias transitivas (ej. `jax` requerida por `mediapipe`) usan la sintaxis `match` introducida en 3.10. Usar 3.9 provoca errores de compilación.

## Instalación (macOS)
1. Instalar Python 3.10 (si no lo tienes):
  - Homebrew: `brew install python@3.10`
  - Pyenv (alternativa):
    ```bash
    brew install pyenv
    pyenv install 3.10.14
    pyenv local 3.10.14
    ```
2. Crear y activar entorno virtual (usando el binario 3.10):
   ```bash
  /opt/homebrew/bin/python3.10 -m venv .venv  # ajusta ruta si es Intel (/usr/local/opt/python@3.10/bin/python3.10)
   source .venv/bin/activate
   ```
3. Actualizar `pip` e instalar dependencias:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

  Notas macOS:
  - Usa exactamente Python 3.10 (este repo incluye `.python-version` y `.vscode/settings.json` apuntando a `.venv`).
  - No mezcles OpenCV de Homebrew con el de PyPI. Si tienes `opencv` vía `brew`, crea un venv limpio.
  - Evita instalar paquetes globalmente fuera del venv.

### Migrar desde otro Python
Si tu entorno actual era 3.9, elimina `.venv` y recrea:
```bash
rm -rf .venv
brew install python@3.10   # si falta
/opt/homebrew/bin/python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Uso
- Listar cámaras disponibles:
  ```bash
  python list_cameras.py
  ```
- Ejecutar la app principal:
  ```bash
  python main.py
  ```

## Ejecutar con Docker (Python 3.10)
Este repo incluye un `Dockerfile` basado en Python 3.10.

1) Construir la imagen:
```bash
docker build -t vr-filtro:py310 .
```

2) Ejecutar:
- Linux (X11 + cámara física):
  ```bash
  xhost +local:docker
  docker run --rm -it \
    --env DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --device /dev/video0:/dev/video0 \
    vr-filtro:py310 python main.py --index 0
  ```
- macOS (limitaciones): Docker Desktop no expone la cámara del host a contenedores. Además, para mostrar ventanas (imshow) necesitas XQuartz y redirigir X11:
  ```bash
  # Instalar y abrir XQuartz, luego:
  xhost + 127.0.0.1
  docker run --rm -it \
    -e DISPLAY=host.docker.internal:0 \
    vr-filtro:py310 python main.py
  ```
  Nota: La cámara del Mac no estará disponible dentro del contenedor. Para pruebas en macOS dentro de Docker, usa fuentes alternativas (RTSP/archivo de video) o ejecuta la app directamente en el host con el venv.

## Solución de problemas
- "No se abre la cámara": prueba otros índices (0, 1, 2) o ejecuta `python list_cameras.py`. En macOS, otorga permisos de cámara a la Terminal.
- Errores de instalación de `mediapipe`: verifica que realmente estés usando Python 3.10 (`python -V`).
- En M1/M2, si usas Rosetta accidentalmente, usa el Python nativo arm64 (`/usr/bin/python3` o `pyenv`).
