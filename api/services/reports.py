"""CafeTLU — Báo cáo & Thống kê doanh thu (Report Service).

Owner: B (@trungdunxg) — Data & Reports Lead.
Nguồn chân lý số liệu cho cả API, giao diện GUI và xuất file Excel/PDF.
Tuân thủ: WORKFLOW.md mục 8 & skill report-export.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
import logging
import os
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ReportService:
    """Nghiệp vụ tổng hợp số liệu báo cáo, thống kê và xuất file cho CafeTLU."""

    @staticmethod
    def revenue_by_day(
        db: Session,
        from_date: datetime.date | str,
        to_date: datetime.date | str,
    ) -> list[dict[str, Any]]:
        """Thống kê doanh thu và số lượng đơn hoàn thành theo từng ngày.

        Truy vấn trực tiếp bằng SQL GROUP BY, bảo đảm không kéo toàn bộ bản ghi về Python.
        """
        query = text(
            """
            SELECT 
                DATE(i.paid_at) AS report_date,
                COUNT(DISTINCT o.id) AS order_count,
                COALESCE(SUM(i.final_amount), 0) AS revenue
            FROM invoices i
            JOIN orders o ON i.order_id = o.id
            WHERE DATE(i.paid_at) BETWEEN :from_date AND :to_date
              AND o.status = 'completed'
              AND o.is_deleted = 0
            GROUP BY DATE(i.paid_at)
            ORDER BY report_date ASC;
            """
        )
        result = db.execute(query, {"from_date": str(from_date), "to_date": str(to_date)})
        rows = []
        for row in result:
            rows.append(
                {
                    "date": row.report_date,
                    "order_count": int(row.order_count),
                    "revenue": Decimal(str(row.revenue)),
                }
            )
        return rows

    @staticmethod
    def top_selling_products(
        db: Session,
        limit: int = 10,
        from_date: datetime.date | str | None = None,
        to_date: datetime.date | str | None = None,
    ) -> list[dict[str, Any]]:
        """Thống kê top món bán chạy nhất theo số lượng và doanh thu."""
        conditions = ["o.status = 'completed'", "o.is_deleted = 0"]
        params: dict[str, Any] = {"limit": limit}

        if from_date:
            conditions.append("DATE(o.created_at) >= :from_date")
            params["from_date"] = str(from_date)
        if to_date:
            conditions.append("DATE(o.created_at) <= :to_date")
            params["to_date"] = str(to_date)

        where_clause = " AND ".join(conditions)
        query = text(
            f"""
            SELECT 
                p.id AS product_id,
                p.name AS product_name,
                c.name AS category_name,
                COALESCE(SUM(oi.quantity), 0) AS total_quantity,
                COALESCE(SUM(oi.subtotal), 0) AS total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE {where_clause}
            GROUP BY p.id, p.name, c.name
            ORDER BY total_quantity DESC, total_revenue DESC
            LIMIT :limit;
            """
        )
        result = db.execute(query, params)
        rows = []
        for row in result:
            rows.append(
                {
                    "product_id": int(row.product_id),
                    "product_name": str(row.product_name),
                    "category_name": str(row.category_name),
                    "total_quantity": int(row.total_quantity),
                    "total_revenue": Decimal(str(row.total_revenue)),
                }
            )
        return rows

    @staticmethod
    def revenue_by_category(
        db: Session,
        from_date: datetime.date | str | None = None,
        to_date: datetime.date | str | None = None,
    ) -> list[dict[str, Any]]:
        """Thống kê cơ cấu doanh thu theo từng danh mục món."""
        conditions = ["o.status = 'completed'", "o.is_deleted = 0"]
        params: dict[str, Any] = {}

        if from_date:
            conditions.append("DATE(o.created_at) >= :from_date")
            params["from_date"] = str(from_date)
        if to_date:
            conditions.append("DATE(o.created_at) <= :to_date")
            params["to_date"] = str(to_date)

        where_clause = " AND ".join(conditions)
        query = text(
            f"""
            SELECT 
                c.id AS category_id,
                c.name AS category_name,
                COALESCE(SUM(oi.quantity), 0) AS total_quantity,
                COALESCE(SUM(oi.subtotal), 0) AS total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE {where_clause}
            GROUP BY c.id, c.name
            ORDER BY total_revenue DESC;
            """
        )
        result = db.execute(query, params)
        rows = []
        for row in result:
            rows.append(
                {
                    "category_id": int(row.category_id),
                    "category_name": str(row.category_name),
                    "total_quantity": int(row.total_quantity),
                    "total_revenue": Decimal(str(row.total_revenue)),
                }
            )
        return rows


# -----------------------------------------------------------------------------
# Module xuất file Excel & PDF (Dùng chung 1 nguồn dữ liệu từ ReportService)
# -----------------------------------------------------------------------------
def export_revenue_to_excel(
    rows: list[dict[str, Any]],
    output_path: str,
    title: str = "BÁO CÁO DOANH THU",
) -> str:
    """Xuất báo cáo doanh thu ra file Excel (.xlsx) chuẩn openpyxl.

    Quy chuẩn:
    - Định dạng tiền tệ #,##0" đ"
    - Cố định dòng tiêu đề (freeze_panes)
    - Auto-filter
    - Dòng tổng kết cuối bảng
    """
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
        from openpyxl.utils import get_column_letter
    except ImportError as e:
        logger.error("Chưa cài đặt thư viện openpyxl: %s", e)
        raise

    wb = Workbook()
    ws = wb.active
    ws.title = "Doanh thu"

    # Tiêu đề báo cáo
    ws["A1"] = title.upper()
    ws["A1"].font = Font(name="Arial", size=14, bold=True, color="000066")

    headers = ["Ngày", "Số đơn hoàn thành", "Doanh thu (VNĐ)"]
    header_fill = PatternFill("solid", fgColor="000066")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    center_align = Alignment(horizontal="center", vertical="center")

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    money_format = '#,##0" đ"'
    thin_border = Border(
        left=Side(style="thin", color="CCCCCC"),
        right=Side(style="thin", color="CCCCCC"),
        top=Side(style="thin", color="CCCCCC"),
        bottom=Side(style="thin", color="CCCCCC"),
    )

    start_row = 4
    total_orders = 0
    total_revenue = Decimal(0)

    for idx, r in enumerate(rows):
        current_row = start_row + idx
        date_val = r["date"].strftime("%d/%m/%Y") if isinstance(r["date"], (datetime.date, datetime.datetime)) else str(r["date"])
        orders_count = r["order_count"]
        revenue = r["revenue"]

        total_orders += orders_count
        total_revenue += Decimal(str(revenue))

        c1 = ws.cell(row=current_row, column=1, value=date_val)
        c2 = ws.cell(row=current_row, column=2, value=orders_count)
        c3 = ws.cell(row=current_row, column=3, value=float(revenue))

        c1.alignment = center_align
        c2.alignment = Alignment(horizontal="right")
        c3.alignment = Alignment(horizontal="right")
        c3.number_format = money_format

        for c in (c1, c2, c3):
            c.border = thin_border

    # Dòng tổng cộng
    end_row = start_row + len(rows)
    total_fill = PatternFill("solid", fgColor="F1F5FF")
    bold_font = Font(name="Arial", size=11, bold=True)

    t1 = ws.cell(row=end_row, column=1, value="TỔNG CỘNG")
    t2 = ws.cell(row=end_row, column=2, value=total_orders)
    t3 = ws.cell(row=end_row, column=3, value=float(total_revenue))

    t1.font = bold_font
    t2.font = bold_font
    t3.font = bold_font
    t1.fill = total_fill
    t2.fill = total_fill
    t3.fill = total_fill
    t1.alignment = center_align
    t2.alignment = Alignment(horizontal="right")
    t3.alignment = Alignment(horizontal="right")
    t3.number_format = money_format

    ws.freeze_panes = "A4"
    if rows:
        ws.auto_filter.ref = f"A3:C{end_row - 1}"

    # Auto-adjust column width
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 25

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    wb.save(output_path)
    logger.info("Đã xuất file Excel doanh thu tại: %s", output_path)
    return output_path


def export_revenue_to_pdf(
    rows: list[dict[str, Any]],
    output_path: str,
    title: str = "BÁO CÁO DOANH THU QUÁN CAFÉ TLU",
) -> str:
    """Xuất báo cáo doanh thu ra PDF (chuẩn ReportLab, nhúng font tiếng Việt)."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as e:
        logger.error("Chưa cài đặt thư viện reportlab: %s", e)
        raise

    # Đăng ký font hỗ trợ tiếng Việt
    font_name = "Helvetica"
    font_bold = "Helvetica-Bold"

    manrope_path = os.path.join("assets", "fonts", "Manrope[wght].ttf")
    if os.path.exists(manrope_path):
        try:
            pdfmetrics.registerFont(TTFont("Manrope", manrope_path))
            font_name = "Manrope"
            font_bold = "Manrope"
        except Exception as e:
            logger.warning("Không thể load font Manrope: %s", e)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName=font_bold,
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#000066"),
        alignment=1,  # Center
    )
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 10 * mm))

    table_data = [["Ngày", "Số đơn", "Doanh thu (VNĐ)"]]
    total_revenue = Decimal(0)
    total_orders = 0

    for r in rows:
        date_str = r["date"].strftime("%d/%m/%Y") if isinstance(r["date"], (datetime.date, datetime.datetime)) else str(r["date"])
        orders_cnt = r["order_count"]
        rev = Decimal(str(r["revenue"]))
        total_orders += orders_cnt
        total_revenue += rev

        rev_formatted = f"{rev:,.0f} đ".replace(",", ".")
        table_data.append([date_str, str(orders_cnt), rev_formatted])

    # Hàng tổng kết
    total_rev_str = f"{total_revenue:,.0f} đ".replace(",", ".")
    table_data.append(["TỔNG CỘNG", str(total_orders), total_rev_str])

    t = Table(table_data, colWidths=[50 * mm, 45 * mm, 65 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#000066")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F1F5FF")),
                ("FONTNAME", (0, -1), (-1, -1), font_bold),
            ]
        )
    )
    elements.append(t)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    doc.build(elements)
    logger.info("Đã xuất file PDF doanh thu tại: %s", output_path)
    return output_path

