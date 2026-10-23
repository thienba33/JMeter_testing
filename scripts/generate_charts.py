#!/usr/bin/env python3
"""
Sinh cac hinh minh hoa ket qua tu file results.jtl that (khong ve tay so lieu).
Chay: python3 scripts/generate_charts.py
Ket qua: images/02, 03, 04, 05 (hinh 01 la so do cau truc Test Plan, ve rieng).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold"})

SCENARIOS = [
    ("kich-ban-1-co-ban-10-users", "Kịch bản 1\n10 users"),
    ("kich-ban-2-tai-thuong-50-users", "Kịch bản 2\n50 users"),
    ("kich-ban-3-stress-100-users", "Kịch bản 3\n100 users"),
]

data = {}
summary = []
for folder, label in SCENARIOS:
    df = pd.read_csv(ROOT / "results" / folder / "results.jtl")
    data[label] = df
    start, end = df.timeStamp.min(), (df.timeStamp + df.elapsed).max()
    summary.append({
        "label": label, "samples": len(df),
        "avg": df.elapsed.mean(), "p95": df.elapsed.quantile(0.95),
        "max": df.elapsed.max(), "err": (~df.success).mean() * 100,
        "throughput": len(df) / ((end - start) / 1000),
    })
s = pd.DataFrame(summary)

# --- Hinh 02: Thoi gian phan hoi theo kich ban (Avg / P95 / Max) ---
fig, ax = plt.subplots(figsize=(8, 4.6))
x = range(len(s))
w = 0.26
ax.bar([i - w for i in x], s.avg, w, label="Trung bình (Avg)", color="#4F46E5")
ax.bar(x, s.p95, w, label="P95", color="#38BDF8")
ax.bar([i + w for i in x], s["max"], w, label="Lớn nhất (Max)", color="#F59E0B")
for i, row in s.iterrows():
    ax.text(i - w, row.avg + 1.5, f"{row.avg:.1f}", ha="center", fontsize=9)
    ax.text(i + w, row["max"] + 1.5, f"{int(row['max'])}", ha="center", fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels(s.label)
ax.set_ylabel("Thời gian phản hồi (ms)")
ax.set_title("Hình 2. Thời gian phản hồi theo kịch bản tải")
ax.legend(); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(IMG / "02-thoi-gian-phan-hoi-theo-kich-ban.png", dpi=150); plt.close(fig)

# --- Hinh 03: Thong luong (Throughput) theo kich ban ---
fig, ax = plt.subplots(figsize=(8, 4.6))
bars = ax.bar(s.label, s.throughput, width=0.5, color="#4F46E5")
for bar, row in zip(bars, s.itertuples()):
    ax.text(bar.get_x() + bar.get_width() / 2, row.throughput + 2,
            f"{row.throughput:.1f} req/s\n({int(row.samples)} requests)", ha="center", fontsize=10)
ax.set_ylabel("Throughput (requests/giây)")
ax.set_title("Hình 3. Thông lượng (Throughput) theo kịch bản tải")
ax.set_ylim(0, s.throughput.max() * 1.25)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(IMG / "03-thong-luong-theo-kich-ban.png", dpi=150); plt.close(fig)

# --- Hinh 04: Thoi gian phan hoi trung binh theo endpoint (kich ban 3) ---
df3 = data["Kịch bản 3\n100 users"]
g = df3.groupby("label").elapsed.mean().sort_values()
fig, ax = plt.subplots(figsize=(8.5, 4.4))
bars = ax.barh([l.replace(" - ", "\n") for l in g.index], g.values, color="#38BDF8", height=0.55)
for bar, v in zip(bars, g.values):
    ax.text(v + 0.5, bar.get_y() + bar.get_height() / 2, f"{v:.1f} ms", va="center", fontsize=10)
ax.set_xlabel("Thời gian phản hồi trung bình (ms)")
ax.set_title("Hình 4. Thời gian phản hồi theo API — Kịch bản 3")
ax.set_xlim(0, g.values.max() * 1.25)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(IMG / "04-thoi-gian-phan-hoi-theo-endpoint.png", dpi=150); plt.close(fig)

# --- Hinh 05: Bang Summary Report (ve lai tu so lieu that cua 3 kich ban) ---
fig, ax = plt.subplots(figsize=(10.5, 3.0))
ax.axis("off")
cols = ["Kịch bản", "Số mẫu", "Avg (ms)", "Min (ms)", "Max (ms)", "P95 (ms)", "Lỗi (%)", "Throughput (req/s)"]
cells = []
for folder, label in SCENARIOS:
    df = data[label]
    start, end = df.timeStamp.min(), (df.timeStamp + df.elapsed).max()
    cells.append([label.replace("\n", " - ").replace("Kịch bản", "KB"), len(df), f"{df.elapsed.mean():.1f}",
                  int(df.elapsed.min()), int(df.elapsed.max()), f"{df.elapsed.quantile(0.95):.0f}",
                  f"{(~df.success).mean() * 100:.2f}", f"{len(df) / ((end - start) / 1000):.1f}"])
tbl = ax.table(cellText=cells, colLabels=cols, loc="center", cellLoc="center", colWidths=[0.19,0.09,0.10,0.10,0.10,0.10,0.09,0.23])
tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1, 1.7)
for j in range(len(cols)):
    tbl[0, j].set_facecolor("#4F46E5"); tbl[0, j].set_text_props(color="white", weight="bold")
ax.set_title("Hình 5. Bảng Summary Report tổng hợp 3 kịch bản", pad=18, weight="bold", fontsize=13)
fig.tight_layout(); fig.savefig(IMG / "05-bang-summary-report.png", dpi=150, bbox_inches="tight"); plt.close(fig)

print("Da tao 4 hinh trong images/:")
for f in sorted(IMG.glob("0*.png")):
    print(" -", f.name)
print("\nSo lieu tong hop dung cho README:")
print(s.to_string(index=False))
