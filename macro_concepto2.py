import pyautogui # libreria grafica
import time #libreria tiempo
import tkinter as tk # libreria grafica
from tkinter import * # libreria grafica
import json # libreria JSON
from tkinter.ttk import Combobox# libreria grafica mensajes emergentes
import copy

with open('data.json', 'r') as file:#abre el archivo JSON generado 
    data = json.load(file)#lee los datos dentro del JSON 

        
def macroconcepto(num_repeticiones):
    
    demo = pyautogui.locateOnScreen("HTML5.png")#localiza la imagen en pantalla
    pyautogui.click(pyautogui.center(demo))
    print(f'Imagen encontrada en {demo}')
    fechas = copy.deepcopy(data["fechas"])  # Hacemos una copia de la lista de fechas
    for _ in range(num_repeticiones):
        for fecha in fechas:
            print(fecha)#imprime la primera fecha en orden, para aumentar a la siguiente fecha creada 
            semana = 0
            pyautogui.press('TAB')#presiona tecla TAB
            pyautogui.press('enter')#presiona tecla ENTER
            time.sleep(1)
            pyautogui.press('TAB')#presiona tecla TAB
            pyautogui.press('TAB')#presiona tecla TAB
            pyautogui.press('ENTER')#presiona tecla ENTER
                
            texto = ("CDC {} COMP MATERIAL RECICLADO".format(fecha).upper())
            pyautogui.write(texto)
            pyautogui.press('DOWN')#presiona tecla ABAJO
            pyautogui.write(texto)
            time.sleep(1)
            pyautogui.press('TAB')#presiona tecla TAB
            pyautogui.press('TAB')#presiona tecla TAB
            pyautogui.press('TAB')#presiona tecla TAB
            pyautogui.press('right')
            pyautogui.press('TAB')#presiona tecla TAB
            pyautogui.press('ENTER')#presiona tecla ENTER
            pyautogui.write(texto)
            pyautogui.press('DOWN')#presiona tecla ABAJO
            pyautogui.write(texto)
            pyautogui.press('TAB')#presiona tecla TAB
            pyautogui.press('TAB')#presiona tecla TAB
            pyautogui.press('ENTER')#presiona tecla ENTER
            pyautogui.press('DOWN')#presiona tecla ABAJO
            semana += 1
