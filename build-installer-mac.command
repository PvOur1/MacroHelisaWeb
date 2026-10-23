#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ "$(uname -s)" != Darwin ]]; then
    echo "Este instalador debe compilarse en macOS."
    exit 1
fi

# Usa Python de python.org con Tkinter, no el Python del sistema.
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" -c 'import sys, tkinter; assert sys.version_info >= (3, 10), "Se requiere Python 3.10 o superior"'
if [[ ! -d .venv-mac ]]; then
    "$PYTHON_BIN" -m venv .venv-mac
fi
PY=.venv-mac/bin/python
"$PY" -c 'import tkinter; from tkinter import Tk; r = Tk(); r.update(); r.destroy()'
"$PY" -m pip install -r requirements.txt 'Pillow>=10' 'PyInstaller==6.16.0'
"$PY" -m pip check
"$PY" -m PyInstaller --noconfirm --clean --distpath dist --workpath build/macos packaging/macos.spec

ARCH="$("$PY" -c 'import platform; print(platform.machine())')"
mkdir -p installer-output
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/CargueFacturas.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT
ditto dist/CargueFacturas.app "$STAGE/CargueFacturas.app"
ln -s /Applications "$STAGE/Applications"
hdiutil create -volname CargueFacturas -srcfolder "$STAGE" -ov -format UDZO "installer-output/CargueFacturas-mac-${ARCH}.dmg"
hdiutil verify "installer-output/CargueFacturas-mac-${ARCH}.dmg"
echo "Instalador creado: installer-output/CargueFacturas-mac-${ARCH}.dmg"
echo "Compilación local sin firma Developer ID ni notarización de Apple."
