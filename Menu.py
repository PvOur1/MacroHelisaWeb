import tkinter as tk # libreria grafica
from tkinter import *# libreria grafica
from tkinter import ttk# libreria grafica listas 
from tkinter import messagebox#  libreria grafica mensajes emergentes
from macro_concepto2 import macroconcepto2 # importa macro de cambio conceptos
from macro_envio import * # importa macro de envio 
import json# libreria manejo JSON


global dia1, dia2, dia3, dia4, dia5 #variables globales
global fecha1, fecha2, fecha3, fecha4, fecha5#variables globales
fecha1 = fecha2 = fecha3 = fecha4 = fecha5 = ""
def envio_factura():#crea un nuevo metedo para enviar facturas
    raiz.withdraw()#esconde la ventana principal
    global envio #variable global para usar entre distitos metodos 
    envio = tk.Toplevel(raiz)  # Crear una nueva ventana sobre la ventana principal
    envio.title("Helisa Bot v1.0") # titulo de ventana emergente
    icono_all = tk.PhotoImage(file="ICONO.png")# Define el icono de la ventana
    envio.iconphoto(False, icono_all) #determina el icono por defecto
    envio.geometry("400x200")#determina el tamaÑo de la ventana actual
    envio.protocol("WM_DELETE_WINDOW", cerrar_envio) # boton dirigo a ventana principal
    #titulo
    Label(envio, text="Envio de Facturas", fg="black", font=("Times New Roman", 16, "bold")).grid(row=0, column=0, pady=20, padx=20)#texto en ventana
    #btn envio
    btn_init = Button(envio, text="Iniciar", relief="groove",command=enviados)# ejecuta  macro de envio 
    Label(envio, text="F1 = Definir concepto   ").grid(row=2, column=0, columnspan=2, pady=2)#texto en ventana
    Label(envio, text="F3 = Enviar Factura     ").grid(row=3, column=0, columnspan=2, pady=2)#texto en ventana
    Label(envio, text="F12 = Detener Macro     ").grid(row=4, column=0, columnspan=2, pady=2)#texto en ventana
    btn_init.grid(row=2, column=1, columnspan=2, pady=2)# configuracion en ventana 
    btn_volver = Button(envio, text="volver", relief="groove", command=cerrar_envio)# boton dirigo a ventana principal
    btn_volver.grid(row=3, column=1, columnspan=2, pady=2) # Configurar el protocolo de cierre

def fechas():
    global entry_semana1, entry_semana2, entry_semana3, entry_semana4, entry_semana5, año_combobox, mes_combobox, semana_combobox, semana_entries, semana_labels#variables globales
    global config#variables globales
    cerrar_cambio2()#cierra la ventana
    def mostrar_campos_semanas(event):
        num_semanas = int(semana_combobox.get())
        for i in range(5): #ciclo para escoger numero de semanas 
            if i < num_semanas:
                semana_entries[i].grid()# imprime el numero de entradas segun semanas escogidas
                semana_labels[i].grid()# imprime el texto segun semanas ecogidas
            else:
                semana_entries[i].grid_remove()#elima numero de entradas
                semana_labels[i].grid_remove()#elimina el texto segun semanas

    def limpiar_campos():
        for entry in semana_entries:#aplica en todas las entradas la siguiente funcion
            entry.delete(0, tk.END)#eliminar todos los valores ingresados
        mes_combobox.set('')#vacia la lista mes 
        año_combobox.set('')#vacia la lista año

    def mostrar_fechas():
        num_semanas = int(semana_combobox.get())#define el numero de semanas segun la seleccion 
        dias = [entry.get() for entry in semana_entries[:num_semanas]] #trae los valores de dias
        mes = mes_combobox.get()#trae el valor de mes
        año = año_combobox.get()#trae el valor año
        fechas = [f"{dia}/{mes}/{año}" for dia in dias]#formato de impresion en pantalla 
        fechas_texto = "\n".join(fechas)
        messagebox.showinfo("Fechas Seleccionadas", fechas_texto)#imprime las fechas con formato aplicado

    config = tk.Toplevel(cambio1)# Crear una nueva ventana sobre la cambio conceptos
    config.title("Helisa Bot v1.0")# titulo de ventana emergente
    icono_all = tk.PhotoImage(file="ICONO.png")# Define el icono de la ventana
    config.iconphoto(False, icono_all)#determina el icono por defecto
    config.geometry("600x400")#determina el tama;o de la ventana actual
    config.protocol("WM_DELETE_WINDOW")#se asegura que se cierre correctamente una ventana
    Label(config, text="Fechas de Timbrado", fg="black", font=("Times New Roman", 16, "bold")).grid(row=0, column=0)#texto en ventana

    # Número de semanas
    semanas = [str(i) for i in range(1, 6)]  # Generar lista del 1 al 5
    semana_combobox = ttk.Combobox(config, values=semanas, state="readonly")
    semana_combobox.grid(row=1, column=1, pady=10, padx=10)#ubicacion en el frame
    semana_combobox.bind("<<ComboboxSelected>>", mostrar_campos_semanas)
    Label(config, text="Número de Semanas").grid(row=1, column=0, pady=10, padx=1)#texto en ventana

    # Entradas de semanas
    semana_entries = [Entry(config) for _ in range(5)] # define formato de semanas
    semana_labels = [Label(config, text=f"Semana {i+1}") for i in range(5)]#define formato de semanas en texto

    for i, (entry, label) in enumerate(zip(semana_entries, semana_labels)):
        entry.grid(row=i+2, column=1, pady=10, padx=10)#ubicacion en el frame
        entry.grid_remove()  # Ocultar inicialmente
        label.grid(row=i+2, column=0, pady=10, padx=1)#ubicacion en el frame
        label.grid_remove()  # Ocultar inicialmente

    entry_semana1, entry_semana2, entry_semana3, entry_semana4, entry_semana5 = semana_entries # llama variables globales

    # Meses
    meses = [str(i) for i in range(1, 13)]  # Generar lista del 1 al 12
    mes_combobox = ttk.Combobox(config, values=meses, state="readonly")# define la lista como solo lectura 
    mes_combobox.grid(row=2, column=3, pady=10, padx=10)#ubicacion en el frame
    Label(config, text="Mes").grid(row=1, column=3, pady=10, padx=1)#texto en ventana

    # Año
    años = ["2024", "2025"] # años de la lisa
    año_combobox = ttk.Combobox(config, values=años, state="readonly")# define la lista como solo lectura 
    año_combobox.grid(row=5, column=3, pady=5, padx=1)#ubicacion en el frame
    Label(config, text="Año").grid(row=3, column=3)#texto en ventana

    # Guardar
    btn_guardar = Button(config, text="Guardar", relief="groove", command=dias_timbrados)#btn para guardar fechas ingresadas en JSON
    btn_guardar.grid(row=7, column=1, columnspan=1, pady=1)#define posicion de boton en la ventana

    # Limpiar
    btn_limpiar = Button(config, text="Limpiar", relief="groove", command=limpiar_campos)#limpia todos los campos de la pantalla
    btn_limpiar.grid(row=7, column=3, columnspan=1, pady=1)#define posicion de boton en la ventana

    # Mostrar Fechas
    btn_mostrar = Button(config, text="Mostrar Fechas", relief="groove", command=mostrar_fechas)#Imprime las fechas actuales a ejecutar
    btn_mostrar.grid(row=8, column=3, columnspan=2, pady=2)#define posicion de boton en la ventana

    # Volver
    btn_volver = Button(config, text="Volver", relief="groove", command=config_semanas)# vuelve al menu principal
    btn_volver.grid(row=7, column=0, columnspan=1, pady=1)#define posicion de boton en la ventana

    cambio1.withdraw()

def dias_timbrados():  # Definir fechas de cuentas de cobro
    num_semanas = int(semana_combobox.get())
    dias = [entry.get() for entry in semana_entries[:num_semanas]]
    mes = mes_combobox.get()
    año = año_combobox.get()

    fechas = [f"{dia}/{mes}/{año}" for dia in dias]

    data = {
        "fechas": fechas
    }
    json_data = json.dumps(data, indent=4)

    with open('data.json', 'w') as file:
        file.write(json_data)

    print("JSON creado exitosamente:")
    print(json_data)

def run_macro():
    num_repeticiones = int(cambio_conceptos.get())  
    macroconcepto2(num_repeticiones)


def cambio_conceptos():
    raiz.withdraw()
    def run_macro():
        num_repeticiones = int(entry_repeticiones.get())  
        macroconcepto2(num_repeticiones)
    global cambio1
    cambio1 = tk.Toplevel(raiz)# Crear una nueva ventana sobre la ventana principal
    cambio1.title("Helisa Bot v1.0")# titulo de ventana emergente
    cambio1.geometry("500x250")#determina el tama;o de la ventana actual
    icono_all = tk.PhotoImage(file="ICONO.png")# Define el icono de la ventana
    cambio1.iconphoto(False, icono_all)#determina el icono por defecto
    cambio1.protocol("WM_DELETE_WINDOW", cerrar_cambio)#se asegura que se cierre correctamente una ventana
    Label(cambio1, text="Cambio de Concetos", fg="black", font=("Times New Roman", 16, "bold")).grid(row=0, column=0, pady=20, padx=30)#texto en ventana
    #menu
    btn_volver2 = Button(cambio1, text=" Menu ",relief="groove",command=cerrar_cambio)# boton dirigo a ventana principal
    btn_volver2.grid(row=3, column=0, pady=(20, 2), padx=(20, 2), sticky="w") # Configurar el protocolo de cierre
    #configuracion semanas
    btn_config = Button(cambio1,text="Fechas",relief="groove",command=fechas, compound=tk.LEFT) # configuracion semanas
    btn_config.grid(row=3, column=1,  columnspan=2, pady=2)#define posicion de boton en la ventana
    entry_repeticiones = Entry(cambio1)# crea una lista seleccionable
    entry_repeticiones.grid(row=1, column=1, pady=10, padx=10) #ubicacion de la lista en el frame
    entry_repeticiones.config(justify="center") # centra todas las opciones de la lista
    Label(cambio1, text="Num Repeticiones ").grid(row=1, column=0, pady=10, padx=1)#texto en ventana
    raiz.withdraw()#esconde el frame principal
    btn_iniciar_macro = Button(cambio1, text="Iniciar Macro",relief="groove", command= run_macro)#llamar macro concepto
    btn_iniciar_macro.grid(row=2, column=1, columnspan=2, pady=2)#ubicacion de la lista en el frame
    
      # Ocultar la ventana principal

def cerrar_envio():
    envio.destroy()  # Cerrar la ventana secundaria
    raiz.deiconify()  # Mostrar nuevamente la ventana principal
def cerrar_cambio():
    cambio1.destroy()  # Cerrar la ventana secundaria
    raiz.deiconify() # Mostrar nuevamente la ventana principal

def cerrar_cambio2():
    cambio1.withdraw()  # Cerrar la ventana secundaria    
def config_semanas():
    config.destroy() # Cerrar la ventana secundaria 
    cambio1.deiconify()# Mostrar nuevamente la ventana anterior
#definiciones nuevas pestañas frame raiz(menu principal)///////////
def btn1():
    envio_factura()
    raiz.withdraw() # esconde la ventana principal
def btn2():
    cambio_conceptos()
    raiz.withdraw()# esconde la ventana principal

raiz = Tk()# Crear la ventana principal
raiz.title("Helisa Bot v1.0")# titulo de ventana emergente
icono_all = tk.PhotoImage(file="ICONO.png")# Define el icono de la ventana
raiz.resizable(0, 0)# Define si el tamaño de la ventana se puede modificar
raiz.geometry("300x250") #determina el tama;o de la ventana actual
raiz.iconphoto(False, icono_all)#determina el icono por defecto
###texto menu
Label(raiz, text="Herramienta a Utilizar", fg="black", font=("Times New Roman", 16, "bold")).grid(row=0, column=0, pady=20, padx=20)#texto en ventana
#///////////////botones pestaña menu//////////////////////////////////////////////////////////
btn_envio = Button(raiz, text="Envio de Facturas", relief="groove", command=btn1)# boton dirigo a nueva ventana 
btn_envio.grid(row=3, column=0, columnspan=1, pady=2)#define posicion de boton en la ventana
#bt2
btn_conceptos = Button(raiz, text="Cambiar Conceptos", relief="groove", command=btn2)# boton dirigo a nueva ventana 
btn_conceptos.grid(row=4, column=0, columnspan=1, pady=2)#define posicion de boton en la ventana
raiz.mainloop()#renderiza siempre la ventana principal

