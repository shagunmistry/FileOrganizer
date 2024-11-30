# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*.png', 'assets'),  # Include any PNG assets
        ('assets/icon.ico', '.'),    # Include the icon
    ],
    hiddenimports=[
        'PyQt6',
        'anthropic',
        'openai',
        'groq'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FileOrganizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for no console window
    icon='assets/icon.ico',  # Windows icon
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS specific
app = BUNDLE(
    exe,
    name='FileOrganizer.app',
    icon='assets/icon.ico',  # macOS icon
    bundle_identifier='com.shagunmistry.fileorganizer',
    codesign_identity='Developer ID Application: shagunmistry',
    entitlements_file='entitlements.plist'
    version='1.0.0',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0',
    },
)