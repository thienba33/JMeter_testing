#!/usr/bin/env python3
"""Ve Hinh 1 - so do cau truc Test Plan (images/01-cau-truc-test-plan.png)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

IMG = Path(__file__).resolve().parent.parent / "images"
fig, ax = plt.subplots(figsize=(9, 5.6))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
items = [
    (0, "Test Plan — Kế hoạch kiểm thử hiệu năng Sample Shop API", "#312E81", "white", "bold"),
    (1, "Thread Group — Người dùng ảo  (users / ramp-up / loops)", "#4F46E5", "white", "bold"),
    (2, "HTTP Request Defaults — 127.0.0.1 : 8089, http", "#EEF2FF", "#1E293B", "normal"),
    (2, "HTTP Header Manager — Content-Type: application/json", "#EEF2FF", "#1E293B", "normal"),
    (2, "Uniform Random Timer — Think time 100–400 ms", "#EEF2FF", "#1E293B", "normal"),
    (2, "HTTP Sampler: GET  /  — Trang chủ", "#E0F2FE", "#1E293B", "normal"),
    (2, "HTTP Sampler: GET  /api/products — Danh sách sản phẩm", "#E0F2FE", "#1E293B", "normal"),
    (2, "HTTP Sampler: GET  /api/products/1 — Chi tiết sản phẩm", "#E0F2FE", "#1E293B", "normal"),
    (2, "HTTP Sampler: GET  /api/products/search — Tìm kiếm", "#E0F2FE", "#1E293B", "normal"),
    (2, "HTTP Sampler: GET  /api/users — Danh sách người dùng", "#E0F2FE", "#1E293B", "normal"),
    (2, "HTTP Sampler: POST /api/orders — Tạo đơn hàng (201)", "#FEF3C7", "#1E293B", "normal"),
]
y = 9.4
for level, text, bg, fg, weight in items:
    x = 0.3 + level * 0.55
    box = FancyBboxPatch((x, y - 0.62), 9.4 - x, 0.62, boxstyle="round,pad=0.02,rounding_size=0.08",
                         facecolor=bg, edgecolor="#94A3B8", linewidth=0.7)
    ax.add_patch(box)
    ax.text(x + 0.18, y - 0.31, text, va="center", ha="left", fontsize=10.5, color=fg, weight=weight)
    y -= 0.78
ax.text(5, y - 0.15, "Mỗi Sampler đều có Response Assertion kiểm tra mã HTTP (200 / 201)",
        ha="center", fontsize=9.5, style="italic", color="#475569")
ax.set_title("Hình 1. Cấu trúc Test Plan trong JMeter", fontsize=13, weight="bold", pad=10)
fig.tight_layout()
fig.savefig(IMG / "01-cau-truc-test-plan.png", dpi=150, bbox_inches="tight")
print("Da tao images/01-cau-truc-test-plan.png")
