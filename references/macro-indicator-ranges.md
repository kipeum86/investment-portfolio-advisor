# Macroeconomic Indicator Historical Ranges

Used by `data-validator.py` for sanity checks and `environment-scorer.py` for position-relative scoring.

## US Indicators

| Indicator | ID | Unit | Historical Low | Historical Median | Historical High | Sanity Min | Sanity Max | Source Period |
|-----------|-----|------|---------------|-------------------|-----------------|------------|------------|-------------|
| GDP Growth (QoQ ann.) | us_gdp_growth | % | -31.2 | 2.5 | 33.8 | -35.0 | 40.0 | 2000–2025 |
| CPI (YoY) | us_cpi | % | -2.1 | 2.3 | 9.1 | -5.0 | 15.0 | 2000–2025 |
| PCE (YoY) | us_pce | % | -1.5 | 1.9 | 7.1 | -5.0 | 12.0 | 2000–2025 |
| Federal Funds Rate | us_fed_rate | % | 0.0 | 1.75 | 5.50 | 0.0 | 10.0 | 2000–2025 |
| Unemployment Rate | us_unemployment | % | 3.4 | 5.0 | 14.7 | 0.0 | 20.0 | 2000–2025 |
| 10Y Treasury Yield | us_10y_yield | % | 0.52 | 2.60 | 5.00 | 0.0 | 8.0 | 2000–2025 |
| 2Y Treasury Yield | us_2y_yield | % | 0.10 | 1.80 | 5.10 | 0.0 | 8.0 | 2000–2025 |
| 2Y-10Y Spread | us_yield_spread | bps | -108 | 80 | 290 | -200 | 400 | 2000–2025 |

## KR Indicators

| Indicator | ID | Unit | Historical Low | Historical Median | Historical High | Sanity Min | Sanity Max | Source Period |
|-----------|-----|------|---------------|-------------------|-----------------|------------|------------|-------------|
| GDP Growth (YoY) | kr_gdp_growth | % | -6.8 | 3.0 | 6.8 | -10.0 | 12.0 | 2000–2025 |
| CPI (YoY) | kr_cpi | % | 0.3 | 2.3 | 6.3 | -2.0 | 10.0 | 2000–2025 |
| BOK Base Rate | kr_base_rate | % | 0.50 | 2.50 | 5.25 | 0.0 | 8.0 | 2000–2025 |
| KRW/USD | kr_usd_fx | KRW | 905 | 1150 | 1450 | 800 | 1800 | 2000–2025 |

## Market Fundamentals

| Indicator | ID | Unit | Historical Low | Historical Median | Historical High | Sanity Min | Sanity Max | Source Period |
|-----------|-----|------|---------------|-------------------|-----------------|------------|------------|-------------|
| S&P 500 P/E | sp500_pe | ratio | 10.0 | 19.5 | 38.0 | 5.0 | 50.0 | 2000–2025 |
| Shiller CAPE | sp500_cape | ratio | 13.3 | 25.0 | 44.0 | 8.0 | 55.0 | 2000–2025 |
| KOSPI PER | kospi_per | ratio | 7.0 | 12.5 | 27.0 | 4.0 | 35.0 | 2000–2025 |
| KOSPI PBR | kospi_pbr | ratio | 0.75 | 1.05 | 1.60 | 0.3 | 3.0 | 2000–2025 |
| IG Credit Spread | us_ig_spread | bps | 80 | 130 | 550 | 50 | 800 | 2000–2025 |
| HY Credit Spread | us_hy_spread | bps | 300 | 450 | 2000 | 200 | 2500 | 2000–2025 |

## Sentiment Indicators

| Indicator | ID | Unit | Historical Low | Historical Median | Historical High | Sanity Min | Sanity Max | Source Period |
|-----------|-----|------|---------------|-------------------|-----------------|------------|------------|-------------|
| VIX | vix | index | 9.0 | 17.0 | 82.0 | 5.0 | 100.0 | 2000–2025 |
| Fear & Greed | fear_greed | index | 0 | 50 | 100 | 0 | 100 | 2012–2025 |
| Put/Call Ratio | put_call_ratio | ratio | 0.50 | 0.85 | 1.80 | 0.3 | 3.0 | 2000–2025 |
| AAII Bull % | aaii_bull | % | 15.0 | 37.5 | 75.0 | 0.0 | 100.0 | 2000–2025 |

## Scoring Formula

For `environment-scorer.py`, each indicator is scored relative to its historical range:

```
position = (value - historical_low) / (historical_high - historical_low)
```

- `position` ranges from 0.0 (at historical low) to 1.0 (at historical high)
- Values outside the range are clamped: position = max(0, min(1, position))
- This position is an INPUT to the LLM's environment scoring — it does NOT directly become the 1–10 score
- The LLM uses these positions along with directional context to assign the final 1–10 scores

## Sanity Check Usage

For `data-validator.py`, a collected value triggers a SANITY_ALERT if:
- `value < sanity_min` OR `value > sanity_max`
- Alert is logged but does NOT auto-downgrade the grade
- The alert is included in `validated-data.json` under `sanity_alerts`
