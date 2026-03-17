# Dashboard Template

## HTML Structure

The dashboard is a single-page HTML file with TailwindCSS CDN + Chart.js.

### Section 1: Header

- User profile summary (budget, period, risk tolerance, asset_scope)
- Analysis date + data confidence grade badge
- Quality flag banner (if critic flagged issues)
- Regime classification badge

### Section 2: Environment Overview

- 6 score cards in a 3×2 grid (macro_us, macro_kr, political, fundamentals_us, fundamentals_kr, sentiment)
- Each card: dimension name, score (1–10), direction indicator, key drivers (2–3 bullet points)
- Use color system for score and direction coloring

### Section 3: Portfolio Comparison (3-column)

- One column per option (Aggressive | Moderate | Conservative)
- Each column: risk level badge, allocation summary table, total allocation = 100%
- Highlighted differentiation row (equity weight difference)

### Section 4: Asset Allocation Charts

- 3 pie charts side-by-side (one per option), using Chart.js
- Legend: US Equity, KR Equity, Bonds, Alternatives, Cash
- Use pieColors from color-system.md

### Section 5: Holdings Tables

- One table per option
- Columns: Ticker, Name, Asset Class, Weight (%), Rationale
- Source tag displayed per holding
- Grade D items shown as "—" (should not appear if quality-gate passed)

### Section 6: Risk/Return Scatter Plot

- Chart.js scatter plot
- X-axis: Bear scenario return (risk)
- Y-axis: Base scenario return (expected return)
- 3 points, one per option, with labels
- Use scatterColors from color-system.md

### Section 7: Scenario Comparison Table

- Rows: Bull, Base, Bear
- Columns per option: Expected Return, Probability, Assumptions
- Use scenarioColors for row headers

### Section 8: Risk-Return Score Summary

- 3 score badges (one per option)
- Score value + interpretation (Favorable / Neutral / Unfavorable)

### Section 9: Key Risks

- Table: Risk, Mechanism Chain, Affected Options, Severity
- Mechanism format: Risk → Impact → Response

### Section 10: Rebalancing Triggers

- Bullet list of trigger conditions

### Section 11: Disclaimer

- Full disclaimer text in muted color
- `text-gray-500 text-sm italic`

### Responsive Design

- Use `grid grid-cols-1 md:grid-cols-3 gap-6` for 3-option layouts
- Charts resize via Chart.js responsive option
- Mobile: stack columns vertically
