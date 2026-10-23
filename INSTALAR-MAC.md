# Crear e instalar CargueFacturas en macOS

La aplicación es de escritorio. Compila el instalador en un Mac del mismo tipo que el equipo de destino: Apple Silicon (arm64) o Intel (x86_64). PyInstaller no genera aplicaciones macOS desde Linux o Windows.

1. Instala Python 3.12 desde https://www.python.org/downloads/macos/ (incluye Tkinter).
2. Descarga este repositorio y abre Terminal en su carpeta.
3. Ejecuta `bash build-installer-mac.command`.
4. Abre el archivo `installer-output/CargueFacturas-mac-arm64.dmg` o `CargueFacturas-mac-x86_64.dmg`, según la arquitectura del Python utilizado.
5. Arrastra **CargueFacturas.app** a **Aplicaciones** y ábrela desde allí.

Puedes seleccionar otro Python con `PYTHON_BIN=/ruta/a/python3 bash build-installer-mac.command`. El entorno `.venv-mac` conserva el Python elegido en la primera ejecución; si cambias de arquitectura o versión, usa un checkout nuevo o retira ese entorno antes de recompilar.

El DMG generado es para uso local y no tiene firma Developer ID ni notarización. macOS puede bloquear su apertura. Para una aplicación que compilaste y en la que confías, utiliza la opción **Abrir igualmente** de **Ajustes del Sistema → Privacidad y seguridad**, si está disponible. La distribución pública requiere firma y notarización de Apple; este script no las configura.

En **Privacidad y seguridad**, concede a CargueFacturas permisos de **Accesibilidad** y **Grabación de pantalla** (el nombre puede variar según macOS). Cierra y vuelve a abrir la aplicación después de concederlos. La macro necesita ver la página de Helisa en esa misma pantalla. Prueba primero con datos de prueba.

Las fechas editables se guardan en `~/CargueFacturas/data/data.json`; reinstalar la aplicación no reemplaza ese archivo.

La compilación y el comportamiento real en macOS deben comprobarse en un Mac. La validación realizada en el entorno de desarrollo Linux no valida el DMG ni los permisos de macOS.
