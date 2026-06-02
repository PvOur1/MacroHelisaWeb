# -*- coding: utf-8 -*-
"""
Helisa Bot v1.0 - UI + Excel + Macro estricta + Cédula (arranque directo)
- Macro estricta (no se salta pasos).
- 📂 Cargar Excel y mostrar (Consecutivo, numero_documento, eca).
- ▶ Procesar filas del Excel: escribe numero_documento como cédula (Enter→Right→numero_documento→Enter→(RUN si está)→macro).
- 🪪 Ejecutar por cédula: mismo flujo, pero con el valor ingresado.
- Hotkeys opcionales: F3 (una corrida), F12 (detener escucha).
- ⏹ Detener Excel: corta el procesamiento del archivo.
- Pinta en verde la fila del DF cuando se completa con éxito.
"""

import time
import random
import threading
import logging
import json
import os
import sys
import ctypes

import pyautogui
import keyboard
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import pandas as pd
try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None

# ---------------- Config básica ----------------
pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = True

# Imágenes (ajústalas a tus archivos reales). Ahora en carpeta `images/`
IMG_DIR = os.path.join(os.path.dirname(__file__), "images")
IMG_ACEPTAR_ORDEN = os.path.join(IMG_DIR, "ACEPTAR_ORDEN.png")
IMG_CERRAR_ORDEN  = os.path.join(IMG_DIR, "Cerrar_Orden.png")
IMG_BTN1          = os.path.join(IMG_DIR, "btn1.png")
IMG_BTN2          = os.path.join(IMG_DIR, "btn2.png")
IMG_BTN3          = os.path.join(IMG_DIR, "btn3.png")
IMG_BTN4          = os.path.join(IMG_DIR, "btn4.png")
IMG_BTN5          = os.path.join(IMG_DIR, "btn5.png")
IMG_RUN               = os.path.join(IMG_DIR, "btn_run.png")         # imagen opcional que se clicará antes de macro
IMG_CENTRO_COSTOS_BTN = os.path.join(IMG_DIR, "centro_costos.png") # botón tres puntos del campo CENTRO COSTOS
INTERFACES_DIR    = os.path.join(os.path.dirname(__file__), "interfaces")
IMG_ICON          = os.path.join(INTERFACES_DIR, "cogwheel.png")
ICON_SIZE = 28

# Regiones base (ajústalas a tu UI). Se guardan por resolución en `CONFIG['REGIONS']`.
# Valores actuales se consideran 720p por defecto.
REGION_ACEPTAR = (401, 319, 556, 196) 
REGION_BTN1    = (256, 171, 854, 120)
REGION_BTN2    = (247, 240, 862, 114)
REGION_BTN3    = (220, 560, 930, 140)   # misma región que BTN4
REGION_BTN4    = (220, 560, 930, 140)   # ampliada para robustez
REGION_BTN5    = (257, 635, 848, 41)

# Región donde buscar IMG_RUN (elegir cédula)
REGION_TERCERO = (192, 292, 1054, 251)

# Estructura de resoluciones (720p preconfigurada; 1080p y 2k escaladas x1.5 y x2.0)
RESOLUTIONS = {
    "720p": {
        "REGION_ACEPTAR": REGION_ACEPTAR,
        "REGION_BTN1": REGION_BTN1,
        "REGION_BTN2": REGION_BTN2,
        "REGION_BTN3": REGION_BTN3,
        "REGION_BTN4": REGION_BTN4,
        "REGION_BTN5": REGION_BTN5,
        "REGION_TERCERO": REGION_TERCERO,
    },
    "1080p": {
        # Escalado x1.5 desde 720p (1920×1080 / 1280×720)
        "REGION_ACEPTAR": (601,  478,  834, 294),
        "REGION_BTN1":    (384,  256, 1281, 180),
        "REGION_BTN2":    (370,  360, 1293, 171),
        "REGION_BTN3":    (330,  840, 1395, 210),
        "REGION_BTN4":    (330,  840, 1395, 210),
        "REGION_BTN5":    (385,  952, 1272,  61),
        "REGION_TERCERO": (288,  438, 1581, 376),
    },
    "2k": {
        # Escalado x2.0 desde 720p (2560×1440 / 1280×720)
        "REGION_ACEPTAR": (802,  638, 1112, 392),
        "REGION_BTN1":    (512,  342, 1708, 240),
        "REGION_BTN2":    (494,  480, 1724, 228),
        "REGION_BTN3":    (440, 1120, 1860, 280),
        "REGION_BTN4":    (440, 1120, 1860, 280),
        "REGION_BTN5":    (514, 1270, 1696,  82),
        "REGION_TERCERO": (384,  584, 2108, 502),
    },
}


def apply_resolution(name: str):
    """Aplica las regiones definidas para la resolución `name` al conjunto de variables globales.
    Si no existen, no modifica las regiones actuales.
    """
    global REGION_ACEPTAR, REGION_BTN1, REGION_BTN2, REGION_BTN3, REGION_BTN4, REGION_BTN5, REGION_TERCERO
    r = RESOLUTIONS.get(name, {})
    if not r:
        logging.info("No hay regiones para resolución %s, mantengo valores actuales", name)
        return
    try:
        if r.get("REGION_ACEPTAR"):
            REGION_ACEPTAR = tuple(r.get("REGION_ACEPTAR"))
        if r.get("REGION_BTN1"):
            REGION_BTN1 = tuple(r.get("REGION_BTN1"))
        if r.get("REGION_BTN2"):
            REGION_BTN2 = tuple(r.get("REGION_BTN2"))
        if r.get("REGION_BTN3"):
            REGION_BTN3 = tuple(r.get("REGION_BTN3"))
        if r.get("REGION_BTN4"):
            REGION_BTN4 = tuple(r.get("REGION_BTN4"))
        if r.get("REGION_BTN5"):
            REGION_BTN5 = tuple(r.get("REGION_BTN5"))
        if r.get("REGION_TERCERO"):
            REGION_TERCERO = tuple(r.get("REGION_TERCERO"))
        logging.info("Regiones aplicadas para resolución %s", name)
    except Exception:
        logging.exception("Error aplicando regiones para %s", name)

# Barrido de confidencias (si tienes opencv-python instalado)
CONFIDENCES = (0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50)

# Mapeo ECA -> código de centro de costos (normalizado a mayusculas sin espacios extra)
ECA_CODIGO = {
    "PRINCIPAL":       "01",
    "SAN ANDRES":      "02",
    "METALPLAS":       "03",
    "LA PLAYA":        "04",
    "SANTANDER":       "05",
    "RECIPLUS":        "06",
    "LA ARBOLEDA":     "07",
    "PLANETA AZUL":    "08",
    "GEORECICLABLES":  "09",
    "JENNY":           "10",
    "JOHANNA":         "11",
}

# Estado global
CURRENT_DF = None
# Use threading.Event for thread-safe stop flags
STOP_FLAG = threading.Event()       # detener escucha/loops generales
STOP_EXCEL = threading.Event()      # detener solo el procesamiento de Excel
LISTENING = threading.Event()

# Config / comportamiento
CONFIG = {
    "DRY_RUN": False,
    "LOG_FILE": "helisa.log"
}



def load_config(path: str = "config.json"):
    global CONFIG
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                CONFIG.update(data)
    except Exception:
        pass


def setup_logging():
    lf = CONFIG.get("LOG_FILE", "helisa.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        handlers=[
            logging.FileHandler(lf, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def init_dry_run():
    """If DRY_RUN is enabled, replace dangerous pyautogui calls with no-ops that log actions."""
    # Capture originals if not already
    global ORIGINAL_PYAUTOGUI
    try:
        ORIGINAL_PYAUTOGUI  # type: ignore
    except NameError:
        ORIGINAL_PYAUTOGUI = {
            "click": pyautogui.click,
            "doubleClick": getattr(pyautogui, "doubleClick", None),
            "press": pyautogui.press,
            "typewrite": pyautogui.typewrite,
            "moveTo": pyautogui.moveTo,
            "screenshot": pyautogui.screenshot,
            "locateOnScreen": pyautogui.locateOnScreen,
        }

    if CONFIG.get("DRY_RUN"):
        logging.info("DRY_RUN enabled — pyautogui actions will be logged, not executed")

        def _noop(*args, **kwargs):
            logging.info("DRY_RUN action: %s %s", args, kwargs)

        # Methods used by the script -> log instead of performing
        pyautogui.click = lambda *a, **k: logging.info("DRY click %s %s", a, k)
        pyautogui.doubleClick = lambda *a, **k: logging.info("DRY doubleClick %s %s", a, k)
        pyautogui.press = lambda *a, **k: logging.info("DRY press %s %s", a, k)
        pyautogui.typewrite = lambda *a, **k: logging.info("DRY typewrite %s %s", a, k)
        pyautogui.moveTo = lambda *a, **k: logging.info("DRY moveTo %s %s", a, k)
        pyautogui.screenshot = lambda *a, **k: _noop(*a, **k) or None
        # Locate on screen should return None in dry-run (no images found)
        pyautogui.locateOnScreen = lambda *a, **k: None
    else:
        # Restore originals if available
        try:
            for k, v in ORIGINAL_PYAUTOGUI.items():
                if v is not None:
                    setattr(pyautogui, k, v)
        except Exception:
            logging.exception("No se pudieron restaurar las funciones originales de pyautogui")

# Mapeo índice DF -> item Treeview (para colorear filas)
TREE_INDEX = {}
# Mapeo inverso: item Treeview -> índice DF (para reanudar desde selección)
ITEM_INDEX = {}

# ---------------- Manejo seguro de excepciones de imagen ----------------
try:
    import pyscreeze
    PYSCR_IMAGE_NOT_FOUND = pyscreeze.ImageNotFoundException
except Exception:
    class PYSCR_IMAGE_NOT_FOUND(Exception):
        pass

# ---------------- Utilidades de imágenes (robustas) ----------------
class StopExcelException(Exception):
    """Se lanza cuando STOP_EXCEL se activa durante una búsqueda de imagen."""
    pass


def fill_centro_costos(eca_val: str):
    """Localiza la imagen del campo CENTRO COSTOS en REGION_TERCERO y hace clic
    en los tres puntos (extremo derecho del box encontrado), luego escribe el
    código correspondiente a `eca_val` y presiona Enter.
    Si no encuentra la imagen o el ECA no tiene mapeo, registra un aviso y continúa.
    """
    codigo = ECA_CODIGO.get(str(eca_val).strip().upper())
    if not codigo:
        logging.warning("fill_centro_costos: ECA '%s' no tiene código definido, se omite.", eca_val)
        return False

    # Localizar el campo CENTRO COSTOS (imagen completa del campo)
    # Pequeña pausa para que la UI termine de renderizar tras el Enter anterior
    time.sleep(0.6)

    # Intento 1: búsqueda normal (color)
    box = wait_image(IMG_CENTRO_COSTOS_BTN, region=REGION_TERCERO, timeout=8.0, confidences=CONFIDENCES)
    # Intento 2: fallback en escala de grises (más tolerante a diferencias de estado/foco)
    if not box:
        logging.info("fill_centro_costos: reintentando con grayscale=True…")
        box = wait_image(IMG_CENTRO_COSTOS_BTN, region=REGION_TERCERO, timeout=6.0,
                         confidences=CONFIDENCES, grayscale=True)
    if not box:
        logging.warning("fill_centro_costos: no se encontró IMG_CENTRO_COSTOS_BTN en REGION_TERCERO.")
        return False

    # Calcular posición de los tres puntos: extremo derecho del box, centrado verticalmente
    left, top, width, height = box.left, box.top, box.width, box.height

    # El botón de tres puntos está a la derecha del campo.
    # OFFSET_TRES_PUNTOS: píxeles DESDE el borde derecho hacia adentro.
    # Si el clic no cae bien, ajusta este valor (prueba 10, 15, 20...).
    OFFSET_TRES_PUNTOS = 12
    x_tres_puntos = left + width - OFFSET_TRES_PUNTOS
    y_tres_puntos = top + height // 2

    # Mover el mouse al punto calculado para que puedas ver visualmente si es correcto
    pyautogui.moveTo(x_tres_puntos, y_tres_puntos, duration=0.3)
    time.sleep(0.2)
    logging.info(
        "fill_centro_costos: box=(%d,%d,%d,%d)  clic en (%d,%d)  offset=%d",
        left, top, width, height, x_tres_puntos, y_tres_puntos, OFFSET_TRES_PUNTOS
    )
    pyautogui.click(x_tres_puntos, y_tres_puntos)
    time.sleep(0.4)

    pyautogui.press("up")
    time.sleep(0.2)
    pyautogui.press("down")
    time.sleep(0.2)

    pyautogui.typewrite(codigo, interval=0.05)
    time.sleep(0.5)
    pyautogui.press("enter")
    time.sleep(1.0)  # Aumentado: dar tiempo al sistema a procesar la entrada
    print(f"[INFO] Centro costos: ECA='{eca_val}' → código '{codigo}' ingresado (clic en tres puntos).")
    return True


def wait_image(img_path, region=None, timeout=8.0, poll=0.25, confidences=CONFIDENCES, grayscale=False):
    """
    Espera hasta que aparezca la imagen y devuelve un box (left, top, width, height).
    Si vence tiempo, devuelve None. Tolera excepciones de PyAutoGUI/PyScreeze.
    Lanza StopExcelException si STOP_EXCEL se activa durante la búsqueda.
    """
    t0 = time.time()
    while time.time() - t0 < timeout:
        if STOP_EXCEL.is_set():
            raise StopExcelException("Detenido por usuario")
        for conf in confidences:
            try:
                box = pyautogui.locateOnScreen(
                    img_path, region=region, confidence=conf, grayscale=grayscale
                )
                if box:
                    return box
            except (NotImplementedError, PYSCR_IMAGE_NOT_FOUND, pyautogui.ImageNotFoundException):
                pass  # seguir intentando
            except Exception:
                pass  # esperar y reintentar
        time.sleep(poll + random.uniform(0, 0.05))
    return None

def click_image(img_path, region=None, timeout=8.0, **kwargs):
    """
    Espera la imagen y hace click al centro. Si no aparece, devuelve False (no lanza excepción).
    """
    box = wait_image(img_path, region=region, timeout=timeout, **kwargs)
    if not box:
        return False
    pyautogui.click(pyautogui.center(box))
    return True

def assert_step(ok: bool, msg: str):
    """
    Corta la macro si ok es False y muestra error bloqueante.
    """
    if not ok:
        try:
            messagebox.showerror("Paso fallido", msg)
        finally:
            raise RuntimeError(msg)

# ---------------- Paso btn4 robusto ----------------
def click_btn4_strict():
    # Intentos rápidos: click y verificar que aparezca btn5 (señal de éxito)
    for attempt in range(3):
        ok = click_image(IMG_BTN4, region=REGION_BTN4, timeout=6.0)
        if ok:
            # verificar que btn5 aparezca (confirmación)
            if wait_image(IMG_BTN5, region=REGION_BTN5, timeout=4.0, confidences=CONFIDENCES):
                return True
            logging.info("btn4 clickado pero btn5 no apareció (intento %d)", attempt + 1)
        time.sleep(0.15)

    # Si los intentos rápidos fallan, probar con búsquedas de baja confianza y clics directos
    for conf in (0.75, 0.70, 0.65, 0.60, 0.55, 0.50):
        try:
            box = pyautogui.locateOnScreen(IMG_BTN4, region=REGION_BTN4, confidence=conf)
        except NotImplementedError:
            box = pyautogui.locateOnScreen(IMG_BTN4, region=REGION_BTN4)
        if box:
            pyautogui.click(pyautogui.center(box))
            if wait_image(IMG_BTN5, region=REGION_BTN5, timeout=4.0, confidences=CONFIDENCES):
                return True
        time.sleep(0.15)

    try:
        import cv2, numpy as np
        shot = pyautogui.screenshot(region=REGION_BTN4)
        scr = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        tpl = cv2.imread(IMG_BTN4, cv2.IMREAD_COLOR)
        if tpl is not None:
            best_rect, best_score, best_scale = None, -1, 1.0
            for scale in (0.90, 0.95, 1.00, 1.05, 1.10, 1.15):
                tpl_s = cv2.resize(tpl, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
                res = cv2.matchTemplate(scr, tpl_s, cv2.TM_CCOEFF_NORMED)
                _, maxVal, _, maxLoc = cv2.minMaxLoc(res)
                if maxVal > best_score:
                    h, w = tpl_s.shape[:2]
                    x0, y0, _, _ = REGION_BTN4
                    rect = (x0 + maxLoc[0], y0 + maxLoc[1], w, h)
                    best_rect, best_score, best_scale = rect, maxVal, scale
            if best_rect and best_score >= 0.50:
                x, y, w, h = best_rect
                # Intento de click robusto en la región encontrada
                if _robust_click_box((x, y, w, h)):
                    # verificar que btn5 aparezca
                    if wait_image(IMG_BTN5, region=REGION_BTN5, timeout=4.0, confidences=CONFIDENCES):
                        logging.info("[btn4] OpenCV score=%0.3f, escala=%0.2f, rect=%s", best_score, best_scale, best_rect)
                        return True
                    else:
                        logging.warning("[btn4] OpenCV encontró rect pero btn5 no apareció tras el click: %s", best_rect)
                else:
                    logging.warning("[btn4] OpenCV encontró rect pero no se pudo clicar correctamente: %s", best_rect)
    except Exception as e:
        print(f"[btn4] OpenCV fallback falló: {e}")

    try:
        ts = int(time.time())
        img = pyautogui.screenshot(region=REGION_BTN4)
        img.save(f"debug_btn4_{ts}.png")
        print(f"[DEBUG] guardado: debug_btn4_{ts}.png")
    except Exception:
        pass

    return False


def _robust_click_box(box, attempts: int = 6, pause: float = 0.12):
    """Intenta clicar dentro del rect (left, top, w, h) probando el centro y offsets.
    Devuelve True si realizó al menos un intento de click (no verifica efectos posteriores).
    """
    try:
        left, top, w, h = box
    except Exception:
        # puede venir como objeto con attributes
        try:
            left, top, w, h = box.left, box.top, box.width, box.height
        except Exception:
            logging.exception("_robust_click_box: formato de box inesperado: %s", box)
            return False

    cx = int(left + w // 2)
    cy = int(top + h // 2)

    # offsets (center, left, right, up, down, corners)
    offs = [(0, 0), (-w//6, 0), (w//6, 0), (0, -h//6), (0, h//6), (-w//6, -h//6), (w//6, h//6), (-w//8, h//8)]

    tried = 0
    for dx, dy in offs:
        if tried >= attempts:
            break
        tx, ty = cx + dx, cy + dy
        try:
            pyautogui.moveTo(tx, ty, duration=0.06)
            pyautogui.click(tx, ty)
            time.sleep(pause + random.uniform(0, 0.06))
            tried += 1
        except Exception:
            logging.exception("_robust_click_box: fallo al clicar en (%s,%s)", tx, ty)
            tried += 1

    return tried > 0


def do_step7_then_btn4(retries: int = 2) -> bool:
    """Ejecuta la secuencia de teclas del Paso 7 y luego intenta clicar btn4.
    - Tras ejecutar Paso 7 espera a que aparezca `IMG_BTN4` antes de llamar a `click_btn4_strict()`.
    - Si no aparece, reintenta la secuencia hasta `retries` veces.
    Devuelve True si `click_btn4_strict()` tuvo éxito.
    """
    for attempt in range(retries + 1):
        logging.info("[Paso7] Ejecutando secuencia de teclas, intento %d", attempt + 1)
        time.sleep(0.4)
        pyautogui.press("enter")
        time.sleep(0.6)
        pyautogui.press("enter", presses=2)
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(0.3)
        pyautogui.press("right")
        time.sleep(0.6)
        pyautogui.press("down", presses=5)
        time.sleep(0.6)
        pyautogui.press("t")
        pyautogui.press("enter", presses=3)
        time.sleep(0.6)

        # Esperar a que aparezca btn4 (o un indicador de que está listo)
        if wait_image(IMG_BTN4, region=REGION_BTN4, timeout=3.0, confidences=CONFIDENCES):
            logging.info("[Paso7] IMG_BTN4 detectado, procediendo a click_btn4_strict()")
            return click_btn4_strict()

        logging.warning("[Paso7] IMG_BTN4 no detectado tras la secuencia (intento %d)", attempt + 1)
        time.sleep(0.5)

    # Si no se detectó IMG_BTN4, intentar click_btn4_strict de todas formas como fallback
    logging.info("[Paso7] Fallback: llamando a click_btn4_strict() sin detectar IMG_BTN4")
    return click_btn4_strict()

# ---------------- Hook opcional (datos de Excel o cédula) ----------------
def on_before_macro(row_dict: dict):
    if not row_dict:
        return
    print("[Datos]", {k: row_dict.get(k) for k in ("cedula", "Consecutivo", "numero_documento", "eca")})

# ---------------- Macro principal (estricta) ----------------
def macro_f3(row_dict: dict | None = None):
    set_status("Iniciando macro…")
    print("▶️ Iniciando macro (estricta)…")

    if row_dict is not None:
        on_before_macro(row_dict)

    # Paso 1: F2 y ACEPTAR_ORDEN
    pyautogui.press("F2")
    time.sleep(0.8)
    ok = click_image(IMG_ACEPTAR_ORDEN, region=REGION_ACEPTAR, timeout=8.0)
    assert_step(ok, "No se encontró ACEPTAR_ORDEN. Verifica región/PNG/zoom.")

    # Paso 2: Entradas
    time.sleep(0.8)
    pyautogui.press("enter")
    pyautogui.press("1")
    pyautogui.press("enter")

    # (Opcional) teclear cédula aquí:
    # if row_dict and row_dict.get("cedula"):
    #     cedula_txt = str(row_dict["cedula"]).strip()
    #     time.sleep(0.3)
    #     pyautogui.typewrite(cedula_txt, interval=0.02)
    #     pyautogui.press("enter")

    # Paso 3: Cerrar_Orden (si aparece)
    box_cerrar = wait_image(IMG_CERRAR_ORDEN, timeout=2.0, confidences=CONFIDENCES)
    if box_cerrar:
        pyautogui.click(pyautogui.center(box_cerrar))

    time.sleep(0.2)
    pyautogui.press("up")
    pyautogui.press("enter", presses=6)
    time.sleep(1.2)

    # Paso 4: btn1
    ok = click_image(IMG_BTN1, region=REGION_BTN1, timeout=8.0)
    assert_step(ok, "No se encontró btn1. No se puede continuar.")

    pyautogui.moveTo(200, 200)
    time.sleep(0.5)
    pyautogui.press("right")
    time.sleep(0.6)

    # Paso 5: btn2 (doble clic)
    box2 = wait_image(IMG_BTN2, region=REGION_BTN2, timeout=8.0, confidences=CONFIDENCES)
    assert_step(box2 is not None, "No se encontró btn2. Macro detenida.")
    pyautogui.click(pyautogui.center(box2))
    time.sleep(0.2)
    pyautogui.click(pyautogui.center(box2))

    time.sleep(0.4)
    pyautogui.press("down")
    time.sleep(0.3)
    pyautogui.press("enter")
    time.sleep(0.5)

    # Click a btn3 (antes del Paso 7)
    ok = click_image(IMG_BTN3, region=REGION_BTN3, timeout=8.0)
    assert_step(ok, "No se encontró btn3. Macro detenida.")

    # Ejecutar Paso 7 y luego Paso 6 de forma robusta (con reintentos y comprobaciones)
    ok = do_step7_then_btn4(retries=2)
    assert_step(ok, "No se encontró btn4. Macro detenida.")
    time.sleep(1.0)

    # Paso 8: btn5 (doble clic)
    box5 = wait_image(IMG_BTN5, region=REGION_BTN5, timeout=8.0, confidences=CONFIDENCES)
    assert_step(box5 is not None, "No se encontró btn5. Macro detenida.")
    pyautogui.doubleClick(pyautogui.center(box5))
    time.sleep(0.6)
    pyautogui.press("enter")
    time.sleep(1.2)

    print("✅ Macro finalizada sin saltar pasos.")
    set_status("Listo ✓")

# ---------------- Utilidades de coloreado en tabla ----------------
def mark_row(idx: int, tag: str):
    """Aplica una etiqueta visual a la fila en la tabla."""
    item = TREE_INDEX.get(idx)
    if not item:
        return
    # limpiamos otras etiquetas y aplicamos la pedida
    tree.item(item, tags=(tag,))

# ---------------- Procesar todas las filas del Excel (igual que cédula) ----------------
def process_all_rows():
    """
    Recorre CURRENT_DF y por cada fila:
    Enter → (pausa) → Right → escribe numero_documento → Enter → (clic IMG_RUN si está) → macro_f3
    """
    global CURRENT_DF, STOP_EXCEL
    if CURRENT_DF is None or CURRENT_DF.empty:
        messagebox.showwarning("Excel", "No hay datos cargados.")
        return

    # reset stop event and begin
    try:
        STOP_EXCEL.clear()
    except Exception:
        pass
    set_status("Procesando filas… (⏹ para detener)")

    df_list = list(CURRENT_DF.iterrows())
    total_filas = len(df_list)

    for fila_num, (idx, row) in enumerate(df_list):
        if STOP_EXCEL.is_set():
            set_status("Procesamiento detenido por usuario")
            break

        doc_txt = str(row.get("numero_documento", "")).strip()
        print(f"\n=== Fila {idx} | numero_documento={doc_txt} ===")

        try:

            # Marcar EN PROCESO (amarillo)
            mark_row(idx, "running")

            # 1) Secuencia previa
            time.sleep(2)
            pyautogui.press("enter")
            time.sleep(0.6)
            pyautogui.press("right")

            # 2) Escribir numero_documento (igual que cédula)
            pyautogui.typewrite(doc_txt, interval=0.02)
            time.sleep(1)
            pyautogui.press("enter")

            # 3) Llenar CENTRO COSTOS según ECA
            eca_val = str(row.get("eca", "")).strip()
            fill_centro_costos(eca_val)
            time.sleep(1.5)  # Pausa importante después de fill_centro_costos

            # 4) Intentar clic en RUN si está
            ok = click_image(IMG_RUN, region=REGION_TERCERO, timeout=10.0, confidences=CONFIDENCES)
            if ok:
                print("[INFO] RUN encontrado y clicado.")
            else:
                print("[INFO] RUN no encontrado, sigo el flujo.")

            # 5) Ejecutar macro principal
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(1)
            macro_f3(row_dict={
                "Consecutivo": row.get("Consecutivo"),
                "numero_documento": row.get("numero_documento"),
                "eca": row.get("eca")
            })

            # Si todo fue bien: marcar COMPLETADO (verde)
            mark_row(idx, "done")

        except StopExcelException:
            print(f"[INFO] Detenido en fila {idx} por usuario.")
            mark_row(idx, "running")  # dejar en amarillo (incompleta)
            set_status("Procesamiento detenido por usuario")
            return
        except Exception as e:
            print(f"💥 Error en fila {idx}: {e}")
            # Marcar ERROR (rojo)
            mark_row(idx, "error")
            continue

        # 5) Post-proceso por fila (solo entre filas, no después de la última)
        if fila_num < total_filas - 1:
            time.sleep(2)
            pyautogui.press("esc"); pyautogui.press("esc")
            time.sleep(1)
            pyautogui.press("enter", presses=3)
            time.sleep(2)  # Espera extra entre filas

    # Post-proceso final después de procesar todas las filas
    time.sleep(2)
    pyautogui.press("esc"); pyautogui.press("esc")
    time.sleep(1)
    pyautogui.press("enter", presses=3)
    set_status("Finalizado (o detenido)")

# ---------------- Ejecutar por cédula (arranque directo) ----------------
def run_cedula_series(cedula: str, repeticiones: int):
    """
    Ejecuta la macro 'repeticiones' veces con la MISMA cédula.
    Enter → (pausa) → Right → cédula → Enter → (RUN si está) → macro
    """
    import traceback
    global STOP_FLAG
    try:
        STOP_FLAG.clear()
    except Exception:
        pass
    set_status(f"Cédula {cedula} x{repeticiones}…")

    cedula_txt = str(cedula).strip()

    for i in range(repeticiones):
        if STOP_FLAG.is_set():
            set_status("Detenido por usuario")
            break

        print(f"\n=== Ejecución {i+1}/{repeticiones} para cédula {cedula_txt} ===")

        try:
            # 1) Secuencia previa
            time.sleep(2)
            pyautogui.press("enter")
            time.sleep(0.6)
            pyautogui.press("right")

            # 2) Escribir cédula
            pyautogui.typewrite(cedula_txt, interval=0.02)
            time.sleep(1)
            pyautogui.press("enter")

            # 3) Intentar clic en RUN si está
            ok = click_image(IMG_RUN, region=REGION_TERCERO, timeout=10.0, confidences=CONFIDENCES)
            if ok:
                print("[INFO] Imagen RUN encontrada y clicada.")
            else:
                print("[INFO] Imagen RUN no encontrada, sigo el flujo.")

            # 4) Macro principal
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(1)
            macro_f3(row_dict=None)

        except Exception as e:
            print(f"💥 Error en ejecución {i+1}: {repr(e)}")
            import traceback as _tb
            print("---- TRACEBACK ----")
            print(_tb.format_exc())
            continue

        # 5) Post-proceso tras cada iteración
        time.sleep(2)
        pyautogui.press("esc"); pyautogui.press("esc")
        time.sleep(1)
        pyautogui.press("enter", presses=3)

    set_status("Listo ✓")

def open_cedula_dialog():
    """Dialogo para ingresar cédula y número de repeticiones. Lanza ejecución directa."""
    dlg = tk.Toplevel(root)
    dlg.title("Ejecutar por cédula")
    dlg.resizable(False, False)
    dlg.grab_set()

    tk.Label(dlg, text="Número de cédula:").grid(row=0, column=0, padx=8, pady=(10,4), sticky="e")
    entry_ced = tk.Entry(dlg, width=24, justify="center")
    entry_ced.grid(row=0, column=1, padx=8, pady=(10,4))
    entry_ced.focus()

    tk.Label(dlg, text="Repeticiones:").grid(row=1, column=0, padx=8, pady=4, sticky="e")
    spn_rep = tk.Spinbox(dlg, from_=1, to=999, width=6, justify="center")
    spn_rep.delete(0, "end"); spn_rep.insert(0, "1")
    spn_rep.grid(row=1, column=1, padx=8, pady=4, sticky="w")

    def on_run():
        ced = entry_ced.get().strip()
        try:
            reps = int(spn_rep.get())
        except ValueError:
            reps = 1
        if not ced:
            messagebox.showwarning("Faltan datos", "Ingresa un número de cédula.")
            return
        dlg.destroy()
        threading.Thread(target=run_cedula_series, args=(ced, reps), daemon=True).start()

    btns = tk.Frame(dlg)
    btns.grid(row=2, column=0, columnspan=2, pady=10)
    tk.Button(btns, text="Cancelar", width=12, command=dlg.destroy).pack(side="left", padx=6)
    tk.Button(btns, text="▶ Ejecutar", width=12, command=on_run).pack(side="left", padx=6)

    # Centrar
    dlg.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - dlg.winfo_width()) // 2
    y = root.winfo_y() + (root.winfo_height() - dlg.winfo_height()) // 2
    dlg.geometry(f"+{x}+{y}")

# ---------------- Hotkeys opcionales ----------------
def on_key_press(event):
    if event.name == 'f3':
        threading.Thread(target=safe_run_macro, daemon=True).start()
    elif event.name == 'f12':
        stop_listening()

def safe_run_macro():
    try:
        set_status("Ejecutando macro…")
        macro_f3(row_dict=None)
    except Exception as e:
        print(f"💥 Macro abortada: {e}")
        set_status("Error")
        try:
            messagebox.showerror("Macro abortada", str(e))
        except Exception:
            pass
            try:
                shot = pyautogui.screenshot()
                if Image and ImageTk:
                    # asegurarse formato RGB
                    try:
                        shot = shot.convert("RGB")
                    except Exception:
                        pass
                    bg_img = ImageTk.PhotoImage(shot)
                    # crear con tag 'bg' para no borrarlo en redraw
                    canvas.create_image(0, 0, image=bg_img, anchor="nw", tags=("bg",))
                    # mantener referencia para evitar GC
                    canvas._bg_img_ref = bg_img
            except Exception:
                logging.exception("No se pudo capturar fondo para editor interactivo")
load_config()
# Ensure CONFIG has a REGIONS key before merging defaults
CONFIG.setdefault("REGIONS", {})
# Merge default RESOLUTIONS into CONFIG['REGIONS'] if not present
for k, v in RESOLUTIONS.items():
    CONFIG["REGIONS"].setdefault(k, v)
setup_logging()
init_dry_run()

# After loading config, update RESOLUTIONS from CONFIG
try:
    RESOLUTIONS.update(CONFIG.get("REGIONS", {}))
except Exception:
    pass

# Apply default resolution (720p)
apply_resolution(CONFIG.get("DEFAULT_RESOLUTION", "720p"))

logging.info("Iniciando Helisa Bot")

root = tk.Tk()
root.title("Helisa Bot v1.0 - Macro + Excel + Cédula")
root.geometry("1000x620")
root.resizable(False, False)

status_var = tk.StringVar(value="Listo")
def set_status(text):
    status_var.set(text)
    root.update_idletasks()

# ---- Botones (2 filas para que se vean todos) ----
top_frame1 = tk.Frame(root)
top_frame1.pack(fill="x", padx=10, pady=(8,4))

top_frame2 = tk.Frame(root)
top_frame2.pack(fill="x", padx=10, pady=(0,8))

btn_run = tk.Button(top_frame1, text="▶ Iniciar macro (1 vez)", width=22,
                    command=lambda: threading.Thread(target=safe_run_macro, daemon=True).start())
btn_run.pack(side="left", padx=6, pady=2)

# Botón de configuración con imagen (polea) — redimensionada a 40x40 si Pillow está disponible
try:
    if Image and ImageTk:
        _pil_img = Image.open(IMG_ICON)
        _pil_img = _pil_img.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
        _icon_img = ImageTk.PhotoImage(_pil_img)
    else:
        _icon_img = tk.PhotoImage(file=IMG_ICON)
        # intentar reducir tamaño con subsample si la imagen es mayor
        try:
            iw = _icon_img.width()
            ih = _icon_img.height()
            sx = max(1, int(round(iw / ICON_SIZE)))
            sy = max(1, int(round(ih / ICON_SIZE)))
            if sx > 1 or sy > 1:
                _icon_img = _icon_img.subsample(sx, sy)
        except Exception:
            pass
except Exception:
    _icon_img = None

# Registro de ventanas únicas: impide abrir la misma ventana más de una vez.
# Clave → instancia Toplevel activa.
_open_windows: dict[str, tk.Toplevel] = {}


def _singleton_guard(key: str) -> bool:
    """Devuelve True (y enfoca la ventana) si ya existe una instancia activa para `key`."""
    win = _open_windows.get(key)
    if win is not None:
        try:
            if win.winfo_exists():
                win.lift()
                win.focus_force()
                return True
        except Exception:
            pass
        # La ventana ya no existe; limpiar referencia
        _open_windows.pop(key, None)
    return False


def _register_window(key: str, win: tk.Toplevel):
    """Registra `win` como instancia activa para `key` y limpia al destruirse."""
    _open_windows[key] = win
    win.bind("<Destroy>", lambda _e: _open_windows.pop(key, None))


def open_config_dialog():
    if _singleton_guard("config"):
        return
    dlg = tk.Toplevel(root)
    _register_window("config", dlg)
    dlg.title("Configuración")
    dlg.resizable(False, False)
    # NO grab_set() — permite interactuar con el editor interactivo de regiones

    # Imagen de la polea
    if _icon_img:
        tk.Label(dlg, image=_icon_img).grid(row=0, column=0, rowspan=3, padx=8, pady=8)

    # Resolución
    tk.Label(dlg, text="Resolución por defecto:").grid(row=0, column=1, sticky="w", padx=6, pady=(8,2))
    sel_var = tk.StringVar(value=CONFIG.get("DEFAULT_RESOLUTION", "720p"))
    ttk.OptionMenu(dlg, sel_var, sel_var.get(), *list(RESOLUTIONS.keys())).grid(row=0, column=2, padx=6, pady=(8,2))

    # DRY_RUN
    dry_var = tk.BooleanVar(value=CONFIG.get("DRY_RUN", False))
    tk.Checkbutton(dlg, text="Dry run (no ejecutar clicks)", variable=dry_var).grid(row=1, column=1, columnspan=2, sticky="w", padx=6)

    # Log file
    tk.Label(dlg, text="Archivo de log:").grid(row=2, column=1, sticky="w", padx=6, pady=(2,8))
    ent_log = tk.Entry(dlg, width=28)
    ent_log.insert(0, CONFIG.get("LOG_FILE", "helisa.log"))
    ent_log.grid(row=2, column=2, padx=6, pady=(2,8))

    def on_save():
        CONFIG["DEFAULT_RESOLUTION"] = sel_var.get()
        CONFIG["DRY_RUN"] = bool(dry_var.get())
        CONFIG["LOG_FILE"] = ent_log.get().strip() or "helisa.log"
        # persist
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(CONFIG, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar config: {e}")
            return

        # aplicar cambios en runtime
        apply_resolution(CONFIG.get("DEFAULT_RESOLUTION", "720p"))
        setup_logging()
        init_dry_run()

        messagebox.showinfo("Guardado", "Configuración guardada. Algunos cambios se aplicaron en caliente.")
        dlg.destroy()

    tk.Button(dlg, text="Editar regiones...", command=lambda: edit_regions_dialog(sel_var.get())).grid(row=3, column=1, padx=6, pady=8)
    tk.Button(dlg, text="Mostrar regiones", width=14, command=lambda: show_regions_overlay(sel_var.get())).grid(row=3, column=2, padx=6, pady=8)
    tk.Button(dlg, text="Guardar", width=12, command=on_save).grid(row=3, column=3, padx=6, pady=8)

if _icon_img:
    lbl_config = tk.Label(top_frame1, image=_icon_img, bd=0, cursor="hand2")
    lbl_config.bind("<Button-1>", lambda e: open_config_dialog())
    # contenedor fijo para que la imagen no se estire
    icon_box = tk.Frame(top_frame1, width=ICON_SIZE, height=ICON_SIZE)
    icon_box.pack_propagate(False)
    icon_box.pack(side="right", padx=6, pady=2)
    lbl_config = tk.Label(icon_box, image=_icon_img, bd=0, cursor="hand2")
    lbl_config.bind("<Button-1>", lambda e: open_config_dialog())
    lbl_config.pack(expand=True)
    # (label 'Ajustes' removed - icon only)
    # keep reference to avoid GC
    root._config_icon_ref = _icon_img
else:
    tk.Button(top_frame1, text="Config", command=open_config_dialog, bd=0).pack(side="right", padx=6, pady=2)

def start_listening():
    global LISTENING
    if LISTENING.is_set():
        messagebox.showinfo("Hotkeys", "Ya está escuchando F3/F12.")
        return
    try:
        keyboard.on_press(on_key_press)
        LISTENING.set()
        set_status("Escuchando F3/F12…")
        messagebox.showinfo("Hotkeys", "F3: Iniciar macro • F12: Detener escucha")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar escucha: {e}")

def stop_listening():
    global LISTENING, STOP_FLAG
    try:
        keyboard.unhook_all()
        LISTENING.clear()
        STOP_FLAG.set()
        set_status("Escucha detenida")
        try:
            messagebox.showinfo("Detenido", "Se detuvo la escucha de hotkeys.")
        except Exception:
            pass
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo detener: {e}")

btn_listen = tk.Button(top_frame1, text="🎧 Escuchar F3 / F12", width=22, command=start_listening)
btn_listen.pack(side="left", padx=6, pady=2)

btn_stop = tk.Button(top_frame1, text="⏹ Detener escucha", width=22, command=stop_listening)
btn_stop.pack(side="left", padx=6, pady=2)

# ---- Excel: cargar / procesar / detener / cédula ----
def normalize_columns(cols):
    return [str(c).strip().lower() for c in cols]

def load_excel():
    global CURRENT_DF, TREE_INDEX
    path = filedialog.askopenfilename(
        title="Seleccionar Excel",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not path:
        return
    try:
        df = pd.read_excel(path)
    except Exception as e:
        messagebox.showerror("Excel", f"No se pudo abrir el Excel:\n{e}")
        return

    orig_cols = list(df.columns)
    ncols = normalize_columns(orig_cols)

    need = {
        "Consecutivo": ["consecutivo", "consec", "id", "consecutivo_orden"],
        "numero_documento": ["numero_documento", "num_documento", "documento", "doc", "cedula", "cédula", "dni"],
        "nombre": ["nombre", "name", "razonsocial", "razon_social", "cliente"],
        "eca": ["eca", "codigo_eca", "valor_eca"]
    }
    colmap = {}
    for target, candidates in need.items():
        found = None
        for cand in candidates:
            if cand in ncols:
                idx = ncols.index(cand)
                found = orig_cols[idx]
                break
        if not found:
            messagebox.showerror("Excel", f"Falta la columna requerida: '{target}'")
            return
        colmap[target] = found

    df_sel = df[[colmap["Consecutivo"], colmap["numero_documento"], colmap["nombre"], colmap["eca"]]].copy()
    df_sel.columns = ["Consecutivo", "numero_documento", "nombre", "eca"]

    CURRENT_DF = df_sel
    populate_table(df_sel)
    set_status("Excel cargado ✓")

def populate_table(df: pd.DataFrame):
    """Rellena la tabla y crea los mapeos índice<->item para colorear filas y reanudar."""
    global TREE_INDEX, ITEM_INDEX
    TREE_INDEX.clear()
    ITEM_INDEX.clear()
    for i in tree.get_children():
        tree.delete(i)
    for idx, row in df.iterrows():
        item = tree.insert("", "end", values=(row["Consecutivo"], row["numero_documento"], row["nombre"], row["eca"]))
        TREE_INDEX[idx] = item
        ITEM_INDEX[item] = idx

def process_rows_clicked():
    if CURRENT_DF is None or CURRENT_DF.empty:
        messagebox.showwarning("Excel", "Carga primero un Excel válido.")
        return
    threading.Thread(target=process_all_rows, daemon=True).start()


def process_rows_from(start_idx):
    """Como process_all_rows pero arranca desde la fila con índice `start_idx`."""
    global CURRENT_DF, STOP_EXCEL
    if CURRENT_DF is None or CURRENT_DF.empty:
        messagebox.showwarning("Excel", "No hay datos cargados.")
        return

    try:
        STOP_EXCEL.clear()
    except Exception:
        pass
    set_status(f"Reanudando desde fila {start_idx}… (⏹ para detener)")

    # Filtrar solo las filas desde start_idx en adelante
    df_from = CURRENT_DF.loc[start_idx:]
    df_list = list(df_from.iterrows())
    total_filas_process = len(df_list)

    for fila_num, (idx, row) in enumerate(df_list):
        if STOP_EXCEL.is_set():
            set_status("Procesamiento detenido por usuario")
            break

        doc_txt = str(row.get("numero_documento", "")).strip()
        print(f"\n=== Fila {idx} | numero_documento={doc_txt} ===")

        try:
            mark_row(idx, "running")

            time.sleep(2)
            pyautogui.press("enter")
            time.sleep(0.6)
            pyautogui.press("right")

            pyautogui.typewrite(doc_txt, interval=0.02)
            time.sleep(1)
            pyautogui.press("enter")
            x, y = pyautogui.center(REGION_TERCERO)
            pyautogui.click(x, y)  # clic extra para asegurar foco


            # Llenar CENTRO COSTOS según ECA
            eca_val = str(row.get("eca", "")).strip()
            fill_centro_costos(eca_val)
            time.sleep(1.5)  # Pausa importante después de fill_centro_costos

            ok = click_image(IMG_RUN, region=REGION_TERCERO, timeout=10.0, confidences=CONFIDENCES)
            if ok:
                print("[INFO] RUN encontrado y clicado.")
            else:
                print("[INFO] RUN no encontrado, sigo el flujo.")

            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(1)
            macro_f3(row_dict={
                "Consecutivo": row.get("Consecutivo"),
                "numero_documento": row.get("numero_documento"),
                "eca": row.get("eca")
            })

            mark_row(idx, "done")

        except StopExcelException:
            print(f"[INFO] Detenido en fila {idx} por usuario.")
            mark_row(idx, "running")  # dejar en amarillo (incompleta)
            set_status("Procesamiento detenido por usuario")
            return
        except Exception as e:
            print(f"💥 Error en fila {idx}: {e}")
            mark_row(idx, "error")
            continue

        # Post-procesamiento: ESC solo entre filas, no después de la última
        if fila_num < total_filas_process - 1:
            time.sleep(2)
            pyautogui.press("esc"); pyautogui.press("esc")
            time.sleep(1)
            pyautogui.press("enter", presses=3)
            time.sleep(2)  # Espera extra entre filas

    # Post-procesamiento final después de procesar todas las filas
    time.sleep(2)
    pyautogui.press("esc"); pyautogui.press("esc")
    time.sleep(1)
    pyautogui.press("enter", presses=3)
    set_status("Finalizado (o detenido)")


def process_selected_rows(selected_indices: list):
    """Procesa solo las filas con índices especificados en selected_indices."""
    global CURRENT_DF, STOP_EXCEL
    if CURRENT_DF is None or CURRENT_DF.empty:
        messagebox.showwarning("Excel", "No hay datos cargados.")
        return

    if not selected_indices:
        messagebox.showwarning("Excel", "No hay filas seleccionadas.")
        return

    try:
        STOP_EXCEL.clear()
    except Exception:
        pass
    
    set_status(f"Procesando {len(selected_indices)} fila(s) seleccionada(s)… (⏹ para detener)")

    for idx in selected_indices:
        if STOP_EXCEL.is_set():
            set_status("Procesamiento detenido por usuario")
            break

        try:
            row = CURRENT_DF.loc[idx]
        except KeyError:
            print(f"⚠️ Fila {idx} no encontrada en el DataFrame.")
            continue

        doc_txt = str(row.get("numero_documento", "")).strip()
        print(f"\n=== Fila {idx} | numero_documento={doc_txt} ===")

        try:
            mark_row(idx, "running")

            time.sleep(2)
            pyautogui.press("enter")
            time.sleep(0.6)
            pyautogui.press("right")

            pyautogui.typewrite(doc_txt, interval=0.02)
            time.sleep(1)
            pyautogui.press("enter")
            pyautogui.click()  # clic extra para asegurar foco

            # Llenar CENTRO COSTOS según ECA
            eca_val = str(row.get("eca", "")).strip()
            fill_centro_costos(eca_val)

            ok = click_image(IMG_RUN, region=REGION_TERCERO, timeout=10.0, confidences=CONFIDENCES)
            if ok:
                print("[INFO] RUN encontrado y clicado.")
            else:
                print("[INFO] RUN no encontrado, sigo el flujo.")

            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(1)
            macro_f3(row_dict={
                "Consecutivo": row.get("Consecutivo"),
                "numero_documento": row.get("numero_documento"),
                "eca": row.get("eca")
            })

            mark_row(idx, "done")

        except StopExcelException:
            print(f"[INFO] Detenido en fila {idx} por usuario.")
            mark_row(idx, "running")
            set_status("Procesamiento detenido por usuario")
            return
        except Exception as e:
            print(f"💥 Error en fila {idx}: {e}")
            mark_row(idx, "error")
            continue

        time.sleep(2)
        pyautogui.press("esc"); pyautogui.press("esc")
        time.sleep(1)
        pyautogui.press("enter", presses=3)

    set_status("Finalizado (o detenido)")


def process_from_selected_clicked():
    """Toma la fila seleccionada en el Treeview y reanuda el procesamiento desde ahí."""
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Reanudar", "Selecciona una fila en la tabla primero.")
        return
    item = sel[0]
    idx = ITEM_INDEX.get(item)
    if idx is None:
        messagebox.showwarning("Reanudar", "No pude determinar el índice de la selección.")
        return
    threading.Thread(target=process_rows_from, args=(idx,), daemon=True).start()

def process_selected_rows_clicked():
    """Procesa desde la fila seleccionada en adelante."""
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Procesar desde seleccionada", "Selecciona una fila en la tabla.")
        return
    
    item = sel[0]
    idx = ITEM_INDEX.get(item)
    if idx is None:
        messagebox.showwarning("Procesar desde seleccionada", "No pude determinar el índice de la selección.")
        return
    
    threading.Thread(target=process_rows_from, args=(idx,), daemon=True).start()


# Diccionario global para almacenar búsquedas seleccionadas
SEARCH_SELECTION = {}


def open_search_dialog():
    """Abre un diálogo para buscar documentos por número, nombre o cédula y seleccionar con checkboxes."""
    if CURRENT_DF is None or CURRENT_DF.empty:
        messagebox.showwarning("Error", "Carga un Excel primero.")
        return
    
    _key = "search_dialog"
    if _singleton_guard(_key):
        return
    
    dlg = tk.Toplevel(root)
    _register_window(_key, dlg)
    dlg.title("Buscar y seleccionar documentos")
    dlg.geometry("700x500")
    dlg.resizable(True, True)
    
    # ---- Frame de búsqueda ----
    search_frame = tk.Frame(dlg)
    search_frame.pack(fill="x", padx=10, pady=10)
    
    # Selector de tipo de búsqueda
    tk.Label(search_frame, text="Buscar por:").pack(side="left", padx=5)
    search_type_var = tk.StringVar(value="numero_documento")
    
    # Mapeo de nombres mostrados a nombres de columnas
    search_field_map = {
        "numero_documento": "numero_documento",
        "nombre": "nombre",
        "consecutivo": "Consecutivo"
    }
    
    ttk.Combobox(search_frame, textvariable=search_type_var, 
                 values=["numero_documento", "nombre", "consecutivo"], 
                 state="readonly", width=18).pack(side="left", padx=5)
    
    tk.Label(search_frame, text="Valor:").pack(side="left", padx=5)
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=5, fill="x", expand=True)
    
    # ---- Frame de resultados con scrollbar ----
    results_frame = tk.Frame(dlg)
    results_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    canvas = tk.Canvas(results_frame, bg="white")
    scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Variables para los checkboxes
    checkbox_vars = {}
    checkbox_indices = {}
    
    def update_results(*args):
        # Limpiar resultados anteriores
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        checkbox_vars.clear()
        checkbox_indices.clear()
        
        search_text = str(search_var.get()).strip().lower()
        search_type = search_type_var.get()
        # Mapear el nombre mostrado al nombre de columna real
        search_field = search_field_map.get(search_type, search_type)
        
        if not search_text:
            # Mostrar todos si está vacío
            visible_rows = list(CURRENT_DF.iterrows())
        else:
            # Filtrar por el campo seleccionado (convertir a string para comparar)
            visible_rows = []
            for idx, row in CURRENT_DF.iterrows():
                field_value = str(row.get(search_field, "")).strip().lower()
                if search_text in field_value:
                    visible_rows.append((idx, row))
        
        # Crear checkboxes
        for idx, row in visible_rows:
            frame = tk.Frame(scrollable_frame, bg="white")
            frame.pack(fill="x", pady=4, padx=5)
            
            var = tk.BooleanVar(value=idx in SEARCH_SELECTION)
            checkbox = tk.Checkbutton(frame, text="", variable=var, bg="white")
            checkbox.pack(side="left", padx=5)
            
            doc = str(row.get("numero_documento", "")).strip()
            nombre = str(row.get("nombre", "")).strip()
            consec = str(row.get("Consecutivo", "")).strip()
            label_text = f"[{consec}] {doc} - {nombre}"
            
            label = tk.Label(frame, text=label_text, justify="left", bg="white", font=("Segoe UI", 9))
            label.pack(side="left", fill="x", expand=True)
            
            checkbox_vars[idx] = var
            checkbox_indices[idx] = row
    
    search_var.trace("w", update_results)
    search_type_var.trace("w", update_results)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # ---- Frame de botones ----
    btn_frame = tk.Frame(dlg)
    btn_frame.pack(fill="x", padx=10, pady=10)
    
    # Label con contador
    counter_label = tk.Label(btn_frame, text=f"Total seleccionados: 0", font=("Segoe UI", 10, "bold"), fg="#155724")
    counter_label.pack(side="left", padx=5)
    
    def update_counter():
        counter_label.config(text=f"Total seleccionados: {len(SEARCH_SELECTION)}")
    
    def on_select_all():
        for var in checkbox_vars.values():
            var.set(True)
    
    def on_deselect_all():
        for var in checkbox_vars.values():
            var.set(False)
    
    def on_confirm():
        selected = {}
        for idx, var in checkbox_vars.items():
            if var.get():
                selected[idx] = checkbox_indices[idx]
        
        # AGREGAR a la selección existente (acumulativa)
        SEARCH_SELECTION.update(selected)
        
        count = len(SEARCH_SELECTION)
        update_counter()
        messagebox.showinfo("Selección", f"Total de documento(s) seleccionado(s): {count}\n\nPuedes seguir buscando y seleccionando más.")
        # NO cerrar la ventana - permitir que continúe buscando y seleccionando
    
    def on_clear_selection():
        """Limpia todas las selecciones previas."""
        if messagebox.askyesno("Confirmar", "¿Borrar toda la selección?"):
            SEARCH_SELECTION.clear()
            # Actualizar los checkboxes
            for var in checkbox_vars.values():
                var.set(False)
            update_counter()
            messagebox.showinfo("Limpiar", "Selección borrada. Puedes empezar de nuevo.")
    
    def on_finish():
        """Cierra la ventana y termina la selección."""
        count = len(SEARCH_SELECTION)
        if count == 0:
            messagebox.showwarning("Advertencia", "No hay documentos seleccionados.")
            return
        messagebox.showinfo("Completado", f"Se guardaron {count} documento(s) para procesar.")
        dlg.destroy()
    
    tk.Button(btn_frame, text="Seleccionar todo", command=on_select_all, width=14).pack(side="left", padx=3)
    tk.Button(btn_frame, text="Deseleccionar todo", command=on_deselect_all, width=16).pack(side="left", padx=3)
    tk.Button(btn_frame, text="Agregar selección", command=on_confirm, width=16, bg="#155724", fg="white").pack(side="left", padx=3)
    tk.Button(btn_frame, text="Limpiar todo", command=on_clear_selection, width=12, bg="#721c24", fg="white").pack(side="left", padx=3)
    tk.Button(btn_frame, text="Finalizar", command=on_finish, width=10, bg="#1e3a8a", fg="white").pack(side="right", padx=3)
    tk.Button(btn_frame, text="Cancelar", command=dlg.destroy, width=10).pack(side="right", padx=3)
    
    # Inicializar resultados
    update_results()


def process_search_selection_clicked():
    """Procesa los documentos seleccionados en la búsqueda."""
    if not SEARCH_SELECTION:
        messagebox.showwarning("Error", "No hay documentos seleccionados. Usa la opción 'Buscar y seleccionar'.")
        return
    
    selected_indices = list(SEARCH_SELECTION.keys())
    threading.Thread(target=process_selected_rows, args=(selected_indices,), daemon=True).start()

def stop_excel_clicked():
    global STOP_EXCEL
    try:
        STOP_EXCEL.set()
    except Exception:
        pass
    set_status("Solicitado detener Excel…")

btn_load = tk.Button(top_frame2, text="📂 Cargar Excel", width=20, command=load_excel)
btn_load.pack(side="left", padx=6, pady=2)

btn_search = tk.Button(top_frame2, text="🔍 Buscar y seleccionar", width=22, command=open_search_dialog)
btn_search.pack(side="left", padx=6, pady=2)

btn_process_search = tk.Button(top_frame2, text="▶ Procesar búsqueda", width=20, command=process_search_selection_clicked)
btn_process_search.pack(side="left", padx=6, pady=2)

btn_process = tk.Button(top_frame2, text="▶ Procesar filas del Excel", width=22, command=process_rows_clicked)
btn_process.pack(side="left", padx=6, pady=2)

btn_selected = tk.Button(top_frame2, text="▶ Procesar desde seleccionada", width=22, command=process_selected_rows_clicked)
btn_selected.pack(side="left", padx=6, pady=2)

btn_stop_excel = tk.Button(top_frame2, text="⏹ Detener Excel", width=18, command=stop_excel_clicked)
btn_stop_excel.pack(side="left", padx=6, pady=2)

btn_resume = tk.Button(top_frame2, text="⏭ Reanudar desde selección", width=24, command=process_from_selected_clicked)
btn_resume.pack(side="left", padx=6, pady=2)

btn_ced = tk.Button(top_frame2, text="🪪 Ejecutar por cédula", width=20, command=lambda: open_cedula_dialog())
btn_ced.pack(side="left", padx=6, pady=2)

# ---- Selección de resolución y edición de regiones ----
resolution_var = tk.StringVar(value=CONFIG.get("DEFAULT_RESOLUTION", "720p"))
res_options = list(RESOLUTIONS.keys())

def on_resolution_change(*args):
    sel = resolution_var.get()
    apply_resolution(sel)


def edit_regions_dialog(sel=None):
    # sel can be passed (from config dialog) or default to main resolution_var
    if sel is None:
        sel = resolution_var.get()
    _key = f"edit_regions_{sel}"
    if _singleton_guard(_key):
        return
    dlg = tk.Toplevel(root)
    _register_window(_key, dlg)
    dlg.title(f"Editar regiones - {sel}")
    dlg.resizable(False, False)
    # NO grab_set() — permite que el editor interactivo reciba eventos del mouse

    entries = {}
    keys = ["REGION_ACEPTAR", "REGION_BTN1", "REGION_BTN2", "REGION_BTN3", "REGION_BTN4", "REGION_BTN5", "REGION_TERCERO"]
    current = RESOLUTIONS.get(sel, {})

    for i, key in enumerate(keys):
        tk.Label(dlg, text=key+":").grid(row=i, column=0, padx=6, pady=4, sticky="e")
        val = current.get(key)
        if val:
            s = f"{val[0]},{val[1]},{val[2]},{val[3]}"
        else:
            s = ""
        ent = tk.Entry(dlg, width=28)
        ent.insert(0, s)
        ent.grid(row=i, column=1, padx=6, pady=4)
        btn_edit = tk.Button(dlg, text="Editar con mouse", width=14,
                             command=lambda k=key, e=ent: edit_region_interactive(
                                 sel, k,
                                 on_saved=lambda l, t, w, h: (e.delete(0, "end"), e.insert(0, f"{l},{t},{w},{h}")),
                                 parent_win=dlg
                             ))
        btn_edit.grid(row=i, column=2, padx=6, pady=4)
        entries[key] = ent

    def on_save_regions():
        for key, ent in entries.items():
            txt = ent.get().strip()
            if not txt:
                # remove if empty
                RESOLUTIONS.setdefault(sel, {}).pop(key, None)
                continue
            try:
                parts = [int(x.strip()) for x in txt.split(",")]
                if len(parts) != 4:
                    raise ValueError("Debe tener 4 valores")
                RESOLUTIONS.setdefault(sel, {})[key] = tuple(parts)
            except Exception as e:
                messagebox.showerror("Error", f"Valor inválido para {key}: {e}")
                return
        # persistir en config
        CONFIG.setdefault("REGIONS", {})[sel] = RESOLUTIONS.get(sel, {})
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(CONFIG, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Guardado", f"Regiones guardadas para {sel} en config.json")
            apply_resolution(sel)
            dlg.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    btns = tk.Frame(dlg)
    btns.grid(row=len(keys), column=0, columnspan=2, pady=8)
    tk.Button(btns, text="Cancelar", width=12, command=dlg.destroy).pack(side="left", padx=6)
    tk.Button(btns, text="Guardar", width=12, command=on_save_regions).pack(side="left", padx=6)


def show_regions_overlay(sel: str | None = None):
    """Muestra un overlay en pantalla con las regiones definidas para la resolución `sel`.
    El overlay es una ventana fullscreen transparente ligera que dibuja rectángulos.
    """
    if sel is None:
        sel = resolution_var.get()
    _ov_key = f"overlay_{sel}"
    if _singleton_guard(_ov_key):
        return

    regs = RESOLUTIONS.get(sel, {})
    if not regs:
        messagebox.showwarning("Regiones", f"No hay regiones definidas para {sel}.")
        return

    # crear ventana overlay (sin bordes, siempre encima)
    ov = tk.Toplevel(root)
    _register_window(_ov_key, ov)
    ov.overrideredirect(True)
    ov.attributes("-topmost", True)
    try:
        ov.attributes("-alpha", 0.25)
    except Exception:
        pass

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    ov.geometry(f"{screen_w}x{screen_h}+0+0")

    TRANSPARENT_COLOR = "#123456"
    canvas = tk.Canvas(ov, width=screen_w, height=screen_h, bg=TRANSPARENT_COLOR, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # dibujar cada región con un outline visible
    colors = ["#00FF00", "#FF0000", "#00FFFF", "#FFFF00", "#FF00FF", "#FFA500"]
    i = 0
    for key, val in regs.items():
        try:
            left, top, w, h = tuple(val)
            color = colors[i % len(colors)]
            canvas.create_rectangle(left, top, left + w, top + h, outline=color, width=3)
            canvas.create_text(left + 6, top + 10, text=key, anchor="nw", fill=color, font=("Segoe UI", 10, "bold"))
            i += 1
        except Exception:
            logging.exception("Mostrar región: formato inválido para %s: %s", key, val)

    # cierre del overlay — usamos hook global de keyboard + botón flotante
    def close_overlay(_e=None):
        # unhook del hotkey global
        try:
            keyboard.remove_hotkey(_esc_hook[0])
        except Exception:
            pass
        # destruir botón flotante
        try:
            close_btn_win.destroy()
        except Exception:
            pass
        # destruir overlay
        try:
            ov.destroy()
        except Exception:
            pass
        # limpiar binding de tkinter también
        try:
            root.bind_all("<Escape>", lambda e: None)
        except Exception:
            pass

    # Hacemos el color de fondo completamente transparente en Windows (para que solo se vean los outlines)
    try:
        ov.attributes("-transparentcolor", TRANSPARENT_COLOR)
    except Exception:
        pass

    # necesitamos asegurarnos que la ventana esté mapeada antes de cambiar estilos nativos
    try:
        ov.update_idletasks()
        ov.update()
    except Exception:
        pass

    # En Windows intentamos hacer la ventana click-through + no-activar (permitir Alt-Tab y clicks al fondo)
    if sys.platform == "win32":
        try:
            hwnd = ov.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_NOACTIVATE = 0x08000000

            # Preferir funciones Ptr para compatibilidad x64/x86
            try:
                GetWindowLongPtr = ctypes.windll.user32.GetWindowLongPtrW
                SetWindowLongPtr = ctypes.windll.user32.SetWindowLongPtrW
            except AttributeError:
                GetWindowLongPtr = ctypes.windll.user32.GetWindowLongW
                SetWindowLongPtr = ctypes.windll.user32.SetWindowLongW

            exStyle = GetWindowLongPtr(hwnd, GWL_EXSTYLE)
            SetWindowLongPtr(hwnd, GWL_EXSTYLE, exStyle | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE)

            # Aplicar atributos de layered (alpha)
            LWA_ALPHA = 0x02
            try:
                ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(255 * 0.25), LWA_ALPHA)
            except Exception:
                pass

            # Forzar recálculo del estilo y redibujado
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOZORDER = 0x0004
            SWP_FRAMECHANGED = 0x0020
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)

            logging.info("Overlay: click-through + no-activate activado (Windows)")
        except Exception:
            logging.exception("No se pudo activar click-through para overlay")
    else:
        logging.info("Overlay click-through sólo soportado en Windows; en otros SO la ventana será interactiva")

    # Atajo global Esc para cerrar (funciona aunque Tkinter pierda el foco)
    _esc_hook = [None]
    try:
        _esc_hook[0] = keyboard.add_hotkey("esc", lambda: root.after(0, close_overlay))
    except Exception:
        logging.exception("No se pudo registrar hotkey global Esc para overlay")

    # Tkinter bind_all como respaldo (cuando root sí tiene foco)
    root.bind_all("<Escape>", lambda e: close_overlay())

    # Botón flotante "× Cerrar" en ventana separada (NO click-through) en esquina inferior derecha
    close_btn_win = tk.Toplevel(root)
    close_btn_win.overrideredirect(True)
    close_btn_win.attributes("-topmost", True)
    btn_w, btn_h = 130, 34
    close_btn_win.geometry(f"{btn_w}x{btn_h}+{screen_w - btn_w - 20}+{screen_h - btn_h - 60}")
    tk.Button(
        close_btn_win,
        text="× Cerrar  [Esc]",
        command=close_overlay,
        bg="#c0392b", fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat", bd=0, cursor="hand2",
    ).pack(fill="both", expand=True)

    # NOTA: no creamos controles en la propia overlay para no interceptar clicks.


def edit_region_interactive(sel: str, key: str, on_saved=None, parent_win=None):
    """Editor interactivo para una única región: fondo completamente transparente y click-through.
    Solo los bordes y controles son opacos y reciben eventos de mouse.
    on_saved(l, t, w, h): callback opcional llamado tras guardar.
    parent_win: ventana padre para messagebox (default: root).
    """
    if sel is None:
        sel = resolution_var.get()
    _ikey = f"interactive_{sel}_{key}"
    if _singleton_guard(_ikey):
        return
    _parent = parent_win if parent_win else root

    regs = RESOLUTIONS.setdefault(sel, {})
    cur = regs.get(key)
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    if not cur:
        cur = (int(screen_w * 0.25), int(screen_h * 0.25),
               int(screen_w * 0.5),  int(screen_h * 0.25))
    try:
        left, top, w, h = tuple(cur)
    except Exception:
        left, top, w, h = 100, 100, 400, 200

    # Color clave de transparencia — los píxeles de este color serán invisibles
    # Y dejarán pasar los clicks al fondo. Los demás píxeles (borde/controles)
    # siguen siendo opacos y reciben eventos de mouse.
    TC = "#010203"   # casi negro, imposible de confundir con verde/blanco del dibujo

    # ── Overlay fullscreen sin barra ──
    ov = tk.Toplevel(root)
    _register_window(_ikey, ov)
    ov.overrideredirect(True)
    ov.attributes("-topmost", True)
    ov.geometry(f"{screen_w}x{screen_h}+0+0")
    # IMPORTANTE: aplicar transparentcolor antes de mostrar la ventana
    try:
        ov.attributes("-transparentcolor", TC)
    except Exception:
        pass

    canvas = tk.Canvas(ov, width=screen_w, height=screen_h, bg=TC, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # ── Estado ──
    state = {
        "rect": [left, top, left + w, top + h],
        "mode": None,   # None | "drag" | "resize"
        "handle": None, "start_x": 0, "start_y": 0, "orig_rect": None,
    }
    HS = 18   # tamaño del handle en píxeles (más grande = más fácil de agarrar)
    BW = 5    # grosor del borde del rectángulo

    def draw():
        canvas.delete("ov")
        l, t, r, b = state["rect"]

        # Borde del rectángulo (opaco = recibe eventos en esa zona)
        canvas.create_rectangle(l, t, r, b,
                                 outline="#00FF00", width=BW, fill=TC,
                                 tags=("ov",))

        # Manija central (mover todo el rect)
        cx, cy = (l + r) // 2, (t + b) // 2
        canvas.create_rectangle(cx - HS//2, cy - HS//2, cx + HS//2, cy + HS//2,
                                 fill="#00AAFF", outline="#fff", width=2, tags=("ov", "h_move"))
        canvas.create_text(cx, cy, text="✥", fill="#fff",
                            font=("Segoe UI", HS - 6, "bold"), tags=("ov",))

        # Manijas de esquina (redimensionar)
        for hx, hy in [(l, t), (r, t), (r, b), (l, b)]:
            canvas.create_rectangle(hx - HS//2, hy - HS//2,
                                     hx + HS//2, hy + HS//2,
                                     fill="#FF6600", outline="#fff", width=2, tags=("ov",))

        # Coordenadas en la esquina
        info = f"  {key}   x={l}  y={t}  w={r-l}  h={b-t}  "
        canvas.create_text(l + 4, t - 18, anchor="nw", text=info,
                            fill=TC, font=("Segoe UI", 10, "bold"), tags=("ov",))  # sombra
        canvas.create_text(l + 3, t - 19, anchor="nw", text=info,
                            fill="#FFFF00", font=("Segoe UI", 10, "bold"), tags=("ov",))

    def corner_hit(x, y):
        l, t, r, b = state["rect"]
        for idx, (hx, hy) in enumerate([(l, t), (r, t), (r, b), (l, b)]):
            if hx - HS//2 <= x <= hx + HS//2 and hy - HS//2 <= y <= hy + HS//2:
                return idx
        return None

    def center_hit(x, y):
        l, t, r, b = state["rect"]
        cx, cy = (l + r) // 2, (t + b) // 2
        return (cx - HS//2 <= x <= cx + HS//2 and
                cy - HS//2 <= y <= cy + HS//2)

    def on_press(e):
        state["start_x"] = e.x; state["start_y"] = e.y
        state["orig_rect"] = state["rect"].copy()
        h = corner_hit(e.x, e.y)
        if h is not None:
            state["mode"] = "resize"; state["handle"] = h
        elif center_hit(e.x, e.y):
            state["mode"] = "drag"
        else:
            state["mode"] = None

    def on_motion(e):
        if state["mode"] is None:
            return
        dx = e.x - state["start_x"]; dy = e.y - state["start_y"]
        l, t, r, b = state["orig_rect"][:]
        if state["mode"] == "drag":
            nl, nt, nr, nb = l+dx, t+dy, r+dx, b+dy
        else:
            hidx = state["handle"]
            nl, nt, nr, nb = l, t, r, b
            if hidx == 0: nl, nt = e.x, e.y
            elif hidx == 1: nr, nt = e.x, e.y
            elif hidx == 2: nr, nb = e.x, e.y
            elif hidx == 3: nl, nb = e.x, e.y
            if nr - nl < 20:
                if hidx in (1, 2): nr = nl + 20
                else: nl = nr - 20
            if nb - nt < 10:
                if hidx in (2, 3): nb = nt + 10
                else: nt = nb - 10
        state["rect"] = [
            int(max(0, min(nl, screen_w - 1))), int(max(0, min(nt, screen_h - 1))),
            int(max(1, min(nr, screen_w))),      int(max(1, min(nb, screen_h))),
        ]
        draw()

    def on_release(e):
        state["mode"] = None
        state["handle"] = None
        state["orig_rect"] = None

    canvas.bind("<ButtonPress-1>",   on_press)
    canvas.bind("<B1-Motion>",       on_motion)
    canvas.bind("<ButtonRelease-1>", on_release)

    # ── Toolbar flotante (opaca, centrada arriba) ──
    tool = tk.Toplevel(root)
    tool.overrideredirect(True)
    tool.attributes("-topmost", True)
    tool.config(bg="#222222")

    def on_save():
        l, t, r, b = state["rect"]
        RESOLUTIONS.setdefault(sel, {})[key] = (int(l), int(t), int(r - l), int(b - t))
        CONFIG.setdefault("REGIONS", {})[sel] = RESOLUTIONS.get(sel, {})
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(CONFIG, f, indent=2, ensure_ascii=False)
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo guardar: {ex}")
            return
        apply_resolution(sel)
        tool.destroy(); ov.destroy()
        if on_saved:
            try:
                on_saved(int(l), int(t), int(r - l), int(b - t))
            except Exception:
                pass
        messagebox.showinfo("Guardado", f"Región {key} guardada para {sel}.", parent=_parent)

    def on_cancel():
        tool.destroy(); ov.destroy()

    tk.Label(tool, text=f"  {key}  [{sel}]   Mover: ✥ azul   Esquinas: 🟠 naranja",
             bg="#222222", fg="#FFFF00", font=("Segoe UI", 10)).pack(side="left", padx=8, pady=6)
    tk.Button(tool, text="  Guardar  ", bg="#155724", fg="#fff",
              command=on_save).pack(side="left", padx=4, pady=6)
    tk.Button(tool, text="  Cancelar  ", bg="#721c24", fg="#fff",
              command=on_cancel).pack(side="left", padx=4, pady=6)

    tool.update_idletasks()
    tool.geometry(f"+{(screen_w - tool.winfo_width()) // 2}+4")

    ov.bind("<Escape>", lambda e: on_cancel())

    draw()
    ov.lift(); tool.lift()

# ---- Tabla (Treeview) para mostrar DataFrame ----
table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=8)

columns = ("Consecutivo", "numero_documento", "nombre", "eca")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150 if col == "nombre" else (200 if col == "eca" else 140), anchor="center")

# Estilos de filas por estado
style = ttk.Style(root)
# Para que respete los colores de tag en Windows
style.map("Treeview", background=[("selected", "#CCE5FF")])

tree.tag_configure("running", background="#FFF3CD")  # amarillo (en proceso)
tree.tag_configure("done",    background="#D4EDDA", foreground="#155724")  # verde (completado)
tree.tag_configure("error",   background="#F8D7DA", foreground="#721C24")  # rojo (error)

vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=vsb.set)
tree.pack(side="left", fill="both", expand=True)
vsb.pack(side="right", fill="y")

# ---- Estado ----
tk.Label(root, text="Estado:").pack(pady=(6, 0))
lbl_status = tk.Label(root, textvariable=status_var, relief="sunken", anchor="w")
lbl_status.pack(fill="x", padx=10, pady=(0, 10))

# Cerrar ordenado
def on_close():
    stop_listening()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_close)

# Inicia UI
try:
    root.mainloop()
except KeyboardInterrupt:
    stop_listening()
