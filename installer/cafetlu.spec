# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — đóng gói GUI CafeTLU thành thư mục chạy được trên Windows.

Build từ gốc repo:  pyinstaller --noconfirm --clean installer/cafetlu.spec
Kết quả:            dist/CafeTLU/CafeTLU.exe  (+ thư mục _internal)

Vì sao `onedir` (Analysis + COLLECT) thay vì `onefile`:
- app Qt khởi động nhanh hơn (không giải nén mỗi lần chạy),
- ít bị Windows Defender/antivirus chặn hơn,
- thiếu file thì thấy ngay trong thư mục, dễ sửa hơn là file .exe nén.
"""

import os
import sys
from pathlib import Path

SPEC_DIR = Path(SPECPATH).resolve()  # installer/
ROOT = SPEC_DIR.parent  # repo root
NAMESPACE: dict[str, str] = {}
exec((ROOT / "shared" / "version.py").read_text(encoding="utf-8"), NAMESPACE)
APP_NAME = NAMESPACE["APP_NAME"]

# File mô tả version cho .exe (Windows). Script build sinh ra, không commit.
VERSION_FILE = os.environ.get("CAFETLU_VERSION_FILE")
IS_WINDOWS = sys.platform == "win32"

a = Analysis(
    [str(ROOT / "gui" / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    # Mọi tài nguyên đọc lúc chạy phải nằm đây, nếu không sẽ chết trên máy sạch.
    datas=[(str(ROOT / "assets"), "assets")],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtSvg",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # GUI chỉ nói HTTP với API — không nhúng driver DB, không nhúng test.
    excludes=["tests", "pytest", "pytestqt", "PySide6.QtWebEngineCore", "PySide6.Qt3DCore"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # bản phát hành: không mở cửa sổ đen
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(SPEC_DIR / "app.ico") if IS_WINDOWS else None,
    version=VERSION_FILE if IS_WINDOWS else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=APP_NAME,
)
