# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# ONNX Runtime, OpenCV ve PyQt6'nın çalışması için gereken C++ DLL'lerini otomatik topluyoruz
binaries = []
binaries += collect_dynamic_libs('onnxruntime')
binaries += collect_dynamic_libs('cv2')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('models', 'models'),      # Yapay zeka modellerinin olduğu klasör
        ('dataset', 'dataset'),    # Referans yüzlerin olduğu klasör
        ('captures', 'captures'),
        ('.env', '.'),
        ('basicsr', 'basicsr'),
        ('gfpgan', 'gfpgan'),   
    ],
    hiddenimports=[
        'PyQt6', 
        'cv2', 
        'onnxruntime', 
        'psycopg2', 
        'numpy', 
        'engine'
    ],
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
    name='PersonaShift',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, # Hataları görebilmek için ilk derlemede terminali açık bırakıyoruz. Daha sonra False yapacağız.
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
    name='PersonaShift',
)