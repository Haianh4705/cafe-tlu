"""Kiểm thử đơn vị cho các thành phần giao diện tĩnh: Theme, i18n và ApiClient."""

import ast
import re
from pathlib import Path

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import t
from gui.theme import COLOR, FONT, RADIUS, SPACE


def test_theme_tlu_tokens_present() -> None:
    """Kiểm tra đầy đủ các token màu thương hiệu Thăng Long và độ tương phản cơ bản."""
    assert COLOR["navy"] == "#000066"
    assert COLOR["red"] == "#F32409"
    assert COLOR["surface"] == "#FFFFFF"
    assert "tint_100" in COLOR
    assert "brand_400" in COLOR


def test_theme_spacing_8pt_grid() -> None:
    """Kiểm tra lưới khoảng cách 8pt chỉ chứa các giá trị 4, 8, 16, 24, 32."""
    assert SPACE["xs"] == 4
    assert SPACE["sm"] == 8
    assert SPACE["md"] == 16
    assert SPACE["lg"] == 24
    assert SPACE["xl"] == 32


def test_theme_radius_and_font() -> None:
    """Kiểm tra bo góc tối giản (2 mức) và font Manrope."""
    assert RADIUS["sm"] == 6
    assert RADIUS["md"] == 10
    assert FONT["family"] == "Manrope"


def test_i18n_translation_lookup() -> None:
    """Kiểm tra hàm tra cứu chuỗi hiển thị tiếng Việt."""
    assert t("app_name") == "CafeTLU"
    assert t("login_title") == "Đăng nhập hệ thống"

    # Kiểm tra format tham số
    formatted = t("confirm_delete_product", name="Trà đào")
    assert "Trà đào" in formatted

    # Kiểm tra khoá không tồn tại thì trả về chính key
    assert t("non_existing_key") == "non_existing_key"


def test_api_client_error_initialization() -> None:
    """Kiểm tra khởi tạo và thuộc tính của ApiClientError."""
    err = ApiClientError(code="NOT_FOUND", message="Không tìm thấy món", details={"id": 12})
    assert err.code == "NOT_FOUND"
    assert err.message == "Không tìm thấy món"
    assert err.details == {"id": 12}
    assert str(err) == "Không tìm thấy món"


def test_api_client_token_management() -> None:
    """Kiểm tra lưu và xoá token xác thực trong ApiClient."""
    client = ApiClient(base_url="http://test.local/api/v1")
    assert client.access_token is None

    client.set_tokens("access123", "refresh456")
    assert client.access_token == "access123"
    assert client.refresh_token == "refresh456"
    assert client._headers()["Authorization"] == "Bearer access123"

    client.clear_tokens()
    assert client.access_token is None
    assert "Authorization" not in client._headers()


def _iter_non_docstring_strings(tree: ast.AST) -> list[str]:
    """Lấy toàn bộ chuỗi literal trong AST trừ docstring của module/class/hàm."""
    docstring_nodes: set[int] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring_nodes.add(id(node.body[0].value))

    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstring_nodes
    ]


def test_gui_floor_no_hardcoded_hex_or_bare_qframe() -> None:
    """Rào Floor Check: cấm mã màu #hex ngoài theme.py và cấm QFrame { không gắn #objectName."""
    hex_pattern = re.compile(r"#[0-9a-fA-F]{3,8}\b")
    bare_qframe_pattern = re.compile(r"(?<![#\w])QFrame\s*\{")
    gui_root = Path(__file__).resolve().parent.parent / "gui"

    hex_violations: list[str] = []
    qframe_violations: list[str] = []

    for py_file in sorted(gui_root.rglob("*.py")):
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))

        if py_file.name != "theme.py":
            for literal in _iter_non_docstring_strings(tree):
                matches = hex_pattern.findall(literal)
                if matches:
                    hex_violations.append(f"{py_file.name}: {matches}")

        for literal in _iter_non_docstring_strings(tree):
            qframe_matches = bare_qframe_pattern.findall(literal)
            if qframe_matches:
                qframe_violations.append(f"{py_file.name}: {qframe_matches}")

    assert not hex_violations, f"Phát hiện mã màu #hex cứng ngoài theme.py: {hex_violations}"
    assert not qframe_violations, f"Phát hiện QFrame {{ thiếu #objectName: {qframe_violations}"
