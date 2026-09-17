# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('config', 'config'), ('ui', 'ui'), ('core', 'core'), ('best.pt', '.')]
datas += collect_data_files('ultralytics')


a = Analysis(
    ['D:/GUI Duren/GUI Duren/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['torchvision', 'ultralytics', 'cv2', 'scipy', 'pynput.keyboard._win32', 'openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DurianVision',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DurianVision',
)
