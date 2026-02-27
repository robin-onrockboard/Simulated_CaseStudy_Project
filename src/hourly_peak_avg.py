#!/usr/bin/env python3
"""Compute average hourly order volume and peak hour across a date range.

Default use case: Jan 1 to Jan 31 based on `Create Time` in Simulated_Case_Study.csv.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Average hourly orders (0-23) across a date range using Create Time"
    )
    parser.add_argument(
        "--input-csv",
        default="/Users/robinhu/Desktop/Robin/Simulated_Case_Study.csv",
        help="Path to source CSV",
    )
    parser.add_argument(
        "--output-csv",
        default="data/processed/jan_hourly_average_orders.csv",
        help="Path to write hourly average results",
    )
    parser.add_argument(
        "--start-date",
        default="2026-01-01",
        help="Inclusive start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        default="2026-01-31",
        help="Inclusive end date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--datetime-format",
        default="%Y-%m-%d %H:%M",
        help="Create Time format in input CSV",
    )
    return parser.parse_args()


def iter_dates(start_day: date, end_day: date) -> list[date]:
    days = []
    current = start_day
    while current <= end_day:
        days.append(current)
        current += timedelta(days=1)
    return days


def main() -> None:
    args = parse_args()

    input_path = Path(args.input_csv)
    output_path = Path(args.output_csv)

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    start_day = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end_day = datetime.strptime(args.end_date, "%Y-%m-%d").date()
    if end_day < start_day:
        raise ValueError("end-date must be >= start-date")

    all_days = iter_dates(start_day, end_day)
    day_count = len(all_days)

    # Key: (date, hour), Value: order count
    counts = defaultdict(int)

    total_rows = 0
    used_rows = 0

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "Create Time" not in (reader.fieldnames or []):
            raise KeyError("Column 'Create Time' not found in CSV")

        for row in reader:
            total_rows += 1
            create_time = (row.get("Create Time") or "").strip()
            if not create_time:
                continue

            try:
                dt = datetime.strptime(create_time, args.datetime_format)
            except ValueError:
                continue

            d = dt.date()
            if d < start_day or d > end_day:
                continue

            counts[(d, dt.hour)] += 1
            used_rows += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for hour in range(24):
        hourly_total = 0
        for d in all_days:
            hourly_total += counts[(d, hour)]
        hourly_avg = hourly_total / day_count
        rows.append(
            {
                "hour": hour,
                "average_orders_per_hour": round(hourly_avg, 4),
                "total_orders_in_month_at_this_hour": hourly_total,
                "days_in_average": day_count,
            }
        )

    peak_row = max(rows, key=lambda r: r["average_orders_per_hour"])

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "hour",
                "average_orders_per_hour",
                "total_orders_in_month_at_this_hour",
                "days_in_average",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("=== Hourly Average Completed ===")
    print(f"Input file: {input_path}")
    print(f"Date range: {start_day} to {end_day} ({day_count} days)")
    print(f"Rows scanned: {total_rows}")
    print(f"Rows used (within date range): {used_rows}")
    print(f"Output CSV: {output_path}")
    print(
        "Peak hour (monthly avg): "
        f"{int(peak_row['hour']):02d}:00 with avg {peak_row['average_orders_per_hour']} orders/hour"
    )


if __name__ == "__main__":
    main()
