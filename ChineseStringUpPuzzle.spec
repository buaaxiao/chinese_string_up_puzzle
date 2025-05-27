# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['chinese_string_up_puzzle.py'],
    pathex=[],
    binaries=[],
    datas=[('./data', 'data'), ('./image', 'image')],
    hiddenimports=[],
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
    name='ChineseStringUpPuzzle',
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
    icon=['image/icon.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChineseStringUpPuzzle',
)
app = BUNDLE(
    coll,
    name='ChineseStringUpPuzzle.app',
    icon='image/icon.png',
    bundle_identifier=None,
)
