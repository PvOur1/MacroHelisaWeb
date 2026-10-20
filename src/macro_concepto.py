import json
import os
from pathlib import Path
import sys
import time

# PyInstaller no puede detectar Tcl/Tk en algunos entornos de Python. Al estar
# congelada, la aplicación lleva sus librerías y las indica antes de importar
# tkinter.
if getattr(sys, "frozen", False):
    bundle_dir = Path(sys._MEIPASS)
    os.environ["TCL_LIBRARY"] = str(bundle_dir / "_tcl_data")
    os.environ["TK_LIBRARY"] = str(bundle_dir / "_tk_data")

from tkinter import Listbox, StringVar, Tk, messagebox
from tkinter import ttk

import pyautogui

from paths import DATA_FILE, ensure_data_file, resource_path

TEXT_TEMPLATE = "CDC {} COMP MATERIAL RECICLADO"
HELISA_IMAGE = resource_path("HTML5.png")

COLORS = {
    "background": "#F2F5FA",
    "surface": "#FFFFFF",
    "primary": "#2563EB",
    "primary_dark": "#1D4ED8",
    "danger": "#DC2626",
    "text": "#172033",
    "muted": "#68738A",
    "border": "#DCE3EE",
}


def cargar_fechas():
    ensure_data_file()
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"No se encontro el archivo {DATA_FILE.name}")

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    fechas = data.get("fechas", [])
    if not fechas:
        raise ValueError("El archivo data.json no tiene fechas para procesar")

    return fechas


def guardar_fechas(fechas):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump({"fechas": fechas}, file, indent=4)


def press_sequence(*keys):
    for key in keys:
        pyautogui.press(key)


def escribir_concepto(texto):
    pyautogui.write(texto)
    pyautogui.press("down")
    pyautogui.write(texto)


def enfocar_ventana_helisa():
    """Localiza en pantalla la imagen de Helisa y hace clic en su centro."""
    if not HELISA_IMAGE.exists():
        raise FileNotFoundError(f"No se encontro la imagen {HELISA_IMAGE.name}.")

    ubicacion = pyautogui.locateOnScreen(str(HELISA_IMAGE))
    if ubicacion is None:
        raise RuntimeError(
            "No se encontro la imagen de Helisa en la pantalla. "
            "Deja visible la pagina de Helisa antes de iniciar."
        )

    pyautogui.click(pyautogui.center(ubicacion))
    time.sleep(0.5)


def procesar_fecha(fecha):
    texto = TEXT_TEMPLATE.format(fecha).upper()
    print(fecha)

    press_sequence("tab", "enter")
    time.sleep(1)
    press_sequence("tab", "tab", "enter")

    escribir_concepto(texto)
    time.sleep(1)
    press_sequence("tab", "tab", "tab", "right", "tab", "enter")

    escribir_concepto(texto)
    press_sequence("tab", "tab", "enter", "down")


def macroconcepto(num_repeticiones):
    fechas = cargar_fechas()
    enfocar_ventana_helisa()

    for _ in range(num_repeticiones):
        for fecha in fechas:
            procesar_fecha(fecha)


def run_macro(entry_repeticiones):
    try:
        num_repeticiones = int(entry_repeticiones.get())
        if num_repeticiones <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Dato invalido", "Ingresa un numero de repeticiones mayor a cero.")
        return

    try:
        macroconcepto(num_repeticiones)
    except Exception as exc:
        messagebox.showerror("Error", str(exc))


def crear_ventana():
    raiz = Tk()
    raiz.title("CargueFacturas · Actualización de conceptos")
    raiz.geometry("780x570")
    raiz.minsize(700, 520)
    raiz.configure(bg=COLORS["background"])

    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    estilo.configure("App.TFrame", background=COLORS["background"])
    estilo.configure("Card.TFrame", background=COLORS["surface"])
    estilo.configure(
        "Title.TLabel", background=COLORS["background"], foreground=COLORS["text"],
        font=("Segoe UI Semibold", 22),
    )
    estilo.configure(
        "Subtitle.TLabel", background=COLORS["background"], foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    estilo.configure(
        "CardTitle.TLabel", background=COLORS["surface"], foreground=COLORS["text"],
        font=("Segoe UI Semibold", 12),
    )
    estilo.configure(
        "CardText.TLabel", background=COLORS["surface"], foreground=COLORS["muted"],
        font=("Segoe UI", 9),
    )
    estilo.configure(
        "Primary.TButton", background=COLORS["primary"], foreground="white",
        borderwidth=0, padding=(20, 11), font=("Segoe UI Semibold", 10),
    )
    estilo.map("Primary.TButton", background=[("active", COLORS["primary_dark"])])
    estilo.configure(
        "Secondary.TButton", background="#E8EEF8", foreground=COLORS["text"],
        borderwidth=0, padding=(13, 8), font=("Segoe UI Semibold", 9),
    )
    estilo.map("Secondary.TButton", background=[("active", "#D8E2F2")])
    estilo.configure(
        "Danger.TButton", background="#FDE8E8", foreground=COLORS["danger"],
        borderwidth=0, padding=(13, 8), font=("Segoe UI Semibold", 9),
    )
    estilo.map("Danger.TButton", background=[("active", "#FBD5D5")])
    estilo.configure("TEntry", padding=8, fieldbackground="#F8FAFD", bordercolor=COLORS["border"])

    principal = ttk.Frame(raiz, style="App.TFrame", padding=(32, 25))
    principal.pack(fill="both", expand=True)
    principal.columnconfigure(0, weight=1)

    ttk.Label(principal, text="Actualizar conceptos", style="Title.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(
        principal,
        text="Automatiza el cambio de conceptos en Helisa Cloud a partir de tus fechas.",
        style="Subtitle.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(3, 20))

    ejecucion = ttk.Frame(principal, style="Card.TFrame", padding=20)
    ejecucion.grid(row=2, column=0, sticky="ew", pady=(0, 16))
    ejecucion.columnconfigure(1, weight=1)
    ttk.Label(ejecucion, text="Ejecución", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
    ttk.Label(
        ejecucion, text="La pestaña correcta se localizará automáticamente por su URL.", style="CardText.TLabel"
    ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 14))
    ttk.Label(ejecucion, text="Número de repeticiones", style="CardText.TLabel").grid(row=2, column=0, sticky="w")
    repeticiones = StringVar(value="1")
    entry_repeticiones = ttk.Entry(ejecucion, textvariable=repeticiones, width=10, justify="center")
    entry_repeticiones.grid(row=2, column=1, sticky="w", padx=(14, 20))
    ttk.Button(
        ejecucion, text="Iniciar macro", style="Primary.TButton",
        command=lambda: run_macro(entry_repeticiones),
    ).grid(row=2, column=2, sticky="e")

    fechas_card = ttk.Frame(principal, style="Card.TFrame", padding=20)
    fechas_card.grid(row=3, column=0, sticky="nsew")
    fechas_card.columnconfigure(0, weight=1)
    fechas_card.columnconfigure(1, weight=1)
    fechas_card.rowconfigure(2, weight=1)
    principal.rowconfigure(3, weight=1)

    ttk.Label(fechas_card, text="Fechas de procesamiento", style="CardTitle.TLabel").grid(
        row=0, column=0, columnspan=2, sticky="w"
    )
    ttk.Label(fechas_card, text="Agrega o elimina las fechas que procesará la macro.", style="CardText.TLabel").grid(
        row=1, column=0, columnspan=2, sticky="w", pady=(2, 14)
    )

    lista_frame = ttk.Frame(fechas_card, style="Card.TFrame")
    lista_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 20))
    lista_frame.columnconfigure(0, weight=1)
    lista_frame.rowconfigure(0, weight=1)
    fechas_listbox = Listbox(
        lista_frame, height=8, activestyle="none", selectmode="extended",
        font=("Segoe UI", 10), bg="#F8FAFD", fg=COLORS["text"],
        selectbackground=COLORS["primary"], selectforeground="white",
        borderwidth=1, relief="solid", highlightthickness=0,
    )
    fechas_listbox.grid(row=0, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=fechas_listbox.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    fechas_listbox.configure(yscrollcommand=scrollbar.set)

    def refrescar_fechas():
        fechas_listbox.delete(0, "end")
        try:
            fechas = cargar_fechas()
        except Exception:
            fechas = []

        for fecha in fechas:
            fechas_listbox.insert("end", fecha)

    def obtener_fechas_listbox():
        return list(fechas_listbox.get(0, "end"))

    def agregar_fecha():
        dia = entry_dia.get().strip()
        mes = entry_mes.get().strip()
        anio = entry_anio.get().strip()

        if not (dia.isdigit() and mes.isdigit() and anio.isdigit()):
            messagebox.showerror("Fecha invalida", "Dia, mes y anio deben ser numeros.")
            return

        dia_num = int(dia)
        mes_num = int(mes)
        if not (1 <= dia_num <= 31 and 1 <= mes_num <= 12 and len(anio) == 4):
            messagebox.showerror("Fecha invalida", "Usa una fecha valida en formato dia/mes/anio.")
            return

        fecha = f"{dia_num:02d}/{mes_num:02d}/{anio}"
        fechas_listbox.insert("end", fecha)
        entry_dia.delete(0, "end")

    def eliminar_fecha():
        seleccion = list(fechas_listbox.curselection())
        if not seleccion:
            messagebox.showinfo("Seleccion requerida", "Selecciona una fecha para eliminar.")
            return

        for index in reversed(seleccion):
            fechas_listbox.delete(index)

    def guardar_configuracion():
        fechas = obtener_fechas_listbox()
        if not fechas:
            messagebox.showerror("Fechas requeridas", "Agrega al menos una fecha antes de guardar.")
            return

        guardar_fechas(fechas)
        messagebox.showinfo("Guardado", "Fechas guardadas correctamente.")

    formulario = ttk.Frame(fechas_card, style="Card.TFrame")
    formulario.grid(row=2, column=1, sticky="new")
    formulario.columnconfigure((0, 1, 2), weight=1)

    entry_dia = ttk.Entry(formulario, width=7, justify="center")
    entry_mes = ttk.Entry(formulario, width=7, justify="center")
    entry_anio = ttk.Entry(formulario, width=9, justify="center")
    for columna, (titulo, entrada) in enumerate(
        (("Día", entry_dia), ("Mes", entry_mes), ("Año", entry_anio))
    ):
        ttk.Label(formulario, text=titulo, style="CardText.TLabel").grid(row=0, column=columna, sticky="w")
        entrada.grid(row=1, column=columna, sticky="ew", padx=(0 if columna == 0 else 6, 0))

    ttk.Button(formulario, text="+ Agregar fecha", style="Secondary.TButton", command=agregar_fecha).grid(
        row=2, column=0, columnspan=3, sticky="ew", pady=(12, 8)
    )
    ttk.Button(formulario, text="Eliminar seleccionada", style="Danger.TButton", command=eliminar_fecha).grid(
        row=3, column=0, columnspan=3, sticky="ew", pady=(0, 8)
    )
    ttk.Button(formulario, text="Guardar cambios", style="Secondary.TButton", command=guardar_configuracion).grid(
        row=4, column=0, columnspan=3, sticky="ew"
    )

    refrescar_fechas()

    return raiz


if __name__ == "__main__":
    crear_ventana().mainloop()
