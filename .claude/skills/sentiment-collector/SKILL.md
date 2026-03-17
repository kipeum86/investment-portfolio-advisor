# Sentiment Collector — SKILL.md

**Role**: Step 5 — Collect market sentiment indicators via web research.
**Triggered by**: environment-researcher agent (Step 5, when staleness routing = FULL for sentiment dimension)
**Reads**: `output/user-profile.json` (market_preference determines collection scope), `output/staleness-routing.json`
**Writes**: `output/data/sentiment/sentiment-raw.json`
**References**: None
**Used by**: environment-researcher agent

---

## Instructions

### Step 5.0 — Staleness Routing Check

Before collecting, read `output/staleness-routing.json`:
- If `dimensions.sentiment.routing` = `"REUSE"` → **SKIP** this entire skill. Use existing `output/data/sentiment/latest.json` as-is.
- If `dimensions.sentiment.routing` = `"FULL"` → proceed with full collection below.

### Step 5.1 — Collection Targets

Collect the following market sentiment indicators via web search:

| Category | Indicators |
|----------|-----------|
| **Volatility** | VIX Index (CBOE Volatility Index) |
| **Composite Sentiment** | CNN Fear & Greed Index |
| **Options** | Put/Call Ratio (CBOE) |
| **Fund Flows** | Fund flows — equity, bond, and money market ETFs |
| **Surveys** | AAII Individual Investor Survey (bullish/bearish/neutral %) |
| **Institutional** | Institutional investor positioning |

**Minimum requirement**: VIX + CNN Fear & Greed Index must be collected at minimum.

### Step 5.2 — Web Search Execution

**Search Tool Priority**:
1. `mcp__tavily__search` (preferred — real-time, structured)
2. `mcp__brave__search` (fallback)
3. `WebSearch` tool (Claude built-in, last resort)
4. `WebFetch` for direct URL access

**Web Search Query Templates**:

| # | Query | Target Data |
|---|-------|-------------|
| 1 | `VIX index current CBOE volatility 2026` | VIX |
| 2 | `CNN Fear and Greed Index current value 2026` | Fear & Greed |
| 3 | `CBOE put call ratio current equity options 2026` | Put/Call Ratio |
| 4 | `ETF fund flows equity bond money market latest 2026` | Fund flows |
| 5 | `AAII investor sentiment survey latest bullish bearish 2026` | AAII Survey |
| 6 | `institutional investor positioning hedge fund allocation 2026` | Institutional positioning |
| 7 | `market sentiment indicators current overview 2026` | General sentiment overview |
| 8 | `stock market breadth advance decline ratio 2026` | Market breadth |

For each search:
- Collect top 3-5 results
- Extract: indicator name, value, interpretation, source URL

### Step 5.3 — Source Tagging Rules

Apply source tags based on provenance:

| Tag | Source Examples |
|-----|---------------|
| `[Official]` | CBOE (for VIX, Put/Call) — exchange-published data |
| `[Portal]` | CNN Money (Fear & Greed), Yahoo Finance, MarketWatch, StockCharts |
| `[KR-Portal]` | Korean market sentiment sources if applicable |
| `[News]` | Financial press reporting on sentiment shifts |
| `[Est]` | Analyst interpretation of positioning data |

**Priority**: `[Official]` for exchange-published data (VIX from CBOE). `[Portal]` for composite indices (Fear & Greed from CNN). Tag every data point.

### Step 5.4 — Interpretation Mapping

For each sentiment indicator, provide an `interpretation` field:

| Indicator | Interpretation Rules |
|-----------|---------------------|
| VIX | < 15 = `"low_fear"`, 15-20 = `"moderate_fear"`, 20-30 = `"elevated_fear"`, > 30 = `"high_fear"` |
| Fear & Greed | 0-25 = `"extreme_fear"`, 25-45 = `"fear"`, 45-55 = `"neutral"`, 55-75 = `"greed"`, 75-100 = `"extreme_greed"` |
| Put/Call Ratio | < 0.7 = `"bullish"`, 0.7-1.0 = `"neutral"`, > 1.0 = `"bearish"` |
| AAII Bullish % | > 40% = `"bullish"`, 25-40% = `"neutral"`, < 25% = `"bearish"` |

### Step 5.5 — Write sentiment-raw.json

**Output Schema**: `sentiment-raw.json`
```json
{
  "collection_timestamp": "2026-03-17T10:20:00Z",
  "indicators": [
    {
      "id": "vix",
      "name": "CBOE Volatility Index (VIX)",
      "value": 18.5,
      "unit": "index",
      "interpretation": "moderate_fear",
      "source_tag": "[Official]",
      "source_url": "https://www.cboe.com/tradable_products/vix/",
      "retrieved_at": "2026-03-17T10:20:00Z"
    },
    {
      "id": "fear_greed",
      "name": "CNN Fear & Greed Index",
      "value": 42,
      "unit": "index",
      "interpretation": "fear",
      "source_tag": "[Portal]",
      "source_url": "https://edition.cnn.com/markets/fear-and-greed",
      "retrieved_at": "2026-03-17T10:20:30Z"
    },
    {
      "id": "put_call_ratio",
      "name": "CBOE Equity Put/Call Ratio",
      "value": 0.85,
      "unit": "ratio",
      "interpretation": "neutral",
      "source_tag": "[Official]",
      "source_url": "https://www.cboe.com/...",
      "retrieved_at": "2026-03-17T10:21:00Z"
    },
    {
      "id": "aaii_survey",
      "name": "AAII Individual Investor Survey — Bullish %",
      "value": 35.2,
      "unit": "%",
      "interpretation": "neutral",
      "source_tag": "[Portal]",
      "source_url": "https://www.aaii.com/...",
      "retrieved_at": "2026-03-17T10:21:30Z"
    }
  ],
  "collection_gaps": []
}
```

The `collection_gaps` array lists any target indicators that could not be collected.

---

## Success Criteria

- [ ] VIX collected
- [ ] CNN Fear & Greed Index collected
- [ ] All indicators have valid `source_tag` and `source_url`
- [ ] All indicators have `interpretation` field
- [ ] `output/data/sentiment/sentiment-raw.json` written and is valid JSON
- [ ] `collection_gaps` accurately records any missing indicators

---

## Failure Handling

- **Individual search failure**: Retry once with an alternate query (rephrase or use different source). If still failing, record in `collection_gaps` with reason and apply Grade D treatment (value = null).
- **3+ consecutive search failures**: Assume network issue. Proceed with whatever data has been collected so far. Do NOT stop.
- **Grade D treatment**: Set `value` to `null`, set `interpretation` to `"unavailable"`, add entry to `collection_gaps`: `{"id": "...", "reason": "Search failed after retry", "grade": "D"}`.
- **Core rule**: Always write `sentiment-raw.json` even if partial. Partial data > no data.
