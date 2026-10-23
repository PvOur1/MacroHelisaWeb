from pathlib import Path

root = Path(SPECPATH).parent
a = Analysis(
    [str(root / "run.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=[(str(root / "HTML5.png"), "."), (str(root / "data/data.json"), "data")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="CargueFacturas",
    debug=False,
    strip=False,
    upx=False,
    console=False,
)
collection = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="CargueFacturas")
app = BUNDLE(
    collection,
    name="CargueFacturas.app",
    bundle_identifier="com.carguefacturas.desktop",
    info_plist={
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "NSHighResolutionCapable": True,
        "NSScreenCaptureUsageDescription": "CargueFacturas necesita localizar Helisa en la pantalla.",
        "NSAccessibilityUsageDescription": "CargueFacturas necesita enviar clics y pulsaciones a Helisa.",
    },
)
