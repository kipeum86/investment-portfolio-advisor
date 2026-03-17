# Portfolio Construction Rules

## Diversification Constraints

| Rule | Constraint | Enforcement |
|------|-----------|-------------|
| Single ticker concentration | ≤ 25% of total portfolio | quality-gate.py check |
| Single sector concentration | ≤ 40% of equity allocation | portfolio-analyst judgment |
| Minimum holdings per option | ≥ 6 total tickers | quality-gate.py check |
| Maximum holdings per option | ≤ 16 total tickers | portfolio-analyst judgment |
| Holdings per asset class | 2–4 tickers | portfolio-analyst AGENT.md |
| Option differentiation | ≥ 10pp equity weight difference | quality-gate.py check |

## Asset Class Definitions

| Asset Class | Key | Includes |
|------------|-----|---------|
| US Equity | us_equity | US-listed stocks and equity ETFs |
| KR Equity | kr_equity | KR-listed stocks and equity ETFs |
| Bonds | bonds | Government bonds, corporate bonds, bond ETFs |
| Alternatives | alternatives | Gold, REITs, commodities, commodity ETFs |
| Cash | cash | Money market, T-bills, ultra-short bond ETFs |

## Return Estimation Rules

### Scenario Probability Constraints

| Scenario | Probability Range | Default |
|----------|------------------|---------|
| Bull | 15–35% | 25% |
| Base | 35–55% | 50% |
| Bear | 15–35% | 25% |
| Sum | Exactly 100% | 100% |

### Per-Asset Return Assumptions by Scenario

These are starting-point ranges. The LLM provides scenario-specific premises, and `return-estimator.py` uses them within these guardrails.

| Asset Class | Bull Return | Base Return | Bear Return |
|------------|-------------|-------------|-------------|
| US Equity | +12% to +25% | +4% to +10% | -15% to -5% |
| KR Equity | +15% to +30% | +3% to +12% | -20% to -8% |
| Bonds | +2% to +8% | +2% to +5% | -5% to +2% |
| Alternatives | +5% to +20% | +2% to +8% | -10% to +2% |
| Cash | +2% to +5% | +2% to +4% | +1% to +3% |

### Risk-Return Score

```
risk_return_score = weighted_return / |weighted_loss|

where:
  weighted_return = (bull_return × bull_prob) + (base_return × base_prob)
  weighted_loss = bear_return × bear_prob   (bear_return is negative)
```

Interpretation:
- > 2.0: Favorable risk/return
- 1.0–2.0: Neutral
- < 1.0: Unfavorable

## Rebalancing Triggers (informational, not automated)

| Trigger | Threshold |
|---------|----------|
| Single asset class drift | ≥ 5pp from target |
| Portfolio-level drift | ≥ 10pp total deviation |
| Regime change signal | New regime classification |
| Time-based | Quarterly review suggested |
