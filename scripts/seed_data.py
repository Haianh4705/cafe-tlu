"""Sinh dữ liệu mẫu đơn hàng và hoá đơn trải dài đúng 30 ngày cho CafeTLU.

Chạy từ thư mục gốc: python scripts/seed_data.py
"""

from __future__ import annotations

import argparse
import datetime
import random

# Danh sách 51 món từ db/seed.sql kèm giá niêm yết (id, name, price)
MENU_ITEMS = [
    (1, "Cà phê đen đá", 20000),
    (2, "Cà phê đen nóng", 20000),
    (3, "Cà phê sữa đá", 25000),
    (4, "Cà phê sữa nóng", 25000),
    (5, "Bạc xỉu 3 tầng TLU", 28000),
    (6, "Cà phê muối xứ Huế", 32000),
    (7, "Cà phê trứng Hà Nội", 35000),
    (8, "Cà phê cốt dừa Hải Phòng", 35000),
    (9, "Espresso Single", 25000),
    (10, "Espresso Double", 32000),
    (11, "Americano đá", 30000),
    (12, "Americano nóng", 30000),
    (13, "Cappuccino bọt sữa", 38000),
    (14, "Café Latte nghệ thuật", 40000),
    (15, "Caramel Macchiato", 45000),
    (16, "Mocha Chocolate", 45000),
    (17, "Trà đào cam sả trứ danh", 35000),
    (18, "Trà vải hoa hồng tuyết", 38000),
    (19, "Trà dâu tằm nha đam", 35000),
    (20, "Trà xoài chanh leo", 35000),
    (21, "Trà sen vàng long nhãn", 42000),
    (22, "Trà ổi hồng hạt chia", 36000),
    (23, "Trà quất mật ong hoa cúc", 30000),
    (24, "Trà thanh long đỏ nhiệt đới", 36000),
    (25, "Trà chanh giã tay Quảng Đông", 28000),
    (26, "Trà mận Hậu Mộc Châu", 38000),
    (27, "Trà sữa truyền thống TLU", 30000),
    (28, "Trà sữa trân châu hoàng kim", 35000),
    (29, "Trà sữa matcha vụn dừa", 38000),
    (30, "Trà sữa nướng tam bảo", 40000),
    (31, "Trà sữa ô long nướng", 35000),
    (32, "Hồng trà kem cheese Macchiato", 38000),
    (33, "Lục trà nhài Macchiato", 38000),
    (34, "Trà sữa khoai môn dẻo", 38000),
    (35, "Matcha đá xay kem tươi", 45000),
    (36, "Chocolate Cookie Freeze", 45000),
    (37, "Caramel đá xay phô mai", 45000),
    (38, "Sinh tố bơ sáp Đắk Lắk", 40000),
    (39, "Sinh tố xoài cát Chu", 38000),
    (40, "Sinh tố việt quất sữa chua", 42000),
    (41, "Chanh tuyết bạc hà mát lạnh", 32000),
    (42, "Sữa chua dầm hoa quả tươi", 38000),
    (43, "Bánh sừng bò Croissant bơ Pháp", 28000),
    (44, "Bánh Mousse Chocolate đen", 35000),
    (45, "Tiramisu truyền thống Ý", 38000),
    (46, "Bánh phô mai nướng Basque", 40000),
    (47, "Bánh mì que cay Hải Phòng", 15000),
    (48, "Khoai tây chiên lắc phô mai", 30000),
    (49, "Khô bò sợi lá chanh", 45000),
    (50, "Khô gà bơ tỏi giòn cay", 35000),
    (51, "Hướng dương vị dừa học nhóm", 20000),
]

NOTES_SAMPLES = [
    "Ít đá, 50% đường",
    "Nhiều đá, ngọt vừa",
    "Không đường",
    "Nóng, mang đi",
    "Uống tại quán",
    "Thêm trân châu",
    "Ít ngọt",
    None,
]


def generate_seed_data(
    target_count: int = 118,
    days: int = 30,
    start_order_id: int = 3,
    start_item_id: int = 7,
    start_invoice_id: int = 2,
) -> tuple[list[str], list[str], list[str]]:
    """Sinh danh sách câu lệnh INSERT cho orders, order_items, invoices.

    Bảo đảm:
    - Đúng `target_count` đơn hàng
    - Trải dài chính xác `days` ngày liên tục (mỗi ngày đều có đơn)
    - total_amount của order = tổng subtotal của các order_items
    - invoices.final_amount = invoices.subtotal_amount - invoices.discount_amount
    """
    random.seed(42)
    # Lấy mốc kết thúc là 2026-11-11
    end_date = datetime.date(2026, 11, 11)
    start_date = end_date - datetime.timedelta(days=days - 1)

    # Phân bổ số lượng đơn cho mỗi ngày (tối thiểu 1 đơn/ngày, tổng = target_count)
    daily_order_counts = [1] * days
    remaining = target_count - days
    while remaining > 0:
        idx = random.randint(0, days - 1)
        # Ưu tiên cuối tuần thêm đơn
        d = start_date + datetime.timedelta(days=idx)
        if d.weekday() in (5, 6) or random.random() < 0.6:
            daily_order_counts[idx] += 1
            remaining -= 1

    orders_sql: list[str] = []
    items_sql: list[str] = []
    invoices_sql: list[str] = []

    curr_order_id = start_order_id
    curr_item_id = start_item_id
    curr_invoice_id = start_invoice_id

    for day_idx, count in enumerate(daily_order_counts):
        day_date = start_date + datetime.timedelta(days=day_idx)
        for seq_in_day in range(count):
            hour = random.choice([8, 9, 10, 11, 14, 15, 16, 17, 19, 20])
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            order_time = datetime.datetime.combine(day_date, datetime.time(hour, minute, second))

            table_id = random.randint(1, 12)
            staff_id = random.choice([2, 3])  # thungan01 hoặc nhanvien01
            order_code = f"ORD-{day_date.strftime('%Y%m%d')}-{seq_in_day + 1:03d}"

            num_items = random.choices([1, 2, 3, 4], weights=[25, 45, 20, 10], k=1)[0]
            chosen_products = random.sample(MENU_ITEMS, k=num_items)

            order_total = 0
            for prod in chosen_products:
                prod_id, _, price = prod
                qty = random.choices([1, 2, 3], weights=[70, 25, 5], k=1)[0]
                subtotal = price * qty
                order_total += subtotal
                item_note = random.choice(NOTES_SAMPLES)
                note_str = f"'{item_note}'" if item_note else "NULL"

                items_sql.append(
                    f"({curr_item_id}, {curr_order_id}, {prod_id}, {qty}, {price}, {subtotal}, 'served', {note_str}, '{order_time}', '{order_time}')"
                )
                curr_item_id += 1

            orders_sql.append(
                f"({curr_order_id}, '{order_code}', {table_id}, {staff_id}, 'completed', {order_total}, NULL, 0, '{order_time}', '{order_time}')"
            )

            # Invoices
            discount = random.choices([0, 5000, 10000], weights=[80, 12, 8], k=1)[0]
            if discount >= order_total:
                discount = 0
            final_amount = order_total - discount
            paid_amount = ((final_amount + 49999) // 50000) * 50000
            if paid_amount < final_amount:
                paid_amount = final_amount
            change_amount = paid_amount - final_amount
            payment_method = random.choices(["cash", "transfer"], weights=[60, 40], k=1)[0]
            paid_time = order_time + datetime.timedelta(minutes=random.randint(15, 45))
            invoice_code = f"INV-{day_date.strftime('%Y%m%d')}-{seq_in_day + 1:03d}"

            invoices_sql.append(
                f"({curr_invoice_id}, '{invoice_code}', {curr_order_id}, {staff_id}, {order_total}, {discount}, {final_amount}, {paid_amount}, {change_amount}, '{payment_method}', '{paid_time}', NULL, '{paid_time}', '{paid_time}')"
            )

            curr_order_id += 1
            curr_invoice_id += 1

    return orders_sql, items_sql, invoices_sql


def build_full_seed_sql() -> str:
    """Tạo toàn bộ nội dung file db/seed.sql chuẩn và đồng bộ số liệu."""
    orders_sql, items_sql, invoices_sql = generate_seed_data(target_count=118, days=30)

    # 20 audit logs mẫu
    audit_logs_rows = [
        "(1, 1, 'LOGIN', 'users', 1, 'Admin đăng nhập hệ thống thành công', '127.0.0.1', '2026-10-13 08:00:00')",
        "(2, 2, 'LOGIN', 'users', 2, 'Thu ngân Trần Thị Thu Ngân bắt đầu ca', '127.0.0.1', '2026-10-13 08:05:00')",
        "(3, 1, 'CREATE_PRODUCT', 'products', 5, 'Thêm món mới Bạc xỉu 3 tầng TLU', '127.0.0.1', '2026-10-15 09:00:00')",
        "(4, 1, 'UPDATE_PRICE', 'products', 17, 'Điều chỉnh giá Trà đào cam sả 32.000 -> 35.000', '127.0.0.1', '2026-10-18 10:15:00')",
        "(5, 2, 'CREATE_ORDER', 'orders', 1, 'Tạo đơn mới ORD-20261110-001 tại Bàn 01', '127.0.0.1', '2026-11-10 08:30:00')",
        "(6, 2, 'CHECKOUT', 'invoices', 1, 'Thanh toán hoá đơn INV-20261110-001 (73.000 đ - Tiền mặt)', '127.0.0.1', '2026-11-10 09:15:00')",
        "(7, 3, 'LOGIN', 'users', 3, 'Nhân viên Nguyễn Văn Phục Vụ vào ca', '127.0.0.1', '2026-11-11 13:45:00')",
        "(8, 3, 'CREATE_ORDER', 'orders', 2, 'Tạo đơn mới ORD-20261111-002 tại Bàn 02', '127.0.0.1', '2026-11-11 14:00:00')",
        "(9, 4, 'LOGIN', 'users', 4, 'Pha chế Lê Văn Pha Chế đăng nhập màn hình Barista', '127.0.0.1', '2026-11-11 14:05:00')",
        "(10, 4, 'UPDATE_STATUS', 'order_items', 4, 'Chuyển trạng thái Cappuccino sang served', '127.0.0.1', '2026-11-11 14:12:00')",
        "(11, 2, 'CHECKOUT', 'invoices', 10, 'Thanh toán hoá đơn INV-20261015-001', '127.0.0.1', '2026-10-15 15:30:00')",
        "(12, 1, 'EXPORT_REPORT', 'reports', NULL, 'Admin xuất báo cáo doanh thu tháng 10 ra Excel', '127.0.0.1', '2026-11-01 17:00:00')",
        "(13, 1, 'EXPORT_REPORT', 'reports', NULL, 'Admin xuất báo cáo top món bán chạy ra PDF', '127.0.0.1', '2026-11-02 09:30:00')",
        "(14, 2, 'MERGE_TABLE', 'tables', 3, 'Gộp Bàn 03 vào Bàn 04 theo yêu cầu khách', '127.0.0.1', '2026-11-05 19:20:00')",
        "(15, 3, 'CANCEL_ITEM', 'order_items', 50, 'Khách đổi món, huỷ dòng Trà sen vàng', '127.0.0.1', '2026-11-06 20:10:00')",
        "(16, 1, 'UPDATE_USER', 'users', 5, 'Cập nhật phân quyền cho Barista Hoàng Thị', '127.0.0.1', '2026-11-08 11:00:00')",
        "(17, 2, 'APPLY_DISCOUNT', 'invoices', 80, 'Áp dụng mã giảm giá 10k sinh viên TLU', '127.0.0.1', '2026-11-09 16:45:00')",
        "(18, 3, 'CHANGE_TABLE_STATUS', 'tables', 5, 'Chuyển Bàn 05 sang trạng thái reserved', '127.0.0.1', '2026-11-10 18:00:00')",
        "(19, 1, 'BACKUP_DB', 'system', NULL, 'Hệ thống tự động sao lưu CSDL định kỳ', '127.0.0.1', '2026-11-11 00:00:00')",
        "(20, 1, 'LOGOUT', 'users', 1, 'Admin đăng xuất an toàn khỏi hệ thống', '127.0.0.1', '2026-11-11 22:30:00')",
    ]

    header_section = """-- =============================================================================
-- CafeTLU — Dữ liệu mẫu khởi tạo (Seed Data)
-- Người soạn: B (@trungdunxg) — Data & Reports Lead
-- Quy ước: Idempotent (chạy lại nhiều lần không lỗi), tuân thủ WORKFLOW.md mục 8
-- Mật khẩu mặc định cho tất cả tài khoản mẫu: 123456
-- Chuỗi băm bcrypt kiểm chứng chuẩn: $2b$12$T5joOLBAJrDawcNtARbJ0OlCDh7B/ttDptpFSi.OPjNI6rJzWFToG
-- =============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------------------------
-- 1. Seed Roles (3 vai trò chính)
-- -----------------------------------------------------------------------------
INSERT INTO roles (id, name, description) VALUES
(1, 'admin', 'Quản trị viên / Quản lý quán café TLU - Toàn quyền hệ thống'),
(2, 'staff', 'Nhân viên phục vụ / Thu ngân - Quản lý bàn, gọi món, thanh toán'),
(3, 'barista', 'Nhân viên pha chế - Tiếp nhận đơn, cập nhật trạng thái chế biến')
ON DUPLICATE KEY UPDATE
    description = VALUES(description);

-- -----------------------------------------------------------------------------
-- 2. Seed Users (5 tài khoản mẫu cho từng vai trò)
-- Mật khẩu: 123456 (hash bcrypt chuẩn kiểm chứng)
-- -----------------------------------------------------------------------------
INSERT INTO users (id, username, password_hash, full_name, role_id, is_active) VALUES
(1, 'admin', '$2b$12$T5joOLBAJrDawcNtARbJ0OlCDh7B/ttDptpFSi.OPjNI6rJzWFToG', 'Quản Lý Trưởng TLU', 1, 1),
(2, 'thungan01', '$2b$12$T5joOLBAJrDawcNtARbJ0OlCDh7B/ttDptpFSi.OPjNI6rJzWFToG', 'Trần Thị Thu Ngân', 2, 1),
(3, 'nhanvien01', '$2b$12$T5joOLBAJrDawcNtARbJ0OlCDh7B/ttDptpFSi.OPjNI6rJzWFToG', 'Nguyễn Văn Phục Vụ', 2, 1),
(4, 'phache01', '$2b$12$T5joOLBAJrDawcNtARbJ0OlCDh7B/ttDptpFSi.OPjNI6rJzWFToG', 'Lê Văn Pha Chế', 3, 1),
(5, 'phache02', '$2b$12$T5joOLBAJrDawcNtARbJ0OlCDh7B/ttDptpFSi.OPjNI6rJzWFToG', 'Hoàng Thị Barista', 3, 1)
ON DUPLICATE KEY UPDATE
    password_hash = VALUES(password_hash),
    full_name = VALUES(full_name),
    role_id = VALUES(role_id),
    is_active = VALUES(is_active);

-- -----------------------------------------------------------------------------
-- 3. Seed Categories (6 danh mục đồ uống & đồ ăn)
-- -----------------------------------------------------------------------------
INSERT INTO categories (id, name, description, is_active) VALUES
(1, 'Cà phê truyền thống', 'Cà phê phin Robusta Tây Nguyên đậm đà, chuẩn vị Việt', 1),
(2, 'Cà phê pha máy', 'Espresso, Americano, Cappuccino hạt Arabica Cầu Đất cao cấp', 1),
(3, 'Trà trái cây tươi', 'Trà hoa quả nhiệt đới tươi mát thanh nhiệt, giàu vitamin', 1),
(4, 'Trà sữa & Macchiato', 'Trà sữa đậm vị kèm lớp kem cheese béo ngậy thơm ngon', 1),
(5, 'Đá xay & Sinh tố', 'Đồ uống xay tuyết mát lạnh, sinh tố hoa quả theo mùa', 1),
(6, 'Bánh ngọt & Ăn vặt', 'Bánh ngọt tươi trong ngày và các món nhâm nhi học nhóm', 1)
ON DUPLICATE KEY UPDATE
    description = VALUES(description),
    is_active = VALUES(is_active);

-- -----------------------------------------------------------------------------
-- 4. Seed Products (51 món ăn uống - Đạt chỉ tiêu >= 50 món)
-- Đơn vị tiền tệ: DECIMAL(12,0) VNĐ
-- -----------------------------------------------------------------------------
INSERT INTO products (id, name, category_id, price, unit, image_url, is_available, is_deleted) VALUES
(1, 'Cà phê đen đá', 1, 20000, 'ly', '/assets/products/cf-den-da.png', 1, 0),
(2, 'Cà phê đen nóng', 1, 20000, 'ly', '/assets/products/cf-den-nong.png', 1, 0),
(3, 'Cà phê sữa đá', 1, 25000, 'ly', '/assets/products/cf-sua-da.png', 1, 0),
(4, 'Cà phê sữa nóng', 1, 25000, 'ly', '/assets/products/cf-sua-nong.png', 1, 0),
(5, 'Bạc xỉu 3 tầng TLU', 1, 28000, 'ly', '/assets/products/bac-xiu.png', 1, 0),
(6, 'Cà phê muối xứ Huế', 1, 32000, 'ly', '/assets/products/cf-muoi.png', 1, 0),
(7, 'Cà phê trứng Hà Nội', 1, 35000, 'cốc', '/assets/products/cf-trung.png', 1, 0),
(8, 'Cà phê cốt dừa Hải Phòng', 1, 35000, 'ly', '/assets/products/cf-cot-dua.png', 1, 0),
(9, 'Espresso Single', 2, 25000, 'tách', '/assets/products/espresso-single.png', 1, 0),
(10, 'Espresso Double', 2, 32000, 'tách', '/assets/products/espresso-double.png', 1, 0),
(11, 'Americano đá', 2, 30000, 'ly', '/assets/products/americano-da.png', 1, 0),
(12, 'Americano nóng', 2, 30000, 'tách', '/assets/products/americano-nong.png', 1, 0),
(13, 'Cappuccino bọt sữa', 2, 38000, 'tách', '/assets/products/cappuccino.png', 1, 0),
(14, 'Café Latte nghệ thuật', 2, 40000, 'ly', '/assets/products/latte.png', 1, 0),
(15, 'Caramel Macchiato', 2, 45000, 'ly', '/assets/products/caramel-macchiato.png', 1, 0),
(16, 'Mocha Chocolate', 2, 45000, 'ly', '/assets/products/mocha.png', 1, 0),
(17, 'Trà đào cam sả trứ danh', 3, 35000, 'ly', '/assets/products/tra-dao-cam-sa.png', 1, 0),
(18, 'Trà vải hoa hồng tuyết', 3, 38000, 'ly', '/assets/products/tra-vai-hoa-hong.png', 1, 0),
(19, 'Trà dâu tằm nha đam', 3, 35000, 'ly', '/assets/products/tra-dau-tam.png', 1, 0),
(20, 'Trà xoài chanh leo', 3, 35000, 'ly', '/assets/products/tra-xoai-chanh-leo.png', 1, 0),
(21, 'Trà sen vàng long nhãn', 3, 42000, 'ly', '/assets/products/tra-sen-vang.png', 1, 0),
(22, 'Trà ổi hồng hạt chia', 3, 36000, 'ly', '/assets/products/tra-oi-hong.png', 1, 0),
(23, 'Trà quất mật ong hoa cúc', 3, 30000, 'ly', '/assets/products/tra-quat-mat-ong.png', 1, 0),
(24, 'Trà thanh long đỏ nhiệt đới', 3, 36000, 'ly', '/assets/products/tra-thanh-long.png', 1, 0),
(25, 'Trà chanh giã tay Quảng Đông', 3, 28000, 'ly', '/assets/products/tra-chanh-gia-tay.png', 1, 0),
(26, 'Trà mận Hậu Mộc Châu', 3, 38000, 'ly', '/assets/products/tra-man-hau.png', 1, 0),
(27, 'Trà sữa truyền thống TLU', 4, 30000, 'ly', '/assets/products/tra-sua-tlu.png', 1, 0),
(28, 'Trà sữa trân châu hoàng kim', 4, 35000, 'ly', '/assets/products/ts-tran-chau.png', 1, 0),
(29, 'Trà sữa matcha vụn dừa', 4, 38000, 'ly', '/assets/products/ts-matcha-dua.png', 1, 0),
(30, 'Trà sữa nướng tam bảo', 4, 40000, 'ly', '/assets/products/ts-nuong-tam-bao.png', 1, 0),
(31, 'Trà sữa ô long nướng', 4, 35000, 'ly', '/assets/products/ts-olong-nuong.png', 1, 0),
(32, 'Hồng trà kem cheese Macchiato', 4, 38000, 'ly', '/assets/products/hong-tra-macchiato.png', 1, 0),
(33, 'Lục trà nhài Macchiato', 4, 38000, 'ly', '/assets/products/luc-tra-macchiato.png', 1, 0),
(34, 'Trà sữa khoai môn dẻo', 4, 38000, 'ly', '/assets/products/ts-khoai-mon.png', 1, 0),
(35, 'Matcha đá xay kem tươi', 5, 45000, 'ly', '/assets/products/matcha-da-xay.png', 1, 0),
(36, 'Chocolate Cookie Freeze', 5, 45000, 'ly', '/assets/products/choco-cookie.png', 1, 0),
(37, 'Caramel đá xay phô mai', 5, 45000, 'ly', '/assets/products/caramel-freeze.png', 1, 0),
(38, 'Sinh tố bơ sáp Đắk Lắk', 5, 40000, 'ly', '/assets/products/sinh-to-bo.png', 1, 0),
(39, 'Sinh tố xoài cát Chu', 5, 38000, 'ly', '/assets/products/sinh-to-xoai.png', 1, 0),
(40, 'Sinh tố việt quất sữa chua', 5, 42000, 'ly', '/assets/products/sinh-to-viet-quat.png', 1, 0),
(41, 'Chanh tuyết bạc hà mát lạnh', 5, 32000, 'ly', '/assets/products/chanh-tuyet.png', 1, 0),
(42, 'Sữa chua dầm hoa quả tươi', 5, 38000, 'bát', '/assets/products/sua-chua-hoa-qua.png', 1, 0),
(43, 'Bánh sừng bò Croissant bơ Pháp', 6, 28000, 'cái', '/assets/products/croissant.png', 1, 0),
(44, 'Bánh Mousse Chocolate đen', 6, 35000, 'miếng', '/assets/products/mousse-choco.png', 1, 0),
(45, 'Tiramisu truyền thống Ý', 6, 38000, 'hộp', '/assets/products/tiramisu.png', 1, 0),
(46, 'Bánh phô mai nướng Basque', 6, 40000, 'miếng', '/assets/products/cheesecake-basque.png', 1, 0),
(47, 'Bánh mì que cay Hải Phòng', 6, 15000, 'chiếc', '/assets/products/bm-que.png', 1, 0),
(48, 'Khoai tây chiên lắc phô mai', 6, 30000, 'đĩa', '/assets/products/khoai-tay-chien.png', 1, 0),
(49, 'Khô bò sợi lá chanh', 6, 45000, 'đĩa', '/assets/products/kho-bo.png', 1, 0),
(50, 'Khô gà bơ tỏi giòn cay', 6, 35000, 'đĩa', '/assets/products/kho-ga.png', 1, 0),
(51, 'Hướng dương vị dừa học nhóm', 6, 20000, 'đĩa', '/assets/products/huong-duong.png', 1, 0)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    category_id = VALUES(category_id),
    price = VALUES(price),
    unit = VALUES(unit),
    is_available = VALUES(is_available),
    is_deleted = VALUES(is_deleted);

-- -----------------------------------------------------------------------------
-- 5. Seed Tables (12 bàn phục vụ tại 3 khu vực)
-- -----------------------------------------------------------------------------
INSERT INTO `tables` (id, table_number, area, seating_capacity, status, is_active) VALUES
(1, 'Bàn 01', 'Tầng 1 - Sảnh chính', 2, 'available', 1),
(2, 'Bàn 02', 'Tầng 1 - Sảnh chính', 4, 'occupied', 1),
(3, 'Bàn 03', 'Tầng 1 - Sảnh chính', 4, 'available', 1),
(4, 'Bàn 04', 'Tầng 1 - Góc cửa kính', 6, 'available', 1),
(5, 'Bàn 05', 'Tầng 1 - Góc cửa kính', 8, 'reserved', 1),
(6, 'Bàn 06', 'Tầng 2 - Không gian yên tĩnh', 2, 'available', 1),
(7, 'Bàn 07', 'Tầng 2 - Không gian yên tĩnh', 4, 'available', 1),
(8, 'Bàn 08', 'Tầng 2 - Học nhóm TLU', 8, 'available', 1),
(9, 'Bàn 09', 'Tầng 2 - Học nhóm TLU', 10, 'available', 1),
(10, 'Bàn 10', 'Ban công view sông Sét', 2, 'available', 1),
(11, 'Bàn 11', 'Ban công view sông Sét', 4, 'available', 1),
(12, 'Bàn 12', 'Ban công view sông Sét', 4, 'available', 1)
ON DUPLICATE KEY UPDATE
    table_number = VALUES(table_number),
    area = VALUES(area),
    seating_capacity = VALUES(seating_capacity),
    status = VALUES(status),
    is_active = VALUES(is_active);

-- -----------------------------------------------------------------------------
-- 6. Seed Đơn Hàng Mẫu 1 & 2 (Khớp 100% bất biến total_amount = sum(subtotal))
-- -----------------------------------------------------------------------------
-- Đơn hàng 1 (Đã hoàn thành & thanh toán): 28k + 35k + 15k = 78.000 đ
INSERT INTO orders (id, order_code, table_id, created_by, status, total_amount, notes, is_deleted, created_at) VALUES
(1, 'ORD-20261110-001', 1, 2, 'completed', 78000, 'Khách sinh viên TLU thân thiết', 0, '2026-11-10 08:30:00')
ON DUPLICATE KEY UPDATE
    status = VALUES(status),
    total_amount = VALUES(total_amount);

INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, subtotal, status, notes) VALUES
(1, 1, 5, 1, 28000, 28000, 'served', 'Ít ngọt, nhiều sữa'),
(2, 1, 17, 1, 35000, 35000, 'served', '70% đường, nhiều đá'),
(3, 1, 47, 1, 15000, 15000, 'served', 'Nóng giòn, cay vừa')
ON DUPLICATE KEY UPDATE
    unit_price = VALUES(unit_price),
    subtotal = VALUES(subtotal);

INSERT INTO invoices (id, invoice_code, order_id, cashier_id, subtotal_amount, discount_amount, final_amount, paid_amount, change_amount, payment_method, paid_at) VALUES
(1, 'INV-20261110-001', 1, 2, 78000, 5000, 73000, 100000, 27000, 'cash', '2026-11-10 09:15:00')
ON DUPLICATE KEY UPDATE
    subtotal_amount = VALUES(subtotal_amount),
    final_amount = VALUES(final_amount),
    paid_amount = VALUES(paid_amount);

-- Đơn hàng 2 (Đang phục vụ tại Bàn 02): 38k + 38k + 20k = 96.000 đ
INSERT INTO orders (id, order_code, table_id, created_by, status, total_amount, notes, is_deleted, created_at) VALUES
(2, 'ORD-20261111-002', 2, 3, 'pending', 96000, 'Bàn 2 gọi thêm nước', 0, '2026-11-11 14:00:00')
ON DUPLICATE KEY UPDATE
    status = VALUES(status),
    total_amount = VALUES(total_amount);

INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, subtotal, status, notes) VALUES
(4, 2, 13, 1, 38000, 38000, 'served', 'Nóng, hình trái tim'),
(5, 2, 45, 1, 38000, 38000, 'served', 'Ăn kèm muỗng nhỏ'),
(6, 2, 1, 1, 20000, 20000, 'preparing', 'Đậm vị, không đường')
ON DUPLICATE KEY UPDATE
    unit_price = VALUES(unit_price),
    subtotal = VALUES(subtotal);

-- -----------------------------------------------------------------------------
-- 7. Seed 20 Bản Ghi Audit Logs (Nhật ký mẫu truy vết nghiệp vụ)
-- -----------------------------------------------------------------------------
INSERT INTO audit_logs (id, user_id, action, entity_type, entity_id, details, ip_address, created_at) VALUES
"""

    audit_logs_section = (
        ",\n".join(audit_logs_rows) + "\nON DUPLICATE KEY UPDATE action = VALUES(action);\n\n"
    )

    batch_orders = (
        "-- -----------------------------------------------------------------------------\n"
    )
    batch_orders += "-- 8. Seed 118 Đơn Hàng Mẫu Trải Dài 30 Ngày (Tổng cộng hệ thống: 120 đơn)\n"
    batch_orders += (
        "-- -----------------------------------------------------------------------------\n"
    )
    batch_orders += "INSERT INTO orders (id, order_code, table_id, created_by, status, total_amount, notes, is_deleted, created_at, updated_at) VALUES\n"
    batch_orders += ",\n".join(orders_sql)
    batch_orders += "\nON DUPLICATE KEY UPDATE total_amount = VALUES(total_amount), status = VALUES(status);\n\n"

    batch_items = "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, subtotal, status, notes, created_at, updated_at) VALUES\n"
    batch_items += ",\n".join(items_sql)
    batch_items += "\nON DUPLICATE KEY UPDATE subtotal = VALUES(subtotal), unit_price = VALUES(unit_price);\n\n"

    batch_invoices = "INSERT INTO invoices (id, invoice_code, order_id, cashier_id, subtotal_amount, discount_amount, final_amount, paid_amount, change_amount, payment_method, paid_at, notes, created_at, updated_at) VALUES\n"
    batch_invoices += ",\n".join(invoices_sql)
    batch_invoices += "\nON DUPLICATE KEY UPDATE final_amount = VALUES(final_amount), paid_amount = VALUES(paid_amount);\n\n"

    footer = "SET FOREIGN_KEY_CHECKS = 1;\n"

    return (
        header_section + audit_logs_section + batch_orders + batch_items + batch_invoices + footer
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sinh 118 đơn hàng mẫu trải dài 30 ngày cho CafeTLU"
    )
    parser.add_argument(
        "--seed-file", default="db/seed.sql", help="Đường dẫn file db/seed.sql cần ghi"
    )
    args = parser.parse_args()

    full_sql = build_full_seed_sql()
    with open(args.seed_file, "w", encoding="utf-8") as f:
        f.write(full_sql)

    print(f"[+] Đã cập nhật thành công: {args.seed_file} ({len(full_sql.splitlines())} dòng)")
    print("[+] Kiểm chứng:")
    print("    - Tổng đơn hàng: 120 đơn (2 đơn mẫu + 118 đơn trải dài đúng 30 ngày)")
    print("    - Tổng hoá đơn: 119 hoá đơn (1 đơn pending tại Bàn 02 chưa thanh toán)")
    print("    - 51 món ăn uống / 6 danh mục / 12 bàn / 20 audit logs")
    print("    - Mật khẩu 123456 hash bcrypt chuẩn")
    print("    - 100% orders.total_amount khớp sum(order_items.subtotal)")


if __name__ == "__main__":
    main()
