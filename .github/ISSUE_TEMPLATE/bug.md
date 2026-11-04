---
name: Báo lỗi
description: Có gì đó chạy không đúng
title: "[bug] "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        Bug report thiếu **bước tái hiện** sẽ không được xử lý (WORKFLOW.md mục 11.3).

  - type: textarea
    id: steps
    attributes:
      label: Bước tái hiện
      value: |
        1.
        2.
        3.
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Kết quả mong đợi
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Kết quả thực tế
    validations:
      required: true

  - type: input
    id: env
    attributes:
      label: Môi trường
      placeholder: "Windows 11 / bản build v0.1.0 / MySQL Docker"
    validations:
      required: true

  - type: textarea
    id: evidence
    attributes:
      label: Ảnh chụp / log
      description: Kéo ảnh vào đây. Log liên quan dán vào khối code.
      render: text

  - type: dropdown
    id: severity
    attributes:
      label: Mức độ
      options:
        - "Chặn demo / không dùng được"
        - "Sai chức năng nhưng vẫn dùng được"
        - "Giao diện / lỗi nhỏ"
    validations:
      required: true
