# PyInstaller one-folder build: no per-launch extraction and no UPX.
import os
from pathlib import Path

root = Path(SPECPATH)
player = Path(os.environ.get('MACAST_MPV_DIR', str(root / 'bin'))).resolve()
data = [(str(root / source), destination) for source, destination in [
    ('macast/.version', 'macast'), ('macast/xml', 'macast/xml'),
    ('macast/assets', 'macast/assets'), ('mpv_ui', 'mpv_ui'),
    ('bundled_plugins', 'bundled_plugins')]]
binaries = [(str(player / 'mpv.exe'), 'bin')]
binaries.append((str(player / 'vulkan-1.dll'), 'bin'))
# Windows 10/11 provide D3DCompiler_47; the archive's Win7-era _43 DLL
# and updater/installer helpers are deliberately outside this build.
a = Analysis([str(root / 'Macast.py')], pathex=[str(root)], binaries=binaries,
             datas=data, hiddenimports=['pystray._win32', 'lxml.etree', 'email.utils',
                                       'macast.diagnostics', 'macast_renderer.ipc'],
             hookspath=[str(root)],
             excludes=['tkinter', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
                       'numpy', 'matplotlib', 'pytest', 'IPython'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='Macast',
          debug=False, strip=False, upx=False, console=False,
          icon=str(root / 'macast/assets/icon.ico'),
          manifest=str(root / 'packaging/windows.manifest'))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               name='Macast-Overhauled-Windows')
