import time
import pyautogui
import tkinter as tk

PNG_A_BUSCAR = "aceptar.png"  # Cambia el nombre si tu archivo es distinto
CONFIDENCE = 0.8              # Requiere opencv-python para funcionar

def tomar_punto(msg, espera=3):
    print(msg)
    for i in range(espera, 0, -1):
        print(f"  Posiciona el mouse... {i}")
        time.sleep(1)
    x, y = pyautogui.position()
    print(f"  Punto capturado: ({x}, {y})")
    return x, y

def mostrar_overlay(x, y, w, h):
    root = tk.Tk()
    root.overrideredirect(True)              # sin bordes
    root.attributes("-topmost", True)        # siempre al frente
    root.attributes("-alpha", 0.35)          # transparencia
    root.geometry(f"{w}x{h}+{x}+{y}")

    canvas = tk.Canvas(root, width=w, height=h, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Rectángulo con borde (no fijamos color para que herede del sistema si se prefiere)
    canvas.create_rectangle(2, 2, w-2, h-2, width=4)

    print("\nOverlay mostrado. Presiona ENTER en la consola para continuar...")
    def cerrar(_event=None):
        root.destroy()
    # Cuando detectemos Enter en consola, cerramos el overlay
    import threading, sys
    def esperar_enter():
        input()
        root.after(0, cerrar)
    threading.Thread(target=esperar_enter, daemon=True).start()

    root.mainloop()

def main():
    print("\n=== Selección de región ===")
    x1, y1 = tomar_punto("1) Mueve el mouse a la ESQUINA SUPERIOR IZQUIERDA de la región.")
    x2, y2 = tomar_punto("2) Ahora a la ESQUINA INFERIOR DERECHA de la región.")

    # Normaliza por si los puntos se tomaron invertidos
    x, y = min(x1, x2), min(y1, y2)
    w, h = abs(x2 - x1), abs(y2 - y1)
    region = (x, y, w, h)

    print(f"\nRegión definida: {region}  (x, y, width, height)")

    # Muestra overlay para validar visualmente
    mostrar_overlay(x, y, w, h)

    print("\nBuscando la imagen dentro de la región...")
    try:
        box = pyautogui.locateOnScreen(PNG_A_BUSCAR, region=region, confidence=CONFIDENCE)
    except TypeError:
        # Si no tienes opencv instalado, confidence no está disponible
        box = pyautogui.locateOnScreen(PNG_A_BUSCAR, region=region)

    if box:
        centro = pyautogui.center(box)
        pyautogui.click(centro)
        print(f"✅ Encontrado en {box}. Clic en {centro}.")
    else:
        print("❌ No se encontró la imagen en esa región. Ajusta la región o la plantilla PNG.")

if __name__ == "__main__":
    main()