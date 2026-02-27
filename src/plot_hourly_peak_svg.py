#!/usr/bin/env python3
"""Generate an SVG bar chart for average hourly orders (0-23)."""

from __future__ import annotations

import csv
from pathlib import Path

INPUT_CSV = Path("data/processed/jan_hourly_average_orders.csv")
OUTPUT_SVG = Path("images/jan_hourly_average_orders.svg")
TITLE = "Average Orders per Hour (Jan 1-31)"

# Canvas settings
W, H = 1200, 680
M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 80, 40, 90, 90
PLOT_W = W - M_LEFT - M_RIGHT
PLOT_H = H - M_TOP - M_BOTTOM


def load_rows(path: Path) -> list[tuple[int, float]]:
    rows: list[tuple[int, float]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            h = int(row["hour"])
            v = float(row["average_orders_per_hour"])
            rows.append((h, v))
    rows.sort(key=lambda x: x[0])
    return rows


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_CSV}")

    rows = load_rows(INPUT_CSV)
    if len(rows) != 24:
        raise ValueError(f"Expected 24 hourly rows, got {len(rows)}")

    peak_hour, peak_val = max(rows, key=lambda x: x[1])
    y_max = max(v for _, v in rows)
    y_axis_max = ((int(y_max / 20) + 1) * 20)  # round up to next 20

    step_x = PLOT_W / 24
    bar_w = step_x * 0.72

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    )
    parts.append('<rect width="100%" height="100%" fill="#f8fafc"/>')

    # Title and subtitle
    parts.append(
        f'<text x="{W/2}" y="42" text-anchor="middle" font-size="30" font-family="-apple-system, Segoe UI, Arial" fill="#0f172a" font-weight="700">{esc(TITLE)}</text>'
    )
    parts.append(
        f'<text x="{W/2}" y="70" text-anchor="middle" font-size="16" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Peak hour: {peak_hour:02d}:00 ({peak_val:.2f} orders/hour)</text>'
    )

    # Grid + y-axis ticks
    for t in range(0, y_axis_max + 1, 20):
        y = M_TOP + (1 - t / y_axis_max) * PLOT_H
        color = "#cbd5e1" if t == 0 else "#e2e8f0"
        parts.append(f'<line x1="{M_LEFT}" y1="{y:.2f}" x2="{W-M_RIGHT}" y2="{y:.2f}" stroke="{color}" stroke-width="1"/>')
        parts.append(
            f'<text x="{M_LEFT-10}" y="{y+5:.2f}" text-anchor="end" font-size="12" font-family="-apple-system, Segoe UI, Arial" fill="#64748b">{t}</text>'
        )

    # Bars + x labels
    for i, (hour, val) in enumerate(rows):
        x = M_LEFT + i * step_x + (step_x - bar_w) / 2
        h = (val / y_axis_max) * PLOT_H
        y = M_TOP + (PLOT_H - h)

        if hour == peak_hour:
            fill = "#ef4444"
            stroke = "#b91c1c"
        else:
            fill = "#2563eb"
            stroke = "#1e40af"

        parts.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="1" rx="3"/>'
        )

        parts.append(
            f'<text x="{x + bar_w/2:.2f}" y="{H - M_BOTTOM + 22}" text-anchor="middle" font-size="11" font-family="-apple-system, Segoe UI, Arial" fill="#475569">{hour}</text>'
        )

        # Value label for every hour
        label_y = max(M_TOP + 10, y - 7)
        parts.append(
            f'<text x="{x + bar_w/2:.2f}" y="{label_y:.2f}" text-anchor="middle" font-size="10" font-family="-apple-system, Segoe UI, Arial" fill="#0f172a">{val:.1f}</text>'
        )

    # Axes
    parts.append(f'<line x1="{M_LEFT}" y1="{M_TOP}" x2="{M_LEFT}" y2="{H-M_BOTTOM}" stroke="#334155" stroke-width="1.5"/>')
    parts.append(f'<line x1="{M_LEFT}" y1="{H-M_BOTTOM}" x2="{W-M_RIGHT}" y2="{H-M_BOTTOM}" stroke="#334155" stroke-width="1.5"/>')

    # Axis titles
    parts.append(
        f'<text x="{(M_LEFT + W - M_RIGHT)/2}" y="{H-25}" text-anchor="middle" font-size="14" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Hour of Day (0-23)</text>'
    )
    parts.append(
        f'<text x="24" y="{(M_TOP + H - M_BOTTOM)/2}" transform="rotate(-90,24,{(M_TOP + H - M_BOTTOM)/2})" text-anchor="middle" font-size="14" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Average Orders per Hour</text>'
    )

    # Legend
    lx = W - 280
    ly = 95
    parts.append(f'<rect x="{lx}" y="{ly}" width="16" height="16" fill="#2563eb" stroke="#1e40af"/>')
    parts.append(f'<text x="{lx+24}" y="{ly+13}" font-size="13" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Regular hours</text>')
    parts.append(f'<rect x="{lx}" y="{ly+24}" width="16" height="16" fill="#ef4444" stroke="#b91c1c"/>')
    parts.append(f'<text x="{lx+24}" y="{ly+37}" font-size="13" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Peak hour</text>')

    parts.append("</svg>")

    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SVG.write_text("\n".join(parts), encoding="utf-8")

    print(f"Saved visualization: {OUTPUT_SVG}")
    print(f"Peak hour: {peak_hour:02d}:00, avg={peak_val:.4f}")


if __name__ == "__main__":
    main()
