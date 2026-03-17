# Allocation Framework

## Regime-Based Allocation Ranges

Base allocation ranges by economic regime. The portfolio-analyst uses these ranges via `allocation-calculator.py`.

### Regime Definitions

| Regime | Description | Typical Indicators |
|--------|-------------|-------------------|
| early-expansion | Economy recovering, rates low, earnings accelerating | GDP ↑, CPI low, rates low, sentiment improving |
| mid-cycle | Steady growth, moderate inflation, rates normalizing | GDP stable, CPI moderate, rates rising, sentiment neutral |
| late-cycle | Growth slowing, inflation elevated, rates high | GDP ↓, CPI high, rates peak, sentiment mixed |
| recession | Contraction, falling rates, defensive positioning | GDP negative, CPI falling, rates cutting, sentiment fear |
| recovery | Bottoming out, policy support, early risk-on | GDP bottoming, CPI stable, rates low, sentiment turning |

### Base Allocation Ranges (%)

| Regime | US Equity | KR Equity | Bonds | Alternatives | Cash |
|--------|-----------|-----------|-------|-------------|------|
| early-expansion | 50–65 | 10–20 | 15–25 | 5–10 | 0–5 |
| mid-cycle | 40–55 | 10–15 | 20–30 | 5–10 | 5–10 |
| late-cycle | 30–45 | 5–15 | 30–40 | 5–10 | 10–15 |
| recession | 20–35 | 5–10 | 35–50 | 5–10 | 15–25 |
| recovery | 45–60 | 15–20 | 15–25 | 5–10 | 5–10 |

### Risk Profile Mapping

Within each regime's ranges, risk tolerance determines the position:

| Risk Tolerance | Equity Position | Bond Position | Cash Position |
|---------------|-----------------|---------------|---------------|
| aggressive | Upper bound of range | Lower bound | Lower bound |
| moderate | Midpoint of range | Midpoint | Midpoint |
| conservative | Lower bound of range | Upper bound | Upper bound |

### Horizon Adjustment Rules

Applied AFTER risk adjustment. Adjustments are additive — the resulting allocation is then normalized to 100%.

| Horizon | Adjustment |
|---------|-----------|
| < 6 months (short) | Cash +10pp, US equity −5pp, KR equity −5pp |
| 6–12 months | No adjustment |
| 1–3 years (medium) | Base allocation (no adjustment) |
| 3–5 years | US equity +3pp, KR equity +2pp, cash −5pp |
| 5+ years (long) | US equity +5pp, KR equity +5pp, bonds −5pp, cash −5pp |

### Normalization

After all adjustments, if total ≠ 100%:
1. Calculate the difference: `delta = 100 - sum(allocations)`
2. Distribute `delta` proportionally across all non-zero asset classes
3. Round each to 1 decimal place
4. Apply final rounding fix to largest class to ensure sum = exactly 100

### Constraints

- No asset class below 0%
- No single asset class above 70%
- US equity + KR equity combined ≤ 80%
- Cash ≥ 0% always
