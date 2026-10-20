from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from macro_concepto import crear_ventana  # noqa: E402


if __name__ == "__main__":
    crear_ventana().mainloop()
