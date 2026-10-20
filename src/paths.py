"""Rutas de recursos incluidos y datos editables de la aplicación."""

from pathlib import Path
import os
import shutil
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resource_path(*parts: str) -> Path:
    """Obtiene recursos tanto desde el código fuente como desde PyInstaller."""
    base_dir = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))
    return base_dir.joinpath(*parts)


APP_DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / "CargueFacturas"
DATA_DIR = APP_DATA_DIR / "data"
DATA_FILE = DATA_DIR / "data.json"
DEFAULT_DATA_FILE = resource_path("data", "data.json")


def ensure_data_file() -> Path:
    """Crea la copia editable inicial de fechas en el perfil del usuario."""
    if not DATA_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if DEFAULT_DATA_FILE.exists():
            shutil.copy2(DEFAULT_DATA_FILE, DATA_FILE)
    return DATA_FILE
