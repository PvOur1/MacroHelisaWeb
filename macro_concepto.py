import pyautogui
import time
import tkinter as tk
from tkinter import *
import json
from tkinter.ttk import Combobox
import copy

with open('fechas.json', 'r') as file: #abre el archivo JSON generado 
    data = json.load(file) #lee los datos dentro del JSON 

        
def macroconcepto(num_repeticiones):
    fechas = copy.deepcopy(data["fechas"])  # Hacemos una copia de la lista de fechas
    
    for _ in range(num_repeticiones): # ciclo que define el numero de repeticiones
        for fecha in fechas:
            print(fecha) #imprime la primera fecha en orden, para aumentar a la siguiente fecha creada 
            semana = 0
            pyautogui.click(x=320, y=20)#cli
            pyautogui.press('TAB')
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('TAB')    
            pyautogui.press('TAB')
            pyautogui.press('ENTER')
                
            texto = ("CDC {} COMP MATERIAL RECICLADO".format(fecha).upper())
            pyautogui.write(texto)
            pyautogui.press('DOWN')
            pyautogui.write(texto)
            time.sleep(1)
            pyautogui.press('TAB')
            pyautogui.press('TAB')
            pyautogui.press('TAB')
            pyautogui.press('right')
            pyautogui.press('TAB')
            pyautogui.press('ENTER')
            pyautogui.write(texto)
            pyautogui.press('DOWN')
            pyautogui.write(texto)
            pyautogui.press('TAB')
            pyautogui.press('TAB')
            pyautogui.press('ENTER')
            pyautogui.press('DOWN')
            semana += 1

def run_macro():
    num_repeticiones = int(entry_repeticiones.get())  
    macroconcepto(num_repeticiones)

raiz = Tk()
raiz.title("Macro Concepto")
raiz.resizable(1, 1)

frame1 = Frame(raiz, bg="white", width="650", height="400", border=10, relief="groove")
frame1.pack(fill="both", expand=True)
frame1.columnconfigure(1, weight=1)
frame1.columnconfigure(2, weight=1)

Label(frame1, text="Cambiar conceptos", fg="red",bg="white", font=("Comic Sans MS", 14)).grid(row=0, column=0, pady=20, padx=20)
entry_repeticiones = Entry(frame1)
entry_repeticiones.grid(row=1, column=1, pady=10, padx=10)
entry_repeticiones.config(justify="center")
Label(frame1, text="Num Repeticiones = ",bg="white").grid(row=1, column=0, pady=10, padx=10)

btn_iniciar_macro = Button(frame1, text="Iniciar Macro",relief="groove", command=run_macro)
btn_iniciar_macro.grid(row=2, column=1, columnspan=2, pady=2)

raiz.mainloop()
