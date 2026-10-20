# Permite que PyInstaller encuentre tkinter incluso si su comprobación de Tcl
# falla durante el empaquetado. Las bibliotecas Tcl/Tk se agregan en el .spec.


def pre_find_module_path(hook_api):
    pass
