# withme.md

## Project Positioning
This is a simulated case study for portfolio use. It is designed to mirror real operational decision-making while avoiding proprietary code and confidential internal datasets.

Core comparison:

- 4 workers x 10 hours
- 6 workers x 6-7 hours

Target outcome of the comparison:

- verify whether 6x6-7 can deliver better per-person efficiency,
- improve stability (less backlog pressure),
- reduce labor cost.

## What We Used
Data foundation:

- Incoming orders from Create Time windows
- Product volume from `Product Size (cm) L * W * H`

Generated tables:

- `data/processed/daily_orders_for_staff_allocation.csv`
- `data/processed/staff_allocation_daily_comparison.csv`
- `data/processed/staff_allocation_efficiency_summary.csv`

Generated visuals:

- `images/jan_hourly_average_orders.svg`
- `images/jan_daily_orders_with_peak.svg`
- `images/staff_allocation_comparison.svg`

## Modeling Logic (How We Simulated)
### 1) Daily demand mapping
Operation day is defined as previous day 09:00:00 to current day 08:59:59.

### 2) Volume calculation
For each record:

- extract length, width, height
- compute `total_volume = L * W * H`

### 3) Packaging-time random generator
Per-order handling time is randomly sampled by total volume:

- <=250: 8-14 sec
- 251-500: 10-15 sec
- 501-1000: 12-16 sec
- 1001-2000: 13-18 sec (bridge assumption)
- >2000: 15-20 sec

### 4) Fatigue logic
For 4-worker model only:

- first 6h at base pace
- hour 6-10 gets fatigue penalty factor 1.3-1.4
- effectively slower completion in late shift

### 5) Backlog carry-over rules
- 4-worker model: above 2000/day goes to backlog
- 6-worker model: above 3500/day goes to backlog

Backlog is carried to next day's total demand.

### 6) Cost logic
Hourly wage is fixed at $18/person/hour.

Daily labor cost:

- `workers * shift_hours * 18`

## What The Data Shows
From `staff_allocation_efficiency_summary.csv`:

- 4x10 avg orders/person/hour: 32.6308
- 6x6-7 avg orders/person/hour: 33.7127
- Efficiency improvement: +3.32% (6x6-7 better)

- 4x10 total labor cost: 21600.0
- 6x6-7 total labor cost: 20836.8941
- Cost reduction: -3.53% (6x6-7 lower)

- 4x10 avg end backlog: 269.5 (8 backlog days)
- 6x6-7 avg end backlog: 29.0 (1 backlog day)

Interpretation:

- both models finish same total processed orders,
- 6x6-7 does it with higher per-person efficiency and lower labor cost,
- backlog pressure is significantly lower under 6x6-7.

## Practical Narrative For Case Study
This simulation supports a practical staffing argument:

- moving from long shifts to shorter shifts with more workers can outperform long-shift concentration,
- once fatigue and carry-over backlog are modeled, the 6x6-7 structure is more stable,
- decision quality improves when demand timing, fatigue penalty, and cost are evaluated together.

## Disclaimer
- This project uses simulated logic and non-proprietary computation.
- Random generation is intentional to emulate operational variability.
- Results are directional and intended for case-study demonstration.
