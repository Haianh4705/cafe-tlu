"""Kiểm thử đơn vị cho các thành phần giao diện tĩnh: Theme, i18n và ApiClient."""

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
