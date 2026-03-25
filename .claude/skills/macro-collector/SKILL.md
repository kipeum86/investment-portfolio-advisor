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

### Step 2.2a — FRED API Collection (US indicators)

Run the FRED client script to collect US macroeconomic indicators:

```bash
python .claude/scripts/fred_client.py \
  --indicators us_gdp_growth,us_cpi,us_pce,us_fed_rate,us_unemployment,us_10y_yield,us_2y_yield,us_yield_spread \
  --output output/data/macro/fred-data.json --write
```

Read the output `fred-data.json`:
- **Exit code 0**: Read `fred-data.json`. Successfully fetched indicators go directly into `macro-raw.json` (they already have correct `source_tag`, `category`, `name`, etc.). Any indicator IDs listed in `errors[]` must be collected via web search in Step 2.2b.
- **Exit code 1**: Script failed entirely (bad API key, network down). Skip FRED, collect ALL US indicators via web search in Step 2.2b.

### Step 2.2b — Web Search Collection (KR + Global + FRED failures)

Collect the following via web search:
- **Always**: KR indicators (kr_gdp_growth, kr_cpi, kr_base_rate, kr_usd_fx) + Global indicators (ECB rate, BOJ rate, trade environment) + FOMC outlook (qualitative)
- **Only if FRED failed**: Any US indicators listed in `fred-data.json` `errors[]` or all US indicators if Step 2.2a exited with code 1

**Search Tool Priority**:
1. `fred_client.py` (US indicators — via Step 2.2a, highest priority)
2. `mcp__tavily__search` (KR/Global + FRED fallback — real-time, structured)
3. `mcp__brave__search` (fallback)
4. `WebSearch` tool (Claude built-in, last resort)
5. `WebFetch` for direct URL access

**Web Search Query Templates** (for KR, Global, FOMC outlook, and FRED fallback):

| # | Query | Target Data | When |
|---|-------|-------------|------|
| 1 | `US GDP growth rate latest quarterly 2026` | US GDP | FRED fallback only |
| 2 | `US CPI inflation rate latest month 2026` | US CPI | FRED fallback only |
| 3 | `US PCE price index latest 2026` | US PCE | FRED fallback only |
| 4 | `Federal funds rate current FOMC decision 2026` | Fed funds rate | FRED fallback only |
| 5 | `US unemployment rate latest BLS 2026` | Unemployment | FRED fallback only |
| 6 | `US Treasury yield curve 2 year 10 year spread current` | Yield curve | FRED fallback only |
| 7 | `FOMC meeting outlook rate decision 2026` | FOMC outlook | Always (qualitative) |
| 8 | `South Korea GDP growth rate BOK latest 2026` | KR GDP | Always |
| 9 | `South Korea CPI inflation rate latest 2026` | KR CPI | Always |
| 10 | `Bank of Korea base rate latest decision 2026` | BOK rate | Always |
| 11 | `KRW USD exchange rate current` | Exchange rate | Always |
| 12 | `ECB interest rate latest decision 2026` | ECB rate | Always |
| 13 | `Bank of Japan interest rate latest 2026` | BOJ rate | Always |
| 14 | `global trade tariffs economic outlook 2026` | Trade environment | Always |

For each search:
- Use the exact query template (adjust year if needed)
- Collect top 3-5 results
- Extract: value, unit, period, source URL, date

### Step 2.3 — Source Tagging Rules

Apply source tags based on provenance:

| Tag | Source Examples |
|-----|---------------|
| `[Official]` | BLS, BEA, Federal Reserve, BOK, KOSIS, FRED API (via `fred_client.py`) — government statistical agencies |
| `[Portal]` | Trading Economics, Yahoo Finance, MarketWatch |
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
