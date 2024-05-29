import pyautogui # libreria grafica
import time #libreria tiempo
import keyboard # libreria para ejecutar comandos de teclado
from tkinter import *# libreria grafica
from tkinter import messagebox # libreria grafica mensajes emergentes

def definicion(event):
    if event.name == 'f1':  #tecla para ejecutar
        print("Se presionó la tecla F1")
        ##macro
        time.sleep(0.2)
        btn1=pyautogui.locateOnScreen("btn1.png")#localiza imagen en pantalla
        print(f'Imagen encontrada en {btn1}')# imprime coordenadas de imagen encontrada
        print(pyautogui.center(btn1))#click en el centro de la imagen
        time.sleep(0.6)
        pyautogui.click(pyautogui.center(btn1))#click en el centro de la imagen
        pyautogui.moveTo(x= 200, y= 200)#mueve el mouse al corrdenadas exactas
        time.sleep(0.6)
        pyautogui.press("right")
        time.sleep(0.3)
        btn2=pyautogui.locateOnScreen("btn2.png", grayscale= True)#localiza imagen en pantalla
        pyautogui.doubleClick(pyautogui.center(btn2))#click en el centro de la imagen
        time.sleep(0.6)
        btn3=pyautogui.locateOnScreen("btn3.png")#localiza imagen en pantalla
        pyautogui.doubleClick(pyautogui.center(btn3))#click en el centro de la imagen
        time.sleep(0.3)
        btn4 = pyautogui.locateOnScreen("btn4.png")#localiza imagen en pantalla
        print(pyautogui.center(btn4))# imprime coordenadas de imagen encontrada
        pyautogui.click(pyautogui.center(btn4))#click en el centro de la imagen
        time.sleep(0.3)
        
def envio(event):
    if event.name == 'f3':  #tecla para ejecutar
        print("Se presionó la tecla F3")#imprime si el listener detecta la tecla presionada
        pyautogui.press("enter", presses= 3)#presiona enter 3 veces
        time.sleep(1.5)
        pyautogui.press("right", presses= 1)#presiona flecha derecha
        time.sleep(0.6)
        pyautogui.press("down", presses= 5)#presiona abajo 5 veces
        time.sleep(1)
        pyautogui.press("t")
        pyautogui.press("enter", presses= 3)#presiona enter 3 veces
        time.sleep(1)
        btn5=pyautogui.locateOnScreen("btn5.png")#localiza imagen en pantalla
        time.sleep(0.5)
        pyautogui.doubleClick(pyautogui.center(btn5))#click en el centro de la imagen
        time.sleep(1)
        pyautogui.press("enter")#presiona enter
        time.sleep(3)
        
def stop_listener(event):
    if event.name == 'f12':#tecla para ejecutar
        print("Macro detenida")#imprime si el listener detecta la tecla presionada
        keyboard.unhook_all()#detiene la escucha de teclas
        messagebox.showinfo("Macro Detenida", "La macro ha sido detenida exitosamente.")#confirma el cierre de la macro

def enviados():
    messagebox.showinfo("Macro En Ejecucion","continuar en Helisa")#confirma la activacion de la macro en pantalla 
    keyboard.on_press(definicion)#crea un listener permanente segun la tecla indicada en cada metodo
    keyboard.on_press(envio)#crea un listener permanente segun la tecla indicada en cada metodo
    keyboard.on_press(stop_listener)#crea un listener permanente segun la tecla indicada en cada metodo
    
    
