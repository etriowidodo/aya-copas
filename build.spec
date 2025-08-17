# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('AYA.ico', '.'),  # Make sure the icon file is included
]

a = Analysis(
    ['aya_copas.py'],  # Your main script file
    pathex=['D:\\KERJAAN\\experiment\\aya_copy_paste_super_cepat'],  # Your project path
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'logging',
        'os',
        'shutil',
        'sys',
        'threading',
        'time',
        'datetime',
        'tkinter',
        'collections'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'PIL',
        'test',
        'unittest'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='AYA_COPAS',  # Changed to match your application name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='AYA.ico',  # Make sure this matches your icon file
    onefile=True,  # Create a single executable file
)