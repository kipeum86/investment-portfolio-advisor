# Investment Portfolio Advisor — Agent System Design Specification v2

**Date**: 2026-03-17
**Status**: Revised Draft
**Phase**: 1 (Portfolio Recommendation Engine)
**Changes from v1**: Sequential execution clarified, quality-checker/critic ownership separated, critic isolation protocol, data-validator split, step numbering normalized, output generation timing changed, intermediate JSON schemas added

---

## Context

The existing stock-analysis-agent analyzes individual stocks bottom-up. This project goes the opposite direction — it takes a user's investment profile (budget/horizon/risk tolerance) as input, performs top-down analysis across macroeconomic, political, fundamental, and sentiment dimensions, then recommends 3 portfolios by risk level. A Personal Investment Manager.

**Key Decisions**:
- Built as a standalone repo (`investment-portfolio-advisor`)
- Borrows skill/agent patterns from stock-analysis-agent but code is independent
- Architecture: 2-Phase sequential pipeline (environment assessment sequential collection → portfolio construction)
- Asset classes: Multi-asset (equities + ETFs + bonds + cash)
- Data sources: Web research-based (no dedicated API in Phase 1)
- Output: HTML dashboard + DOCX investment memo + chat summary
- 3 options differentiated by risk level (aggressive / moderate / conservative)
- Language: Bilingual auto-detection (Korean / English)

---

## 1. Identity & Mission

A portfolio recommendation assistant for individual investors. Covers US equities/ETFs, KR equities/ETFs, bonds, and cash equivalents.

**5 Core Principles** (inherited from stock-analysis-agent):
1. **Blank > Wrong Number**: Grade D data displayed as "—", never fabricated
2. **No Source = No Number**: Every figure must carry a source tag
3. **User-Specificity**: Generic recommendations are not recommendations. Must be tailored to user profile
4. **Adaptive Data**: Enhanced when MCP is available, Standard otherwise — both produce valid output
5. **Mechanism Required**: Every risk must have a causal chain (risk → portfolio impact → response action)

**Disclaimer**: All outputs include "This is not investment advice. For informational purposes only."

---

## 2. Pipeline Overview

```
User Input ("50M KRW, 1 year, moderate risk tolerance")
    │
    ▼
[Step 0] Staleness Check — Check if existing environment data can be reused
    │                       → Per-dimension REUSE / FULL routing decision
    ▼
[Step 1] Query Interpreter — Profile parsing → user-profile.json
    │
    ▼
══════════════ Phase 1: Environment Assessment (Sequential) ══════════════
    │
    │  [environment-researcher agent]
    │    Step 2: macro-collector      → macro-raw.json      (staleness routing applied)
    │    Step 3: political-collector  → political-raw.json   (staleness routing applied)
    │    Step 4: fundamentals-collector → fundamentals-raw.json (staleness routing applied)
    │    Step 5: sentiment-collector  → sentiment-raw.json   (staleness routing applied)
    │
    ▼
[Step 6] Data Validation (script) → validated-data.json
    │
    ▼
[Step 7] Environment Scoring (LLM) → environment-assessment.json
    │
    ▼
══════════════ Phase 2: Portfolio Construction ══════════════
    │
    │  [portfolio-analyst agent]
    │    [Step 8] Reads: environment-assessment.json + user-profile.json + reference frameworks
    │             Writes: portfolio-recommendation.json (3 options)
    │
    ▼
[Step 9] Quality Gate (script) — Deterministic validation → quality-report.json
    │
    ▼
[Step 10] Critic Review (agent) — Qualitative LLM judgment → critic-report.json
    │   │
    │   └── On FAIL: portfolio-analyst patch → Critic re-review (max 1 iteration)
    │
    ▼
[Step 11] Output Generation — Generated only after Critic pass
    │    ├── HTML Dashboard (3-option comparison)
    │    └── DOCX Investment Memo
    │
    ▼
[Step 12] Persistence + Delivery
```

**Changes from v1**:
- Environment collection runs sequentially. Parallel execution moved to Phase 2+ expansion.
- Data Validation (script) and Environment Scoring (LLM) split into separate steps.
- Quality Gate (script) and Critic (LLM) ownership fully separated.
- Output generation (HTML/DOCX) moved after Critic — avoids wasted regeneration.

---

## 3. Step-by-Step Detail

### Step 0: Staleness Check
- **Executor**: Script (`staleness-checker.py`)
- **Input**: `output/data/*/latest.json` (if they exist)
- **Processing**: Per-dimension timestamp comparison, staleness rules applied
- **Output**: `output/staleness-routing.json`
- **Success criteria**: Routing decision exists for all 4 dimensions
- **Validation**: Schema validation (only REUSE/FULL values allowed)
- **On failure**: Fall back to FULL for all dimensions (conservative default)

**Staleness Rules**:

| Dimension | Reuse (REUSE) | Full Collection (FULL) |
|-----------|---------------|----------------------|
| Macroeconomic | < 24 hours | ≥ 24 hours |
| Political/Geopolitical | < 7 days | ≥ 7 days |
| Fundamentals | < 3 days | ≥ 3 days |
| Sentiment | < 12 hours | ≥ 12 hours |

> v1's DELTA_FAST (partial refresh) removed. Phase 1 uses only REUSE or FULL — simpler branching means simpler implementation.

**Staleness Routing Application**: environment-researcher reads `staleness-routing.json` before starting collection, conditionally executing each collector:
- `REUSE` → Skip that collector, use existing `latest.json` as-is
- `FULL` → Run that collector, collect fresh data

### Step 1: Query Interpreter
- **Executor**: LLM
- **Input**: User natural language input
- **Processing**: Investment profile extraction + normalization
- **Output**: `output/user-profile.json`
- **Success criteria**: 3 required fields extracted (budget, investment_period_months, risk_tolerance)
- **Validation**: Schema validation (required fields present + type check)
- **On failure**: Follow-up question to user for missing fields

**Output Schema**: `user-profile.json`
```json
{
  "budget": 50000000,
  "budget_currency": "KRW",
  "budget_usd_equivalent": 38000,
  "investment_period_months": 12,
  "investment_horizon": "medium",
  "risk_tolerance": "moderate",
  "asset_scope": "etf_and_stocks",
  "sector_preferences": [],
  "sector_exclusions": [],
  "existing_holdings": [],
  "market_preference": "mixed",
  "output_language": "ko",
  "query_timestamp": "2026-03-17T10:00:00Z"
}
```
- `investment_horizon` determination: < 6 months = "short", 6–36 months = "medium", > 36 months = "long"
- `asset_scope` determination: "ETF로만" / "ETF only" → `"etf_only"`, "개별주도 포함" / "include individual stocks" → `"etf_and_stocks"`, "대안자산 포함" / "include alternatives" → `"broad"`. Default: `"etf_and_stocks"`. The portfolio-analyst filters `asset-universe.md` by this scope when selecting holdings.
- `market_preference` default: "mixed". Set to US/KR only when user explicitly mentions one market.

### Step 2: Macro Collection
- **Executor**: LLM (web research)
- **Input**: `user-profile.json` (market_preference determines collection scope), `staleness-routing.json`
- **Processing**: US/KR/global macroeconomic indicator web search + source tagging
- **Output**: `output/data/macro/macro-raw.json`
- **Success criteria**: Minimum 5 core indicators collected (GDP, CPI, policy rate, unemployment, yield curve)
- **Validation**: Required indicator presence check
- **On failure**: Retry once (alternate search query). If still failing, Grade D treatment.

**Collection Targets**:

| Category | Indicators |
|----------|-----------|
| US | GDP growth rate, CPI, PCE, federal funds rate, unemployment rate, yield curve (2y-10y), FOMC outlook |
| KR | GDP growth rate, CPI, BOK base rate, KRW/USD exchange rate |
| Global | ECB rate, BOJ rate, global trade environment |

**Output Schema**: `macro-raw.json`
```json
{
  "collection_timestamp": "2026-03-17T10:05:00Z",
  "indicators": [
    {
      "id": "us_gdp_growth",
      "category": "us",
      "name": "US GDP Growth Rate (QoQ annualized)",
      "value": 2.3,
      "unit": "%",
      "period": "Q4 2025",
      "source_tag": "[Official]",
      "source_url": "https://...",
      "retrieved_at": "2026-03-17T10:05:00Z"
    }
  ],
  "collection_gaps": []
}
```

### Step 3: Political Collection
- **Executor**: LLM (web research)
- **Input**: `user-profile.json`, `staleness-routing.json`
- **Processing**: Political/geopolitical risk web search + source tagging
- **Output**: `output/data/political/political-raw.json`
- **Success criteria**: Minimum 1 item each for US + geopolitical categories
- **Validation**: Per-category minimum count check
- **On failure**: Retry once. If still failing, Grade D treatment.

**Collection Targets**:
- US: Trade policy/tariffs, tech regulation, fiscal policy, financial regulation
- KR: Political situation, corporate regulation, Value-Up program
- Geopolitical: US-China relations, regional conflicts, semiconductor supply chain

**Output Schema**: `political-raw.json`
```json
{
  "collection_timestamp": "...",
  "developments": [
    {
      "id": "us_tariff_policy",
      "category": "us_trade",
      "headline": "...",
      "summary": "...",
      "impact_assessment": "negative | neutral | positive",
      "affected_sectors": ["technology", "manufacturing"],
      "source_tag": "[News]",
      "source_url": "https://...",
      "retrieved_at": "..."
    }
  ],
  "collection_gaps": []
}
```

### Step 4: Fundamentals Collection
- **Executor**: LLM (web research)
- **Input**: `user-profile.json`, `staleness-routing.json`
- **Processing**: Market-level fundamental indicator web search + source tagging
- **Output**: `output/data/fundamentals/fundamentals-raw.json`
- **Success criteria**: S&P 500 P/E + KOSPI PER collected at minimum
- **Validation**: Required indicator presence check
- **On failure**: Retry once. If still failing, Grade D treatment.

**Collection Targets**:
- S&P 500 P/E, Shiller CAPE
- KOSPI PER, PBR
- Sector rotation signals, sector ETF performance YTD
- S&P 500 earnings growth estimates
- Corporate credit spreads (investment grade vs high yield)

**Output Schema**: `fundamentals-raw.json`
```json
{
  "collection_timestamp": "...",
  "market_metrics": [
    {
      "id": "sp500_pe",
      "market": "us",
      "name": "S&P 500 Trailing P/E",
      "value": 22.5,
      "unit": "ratio",
      "period": "current",
      "source_tag": "[Portal]",
      "source_url": "https://...",
      "retrieved_at": "..."
    }
  ],
  "sector_performance": [
    {
      "sector": "technology",
      "etf_ticker": "XLK",
      "ytd_return": 12.3,
      "source_tag": "[Portal]",
      "source_url": "..."
    }
  ],
  "collection_gaps": []
}
```

### Step 5: Sentiment Collection
- **Executor**: LLM (web research)
- **Input**: `user-profile.json`, `staleness-routing.json`
- **Processing**: Market sentiment indicator web search + source tagging
- **Output**: `output/data/sentiment/sentiment-raw.json`
- **Success criteria**: VIX + Fear & Greed collected at minimum
- **Validation**: Required indicator presence check
- **On failure**: Retry once. If still failing, Grade D treatment.

**Collection Targets**:
- VIX Index
- CNN Fear & Greed Index
- Put/Call Ratio (CBOE)
- Fund flows (equity/bond/money market ETFs)
- AAII Individual Investor Survey
- Institutional investor positioning

**Output Schema**: `sentiment-raw.json`
```json
{
  "collection_timestamp": "...",
  "indicators": [
    {
      "id": "vix",
      "name": "CBOE Volatility Index (VIX)",
      "value": 18.5,
      "unit": "index",
      "interpretation": "moderate_fear",
      "source_tag": "[Portal]",
      "source_url": "...",
      "retrieved_at": "..."
    }
  ],
  "collection_gaps": []
}
```

### Step 6: Data Validation
- **Executor**: Script (`data-validator.py`)
- **Input**: 4 raw JSON files
- **Processing**: 3-stage validation — arithmetic consistency → cross-reference → sanity check. Assigns Grade A/B/C/D to each data point.
- **Output**: `output/validated-data.json`
- **Success criteria**: All raw data points graded
- **Validation**: Confirm Grade D items are null-treated
- **On failure**: Validation script error → log error, assign blanket Grade C to raw data, proceed

**Grading System**:

| Grade | Criteria |
|-------|---------|
| A | Official government statistics + arithmetic consistency |
| B | 2+ independent sources ≤ 5% difference |
| C | Single source, arithmetic consistency confirmed |
| D | Unverifiable → `null` treatment, excluded from analysis |

**Output Schema**: `validated-data.json`
```json
{
  "validation_timestamp": "...",
  "overall_data_grade": "B",
  "validated_indicators": {
    "macro": [
      {
        "id": "us_gdp_growth",
        "value": 2.3,
        "grade": "A",
        "source_tag": "[Official]"
      }
    ],
    "political": [],
    "fundamentals": [],
    "sentiment": []
  },
  "exclusions": [
    {
      "id": "nyse_margin_debt",
      "reason": "Single source, failed sanity check",
      "original_grade": "D"
    }
  ]
}
```

### Step 7: Environment Scoring
- **Executor**: LLM
- **Input**: `output/validated-data.json`
- **Processing**: Scores each of 6 dimensions on a 1–10 scale with directional assessment + regime classification, based on validated data. A helper script (`environment-scorer.py`) computes positions relative to historical ranges; the LLM performs qualitative judgment and final regime classification.
- **Output**: `output/environment-assessment.json`
- **Success criteria**: 6 dimension scores + regime classification completed
- **Validation**: Score range 1–10, direction enum check (script); regime classification consistency with indicators (LLM self-check)
- **On failure**: Scorer script failure → LLM scores directly using reference file (`macro-indicator-ranges.md`)

**Output Schema**: `environment-assessment.json`
```json
{
  "assessment_timestamp": "...",
  "data_grade": "B",
  "environment_scores": {
    "macro_us": { "score": 6.5, "direction": "neutral-positive", "grade": "B", "key_drivers": ["..."] },
    "macro_kr": { "score": 5.0, "direction": "neutral", "grade": "B", "key_drivers": ["..."] },
    "political": { "score": 4.0, "direction": "negative", "grade": "C", "key_drivers": ["..."] },
    "fundamentals_us": { "score": 7.0, "direction": "positive", "grade": "B", "key_drivers": ["..."] },
    "fundamentals_kr": { "score": 5.5, "direction": "neutral", "grade": "B", "key_drivers": ["..."] },
    "sentiment": { "score": 6.0, "direction": "neutral-positive", "grade": "B", "key_drivers": ["..."] }
  },
  "regime_classification": "late-cycle-expansion",
  "regime_rationale": "...",
  "sanity_alerts": []
}
```

### Step 8: Portfolio Construction
- **Executor**: portfolio-analyst agent (LLM + script hybrid)
- **Input**: `environment-assessment.json`, `user-profile.json`, `references/allocation-framework.md`, `references/asset-universe.md`
- **Processing**: 6-stage construction (detailed below)
- **Output**: `output/portfolio-recommendation.json`
- **Success criteria**: 3 portfolio options completed, each option's allocation totals exactly 100%
- **Validation**: Allocation sum check (script), holding count range check
- **On failure**: Sum ≠ 100% → re-run `allocation-calculator.py`. Holding selection failure → retry with alternate tickers.

**6-Stage Construction Logic (LLM/Script Mapping)**:

| Stage | Description | Executor | Rationale |
|-------|------------|----------|-----------|
| 1. Regime Classification | Environment scores → regime judgment | **LLM** | Qualitative synthesis required (already done in Step 7, confirmed/adjusted here) |
| 2. Base Allocation | Apply regime-specific allocation ranges | **Script** (`allocation-calculator.py`) | Regime → range mapping is deterministic |
| 3. Risk Adjustment | Adjust within ranges for 3 risk profiles | **Script** (`allocation-calculator.py`) | Aggressive = upper bound, moderate = midpoint, conservative = lower bound — rule-based |
| 4. Horizon Adjustment | Shift allocation based on investment period | **Script** (`allocation-calculator.py`) | Period-based adjustment rules are deterministic |
| 5. Holding Selection | Select 2–4 tickers per asset class | **LLM** | Requires sector tilt and environmental context judgment |
| 6. Return Estimation | Expected returns per bull/base/bear scenario | **Script** (`return-estimator.py`) + **LLM** (scenario premises) | Scenario premises require LLM; calculations are script |

**Regime-Based Allocation Ranges** (Stage 2 reference):

| Regime | US Equity | KR Equity | Bonds | Alternatives | Cash |
|--------|-----------|-----------|-------|-------------|------|
| Early Expansion | 50–65% | 10–20% | 15–25% | 5–10% | 0–5% |
| Mid-Cycle | 40–55% | 10–15% | 20–30% | 5–10% | 5–10% |
| Late-Cycle | 30–45% | 5–15% | 30–40% | 5–10% | 10–15% |
| Recession | 20–35% | 5–10% | 35–50% | 5–10% | 15–25% |
| Recovery | 45–60% | 15–20% | 15–25% | 5–10% | 5–10% |

**Horizon Adjustment Rules** (Stage 4):

| Horizon | Adjustment |
|---------|-----------|
| < 6 months | Cash +10%, equities −10% |
| 6–12 months | Neutral |
| 1–3 years | Base allocation |
| 3–5 years | Equities +5%, cash −5% |
| 5+ years | Equities +10%, bonds −5%, cash −5% |

**Output Schema**: `portfolio-recommendation.json`
```json
{
  "recommendation_timestamp": "...",
  "user_profile_hash": "...",
  "regime": "late-cycle-expansion",
  "options": [
    {
      "option_id": "aggressive",
      "label": "Aggressive Portfolio",
      "allocation": {
        "us_equity": 45,
        "kr_equity": 15,
        "bonds": 25,
        "alternatives": 10,
        "cash": 5,
        "total": 100
      },
      "holdings": [
        {
          "asset_class": "us_equity",
          "ticker": "VOO",
          "name": "Vanguard S&P 500 ETF",
          "weight": 20,
          "rationale": "...",
          "source_tag": "[Portal]"
        }
      ],
      "scenarios": {
        "bull": { "expected_return": 18.5, "probability": 25, "assumptions": "..." },
        "base": { "expected_return": 8.2, "probability": 50, "assumptions": "..." },
        "bear": { "expected_return": -12.0, "probability": 25, "assumptions": "..." }
      },
      "risk_return_score": 1.15
    }
  ],
  "key_risks": [
    {
      "risk": "...",
      "mechanism": "Risk → Portfolio Impact → Response Action",
      "affected_options": ["aggressive", "moderate"],
      "severity": "high"
    }
  ],
  "rebalancing_triggers": ["..."],
  "disclaimer": "This is not investment advice. For informational purposes only."
}
```

### Step 9: Quality Gate
- **Executor**: Script (`quality-gate.py`)
- **Input**: `portfolio-recommendation.json`, `user-profile.json`
- **Processing**: Deterministic validation only. No LLM judgment.
- **Output**: `output/quality-report.json`
- **Success criteria**: All checks PASS
- **Validation**: N/A (this step is the validation)
- **On failure**: FAIL items recorded in quality-report.json. Patch request sent to portfolio-analyst.

**Quality Gate Checklist** (all deterministic):

| # | Item | Method | PASS Criteria |
|---|------|--------|--------------|
| 1 | Allocation sum | 3 options × `allocation.total` | Each exactly 100 |
| 2 | Source tag coverage | source_tag ratio within holdings | ≥ 80% |
| 3 | Required fields present | Schema comparison | All required fields present |
| 4 | Disclaimer present | `disclaimer` field | Non-empty string |
| 5 | Grade D exclusion compliance | Excluded items not in holdings | 0 violations |
| 6 | User profile reflected | budget/period/risk_tolerance values reflected in output | Match confirmed |
| 7 | Option differentiation (numeric) | Equity weight difference across 3 options | Minimum 10pp difference |

### Step 10: Critic Review
- **Executor**: critic agent (LLM)
- **Input**: File paths only — `portfolio-recommendation.json`, `user-profile.json`, `quality-report.json`. No intermediate artifacts (raw data, environment-assessment, analyst reasoning) are passed.
- **Processing**: Evaluates only the 3 items requiring qualitative judgment
- **Output**: `output/critic-report.json`
- **Success criteria**: All 3 items evaluated
- **Validation**: N/A
- **On failure**: Critic timeout (2 min) → skip, attach `[No critic review]` flag and proceed

**Critic-Owned Items** (LLM judgment only):

| # | Item | Evaluation Criteria |
|---|------|-------------------|
| 1 | User-Specificity (qualitative) | Is this recommendation genuinely tailored to this user's budget/horizon/risk tolerance/preferences, or is it generic? |
| 2 | Mechanism Chain Completeness | Does every key_risk have a logically sound "Risk → Impact → Response" causal chain? |
| 3 | Substantive Option Differentiation | Do the 3 options differ not just in numbers but in investment logic and positioning? |

**Feedback Loop**: FAIL → portfolio-analyst patch (Critic provides specific remediation instructions) → Critic re-review (max 1 iteration). Remaining issues after re-review are passed through with `[Quality flag: ...]` tags attached to output.

**Critic Invocation Protocol** (specified in main agent CLAUDE.md):
```
When invoking Critic, the following rules MUST be followed:
1. Information to pass: Only 3 file paths (portfolio-recommendation.json, user-profile.json, quality-report.json)
2. Information NOT to pass: Raw data files, environment-assessment.json, analyst intermediate reasoning, prior conversation context
3. Do not summarize or explain the analysis process to Critic — let it judge from outputs alone
```

### Step 11: Output Generation
- **Executor**: Script + LLM hybrid
- **Input**: `portfolio-recommendation.json`, `environment-assessment.json`, `user-profile.json`, `critic-report.json`
- **Processing**: Generate HTML dashboard + DOCX investment memo
- **Output**: `output/reports/portfolio_{lang}_{date}.html`, `output/reports/portfolio_{lang}_{date}.docx`
- **Success criteria**: Both files generated, size > 0
- **Validation**: HTML renderable (basic structure check), DOCX openable
- **On failure**: HTML failure → retry once. DOCX failure → deliver HTML only, output memo text in chat.

**HTML Dashboard Sections**:
1. Header (user profile summary, analysis date, data confidence, Quality Flag if present)
2. Environment overview (macro/political/sentiment summary cards)
3. 3-column portfolio comparison (one column per option)
4. Asset allocation pie charts (Chart.js, per option)
5. Holding recommendation tables (per option)
6. Risk/Return scatter plot (3-option comparison)
7. Scenario comparison table (bull/base/bear)
8. Key risks + mechanism chains
9. Rebalancing triggers
10. Disclaimer

**DOCX Investment Memo Sections**: Executive Summary, Environment Analysis (4 dimensions), Regime Diagnosis, 3 Options Detail (allocation/holdings/rationale), Risk Analysis, Scenarios, Disclaimer

### Step 12: Persistence
- **Executor**: Script (`recommendation-archiver.py`)
- **Input**: `portfolio-recommendation.json`, 4 raw data files
- **Processing**: Snapshot archival + latest.json updates
- **Output**: `output/data/recommendations/{date}_recommendation.json`, per-dimension `latest.json` updates
- **Success criteria**: Archive file created
- **Validation**: File exists + size > 0
- **On failure**: Skip + log (non-blocking; recommendation already delivered)

---

## 4. Skills

### 4.1 staleness-checker
- **Role**: Check existing environment data freshness, determine per-dimension REUSE/FULL routing
- **Trigger**: Pipeline start (Step 0)
- **Scripts**: `staleness-checker.py`
- **References**: None
- **Used by**: Main agent (CLAUDE.md)

### 4.2 query-interpreter
- **Role**: Convert user natural language → user-profile.json
- **Trigger**: Step 1
- **Scripts**: None (LLM only)
- **References**: None
- **Used by**: Main agent

### 4.3 macro-collector
- **Role**: Collect US/KR/global macroeconomic indicators via web research
- **Trigger**: Step 2 (when staleness = FULL)
- **Scripts**: None (LLM web research)
- **References**: `references/macro-indicator-ranges.md` (collection target list)
- **Used by**: environment-researcher

### 4.4 political-collector
- **Role**: Collect political/geopolitical risks via web research
- **Trigger**: Step 3 (when staleness = FULL)
- **Scripts**: None
- **References**: None
- **Used by**: environment-researcher

### 4.5 fundamentals-collector
- **Role**: Collect market-level fundamental indicators via web research
- **Trigger**: Step 4 (when staleness = FULL)
- **Scripts**: None
- **References**: None
- **Used by**: environment-researcher

### 4.6 sentiment-collector
- **Role**: Collect market sentiment indicators via web research
- **Trigger**: Step 5 (when staleness = FULL)
- **Scripts**: None
- **References**: None
- **Used by**: environment-researcher

### 4.7 data-validator
- **Role**: Validate 4 raw data files + assign grades. Deterministic validation only. No scoring.
- **Trigger**: Step 6 (after all 4 collectors complete)
- **Scripts**: `data-validator.py` (arithmetic consistency, cross-reference, sanity check, grade determination)
- **References**: `references/macro-indicator-ranges.md` (historical ranges for sanity check)
- **Used by**: Main agent

### 4.8 environment-scorer
- **Role**: Validated data → per-dimension scores + direction calculation (helper). LLM performs final regime classification.
- **Trigger**: Step 7
- **Scripts**: `environment-scorer.py` (position relative to historical ranges)
- **References**: `references/macro-indicator-ranges.md`
- **Used by**: Main agent

### 4.9 portfolio-dashboard-generator
- **Role**: Generate HTML dashboard (TailwindCSS CDN + Chart.js)
- **Trigger**: Step 11
- **Scripts**: None (LLM generates HTML)
- **References**: `references/output-templates/dashboard-template.md`, `references/output-templates/color-system.md`
- **Used by**: Main agent

### 4.10 memo-generator
- **Role**: Generate DOCX investment memo
- **Trigger**: Step 11
- **Scripts**: `docx-generator.py` (python-docx)
- **References**: `references/output-templates/memo-template.md`
- **Used by**: Main agent

### 4.11 quality-gate
- **Role**: Deterministic quality validation only. 7 check items. No LLM judgment.
- **Trigger**: Step 9
- **Scripts**: `quality-gate.py`
- **References**: None
- **Used by**: Main agent

### 4.12 data-manager
- **Role**: Recommendation history archival + latest.json updates
- **Trigger**: Step 12
- **Scripts**: `recommendation-archiver.py`
- **References**: None
- **Used by**: Main agent

---

## 5. Agents

### 5.1 Main Agent (CLAUDE.md)
- **Role**: Orchestrator. Controls overall pipeline sequencing, agent invocation, skill invocation, error handling.
- **Owned steps**: Steps 0, 1, 6, 7, 9, 11, 12
- **Agent invocation rules**:
  - environment-researcher: Invoked after Step 1 completion. Pass `staleness-routing.json` + `user-profile.json`.
  - portfolio-analyst: Invoked after Step 7 completion. Pass `environment-assessment.json` + `user-profile.json`.
  - critic: Invoked after Step 9 completion. **Pass only 3 file paths** (intermediate reasoning transfer prohibited).

### 5.2 environment-researcher
- **File**: `.claude/agents/environment-researcher/AGENT.md`
- **Role**: Data collection specialist. Source tagging only, no opinion formation. Runs 4 collector skills **sequentially**.
- **Trigger**: Main agent invokes after Step 1 completion
- **Input**: `output/user-profile.json`, `output/staleness-routing.json`
- **Output**: 4 raw JSON files + completion signal
- **Skills used**: macro-collector, political-collector, fundamentals-collector, sentiment-collector
- **Execution order**: macro → political → fundamentals → sentiment (sequential)
- **Staleness routing**: Before executing each collector, checks the corresponding dimension value in `staleness-routing.json`. If REUSE, skip.

### 5.3 portfolio-analyst
- **File**: `.claude/agents/portfolio-analyst/AGENT.md`
- **Role**: Core analysis engine. Environment data + user profile → 3 portfolio option construction.
- **Trigger**: Main agent invokes after Step 7 completion
- **Input**: `output/environment-assessment.json`, `output/user-profile.json`
- **Output**: `output/portfolio-recommendation.json`
- **References**: `references/allocation-framework.md`, `references/asset-universe.md`, `references/portfolio-construction-rules.md`
- **Scripts**:
  - `allocation-calculator.py`: Stages 2–4 (regime → range, risk adjustment, horizon adjustment)
  - `return-estimator.py`: Stage 6 (per-scenario expected return calculation)

### 5.4 critic
- **File**: `.claude/agents/critic/AGENT.md`
- **Role**: Independent qualitative review. Judges from outputs only. 3 items only.
- **Trigger**: Main agent invokes after Step 9 completion
- **Input**: **File paths only** — `output/portfolio-recommendation.json`, `output/user-profile.json`, `output/quality-report.json`
- **Output**: `output/critic-report.json`
- **References**: None (no reference materials, to preserve independent judgment)
- **Isolation protocol**: Main agent does not pass raw data files, environment-assessment.json, analyst intermediate reasoning, or prior conversation context when invoking critic.

---

## 6. Source Tagging & Confidence Grading

### Source Tags

| Tag | Source |
|-----|--------|
| `[Official]` | Government statistical agencies (BLS, BEA, BOK, KOSIS) — filing-grade authority |
| `[Portal]` | Financial portals (Yahoo Finance, Trading Economics, etc.) |
| `[KR-Portal]` | Korean financial portals (Naver Finance, FnGuide, etc.) |
| `[Calc]` | Self-calculated from verified inputs |
| `[Est]` | Analyst estimates, model projections |
| `[News]` | News sources (for political/geopolitical assessment) |

### Confidence Grades
(Same as used in Step 6 data-validator. Repeated here for reference.)

| Grade | Criteria |
|-------|---------|
| A | Official government statistics + arithmetic consistency |
| B | 2+ independent sources ≤ 5% difference |
| C | Single source, arithmetic consistency confirmed |
| D | Unverifiable → displayed as "—", excluded from analysis |

---

## 7. Python Scripts

| Script | Location | Role | Executor |
|--------|----------|------|----------|
| `staleness-checker.py` | `.claude/skills/staleness-checker/scripts/` | Per-dimension timestamp comparison → REUSE/FULL decision | Script only |
| `data-validator.py` | `.claude/skills/data-validator/scripts/` | 3-stage validation + grade assignment | Script only |
| `environment-scorer.py` | `.claude/skills/environment-scorer/scripts/` | Position relative to historical ranges (LLM helper) | Script (+ LLM regime classification) |
| `allocation-calculator.py` | `.claude/agents/portfolio-analyst/scripts/` | Regime + risk tolerance + horizon → allocation ranges | Script only |
| `return-estimator.py` | `.claude/agents/portfolio-analyst/scripts/` | Allocation + per-asset return assumptions → portfolio expected return | Script only |
| `quality-gate.py` | `.claude/skills/quality-gate/scripts/` | 7 deterministic checks | Script only |
| `docx-generator.py` | `.claude/skills/memo-generator/scripts/` | portfolio-recommendation.json → DOCX | Script only |
| `recommendation-archiver.py` | `.claude/skills/data-manager/scripts/` | Recommendation history archival | Script only |

---

## 8. Data Flow

| From → To | Method | Format | Path |
|-----------|--------|--------|------|
| Step 0 → Steps 2–5 | File | JSON | `output/staleness-routing.json` |
| Step 1 → Steps 2–5, 8, 9, 10 | File | JSON | `output/user-profile.json` |
| Step 2 → Step 6 | File | JSON | `output/data/macro/macro-raw.json` |
| Step 3 → Step 6 | File | JSON | `output/data/political/political-raw.json` |
| Step 4 → Step 6 | File | JSON | `output/data/fundamentals/fundamentals-raw.json` |
| Step 5 → Step 6 | File | JSON | `output/data/sentiment/sentiment-raw.json` |
| Step 6 → Step 7 | File | JSON | `output/validated-data.json` |
| Step 7 → Steps 8, 11 | File | JSON | `output/environment-assessment.json` |
| Step 8 → Steps 9, 10, 11 | File | JSON | `output/portfolio-recommendation.json` |
| Step 9 → Step 10 | File | JSON | `output/quality-report.json` |
| Step 10 → Step 11 | File | JSON | `output/critic-report.json` |
| Step 11 → User | File | HTML, DOCX | `output/reports/portfolio_{lang}_{date}.*` |
| Step 12 → Disk | File | JSON | `output/data/recommendations/{date}_recommendation.json` |

---

## 9. Directory Structure

```
investment-portfolio-advisor/
├── CLAUDE.md                              ← Master orchestrator
├── .mcp.json
├── .gitignore
├── README.md / README.ko.md
│
├── references/                            ← Reference materials (low change frequency)
│   ├── allocation-framework.md            ← Regime → allocation mapping rules
│   ├── asset-universe.md                  ← Approved ticker/ETF/bond universe
│   ├── macro-indicator-ranges.md          ← Historical ranges for scoring/sanity check
│   ├── portfolio-construction-rules.md    ← Diversification constraints, concentration limits
│   └── output-templates/
│       ├── dashboard-template.md
│       ├── memo-template.md
│       └── color-system.md
│
├── output/                                ← .gitignore target, runtime artifacts
│   ├── staleness-routing.json
│   ├── user-profile.json
│   ├── validated-data.json
│   ├── environment-assessment.json
│   ├── portfolio-recommendation.json
│   ├── quality-report.json
│   ├── critic-report.json
│   ├── data/
│   │   ├── macro/          (macro-raw.json, latest.json)
│   │   ├── political/      (political-raw.json, latest.json)
│   │   ├── fundamentals/   (fundamentals-raw.json, latest.json)
│   │   ├── sentiment/      (sentiment-raw.json, latest.json)
│   │   └── recommendations/ ({date}_recommendation.json)
│   ├── reports/            (portfolio_{lang}_{date}.html, .docx)
│   └── logs/               (error logs, skip records)
│
└── .claude/
    ├── settings.json
    ├── skills/
    │   ├── staleness-checker/
    │   │   ├── SKILL.md
    │   │   └── scripts/staleness-checker.py
    │   ├── query-interpreter/
    │   │   └── SKILL.md
    │   ├── macro-collector/
    │   │   └── SKILL.md
    │   ├── political-collector/
    │   │   └── SKILL.md
    │   ├── fundamentals-collector/
    │   │   └── SKILL.md
    │   ├── sentiment-collector/
    │   │   └── SKILL.md
    │   ├── data-validator/
    │   │   ├── SKILL.md
    │   │   └── scripts/data-validator.py
    │   ├── environment-scorer/
    │   │   ├── SKILL.md
    │   │   └── scripts/environment-scorer.py
    │   ├── portfolio-dashboard-generator/
    │   │   ├── SKILL.md
    │   │   └── references/
    │   ├── memo-generator/
    │   │   ├── SKILL.md
    │   │   └── scripts/docx-generator.py
    │   ├── quality-gate/
    │   │   ├── SKILL.md
    │   │   └── scripts/quality-gate.py
    │   └── data-manager/
    │       ├── SKILL.md
    │       └── scripts/recommendation-archiver.py
    └── agents/
        ├── environment-researcher/
        │   └── AGENT.md
        ├── portfolio-analyst/
        │   ├── AGENT.md
        │   └── scripts/
        │       ├── allocation-calculator.py
        │       └── return-estimator.py
        └── critic/
            └── AGENT.md
```

---

## 10. Failure Handling

| Step | Failure Type | Retry | Fallback |
|------|-------------|-------|---------|
| Step 0 (Staleness) | Script error | — | Fall back to FULL for all dimensions |
| Step 1 (Query) | Required field missing | — | Follow-up question to user |
| Steps 2–5 (Collectors) | Web search failure | 1× (alternate query) | Grade D treatment |
| Steps 2–5 (Collectors) | 3+ consecutive failures | — | Assume network issue, proceed with collected data |
| Step 6 (Validation) | Script error | — | Assign blanket Grade C to raw data, proceed |
| Step 7 (Scoring) | Script error | — | LLM scores directly using reference file |
| Step 8 (Portfolio) | Allocation sum ≠ 100% | 1× (re-run script) | — |
| Step 9 (Quality Gate) | Check FAIL | — | Patch request to portfolio-analyst |
| Step 10 (Critic) | Timeout (2 min) | — | Skip, attach `[No critic review]` flag |
| Step 10 (Critic) | FAIL verdict | portfolio-analyst patch → re-review (1×) | Remaining issues passed with `[Quality flag]` |
| Step 11 (Output) | HTML generation failure | 1× | — |
| Step 11 (Output) | DOCX generation failure | — | Deliver HTML only, output memo text in chat |
| Step 12 (Persistence) | Archival failure | — | Skip + log (non-blocking) |
| Full pipeline | 15-minute timeout | — | Deliver partial output from collected data |

**Core rule**: No sleep polling. Agent return value is the completion signal. Always deliver something.

---

## 11. Technical Decisions

### LLM vs Script Separation Principle
- **Decision**: Each step has an explicitly designated LLM/Script executor
- **Rationale**: "Same input, always same output?" → Yes = Script, No = LLM
- **Trade-off**: Increased script count (8) — but reduced token waste + improved reproducibility

### Quality Gate / Critic Separation
- **Decision**: Deterministic validation in script (quality-gate.py), qualitative judgment in LLM (critic agent)
- **Alternatives**: Both as LLM (v1 approach) → ownership overlap, ambiguous judgment criteria
- **Trade-off**: Critic's scope shrinks, but judgment quality on remaining 3 items improves

### Sequential Execution (Phase 1)
- **Decision**: environment-researcher's 4 collectors run sequentially
- **Alternatives**: Parallel execution (no native mechanism in Claude Code)
- **Trade-off**: Collection time ~4× longer (assuming 1–2 min per collector = 4–8 min) — parallel execution to be explored in Phase 2+

### Critic Isolation (Pragmatic)
- **Decision**: Pass file paths only, exclude intermediate artifacts
- **Alternatives**: Full isolation (not achievable), no isolation (confirmation bias risk)
- **Trade-off**: Not perfect independence, but limiting input scope achieves practical independence

### Data Validation / Environment Scoring Split
- **Decision**: Validation (script) and scoring (LLM + script) as separate steps
- **Alternatives**: Combined in a single data-validator skill (v1 approach)
- **Trade-off**: +1 step — but clearer role separation, clean script/LLM boundary

---

## 12. Future Phases

| Phase | Feature | Additional Components |
|-------|---------|----------------------|
| 1.5 | **Parallel Collection** | Parallel execution mechanism for environment-researcher's 4 collectors |
| 2 | Rebalancing | rebalancing-advisor skill, rebalancing-calculator.py |
| 3 | Tax Optimization | tax-optimizer skill, us-tax-rules.md, kr-tax-rules.md |
| 4 | Performance Tracking | performance-tracker skill, performance-calculator.py |
| 5 | stock-analysis-agent Integration | Cross-invocation for individual stock deep dives |

---

## 13. Reference Files from stock-analysis-agent (Pattern Reference)

Refer to the structure and patterns of the following files during implementation:

| Reference Target | Path | Usage |
|-----------------|------|-------|
| Master orchestrator structure | `stock-analysis-agent/CLAUDE.md` | CLAUDE.md section structure, failure handling, stall detection patterns |
| Agent pattern | `stock-analysis-agent/.claude/agents/analyst/AGENT.md` | portfolio-analyst structure |
| Web collection pattern | `stock-analysis-agent/.claude/skills/web-researcher/SKILL.md` | Common pattern for 4 collectors |
| Data validation pattern | `stock-analysis-agent/.claude/skills/data-validator/SKILL.md` | 3-layer validation, confidence grading |
| Dashboard generation pattern | `stock-analysis-agent/.claude/skills/dashboard-generator/SKILL.md` | TailwindCSS + Chart.js HTML generation |

---

## Verification Plan

| # | Scenario | Expected Result |
|---|---------|----------------|
| 1 | "50M KRW, 1 year, moderate risk tolerance — recommend a portfolio" | 3 options HTML + DOCX, Korean output, all steps completed |
| 2 | "$100K, 3 years, aggressive" | English output, horizon adjustment reflected (equities +5%) |
| 3 | Re-run with different risk tolerance in same session | Staleness REUSE → environment data reused, collection skipped |
| 4 | Collection failure simulation | Grade D "—" display + exclusions recorded |
| 5 | Quality Gate validation | Allocation sum = 100%, source tags ≥ 80%, disclaimer present |
| 6 | Critic validation | 3 qualitative items evaluated, FAIL triggers patch loop (1 iteration) |
| 7 | Network blockage | Partial output delivered within 15 minutes |
| 8 | Option differentiation | Minimum 10pp equity weight difference across 3 options |
