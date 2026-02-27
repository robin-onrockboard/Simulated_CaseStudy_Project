#!/usr/bin/env python3
"""Plot 3-line staff allocation comparison chart as SVG.

Lines:
1) Incoming Orders (Jan 1-31)
2) Total Demanded Orders - 4 workers x 10h
3) Total Demanded Orders - 6 workers x 6-7h
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List

INCOMING_CSV = Path("data/processed/daily_orders_for_staff_allocation.csv")
STAFF_CSV = Path("data/processed/staff_allocation_daily_comparison.csv")
OUTPUT_SVG = Path("images/staff_allocation_comparison.svg")

TITLE = "Staff Allocation Comparison (Jan 1-31)"
SUBTITLE = "Y-axis: Orders | Lines: Incoming vs Total Demanded (4x10h, 6x6-7h)"

W, H = 1320, 760
M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 95, 60, 100, 110
PLOT_W = W - M_LEFT - M_RIGHT
PLOT_H = H - M_TOP - M_BOTTOM


def parse_day_num(s: str) -> int:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).day
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {s}")


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def nice_axis_max(v: float) -> int:
    if v <= 1000:
        step = 100
    elif v <= 3000:
        step = 250
    else:
        step = 500
    return int((int(v / step) + 1) * step)


def load_incoming() -> Dict[int, float]:
    if not INCOMING_CSV.exists():
        raise FileNotFoundError(f"Missing: {INCOMING_CSV}")
    out: Dict[int, float] = {}
    with INCOMING_CSV.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            d = parse_day_num(row["day"])
            out[d] = float(row["orders_total"])
    return out


def load_demand_by_model() -> Dict[str, Dict[int, float]]:
    if not STAFF_CSV.exists():
        raise FileNotFoundError(f"Missing: {STAFF_CSV}")

    out: Dict[str, Dict[int, float]] = {
        "4_workers_10h": {},
        "6_workers_6to7h": {},
    }
    with STAFF_CSV.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            m = (row.get("model") or "").strip()
            if m not in out:
                continue
            d = parse_day_num(row["day"])
            out[m][d] = float(row["total_demand_orders"])
    return out


def line_path(xs: List[float], ys: List[float]) -> str:
    cmds = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        cmds.append(("M" if i == 0 else "L") + f" {x:.2f} {y:.2f}")
    return " ".join(cmds)


def main() -> None:
    incoming = load_incoming()
    demand = load_demand_by_model()

    # Day range 1..31
    days = list(range(1, 32))

    # Fill model day-1 using incoming day-1 as baseline (no prior backlog)
    day1_incoming = incoming.get(1, 0.0)
    if 1 not in demand["4_workers_10h"]:
        demand["4_workers_10h"][1] = day1_incoming
    if 1 not in demand["6_workers_6to7h"]:
        demand["6_workers_6to7h"][1] = day1_incoming

    incoming_vals = [incoming.get(d, 0.0) for d in days]
    m4_vals = [demand["4_workers_10h"].get(d, 0.0) for d in days]
    m6_vals = [demand["6_workers_6to7h"].get(d, 0.0) for d in days]

    y_max = max(max(incoming_vals), max(m4_vals), max(m6_vals))
    y_axis_max = nice_axis_max(y_max)

    x_step = PLOT_W / (len(days) - 1)

    def x_of(day_num: int) -> float:
        return M_LEFT + (day_num - 1) * x_step

    def y_of(v: float) -> float:
        return M_TOP + (1 - v / y_axis_max) * PLOT_H

    x_coords = [x_of(d) for d in days]
    y_in = [y_of(v) for v in incoming_vals]
    y_m4 = [y_of(v) for v in m4_vals]
    y_m6 = [y_of(v) for v in m6_vals]

    peak_day = days[incoming_vals.index(max(incoming_vals))]
    peak_val = max(incoming_vals)

    parts: List[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    )
    parts.append('<rect width="100%" height="100%" fill="#f8fafc"/>')

    parts.append(
        f'<text x="{W/2}" y="44" text-anchor="middle" font-size="30" font-family="-apple-system, Segoe UI, Arial" fill="#0f172a" font-weight="700">{esc(TITLE)}</text>'
    )
    parts.append(
        f'<text x="{W/2}" y="72" text-anchor="middle" font-size="15" font-family="-apple-system, Segoe UI, Arial" fill="#334155">{esc(SUBTITLE)}</text>'
    )
    parts.append(
        '<text x="95" y="88" font-size="12" font-family="-apple-system, Segoe UI, Arial" fill="#64748b">Assumption: model day-1 total demanded orders initialized from day-1 incoming orders.</text>'
    )

    # Y grid
    tick = 500 if y_axis_max >= 3000 else 250
    for t in range(0, y_axis_max + 1, tick):
        y = y_of(float(t))
        color = "#cbd5e1" if t == 0 else "#e2e8f0"
        parts.append(f'<line x1="{M_LEFT}" y1="{y:.2f}" x2="{W-M_RIGHT}" y2="{y:.2f}" stroke="{color}" stroke-width="1"/>')
        parts.append(
            f'<text x="{M_LEFT-10}" y="{y+5:.2f}" text-anchor="end" font-size="12" font-family="-apple-system, Segoe UI, Arial" fill="#64748b">{t}</text>'
        )

    # X ticks every 2 days + 1 and 31
    for d in days:
        if d not in (1, 31) and d % 2 != 0:
            continue
        x = x_of(d)
        parts.append(f'<line x1="{x:.2f}" y1="{H-M_BOTTOM}" x2="{x:.2f}" y2="{H-M_BOTTOM+6}" stroke="#64748b" stroke-width="1"/>')
        parts.append(
            f'<text x="{x:.2f}" y="{H-M_BOTTOM+24}" text-anchor="middle" font-size="11" font-family="-apple-system, Segoe UI, Arial" fill="#475569">{d}</text>'
        )

    # Axes
    parts.append(f'<line x1="{M_LEFT}" y1="{M_TOP}" x2="{M_LEFT}" y2="{H-M_BOTTOM}" stroke="#334155" stroke-width="1.5"/>')
    parts.append(f'<line x1="{M_LEFT}" y1="{H-M_BOTTOM}" x2="{W-M_RIGHT}" y2="{H-M_BOTTOM}" stroke="#334155" stroke-width="1.5"/>')

    # Line styles
    color_in = "#0f766e"   # teal
    color_m4 = "#dc2626"   # red
    color_m6 = "#2563eb"   # blue

    parts.append(
        f'<path d="{line_path(x_coords, y_in)}" fill="none" stroke="{color_in}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    parts.append(
        f'<path d="{line_path(x_coords, y_m4)}" fill="none" stroke="{color_m4}" stroke-width="2.8" stroke-dasharray="7 5" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    parts.append(
        f'<path d="{line_path(x_coords, y_m6)}" fill="none" stroke="{color_m6}" stroke-width="2.8" stroke-dasharray="2 0" stroke-linejoin="round" stroke-linecap="round"/>'
    )

    # Markers for incoming peak
    px, py = x_of(peak_day), y_of(peak_val)
    parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="6" fill="#0ea5a3" stroke="#115e59" stroke-width="1.5"/>')
    parts.append(f'<line x1="{px:.2f}" y1="{py:.2f}" x2="{px+26:.2f}" y2="{py-20:.2f}" stroke="#0f766e" stroke-width="1.5"/>')
    parts.append(f'<rect x="{px+30:.2f}" y="{py-39:.2f}" width="200" height="30" rx="6" fill="#ccfbf1" stroke="#5eead4"/>')
    parts.append(
        f'<text x="{px+40:.2f}" y="{py-20:.2f}" font-size="12" font-family="-apple-system, Segoe UI, Arial" fill="#134e4a">Incoming Peak: Day {peak_day} ({peak_val:.0f})</text>'
    )

    # Axis titles
    parts.append(
        f'<text x="{(M_LEFT + W - M_RIGHT)/2}" y="{H-34}" text-anchor="middle" font-size="14" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Day of Month (Jan 2026)</text>'
    )
    parts.append(
        f'<text x="28" y="{(M_TOP + H - M_BOTTOM)/2}" transform="rotate(-90,28,{(M_TOP + H - M_BOTTOM)/2})" text-anchor="middle" font-size="14" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Orders</text>'
    )

    # Legend
    lx = W - 430
    ly = 110
    parts.append(f'<rect x="{lx}" y="{ly}" width="16" height="16" fill="{color_in}"/>')
    parts.append(f'<text x="{lx+24}" y="{ly+13}" font-size="13" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Incoming Orders (Day 1-31)</text>')
    parts.append(f'<line x1="{lx}" y1="{ly+30}" x2="{lx+16}" y2="{ly+30}" stroke="{color_m4}" stroke-width="2.8" stroke-dasharray="7 5"/>')
    parts.append(f'<text x="{lx+24}" y="{ly+34}" font-size="13" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Total Demanded Orders - 4 workers x 10h</text>')
    parts.append(f'<line x1="{lx}" y1="{ly+50}" x2="{lx+16}" y2="{ly+50}" stroke="{color_m6}" stroke-width="2.8"/>')
    parts.append(f'<text x="{lx+24}" y="{ly+54}" font-size="13" font-family="-apple-system, Segoe UI, Arial" fill="#334155">Total Demanded Orders - 6 workers x 6-7h</text>')

    parts.append("</svg>")

    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SVG.write_text("\n".join(parts), encoding="utf-8")

    print(f"Saved visualization: {OUTPUT_SVG}")
    print(f"Incoming peak day: {peak_day}, orders={peak_val:.2f}")


if __name__ == "__main__":
    main()
