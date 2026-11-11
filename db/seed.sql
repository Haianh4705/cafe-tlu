-- =============================================================================
-- CafeTLU — Dữ liệu mẫu khởi tạo (Seed Data)
-- Người soạn: B (@trungdunxg) — Data & Reports Lead
-- Quy ước: Idempotent (chạy lại nhiều lần không lỗi), tuân thủ WORKFLOW.md mục 8
-- Mật khẩu mặc định cho tất cả tài khoản mẫu: 123456
-- Chuỗi băm bcrypt ($2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy)
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
-- Mật khẩu: 123456
-- -----------------------------------------------------------------------------
INSERT INTO users (id, username, password_hash, full_name, role_id, is_active) VALUES
(1, 'admin', '$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Quản Lý Trưởng TLU', 1, 1),
(2, 'thungan01', '$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Trần Thị Thu Ngân', 2, 1),
(3, 'nhanvien01', '$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Nguyễn Văn Phục Vụ', 2, 1),
(4, 'phache01', '$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Lê Văn Pha Chế', 3, 1),
(5, 'phache02', '$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Hoàng Thị Barista', 3, 1)
ON DUPLICATE KEY UPDATE
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
-- Nhóm 1: Cà phê truyền thống (8 món)
(1, 'Cà phê đen đá', 1, 20000, 'ly', '/assets/products/cf-den-da.png', 1, 0),
(2, 'Cà phê đen nóng', 1, 20000, 'ly', '/assets/products/cf-den-nong.png', 1, 0),
(3, 'Cà phê sữa đá', 1, 25000, 'ly', '/assets/products/cf-sua-da.png', 1, 0),
(4, 'Cà phê sữa nóng', 1, 25000, 'ly', '/assets/products/cf-sua-nong.png', 1, 0),
(5, 'Bạc xỉu 3 tầng TLU', 1, 28000, 'ly', '/assets/products/bac-xiu.png', 1, 0),
(6, 'Cà phê muối xứ Huế', 1, 32000, 'ly', '/assets/products/cf-muoi.png', 1, 0),
(7, 'Cà phê trứng Hà Nội', 1, 35000, 'cốc', '/assets/products/cf-trung.png', 1, 0),
(8, 'Cà phê cốt dừa Hải Phòng', 1, 35000, 'ly', '/assets/products/cf-cot-dua.png', 1, 0),

-- Nhóm 2: Cà phê pha máy (8 món)
(9, 'Espresso Single', 2, 25000, 'tách', '/assets/products/espresso-single.png', 1, 0),
(10, 'Espresso Double', 2, 32000, 'tách', '/assets/products/espresso-double.png', 1, 0),
(11, 'Americano đá', 2, 30000, 'ly', '/assets/products/americano-da.png', 1, 0),
(12, 'Americano nóng', 2, 30000, 'tách', '/assets/products/americano-nong.png', 1, 0),
(13, 'Cappuccino bọt sữa', 2, 38000, 'tách', '/assets/products/cappuccino.png', 1, 0),
(14, 'Café Latte nghệ thuật', 2, 40000, 'ly', '/assets/products/latte.png', 1, 0),
(15, 'Caramel Macchiato', 2, 45000, 'ly', '/assets/products/caramel-macchiato.png', 1, 0),
(16, 'Mocha Chocolate', 2, 45000, 'ly', '/assets/products/mocha.png', 1, 0),

-- Nhóm 3: Trà trái cây tươi (10 món)
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

-- Nhóm 4: Trà sữa & Macchiato (8 món)
(27, 'Trà sữa truyền thống TLU', 4, 30000, 'ly', '/assets/products/tra-sua-tlu.png', 1, 0),
(28, 'Trà sữa trân châu hoàng kim', 4, 35000, 'ly', '/assets/products/ts-tran-chau.png', 1, 0),
(29, 'Trà sữa matcha vụn dừa', 4, 38000, 'ly', '/assets/products/ts-matcha-dua.png', 1, 0),
(30, 'Trà sữa nướng tam bảo', 4, 40000, 'ly', '/assets/products/ts-nuong-tam-bao.png', 1, 0),
(31, 'Trà sữa ô long nướng', 4, 35000, 'ly', '/assets/products/ts-olong-nuong.png', 1, 0),
(32, 'Hồng trà kem cheese Macchiato', 4, 38000, 'ly', '/assets/products/hong-tra-macchiato.png', 1, 0),
(33, 'Lục trà nhài Macchiato', 4, 38000, 'ly', '/assets/products/luc-tra-macchiato.png', 1, 0),
(34, 'Trà sữa khoai môn dẻo', 4, 38000, 'ly', '/assets/products/ts-khoai-mon.png', 1, 0),

-- Nhóm 5: Đá xay & Sinh tố (8 món)
(35, 'Matcha đá xay kem tươi', 5, 45000, 'ly', '/assets/products/matcha-da-xay.png', 1, 0),
(36, 'Chocolate Cookie Freeze', 5, 45000, 'ly', '/assets/products/choco-cookie.png', 1, 0),
(37, 'Caramel đá xay phô mai', 5, 45000, 'ly', '/assets/products/caramel-freeze.png', 1, 0),
(38, 'Sinh tố bơ sáp Đắk Lắk', 5, 40000, 'ly', '/assets/products/sinh-to-bo.png', 1, 0),
(39, 'Sinh tố xoài cát Chu', 5, 38000, 'ly', '/assets/products/sinh-to-xoai.png', 1, 0),
(40, 'Sinh tố việt quất sữa chua', 5, 42000, 'ly', '/assets/products/sinh-to-viet-quat.png', 1, 0),
(41, 'Chanh tuyết bạc hà mát lạnh', 5, 32000, 'ly', '/assets/products/chanh-tuyet.png', 1, 0),
(42, 'Sữa chua dầm hoa quả tươi', 5, 38000, 'bát', '/assets/products/sua-chua-hoa-qua.png', 1, 0),

-- Nhóm 6: Bánh ngọt & Đồ ăn vặt (9 món)
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
-- 6. Seed Mẫu Đơn Hàng & Hóa Đơn (Phục vụ test ngay Swagger & GUI)
-- -----------------------------------------------------------------------------
-- Đơn hàng 1 (Đã hoàn thành & thanh toán)
INSERT INTO orders (id, order_code, table_id, created_by, status, total_amount, notes, is_deleted, created_at) VALUES
(1, 'ORD-20261110-001', 1, 2, 'completed', 73000, 'Khách sinh viên TLU thân thiết', 0, '2026-11-10 08:30:00')
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
    final_amount = VALUES(final_amount),
    paid_amount = VALUES(paid_amount);

-- Đơn hàng 2 (Đang phục vụ tại Bàn 02)
INSERT INTO orders (id, order_code, table_id, created_by, status, total_amount, notes, is_deleted, created_at) VALUES
(2, 'ORD-20261111-002', 2, 3, 'pending', 98000, 'Bàn 2 gọi thêm nước', 0, '2026-11-11 14:00:00')
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
-- 7. Seed Audit Logs (Nhật ký mẫu)
-- -----------------------------------------------------------------------------
INSERT INTO audit_logs (id, user_id, action, entity_type, entity_id, details, ip_address, created_at) VALUES
(1, 1, 'LOGIN', 'users', 1, 'Admin đăng nhập hệ thống thành công', '127.0.0.1', '2026-11-10 08:00:00'),
(2, 2, 'CREATE_ORDER', 'orders', 1, 'Tạo đơn mới ORD-20261110-001 tại Bàn 01', '127.0.0.1', '2026-11-10 08:30:00'),
(3, 2, 'CHECKOUT', 'invoices', 1, 'Thanh toán hoá đơn INV-20261110-001 (73.000 đ - Tiền mặt)', '127.0.0.1', '2026-11-10 09:15:00'),
(4, 3, 'CREATE_ORDER', 'orders', 2, 'Tạo đơn mới ORD-20261111-002 tại Bàn 02', '127.0.0.1', '2026-11-11 14:00:00')
ON DUPLICATE KEY UPDATE
    action = VALUES(action);

SET FOREIGN_KEY_CHECKS = 1;
