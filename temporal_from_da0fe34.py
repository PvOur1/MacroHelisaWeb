# -*- coding: utf-8 -*-
"""
Helisa Bot v1.0 - UI + Excel + Macro estricta + Cédula + Reanudar + Colores + Stop cooperativo
- Macro estricta (no se salta pasos).
- 📂 Cargar Excel y mostrar (Consecutivo, numero_documento, eca, nombre).
- ▶ Procesar filas del Excel: Enter→Right→numero_documento→Enter→(RUN si está)→macro.
- 🪪 Ejecutar por cédula (mismo flujo).
- ⏹ Detener Excel (corta el bucle de forma cooperativa e inmediata).
- ▶ Reanudar desde selección (continúa desde la fila seleccionada).
- 🎨 Colores: cambia colores de running/ok/error en la tabla.
- Colores por fila: amarillo (procesando), verde (ok), rojo (error) — configurables.
"""

import time
import random
import threading

import pyautogui
import keyboard
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
from tkinter import ttk
import pandas as pd

# ---------------- Config básica ----------------
pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = True

# Imágenes (ajústalas a tus archivos reales)
IMG_ACEPTAR_ORDEN = "ACEPTAR_ORDEN.png"
IMG_CERRAR_ORDEN  = "Cerrar_Orden.png"
IMG_BTN1          = "btn1.png"
IMG_BTN2          = "btn2.png"
IMG_BTN4          = "btn4.png"
IMG_BTN5          = "btn5.png"
IMG_RUN           = "btn_run.png"     # imagen opcional que se clicará antes de macro

# Regiones (ajústalas a tu UI)
REGION_ACEPTAR = (401, 319, 556, 196)
REGION_BTN1    = (256, 171, 854, 120)
REGION_BTN2    = (247, 240, 862, 114)
REGION_BTN4    = (220, 560, 930, 140)   # ampliada para robustez
REGION_BTN5    = (257, 635, 848, 41)

# Región donde buscar IMG_RUN (elegir cédula)
REGION_TERCERO = (192, 292, 1054, 251)

# Barrido de confidencias
CONFIDENCES = (0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50)

# Estado global
CURRENT_DF = None
STOP_FLAG = False            # detener escucha/loops generales (para cédula / hotkeys)
STOP_EXCEL = False           # detener procesamiento de Excel (cooperativo)
LISTENING = False

# Mapeos índice DF <-> item Treeview (para colorear y reanudar)
TREE_INDEX = {}  # idx -> item
ITEM_INDEX = {}  # item -> idx

# Colores (por defecto) de tags en la tabla
COLOR_RUNNING_BG = "#FFF3CD"  # amarillo
COLOR_RUNNING_FG = "#7A6212"
COLOR_DONE_BG    = "#D4EDDA"  # verde
COLOR_DONE_FG    = "#155724"
COLOR_ERROR_BG   = "#F8D7DA"  # rojo
COLOR_ERROR_FG   = "#721C24"

# ---------------- Manejo seguro de excepciones de imagen ----------------
try:
    import pyscreeze
    PYSCR_IMAGE_NOT_FOUND = pyscreeze.ImageNotFoundException
except Exception:
    class PYSCR_IMAGE_NOT_FOUND(Exception):
        pass

# ---------------- Stop helpers (cooperativos para Excel) ----------------
def should_stop():
    """Se usa para cortar el procesamiento de Excel casi al instante."""
    return STOP_EXCEL

def sleep_check(seconds: float):
    """Dormir en porciones cortas y permitir corte rápido."""
    t_end = time.time() + seconds
    while time.time() < t_end:
        if should_stop():
            raise InterruptedError("Detenido por usuario")
        time.sleep(0.1)

# ---------------- Utilidades de imágenes (robustas y cooperativas) ----------------
def wait_image(img_path, region=None, timeout=8.0, poll=0.25, confidences=CONFIDENCES, grayscale=False):
    """
    Espera hasta que aparezca la imagen y devuelve un box (left, top, width, height).
    Si vence tiempo, devuelve None. Tolera excepciones de PyAutoGUI/PyScreeze.
    Sale inmediatamente si se solicita STOP_EXCEL.
    """
    t0 = time.time()
    while time.time() - t0 < timeout:
        if should_stop():
            return None
        for conf in confidences:
            try:
                box = pyautogui.locateOnScreen(
                    img_path, region=region, confidence=conf, grayscale=grayscale
                )
                if box:
                    return box
            except (NotImplementedError, PYSCR_IMAGE_NOT_FOUND, pyautogui.ImageNotFoundException):
                pass
            except Exception:
                pass
        sleep_check(poll + random.uniform(0, 0.05))
    return None

def click_image(img_path, region=None, timeout=8.0, **kwargs):
    box = wait_image(img_path, region=region, timeout=timeout, **kwargs)
    if not box:
        return False
    pyautogui.click(pyautogui.center(box))
    return True

def assert_step(ok: bool, msg: str):
    if not ok:
        try:
            messagebox.showerror("Paso fallido", msg)
        finally:
            raise RuntimeError(msg)

# ---------------- Paso btn4 robusto ----------------
def click_btn4_strict():
    ok = click_image(IMG_BTN4, region=REGION_BTN4, timeout=10.0)
    if ok:
        return True

    for conf in (0.75, 0.70, 0.65, 0.60, 0.55, 0.50):
        try:
            box = pyautogui.locateOnScreen(IMG_BTN4, region=REGION_BTN4, confidence=conf)
        except NotImplementedError:
            box = pyautogui.locateOnScreen(IMG_BTN4, region=REGION_BTN4)
        if box:
            pyautogui.click(pyautogui.center(box))
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
                pyautogui.click(x + w//2, y + h//2)
                print(f"[btn4] OpenCV score={best_score:.3f}, escala={best_scale:.2f}, rect={best_rect}")
                return True
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

# ---------------- Hook opcional (datos de Excel o cédula) ----------------
def on_before_macro(row_dict: dict):
    if not row_dict:
        return
    print("[Datos]", {k: row_dict.get(k) for k in ("cedula", "Consecutivo", "numero_documento", "eca", "nombre")})

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

    # Paso 6: btn4 (robusto)
    ok = click_btn4_strict()
    assert_step(ok, "No se encontró btn4. Macro detenida.")
    time.sleep(1.0)

    # Paso 7: Secuencia exacta de teclas
    pyautogui.press("enter")
    time.sleep(0.6)
    pyautogui.press("enter", presses=2)
    time.sleep(0.6)
    pyautogui.press("enter")
    time.sleep(0.9)
    pyautogui.press("right")
    time.sleep(0.8)
    pyautogui.press("down", presses=5)
    time.sleep(1)
    pyautogui.press("t")
    time.sleep(0.6)
    pyautogui.press("enter", presses=3)
    time.sleep(1)

    # Paso 8: btn5 (doble clic)
    box5 = wait_image(IMG_BTN5, region=REGION_BTN5, timeout=8.0, confidences=CONFIDENCES)
    assert_step(box5 is not None, "No se encontró btn5. Macro detenida.")
    pyautogui.doubleClick(pyautogui.center(box5))
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(1.2)

    print("✅ Macro finalizada sin saltar pasos.")
    set_status("Listo ✓")

# ---------------- Utilidades de coloreado en tabla ----------------
def apply_tree_colors():
    """Aplica los colores globales a las etiquetas del Treeview."""
    tree.tag_configure("running", background=COLOR_RUNNING_BG, foreground=COLOR_RUNNING_FG)
    tree.tag_configure("done",    background=COLOR_DONE_BG,    foreground=COLOR_DONE_FG)
    tree.tag_configure("error",   background=COLOR_ERROR_BG,   foreground=COLOR_ERROR_FG)

def mark_row(idx: int, tag: str):
    item = TREE_INDEX.get(idx)
    if not item:
        return
    tree.item(item, tags=(tag,))
    # Asegurar visibilidad/selección
    try:
        tree.see(item)
        tree.selection_set(item)
    except Exception:
        pass

# ---------------- Procesar filas helpers (cooperativos) ----------------
def run_one_row(idx, row):
    """Procesa de forma robusta una única fila (con pintado de estado y stop cooperativo)."""
    if should_stop():
        return

    doc_txt = str(row.get("numero_documento", "")).strip()
    nombre  = str(row.get("nombre", "")).strip()
    print(f"\n=== Fila {idx} | numero_documento={doc_txt} | nombre={nombre} ===")

    try:
        # Marcar EN PROCESO (amarillo)
        mark_row(idx, "running")

        # 1) Secuencia previa
        sleep_check(2)
        if should_stop(): return
        pyautogui.press("enter")
        sleep_check(0.6)
        if should_stop(): return
        pyautogui.press("right")

        # 2) Escribir numero_documento
        if should_stop(): return
        pyautogui.typewrite(doc_txt, interval=0.02)
        sleep_check(1)
        if should_stop(): return
        pyautogui.press("enter")

        # 3) Intentar clic en RUN si está
        if should_stop(): return
        ok = click_image(IMG_RUN, region=REGION_TERCERO, timeout=10.0, confidences=CONFIDENCES)
        print("[INFO] RUN encontrado y clicado." if ok else "[INFO] RUN no encontrado, sigo el flujo.")

        # 4) Ejecutar macro principal
        sleep_check(0.5)
        if should_stop(): return
        pyautogui.press("enter")
        sleep_check(1)
        if should_stop(): return
        macro_f3(row_dict={
            "Consecutivo": row.get("Consecutivo"),
            "numero_documento": row.get("numero_documento"),
            "eca": row.get("eca"),
            "nombre": row.get("nombre")
        })

        # Si todo fue bien: marcar COMPLETADO (verde)
        mark_row(idx, "done")

    except InterruptedError:
        set_status("Procesamiento detenido por usuario")
        # No cambiamos color (o podrías dejarlo en 'running')
        return
    except Exception as e:
        print(f"💥 Error en fila {idx}: {e}")
        # Marcar ERROR (rojo)
        mark_row(idx, "error")

    # 5) Post-proceso por fila (también cooperativo)
    try:
        sleep_check(5)
        if should_stop(): return
        pyautogui.press("esc"); pyautogui.press("esc")
        sleep_check(1)
        if should_stop(): return
        pyautogui.press("enter", presses=3)
    except InterruptedError:
        set_status("Procesamiento detenido por usuario")
        return

# ---------------- Procesos principales (Excel) ----------------
def process_all_rows():
    """
    Recorre CURRENT_DF y por cada fila:
    Enter → Right → numero_documento → Enter → (RUN si está) → macro_f3
    """
    global CURRENT_DF, STOP_EXCEL
    if CURRENT_DF is None or CURRENT_DF.empty:
        messagebox.showwarning("Excel", "No hay datos cargados.")
        return

    STOP_EXCEL = False
    set_status("Procesando filas… (⏹ para detener)")

    for idx, row in CURRENT_DF.iterrows():
        if STOP_EXCEL:
            set_status("Procesamiento detenido por usuario")
            break
        run_one_row(idx, row)

    set_status("Finalizado (o detenido)")

def process_rows_from(start_idx: int):
    """Igual a process_all_rows, pero arranca en start_idx (incluido)."""
    global CURRENT_DF, STOP_EXCEL
    if CURRENT_DF is None or CURRENT_DF.empty:
        messagebox.showwarning("Excel", "No hay datos cargados.")
        return
    if start_idx not in CURRENT_DF.index:
        messagebox.showwarning("Selección", "Índice inválido para reanudar.")
        return

    STOP_EXCEL = False
    set_status(f"Reanudando desde fila {start_idx}… (⏹ para detener)")

    started = False
    for idx, row in CURRENT_DF.iterrows():
        if idx < start_idx:
            continue
        if STOP_EXCEL:
            set_status("Procesamiento detenido por usuario")
            break
        run_one_row(idx, row)
        started = True

    if not started:
        messagebox.showinfo("Reanudar", "No hay filas posteriores a la selección.")
    set_status("Finalizado (o detenido)")

# ---------------- Ejecutar por cédula (arranque directo) ----------------
def run_cedula_series(cedula: str, repeticiones: int):
    global STOP_FLAG
    STOP_FLAG = False
    set_status(f"Cédula {cedula} x{repeticiones}…")

    cedula_txt = str(cedula).strip()

    for i in range(repeticiones):
        if STOP_FLAG:
            set_status("Detenido por usuario")
            break

        print(f"\n=== Ejecución {i+1}/{repeticiones} para cédula {cedula_txt} ===")

        try:
            time.sleep(2)
            pyautogui.press("enter")
            time.sleep(0.6)
            pyautogui.press("right")

            pyautogui.typewrite(cedula_txt, interval=0.02)
            time.sleep(1)
            pyautogui.press("enter")

            ok = click_image(IMG_RUN, region=REGION_TERCERO, timeout=10.0, confidences=CONFIDENCES)
            if ok:
                print("[INFO] Imagen RUN encontrada y clicada.")
            else:
                print("[INFO] Imagen RUN no encontrada, sigo el flujo.")

            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(2)
            macro_f3(row_dict=None)

        except Exception as e:
            print(f"💥 Error en ejecución {i+1}: {repr(e)}")
            import traceback as _tb
            print("---- TRACEBACK ----")
            print(_tb.format_exc())
            continue

        time.sleep(4)
        pyautogui.press("esc"); pyautogui.press("esc")
        time.sleep(1)
        pyautogui.press("enter", presses=3)

    set_status("Listo ✓")

def open_cedula_dialog():
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

# ---------------- UI (Tkinter) ----------------
root = tk.Tk()
root.title("Helisa Bot v1.0 - Macro + Excel + Cédula")
root.geometry("1120x680")
root.resizable(False, False)

status_var = tk.StringVar(value="Listo")
def set_status(text):
    status_var.set(text)
    root.update_idletasks()

# ---- Botones (2 filas) ----
top_frame1 = tk.Frame(root)
top_frame1.pack(fill="x", padx=10, pady=(8,4))

top_frame2 = tk.Frame(root)
top_frame2.pack(fill="x", padx=10, pady=(0,8))

btn_run = tk.Button(top_frame1, text="▶ Iniciar macro (1 vez)", width=22,
                    command=lambda: threading.Thread(target=safe_run_macro, daemon=True).start())
btn_run.pack(side="left", padx=6, pady=2)

def start_listening():
    global LISTENING
    if LISTENING:
        messagebox.showinfo("Hotkeys", "Ya está escuchando F3/F12.")
        return
    try:
        keyboard.on_press(on_key_press)
        LISTENING = True
        set_status("Escuchando F3/F12…")
        messagebox.showinfo("Hotkeys", "F3: Iniciar macro • F12: Detener escucha")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar escucha: {e}")

def stop_listening():
    global LISTENING, STOP_FLAG
    try:
        keyboard.unhook_all()
        LISTENING = False
        STOP_FLAG = True
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

# ---- Excel: cargar / procesar / detener / reanudar / cédula / colores ----
def normalize_columns(cols):
    return [str(c).strip().lower() for c in cols]

def load_excel():
    global CURRENT_DF, TREE_INDEX, ITEM_INDEX
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
        "eca": ["eca", "codigo_eca", "valor_eca"],
        "nombre": ["nombre", "name", "razon_social", "razón social", "tercero", "cliente"]
    }
    colmap = {}
    for target, candidates in need.items():
        found = None
        for cand in candidates:
            if cand in ncols:
                idx = ncols.index(cand)
                found = orig_cols[idx]
                break
        if not found and target != "nombre":
            messagebox.showerror("Excel", f"Falta la columna requerida: '{target}'")
            return
        colmap[target] = found  # puede quedar None solo para 'nombre'

    # construir selección (si no hay nombre, creamos columna vacía)
    cols_to_take = [colmap["Consecutivo"], colmap["numero_documento"], colmap["eca"]]
    df_sel = df[cols_to_take].copy()
    df_sel.columns = ["Consecutivo", "numero_documento", "eca"]
    if colmap.get("nombre"):
        df_sel["nombre"] = df[colmap["nombre"]]
    else:
        df_sel["nombre"] = ""

    CURRENT_DF = df_sel
    populate_table(df_sel)
    set_status("Excel cargado ✓")

def populate_table(df: pd.DataFrame):
    """Rellena la tabla y crea los mapeos índice<->item para colorear y reanudar."""
    global TREE_INDEX, ITEM_INDEX
    TREE_INDEX.clear()
    ITEM_INDEX.clear()
    for i in tree.get_children():
        tree.delete(i)
    for idx, row in df.iterrows():
        item = tree.insert("", "end", values=(row["Consecutivo"], row["numero_documento"], row["eca"], row["nombre"]))
        TREE_INDEX[idx] = item
        ITEM_INDEX[item] = idx

def process_rows_clicked():
    if CURRENT_DF is None or CURRENT_DF.empty:
        messagebox.showwarning("Excel", "Carga primero un Excel válido.")
        return
    threading.Thread(target=process_all_rows, daemon=True).start()

def stop_excel_clicked():
    global STOP_EXCEL
    STOP_EXCEL = True
    set_status("Solicitado detener Excel…")

def process_from_selected_clicked():
    """Toma la fila seleccionada en el Treeview y reanuda desde ahí."""
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

def open_color_dialog():
    """Diálogo para editar colores de running/ok/error."""
    def pick_color(title, initial):
        color = colorchooser.askcolor(title=title, color=initial)
        return color[1] if color and color[1] else initial

    def apply_and_close():
        nonlocal_vars = {
            "run_bg": entry_run_bg.get().strip(),
            "run_fg": entry_run_fg.get().strip(),
            "ok_bg": entry_ok_bg.get().strip(),
            "ok_fg": entry_ok_fg.get().strip(),
            "err_bg": entry_err_bg.get().strip(),
            "err_fg": entry_err_fg.get().strip(),
        }
        set_colors(nonlocal_vars)
        dlg.destroy()

    def set_colors(vals):
        global COLOR_RUNNING_BG, COLOR_RUNNING_FG, COLOR_DONE_BG, COLOR_DONE_FG, COLOR_ERROR_BG, COLOR_ERROR_FG
        COLOR_RUNNING_BG = vals["run_bg"] or COLOR_RUNNING_BG
        COLOR_RUNNING_FG = vals["run_fg"] or COLOR_RUNNING_FG
        COLOR_DONE_BG    = vals["ok_bg"]  or COLOR_DONE_BG
        COLOR_DONE_FG    = vals["ok_fg"]  or COLOR_DONE_FG
        COLOR_ERROR_BG   = vals["err_bg"] or COLOR_ERROR_BG
        COLOR_ERROR_FG   = vals["err_fg"] or COLOR_ERROR_FG
        apply_tree_colors()

    dlg = tk.Toplevel(root)
    dlg.title("Colores de estados")
    dlg.resizable(False, False)
    dlg.grab_set()

    # Running
    tk.Label(dlg, text="EN PROCESO (running)").grid(row=0, column=0, columnspan=3, sticky="w", padx=8, pady=(8,2))
    tk.Label(dlg, text="Fondo:").grid(row=1, column=0, sticky="e", padx=8)
    entry_run_bg = tk.Entry(dlg, width=12); entry_run_bg.insert(0, COLOR_RUNNING_BG)
    entry_run_bg.grid(row=1, column=1, padx=4)
    tk.Button(dlg, text="Elegir…", command=lambda: entry_run_bg.delete(0, 'end') or entry_run_bg.insert(0, pick_color("Fondo (running)", COLOR_RUNNING_BG))).grid(row=1, column=2, padx=4)

    tk.Label(dlg, text="Texto:").grid(row=2, column=0, sticky="e", padx=8)
    entry_run_fg = tk.Entry(dlg, width=12); entry_run_fg.insert(0, COLOR_RUNNING_FG)
    entry_run_fg.grid(row=2, column=1, padx=4)
    tk.Button(dlg, text="Elegir…", command=lambda: entry_run_fg.delete(0, 'end') or entry_run_fg.insert(0, pick_color("Texto (running)", COLOR_RUNNING_FG))).grid(row=2, column=2, padx=4)

    # OK
    tk.Label(dlg, text="COMPLETADO (ok)").grid(row=3, column=0, columnspan=3, sticky="w", padx=8, pady=(10,2))
    tk.Label(dlg, text="Fondo:").grid(row=4, column=0, sticky="e", padx=8)
    entry_ok_bg = tk.Entry(dlg, width=12); entry_ok_bg.insert(0, COLOR_DONE_BG)
    entry_ok_bg.grid(row=4, column=1, padx=4)
    tk.Button(dlg, text="Elegir…", command=lambda: entry_ok_bg.delete(0, 'end') or entry_ok_bg.insert(0, pick_color("Fondo (ok)", COLOR_DONE_BG))).grid(row=4, column=2, padx=4)

    tk.Label(dlg, text="Texto:").grid(row=5, column=0, sticky="e", padx=8)
    entry_ok_fg = tk.Entry(dlg, width=12); entry_ok_fg.insert(0, COLOR_DONE_FG)
    entry_ok_fg.grid(row=5, column=1, padx=4)
    tk.Button(dlg, text="Elegir…", command=lambda: entry_ok_fg.delete(0, 'end') or entry_ok_fg.insert(0, pick_color("Texto (ok)", COLOR_DONE_FG))).grid(row=5, column=2, padx=4)

    # ERROR
    tk.Label(dlg, text="ERROR").grid(row=6, column=0, columnspan=3, sticky="w", padx=8, pady=(10,2))
    tk.Label(dlg, text="Fondo:").grid(row=7, column=0, sticky="e", padx=8)
    entry_err_bg = tk.Entry(dlg, width=12); entry_err_bg.insert(0, COLOR_ERROR_BG)
    entry_err_bg.grid(row=7, column=1, padx=4)
    tk.Button(dlg, text="Elegir…", command=lambda: entry_err_bg.delete(0, 'end') or entry_err_bg.insert(0, pick_color("Fondo (error)", COLOR_ERROR_BG))).grid(row=7, column=2, padx=4)

    tk.Label(dlg, text="Texto:").grid(row=8, column=0, sticky="e", padx=8)
    entry_err_fg = tk.Entry(dlg, width=12); entry_err_fg.insert(0, COLOR_ERROR_FG)
    entry_err_fg.grid(row=8, column=1, padx=4)
    tk.Button(dlg, text="Elegir…", command=lambda: entry_err_fg.delete(0, 'end') or entry_err_fg.insert(0, pick_color("Texto (error)", COLOR_ERROR_FG))).grid(row=8, column=2, padx=4)

    tk.Frame(dlg, height=8).grid(row=9, column=0)

    btns = tk.Frame(dlg)
    btns.grid(row=10, column=0, columnspan=3, pady=10)
    tk.Button(btns, text="Cancelar", width=12, command=dlg.destroy).pack(side="left", padx=6)
    tk.Button(btns, text="Aplicar", width=12, command=apply_and_close).pack(side="left", padx=6)

    dlg.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - dlg.winfo_width()) // 2
    y = root.winfo_y() + (root.winfo_height() - dlg.winfo_height()) // 2
    dlg.geometry(f"+{x}+{y}")

btn_load = tk.Button(top_frame2, text="📂 Cargar Excel", width=18, command=load_excel)
btn_load.pack(side="left", padx=6, pady=2)

btn_process = tk.Button(top_frame2, text="▶ Procesar Excel", width=18, command=lambda: threading.Thread(target=process_all_rows, daemon=True).start())
btn_process.pack(side="left", padx=6, pady=2)

btn_stop_excel = tk.Button(top_frame2, text="⏹ Detener Excel", width=16, command=stop_excel_clicked)
btn_stop_excel.pack(side="left", padx=6, pady=2)

btn_resume = tk.Button(top_frame2, text="▶ Reanudar desde selección", width=24, command=process_from_selected_clicked)
btn_resume.pack(side="left", padx=6, pady=2)

btn_colors = tk.Button(top_frame2, text="🎨 Colores", width=14, command=open_color_dialog)
btn_colors.pack(side="left", padx=6, pady=2)

btn_ced = tk.Button(top_frame2, text="🪪 Ejecutar por cédula", width=18, command=lambda: open_cedula_dialog())
btn_ced.pack(side="left", padx=6, pady=2)

# ---- Tabla (Treeview) para mostrar DataFrame ----
table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=8)

columns = ("Consecutivo", "numero_documento", "eca", "nombre")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
for col in columns:
    tree.heading(col, text=col)
    if col == "nombre":
        tree.column(col, width=320, anchor="w")
    else:
        tree.column(col, width=180 if col != "eca" else 120, anchor="center")

# Estilos base y aplicar colores
style = ttk.Style(root)
style.map("Treeview", background=[("selected", "#CCE5FF")])
apply_tree_colors()

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
