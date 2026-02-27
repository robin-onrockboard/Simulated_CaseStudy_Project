#!/usr/bin/env python3
"""Generate SVG line chart for daily order totals with peak marker."""

from __future__ import annotations

import csv
from pathlib import Path

INPUT_CSV = Path("data/processed/daily_orders_for_staff_allocation.csv")
OUTPUT_SVG = Path("images/jan_daily_orders_with_peak.svg")
TITLE = "Daily Orders (Jan 1-31, Defined Operation-Day Method)"

W, H = 1300, 700
M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 90, 50, 90, 100
PLOT_W = W - M_LEFT - M_RIGHT
PLOT_H = H - M_TOP - M_BOTTOM


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def load_rows(path: Path) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            day = row["day"].strip()
            total = float(row["orders_total"])
            rows.append((day, total))
    return rows


def nice_axis_max(v: float) -> int:
    if v <= 100:
        step = 20
    elif v <= 1000:
        step = 100
    else:
        step = 500
    return int((int(v / step) + 1) * step)


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_CSV}")

    rows = load_rows(INPUT_CSV)
    if not rows:
        raise ValueError("No rows found in daily CSV")

    n = len(rows)
    peak_idx, (peak_day, peak_val) = max(enumerate(rows), key=lambda x: x[1][1])

    y_max = max(v for _, v in rows)
    y_axis_max = nice_axis_max(y_max)

    x_step = PLOT_W / (n - 1 if n > 1 else 1)

    points = []
    for i, (_, val) in enumerate(rows):
        x = M_LEFT + i * x_step
        y = M_TOP + (1 - val / y_axis_max) * PLOT_H
        points.append((x, y))

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    )
    parts.append('<rect width="100%" height="100%" fill="#f8fafc"/>')

    parts.append(
        f'<text x="{W/2}" y="42" text-anchor="middle" font-size="30" font-family="-apple-system, Segoe UI, Arial" fill="#0f172a" font-weight="700">{esc(TITLE)}</text>'
    )
    parts.append(
        f'<text x="{W/2}" y="70" text-anchor="middle" font-size="16" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Peak day: {peak_day} ({peak_val:.2f} orders)</text>'
    )

    # Grid and Y ticks
    tick = 500 if y_axis_max > 2000 else 200
    for t in range(0, y_axis_max + 1, tick):
        y = M_TOP + (1 - t / y_axis_max) * PLOT_H
        color = "#cbd5e1" if t == 0 else "#e2e8f0"
        parts.append(f'<line x1="{M_LEFT}" y1="{y:.2f}" x2="{W-M_RIGHT}" y2="{y:.2f}" stroke="{color}" stroke-width="1"/>')
        parts.append(
            f'<text x="{M_LEFT-10}" y="{y+5:.2f}" text-anchor="end" font-size="12" font-family="-apple-system, Segoe UI, Arial" fill="#64748b">{t}</text>'
        )

    # Axes
    parts.append(f'<line x1="{M_LEFT}" y1="{M_TOP}" x2="{M_LEFT}" y2="{H-M_BOTTOM}" stroke="#334155" stroke-width="1.5"/>')
    parts.append(f'<line x1="{M_LEFT}" y1="{H-M_BOTTOM}" x2="{W-M_RIGHT}" y2="{H-M_BOTTOM}" stroke="#334155" stroke-width="1.5"/>')

    # X tick labels: show every 2 days for readability
    for i, (day, _) in enumerate(rows):
        if (i + 1) % 2 != 0 and i not in (0, n - 1, peak_idx):
            continue
        x, _ = points[i]
        day_num = day[-2:]
        parts.append(
            f'<line x1="{x:.2f}" y1="{H-M_BOTTOM}" x2="{x:.2f}" y2="{H-M_BOTTOM+6}" stroke="#64748b" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{H-M_BOTTOM+24}" text-anchor="middle" font-size="11" font-family="-apple-system, Segoe UI, Arial" fill="#475569">{int(day_num)}</text>'
        )

    # Line path
    d = []
    for i, (x, y) in enumerate(points):
        cmd = "M" if i == 0 else "L"
        d.append(f"{cmd} {x:.2f} {y:.2f}")
    parts.append(
        f'<path d="{" ".join(d)}" fill="none" stroke="#2563eb" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
    )

    # Point markers
    for i, (x, y) in enumerate(points):
        if i == peak_idx:
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="#ef4444" stroke="#991b1b" stroke-width="1.5"/>')
        else:
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="#1d4ed8"/>')

    # Peak annotation
    px, py = points[peak_idx]
    label_x = min(W - M_RIGHT - 10, px + 20)
    label_y = max(M_TOP + 20, py - 25)

    parts.append(
        f'<line x1="{px:.2f}" y1="{py:.2f}" x2="{label_x-8:.2f}" y2="{label_y-8:.2f}" stroke="#dc2626" stroke-width="1.5"/>'
    )
    parts.append(
        f'<rect x="{label_x:.2f}" y="{label_y-22:.2f}" width="210" height="40" rx="6" fill="#fee2e2" stroke="#fca5a5"/>'
    )
    parts.append(
        f'<text x="{label_x+10:.2f}" y="{label_y-5:.2f}" font-size="12" font-family="-apple-system, Segoe UI, Arial" fill="#7f1d1d">Peak: {peak_day} | {peak_val:.0f} orders</text>'
    )

    # Axis titles
    parts.append(
        f'<text x="{(M_LEFT + W - M_RIGHT)/2}" y="{H-30}" text-anchor="middle" font-size="14" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Day of Month (Jan 2026)</text>'
    )
    parts.append(
        f'<text x="26" y="{(M_TOP + H - M_BOTTOM)/2}" transform="rotate(-90,26,{(M_TOP + H - M_BOTTOM)/2})" text-anchor="middle" font-size="14" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Orders per Day</text>'
    )

    parts.append("</svg>")

    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SVG.write_text("\n".join(parts), encoding="utf-8")

    print(f"Saved visualization: {OUTPUT_SVG}")
    print(f"Peak day: {peak_day} ({peak_val:.4f} orders)")


if __name__ == "__main__":
    main()
