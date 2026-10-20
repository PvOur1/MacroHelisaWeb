@echo off
setlocal

set "APP_DIR=%LOCALAPPDATA%\Programs\CargueFacturas"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

if not exist "%APP_DIR%" mkdir "%APP_DIR%"
copy /Y "%~dp0CargueFacturas.exe" "%APP_DIR%\CargueFacturas.exe" >nul

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$shell = New-Object -ComObject WScript.Shell; $shortcut = $shell.CreateShortcut($env:APPDATA + '\Microsoft\Windows\Start Menu\Programs\CargueFacturas.lnk'); $shortcut.TargetPath = $env:LOCALAPPDATA + '\Programs\CargueFacturas\CargueFacturas.exe'; $shortcut.WorkingDirectory = $env:LOCALAPPDATA + '\Programs\CargueFacturas'; $shortcut.Description = 'Actualizar conceptos de Helisa'; $shortcut.Save()"

start "" "%APP_DIR%\CargueFacturas.exe"
endlocal
