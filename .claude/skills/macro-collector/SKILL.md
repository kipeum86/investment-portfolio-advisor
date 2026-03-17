# Macro Collector — SKILL.md

**Role**: Step 2 — Collect US/KR/global macroeconomic indicators via web research.
**Triggered by**: environment-researcher agent (Step 2, when staleness routing = FULL for macro dimension)
**Reads**: `output/user-profile.json` (market_preference determines collection scope), `output/staleness-routing.json`
**Writes**: `output/data/macro/macro-raw.json`
**References**: `references/macro-indicator-ranges.md` (collection target list and historical ranges)
**Used by**: environment-researcher agent

---

## Instructions

### Step 2.0 — Staleness Routing Check

Before collecting, read `output/staleness-routing.json`:
- If `dimensions.macro.routing` = `"REUSE"` → **SKIP** this entire skill. Use existing `output/data/macro/latest.json` as-is.
- If `dimensions.macro.routing` = `"FULL"` → proceed with full collection below.

### Step 2.1 — Collection Targets

Collect the following macroeconomic indicators via web search:

| Category | Indicators |
|----------|-----------|
| **US** | GDP growth rate (QoQ annualized), CPI (YoY), PCE (YoY), Federal funds rate, Unemployment rate, Yield curve (2y-10y spread), FOMC outlook |
| **KR** | GDP growth rate, CPI (YoY), BOK base rate, KRW/USD exchange rate |
| **Global** | ECB rate, BOJ rate, Global trade environment |

**Minimum requirement**: 5 core indicators must be collected — GDP (US), CPI (US), Federal funds rate, Unemployment rate (US), Yield curve (2y-10y).

If `user-profile.json` `market_preference` = `"us"`, KR indicators are still collected but at lower priority. If `"kr"`, US indicators are still collected but at lower priority.

### Step 2.2 — Web Search Execution

**Search Tool Priority**:
1. `mcp__tavily__search` (preferred — real-time, structured)
2. `mcp__brave__search` (fallback)
3. `WebSearch` tool (Claude built-in, last resort)
4. `WebFetch` for direct URL access

**Web Search Query Templates**:

| # | Query | Target Data |
|---|-------|-------------|
| 1 | `US GDP growth rate latest quarterly 2026` | US GDP |
| 2 | `US CPI inflation rate latest month 2026` | US CPI |
| 3 | `US PCE price index latest 2026` | US PCE |
| 4 | `Federal funds rate current FOMC decision 2026` | Fed funds rate |
| 5 | `US unemployment rate latest BLS 2026` | Unemployment |
| 6 | `US Treasury yield curve 2 year 10 year spread current` | Yield curve |
| 7 | `FOMC meeting outlook rate decision 2026` | FOMC outlook |
| 8 | `South Korea GDP growth rate BOK latest 2026` | KR GDP |
| 9 | `South Korea CPI inflation rate latest 2026` | KR CPI |
| 10 | `Bank of Korea base rate latest decision 2026` | BOK rate |
| 11 | `KRW USD exchange rate current` | Exchange rate |
| 12 | `ECB interest rate latest decision 2026` | ECB rate |
| 13 | `Bank of Japan interest rate latest 2026` | BOJ rate |
| 14 | `global trade tariffs economic outlook 2026` | Trade environment |

For each search:
- Use the exact query template (adjust year if needed)
- Collect top 3-5 results
- Extract: value, unit, period, source URL, date

### Step 2.3 — Source Tagging Rules

Apply source tags based on provenance:

| Tag | Source Examples |
|-----|---------------|
| `[Official]` | BLS, BEA, Federal Reserve, BOK, KOSIS — government statistical agencies |
| `[Portal]` | Trading Economics, Yahoo Finance, FRED, MarketWatch |
| `[KR-Portal]` | Naver Finance, FnGuide, KRX |
| `[News]` | Reuters, Bloomberg, CNBC, WSJ — for qualitative outlook |
| `[Calc]` | Self-calculated (e.g., yield curve spread from individual yields) |
| `[Est]` | Analyst/model projections |

**Priority**: Always prefer `[Official]` sources. Use `[Portal]` when official source is not directly accessible. Tag every data point — no untagged values.

### Step 2.4 — Data Extraction & Formatting

For each indicator collected, record:
- `id`: snake_case identifier (e.g., `us_gdp_growth`, `kr_cpi`, `fed_funds_rate`)
- `category`: `"us"`, `"kr"`, or `"global"`
- `name`: Human-readable name with unit context
- `value`: Numeric value (or null if Grade D)
- `unit`: `"%"`, `"ratio"`, `"index"`, `"KRW/USD"`, etc.
- `period`: Data period (e.g., `"Q4 2025"`, `"Feb 2026"`, `"current"`)
- `source_tag`: One of the tags above
- `source_url`: Full URL of the source
- `retrieved_at`: ISO 8601 timestamp of retrieval

### Step 2.5 — Write macro-raw.json

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
      "source_url": "https://www.bea.gov/...",
      "retrieved_at": "2026-03-17T10:05:00Z"
    },
    {
      "id": "us_cpi",
      "category": "us",
      "name": "US CPI (YoY)",
      "value": 3.1,
      "unit": "%",
      "period": "Feb 2026",
      "source_tag": "[Official]",
      "source_url": "https://www.bls.gov/...",
      "retrieved_at": "2026-03-17T10:05:30Z"
    }
  ],
  "collection_gaps": []
}
```

The `collection_gaps` array lists any target indicators that could not be collected, with reasons.

---

## Success Criteria

- [ ] Minimum 5 core indicators collected (GDP, CPI, federal funds rate, unemployment, yield curve)
- [ ] All indicators have valid `source_tag` and `source_url`
- [ ] `output/data/macro/macro-raw.json` written and is valid JSON
- [ ] All collected values have appropriate `period` fields (not stale/undated)
- [ ] `collection_gaps` accurately records any missing indicators

---

## Failure Handling

- **Individual search failure**: Retry once with an alternate query (rephrase or use different source). If still failing, record in `collection_gaps` with reason and apply Grade D treatment (value = null).
- **3+ consecutive search failures**: Assume network issue. Proceed with whatever data has been collected so far. Do NOT stop.
- **Grade D treatment**: Set `value` to `null`, add entry to `collection_gaps`: `{"id": "...", "reason": "Search failed after retry", "grade": "D"}`.
- **Core rule**: Always write `macro-raw.json` even if partial. Partial data > no data.
