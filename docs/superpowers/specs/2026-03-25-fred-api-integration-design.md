# FRED API Integration Design

**Date**: 2026-03-25
**Status**: Approved
**Scope**: macro-collector + fundamentals-collector

---

## Problem

The macro-collector and fundamentals-collector currently rely on web search (Tavily/Brave/WebSearch) to gather US macroeconomic data. This approach is fragile (search failures), slow (14+ queries × seconds each), and yields lower-confidence data (mostly `[Portal]` tagged → Grade B/C).

## Solution

Integrate the FRED (Federal Reserve Economic Data) API as the primary data source for US macroeconomic indicators and credit spreads. Web search becomes the fallback for FRED failures and remains the primary source for KR/Global indicators.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| API call method | Python script (hybrid) | Matches project pattern (`data_validator.py`, `staleness_checker.py`). Reliable error handling. |
| Fallback strategy | FRED first → web search fallback | Maximizes collection success rate. Aligns with existing retry/fallback pattern. |
| Scope | macro + fundamentals (credit spreads) | FRED covers US macro indicators + ICE BofA credit spreads. KR/Global stay on web search. |
| Script location | `.claude/scripts/fred_client.py` (shared scripts dir) | New shared directory for cross-skill utilities. Avoids duplicate FRED logic. |
| Source tag reclassification | FRED API data tagged `[Official]` | FRED is operated by the Federal Reserve Bank of St. Louis and serves official government data via API. Web-scraped FRED URLs remain `[Portal]` per existing SKILL.md. |
| HTTP library | `requests` (not `fredapi`) | Lighter dependency, sufficient for our use case (fetch latest observation per series). |

---

## 1. `.claude/scripts/fred_client.py`

### Interface

```bash
# Macro indicators
python .claude/scripts/fred_client.py \
  --indicators us_gdp_growth,us_cpi,us_pce,us_fed_rate,us_unemployment,us_10y_yield,us_2y_yield,us_yield_spread \
  --output output/data/macro/fred-data.json \
  --write

# Fundamentals indicators
python .claude/scripts/fred_client.py \
  --indicators us_ig_spread,us_hy_spread \
  --output output/data/fundamentals/fred-data.json \
  --write

# With explicit API key
python .claude/scripts/fred_client.py \
  --indicators us_gdp_growth --api-key <key> --output output.json --write
```

- Without `--write`: prints JSON to stdout
- With `--write`: writes to `--output` path and prints confirmation
- Exit code 0: at least 1 indicator succeeded
- Exit code 1: total failure (bad API key, network down, all series failed)

### API Key

```
Priority:
1. --api-key CLI argument (explicit override)
2. Environment variable FRED_API_KEY
```

No `.env` file. User adds `export FRED_API_KEY=<key>` to shell profile.

### FRED Series Mapping

```python
SERIES_MAP = {
    # Macro indicators
    "us_gdp_growth": {
        "series_id": "A191RL1Q225SBEA",
        "name": "US GDP Growth Rate (QoQ annualized)",
        "category": "us",
        "unit": "%",
        "transform": None,              # Value is already QoQ annualized %
        "api_units": None,               # Use default FRED units
    },
    "us_cpi": {
        "series_id": "CPIAUCSL",
        "name": "US CPI (YoY)",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": "pc1",              # Percent change from year ago
    },
    "us_pce": {
        "series_id": "PCEPI",
        "name": "US PCE Price Index (YoY)",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": "pc1",
    },
    "us_fed_rate": {
        "series_id": "DFF",
        "name": "Effective Federal Funds Rate",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": None,
    },
    "us_unemployment": {
        "series_id": "UNRATE",
        "name": "US Unemployment Rate",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": None,
    },
    "us_10y_yield": {
        "series_id": "DGS10",
        "name": "10-Year Treasury Yield",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": None,
    },
    "us_2y_yield": {
        "series_id": "DGS2",
        "name": "2-Year Treasury Yield",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": None,
    },
    "us_yield_spread": {
        "series_id": "T10Y2Y",
        "name": "2Y-10Y Treasury Spread",
        "category": "us",
        "unit": "bps",
        "transform": "multiply_100",    # FRED returns percentage points, convert to bps
        "api_units": None,
    },
    # Fundamentals indicators
    "us_ig_spread": {
        "series_id": "BAMLC0A0CM",
        "name": "ICE BofA US Corporate IG OAS",
        "market": "us",
        "unit": "bps",
        "transform": "multiply_100",    # FRED returns percentage points, convert to bps
        "api_units": None,
    },
    "us_hy_spread": {
        "series_id": "BAMLH0A0HYM2",
        "name": "ICE BofA US High Yield OAS",
        "market": "us",
        "unit": "bps",
        "transform": "multiply_100",
        "api_units": None,
    },
}
```

### Output Format

Same structure as `macro-raw.json` indicators:

```json
{
  "source": "FRED_API",
  "fetched_at": "2026-03-25T10:00:00Z",
  "indicators": [
    {
      "id": "us_gdp_growth",
      "category": "us",
      "name": "US GDP Growth Rate (QoQ annualized)",
      "value": 2.3,
      "unit": "%",
      "period": "Q4 2025",
      "source_tag": "[Official]",
      "source_url": "https://fred.stlouisfed.org/series/A191RL1Q225SBEA",
      "retrieved_at": "2026-03-25T10:00:00Z"
    }
  ],
  "errors": [
    {
      "id": "us_pce",
      "series_id": "PCEPI",
      "error": "HTTP 429 rate limited",
      "timestamp": "2026-03-25T10:00:01Z"
    }
  ]
}
```

Note: Macro indicators include `category` field (`"us"`). Fundamentals indicators include `market` field (`"us"`) instead, matching the respective raw JSON schemas.

### Error Handling

| Scenario | Behavior |
|----------|----------|
| Invalid API key | Exit code 1, stderr message, no output file |
| Individual series failure | Record in `errors`, continue with remaining series |
| Network timeout | 10s per request, failure → `errors` |
| Empty response (no observations) | Record in `errors` with "No observations available" |
| Rate limiting (429) | 1 retry with 1s backoff, then record in `errors` |

### Period Detection

The script extracts the observation date from FRED response and formats it:
- Quarterly data (GDP): `"Q4 2025"` format
- Monthly data (CPI, unemployment): `"Feb 2026"` format
- Daily data (yields, rates): `"2026-03-24"` or `"current"` format

---

## 2. SKILL.md Modifications

### macro-collector/SKILL.md

**Step 2.2 splits into 2.2a + 2.2b:**

**Step 2.2a — FRED API Collection (US indicators)**

```
Run: python .claude/scripts/fred_client.py \
       --indicators us_gdp_growth,us_cpi,us_pce,us_fed_rate,us_unemployment,us_10y_yield,us_2y_yield,us_yield_spread \
       --output output/data/macro/fred-data.json --write

Read fred-data.json:
  - Successfully fetched indicators → include in macro-raw.json with source_tag [Official]
  - Failed indicators (in errors[]) → collect via web search in Step 2.2b
  - If script exits with code 1 → skip entirely, all US indicators go to Step 2.2b
```

**Step 2.2b — Web Search Collection (KR + Global + FRED failures)**

Existing web search logic unchanged. Additional queries only for indicators that FRED failed to collect.

**Search Tool Priority updated to:**
1. `fred_client.py` (US indicators — highest priority)
2. `mcp__tavily__search` (KR/Global + fallback)
3. `mcp__brave__search`
4. `WebSearch`
5. `WebFetch`

### fundamentals-collector/SKILL.md

**Step 4.2 splits into 4.2a + 4.2b:**

**Step 4.2a — FRED API Collection (credit spreads)**

```
Run: python .claude/scripts/fred_client.py \
       --indicators us_ig_spread,us_hy_spread \
       --output output/data/fundamentals/fred-data.json --write

Read fred-data.json:
  - Success → include in fundamentals-raw.json market_metrics with source_tag [Official]
  - Failure → collect via web search in Step 4.2b
```

**Step 4.2b — Web Search Collection (valuations + sectors + FRED failures)**

Existing web search logic unchanged.

---

## 3. File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `.claude/scripts/fred_client.py` | CREATE | FRED API client, shared by both collectors |
| `.claude/skills/macro-collector/SKILL.md` | MODIFY | Add Step 2.2a (FRED), update search priority, move FRED from `[Portal]` to `[Official]` in source tag table |
| `.claude/skills/fundamentals-collector/SKILL.md` | MODIFY | Add Step 4.2a (FRED), update search priority |
| `CLAUDE.md` Section 10 | MODIFY | Add `.claude/scripts/` to file path tree |
| `requirements.txt` | MODIFY | Add `requests>=2.31.0` |

### Files NOT modified

- `data_validator.py` — `[Official]` tag → Grade A already works
- `environment_scorer.py` — input format identical
- `environment-researcher/AGENT.md` — calls skills, no change needed
- `references/macro-indicator-ranges.md` — ranges unchanged
- All downstream pipeline files — no schema changes

---

## 4. Data Quality Impact

| Indicator | Before | After |
|-----------|--------|-------|
| US GDP, CPI, PCE, rates, unemployment, yields | `[Portal]` Grade B/C | `[Official]` Grade A |
| US yield spread | `[Calc]` Grade C | `[Official]` Grade A |
| IG/HY credit spreads | `[Portal]` Grade C | `[Official]` Grade A |
| KR indicators | `[KR-Portal]` Grade C | No change |
| Global indicators | `[Portal]`/`[News]` Grade C | No change |

Expected overall data grade improvement: C/B → B/A for typical runs.

---

## 5. Notes

### Source Tag Reclassification

FRED is currently listed under `[Portal]` in `macro-collector/SKILL.md` (line 73). With this integration:
- **FRED API** data (via `fred_client.py`) → tagged `[Official]`. Rationale: direct API access to Federal Reserve Bank data is equivalent to official government statistics.
- **FRED website** data (via web search hitting `fred.stlouisfed.org`) → remains `[Portal]`. Web-scraped data goes through a portal regardless of the underlying authority.

This distinction is intentional: the collection method determines the tag, not just the data origin.

### Arithmetic Consistency with Mixed Sources

When FRED provides `us_yield_spread` (T10Y2Y) but individual yields (`us_10y_yield`, `us_2y_yield`) come from web search (or vice versa), the `data_validator.py` arithmetic check may flag a timing mismatch. The existing 20 bps tolerance is sufficient to absorb typical intraday differences. No code change needed.

### Intermediate File Lifecycle

`fred-data.json` files (`output/data/macro/fred-data.json`, `output/data/fundamentals/fred-data.json`) are intermediate artifacts. They are retained for debugging but are not checked by `staleness_checker.py` (which only checks `latest.json`). Already covered by `output/` in `.gitignore`.
