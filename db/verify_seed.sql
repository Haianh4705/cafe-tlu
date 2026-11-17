-- =============================================================================
-- CafeTLU — Kiểm chứng dữ liệu seed sau khi nạp
--
-- Cách chạy:
--   docker exec -i <container> mysql -uroot -proot cafetlu < db/verify_seed.sql
--   hoặc: make reset-db  (nạp schema + seed)  rồi chạy lệnh trên
--
-- Mỗi dòng trả về: tên phép kiểm · giá trị mong đợi · giá trị thực tế · PASS/FAIL.
-- Không có dòng nào FAIL = dữ liệu đúng. Đây là bằng chứng cho #17/#18/#28.
-- =============================================================================

SET NAMES utf8mb4;

SELECT 'roles = 3' AS phep_kiem, 3 AS mong_doi, COUNT(*) AS thuc_te,
       IF(COUNT(*) = 3, 'PASS', 'FAIL') AS ket_qua
FROM roles
UNION ALL
SELECT 'users = 5', 5, COUNT(*), IF(COUNT(*) = 5, 'PASS', 'FAIL') FROM users
UNION ALL
SELECT 'categories = 6', 6, COUNT(*), IF(COUNT(*) = 6, 'PASS', 'FAIL') FROM categories
UNION ALL
SELECT 'products = 51', 51, COUNT(*), IF(COUNT(*) = 51, 'PASS', 'FAIL') FROM products
UNION ALL
SELECT 'tables = 12', 12, COUNT(*), IF(COUNT(*) = 12, 'PASS', 'FAIL') FROM `tables`
UNION ALL
SELECT 'orders = 120', 120, COUNT(*), IF(COUNT(*) = 120, 'PASS', 'FAIL') FROM orders
UNION ALL
SELECT 'order_items = 250', 250, COUNT(*), IF(COUNT(*) = 250, 'PASS', 'FAIL') FROM order_items
UNION ALL
SELECT 'invoices = 119', 119, COUNT(*), IF(COUNT(*) = 119, 'PASS', 'FAIL') FROM invoices
UNION ALL
SELECT 'audit_logs = 20', 20, COUNT(*), IF(COUNT(*) = 20, 'PASS', 'FAIL') FROM audit_logs
UNION ALL
-- Mã đơn / mã hoá đơn phải unique (đây là lỗi đã từng làm seed mất 2 dòng)
SELECT 'mã đơn trùng = 0', 0,
       (SELECT COUNT(*) FROM (SELECT order_code FROM orders GROUP BY order_code HAVING COUNT(*) > 1) x),
       IF((SELECT COUNT(*) FROM (SELECT order_code FROM orders GROUP BY order_code HAVING COUNT(*) > 1) x) = 0, 'PASS', 'FAIL')
UNION ALL
SELECT 'mã hoá đơn trùng = 0', 0,
       (SELECT COUNT(*) FROM (SELECT invoice_code FROM invoices GROUP BY invoice_code HAVING COUNT(*) > 1) x),
       IF((SELECT COUNT(*) FROM (SELECT invoice_code FROM invoices GROUP BY invoice_code HAVING COUNT(*) > 1) x) = 0, 'PASS', 'FAIL')
UNION ALL
-- orders.total_amount = Σ subtotal của các dòng không bị huỷ (bất biến §3.3 mục 2)
SELECT 'đơn lệch tổng tiền = 0', 0, COUNT(*), IF(COUNT(*) = 0, 'PASS', 'FAIL')
FROM orders o
JOIN (SELECT order_id, SUM(subtotal) AS s FROM order_items WHERE status <> 'cancelled' GROUP BY order_id) i
  ON i.order_id = o.id
WHERE o.total_amount <> i.s
UNION ALL
SELECT 'hàng hoá đơn sai final = 0', 0, COUNT(*), IF(COUNT(*) = 0, 'PASS', 'FAIL')
FROM invoices WHERE final_amount <> subtotal_amount - discount_amount
UNION ALL
SELECT 'hàng hoá đơn sai change = 0', 0, COUNT(*), IF(COUNT(*) = 0, 'PASS', 'FAIL')
FROM invoices WHERE change_amount <> paid_amount - final_amount
UNION ALL
SELECT 'hoá đơn paid < final = 0', 0, COUNT(*), IF(COUNT(*) = 0, 'PASS', 'FAIL')
FROM invoices WHERE paid_amount < final_amount
UNION ALL
SELECT 'dòng món sai subtotal = 0', 0, COUNT(*), IF(COUNT(*) = 0, 'PASS', 'FAIL')
FROM order_items WHERE subtotal <> quantity * unit_price
UNION ALL
SELECT 'hoá đơn mồ côi = 0', 0, COUNT(*), IF(COUNT(*) = 0, 'PASS', 'FAIL')
FROM invoices v LEFT JOIN orders o ON o.id = v.order_id WHERE o.id IS NULL
UNION ALL
SELECT 'dòng món mồ côi = 0', 0, COUNT(*), IF(COUNT(*) = 0, 'PASS', 'FAIL')
FROM order_items i LEFT JOIN orders o ON o.id = i.order_id WHERE o.id IS NULL
UNION ALL
-- Mỗi bàn chỉ 1 đơn đang mở (ràng buộc uq_orders_open_table)
SELECT 'bàn có 2 đơn mở = 0', 0, COUNT(*), IF(COUNT(*) = 0, 'PASS', 'FAIL')
FROM (SELECT table_id FROM orders WHERE status IN ('pending', 'serving') GROUP BY table_id HAVING COUNT(*) > 1) x
UNION ALL
-- Đơn trải đủ 30 ngày khác nhau (#28)
SELECT 'số ngày có đơn = 30', 30, COUNT(DISTINCT DATE(created_at)), IF(COUNT(DISTINCT DATE(created_at)) = 30, 'PASS', 'FAIL')
FROM orders
UNION ALL
-- Món đang bán không được trùng tên (ràng buộc uq_products_active_name)
SELECT 'tên món đang bán trùng = 0', 0,
       (SELECT COUNT(*) FROM (SELECT name FROM products WHERE deleted_at IS NULL GROUP BY name HAVING COUNT(*) > 1) x),
       IF((SELECT COUNT(*) FROM (SELECT name FROM products WHERE deleted_at IS NULL GROUP BY name HAVING COUNT(*) > 1) x) = 0, 'PASS', 'FAIL')
UNION ALL
-- Bảng refresh_tokens tồn tại (ADR-013, #22) và seed không tạo token nào
SELECT 'bảng refresh_tokens tồn tại = 1', 1,
       (SELECT COUNT(*) FROM information_schema.tables
         WHERE table_schema = DATABASE() AND table_name = 'refresh_tokens'),
       IF((SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name = 'refresh_tokens') = 1, 'PASS', 'FAIL')
UNION ALL
SELECT 'refresh_tokens rỗng sau seed = 0', 0, COUNT(*), IF(COUNT(*) = 0, 'PASS', 'FAIL')
FROM refresh_tokens;
