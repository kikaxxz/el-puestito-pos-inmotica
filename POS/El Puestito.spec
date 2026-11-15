# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('assets', 'assets'), ('server/templates', 'server/templates'), ('server/static', 'server/static')]
datas += collect_data_files('escpos')


a = Analysis(
    ['app.py'],
    pathex=['.', 'src', 'views', 'widgets'],
    binaries=[('libusb-1.0.dll', '.')],
    datas=datas,
    hiddenimports=['engineio.async_drivers.threading', 'usb.core', 'usb.backend.libusb1', 'firebase_admin', 'google.auth', 'google.cloud.core'],
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
    name='El Puestito',
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
    uac_admin=True,
    icon=['assets\\logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='El Puestito',
)
