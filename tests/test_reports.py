"""Unit tests cho ReportService và module xuất báo cáo Excel/PDF (vùng B)."""

from __future__ import annotations

import datetime
import os
import tempfile
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from api.services.reports import (
    ReportService,
    export_revenue_to_excel,
    export_revenue_to_pdf,
)


def test_revenue_by_day_query_execution():
    """Kiểm tra ReportService.revenue_by_day gọi SQL đúng tham số và parse kết quả."""
    mock_db = MagicMock()
    mock_row = MagicMock()
    mock_row.report_date = datetime.date(2026, 11, 10)
    mock_row.order_count = 5
    mock_row.revenue = Decimal("350000")
    mock_db.execute.return_value = [mock_row]

    rows = ReportService.revenue_by_day(mock_db, "2026-11-01", "2026-11-10")

    assert len(rows) == 1
    assert rows[0]["date"] == datetime.date(2026, 11, 10)
    assert rows[0]["order_count"] == 5
    assert rows[0]["revenue"] == Decimal("350000")
    assert mock_db.execute.called

    # Kiểm tra tham số truyền vào execute
    _, kwargs = mock_db.execute.call_args
    call_args = mock_db.execute.call_args[0]
    passed_params = call_args[1] if len(call_args) > 1 else kwargs.get("parameters")
    assert passed_params == {"from_date": "2026-11-01", "to_date": "2026-11-10"}


def test_top_selling_products_query_execution():
    """Kiểm tra ReportService.top_selling_products tổng hợp đúng top món."""
    mock_db = MagicMock()
    mock_row = MagicMock()
    mock_row.product_id = 5
    mock_row.product_name = "Bạc xỉu 3 tầng TLU"
    mock_row.category_name = "Cà phê truyền thống"
    mock_row.total_quantity = 42
    mock_row.total_revenue = Decimal("1176000")
    mock_db.execute.return_value = [mock_row]

    rows = ReportService.top_selling_products(
        mock_db, limit=5, from_date="2026-11-01", to_date="2026-11-10"
    )

    assert len(rows) == 1
    assert rows[0]["product_id"] == 5
    assert rows[0]["product_name"] == "Bạc xỉu 3 tầng TLU"
    assert rows[0]["total_quantity"] == 42
    assert rows[0]["total_revenue"] == Decimal("1176000")
    assert mock_db.execute.called

    call_args = mock_db.execute.call_args[0]
    passed_params = call_args[1]
    assert passed_params == {"limit": 5, "from_date": "2026-11-01", "to_date": "2026-11-10"}


def test_export_revenue_to_excel_formatting():
    """Kiểm tra hàm xuất Excel tạo file hợp lệ, đúng format tiền tệ và dòng tổng."""
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl chưa được cài đặt")

    sample_rows = [
        {"date": datetime.date(2026, 11, 1), "order_count": 4, "revenue": Decimal("120000")},
        {"date": datetime.date(2026, 11, 2), "order_count": 6, "revenue": Decimal("250000")},
    ]

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        res = export_revenue_to_excel(sample_rows, tmp_path, "Báo cáo thử nghiệm")
        assert os.path.exists(res)
        assert os.path.getsize(res) > 0

        wb = openpyxl.load_workbook(res)
        assert "Doanh thu" in wb.sheetnames
        ws = wb["Doanh thu"]

        # Kiểm tra tiêu đề và header
        assert ws["A1"].value == "BÁO CÁO THỬ NGHIỆM"
        assert ws["A3"].value == "Ngày"
        assert ws["B3"].value == "Số đơn hoàn thành"
        assert ws["C3"].value == "Doanh thu (VNĐ)"

        # Kiểm tra dữ liệu
        assert ws["B4"].value == 4
        assert ws["C4"].value == 120000
        assert ws["C4"].number_format == '#,##0" đ"'

        # Dòng tổng cộng (hàng 6)
        assert ws["A6"].value == "TỔNG CỘNG"
        assert ws["B6"].value == 10
        assert ws["C6"].value == 370000
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_export_revenue_to_pdf_generation():
    """Kiểm tra hàm xuất PDF tạo file hợp lệ không bị exception."""
    try:
        import reportlab  # noqa: F401
    except ImportError:
        pytest.skip("reportlab chưa được cài đặt")

    sample_rows = [
        {"date": datetime.date(2026, 11, 1), "order_count": 4, "revenue": Decimal("120000")},
    ]

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        res = export_revenue_to_pdf(sample_rows, tmp_path, "Báo cáo doanh thu mẫu")
        assert os.path.exists(res)
        assert os.path.getsize(res) > 0
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
