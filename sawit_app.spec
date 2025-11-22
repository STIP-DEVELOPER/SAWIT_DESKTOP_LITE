# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

project_root = os.path.abspath(".")

# Include all NCNN model files
ncnn_binaries = collect_data_files("models", include_py_files=True)

# Include images/icons
asset_files = collect_data_files("src/assets")

# Include config folder
config_files = collect_data_files("src/configs")

# Include logs folder
log_files = collect_data_files("logs")

# Include videos (optional)
video_files = collect_data_files("videos")

# Include utils, enums, ui etc is done automatically through PyInstaller

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[project_root],
    binaries=collect_dynamic_libs("cv2") +
             collect_dynamic_libs("ncnn"),
    datas=asset_files + config_files + log_files + video_files + ncnn_binaries,
    hiddenimports=[
        "PyQt5.sip",
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
        "cv2",
    ],
    hookspath=['hooks'],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='SawitApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    bundle_files=1
)

app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='SawitApp.app',
)
