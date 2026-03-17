# Investment Portfolio Advisor — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a top-down portfolio recommendation system that takes a user's investment profile and produces 3 risk-differentiated portfolio options with HTML dashboard and DOCX memo output.

**Architecture:** 12-step 2-phase pipeline (Environment Assessment → Portfolio Construction) orchestrated by CLAUDE.md, with 3 sub-agents (environment-researcher, portfolio-analyst, critic), 12 skills, and 8 Python scripts. Data flows through JSON files between steps. LLM handles qualitative judgment; scripts handle deterministic computation.

**Tech Stack:** Python 3.11+, python-docx (DOCX generation), pytest (testing), TailwindCSS CDN + Chart.js (HTML dashboard), Claude Code agent framework (.claude/skills + .claude/agents)

**Spec:** `investment-portfolio-advisor-design-v2-en.md` (root directory)

**Implementation Order:** Bottom-Up — Reference Files → Python Scripts (with TDD) → Skills → Agents → CLAUDE.md

---

## Chunk 1: Project Foundation

### Task 1: Initialize Project Structure

**Files:**
- Create: `.gitignore`
- Create: `.claude/settings.json`
- Create: `.mcp.json`
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `output/.gitkeep`

- [ ] **Step 1: Initialize git repository**

```bash
cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor
git init
```

- [ ] **Step 2: Create .gitignore**

Create `.gitignore`:
```
# Design docs (tracked separately)
# investment-portfolio-advisor-design-*.md

# Runtime output
output/*
!output/.gitkeep

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.pytest_cache/
venv/
.venv/

# Environment & secrets
.env
.env.local
.env.*.local
*.pem
*.key

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/settings.json
*.swp
*.swo
*~

# Claude session artifacts
.claude/projects/
```

- [ ] **Step 3: Create .claude/settings.json**

Create `.claude/settings.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(python3 *)",
      "Bash(python *)",
      "Bash(pytest *)",
      "Bash(pip install *)",
      "Bash(pip3 install *)",
      "Bash(cat output/*)",
      "Bash(ls *)",
      "Bash(mkdir *)",
      "Bash(open output/reports/*)"
    ]
  }
}
```

- [ ] **Step 4: Create .mcp.json (placeholder for Phase 2+)**

Create `.mcp.json`:
```json
{
  "mcpServers": {}
}
```

- [ ] **Step 5: Create requirements.txt**

Create `requirements.txt`:
```
python-docx>=1.1.0
pytest>=8.0.0
```

- [ ] **Step 6: Create pytest.ini**

Create `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
```

- [ ] **Step 7: Create full directory structure**

```bash
# Output directories
mkdir -p output/{data/{macro,political,fundamentals,sentiment,recommendations},reports,logs}
touch output/.gitkeep

# Reference directories
mkdir -p references/output-templates

# Skill directories
mkdir -p .claude/skills/{staleness-checker/scripts,query-interpreter,macro-collector,political-collector,fundamentals-collector,sentiment-collector,data-validator/scripts,environment-scorer/scripts,portfolio-dashboard-generator/references,memo-generator/scripts,quality-gate/scripts,data-manager/scripts}

# Agent directories
mkdir -p .claude/agents/{environment-researcher,portfolio-analyst/scripts,critic}

# Test directories
mkdir -p tests/{scripts,integration}
```

- [ ] **Step 8: Create Python virtual environment and install dependencies**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- [ ] **Step 9: Commit project foundation**

```bash
git add .gitignore .claude/settings.json .mcp.json requirements.txt pytest.ini output/.gitkeep
git commit -m "chore: initialize project structure with config files"
```

---

## Chunk 2: Reference Files

### Task 2: Create allocation-framework.md

**Files:**
- Create: `references/allocation-framework.md`

This is the core reference for portfolio-analyst's allocation-calculator.py. Defines regime → allocation range mappings plus adjustment rules.

- [ ] **Step 1: Create allocation-framework.md**

Create `references/allocation-framework.md`:
```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add references/allocation-framework.md
git commit -m "docs: add allocation framework reference with regime-based ranges"
```

### Task 3: Create asset-universe.md

**Files:**
- Create: `references/asset-universe.md`

Defines the approved ticker/ETF/bond universe, categorized by asset_scope (etf_only, etf_and_stocks, broad).

- [ ] **Step 1: Create asset-universe.md**

Create `references/asset-universe.md`:
```markdown
# Asset Universe

## Scope Filtering

The user's `asset_scope` in `user-profile.json` determines which tickers are available for selection:

- `etf_only`: Only rows marked with scope `etf_only` (ETFs only)
- `etf_and_stocks`: Rows marked `etf_only` + `etf_and_stocks` (ETFs + major individual stocks)
- `broad`: All rows (ETFs + stocks + alternatives + individual bonds)

## US Equity

### ETFs (scope: etf_only)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| VOO | Vanguard S&P 500 ETF | US Large Cap Index | Core US equity exposure |
| SPY | SPDR S&P 500 ETF | US Large Cap Index | Most liquid S&P 500 ETF |
| QQQ | Invesco QQQ Trust | US Tech/Growth | Nasdaq-100 exposure |
| VTI | Vanguard Total Stock Market | US Total Market | Broadest US equity |
| IWM | iShares Russell 2000 | US Small Cap | Small-cap exposure |
| VIG | Vanguard Dividend Appreciation | US Dividend Growth | Quality dividend growers |
| SCHD | Schwab US Dividend Equity | US High Dividend | High yield dividend |
| XLK | Technology Select Sector SPDR | US Sector - Tech | Technology sector |
| XLF | Financial Select Sector SPDR | US Sector - Financials | Financial sector |
| XLE | Energy Select Sector SPDR | US Sector - Energy | Energy sector |
| XLV | Health Care Select Sector SPDR | US Sector - Healthcare | Healthcare sector |
| XLI | Industrial Select Sector SPDR | US Sector - Industrials | Industrial sector |

### Individual Stocks (scope: etf_and_stocks)

| Ticker | Name | Sector | Notes |
|--------|------|--------|-------|
| AAPL | Apple Inc. | Technology | Mega cap, consumer tech |
| MSFT | Microsoft Corp. | Technology | Mega cap, enterprise/cloud |
| GOOGL | Alphabet Inc. | Technology | Mega cap, advertising/cloud |
| AMZN | Amazon.com Inc. | Consumer/Tech | Mega cap, e-commerce/cloud |
| NVDA | NVIDIA Corp. | Technology | AI/semiconductor leader |
| META | Meta Platforms Inc. | Technology | Social media/metaverse |
| TSLA | Tesla Inc. | Consumer/Auto | EV/energy leader |
| BRK.B | Berkshire Hathaway B | Financials | Diversified conglomerate |
| JPM | JPMorgan Chase | Financials | Largest US bank |
| JNJ | Johnson & Johnson | Healthcare | Diversified healthcare |
| V | Visa Inc. | Financials | Payment network |
| PG | Procter & Gamble | Consumer Staples | Defensive consumer |

## KR Equity

### ETFs (scope: etf_only)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| KODEX 200 | KODEX 200 ETF | KR Large Cap Index | KOSPI 200 tracking |
| KODEX 코스닥150 | KODEX KOSDAQ 150 | KR Growth | KOSDAQ 150 tracking |
| TIGER 미국S&P500 | TIGER US S&P 500 | US Equity (KRW) | KRW-denominated US equity |
| KODEX 삼성그룹 | KODEX Samsung Group | KR Conglomerate | Samsung group exposure |
| TIGER 반도체 | TIGER Semiconductor | KR Sector - Semi | Korean semiconductor sector |
| KODEX 배당가치 | KODEX Dividend Value | KR Dividend | Korean high dividend |
| KODEX 2차전지산업 | KODEX Secondary Battery | KR Sector - Battery | Battery/EV supply chain |

### Individual Stocks (scope: etf_and_stocks)

| Ticker | Name | Sector | Notes |
|--------|------|--------|-------|
| 005930 | Samsung Electronics | Technology/Semi | Korea's largest company |
| 000660 | SK Hynix | Technology/Semi | Memory semiconductor |
| 035420 | NAVER Corp. | Internet/Platform | Korea's largest internet co |
| 035720 | Kakao Corp. | Internet/Platform | Messaging/fintech platform |
| 005380 | Hyundai Motor | Auto | Major Korean automaker |
| 373220 | LG Energy Solution | Battery | EV battery manufacturer |
| 068270 | Celltrion | Bio/Pharma | Biosimilar leader |
| 005490 | POSCO Holdings | Materials/Steel | Steel conglomerate |

## Bonds

### ETFs (scope: etf_only)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| AGG | iShares Core US Aggregate Bond | US Aggregate | Core US bond exposure |
| BND | Vanguard Total Bond Market | US Total Bond | Broad US bond market |
| TLT | iShares 20+ Year Treasury | US Long-Term Treasury | Duration/rate sensitivity |
| SHY | iShares 1-3 Year Treasury | US Short-Term Treasury | Low duration, defensive |
| IEF | iShares 7-10 Year Treasury | US Mid-Term Treasury | Intermediate duration |
| LQD | iShares Investment Grade Corp | US IG Corporate | Investment grade corporate |
| HYG | iShares High Yield Corporate | US HY Corporate | High yield (junk) bonds |
| TIP | iShares TIPS Bond | US Inflation-Protected | Inflation hedge |
| KODEX 국고채10년 | KODEX KR Treasury 10Y | KR Government Bond | Korean 10-year treasury |
| TIGER 단기채권 | TIGER Short-Term Bond | KR Short-Term Bond | Korean short-term bond |

## Alternatives (scope: broad)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| GLD | SPDR Gold Shares | Gold | Gold bullion exposure |
| IAU | iShares Gold Trust | Gold | Lower-cost gold ETF |
| SLV | iShares Silver Trust | Silver | Silver bullion exposure |
| VNQ | Vanguard Real Estate | US REITs | Real estate exposure |
| DBC | Invesco DB Commodity | Commodities | Broad commodity basket |
| PDBC | Invesco Optimum Yield Diversified | Commodities | Optimized commodity |
| KODEX 골드선물(H) | KODEX Gold Futures (H) | Gold (KRW) | KRW-denominated gold |

## Cash Equivalents (scope: etf_only)

| Ticker | Name | Category | Notes |
|--------|------|----------|-------|
| SHV | iShares Short Treasury Bond | US Ultra Short | Near-cash, minimal risk |
| BIL | SPDR Bloomberg 1-3M T-Bill | US T-Bill | Treasury bill proxy |
| SGOV | iShares 0-3 Month Treasury | US T-Bill | Ultra-short treasury |
| CMA 머니마켓 | CMA Money Market | KR Money Market | Korean money market |

## Selection Rules

1. Select 2–4 tickers per asset class
2. Prefer ETFs over individual stocks for diversification
3. For `etf_only` scope: use ETFs exclusively
4. For `etf_and_stocks`: mix ETFs and individual stocks based on sector tilt
5. For `broad`: include alternatives (gold, REITs, commodities) when environment supports it
6. Korean tickers used when user's `market_preference` includes KR or is "mixed"
7. Every selected holding must have a `rationale` tied to environment assessment
8. Every holding carries a `source_tag` from data collection
```

- [ ] **Step 2: Commit**

```bash
git add references/asset-universe.md
git commit -m "docs: add asset universe reference with scope-based filtering"
```

### Task 4: Create macro-indicator-ranges.md

**Files:**
- Create: `references/macro-indicator-ranges.md`

Critical reference for data-validator.py (sanity checks) and environment-scorer.py (position relative to historical ranges).

- [ ] **Step 1: Create macro-indicator-ranges.md**

Create `references/macro-indicator-ranges.md`:
```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add references/macro-indicator-ranges.md
git commit -m "docs: add macro indicator ranges reference for scoring and validation"
```

### Task 5: Create portfolio-construction-rules.md

**Files:**
- Create: `references/portfolio-construction-rules.md`

- [ ] **Step 1: Create portfolio-construction-rules.md**

Create `references/portfolio-construction-rules.md`:
```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add references/portfolio-construction-rules.md
git commit -m "docs: add portfolio construction rules reference"
```

### Task 6: Create Output Templates

**Files:**
- Create: `references/output-templates/color-system.md`
- Create: `references/output-templates/dashboard-template.md`
- Create: `references/output-templates/memo-template.md`

- [ ] **Step 1: Create color-system.md**

Create `references/output-templates/color-system.md`:
```markdown
# Color System

## TailwindCSS Classes (CDN)

Dashboard uses dark theme. Include CDN:
```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### Background & Layout

- Page: `bg-gray-950 text-gray-100`
- Cards: `bg-gray-900 border border-gray-800 rounded-xl p-6`
- Section headers: `text-xl font-bold text-gray-100 mb-4`

### Risk Level Badges

| Level | Classes |
|-------|---------|
| Aggressive | `bg-red-900/50 text-red-300 border border-red-700 px-3 py-1 rounded-full text-sm` |
| Moderate | `bg-yellow-900/50 text-yellow-300 border border-yellow-700 px-3 py-1 rounded-full text-sm` |
| Conservative | `bg-blue-900/50 text-blue-300 border border-blue-700 px-3 py-1 rounded-full text-sm` |

### Data Confidence Badges

| Grade | Classes |
|-------|---------|
| A | `bg-emerald-900/50 text-emerald-300 border border-emerald-700` |
| B | `bg-blue-900/50 text-blue-300 border border-blue-700` |
| C | `bg-amber-900/50 text-amber-300 border border-amber-700` |
| D | `bg-red-900/50 text-red-300 border border-red-700` |

### Environment Score Colors

| Score Range | Color |
|-------------|-------|
| 8.0–10.0 | `text-emerald-400` (very positive) |
| 6.0–7.9 | `text-blue-400` (positive) |
| 4.0–5.9 | `text-yellow-400` (neutral) |
| 2.0–3.9 | `text-orange-400` (negative) |
| 1.0–1.9 | `text-red-400` (very negative) |

### Direction Indicators

| Direction | Display | Color |
|-----------|---------|-------|
| positive | ▲ | `text-emerald-400` |
| neutral-positive | ↗ | `text-blue-400` |
| neutral | → | `text-yellow-400` |
| neutral-negative | ↘ | `text-orange-400` |
| negative | ▼ | `text-red-400` |

### Chart.js Configuration

#### Pie Chart (Asset Allocation)

```javascript
const pieColors = {
  us_equity: '#3b82f6',   // blue-500
  kr_equity: '#8b5cf6',   // violet-500
  bonds: '#10b981',       // emerald-500
  alternatives: '#f59e0b', // amber-500
  cash: '#6b7280'         // gray-500
};
```

#### Scatter Plot (Risk/Return)

```javascript
const scatterColors = {
  aggressive: '#ef4444',   // red-500
  moderate: '#eab308',     // yellow-500
  conservative: '#3b82f6'  // blue-500
};
```

#### Scenario Bar Chart

```javascript
const scenarioColors = {
  bull: '#10b981',  // emerald-500
  base: '#6b7280',  // gray-500
  bear: '#ef4444'   // red-500
};
```
```

- [ ] **Step 2: Create dashboard-template.md**

Create `references/output-templates/dashboard-template.md`:
```markdown
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
```

- [ ] **Step 3: Create memo-template.md**

Create `references/output-templates/memo-template.md`:
```markdown
# DOCX Investment Memo Template

## Document Style

- Font: Calibri (body), Calibri Bold (headings)
- Body size: 11pt
- Heading 1: 16pt bold
- Heading 2: 13pt bold
- Margins: 2.54cm all sides (Word default)
- Page size: A4
- Line spacing: 1.15

## Section Structure

### Cover Page (Page 1)

- Title: "Investment Portfolio Recommendation"
- Subtitle: "{budget_formatted} | {period} | {risk_tolerance} profile"
- Date: analysis date
- Data confidence: overall grade
- Disclaimer: abbreviated version

### 1. Executive Summary (200–300 words)

- Investment objective (from user profile)
- Current market regime classification
- Recommended approach summary
- 3-option overview (1 sentence each)

### 2. Market Environment Analysis (400–600 words)

#### 2.1 Macroeconomic Environment
- US macro summary with key indicators and grades
- KR macro summary (if applicable)

#### 2.2 Political & Geopolitical Landscape
- Key political developments and impact assessment

#### 2.3 Market Fundamentals
- Valuation levels, sector performance
- US and KR market comparisons

#### 2.4 Sentiment Analysis
- VIX, Fear & Greed, fund flows interpretation

### 3. Regime Diagnosis (100–150 words)

- Current regime classification with rationale
- Key indicators supporting the classification

### 4–6. Portfolio Options (300–400 words each)

For each option (Aggressive, Moderate, Conservative):

#### N.1 Allocation
- Table: Asset Class | Weight (%) | Rationale

#### N.2 Key Holdings
- Table: Ticker | Name | Weight | Selection Rationale | Source

#### N.3 Scenario Analysis
- Bull/Base/Bear table with assumptions and expected returns
- Risk-return score

#### N.4 Risk Considerations
- Top 2–3 risks with mechanism chains

### 7. Comparative Analysis (200–300 words)

- Side-by-side option comparison
- When to choose each option
- Key differentiation factors

### 8. Risk Analysis (200–300 words)

- Cross-cutting risks (affect all options)
- Mechanism chains: Risk → Impact → Response

### 9. Rebalancing Guidance (100–150 words)

- Suggested trigger conditions
- Monitoring frequency

### 10. Disclaimer (standard text)

"This analysis is generated by an AI assistant and is for informational purposes only. It does not constitute investment advice, a recommendation, or an offer to buy or sell any securities. Past performance does not guarantee future results. Investment decisions should be made in consultation with a qualified financial advisor. The AI assistant does not have a fiduciary duty to the user."

## Table Formatting

- Header row: bold, light gray background
- Border: single, 0.5pt
- Alignment: text left, numbers right
- Percentage format: "45.0%"
```

- [ ] **Step 3: Commit all output templates**

```bash
git add references/output-templates/
git commit -m "docs: add output templates (color-system, dashboard, memo)"
```

---

## Chunk 3: Python Scripts — Environment Pipeline

### Task 7: staleness_checker.py

**Files:**
- Create: `.claude/skills/staleness-checker/scripts/staleness_checker.py`
- Create: `tests/scripts/test_staleness_checker.py`

- [ ] **Step 1: Write failing tests**

Create `tests/scripts/test_staleness_checker.py`:
```python
"""Tests for staleness-checker.py"""
import json
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/staleness-checker/scripts"))

from staleness_checker import check_staleness, STALENESS_RULES


class TestStalenessRules:
    """Test staleness rule definitions."""

    def test_all_four_dimensions_defined(self):
        assert set(STALENESS_RULES.keys()) == {"macro", "political", "fundamentals", "sentiment"}

    def test_macro_threshold_24h(self):
        assert STALENESS_RULES["macro"]["threshold_hours"] == 24

    def test_political_threshold_7d(self):
        assert STALENESS_RULES["political"]["threshold_hours"] == 168  # 7 * 24

    def test_fundamentals_threshold_3d(self):
        assert STALENESS_RULES["fundamentals"]["threshold_hours"] == 72  # 3 * 24

    def test_sentiment_threshold_12h(self):
        assert STALENESS_RULES["sentiment"]["threshold_hours"] == 12


class TestCheckStaleness:
    """Test the main staleness check function."""

    def _make_latest_json(self, tmpdir, dimension, hours_ago):
        """Helper: create a latest.json file with a timestamp N hours ago."""
        dim_dir = os.path.join(tmpdir, "data", dimension)
        os.makedirs(dim_dir, exist_ok=True)
        ts = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()
        data = {"collection_timestamp": ts, "indicators": []}
        path = os.path.join(dim_dir, "latest.json")
        with open(path, "w") as f:
            json.dump(data, f)
        return path

    def test_no_existing_data_returns_all_full(self):
        """When no latest.json files exist, all dimensions should be FULL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_staleness(tmpdir)
            for dim in ["macro", "political", "fundamentals", "sentiment"]:
                assert result["dimensions"][dim]["routing"] == "FULL"

    def test_fresh_macro_returns_reuse(self):
        """Macro data < 24h old should be REUSE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "macro", hours_ago=6)
            result = check_staleness(tmpdir)
            assert result["dimensions"]["macro"]["routing"] == "REUSE"

    def test_stale_macro_returns_full(self):
        """Macro data >= 24h old should be FULL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "macro", hours_ago=25)
            result = check_staleness(tmpdir)
            assert result["dimensions"]["macro"]["routing"] == "FULL"

    def test_fresh_political_7_days(self):
        """Political data < 7 days old should be REUSE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "political", hours_ago=120)  # 5 days
            result = check_staleness(tmpdir)
            assert result["dimensions"]["political"]["routing"] == "REUSE"

    def test_stale_political(self):
        """Political data >= 7 days old should be FULL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "political", hours_ago=170)  # 7+ days
            result = check_staleness(tmpdir)
            assert result["dimensions"]["political"]["routing"] == "FULL"

    def test_mixed_staleness(self):
        """Different dimensions can have different routing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "macro", hours_ago=6)       # REUSE
            self._make_latest_json(tmpdir, "political", hours_ago=200) # FULL
            self._make_latest_json(tmpdir, "fundamentals", hours_ago=48) # FULL (>72h? no, 48<72)
            # sentiment: no file → FULL
            result = check_staleness(tmpdir)
            assert result["dimensions"]["macro"]["routing"] == "REUSE"
            assert result["dimensions"]["political"]["routing"] == "FULL"
            assert result["dimensions"]["fundamentals"]["routing"] == "REUSE"
            assert result["dimensions"]["sentiment"]["routing"] == "FULL"

    def test_output_schema(self):
        """Output should have correct schema structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_staleness(tmpdir)
            assert "check_timestamp" in result
            assert "dimensions" in result
            for dim in ["macro", "political", "fundamentals", "sentiment"]:
                assert "routing" in result["dimensions"][dim]
                assert "reason" in result["dimensions"][dim]
                assert result["dimensions"][dim]["routing"] in ("REUSE", "FULL")

    def test_corrupted_json_falls_back_to_full(self):
        """Corrupted latest.json should fall back to FULL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dim_dir = os.path.join(tmpdir, "data", "macro")
            os.makedirs(dim_dir, exist_ok=True)
            with open(os.path.join(dim_dir, "latest.json"), "w") as f:
                f.write("NOT VALID JSON{{{")
            result = check_staleness(tmpdir)
            assert result["dimensions"]["macro"]["routing"] == "FULL"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor
source .venv/bin/activate
pytest tests/scripts/test_staleness_checker.py -v
```
Expected: FAIL (ModuleNotFoundError: staleness_checker)

- [ ] **Step 3: Write implementation**

Create `.claude/skills/staleness-checker/scripts/staleness_checker.py`:
```python
#!/usr/bin/env python3
"""
Staleness Checker — Step 0 of the Investment Portfolio Advisor pipeline.

Checks existing environment data freshness and determines per-dimension
REUSE/FULL routing decisions.

Usage:
    python staleness_checker.py --output-dir <path_to_output_dir>
    python staleness_checker.py --output-dir output/ --write

Output: JSON routing decision to stdout (or writes to output/staleness-routing.json with --write)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta


STALENESS_RULES = {
    "macro": {
        "threshold_hours": 24,
        "description": "Macroeconomic data",
    },
    "political": {
        "threshold_hours": 168,  # 7 days
        "description": "Political/geopolitical data",
    },
    "fundamentals": {
        "threshold_hours": 72,  # 3 days
        "description": "Market fundamentals data",
    },
    "sentiment": {
        "threshold_hours": 12,
        "description": "Market sentiment data",
    },
}

DIMENSION_FILE_MAP = {
    "macro": "data/macro/latest.json",
    "political": "data/political/latest.json",
    "fundamentals": "data/fundamentals/latest.json",
    "sentiment": "data/sentiment/latest.json",
}


def _read_timestamp(filepath: str) -> datetime | None:
    """Read collection_timestamp from a latest.json file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        ts_str = data.get("collection_timestamp")
        if not ts_str:
            return None
        return datetime.fromisoformat(ts_str)
    except (json.JSONDecodeError, FileNotFoundError, KeyError, ValueError):
        return None


def check_staleness(output_dir: str) -> dict:
    """
    Check staleness of all 4 dimensions.

    Args:
        output_dir: Path to the output directory containing data/ subdirectories.

    Returns:
        dict with routing decisions per dimension.
    """
    now = datetime.now(timezone.utc)
    dimensions = {}

    for dim, rule in STALENESS_RULES.items():
        filepath = os.path.join(output_dir, DIMENSION_FILE_MAP[dim])
        timestamp = _read_timestamp(filepath)

        if timestamp is None:
            dimensions[dim] = {
                "routing": "FULL",
                "reason": "No existing data found",
                "last_collected": None,
                "age_hours": None,
                "threshold_hours": rule["threshold_hours"],
            }
        else:
            # Ensure timezone-aware comparison
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            age = now - timestamp
            age_hours = age.total_seconds() / 3600

            if age_hours < rule["threshold_hours"]:
                routing = "REUSE"
                reason = f"Data is {age_hours:.1f}h old (threshold: {rule['threshold_hours']}h)"
            else:
                routing = "FULL"
                reason = f"Data is {age_hours:.1f}h old, exceeds threshold of {rule['threshold_hours']}h"

            dimensions[dim] = {
                "routing": routing,
                "reason": reason,
                "last_collected": timestamp.isoformat(),
                "age_hours": round(age_hours, 1),
                "threshold_hours": rule["threshold_hours"],
            }

    return {
        "check_timestamp": now.isoformat(),
        "dimensions": dimensions,
    }


def main():
    parser = argparse.ArgumentParser(description="Check data staleness for environment dimensions")
    parser.add_argument("--output-dir", required=True, help="Path to output/ directory")
    parser.add_argument("--write", action="store_true", help="Write result to staleness-routing.json")
    args = parser.parse_args()

    result = check_staleness(args.output_dir)

    if args.write:
        out_path = os.path.join(args.output_dir, "staleness-routing.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Written to {out_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/scripts/test_staleness_checker.py -v
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/staleness-checker/scripts/staleness_checker.py tests/scripts/test_staleness_checker.py
git commit -m "feat: add staleness-checker script with tests (Step 0)"
```

### Task 8: data_validator.py

**Files:**
- Create: `.claude/skills/data-validator/scripts/data_validator.py`
- Create: `tests/scripts/test_data_validator.py`

- [ ] **Step 1: Write failing tests**

Create `tests/scripts/test_data_validator.py`:
```python
"""Tests for data-validator.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/data-validator/scripts"))

from data_validator import (
    validate_all,
    check_arithmetic_consistency,
    cross_reference_check,
    sanity_check,
    assign_grade,
    load_indicator_ranges,
)


# --- Sample test data ---

SAMPLE_MACRO = {
    "collection_timestamp": "2026-03-17T10:05:00Z",
    "indicators": [
        {
            "id": "us_gdp_growth",
            "category": "us",
            "name": "US GDP Growth Rate",
            "value": 2.3,
            "unit": "%",
            "period": "Q4 2025",
            "source_tag": "[Official]",
            "source_url": "https://bea.gov",
            "retrieved_at": "2026-03-17T10:05:00Z",
        },
        {
            "id": "us_cpi",
            "category": "us",
            "name": "US CPI YoY",
            "value": 3.1,
            "unit": "%",
            "period": "Feb 2026",
            "source_tag": "[Official]",
            "source_url": "https://bls.gov",
            "retrieved_at": "2026-03-17T10:05:00Z",
        },
    ],
    "collection_gaps": [],
}

SAMPLE_POLITICAL = {
    "collection_timestamp": "2026-03-17T10:10:00Z",
    "developments": [
        {
            "id": "us_tariff_policy",
            "category": "us_trade",
            "headline": "New tariffs announced",
            "summary": "25% tariffs on imports",
            "impact_assessment": "negative",
            "affected_sectors": ["technology", "manufacturing"],
            "source_tag": "[News]",
            "source_url": "https://reuters.com",
            "retrieved_at": "2026-03-17T10:10:00Z",
        }
    ],
    "collection_gaps": [],
}

SAMPLE_FUNDAMENTALS = {
    "collection_timestamp": "2026-03-17T10:15:00Z",
    "market_metrics": [
        {
            "id": "sp500_pe",
            "market": "us",
            "name": "S&P 500 P/E",
            "value": 22.5,
            "unit": "ratio",
            "period": "current",
            "source_tag": "[Portal]",
            "source_url": "https://yahoo.com",
            "retrieved_at": "2026-03-17T10:15:00Z",
        }
    ],
    "sector_performance": [],
    "collection_gaps": [],
}

SAMPLE_SENTIMENT = {
    "collection_timestamp": "2026-03-17T10:20:00Z",
    "indicators": [
        {
            "id": "vix",
            "name": "VIX",
            "value": 18.5,
            "unit": "index",
            "interpretation": "moderate_fear",
            "source_tag": "[Portal]",
            "source_url": "https://cboe.com",
            "retrieved_at": "2026-03-17T10:20:00Z",
        }
    ],
    "collection_gaps": [],
}


class TestAssignGrade:
    def test_official_source_gets_grade_a(self):
        grade = assign_grade(source_tag="[Official]", source_count=1, sanity_passed=True)
        assert grade == "A"

    def test_two_sources_within_5pct_gets_grade_b(self):
        grade = assign_grade(source_tag="[Portal]", source_count=2, sanity_passed=True)
        assert grade == "B"

    def test_single_source_gets_grade_c(self):
        grade = assign_grade(source_tag="[Portal]", source_count=1, sanity_passed=True)
        assert grade == "C"

    def test_failed_sanity_gets_grade_d(self):
        grade = assign_grade(source_tag="[Portal]", source_count=1, sanity_passed=False)
        assert grade == "D"


class TestSanityCheck:
    def test_normal_gdp_passes(self):
        alert = sanity_check("us_gdp_growth", 2.3)
        assert alert is None

    def test_extreme_gdp_fails(self):
        alert = sanity_check("us_gdp_growth", 50.0)
        assert alert is not None
        assert "SANITY_ALERT" in alert["type"]

    def test_unknown_indicator_passes(self):
        alert = sanity_check("unknown_indicator", 999)
        assert alert is None  # No range defined → no alert


class TestValidateAll:
    def test_produces_valid_output_schema(self):
        result = validate_all(
            macro=SAMPLE_MACRO,
            political=SAMPLE_POLITICAL,
            fundamentals=SAMPLE_FUNDAMENTALS,
            sentiment=SAMPLE_SENTIMENT,
        )
        assert "validation_timestamp" in result
        assert "overall_data_grade" in result
        assert "validated_indicators" in result
        assert "exclusions" in result
        for dim in ["macro", "political", "fundamentals", "sentiment"]:
            assert dim in result["validated_indicators"]

    def test_grade_d_items_excluded(self):
        # Create a sentiment indicator that fails sanity check
        bad_sentiment = {
            "collection_timestamp": "2026-03-17T10:20:00Z",
            "indicators": [
                {
                    "id": "vix",
                    "name": "VIX",
                    "value": 150.0,  # Way beyond sanity max of 100
                    "unit": "index",
                    "source_tag": "[Portal]",
                    "source_url": "https://cboe.com",
                    "retrieved_at": "2026-03-17T10:20:00Z",
                }
            ],
            "collection_gaps": [],
        }
        result = validate_all(
            macro=SAMPLE_MACRO,
            political=SAMPLE_POLITICAL,
            fundamentals=SAMPLE_FUNDAMENTALS,
            sentiment=bad_sentiment,
        )
        # VIX with value 150 should trigger sanity alert
        assert len(result.get("sanity_alerts", [])) > 0

    def test_overall_grade_computed(self):
        result = validate_all(
            macro=SAMPLE_MACRO,
            political=SAMPLE_POLITICAL,
            fundamentals=SAMPLE_FUNDAMENTALS,
            sentiment=SAMPLE_SENTIMENT,
        )
        assert result["overall_data_grade"] in ("A", "B", "C", "D")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/scripts/test_data_validator.py -v
```
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write implementation**

Create `.claude/skills/data-validator/scripts/data_validator.py`:
```python
#!/usr/bin/env python3
"""
Data Validator — Step 6 of the Investment Portfolio Advisor pipeline.

Validates 4 raw data JSON files through 3-stage validation:
  1. Arithmetic consistency check
  2. Cross-reference check (multi-source comparison)
  3. Sanity check (against historical ranges)

Assigns confidence grades (A/B/C/D) to each data point.

Usage:
    python data_validator.py --output-dir <path> [--write]
    python data_validator.py --macro <file> --political <file> --fundamentals <file> --sentiment <file>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def load_indicator_ranges() -> dict:
    """Return sanity ranges per indicator ID (hardcoded from macro-indicator-ranges.md)."""
    _SANITY_RANGES = {
        "us_gdp_growth": (-35.0, 40.0),
        "us_cpi": (-5.0, 15.0),
        "us_pce": (-5.0, 12.0),
        "us_fed_rate": (0.0, 10.0),
        "us_unemployment": (0.0, 20.0),
        "us_10y_yield": (0.0, 8.0),
        "us_2y_yield": (0.0, 8.0),
        "us_yield_spread": (-200, 400),
        "kr_gdp_growth": (-10.0, 12.0),
        "kr_cpi": (-2.0, 10.0),
        "kr_base_rate": (0.0, 8.0),
        "kr_usd_fx": (800, 1800),
        "sp500_pe": (5.0, 50.0),
        "sp500_cape": (8.0, 55.0),
        "kospi_per": (4.0, 35.0),
        "kospi_pbr": (0.3, 3.0),
        "us_ig_spread": (50, 800),
        "us_hy_spread": (200, 2500),
        "vix": (5.0, 100.0),
        "fear_greed": (0, 100),
        "put_call_ratio": (0.3, 3.0),
        "aaii_bull": (0.0, 100.0),
    }
    return _SANITY_RANGES


_SANITY_RANGES = load_indicator_ranges()


def sanity_check(indicator_id: str, value: float) -> dict | None:
    """
    Check if a value falls within sanity bounds.

    Returns None if OK, or a SANITY_ALERT dict if outside bounds.
    """
    if indicator_id not in _SANITY_RANGES:
        return None

    sanity_min, sanity_max = _SANITY_RANGES[indicator_id]
    if value < sanity_min or value > sanity_max:
        return {
            "type": "SANITY_ALERT",
            "indicator_id": indicator_id,
            "value": value,
            "sanity_min": sanity_min,
            "sanity_max": sanity_max,
            "message": f"{indicator_id}={value} outside sanity range [{sanity_min}, {sanity_max}]",
        }
    return None


def check_arithmetic_consistency(indicators: list[dict]) -> list[dict]:
    """
    Layer 1: Check arithmetic consistency between related indicators.

    For portfolio-advisor, this is simpler than stock-analysis since
    we deal with macro indicators rather than financial ratios.
    Currently checks: yield spread = 10Y - 2Y
    """
    inconsistencies = []
    values = {ind["id"]: ind["value"] for ind in indicators if ind.get("value") is not None}

    # Check yield spread consistency
    if all(k in values for k in ("us_10y_yield", "us_2y_yield", "us_yield_spread")):
        calculated = (values["us_10y_yield"] - values["us_2y_yield"]) * 100  # to bps
        reported = values["us_yield_spread"]
        if abs(calculated - reported) > 20:  # 20 bps tolerance
            inconsistencies.append({
                "type": "ARITHMETIC_INCONSISTENCY",
                "indicator": "us_yield_spread",
                "reported": reported,
                "calculated": round(calculated, 1),
                "difference_bps": round(abs(calculated - reported), 1),
            })

    return inconsistencies


def cross_reference_check(indicators: list[dict]) -> list[dict]:
    """
    Layer 2: Cross-reference check.

    In Phase 1, most indicators come from single web searches.
    This layer groups by indicator ID and checks for multi-source agreement.
    """
    # Group by id
    by_id = {}
    for ind in indicators:
        ind_id = ind["id"]
        if ind_id not in by_id:
            by_id[ind_id] = []
        by_id[ind_id].append(ind)

    cross_refs = []
    for ind_id, sources in by_id.items():
        if len(sources) >= 2:
            values = [s["value"] for s in sources if s.get("value") is not None]
            if len(values) >= 2:
                avg = sum(values) / len(values)
                max_diff = max(abs(v - avg) / avg * 100 for v in values) if avg != 0 else 0
                cross_refs.append({
                    "indicator_id": ind_id,
                    "source_count": len(values),
                    "values": values,
                    "max_difference_pct": round(max_diff, 2),
                    "agreement": max_diff <= 5.0,
                })
    return cross_refs


def assign_grade(source_tag: str, source_count: int = 1, sanity_passed: bool = True) -> str:
    """
    Assign confidence grade based on source authority and verification.

    Grade A: Official government statistics + sanity passed
    Grade B: 2+ independent sources or official cross-referenced
    Grade C: Single source, sanity passed
    Grade D: Unverifiable or sanity failed
    """
    if not sanity_passed:
        return "D"
    if source_tag == "[Official]":
        return "A"
    if source_count >= 2:
        return "B"
    if source_count == 1:
        return "C"
    return "D"


def _validate_dimension_indicators(indicators: list[dict], dimension: str) -> tuple[list[dict], list[dict], list[dict]]:
    """Validate indicators for a single dimension. Returns (validated, exclusions, sanity_alerts)."""
    validated = []
    exclusions = []
    sanity_alerts = []

    for ind in indicators:
        ind_id = ind.get("id", "unknown")
        value = ind.get("value")

        if value is None:
            exclusions.append({
                "id": ind_id,
                "reason": "Value is null",
                "original_grade": "D",
            })
            continue

        # Sanity check
        alert = sanity_check(ind_id, value)
        sanity_passed = alert is None
        if alert:
            sanity_alerts.append(alert)

        # Determine source count (Phase 1: usually 1)
        source_count = 1
        source_tag = ind.get("source_tag", "")

        grade = assign_grade(source_tag, source_count, sanity_passed)

        if grade == "D":
            exclusions.append({
                "id": ind_id,
                "reason": alert["message"] if alert else "Unverifiable",
                "original_grade": "D",
            })
        else:
            validated.append({
                "id": ind_id,
                "value": value,
                "grade": grade,
                "source_tag": source_tag,
            })

    return validated, exclusions, sanity_alerts


def _validate_political(developments: list[dict]) -> tuple[list[dict], list[dict]]:
    """Validate political developments (qualitative — simpler grading)."""
    validated = []
    exclusions = []

    for dev in developments:
        dev_id = dev.get("id", "unknown")
        source_tag = dev.get("source_tag", "")
        # Political data is qualitative — grade based on source presence
        if source_tag:
            grade = "C" if source_tag == "[News]" else "B"
            validated.append({
                "id": dev_id,
                "headline": dev.get("headline", ""),
                "impact_assessment": dev.get("impact_assessment", "neutral"),
                "grade": grade,
                "source_tag": source_tag,
            })
        else:
            exclusions.append({
                "id": dev_id,
                "reason": "No source tag",
                "original_grade": "D",
            })

    return validated, exclusions


def _compute_overall_grade(all_grades: list[str]) -> str:
    """Compute overall data grade from individual grades."""
    if not all_grades:
        return "D"

    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for g in all_grades:
        grade_counts[g] = grade_counts.get(g, 0) + 1

    total = len(all_grades)
    a_b_ratio = (grade_counts["A"] + grade_counts["B"]) / total

    if a_b_ratio >= 0.8:
        return "A" if grade_counts["A"] > grade_counts["B"] else "B"
    elif a_b_ratio >= 0.5:
        return "B"
    elif grade_counts["D"] / total < 0.3:
        return "C"
    else:
        return "D"


def validate_all(
    macro: dict,
    political: dict,
    fundamentals: dict,
    sentiment: dict,
) -> dict:
    """
    Main validation entry point. Validates all 4 raw data files.

    Returns validated-data.json structure.
    """
    now = datetime.now(timezone.utc)
    all_exclusions = []
    all_sanity_alerts = []
    all_grades = []

    # Macro indicators
    macro_validated, macro_excl, macro_alerts = _validate_dimension_indicators(
        macro.get("indicators", []), "macro"
    )
    all_exclusions.extend(macro_excl)
    all_sanity_alerts.extend(macro_alerts)
    all_grades.extend(v["grade"] for v in macro_validated)

    # Political developments
    political_validated, political_excl = _validate_political(
        political.get("developments", [])
    )
    all_exclusions.extend(political_excl)
    all_grades.extend(v["grade"] for v in political_validated)

    # Fundamentals
    fund_indicators = fundamentals.get("market_metrics", [])
    fund_validated, fund_excl, fund_alerts = _validate_dimension_indicators(
        fund_indicators, "fundamentals"
    )
    all_exclusions.extend(fund_excl)
    all_sanity_alerts.extend(fund_alerts)
    all_grades.extend(v["grade"] for v in fund_validated)

    # Sentiment
    sent_validated, sent_excl, sent_alerts = _validate_dimension_indicators(
        sentiment.get("indicators", []), "sentiment"
    )
    all_exclusions.extend(sent_excl)
    all_sanity_alerts.extend(sent_alerts)
    all_grades.extend(v["grade"] for v in sent_validated)

    # Arithmetic consistency (macro only for now)
    arith_inconsistencies = check_arithmetic_consistency(macro.get("indicators", []))

    overall_grade = _compute_overall_grade(all_grades)

    return {
        "validation_timestamp": now.isoformat(),
        "overall_data_grade": overall_grade,
        "validated_indicators": {
            "macro": macro_validated,
            "political": political_validated,
            "fundamentals": fund_validated,
            "sentiment": sent_validated,
        },
        "exclusions": all_exclusions,
        "arithmetic_inconsistencies": arith_inconsistencies,
        "sanity_alerts": all_sanity_alerts,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate raw environment data")
    parser.add_argument("--output-dir", help="Path to output/ directory (reads raw files from data/)")
    parser.add_argument("--macro", help="Path to macro-raw.json")
    parser.add_argument("--political", help="Path to political-raw.json")
    parser.add_argument("--fundamentals", help="Path to fundamentals-raw.json")
    parser.add_argument("--sentiment", help="Path to sentiment-raw.json")
    parser.add_argument("--write", action="store_true", help="Write to validated-data.json")
    args = parser.parse_args()

    if args.output_dir:
        base = args.output_dir
        paths = {
            "macro": os.path.join(base, "data/macro/macro-raw.json"),
            "political": os.path.join(base, "data/political/political-raw.json"),
            "fundamentals": os.path.join(base, "data/fundamentals/fundamentals-raw.json"),
            "sentiment": os.path.join(base, "data/sentiment/sentiment-raw.json"),
        }
    else:
        paths = {
            "macro": args.macro,
            "political": args.political,
            "fundamentals": args.fundamentals,
            "sentiment": args.sentiment,
        }

    data = {}
    for key, path in paths.items():
        if path and os.path.exists(path):
            with open(path) as f:
                data[key] = json.load(f)
        else:
            data[key] = {"indicators": [], "developments": [], "market_metrics": [], "collection_gaps": []}

    result = validate_all(**data)

    if args.write and args.output_dir:
        out_path = os.path.join(args.output_dir, "validated-data.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Written to {out_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/scripts/test_data_validator.py -v
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/data-validator/scripts/data_validator.py tests/scripts/test_data_validator.py
git commit -m "feat: add data-validator script with 3-layer validation and grading (Step 6)"
```

### Task 9: environment-scorer.py

**Files:**
- Create: `.claude/skills/environment-scorer/scripts/environment_scorer.py`
- Create: `tests/scripts/test_environment_scorer.py`

- [ ] **Step 1: Write failing tests**

Create `tests/scripts/test_environment_scorer.py`:
```python
"""Tests for environment-scorer.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/environment-scorer/scripts"))

from environment_scorer import (
    compute_position,
    score_dimension,
    compute_all_positions,
    HISTORICAL_RANGES,
)


class TestComputePosition:
    def test_at_historical_low(self):
        pos = compute_position(9.0, low=9.0, high=82.0)
        assert pos == 0.0

    def test_at_historical_high(self):
        pos = compute_position(82.0, low=9.0, high=82.0)
        assert pos == 1.0

    def test_at_median(self):
        pos = compute_position(45.5, low=9.0, high=82.0)
        assert 0.4 < pos < 0.6

    def test_below_low_clamped(self):
        pos = compute_position(5.0, low=9.0, high=82.0)
        assert pos == 0.0

    def test_above_high_clamped(self):
        pos = compute_position(90.0, low=9.0, high=82.0)
        assert pos == 1.0


class TestScoreDimension:
    def test_returns_valid_structure(self):
        indicators = [
            {"id": "us_gdp_growth", "value": 2.3, "grade": "A"},
            {"id": "us_cpi", "value": 3.1, "grade": "B"},
            {"id": "us_fed_rate", "value": 4.5, "grade": "B"},
            {"id": "us_unemployment", "value": 4.0, "grade": "B"},
        ]
        result = score_dimension("macro_us", indicators)
        assert "positions" in result
        assert "average_position" in result
        assert "indicator_count" in result

    def test_empty_indicators_returns_null(self):
        result = score_dimension("macro_us", [])
        assert result["average_position"] is None
        assert result["indicator_count"] == 0


class TestComputeAllPositions:
    def test_returns_all_six_dimensions(self):
        validated = {
            "macro": [
                {"id": "us_gdp_growth", "value": 2.3, "grade": "A"},
                {"id": "kr_gdp_growth", "value": 2.0, "grade": "B"},
            ],
            "political": [],
            "fundamentals": [
                {"id": "sp500_pe", "value": 22.0, "grade": "B"},
                {"id": "kospi_per", "value": 12.0, "grade": "B"},
            ],
            "sentiment": [
                {"id": "vix", "value": 18.0, "grade": "B"},
            ],
        }
        result = compute_all_positions(validated)
        assert "macro_us" in result
        assert "macro_kr" in result
        assert "political" in result
        assert "fundamentals_us" in result
        assert "fundamentals_kr" in result
        assert "sentiment" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/scripts/test_environment_scorer.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `.claude/skills/environment-scorer/scripts/environment_scorer.py`:
```python
#!/usr/bin/env python3
"""
Environment Scorer — Step 7 helper script.

Computes indicator positions relative to historical ranges.
The LLM uses these positions to assign final 1-10 scores and regime classification.

Usage:
    python environment_scorer.py --validated-data <path> [--write --output-dir <path>]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


# Historical ranges from macro-indicator-ranges.md
HISTORICAL_RANGES = {
    "us_gdp_growth": {"low": -31.2, "median": 2.5, "high": 33.8},
    "us_cpi": {"low": -2.1, "median": 2.3, "high": 9.1},
    "us_pce": {"low": -1.5, "median": 1.9, "high": 7.1},
    "us_fed_rate": {"low": 0.0, "median": 1.75, "high": 5.50},
    "us_unemployment": {"low": 3.4, "median": 5.0, "high": 14.7},
    "us_10y_yield": {"low": 0.52, "median": 2.60, "high": 5.00},
    "us_2y_yield": {"low": 0.10, "median": 1.80, "high": 5.10},
    "us_yield_spread": {"low": -108, "median": 80, "high": 290},
    "kr_gdp_growth": {"low": -6.8, "median": 3.0, "high": 6.8},
    "kr_cpi": {"low": 0.3, "median": 2.3, "high": 6.3},
    "kr_base_rate": {"low": 0.50, "median": 2.50, "high": 5.25},
    "kr_usd_fx": {"low": 905, "median": 1150, "high": 1450},
    "sp500_pe": {"low": 10.0, "median": 19.5, "high": 38.0},
    "sp500_cape": {"low": 13.3, "median": 25.0, "high": 44.0},
    "kospi_per": {"low": 7.0, "median": 12.5, "high": 27.0},
    "kospi_pbr": {"low": 0.75, "median": 1.05, "high": 1.60},
    "us_ig_spread": {"low": 80, "median": 130, "high": 550},
    "us_hy_spread": {"low": 300, "median": 450, "high": 2000},
    "vix": {"low": 9.0, "median": 17.0, "high": 82.0},
    "fear_greed": {"low": 0, "median": 50, "high": 100},
    "put_call_ratio": {"low": 0.50, "median": 0.85, "high": 1.80},
    "aaii_bull": {"low": 15.0, "median": 37.5, "high": 75.0},
}

# Dimension-to-indicator mapping
DIMENSION_INDICATORS = {
    "macro_us": ["us_gdp_growth", "us_cpi", "us_pce", "us_fed_rate", "us_unemployment",
                 "us_10y_yield", "us_2y_yield", "us_yield_spread"],
    "macro_kr": ["kr_gdp_growth", "kr_cpi", "kr_base_rate", "kr_usd_fx"],
    "political": [],  # Political is qualitative, not scored by this script
    "fundamentals_us": ["sp500_pe", "sp500_cape", "us_ig_spread", "us_hy_spread"],
    "fundamentals_kr": ["kospi_per", "kospi_pbr"],
    "sentiment": ["vix", "fear_greed", "put_call_ratio", "aaii_bull"],
}


def compute_position(value: float, low: float, high: float) -> float:
    """
    Compute a value's position within historical range [0.0, 1.0].
    Clamped to [0.0, 1.0] if outside range.
    """
    if high == low:
        return 0.5
    position = (value - low) / (high - low)
    return max(0.0, min(1.0, round(position, 4)))


def score_dimension(dimension: str, indicators: list[dict]) -> dict:
    """
    Score a dimension by computing positions for each indicator.

    Returns positions and average for the LLM to use in scoring.
    """
    if not indicators:
        return {
            "positions": [],
            "average_position": None,
            "indicator_count": 0,
        }

    dim_indicator_ids = DIMENSION_INDICATORS.get(dimension, [])
    positions = []

    for ind in indicators:
        ind_id = ind["id"]
        value = ind.get("value")

        if value is None or ind_id not in HISTORICAL_RANGES:
            continue

        # Filter to only this dimension's indicators
        if dim_indicator_ids and ind_id not in dim_indicator_ids:
            continue

        ranges = HISTORICAL_RANGES[ind_id]
        position = compute_position(value, ranges["low"], ranges["high"])
        median_position = compute_position(ranges["median"], ranges["low"], ranges["high"])

        positions.append({
            "indicator_id": ind_id,
            "value": value,
            "position": position,
            "median_position": median_position,
            "relative_to_median": "above" if position > median_position else "below" if position < median_position else "at",
            "grade": ind.get("grade", "C"),
        })

    avg_position = (
        round(sum(p["position"] for p in positions) / len(positions), 4)
        if positions else None
    )

    return {
        "positions": positions,
        "average_position": avg_position,
        "indicator_count": len(positions),
    }


def compute_all_positions(validated_indicators: dict) -> dict:
    """
    Compute positions for all 6 dimensions.

    Args:
        validated_indicators: The validated_indicators dict from validated-data.json

    Returns:
        Dict with positions per dimension, ready for LLM scoring.
    """
    macro = validated_indicators.get("macro", [])
    political = validated_indicators.get("political", [])
    fundamentals = validated_indicators.get("fundamentals", [])
    sentiment = validated_indicators.get("sentiment", [])

    return {
        "macro_us": score_dimension("macro_us", macro),
        "macro_kr": score_dimension("macro_kr", macro),
        "political": {
            "positions": [],
            "average_position": None,
            "indicator_count": len(political),
            "note": "Political scoring is qualitative — handled by LLM directly",
        },
        "fundamentals_us": score_dimension("fundamentals_us", fundamentals),
        "fundamentals_kr": score_dimension("fundamentals_kr", fundamentals),
        "sentiment": score_dimension("sentiment", sentiment),
    }


def main():
    parser = argparse.ArgumentParser(description="Compute environment indicator positions")
    parser.add_argument("--validated-data", required=True, help="Path to validated-data.json")
    parser.add_argument("--write", action="store_true", help="Write positions to file")
    parser.add_argument("--output-dir", help="Output directory for positions file")
    args = parser.parse_args()

    with open(args.validated_data) as f:
        validated = json.load(f)

    result = compute_all_positions(validated.get("validated_indicators", {}))
    result["computation_timestamp"] = datetime.now(timezone.utc).isoformat()
    result["data_grade"] = validated.get("overall_data_grade", "C")

    if args.write and args.output_dir:
        out_path = os.path.join(args.output_dir, "environment-positions.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Written to {out_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/scripts/test_environment_scorer.py -v
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/environment-scorer/scripts/environment_scorer.py tests/scripts/test_environment_scorer.py
git commit -m "feat: add environment-scorer script with position calculation (Step 7)"
```

---

## Chunk 4: Python Scripts — Portfolio Construction

### Task 10: allocation-calculator.py

**Files:**
- Create: `.claude/agents/portfolio-analyst/scripts/allocation_calculator.py`
- Create: `tests/scripts/test_allocation_calculator.py`

- [ ] **Step 1: Write failing tests**

Create `tests/scripts/test_allocation_calculator.py`:
```python
"""Tests for allocation-calculator.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/agents/portfolio-analyst/scripts"))

from allocation_calculator import (
    get_base_allocation,
    apply_risk_adjustment,
    apply_horizon_adjustment,
    normalize_allocation,
    calculate_allocation,
    REGIME_RANGES,
)


class TestGetBaseAllocation:
    def test_mid_cycle_returns_ranges(self):
        ranges = get_base_allocation("mid-cycle")
        assert "us_equity" in ranges
        assert ranges["us_equity"] == (40, 55)
        assert ranges["kr_equity"] == (10, 15)

    def test_unknown_regime_raises(self):
        try:
            get_base_allocation("unknown")
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_all_regimes_defined(self):
        for regime in ["early-expansion", "mid-cycle", "late-cycle", "recession", "recovery"]:
            ranges = get_base_allocation(regime)
            assert len(ranges) == 5


class TestApplyRiskAdjustment:
    def test_aggressive_uses_upper_equity(self):
        ranges = {"us_equity": (40, 55), "kr_equity": (10, 15),
                  "bonds": (20, 30), "alternatives": (5, 10), "cash": (5, 10)}
        alloc = apply_risk_adjustment(ranges, "aggressive")
        assert alloc["us_equity"] == 55  # upper bound
        assert alloc["bonds"] == 20      # lower bound for defensive
        assert alloc["cash"] == 5        # lower bound

    def test_conservative_uses_lower_equity(self):
        ranges = {"us_equity": (40, 55), "kr_equity": (10, 15),
                  "bonds": (20, 30), "alternatives": (5, 10), "cash": (5, 10)}
        alloc = apply_risk_adjustment(ranges, "conservative")
        assert alloc["us_equity"] == 40  # lower bound
        assert alloc["bonds"] == 30      # upper bound for defensive
        assert alloc["cash"] == 10       # upper bound

    def test_moderate_uses_midpoint(self):
        ranges = {"us_equity": (40, 55), "kr_equity": (10, 15),
                  "bonds": (20, 30), "alternatives": (5, 10), "cash": (5, 10)}
        alloc = apply_risk_adjustment(ranges, "moderate")
        assert alloc["us_equity"] == 47.5  # midpoint


class TestApplyHorizonAdjustment:
    def test_short_horizon_adds_cash(self):
        alloc = {"us_equity": 50, "kr_equity": 10, "bonds": 25, "alternatives": 5, "cash": 10}
        adjusted = apply_horizon_adjustment(alloc, "short")
        assert adjusted["cash"] == 20    # +10
        assert adjusted["us_equity"] == 45  # -5
        assert adjusted["kr_equity"] == 5   # -5

    def test_medium_no_change(self):
        alloc = {"us_equity": 50, "kr_equity": 10, "bonds": 25, "alternatives": 5, "cash": 10}
        adjusted = apply_horizon_adjustment(alloc, "medium")
        assert adjusted == alloc

    def test_long_horizon_adds_equity(self):
        alloc = {"us_equity": 50, "kr_equity": 10, "bonds": 25, "alternatives": 5, "cash": 10}
        adjusted = apply_horizon_adjustment(alloc, "long")
        assert adjusted["us_equity"] == 55   # +5
        assert adjusted["kr_equity"] == 15   # +5
        assert adjusted["bonds"] == 20       # -5
        assert adjusted["cash"] == 5         # -5

    def test_no_negative_values(self):
        alloc = {"us_equity": 30, "kr_equity": 5, "bonds": 25, "alternatives": 5, "cash": 2}
        adjusted = apply_horizon_adjustment(alloc, "short")
        for v in adjusted.values():
            assert v >= 0


class TestNormalizeAllocation:
    def test_already_100_no_change(self):
        alloc = {"us_equity": 50, "kr_equity": 10, "bonds": 25, "alternatives": 5, "cash": 10}
        norm = normalize_allocation(alloc)
        assert sum(norm.values()) == 100.0

    def test_normalizes_over_100(self):
        alloc = {"us_equity": 55, "kr_equity": 15, "bonds": 20, "alternatives": 5, "cash": 10}
        # sum = 105
        norm = normalize_allocation(alloc)
        assert abs(sum(norm.values()) - 100.0) < 0.01

    def test_normalizes_under_100(self):
        alloc = {"us_equity": 40, "kr_equity": 10, "bonds": 20, "alternatives": 5, "cash": 5}
        # sum = 80
        norm = normalize_allocation(alloc)
        assert abs(sum(norm.values()) - 100.0) < 0.01


class TestCalculateAllocation:
    def test_full_pipeline(self):
        result = calculate_allocation("mid-cycle", "moderate", "medium")
        assert "allocation" in result
        assert abs(result["allocation"]["total"] - 100.0) < 0.01
        assert result["regime"] == "mid-cycle"
        assert result["risk_tolerance"] == "moderate"

    def test_three_options_differentiated(self):
        agg = calculate_allocation("mid-cycle", "aggressive", "medium")
        mod = calculate_allocation("mid-cycle", "moderate", "medium")
        con = calculate_allocation("mid-cycle", "conservative", "medium")

        agg_eq = agg["allocation"]["us_equity"] + agg["allocation"]["kr_equity"]
        con_eq = con["allocation"]["us_equity"] + con["allocation"]["kr_equity"]
        # At least 10pp difference
        assert agg_eq - con_eq >= 10

    def test_no_asset_exceeds_70(self):
        for regime in ["early-expansion", "mid-cycle", "late-cycle", "recession", "recovery"]:
            for risk in ["aggressive", "moderate", "conservative"]:
                result = calculate_allocation(regime, risk, "medium")
                for key, val in result["allocation"].items():
                    if key != "total":
                        assert val <= 70, f"{key}={val} exceeds 70% in {regime}/{risk}"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/scripts/test_allocation_calculator.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `.claude/agents/portfolio-analyst/scripts/allocation_calculator.py`:
```python
#!/usr/bin/env python3
"""
Allocation Calculator — Step 8 (Stages 2-4) of the pipeline.

Computes portfolio allocations using:
  Stage 2: Regime → base allocation ranges
  Stage 3: Risk tolerance → position within ranges
  Stage 4: Horizon → adjustment + normalization

Usage:
    python allocation_calculator.py --regime <regime> --risk <risk> --horizon <horizon>
"""

import argparse
import json
import sys


REGIME_RANGES = {
    "early-expansion": {
        "us_equity": (50, 65),
        "kr_equity": (10, 20),
        "bonds": (15, 25),
        "alternatives": (5, 10),
        "cash": (0, 5),
    },
    "mid-cycle": {
        "us_equity": (40, 55),
        "kr_equity": (10, 15),
        "bonds": (20, 30),
        "alternatives": (5, 10),
        "cash": (5, 10),
    },
    "late-cycle": {
        "us_equity": (30, 45),
        "kr_equity": (5, 15),
        "bonds": (30, 40),
        "alternatives": (5, 10),
        "cash": (10, 15),
    },
    "recession": {
        "us_equity": (20, 35),
        "kr_equity": (5, 10),
        "bonds": (35, 50),
        "alternatives": (5, 10),
        "cash": (15, 25),
    },
    "recovery": {
        "us_equity": (45, 60),
        "kr_equity": (15, 20),
        "bonds": (15, 25),
        "alternatives": (5, 10),
        "cash": (5, 10),
    },
}

HORIZON_ADJUSTMENTS = {
    "short": {"us_equity": -5, "kr_equity": -5, "bonds": 0, "alternatives": 0, "cash": 10},
    "medium": {"us_equity": 0, "kr_equity": 0, "bonds": 0, "alternatives": 0, "cash": 0},
    "medium-long": {"us_equity": 3, "kr_equity": 2, "bonds": 0, "alternatives": 0, "cash": -5},
    "long": {"us_equity": 5, "kr_equity": 5, "bonds": -5, "alternatives": 0, "cash": -5},
}


def months_to_horizon(months: int) -> str:
    """Map investment_period_months to horizon string.

    Spec buckets: <6mo=short, 6-12mo=medium, 1-3yr=medium, 3-5yr=medium-long, 5+yr=long
    """
    if months < 6:
        return "short"
    elif months <= 36:
        return "medium"
    elif months <= 60:
        return "medium-long"
    else:
        return "long"


def get_base_allocation(regime: str) -> dict:
    """Stage 2: Get base allocation ranges for a regime."""
    if regime not in REGIME_RANGES:
        raise ValueError(f"Unknown regime: {regime}. Valid: {list(REGIME_RANGES.keys())}")
    return REGIME_RANGES[regime].copy()


def apply_risk_adjustment(ranges: dict, risk_tolerance: str) -> dict:
    """
    Stage 3: Position within ranges based on risk tolerance.

    Aggressive: upper equity, lower bonds/cash
    Moderate: midpoint
    Conservative: lower equity, upper bonds/cash
    """
    allocation = {}
    equity_classes = {"us_equity", "kr_equity"}
    defensive_classes = {"bonds", "cash"}

    for asset_class, (low, high) in ranges.items():
        if risk_tolerance == "aggressive":
            if asset_class in equity_classes:
                allocation[asset_class] = high
            elif asset_class in defensive_classes:
                allocation[asset_class] = low
            else:
                allocation[asset_class] = round((low + high) / 2, 1)
        elif risk_tolerance == "conservative":
            if asset_class in equity_classes:
                allocation[asset_class] = low
            elif asset_class in defensive_classes:
                allocation[asset_class] = high
            else:
                allocation[asset_class] = round((low + high) / 2, 1)
        else:  # moderate
            allocation[asset_class] = round((low + high) / 2, 1)

    return allocation


def apply_horizon_adjustment(allocation: dict, horizon: str) -> dict:
    """
    Stage 4: Adjust allocation based on investment horizon.

    Adjustments are additive. Values clamped to >= 0.
    """
    adjustments = HORIZON_ADJUSTMENTS.get(horizon, HORIZON_ADJUSTMENTS["medium"])
    adjusted = {}

    for asset_class, value in allocation.items():
        adj = adjustments.get(asset_class, 0)
        adjusted[asset_class] = max(0, round(value + adj, 1))

    return adjusted


def normalize_allocation(allocation: dict) -> dict:
    """
    Normalize allocation so total = exactly 100%.

    Distributes the delta proportionally across all non-zero classes.
    """
    total = sum(allocation.values())
    if total == 0:
        return allocation

    if abs(total - 100.0) < 0.01:
        # Close enough, just fix rounding
        normalized = {k: round(v, 1) for k, v in allocation.items()}
        diff = round(100.0 - sum(normalized.values()), 1)
        if diff != 0:
            # Add to the largest class
            largest = max(normalized, key=normalized.get)
            normalized[largest] = round(normalized[largest] + diff, 1)
        return normalized

    # Proportional scaling
    scale = 100.0 / total
    normalized = {k: round(v * scale, 1) for k, v in allocation.items()}

    # Fix rounding error
    diff = round(100.0 - sum(normalized.values()), 1)
    if diff != 0:
        largest = max(normalized, key=normalized.get)
        normalized[largest] = round(normalized[largest] + diff, 1)

    return normalized


def calculate_allocation(regime: str, risk_tolerance: str, horizon: str) -> dict:
    """
    Full allocation pipeline: regime → ranges → risk adjust → horizon adjust → normalize.

    Returns allocation dict with total = 100.
    """
    # Stage 2: Base ranges
    ranges = get_base_allocation(regime)

    # Stage 3: Risk adjustment
    allocation = apply_risk_adjustment(ranges, risk_tolerance)

    # Stage 4: Horizon adjustment
    allocation = apply_horizon_adjustment(allocation, horizon)

    # Normalize to 100%
    allocation = normalize_allocation(allocation)

    # Enforce constraints
    for key, val in allocation.items():
        if val > 70:
            overflow = val - 70
            allocation[key] = 70
            # Distribute overflow to cash
            allocation["cash"] = round(allocation.get("cash", 0) + overflow, 1)
            allocation = normalize_allocation(allocation)

    allocation["total"] = round(sum(v for k, v in allocation.items() if k != "total"), 1)

    return {
        "regime": regime,
        "risk_tolerance": risk_tolerance,
        "horizon": horizon,
        "allocation": allocation,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate portfolio allocation")
    parser.add_argument("--regime", required=True, choices=list(REGIME_RANGES.keys()))
    parser.add_argument("--risk", required=True, choices=["aggressive", "moderate", "conservative"])
    parser.add_argument("--horizon", required=True, choices=["short", "medium", "medium-long", "long"])
    args = parser.parse_args()

    result = calculate_allocation(args.regime, args.risk, args.horizon)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/scripts/test_allocation_calculator.py -v
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/agents/portfolio-analyst/scripts/allocation_calculator.py tests/scripts/test_allocation_calculator.py
git commit -m "feat: add allocation-calculator with regime/risk/horizon pipeline (Step 8)"
```

### Task 11: return-estimator.py

**Files:**
- Create: `.claude/agents/portfolio-analyst/scripts/return_estimator.py`
- Create: `tests/scripts/test_return_estimator.py`

- [ ] **Step 1: Write failing tests**

Create `tests/scripts/test_return_estimator.py`:
```python
"""Tests for return-estimator.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/agents/portfolio-analyst/scripts"))

from return_estimator import (
    estimate_portfolio_return,
    compute_risk_return_score,
    validate_scenario_probabilities,
)


SAMPLE_ALLOCATION = {
    "us_equity": 45,
    "kr_equity": 15,
    "bonds": 25,
    "alternatives": 10,
    "cash": 5,
    "total": 100,
}

SAMPLE_RETURN_ASSUMPTIONS = {
    "bull": {
        "us_equity": 18.0,
        "kr_equity": 22.0,
        "bonds": 5.0,
        "alternatives": 12.0,
        "cash": 4.0,
    },
    "base": {
        "us_equity": 8.0,
        "kr_equity": 6.0,
        "bonds": 3.5,
        "alternatives": 5.0,
        "cash": 3.0,
    },
    "bear": {
        "us_equity": -12.0,
        "kr_equity": -18.0,
        "bonds": 2.0,
        "alternatives": -5.0,
        "cash": 2.0,
    },
}

SAMPLE_PROBABILITIES = {"bull": 25, "base": 50, "bear": 25}


class TestValidateScenarioProbabilities:
    def test_valid_probabilities(self):
        assert validate_scenario_probabilities({"bull": 25, "base": 50, "bear": 25}) is True

    def test_sum_not_100(self):
        assert validate_scenario_probabilities({"bull": 30, "base": 50, "bear": 25}) is False

    def test_negative_probability(self):
        assert validate_scenario_probabilities({"bull": -10, "base": 60, "bear": 50}) is False


class TestEstimatePortfolioReturn:
    def test_returns_three_scenarios(self):
        result = estimate_portfolio_return(
            SAMPLE_ALLOCATION, SAMPLE_RETURN_ASSUMPTIONS, SAMPLE_PROBABILITIES
        )
        assert "bull" in result["scenarios"]
        assert "base" in result["scenarios"]
        assert "bear" in result["scenarios"]

    def test_weighted_return_computed(self):
        result = estimate_portfolio_return(
            SAMPLE_ALLOCATION, SAMPLE_RETURN_ASSUMPTIONS, SAMPLE_PROBABILITIES
        )
        bull_return = result["scenarios"]["bull"]["expected_return"]
        # Weighted: 45*18 + 15*22 + 25*5 + 10*12 + 5*4 = 810+330+125+120+20 = 1405 / 100 = 14.05
        assert abs(bull_return - 14.05) < 0.1

    def test_probability_preserved(self):
        result = estimate_portfolio_return(
            SAMPLE_ALLOCATION, SAMPLE_RETURN_ASSUMPTIONS, SAMPLE_PROBABILITIES
        )
        total_prob = sum(
            s["probability"] for s in result["scenarios"].values()
        )
        assert total_prob == 100


class TestComputeRiskReturnScore:
    def test_positive_score(self):
        scenarios = {
            "bull": {"expected_return": 15.0, "probability": 25},
            "base": {"expected_return": 7.0, "probability": 50},
            "bear": {"expected_return": -10.0, "probability": 25},
        }
        score = compute_risk_return_score(scenarios)
        # weighted_return = 15*0.25 + 7*0.50 = 3.75 + 3.50 = 7.25
        # weighted_loss = |-10*0.25| = 2.50
        # score = 7.25 / 2.50 = 2.90
        assert abs(score - 2.90) < 0.1

    def test_zero_loss_returns_max(self):
        scenarios = {
            "bull": {"expected_return": 10.0, "probability": 25},
            "base": {"expected_return": 5.0, "probability": 50},
            "bear": {"expected_return": 1.0, "probability": 25},
        }
        score = compute_risk_return_score(scenarios)
        assert score == 99.99  # Capped at max
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/scripts/test_return_estimator.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `.claude/agents/portfolio-analyst/scripts/return_estimator.py`:
```python
#!/usr/bin/env python3
"""
Return Estimator — Step 8 (Stage 6) of the pipeline.

Computes expected portfolio returns per scenario using allocation weights
and per-asset return assumptions (provided by LLM).

Usage:
    python return_estimator.py --allocation <json> --returns <json> --probabilities <json>
"""

import argparse
import json
import sys


def validate_scenario_probabilities(probabilities: dict) -> bool:
    """Validate that scenario probabilities sum to 100 and are non-negative."""
    if any(p < 0 for p in probabilities.values()):
        return False
    return abs(sum(probabilities.values()) - 100) < 1


def estimate_portfolio_return(
    allocation: dict,
    return_assumptions: dict,
    probabilities: dict,
) -> dict:
    """
    Calculate weighted portfolio return for each scenario.

    Args:
        allocation: Asset class weights (e.g., {"us_equity": 45, ...})
        return_assumptions: Per-scenario, per-asset returns (%)
            e.g., {"bull": {"us_equity": 18.0, ...}, ...}
        probabilities: Per-scenario probabilities (%)
            e.g., {"bull": 25, "base": 50, "bear": 25}

    Returns:
        Dict with per-scenario expected returns and probabilities.
    """
    asset_classes = [k for k in allocation if k != "total"]
    scenarios = {}

    for scenario in ["bull", "base", "bear"]:
        assumptions = return_assumptions.get(scenario, {})
        weighted_return = 0.0

        for asset_class in asset_classes:
            weight = allocation.get(asset_class, 0) / 100.0  # Convert % to decimal
            asset_return = assumptions.get(asset_class, 0)
            weighted_return += weight * asset_return

        scenarios[scenario] = {
            "expected_return": round(weighted_return, 2),
            "probability": probabilities.get(scenario, 0),
            "per_asset_returns": {
                ac: assumptions.get(ac, 0) for ac in asset_classes
            },
        }

    return {
        "scenarios": scenarios,
        "risk_return_score": compute_risk_return_score(scenarios),
    }


def compute_risk_return_score(scenarios: dict) -> float:
    """
    Compute Risk/Return score.

    R/R = (bull_return * bull_prob + base_return * base_prob) / |bear_return * bear_prob|

    Returns capped at 99.99 if bear loss is near zero.
    """
    bull = scenarios.get("bull", {})
    base = scenarios.get("base", {})
    bear = scenarios.get("bear", {})

    bull_return = bull.get("expected_return", 0)
    base_return = base.get("expected_return", 0)
    bear_return = bear.get("expected_return", 0)

    bull_prob = bull.get("probability", 25) / 100.0
    base_prob = base.get("probability", 50) / 100.0
    bear_prob = bear.get("probability", 25) / 100.0

    weighted_upside = (bull_return * bull_prob) + (base_return * base_prob)
    weighted_downside = abs(bear_return * bear_prob)

    if weighted_downside < 0.01:
        return 99.99  # Cap when no meaningful downside

    return round(weighted_upside / weighted_downside, 2)


def main():
    parser = argparse.ArgumentParser(description="Estimate portfolio returns per scenario")
    parser.add_argument("--allocation", required=True, help="JSON string or file path for allocation")
    parser.add_argument("--returns", required=True, help="JSON string or file path for return assumptions")
    parser.add_argument("--probabilities", required=True, help="JSON string or file path for probabilities")
    args = parser.parse_args()

    def load_json(val):
        if val.startswith("{"):
            return json.loads(val)
        with open(val) as f:
            return json.load(f)

    allocation = load_json(args.allocation)
    returns = load_json(args.returns)
    probs = load_json(args.probabilities)

    result = estimate_portfolio_return(allocation, returns, probs)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/scripts/test_return_estimator.py -v
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/agents/portfolio-analyst/scripts/return_estimator.py tests/scripts/test_return_estimator.py
git commit -m "feat: add return-estimator with scenario-weighted calculation (Step 8)"
```

### Task 12: quality-gate.py

**Files:**
- Create: `.claude/skills/quality-gate/scripts/quality_gate.py`
- Create: `tests/scripts/test_quality_gate.py`

- [ ] **Step 1: Write failing tests**

Create `tests/scripts/test_quality_gate.py`:
```python
"""Tests for quality-gate.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/quality-gate/scripts"))

from quality_gate import run_quality_gate, CHECKS


SAMPLE_RECOMMENDATION = {
    "recommendation_timestamp": "2026-03-17T12:00:00Z",
    "user_profile_hash": "abc123",
    "regime": "mid-cycle",
    "options": [
        {
            "option_id": "aggressive",
            "allocation": {"us_equity": 55, "kr_equity": 15, "bonds": 20, "alternatives": 5, "cash": 5, "total": 100},
            "holdings": [
                {"ticker": "VOO", "asset_class": "us_equity", "weight": 25, "source_tag": "[Portal]", "rationale": "Core US"},
                {"ticker": "QQQ", "asset_class": "us_equity", "weight": 30, "source_tag": "[Portal]", "rationale": "Growth"},
                {"ticker": "KODEX200", "asset_class": "kr_equity", "weight": 15, "source_tag": "[KR-Portal]", "rationale": "KR core"},
                {"ticker": "AGG", "asset_class": "bonds", "weight": 20, "source_tag": "[Portal]", "rationale": "Bonds"},
                {"ticker": "GLD", "asset_class": "alternatives", "weight": 5, "source_tag": "[Portal]", "rationale": "Gold"},
                {"ticker": "SHV", "asset_class": "cash", "weight": 5, "source_tag": "[Portal]", "rationale": "Cash"},
            ],
            "scenarios": {
                "bull": {"expected_return": 18.5, "probability": 25},
                "base": {"expected_return": 8.0, "probability": 50},
                "bear": {"expected_return": -12.0, "probability": 25},
            },
        },
        {
            "option_id": "moderate",
            "allocation": {"us_equity": 45, "kr_equity": 10, "bonds": 27.5, "alternatives": 7.5, "cash": 10, "total": 100},
            "holdings": [
                {"ticker": "VTI", "asset_class": "us_equity", "weight": 45, "source_tag": "[Portal]", "rationale": "Broad US"},
                {"ticker": "KODEX200", "asset_class": "kr_equity", "weight": 10, "source_tag": "[KR-Portal]", "rationale": "KR"},
                {"ticker": "BND", "asset_class": "bonds", "weight": 27.5, "source_tag": "[Portal]", "rationale": "Bonds"},
                {"ticker": "IAU", "asset_class": "alternatives", "weight": 7.5, "source_tag": "[Portal]", "rationale": "Gold"},
                {"ticker": "SGOV", "asset_class": "cash", "weight": 10, "source_tag": "[Portal]", "rationale": "Cash"},
            ],
            "scenarios": {
                "bull": {"expected_return": 12.0, "probability": 25},
                "base": {"expected_return": 6.0, "probability": 50},
                "bear": {"expected_return": -8.0, "probability": 25},
            },
        },
        {
            "option_id": "conservative",
            "allocation": {"us_equity": 35, "kr_equity": 5, "bonds": 35, "alternatives": 7.5, "cash": 17.5, "total": 100},
            "holdings": [
                {"ticker": "VIG", "asset_class": "us_equity", "weight": 35, "source_tag": "[Portal]", "rationale": "Dividend"},
                {"ticker": "KODEX배당", "asset_class": "kr_equity", "weight": 5, "source_tag": "[KR-Portal]", "rationale": "KR div"},
                {"ticker": "TLT", "asset_class": "bonds", "weight": 20, "source_tag": "[Portal]", "rationale": "Long treasury"},
                {"ticker": "SHY", "asset_class": "bonds", "weight": 15, "source_tag": "[Portal]", "rationale": "Short treasury"},
                {"ticker": "GLD", "asset_class": "alternatives", "weight": 7.5, "source_tag": "[Portal]", "rationale": "Gold"},
                {"ticker": "BIL", "asset_class": "cash", "weight": 17.5, "source_tag": "[Portal]", "rationale": "T-bills"},
            ],
            "scenarios": {
                "bull": {"expected_return": 8.0, "probability": 25},
                "base": {"expected_return": 4.5, "probability": 50},
                "bear": {"expected_return": -4.0, "probability": 25},
            },
        },
    ],
    "key_risks": [{"risk": "Rate hike", "mechanism": "Rates up → Bond prices down → Portfolio drag"}],
    "disclaimer": "This is not investment advice.",
}

SAMPLE_USER_PROFILE = {
    "budget": 50000000,
    "budget_currency": "KRW",
    "investment_period_months": 12,
    "risk_tolerance": "moderate",
}


class TestRunQualityGate:
    def test_all_checks_defined(self):
        assert len(CHECKS) == 7

    def test_valid_recommendation_passes(self):
        result = run_quality_gate(SAMPLE_RECOMMENDATION, SAMPLE_USER_PROFILE)
        assert result["overall"] == "PASS"
        assert all(c["status"] == "PASS" for c in result["checks"])

    def test_allocation_not_100_fails(self):
        bad = json.loads(json.dumps(SAMPLE_RECOMMENDATION))
        bad["options"][0]["allocation"]["total"] = 95
        bad["options"][0]["allocation"]["us_equity"] = 50
        result = run_quality_gate(bad, SAMPLE_USER_PROFILE)
        # Check 1 should fail
        check1 = next(c for c in result["checks"] if c["check_id"] == 1)
        assert check1["status"] == "FAIL"

    def test_missing_disclaimer_fails(self):
        bad = json.loads(json.dumps(SAMPLE_RECOMMENDATION))
        bad["disclaimer"] = ""
        result = run_quality_gate(bad, SAMPLE_USER_PROFILE)
        check4 = next(c for c in result["checks"] if c["check_id"] == 4)
        assert check4["status"] == "FAIL"

    def test_insufficient_differentiation_fails(self):
        bad = json.loads(json.dumps(SAMPLE_RECOMMENDATION))
        # Make all options have same equity weight
        for opt in bad["options"]:
            opt["allocation"]["us_equity"] = 45
            opt["allocation"]["kr_equity"] = 10
        result = run_quality_gate(bad, SAMPLE_USER_PROFILE)
        check7 = next(c for c in result["checks"] if c["check_id"] == 7)
        assert check7["status"] == "FAIL"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/scripts/test_quality_gate.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `.claude/skills/quality-gate/scripts/quality_gate.py`:
```python
#!/usr/bin/env python3
"""
Quality Gate — Step 9 of the pipeline.

Runs 7 deterministic checks on portfolio-recommendation.json.
No LLM judgment — purely script-based validation.

Usage:
    python quality_gate.py --recommendation <path> --user-profile <path> [--write --output-dir <path>]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


CHECKS = [
    {"check_id": 1, "name": "Allocation sum", "description": "Each option's allocation totals exactly 100"},
    {"check_id": 2, "name": "Source tag coverage", "description": "≥80% of holdings have source_tag"},
    {"check_id": 3, "name": "Required fields", "description": "All required fields present in each option"},
    {"check_id": 4, "name": "Disclaimer present", "description": "Non-empty disclaimer field"},
    {"check_id": 5, "name": "Grade D exclusion", "description": "No Grade D items in holdings"},
    {"check_id": 6, "name": "User profile reflected", "description": "Budget/period/risk reflected in output"},
    {"check_id": 7, "name": "Option differentiation", "description": "≥10pp equity weight difference"},
]


def _check_allocation_sum(recommendation: dict) -> dict:
    """Check 1: Each option's allocation.total == 100."""
    failures = []
    for opt in recommendation.get("options", []):
        alloc = opt.get("allocation", {})
        total = alloc.get("total", 0)
        if abs(total - 100.0) > 0.1:
            failures.append(f"{opt['option_id']}: total={total}")

    return {
        "check_id": 1,
        "name": "Allocation sum",
        "status": "PASS" if not failures else "FAIL",
        "details": failures if failures else "All options sum to 100%",
    }


def _check_source_tags(recommendation: dict) -> dict:
    """Check 2: ≥80% of holdings have source_tag."""
    total_holdings = 0
    tagged_holdings = 0
    for opt in recommendation.get("options", []):
        for holding in opt.get("holdings", []):
            total_holdings += 1
            if holding.get("source_tag"):
                tagged_holdings += 1

    if total_holdings == 0:
        return {"check_id": 2, "name": "Source tag coverage", "status": "FAIL", "details": "No holdings found"}

    coverage = tagged_holdings / total_holdings
    return {
        "check_id": 2,
        "name": "Source tag coverage",
        "status": "PASS" if coverage >= 0.8 else "FAIL",
        "details": f"{tagged_holdings}/{total_holdings} ({coverage:.0%})",
    }


def _check_required_fields(recommendation: dict) -> dict:
    """Check 3: Required fields present in each option."""
    required_option = {"option_id", "allocation", "holdings", "scenarios"}
    required_alloc = {"us_equity", "kr_equity", "bonds", "alternatives", "cash", "total"}
    failures = []

    for opt in recommendation.get("options", []):
        missing = required_option - set(opt.keys())
        if missing:
            failures.append(f"{opt.get('option_id', '?')}: missing {missing}")
        alloc_missing = required_alloc - set(opt.get("allocation", {}).keys())
        if alloc_missing:
            failures.append(f"{opt.get('option_id', '?')}: allocation missing {alloc_missing}")

    return {
        "check_id": 3,
        "name": "Required fields",
        "status": "PASS" if not failures else "FAIL",
        "details": failures if failures else "All required fields present",
    }


def _check_disclaimer(recommendation: dict) -> dict:
    """Check 4: Non-empty disclaimer field."""
    disclaimer = recommendation.get("disclaimer", "")
    return {
        "check_id": 4,
        "name": "Disclaimer present",
        "status": "PASS" if disclaimer else "FAIL",
        "details": "Disclaimer present" if disclaimer else "Disclaimer missing or empty",
    }


def _check_grade_d_exclusion(recommendation: dict, exclusions: list | None = None) -> dict:
    """Check 5: Grade D items not in holdings."""
    if not exclusions:
        return {"check_id": 5, "name": "Grade D exclusion", "status": "PASS", "details": "No exclusions to check"}

    excluded_ids = {e.get("id") for e in exclusions}
    violations = []
    for opt in recommendation.get("options", []):
        for holding in opt.get("holdings", []):
            if holding.get("ticker") in excluded_ids:
                violations.append(f"{opt['option_id']}: {holding['ticker']} is Grade D excluded")

    return {
        "check_id": 5,
        "name": "Grade D exclusion",
        "status": "PASS" if not violations else "FAIL",
        "details": violations if violations else "No Grade D items in holdings",
    }


def _check_user_profile(recommendation: dict, user_profile: dict) -> dict:
    """Check 6: User profile reflected in output."""
    failures = []
    risk = user_profile.get("risk_tolerance", "")

    # Check that options include all 3 risk levels
    option_ids = {opt.get("option_id") for opt in recommendation.get("options", [])}
    expected_ids = {"aggressive", "moderate", "conservative"}
    if not expected_ids.issubset(option_ids):
        failures.append(f"Missing options: {expected_ids - option_ids}")

    return {
        "check_id": 6,
        "name": "User profile reflected",
        "status": "PASS" if not failures else "FAIL",
        "details": failures if failures else "User profile reflected in output",
    }


def _check_differentiation(recommendation: dict) -> dict:
    """Check 7: ≥10pp equity weight difference between most and least aggressive."""
    options = recommendation.get("options", [])
    if len(options) < 2:
        return {"check_id": 7, "name": "Option differentiation", "status": "FAIL", "details": "Need ≥2 options"}

    equity_weights = []
    for opt in options:
        alloc = opt.get("allocation", {})
        eq = alloc.get("us_equity", 0) + alloc.get("kr_equity", 0)
        equity_weights.append((opt.get("option_id"), eq))

    equity_weights.sort(key=lambda x: x[1], reverse=True)
    max_eq = equity_weights[0][1]
    min_eq = equity_weights[-1][1]
    diff = max_eq - min_eq

    return {
        "check_id": 7,
        "name": "Option differentiation",
        "status": "PASS" if diff >= 10 else "FAIL",
        "details": f"Equity range: {equity_weights[0][0]}={max_eq}%, {equity_weights[-1][0]}={min_eq}%, diff={diff}pp",
    }


def run_quality_gate(recommendation: dict, user_profile: dict, exclusions: list | None = None) -> dict:
    """Run all 7 quality gate checks."""
    checks = [
        _check_allocation_sum(recommendation),
        _check_source_tags(recommendation),
        _check_required_fields(recommendation),
        _check_disclaimer(recommendation),
        _check_grade_d_exclusion(recommendation, exclusions),
        _check_user_profile(recommendation, user_profile),
        _check_differentiation(recommendation),
    ]

    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")

    return {
        "gate_timestamp": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "pass_count": 7 - fail_count,
        "fail_count": fail_count,
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description="Run quality gate on portfolio recommendation")
    parser.add_argument("--recommendation", required=True, help="Path to portfolio-recommendation.json")
    parser.add_argument("--user-profile", required=True, help="Path to user-profile.json")
    parser.add_argument("--exclusions", help="Path to exclusions list (from validated-data.json)")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output-dir", help="Output directory")
    args = parser.parse_args()

    with open(args.recommendation) as f:
        rec = json.load(f)
    with open(args.user_profile) as f:
        profile = json.load(f)

    exclusions = None
    if args.exclusions and os.path.exists(args.exclusions):
        with open(args.exclusions) as f:
            exclusions = json.load(f)

    result = run_quality_gate(rec, profile, exclusions)

    if args.write and args.output_dir:
        out_path = os.path.join(args.output_dir, "quality-report.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Written to {out_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/scripts/test_quality_gate.py -v
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/quality-gate/scripts/quality_gate.py tests/scripts/test_quality_gate.py
git commit -m "feat: add quality-gate with 7 deterministic checks (Step 9)"
```

---

## Chunk 5: Python Scripts — Output & Persistence

### Task 13: docx-generator.py

**Files:**
- Create: `.claude/skills/memo-generator/scripts/docx_generator.py`
- Create: `tests/scripts/test_docx_generator.py`

- [ ] **Step 1: Write failing tests**

Create `tests/scripts/test_docx_generator.py`:
```python
"""Tests for docx-generator.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/memo-generator/scripts"))

from docx_generator import generate_memo, create_allocation_table, create_holdings_table


SAMPLE_RECOMMENDATION = {
    "recommendation_timestamp": "2026-03-17T12:00:00Z",
    "regime": "mid-cycle",
    "options": [
        {
            "option_id": "aggressive",
            "label": "Aggressive Portfolio",
            "allocation": {"us_equity": 55, "kr_equity": 15, "bonds": 20, "alternatives": 5, "cash": 5, "total": 100},
            "holdings": [
                {"ticker": "VOO", "name": "Vanguard S&P 500", "asset_class": "us_equity", "weight": 30, "rationale": "Core", "source_tag": "[Portal]"},
                {"ticker": "QQQ", "name": "Invesco QQQ", "asset_class": "us_equity", "weight": 25, "rationale": "Growth", "source_tag": "[Portal]"},
            ],
            "scenarios": {
                "bull": {"expected_return": 18.5, "probability": 25, "assumptions": "Strong growth"},
                "base": {"expected_return": 8.0, "probability": 50, "assumptions": "Steady"},
                "bear": {"expected_return": -12.0, "probability": 25, "assumptions": "Recession"},
            },
            "risk_return_score": 2.5,
        },
    ],
    "key_risks": [{"risk": "Rising rates", "mechanism": "Rates up → Bonds down", "severity": "high"}],
    "disclaimer": "This is not investment advice.",
}

SAMPLE_ENVIRONMENT = {
    "assessment_timestamp": "2026-03-17T11:00:00Z",
    "data_grade": "B",
    "regime_classification": "mid-cycle",
    "regime_rationale": "Steady growth with moderate inflation",
}

SAMPLE_PROFILE = {
    "budget": 50000000,
    "budget_currency": "KRW",
    "investment_period_months": 12,
    "risk_tolerance": "moderate",
    "output_language": "en",
}


class TestGenerateMemo:
    def test_generates_docx_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "test_memo.docx")
            generate_memo(SAMPLE_RECOMMENDATION, SAMPLE_ENVIRONMENT, SAMPLE_PROFILE, out_path)
            assert os.path.exists(out_path)
            assert os.path.getsize(out_path) > 0

    def test_output_is_valid_docx(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "test_memo.docx")
            generate_memo(SAMPLE_RECOMMENDATION, SAMPLE_ENVIRONMENT, SAMPLE_PROFILE, out_path)
            # python-docx can open it
            from docx import Document
            doc = Document(out_path)
            assert len(doc.paragraphs) > 0


class TestCreateAllocationTable:
    def test_returns_table_data(self):
        alloc = {"us_equity": 55, "kr_equity": 15, "bonds": 20, "alternatives": 5, "cash": 5, "total": 100}
        rows = create_allocation_table(alloc)
        assert len(rows) == 5  # 5 asset classes (no total row in data)
        assert rows[0][0] == "US Equity"
        assert rows[0][1] == "55.0%"


class TestCreateHoldingsTable:
    def test_returns_table_data(self):
        holdings = [
            {"ticker": "VOO", "name": "Vanguard S&P 500", "weight": 30, "rationale": "Core", "source_tag": "[Portal]"},
        ]
        rows = create_holdings_table(holdings)
        assert len(rows) == 1
        assert rows[0][0] == "VOO"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/scripts/test_docx_generator.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `.claude/skills/memo-generator/scripts/docx_generator.py`:
```python
#!/usr/bin/env python3
"""
DOCX Memo Generator — Step 11 of the pipeline.

Generates a Word document investment memo from portfolio-recommendation.json.

Usage:
    python docx_generator.py --recommendation <path> --environment <path> --profile <path> --output <path>
"""

import argparse
import json
import os
import sys
from datetime import datetime

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


ASSET_CLASS_LABELS = {
    "us_equity": "US Equity",
    "kr_equity": "KR Equity",
    "bonds": "Bonds",
    "alternatives": "Alternatives",
    "cash": "Cash",
}


def create_allocation_table(allocation: dict) -> list[list[str]]:
    """Convert allocation dict to table rows."""
    rows = []
    for key in ["us_equity", "kr_equity", "bonds", "alternatives", "cash"]:
        label = ASSET_CLASS_LABELS.get(key, key)
        value = allocation.get(key, 0)
        rows.append([label, f"{value:.1f}%"])
    return rows


def create_holdings_table(holdings: list[dict]) -> list[list[str]]:
    """Convert holdings list to table rows."""
    rows = []
    for h in holdings:
        rows.append([
            h.get("ticker", ""),
            h.get("name", ""),
            f"{h.get('weight', 0):.1f}%",
            h.get("rationale", ""),
            h.get("source_tag", ""),
        ])
    return rows


def _add_table(doc, headers: list[str], rows: list[list[str]]):
    """Add a formatted table to the document."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(10)

    # Data rows
    for r, row_data in enumerate(rows):
        for c, val in enumerate(row_data):
            table.rows[r + 1].cells[c].text = str(val)

    return table


def generate_memo(
    recommendation: dict,
    environment: dict,
    user_profile: dict,
    output_path: str,
):
    """Generate the DOCX investment memo."""
    doc = Document()

    # -- Document style defaults --
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    # -- Cover Page --
    title = doc.add_heading("Investment Portfolio Recommendation", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    budget = user_profile.get("budget", 0)
    currency = user_profile.get("budget_currency", "KRW")
    period = user_profile.get("investment_period_months", 0)
    risk = user_profile.get("risk_tolerance", "moderate")

    if currency == "KRW" and budget >= 10000:
        budget_str = f"{budget / 10000:,.0f}만원"
    else:
        budget_str = f"{currency} {budget:,.0f}"

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(f"{budget_str} | {period}개월 | {risk} profile")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(100, 100, 100)

    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.add_run(f"Date: {recommendation.get('recommendation_timestamp', '')[:10]}")

    grade = environment.get("data_grade", "C")
    grade_para = doc.add_paragraph()
    grade_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    grade_para.add_run(f"Data Confidence: Grade {grade}")

    doc.add_page_break()

    # -- 1. Executive Summary --
    doc.add_heading("1. Executive Summary", level=1)
    regime = recommendation.get("regime", environment.get("regime_classification", "unknown"))
    doc.add_paragraph(
        f"This report presents three portfolio options for an investor with "
        f"{budget_str} over {period} months with a {risk} risk tolerance. "
        f"The current market environment is classified as '{regime}'. "
        f"Three options are provided: Aggressive, Moderate, and Conservative, "
        f"each differentiated by equity exposure and risk positioning."
    )

    # -- 2. Market Environment Analysis --
    doc.add_heading("2. Market Environment Analysis", level=1)
    doc.add_paragraph(
        f"Regime Classification: {regime}"
    )
    rationale = environment.get("regime_rationale", "")
    if rationale:
        doc.add_paragraph(f"Rationale: {rationale}")

    # -- 3-5. Portfolio Options --
    for i, opt in enumerate(recommendation.get("options", []), start=3):
        opt_id = opt.get("option_id", f"option_{i}")
        label = opt.get("label", opt_id.title() + " Portfolio")
        doc.add_heading(f"{i}. {label}", level=1)

        # Allocation table
        doc.add_heading("Allocation", level=2)
        alloc_rows = create_allocation_table(opt.get("allocation", {}))
        _add_table(doc, ["Asset Class", "Weight"], alloc_rows)
        doc.add_paragraph()  # spacing

        # Holdings table
        doc.add_heading("Key Holdings", level=2)
        holdings_rows = create_holdings_table(opt.get("holdings", []))
        _add_table(doc, ["Ticker", "Name", "Weight", "Rationale", "Source"], holdings_rows)
        doc.add_paragraph()

        # Scenarios
        doc.add_heading("Scenario Analysis", level=2)
        scenarios = opt.get("scenarios", {})
        scenario_rows = []
        for sc in ["bull", "base", "bear"]:
            s = scenarios.get(sc, {})
            scenario_rows.append([
                sc.title(),
                f"{s.get('expected_return', 0):.1f}%",
                f"{s.get('probability', 0)}%",
                s.get("assumptions", ""),
            ])
        _add_table(doc, ["Scenario", "Expected Return", "Probability", "Assumptions"], scenario_rows)

        rr_score = opt.get("risk_return_score", 0)
        doc.add_paragraph(f"\nRisk/Return Score: {rr_score:.2f}")
        doc.add_paragraph()

    # -- Risk Analysis --
    doc.add_heading(f"{len(recommendation.get('options', [])) + 3}. Risk Analysis", level=1)
    for risk_item in recommendation.get("key_risks", []):
        p = doc.add_paragraph()
        p.add_run(f"Risk: ").bold = True
        p.add_run(risk_item.get("risk", ""))
        doc.add_paragraph(f"Mechanism: {risk_item.get('mechanism', '')}")
        doc.add_paragraph(f"Severity: {risk_item.get('severity', 'medium')}")

    # -- Disclaimer --
    doc.add_heading("Disclaimer", level=1)
    disclaimer = recommendation.get("disclaimer", "This is not investment advice. For informational purposes only.")
    p = doc.add_paragraph(disclaimer)
    p.style = doc.styles["Normal"]
    for run in p.runs:
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(128, 128, 128)

    # Save
    doc.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="Generate DOCX investment memo")
    parser.add_argument("--recommendation", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.recommendation) as f:
        rec = json.load(f)
    with open(args.environment) as f:
        env = json.load(f)
    with open(args.profile) as f:
        profile = json.load(f)

    generate_memo(rec, env, profile, args.output)
    print(f"Memo generated: {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/scripts/test_docx_generator.py -v
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/memo-generator/scripts/docx_generator.py tests/scripts/test_docx_generator.py
git commit -m "feat: add DOCX memo generator with python-docx (Step 11)"
```

### Task 14: recommendation-archiver.py

**Files:**
- Create: `.claude/skills/data-manager/scripts/recommendation_archiver.py`
- Create: `tests/scripts/test_recommendation_archiver.py`

- [ ] **Step 1: Write failing tests**

Create `tests/scripts/test_recommendation_archiver.py`:
```python
"""Tests for recommendation-archiver.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/data-manager/scripts"))

from recommendation_archiver import archive_recommendation, update_latest


SAMPLE_RECOMMENDATION = {
    "recommendation_timestamp": "2026-03-17T12:00:00Z",
    "regime": "mid-cycle",
    "options": [{"option_id": "aggressive"}],
}

SAMPLE_MACRO = {"collection_timestamp": "2026-03-17T10:00:00Z", "indicators": []}


class TestArchiveRecommendation:
    def test_creates_archive_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = os.path.join(tmpdir, "data", "recommendations")
            os.makedirs(out_dir, exist_ok=True)
            path = archive_recommendation(SAMPLE_RECOMMENDATION, out_dir)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0

    def test_archive_filename_contains_date(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = os.path.join(tmpdir, "data", "recommendations")
            os.makedirs(out_dir, exist_ok=True)
            path = archive_recommendation(SAMPLE_RECOMMENDATION, out_dir)
            assert "2026-03-17" in os.path.basename(path)


class TestUpdateLatest:
    def test_creates_latest_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dim_dir = os.path.join(tmpdir, "macro")
            os.makedirs(dim_dir, exist_ok=True)
            update_latest(SAMPLE_MACRO, dim_dir)
            latest_path = os.path.join(dim_dir, "latest.json")
            assert os.path.exists(latest_path)
            with open(latest_path) as f:
                data = json.load(f)
            assert data["collection_timestamp"] == SAMPLE_MACRO["collection_timestamp"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/scripts/test_recommendation_archiver.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

Create `.claude/skills/data-manager/scripts/recommendation_archiver.py`:
```python
#!/usr/bin/env python3
"""
Recommendation Archiver — Step 12 of the pipeline.

Archives portfolio recommendations and updates per-dimension latest.json files.

Usage:
    python recommendation_archiver.py --output-dir <path> [--recommendation <path>]
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone


def archive_recommendation(recommendation: dict, archive_dir: str) -> str:
    """
    Save a timestamped copy of the recommendation.

    Args:
        recommendation: The portfolio-recommendation.json content
        archive_dir: Path to output/data/recommendations/

    Returns:
        Path to the created archive file.
    """
    os.makedirs(archive_dir, exist_ok=True)

    ts = recommendation.get("recommendation_timestamp", datetime.now(timezone.utc).isoformat())
    date_str = ts[:10]  # YYYY-MM-DD
    filename = f"{date_str}_recommendation.json"
    filepath = os.path.join(archive_dir, filename)

    # If file exists, add a counter
    counter = 1
    while os.path.exists(filepath):
        filename = f"{date_str}_recommendation_{counter}.json"
        filepath = os.path.join(archive_dir, filename)
        counter += 1

    with open(filepath, "w") as f:
        json.dump(recommendation, f, indent=2, ensure_ascii=False)

    return filepath


def update_latest(raw_data: dict, dimension_dir: str) -> str:
    """
    Update latest.json for a data dimension.

    Args:
        raw_data: The raw data JSON content (macro-raw.json, etc.)
        dimension_dir: Path to output/data/{dimension}/

    Returns:
        Path to the updated latest.json.
    """
    os.makedirs(dimension_dir, exist_ok=True)
    latest_path = os.path.join(dimension_dir, "latest.json")

    with open(latest_path, "w") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)

    return latest_path


def archive_all(output_dir: str) -> dict:
    """
    Full archival: save recommendation + update all dimension latest.json files.

    Args:
        output_dir: Path to the output/ directory

    Returns:
        Summary of archival actions.
    """
    results = {"archived": [], "latest_updated": [], "errors": []}

    # Archive recommendation
    rec_path = os.path.join(output_dir, "portfolio-recommendation.json")
    if os.path.exists(rec_path):
        try:
            with open(rec_path) as f:
                rec = json.load(f)
            archive_dir = os.path.join(output_dir, "data", "recommendations")
            path = archive_recommendation(rec, archive_dir)
            results["archived"].append(path)
        except Exception as e:
            results["errors"].append(f"Recommendation archive failed: {e}")

    # Update latest.json for each dimension
    dimensions = {
        "macro": "data/macro/macro-raw.json",
        "political": "data/political/political-raw.json",
        "fundamentals": "data/fundamentals/fundamentals-raw.json",
        "sentiment": "data/sentiment/sentiment-raw.json",
    }

    for dim, raw_file in dimensions.items():
        raw_path = os.path.join(output_dir, raw_file)
        if os.path.exists(raw_path):
            try:
                with open(raw_path) as f:
                    raw_data = json.load(f)
                dim_dir = os.path.join(output_dir, "data", dim)
                path = update_latest(raw_data, dim_dir)
                results["latest_updated"].append(path)
            except Exception as e:
                results["errors"].append(f"{dim} latest update failed: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Archive recommendation and update latest.json files")
    parser.add_argument("--output-dir", required=True, help="Path to output/ directory")
    args = parser.parse_args()

    results = archive_all(args.output_dir)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/scripts/test_recommendation_archiver.py -v
```
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/data-manager/scripts/recommendation_archiver.py tests/scripts/test_recommendation_archiver.py
git commit -m "feat: add recommendation archiver with latest.json updates (Step 12)"
```

---

## Chunk 6: Skills (SKILL.md files)

### Task 15: Create Pipeline Skills (Steps 0-5)

**Files:**
- Create: `.claude/skills/staleness-checker/SKILL.md`
- Create: `.claude/skills/query-interpreter/SKILL.md`
- Create: `.claude/skills/macro-collector/SKILL.md`
- Create: `.claude/skills/political-collector/SKILL.md`
- Create: `.claude/skills/fundamentals-collector/SKILL.md`
- Create: `.claude/skills/sentiment-collector/SKILL.md`

Each SKILL.md defines the skill's role, trigger, inputs, outputs, and execution instructions. These are prompt files that guide the LLM during pipeline execution.

- [ ] **Step 1: Create staleness-checker SKILL.md**

Create `.claude/skills/staleness-checker/SKILL.md` — see spec Step 0. Key content:
- Role: Check data freshness, route REUSE/FULL per dimension
- Script invocation: `python .claude/skills/staleness-checker/scripts/staleness_checker.py --output-dir output/ --write`
- Output: `output/staleness-routing.json`
- On failure: Fall back to FULL for all dimensions

- [ ] **Step 2: Create query-interpreter SKILL.md**

Create `.claude/skills/query-interpreter/SKILL.md` — see spec Step 1. Key content:
- Role: Parse user natural language → user-profile.json
- LLM-only (no script)
- Required fields: budget, investment_period_months, risk_tolerance
- New field: asset_scope (etf_only | etf_and_stocks | broad, default: etf_and_stocks)
- Output: `output/user-profile.json`
- On failure: Follow-up question to user

- [ ] **Step 3: Create macro-collector SKILL.md**

Create `.claude/skills/macro-collector/SKILL.md` — see spec Step 2. Key content:
- Role: Collect US/KR/global macroeconomic indicators via web research
- Reference: `references/macro-indicator-ranges.md` (collection targets)
- Source tagging rules: [Official], [Portal], [KR-Portal]
- Output: `output/data/macro/macro-raw.json`
- Success criteria: Minimum 5 core indicators
- On failure: Retry once, then Grade D treatment

- [ ] **Step 4: Create political-collector SKILL.md**

Create `.claude/skills/political-collector/SKILL.md` — see spec Step 3.

- [ ] **Step 5: Create fundamentals-collector SKILL.md**

Create `.claude/skills/fundamentals-collector/SKILL.md` — see spec Step 4.

- [ ] **Step 6: Create sentiment-collector SKILL.md**

Create `.claude/skills/sentiment-collector/SKILL.md` — see spec Step 5.

- [ ] **Step 7: Commit all pipeline skills**

```bash
git add .claude/skills/staleness-checker/SKILL.md .claude/skills/query-interpreter/SKILL.md \
  .claude/skills/macro-collector/SKILL.md .claude/skills/political-collector/SKILL.md \
  .claude/skills/fundamentals-collector/SKILL.md .claude/skills/sentiment-collector/SKILL.md
git commit -m "feat: add pipeline skills for Steps 0-5 (staleness, query, 4 collectors)"
```

### Task 16: Create Validation & Scoring Skills (Steps 6-7)

**Files:**
- Create: `.claude/skills/data-validator/SKILL.md`
- Create: `.claude/skills/environment-scorer/SKILL.md`

- [ ] **Step 1: Create data-validator SKILL.md**

Create `.claude/skills/data-validator/SKILL.md` — see spec Step 6. Key content:
- Role: Validate 4 raw data files + assign grades (deterministic only)
- Script: `python .claude/skills/data-validator/scripts/data_validator.py --output-dir output/ --write`
- Reference: `references/macro-indicator-ranges.md` (sanity check ranges)
- 3-stage validation: arithmetic → cross-reference → sanity
- Output: `output/validated-data.json`

- [ ] **Step 2: Create environment-scorer SKILL.md**

Create `.claude/skills/environment-scorer/SKILL.md` — see spec Step 7. Key content:
- Role: Score environment dimensions (script helper + LLM judgment)
- Script: `python .claude/skills/environment-scorer/scripts/environment_scorer.py --validated-data output/validated-data.json --write --output-dir output/`
- LLM performs: regime classification, direction assessment, key driver identification
- Output: `output/environment-assessment.json`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/data-validator/SKILL.md .claude/skills/environment-scorer/SKILL.md
git commit -m "feat: add validation and scoring skills (Steps 6-7)"
```

### Task 17: Create Output & Quality Skills (Steps 9, 11, 12)

**Files:**
- Create: `.claude/skills/quality-gate/SKILL.md`
- Create: `.claude/skills/portfolio-dashboard-generator/SKILL.md`
- Create: `.claude/skills/memo-generator/SKILL.md`
- Create: `.claude/skills/data-manager/SKILL.md`

- [ ] **Step 1: Create quality-gate SKILL.md**

Create `.claude/skills/quality-gate/SKILL.md` — see spec Step 9. Key content:
- Role: 7 deterministic checks (no LLM judgment)
- Script: `python .claude/skills/quality-gate/scripts/quality_gate.py --recommendation output/portfolio-recommendation.json --user-profile output/user-profile.json --write --output-dir output/`
- Output: `output/quality-report.json`

- [ ] **Step 2: Create portfolio-dashboard-generator SKILL.md**

Create `.claude/skills/portfolio-dashboard-generator/SKILL.md` — see spec Step 11. Key content:
- Role: Generate HTML dashboard with TailwindCSS CDN + Chart.js
- References: `references/output-templates/dashboard-template.md`, `references/output-templates/color-system.md`
- LLM generates HTML (no script)
- Output: `output/reports/portfolio_{lang}_{date}.html`
- 10 sections as defined in dashboard-template.md

- [ ] **Step 3: Create memo-generator SKILL.md**

Create `.claude/skills/memo-generator/SKILL.md` — see spec Step 11. Key content:
- Role: Generate DOCX investment memo
- Script: `python .claude/skills/memo-generator/scripts/docx_generator.py --recommendation output/portfolio-recommendation.json --environment output/environment-assessment.json --profile output/user-profile.json --output output/reports/portfolio_{lang}_{date}.docx`
- Reference: `references/output-templates/memo-template.md`

- [ ] **Step 4: Create data-manager SKILL.md**

Create `.claude/skills/data-manager/SKILL.md` — see spec Step 12. Key content:
- Role: Archive recommendation + update latest.json
- Script: `python .claude/skills/data-manager/scripts/recommendation_archiver.py --output-dir output/`

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/quality-gate/SKILL.md .claude/skills/portfolio-dashboard-generator/SKILL.md \
  .claude/skills/memo-generator/SKILL.md .claude/skills/data-manager/SKILL.md
git commit -m "feat: add output and quality skills (Steps 9, 11, 12)"
```

---

## Chunk 7: Agents & Master Orchestrator

### Task 18: Create environment-researcher Agent

**Files:**
- Create: `.claude/agents/environment-researcher/AGENT.md`

- [ ] **Step 1: Create AGENT.md**

Create `.claude/agents/environment-researcher/AGENT.md` — see spec Section 5.2. Key content:

```markdown
# Environment Researcher Agent

## Identity
Data collection specialist. I collect, tag, and report. I form no opinions.

## Inputs
- `output/user-profile.json` (market_preference → collection scope)
- `output/staleness-routing.json` (per-dimension REUSE/FULL routing)

## Execution
For each dimension in order (macro → political → fundamentals → sentiment):
1. Read staleness routing for this dimension
2. If REUSE: skip, use existing data
3. If FULL: invoke the corresponding collector skill
4. Verify output file exists and is non-empty

## Skills Used
- macro-collector (Step 2)
- political-collector (Step 3)
- fundamentals-collector (Step 4)
- sentiment-collector (Step 5)

## Output
4 raw JSON files:
- `output/data/macro/macro-raw.json`
- `output/data/political/political-raw.json`
- `output/data/fundamentals/fundamentals-raw.json`
- `output/data/sentiment/sentiment-raw.json`

## Completion Signal
My return message IS the completion signal. The orchestrator receives it via Agent tool return value — NOT file polling.

## Failure Handling
- Web search failure → retry once with alternate query
- 3+ consecutive failures → assume network issue, proceed with collected data
- Grade D treatment for uncollectable items
- I NEVER stop because one dimension fails
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/environment-researcher/AGENT.md
git commit -m "feat: add environment-researcher agent definition"
```

### Task 19: Create portfolio-analyst Agent

**Files:**
- Create: `.claude/agents/portfolio-analyst/AGENT.md`

- [ ] **Step 1: Create AGENT.md**

Create `.claude/agents/portfolio-analyst/AGENT.md` — see spec Section 5.3. Key content:

```markdown
# Portfolio Analyst Agent

## Identity
Core analysis engine. I construct 3 portfolio options from environment data + user profile.

## Inputs
- `output/environment-assessment.json`
- `output/user-profile.json`
- `references/allocation-framework.md`
- `references/asset-universe.md`
- `references/portfolio-construction-rules.md`

## 6-Stage Construction

### Stage 1: Regime Classification (LLM)
Read environment-assessment.json regime_classification. Confirm or adjust.

### Stage 2: Base Allocation (Script)
```bash
python .claude/agents/portfolio-analyst/scripts/allocation_calculator.py \
  --regime {regime} --risk aggressive --horizon {horizon}
# Repeat for moderate and conservative
```

### Stage 3-4: Risk + Horizon Adjustment (Script)
Handled by allocation_calculator.py in Stage 2 call.

### Stage 5: Holding Selection (LLM)
- Read asset-universe.md
- Filter by user's asset_scope
- Select 2-4 tickers per asset class
- Each holding must have rationale tied to environment assessment
- Each holding carries source_tag

### Stage 6: Return Estimation (Script + LLM)
1. LLM provides scenario premises (bull/base/bear assumptions)
2. Script computes weighted returns:
```bash
python .claude/agents/portfolio-analyst/scripts/return_estimator.py \
  --allocation '{...}' --returns '{...}' --probabilities '{...}'
```

## Output
`output/portfolio-recommendation.json` with 3 options.

## Anti-Generic Rules
- Every holding rationale must be specific to the current environment
- "Good for diversification" is NOT a valid rationale
- Replace company name with competitor — if rationale still holds, rewrite
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/portfolio-analyst/AGENT.md
git commit -m "feat: add portfolio-analyst agent definition with 6-stage construction"
```

### Task 20: Create critic Agent

**Files:**
- Create: `.claude/agents/critic/AGENT.md`

- [ ] **Step 1: Create AGENT.md**

Create `.claude/agents/critic/AGENT.md` — see spec Section 5.4. Key content:

```markdown
# Critic Agent

## Identity
Independent qualitative reviewer. I judge from outputs only.

## Isolation Protocol
I receive ONLY file paths. I do NOT receive:
- Raw data files
- environment-assessment.json
- Analyst intermediate reasoning
- Prior conversation context

## Inputs (file paths only)
1. `output/portfolio-recommendation.json`
2. `output/user-profile.json`
3. `output/quality-report.json`

## 3 Evaluation Items

### 1. User-Specificity
Is this recommendation genuinely tailored to this user's budget/horizon/risk/preferences, or generic?
- PASS: Recommendations demonstrably change with different user profiles
- FAIL: Could apply to any user with the same risk tolerance

### 2. Mechanism Chain Completeness
Does every key_risk have a logically sound "Risk → Impact → Response" chain?
- PASS: All chains have 3 elements with specific numbers/percentages
- FAIL: Any risk stated as category without mechanism

### 3. Substantive Option Differentiation
Do the 3 options differ in investment logic, not just numbers?
- PASS: Each option has a distinct investment thesis
- FAIL: Options are just scaled versions of each other

## Output
`output/critic-report.json`

## Feedback Loop
- FAIL → specific remediation instructions → portfolio-analyst patches → I re-review (max 1 iteration)
- Remaining issues after re-review → passed with [Quality flag] tags
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/critic/AGENT.md
git commit -m "feat: add critic agent definition with isolation protocol"
```

### Task 21: Create CLAUDE.md Master Orchestrator

**Files:**
- Create: `CLAUDE.md`

This is the largest and most critical file — the master orchestrator that controls the entire pipeline.

- [ ] **Step 1: Create CLAUDE.md**

Create `CLAUDE.md` following the stock-analysis-agent pattern. Key sections:

1. **Identity & Mission** — Portfolio recommendation assistant, 5 core principles
2. **Session Start Protocol** — Display state block (date, data mode, ready signal)
3. **Pipeline** — 12-step sequential pipeline with file handoff points
4. **Step Execution Details** — Per-step instructions with skill/agent invocation
5. **Agent Invocation Rules**:
   - environment-researcher: after Step 1, pass staleness-routing + user-profile
   - portfolio-analyst: after Step 7, pass environment-assessment + user-profile
   - critic: after Step 9, pass ONLY 3 file paths (isolation protocol)
6. **Failure Handling** — Timeout table, stall detection, fallback chains
7. **Output Delivery** — Chat summary + file links
8. **Staleness Rules** — Per-dimension thresholds
9. **Source Tags & Grading** — Tag definitions + grade criteria

Key CLAUDE.md rules:
- NEVER use sleep + file polling (stall detection protocol)
- Agent return value IS the completion signal
- Always deliver something — partial output > no output
- Critic isolation: do NOT pass raw data or intermediate reasoning
- Language auto-detection: respond in user's language

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "feat: add CLAUDE.md master orchestrator for 12-step pipeline"
```

### Task 22: Final Integration

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

Minimal README with:
- Project description
- Prerequisites (Python 3.11+, python-docx)
- Setup instructions (venv, pip install)
- Usage (how to start a conversation)
- Architecture overview (link to design doc)

- [ ] **Step 2: Run all tests**

```bash
cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor
source .venv/bin/activate
pytest tests/ -v
```
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup and usage instructions"
```

- [ ] **Step 4: Final verification**

```bash
# Verify directory structure matches design spec
find . -name "*.py" -o -name "*.md" -o -name "*.json" -o -name "*.ini" | sort
# Verify all skill/agent directories exist
ls -la .claude/skills/*/
ls -la .claude/agents/*/
```

---

## Execution Summary

| Chunk | Tasks | Focus | Estimated Steps |
|-------|-------|-------|----------------|
| 1 | 1 | Project foundation (git, config, dirs) | 9 |
| 2 | 2–6 | Reference files (7 files) | 8 |
| 3 | 7–9 | Python scripts — environment pipeline (3 scripts + tests) | 15 |
| 4 | 10–12 | Python scripts — portfolio construction (3 scripts + tests) | 15 |
| 5 | 13–14 | Python scripts — output & persistence (2 scripts + tests) | 10 |
| 6 | 15–17 | Skills (12 SKILL.md files) | 13 |
| 7 | 18–22 | Agents (3 AGENT.md) + CLAUDE.md + README | 12 |
| **Total** | **22** | | **~82** |

## Key Dependencies

```
Chunk 1 (foundation) → everything
Chunk 2 (references) → Chunks 3-7 (scripts/skills/agents reference these)
Chunk 3 (env scripts) → Chunk 6 (env skills use these scripts)
Chunk 4 (portfolio scripts) → Chunk 7 (portfolio-analyst agent uses these)
Chunk 5 (output scripts) → Chunk 6 (output skills use these scripts)
Chunk 6 (skills) → Chunk 7 (agents invoke skills)
Chunk 7 (agents + CLAUDE.md) → final integration
```

Chunks 3, 4, 5 are independent of each other and can be parallelized via subagents.

---

## Implementation Notes (from review)

### Python Filename Convention

All Python script filenames use **underscores** (Python convention) for importability:
- `staleness_checker.py` (not `staleness-checker.py`)
- `data_validator.py`, `environment_scorer.py`, etc.

The enclosing **directory** names use hyphens per the design spec (e.g., `.claude/skills/staleness-checker/scripts/staleness_checker.py`).

### Canonical Regime Names

The 5 canonical regime names used consistently throughout the codebase:
- `early-expansion`
- `mid-cycle`
- `late-cycle`
- `recession`
- `recovery`

Note: The spec's example `late-cycle-expansion` in the environment-assessment schema is illustrative only — not a sixth regime.

### Horizon Mapping (investment_period_months → horizon string)

| Spec Bucket | Months | Horizon String | Adjustment |
|-------------|--------|---------------|------------|
| < 6 months | 1-5 | `"short"` | Cash +10, equity −10 |
| 6-12 months | 6-12 | `"medium"` | No adjustment |
| 1-3 years | 13-36 | `"medium"` | No adjustment |
| 3-5 years | 37-60 | `"medium-long"` | US eq +3, KR eq +2, cash −5 |
| 5+ years | 61+ | `"long"` | US eq +5, KR eq +5, bonds −5, cash −5 |

Mapping function: `months_to_horizon()` in `allocation_calculator.py`.

### SKILL.md Content Requirements

Each collector SKILL.md (macro, political, fundamentals, sentiment) MUST include these sections from the design spec:

1. **Collection Targets** — exactly from spec Steps 2-5 tables
2. **Output Schema** — JSON schema from spec (macro-raw.json, etc.)
3. **Source Tagging Rules** — [Official], [Portal], [KR-Portal], [News], [Calc], [Est]
4. **Success Criteria** — minimum indicator counts from spec
5. **Failure Handling** — retry once, Grade D treatment
6. **Staleness Check** — read staleness-routing.json before collection

### CLAUDE.md Critical Sections

The master orchestrator CLAUDE.md must include:

1. **Identity & Mission** — 5 core principles verbatim from spec
2. **Session Start** — display date, data mode, ready signal
3. **Pipeline Execution** — 12-step sequence with file verification after each step
4. **Agent Invocation Syntax**:
   - `environment-researcher`: pass staleness-routing.json + user-profile.json
   - `portfolio-analyst`: pass environment-assessment.json + user-profile.json
   - `critic`: pass ONLY 3 file paths (isolation protocol — no raw data, no intermediate reasoning)
5. **Failure Handling Table** — all 13 rows from spec Section 10
6. **Stall Detection Protocol** — NEVER use sleep + file polling; agent return = completion signal
7. **Timeout Table** — per-step timeouts (15-min full pipeline, 2-min critic, etc.)
8. **Language Auto-Detection** — respond in user's input language

### Integration Tests (deferred to post-implementation)

Based on spec Verification Plan (8 scenarios):

| # | Test | What to Verify |
|---|------|---------------|
| 1 | Korean moderate input | Full pipeline end-to-end with KRW budget |
| 2 | English aggressive input | Horizon adjustment (+5% equity) applied |
| 3 | Staleness reuse | REUSE routing skips collection |
| 4 | Collection failure | Grade D "—" display + exclusions |
| 5 | Quality gate | allocation sum, source tags, disclaimer |
| 6 | Critic feedback loop | FAIL → patch → re-review flow |
| 7 | Network blockage | Partial output within 15 minutes |
| 8 | Option differentiation | ≥10pp equity weight difference |

These should be implemented as `tests/integration/test_pipeline.py` after all components are in place.
