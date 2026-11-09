#!/usr/bin/env bash
# ============================================================
# Build bộ cài Windows cho CafeTLU.
#
#   bash scripts/build_installer.sh        (hoặc make build-installer)
#
# Kết quả:
#   dist/CafeTLU/CafeTLU.exe               — bản chạy trực tiếp (PyInstaller onedir)
#   installer/Output/CafeTLU-Setup-v*.exe  — bộ cài (cần Inno Setup)
#
# Version lấy từ shared/version.py — nguồn duy nhất. Không sửa tay ở .iss/spec.
# ============================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Dùng venv nếu có (Windows: .venv/Scripts, macOS/Linux: .venv/bin)
PY="${PYTHON:-python3}"
if [[ -x ".venv/bin/python" ]]; then
  PY=".venv/bin/python"
elif [[ -x ".venv/Scripts/python.exe" ]]; then
  PY=".venv/Scripts/python.exe"
fi

VERSION="$("$PY" -c 'from shared.version import __version__; print(__version__)')"
echo "── CafeTLU v$VERSION ─────────────────────────────"

if ! "$PY" -m PyInstaller --version >/dev/null 2>&1; then
  echo "❌ Thiếu PyInstaller. Cài: $PY -m pip install pyinstaller==6.11.1"
  exit 1
fi

# --- Sinh version resource cho .exe (chỉ Windows đọc; file nằm trong build/) ---
mkdir -p build
"$PY" - "$VERSION" > build/version_info.txt <<'PYEOF'
import sys

version = sys.argv[1]
parts = [int(p) for p in version.split(".") if p.isdigit()][:4]
parts += [0] * (4 - len(parts))
v4 = ", ".join(str(p) for p in parts)

print(f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({v4}),
    prodvers=({v4}),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'Nhom 5 - Dai hoc Thang Long'),
        StringStruct('FileDescription', 'CafeTLU - Quan ly quan cafe'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', 'CafeTLU'),
        StringStruct('OriginalFilename', 'CafeTLU.exe'),
        StringStruct('ProductName', 'CafeTLU'),
        StringStruct('ProductVersion', '{version}')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""")
PYEOF
export CAFETLU_VERSION_FILE="$ROOT/build/version_info.txt"

# --- 1. PyInstaller (onedir) ---
echo "→ PyInstaller…"
"$PY" -m PyInstaller --noconfirm --clean installer/cafetlu.spec

if [[ ! -f "dist/CafeTLU/CafeTLU.exe" && ! -f "dist/CafeTLU/CafeTLU" ]]; then
  echo "❌ PyInstaller không tạo ra dist/CafeTLU/. Xem log phía trên."
  exit 1
fi
echo "✅ dist/CafeTLU/ ($(du -sh dist/CafeTLU 2>/dev/null | cut -f1))"

# --- 2. Inno Setup (chỉ có trên Windows; macOS/Linux bỏ qua và báo rõ) ---
ISCC="${ISCC:-}"
if [[ -z "$ISCC" ]]; then
  if command -v iscc >/dev/null 2>&1; then
    ISCC="iscc"
  elif [[ -f "/c/Program Files (x86)/Inno Setup 6/ISCC.exe" ]]; then
    ISCC="/c/Program Files (x86)/Inno Setup 6/ISCC.exe"
  elif [[ -f "C:/Program Files (x86)/Inno Setup 6/ISCC.exe" ]]; then
    ISCC="C:/Program Files (x86)/Inno Setup 6/ISCC.exe"
  fi
fi

if [[ -z "$ISCC" ]]; then
  echo "⚠️  Không thấy Inno Setup (ISCC). Đã có dist/CafeTLU/ nhưng CHƯA có Setup.exe."
  echo "    Windows: cài Inno Setup 6 rồi chạy lại; hoặc để CI windows-latest build."
  exit 0
fi

echo "→ Inno Setup…"
# Git Bash (MSYS) tự đổi "/D..." thành đường dẫn Windows -> ISCC thấy 2 file script.
# Tắt quy đổi đó cho đúng một tham số /D.
MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" "$ISCC" "/DMyAppVersion=$VERSION" "installer/cafetlu.iss"

SETUP="installer/Output/CafeTLU-Setup-v$VERSION.exe"
if [[ -f "$SETUP" ]]; then
  echo "✅ $SETUP ($(du -h "$SETUP" | cut -f1))"
else
  echo "❌ Không thấy $SETUP — kiểm tra log ISCC."
  exit 1
fi
