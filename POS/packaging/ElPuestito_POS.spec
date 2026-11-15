from pathlib import Path
import os
from PyInstaller.utils.hooks import collect_data_files

root = Path(SPECPATH).parent
assets = Path(os.environ.get('PUESTITO_BUILD_ASSETS', str(root / 'Assets')))
datas = [(str(assets), "Assets"),
         (str(root / "server/templates"), "server/templates"),
         (str(root / "server/static"), "server/static")]
datas += collect_data_files("escpos")
a = Analysis(
    [str(root / "packaging/pos_entry.py")],
    pathex=[str(root), str(root / "src"), str(root / "views"), str(root / "widgets")],
    binaries=[(str(root / "libusb-1.0.dll"), ".")], datas=datas,
    hiddenimports=["app", "engineio.async_drivers.threading", "usb.core",
                   "usb.backend.libusb1", "firebase_admin", "google.auth"],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False, optimize=0,
)
# Qt uses Windows' ICU ABI. A same-named ICU DLL from another tool on PATH
# exports version-suffixed symbols and breaks QtGui in the frozen application.
a.binaries = [entry for entry in a.binaries
              if Path(entry[0]).name.lower() not in {'icuuc.dll', 'icudt78.dll'}]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="ElPuestito_POS",
          debug=False, strip=False, upx=False, console=False, uac_admin=False,
          icon=str(root / "Assets/logo.ico"))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="POS")
