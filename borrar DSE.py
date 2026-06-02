import tkinter as tk
import threading
import keyboard
import time

ejecutando = False

def ciclo_f4():
    global ejecutando

    while ejecutando:
        keyboard.press_and_release('f4')
        time.sleep(1)

def iniciar():
    global ejecutando

    if not ejecutando:
        ejecutando = True
        threading.Thread(target=ciclo_f4, daemon=True).start()

def detener():
    global ejecutando
    ejecutando = False

# Ventana
ventana = tk.Tk()
ventana.title("Auto F4")
ventana.geometry("300x150")

btn_iniciar = tk.Button(
    ventana,
    text="Iniciar",
    font=("Arial", 12),
    command=iniciar
)
btn_iniciar.pack(pady=10)

btn_detener = tk.Button(
    ventana,
    text="Detener",
    font=("Arial", 12),
    command=detener
)
btn_detener.pack(pady=10)

ventana.mainloop()