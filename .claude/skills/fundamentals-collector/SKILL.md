# Fundamentals Collector — SKILL.md

**Role**: Step 4 — Collect market-level fundamental indicators via web research.
**Triggered by**: environment-researcher agent (Step 4, when staleness routing = FULL for fundamentals dimension)
**Reads**: `output/user-profile.json` (market_preference determines collection scope), `output/staleness-routing.json`
**Writes**: `output/data/fundamentals/fundamentals-raw.json`
**References**: None
**Used by**: environment-researcher agent

---

## Instructions

### Step 4.0 — Staleness Routing Check

Before collecting, read `output/staleness-routing.json`:
- If `dimensions.fundamentals.routing` = `"REUSE"` → **SKIP** this entire skill. Use existing `output/data/fundamentals/latest.json` as-is.
- If `dimensions.fundamentals.routing` = `"FULL"` → proceed with full collection below.

### Step 4.1 — Collection Targets

Collect the following market-level fundamental indicators via web search:

| Category | Indicators |
|----------|-----------|
| **US Market Valuations** | S&P 500 P/E (trailing), Shiller CAPE |
| **KR Market Valuations** | KOSPI PER, KOSPI PBR |
| **Sector Performance** | Sector rotation signals, Sector ETF performance YTD (XLK, XLF, XLE, XLV, etc.) |
| **Earnings** | S&P 500 earnings growth estimates (forward) |
| **Credit** | Corporate credit spreads (investment grade vs high yield) |

**Minimum requirement**: S&P 500 P/E + KOSPI PER must be collected at minimum.

### Step 4.2a — FRED API Collection (credit spreads)

Run the FRED client script to collect US credit spread indicators:

```bash
python .claude/scripts/fred_client.py \
  --indicators us_ig_spread,us_hy_spread \
  --output output/data/fundamentals/fred-data.json --write
```

Read the output `fred-data.json`:
- **Exit code 0**: Read `fred-data.json`. Successfully fetched indicators go directly into `fundamentals-raw.json` `market_metrics[]` (they already have correct `source_tag`, `market`, `name`, etc.). Any indicator IDs listed in `errors[]` must be collected via web search in Step 4.2b.
- **Exit code 1**: Script failed entirely. Skip FRED, collect credit spreads via web search in Step 4.2b.

### Step 4.2b — Web Search Collection (valuations + sectors + FRED failures)

Collect via web search:
- **Always**: S&P 500 P/E, Shiller CAPE, KOSPI PER/PBR, sector performance, earnings estimates
- **Only if FRED failed**: Credit spreads (us_ig_spread, us_hy_spread) if listed in `fred-data.json` `errors[]` or if Step 4.2a exited with code 1

**Search Tool Priority**:
1. `fred_client.py` (credit spreads — via Step 4.2a, highest priority)
2. `mcp__tavily__search` (preferred — real-time, structured)
3. `mcp__brave__search` (fallback)
4. `WebSearch` tool (Claude built-in, last resort)
5. `WebFetch` for direct URL access

**Web Search Query Templates**:

| # | Query | Target Data | When |
|---|-------|-------------|------|
| 1 | `S&P 500 P/E ratio trailing current 2026` | S&P 500 P/E | Always |
| 2 | `Shiller CAPE ratio S&P 500 current` | Shiller CAPE | Always |
| 3 | `KOSPI PER PBR current valuation 2026` | KOSPI valuations | Always |
| 4 | `S&P 500 sector ETF performance YTD 2026` | Sector performance | Always |
| 5 | `XLK XLF XLE XLV XLI sector ETF returns YTD 2026` | Individual sector ETFs | Always |
| 6 | `S&P 500 earnings growth estimate forward 2026` | Earnings estimates | Always |
| 7 | `US corporate credit spread investment grade high yield 2026` | Credit spreads | FRED fallback only |
| 8 | `sector rotation signals US stock market 2026` | Rotation signals | Always |
| 9 | `KOSPI sector performance top sectors 2026` | KR sector data | Always |

For each search:
- Collect top 3-5 results
- Extract: metric name, value, unit, period, source URL

### Step 4.3 — Source Tagging Rules

Apply source tags based on provenance:

| Tag | Source Examples |
|-----|---------------|
| `[Official]` | SEC filings, exchange data — rare for fundamentals collection |
| `[Portal]` | Yahoo Finance, Multpl.com, Macrotrends, FactSet, S&P Global, Yardeni Research |
| `[KR-Portal]` | Naver Finance, FnGuide, KRX market data |
| `[Calc]` | Self-calculated ratios or spreads from verified components |
| `[Est]` | Analyst consensus estimates, forward projections |
| `[News]` | Financial press reporting on earnings or market metrics |

**Priority**: `[Portal]` sources are primary for market metrics. Use `[KR-Portal]` for KOSPI data. `[Est]` tag for any forward-looking estimates.

### Step 4.4 — Data Extraction & Formatting

**Market Metrics**: Record each with:
- `id`: snake_case identifier (e.g., `sp500_pe`, `shiller_cape`, `kospi_per`)
- `market`: `"us"` or `"kr"`
- `name`: Human-readable name
- `value`: Numeric value
- `unit`: `"ratio"`, `"%"`, `"bps"`, etc.
- `period`: `"current"`, `"Q4 2025"`, `"YTD"`, etc.
- `source_tag`, `source_url`, `retrieved_at`

**Sector Performance**: Record each with:
- `sector`: sector name (e.g., `"technology"`, `"financials"`)
- `etf_ticker`: representative ETF ticker (e.g., `"XLK"`, `"XLF"`)
- `ytd_return`: YTD return percentage
- `source_tag`, `source_url`

### Step 4.5 — Write fundamentals-raw.json

**Output Schema**: `fundamentals-raw.json`
```json
{
  "collection_timestamp": "2026-03-17T10:15:00Z",
  "market_metrics": [
    {
      "id": "sp500_pe",
      "market": "us",
      "name": "S&P 500 Trailing P/E",
      "value": 22.5,
      "unit": "ratio",
      "period": "current",
      "source_tag": "[Portal]",
      "source_url": "https://www.multpl.com/s-p-500-pe-ratio",
      "retrieved_at": "2026-03-17T10:15:00Z"
    },
    {
      "id": "kospi_per",
      "market": "kr",
      "name": "KOSPI PER",
      "value": 12.8,
      "unit": "ratio",
      "period": "current",
      "source_tag": "[KR-Portal]",
      "source_url": "https://finance.naver.com/...",
      "retrieved_at": "2026-03-17T10:16:00Z"
    }
  ],
  "sector_performance": [
    {
      "sector": "technology",
      "etf_ticker": "XLK",
      "ytd_return": 12.3,
      "source_tag": "[Portal]",
      "source_url": "https://finance.yahoo.com/quote/XLK/"
    },
    {
      "sector": "financials",
      "etf_ticker": "XLF",
      "ytd_return": 8.1,
      "source_tag": "[Portal]",
      "source_url": "https://finance.yahoo.com/quote/XLF/"
    }
  ],
  "collection_gaps": []
}
```

The `collection_gaps` array lists any target indicators that could not be collected.

---

## Success Criteria

- [ ] S&P 500 P/E collected
- [ ] KOSPI PER collected
- [ ] All metrics have valid `source_tag` and `source_url`
- [ ] Sector performance data includes at least 3 sectors
- [ ] `output/data/fundamentals/fundamentals-raw.json` written and is valid JSON
- [ ] `collection_gaps` accurately records any missing indicators

---

## Failure Handling

- **Individual search failure**: Retry once with an alternate query (rephrase or use different portal). If still failing, record in `collection_gaps` with reason and apply Grade D treatment (value = null).
- **3+ consecutive search failures**: Assume network issue. Proceed with whatever data has been collected so far. Do NOT stop.
- **Grade D treatment**: Set `value` to `null` in `market_metrics`, add entry to `collection_gaps`: `{"id": "...", "reason": "Search failed after retry", "grade": "D"}`.
- **Core rule**: Always write `fundamentals-raw.json` even if partial. Partial data > no data.
