# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('./sql_scripts/*', './sql_scripts/'), ('./config.yaml', './')],
    hiddenimports=['psutil._psutil_windows', 'psutil._psutil_common', 'psutil'],
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
    a.binaries,        # Include binaries in the exe
    a.datas,          # Include data in the exe
    [],
    name='mimicQuery',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,    # Changed to False to hide terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(exe,
         name='mimicQuery.app',
         icon=None,
         bundle_identifier='com.mimicquery.app')  # Added bundle identifier