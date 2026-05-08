# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('pynput')
hiddenimports += collect_submodules('pyautogui')


a = Analysis(
    ['F:\\Code\\OptoStim\\V5.1.2.py'],
    pathex=[],
    binaries=[],
    datas=[('F:\\Code\\OptoStim\\icon.png', '.'), ('F:\\Code\\OptoStim\\app_settings.json', '.')],
    hiddenimports=hiddenimports,
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
    name='OptoStim2P_v5.1.2',
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
    icon=['F:\\Code\\OptoStim\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OptoStim2P_v5.1.2',
)
