"""Sinh ~120 đơn hàng và hoá đơn mẫu trải dài 30 ngày cho CafeTLU.

Chạy từ thư mục gốc: python scripts/seed_data.py [--out db/seed_orders.sql]
"""

from __future__ import annotations

import argparse
import datetime
import os
import random
import sys

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


def generate_seed_sql(
    days: int = 30,
    total_target_orders: int = 120,
    start_order_id: int = 10,
    start_item_id: int = 20,
    start_invoice_id: int = 10,
) -> str:
    """Sinh chuỗi câu lệnh SQL cho ~120 đơn và hoá đơn trong 30 ngày."""
    random.seed(42)  # Giữ kết quả deterministic để kiểm chứng
    now = datetime.datetime.now().replace(microsecond=0)
    start_date = now - datetime.timedelta(days=days)

    lines: list[str] = [
        "-- =============================================================================",
        f"-- CafeTLU: Dữ liệu mẫu {total_target_orders} đơn hàng & hoá đơn trải dài {days} ngày",
        "-- Sinh tự động bởi scripts/seed_data.py — B (@trungdunxg)",
        "-- Bảo đảm: Tính bất biến, snapshot unit_price, khớp tổng tiền, idempotent",
        "-- =============================================================================",
        "SET NAMES utf8mb4;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "",
    ]

    orders_sql: list[str] = []
    items_sql: list[str] = []
    invoices_sql: list[str] = []

    current_order_id = start_order_id
    current_item_id = start_item_id
    current_invoice_id = start_invoice_id

    # Phân bổ đơn hàng qua từng ngày (trung bình 3-6 đơn/ngày)
    orders_per_day = max(1, total_target_orders // days)
    order_seq = 1

    for day_offset in range(days):
        current_day = start_date + datetime.timedelta(days=day_offset)
        # Cuối tuần đông khách hơn một chút
        is_weekend = current_day.weekday() in (5, 6)
        daily_count = orders_per_day + random.randint(1, 3 if is_weekend else 2)

        for _ in range(daily_count):
            if current_order_id - start_order_id >= total_target_orders:
                break

            # Chọn giờ thực tế: sáng 8-11h, chiều 14-17h, tối 19-21h
            hour_bucket = random.choices([8, 9, 10, 14, 15, 16, 19, 20], k=1)[0]
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            order_time = current_day.replace(hour=hour_bucket, minute=minute, second=second)

            table_id = random.randint(1, 12)
            staff_id = random.choice([2, 3])  # thungan01 hoặc nhanvien01
            order_code = f"ORD-{order_time.strftime('%Y%m%d')}-{order_seq:04d}"
            order_seq += 1

            # Sinh từ 1 đến 4 món cho mỗi đơn
            num_items = random.choices([1, 2, 3, 4], weights=[20, 45, 25, 10], k=1)[0]
            chosen_products = random.sample(MENU_ITEMS, k=num_items)

            order_total = 0
            for prod in chosen_products:
                prod_id, prod_name, price = prod
                qty = random.choices([1, 2, 3], weights=[70, 25, 5], k=1)[0]
                subtotal = price * qty
                order_total += subtotal
                item_note = random.choice(NOTES_SAMPLES)
                note_val = f"'{item_note}'" if item_note else "NULL"

                items_sql.append(
                    f"({current_item_id}, {current_order_id}, {prod_id}, {qty}, {price}, {subtotal}, 'served', {note_val}, '{order_time}', '{order_time}')"
                )
                current_item_id += 1

            # Đơn trong quá khứ đều là 'completed'
            orders_sql.append(
                f"({current_order_id}, '{order_code}', {table_id}, {staff_id}, 'completed', {order_total}, NULL, 0, '{order_time}', '{order_time}')"
            )

            # Hoá đơn tương ứng cho đơn completed
            # Chiết khấu thỉnh thoảng 0, 5.000đ hoặc 10.000đ
            discount = random.choices([0, 5000, 10000], weights=[75, 15, 10], k=1)[0]
            if discount > order_total:
                discount = 0
            final_amount = order_total - discount
            # Tiền khách đưa làm tròn 50k, 100k, 200k, 500k
            paid_amount = ((final_amount + 49999) // 50000) * 50000
            if paid_amount < final_amount:
                paid_amount = final_amount
            change_amount = paid_amount - final_amount
            payment_method = random.choices(["cash", "transfer"], weights=[60, 40], k=1)[0]
            paid_time = order_time + datetime.timedelta(minutes=random.randint(15, 60))
            invoice_code = f"INV-{order_time.strftime('%Y%m%d')}-{current_invoice_id:04d}"

            invoices_sql.append(
                f"({current_invoice_id}, '{invoice_code}', {current_order_id}, {staff_id}, {order_total}, {discount}, {final_amount}, {paid_amount}, {change_amount}, '{payment_method}', '{paid_time}', NULL, '{paid_time}', '{paid_time}')"
            )
            current_invoice_id += 1
            current_order_id += 1

    # Tạo batch INSERT với ON DUPLICATE KEY UPDATE
    lines.append("-- 1. Nạp danh sách đơn hàng")
    lines.append("INSERT INTO orders (id, order_code, table_id, created_by, status, total_amount, notes, is_deleted, created_at, updated_at) VALUES")
    lines.append(",\n".join(orders_sql))
    lines.append("ON DUPLICATE KEY UPDATE total_amount = VALUES(total_amount), status = VALUES(status);\n")

    lines.append("-- 2. Nạp chi tiết món của từng đơn (snapshot unit_price)")
    lines.append("INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, subtotal, status, notes, created_at, updated_at) VALUES")
    lines.append(",\n".join(items_sql))
    lines.append("ON DUPLICATE KEY UPDATE subtotal = VALUES(subtotal), unit_price = VALUES(unit_price);\n")

    lines.append("-- 3. Nạp hoá đơn tương ứng (khớp 100% doanh thu)")
    lines.append("INSERT INTO invoices (id, invoice_code, order_id, cashier_id, subtotal_amount, discount_amount, final_amount, paid_amount, change_amount, payment_method, paid_at, notes, created_at, updated_at) VALUES")
    lines.append(",\n".join(invoices_sql))
    lines.append("ON DUPLICATE KEY UPDATE final_amount = VALUES(final_amount), paid_amount = VALUES(paid_amount);\n")

    lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    lines.append(f"-- Hoàn tất sinh {len(orders_sql)} đơn hàng và {len(items_sql)} dòng món.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sinh ~120 đơn hàng mẫu trải dài 30 ngày cho CafeTLU")
    parser.add_argument("--out", default="db/seed_orders.sql", help="Đường dẫn file SQL đầu ra")
    parser.add_argument("--days", type=int, default=30, help="Số ngày trải dài dữ liệu (mặc định 30)")
    parser.add_argument("--count", type=int, default=120, help="Số đơn mục tiêu (mặc định 120)")
    args = parser.parse_args()

    print(f"[*] Đang sinh {args.count} đơn hàng mẫu trong {args.days} ngày gần nhất...")
    sql_content = generate_seed_sql(days=args.days, total_target_orders=args.count)

    out_path = args.out
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(sql_content)

    print(f"[+] Đã ghi dữ liệu vào: {out_path} ({len(sql_content.splitlines())} dòng)")
    print("[+] Dữ liệu bảo đảm: Total amount khớp chi tiết món, giá snapshot, không có sai số nhị phân.")


if __name__ == "__main__":
    main()
