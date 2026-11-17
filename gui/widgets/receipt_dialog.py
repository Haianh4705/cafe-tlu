"""Hộp thoại Xem trước và In hoá đơn thanh toán (ReceiptDialog / Bill K80) trong CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint 19 POST /orders/{id}/checkout -> tạo hoá đơn (invoices).
- docs/test-cases.md: TC-ORD-03 (Thanh toán, tạo hoá đơn).
- .claude/skills/ui-design/SKILL.md: Khổ giấy in nhiệt K80 chuẩn quán café, màu sắc Navy TLU, font Manrope.
"""

from datetime import datetime
from typing import Any

from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from gui.i18n import format_currency, t
from gui.theme import COLOR, RADIUS, SPACE


class ReceiptDialog(QDialog):
    """Hộp thoại xem trước phiếu thanh toán theo chuẩn in nhiệt K80 và hỗ trợ in/xuất PDF."""

    def __init__(
        self,
        receipt_data: dict[str, Any],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.receipt_data = receipt_data
        self.invoice_code = receipt_data.get(
            "invoice_code", f"HD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        self.table_name = receipt_data.get("table_name", "Mang về")
        self.cashier_name = receipt_data.get("cashier_name", "Thu ngân")
        self.created_at = receipt_data.get(
            "created_at", datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )
        self.items = receipt_data.get("items", [])
        self.total_amount = int(receipt_data.get("total_amount", 0))
        self.payment_method = receipt_data.get("payment_method", "cash")
        self.received_amount = int(receipt_data.get("received_amount", self.total_amount))
        self.change_amount = int(receipt_data.get("change_amount", 0))

        self.setWindowTitle(f"{t('receipt_title')} — {self.invoice_code}")
        self.setFixedWidth(460)
        self.setFixedHeight(680)
        self.setModal(True)

        self._init_ui()

    def _generate_html(self) -> str:
        """Sinh mã HTML định dạng phiếu in nhiệt K80 (rộng ~80mm / 300px nội dung)."""
        pm_text = (
            t("checkout_method_cash") if self.payment_method == "cash" else t("checkout_method_qr")
        )

        rows_html = ""
        for idx, item in enumerate(self.items, start=1):
            name = item.get("name", "Món")
            qty = item.get("quantity", 1)
            price = item.get("price", 0)
            subtotal = item.get("subtotal", price * qty)
            note = item.get("note", "").strip()
            note_html = (
                f"<div style='font-size: 11px; color: #6b7280; font-style: italic; margin-left: 8px;'>↳ {note}</div>"
                if note
                else ""
            )

            rows_html += f"""
            <tr>
                <td style='padding: 3px 0; vertical-align: top; width: 42%;'>
                    <span style='font-weight: 500;'>{idx}. {name}</span>
                    {note_html}
                </td>
                <td style='padding: 3px 0; text-align: center; vertical-align: top; width: 12%;'>{qty}</td>
                <td style='padding: 3px 0; text-align: right; vertical-align: top; width: 22%; padding-right: 6px;'>{format_currency(price)}</td>
                <td style='padding: 3px 0; text-align: right; vertical-align: top; width: 24%; font-weight: bold;'>{format_currency(subtotal)}</td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset='utf-8'>
        <style>
            body {{
                font-family: 'Manrope', 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                color: #1f2937;
                background-color: #ffffff;
                margin: 0;
                padding: 10px;
                line-height: 1.4;
            }}
            .text-center {{ text-align: center; }}
            .text-right {{ text-align: right; }}
            .bold {{ font-weight: bold; }}
            .divider {{
                border-top: 1px dashed #9ca3af;
                margin: 8px 0;
            }}
            .header-title {{
                font-size: 16px;
                font-weight: bold;
                color: {COLOR['navy']};
                letter-spacing: 0.5px;
            }}
            .invoice-title {{
                font-size: 15px;
                font-weight: bold;
                color: {COLOR['navy']};
                margin: 6px 0 2px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 6px 0;
            }}
            th {{
                border-bottom: 1px solid #d1d5db;
                padding-bottom: 4px;
                font-size: 12px;
                color: #4b5563;
            }}
            .summary-row {{
                display: flex;
                justify-content: space-between;
                margin: 3px 0;
            }}
            .total-row {{
                font-size: 15px;
                font-weight: bold;
                color: {COLOR['navy']};
                margin-top: 4px;
                padding-top: 4px;
                border-top: 1px solid #1f2937;
            }}
            .footer {{
                text-align: center;
                font-size: 11px;
                color: #6b7280;
                margin-top: 12px;
            }}
        </style>
        </head>
        <body>
            <div class='text-center'>
                <div class='header-title'>{t('receipt_header_title')}</div>
                <div style='font-size: 12px; font-weight: 500; color: #4b5563;'>{t('receipt_header_sub')}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t('receipt_header_address')}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t('receipt_header_hotline')}</div>
            </div>

            <div class='divider'></div>

            <div class='text-center'>
                <div class='invoice-title'>{t('receipt_title').upper()}</div>
                <div style='font-size: 12px; color: #374151;'>{t('receipt_invoice_code')}: <span class='bold'>{self.invoice_code}</span></div>
            </div>

            <div style='margin-top: 6px; font-size: 12px;'>
                <div>• {t('receipt_table')}: <span class='bold'>{self.table_name}</span></div>
                <div>• {t('receipt_cashier')}: <span class='bold'>{self.cashier_name}</span></div>
                <div>• {t('receipt_date')}: {self.created_at}</div>
            </div>

            <div class='divider'></div>

            <table>
                <thead>
                    <tr>
                        <th style='text-align: left; width: 42%;'>Món</th>
                        <th style='text-align: center; width: 12%;'>SL</th>
                        <th style='text-align: right; width: 22%; padding-right: 6px;'>Đơn giá</th>
                        <th style='text-align: right; width: 24%;'>T.Tiền</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <div class='divider'></div>

            <table style='width: 100%; font-size: 13px;'>
                <tr>
                    <td>{t('order_subtotal')}:</td>
                    <td class='text-right bold'>{format_currency(self.total_amount)}</td>
                </tr>
                <tr>
                    <td>{t('order_discount')}:</td>
                    <td class='text-right'>0 đ</td>
                </tr>
                <tr style='font-size: 15px; font-weight: bold; color: {COLOR['navy']};'>
                    <td style='padding-top: 6px; border-top: 1px solid #374151;'>{t('order_total').upper()}:</td>
                    <td class='text-right' style='padding-top: 6px; border-top: 1px solid #374151;'>{format_currency(self.total_amount)}</td>
                </tr>
                <tr>
                    <td style='padding-top: 6px;'>{t('checkout_payment_method')}:</td>
                    <td class='text-right bold' style='padding-top: 6px;'>{pm_text}</td>
                </tr>
                <tr>
                    <td>{t('checkout_customer_pay')}:</td>
                    <td class='text-right'>{format_currency(self.received_amount)}</td>
                </tr>
                <tr>
                    <td>{t('checkout_change')}:</td>
                    <td class='text-right bold' style='color: {COLOR['success']};'>{format_currency(self.change_amount)}</td>
                </tr>
            </table>

            <div class='divider'></div>

            <div class='footer'>
                <div class='bold' style='font-size: 12px; color: {COLOR['navy']};'>{t('receipt_thank_you')}</div>
                <div style='margin-top: 4px;'>{t('receipt_wifi')}</div>
                <div style='margin-top: 2px; font-style: italic;'>Hệ thống quản lý Café TLU — Nhóm 5 BTL Python 2026</div>
            </div>
        </body>
        </html>
        """
        return html

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"])
        layout.setSpacing(SPACE["sm"])

        # Khung giấy in nhiệt (Thermal Paper Preview Container)
        paper_card = QFrame(self)
        paper_card.setStyleSheet(
            f"background-color: #ffffff; border: 1px solid {COLOR['border']}; "
            f"border-radius: {RADIUS['md']}px;"
        )
        paper_layout = QVBoxLayout(paper_card)
        paper_layout.setContentsMargins(SPACE["xs"], SPACE["xs"], SPACE["xs"], SPACE["xs"])

        self._text_browser = QTextBrowser(paper_card)
        self._text_browser.setOpenExternalLinks(False)
        self._text_browser.setStyleSheet("border: none; background: transparent;")
        self._text_browser.setHtml(self._generate_html())
        paper_layout.addWidget(self._text_browser)

        layout.addWidget(paper_card, stretch=1)

        # Thanh nút hành động (In / Xuất PDF / Đóng)
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(SPACE["sm"])

        self._print_btn = QPushButton(t("receipt_btn_print"), self)
        self._print_btn.setFixedHeight(36)
        self._print_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR['navy']}; color: {COLOR['surface']}; "
            f"font-weight: bold; border-radius: {RADIUS['sm']}px; padding: 0 {SPACE['md']}px; }}"
            f"QPushButton:hover {{ background-color: {COLOR['navy_600']}; }}"
        )
        self._print_btn.clicked.connect(self._handle_print)

        self._pdf_btn = QPushButton(t("receipt_btn_pdf"), self)
        self._pdf_btn.setProperty("variant", "secondary")
        self._pdf_btn.setFixedHeight(36)
        self._pdf_btn.clicked.connect(self._handle_export_pdf)

        self._close_btn = QPushButton("Đóng", self)
        self._close_btn.setProperty("variant", "secondary")
        self._close_btn.setFixedHeight(36)
        self._close_btn.clicked.connect(self.accept)

        btn_bar.addWidget(self._print_btn)
        btn_bar.addWidget(self._pdf_btn)
        btn_bar.addStretch()
        btn_bar.addWidget(self._close_btn)

        layout.addLayout(btn_bar)

    def _handle_print(self) -> None:
        """Gửi lệnh in ra máy in hệ thống qua QPrinter & QPrintDialog."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle(t("receipt_btn_print"))
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            doc = QTextDocument()
            doc.setHtml(self._generate_html())
            doc.print_(printer)
            QMessageBox.information(
                self,
                t("receipt_title"),
                t("receipt_print_success"),
            )

    def _handle_export_pdf(self) -> None:
        """Xuất hoá đơn ra định dạng file PDF."""
        default_filename = f"HoaDon_{self.invoice_code}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t("receipt_btn_pdf"),
            default_filename,
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        if not file_path.endswith(".pdf"):
            file_path += ".pdf"

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)

        doc = QTextDocument()
        doc.setHtml(self._generate_html())
        doc.print_(printer)

        QMessageBox.information(
            self,
            t("receipt_title"),
            t("receipt_export_pdf_success", path=file_path),
        )
