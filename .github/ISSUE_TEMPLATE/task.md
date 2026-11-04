---
name: Việc cần làm
description: Tạo một việc mới (feature / nghiên cứu / setup)
title: "[việc] "
labels: ["triage"]
body:
  - type: markdown
    attributes:
      value: |
        Đọc `WORKFLOW.md` mục 6.1 (Definition of Ready) trước khi điền.
        Issue chưa đạt Definition of Ready sẽ không được kéo vào cột **Ready**.

  - type: textarea
    id: goal
    attributes:
      label: Mục tiêu
      description: Kết quả mong đợi, 1–2 câu. Nói KẾT QUẢ, không phải các bước làm.
      placeholder: "Người dùng có thể gộp 2 bàn đang phục vụ thành 1 hoá đơn."
    validations:
      required: true

  - type: textarea
    id: acceptance
    attributes:
      label: Tiêu chí nghiệm thu
      description: Kiểm tra được, không mơ hồ.
      value: |
        - [ ] ...
        - [ ] ...
    validations:
      required: true

  - type: dropdown
    id: area
    attributes:
      label: Vùng ảnh hưởng
      multiple: true
      options:
        - api (A)
        - db (B)
        - report (B)
        - gui (C)
        - infra / ci (D)
        - docs (D)
    validations:
      required: true

  - type: input
    id: files
    attributes:
      label: File dự kiến sửa
      placeholder: "api/routers/orders.py, gui/views/order_view.py"

  - type: textarea
    id: deps
    attributes:
      label: Phụ thuộc
      description: Cần endpoint / bảng / người nào trước?
      placeholder: "Cần endpoint POST /orders/{id}/merge-table từ A (Issue #12)"

  - type: dropdown
    id: estimate
    attributes:
      label: Ước lượng
      options: ["S (< 2h)", "M (nửa ngày)", "L (1–2 ngày)"]
    validations:
      required: true

  - type: checkboxes
    id: checklist
    attributes:
      label: Sẵn sàng để làm?
      options:
        - label: Đã có assignee
        - label: Nếu đổi schema/API thì đã chốt trong docs/api-contract.md hoặc docs/erd.md
        - label: Nếu cần thư viện mới thì đã xin phép
