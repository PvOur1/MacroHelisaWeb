Helisa Bot — Macro + Excel automation

Resumen
- `Cargue_Excel.py` es la UI principal que carga un Excel y automatiza una macro usando `pyautogui`.

Mejoras añadidas
- Logging a `helisa.log` y consola.
- `config.json` con `DRY_RUN` y `LOG_FILE`.
- Modo `DRY_RUN` (si `DRY_RUN: true`) que registra acciones en vez de interactuar con el mouse/teclado.
- Flags de parada basados en `threading.Event()` para manejo seguro entre hilos.

Archivos nuevos
- `requirements.txt` — dependencias sugeridas.
- `config.json` — configuración por defecto.
- `README.md` — este archivo.

Uso rápido
1. Crear un entorno virtual (recomendado) e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Edita `config.json` según necesites (`DRY_RUN: true` para probar sin clicks).
3. Ejecuta `Cargue_Excel.py` con Python.

Notas
- Ajusta las rutas de las imágenes y regiones dentro de `Cargue_Excel.py` si cambias la estructura del proyecto.
- Para pruebas de integración y automatización, usa `DRY_RUN: true`.
 - Las imágenes ahora están en la carpeta `images/`. Mantén los PNG allí o actualiza las rutas en `Cargue_Excel.py`.
