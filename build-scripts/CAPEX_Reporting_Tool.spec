# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../src/app_desktop.py'],
    pathex=['..'],
    binaries=[],
    datas=[('../templates', 'templates')],
    hiddenimports=['tkinter', 'pandas', 'openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
)
pyz = PYZ(a.pure)

# For Windows: single file exe
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CAPEX_Reporting_Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Optional: Keep COLLECT for OnDir builds (comment out if you only want OnFile)
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='CAPEX_Reporting_Tool',
# )

# For macOS, create an app bundle
app = BUNDLE(
    coll,
    name='CAPEX_Reporting_Tool.app',
    icon=None,
    bundle_identifier=None,
)
