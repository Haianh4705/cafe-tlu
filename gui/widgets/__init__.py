"""Gói chứa các widget dùng lại của CafeTLU."""

from gui.widgets.checkout_dialog import CheckoutDialog
from gui.widgets.order_cart import ConfirmCancelOrderDialog, OrderCartWidget
from gui.widgets.product_dialog import ConfirmDeleteDialog, ProductFormDialog
from gui.widgets.receipt_dialog import ReceiptDialog
from gui.widgets.table_card import TableCardWidget

__all__ = [
    "CheckoutDialog",
    "ConfirmCancelOrderDialog",
    "ConfirmDeleteDialog",
    "OrderCartWidget",
    "ProductFormDialog",
    "ReceiptDialog",
    "TableCardWidget",
]
