# Political Collector — SKILL.md

**Role**: Step 3 — Collect political and geopolitical risk developments via web research.
**Triggered by**: environment-researcher agent (Step 3, when staleness routing = FULL for political dimension)
**Reads**: `output/user-profile.json` (market_preference determines collection scope), `output/staleness-routing.json`
**Writes**: `output/data/political/political-raw.json`
**References**: None
**Used by**: environment-researcher agent

---

## Instructions

### Step 3.0 — Staleness Routing Check

Before collecting, read `output/staleness-routing.json`:
- If `dimensions.political.routing` = `"REUSE"` → **SKIP** this entire skill. Use existing `output/data/political/latest.json` as-is.
- If `dimensions.political.routing` = `"FULL"` → proceed with full collection below.

### Step 3.1 — Collection Targets

Collect political and geopolitical developments across these categories:

| Category | Targets |
|----------|---------|
| **US** | Trade policy/tariffs, Tech regulation, Fiscal policy, Financial regulation |
| **KR** | Political situation, Corporate regulation, Value-Up program |
| **Geopolitical** | US-China relations, Regional conflicts, Semiconductor supply chain |

**Minimum requirement**: At least 1 development item each for US and Geopolitical categories.

### Step 3.2 — Web Search Execution

**Search Tool Priority**:
1. `mcp__tavily__search` (preferred — real-time, structured)
2. `mcp__brave__search` (fallback)
3. `WebSearch` tool (Claude built-in, last resort)
4. `WebFetch` for direct URL access

**Web Search Query Templates**:

| # | Query | Target Data |
|---|-------|-------------|
| 1 | `US trade policy tariffs latest developments 2026` | Trade policy |
| 2 | `US technology regulation big tech policy 2026` | Tech regulation |
| 3 | `US fiscal policy government spending budget 2026` | Fiscal policy |
| 4 | `US financial regulation banking policy SEC 2026` | Financial regulation |
| 5 | `South Korea political situation government policy 2026` | KR politics |
| 6 | `South Korea corporate governance Value-Up program 2026` | KR corporate regulation |
| 7 | `US China relations trade technology tensions 2026` | US-China |
| 8 | `geopolitical risks conflicts Middle East Asia 2026` | Regional conflicts |
| 9 | `semiconductor supply chain geopolitics CHIPS act 2026` | Semiconductor supply chain |
| 10 | `global trade war tariff impact stock market 2026` | Trade environment |

For each search:
- Collect top 3-5 results
- Extract: headline, summary, impact assessment, affected sectors, source URL

### Step 3.3 — Source Tagging Rules

Apply source tags based on provenance:

| Tag | Source Examples |
|-----|---------------|
| `[Official]` | White House, USTR, government press releases — official policy announcements |
| `[News]` | Reuters, Bloomberg, WSJ, FT, AP — for news reporting and analysis |
| `[Portal]` | Financial portals reporting on political developments |
| `[KR-Portal]` | Korean news sources (Yonhap, Hankyoreh, MBN) for KR political items |

**Priority**: For political developments, `[News]` sources from major wire services and financial press are primary. Use `[Official]` when citing actual policy documents or government statements.

### Step 3.4 — Impact Assessment

For each development, assess market impact:
- `"positive"` — likely positive for equity markets
- `"neutral"` — limited or uncertain market impact
- `"negative"` — likely negative for equity markets

Also identify `affected_sectors` — which market sectors are most impacted by this development (e.g., `["technology", "manufacturing"]` for tariff changes).

### Step 3.5 — Write political-raw.json

**Output Schema**: `political-raw.json`
```json
{
  "collection_timestamp": "2026-03-17T10:10:00Z",
  "developments": [
    {
      "id": "us_tariff_policy",
      "category": "us_trade",
      "headline": "New tariffs announced on semiconductor imports",
      "summary": "The administration announced 25% tariffs on semiconductor imports from select countries, effective Q2 2026...",
      "impact_assessment": "negative",
      "affected_sectors": ["technology", "manufacturing"],
      "source_tag": "[News]",
      "source_url": "https://www.reuters.com/...",
      "retrieved_at": "2026-03-17T10:10:00Z"
    },
    {
      "id": "kr_value_up",
      "category": "kr_corporate",
      "headline": "Korea Value-Up program phase 2 announced",
      "summary": "FSC announced expanded Value-Up program incentives for listed companies...",
      "impact_assessment": "positive",
      "affected_sectors": ["financials", "conglomerates"],
      "source_tag": "[KR-Portal]",
      "source_url": "https://...",
      "retrieved_at": "2026-03-17T10:11:00Z"
    }
  ],
  "collection_gaps": []
}
```

The `collection_gaps` array lists any target categories that could not be assessed.

---

## Success Criteria

- [ ] At least 1 development item for US category
- [ ] At least 1 development item for Geopolitical category
- [ ] All developments have valid `source_tag` and `source_url`
- [ ] All developments have `impact_assessment` (positive/neutral/negative)
- [ ] `output/data/political/political-raw.json` written and is valid JSON
- [ ] `collection_gaps` accurately records any uncovered categories

---

## Failure Handling

- **Individual search failure**: Retry once with an alternate query (rephrase or use different news source). If still failing, record in `collection_gaps` with reason and apply Grade D treatment.
- **3+ consecutive search failures**: Assume network issue. Proceed with whatever data has been collected so far. Do NOT stop.
- **Grade D treatment**: Add entry to `collection_gaps`: `{"category": "...", "reason": "Search failed after retry", "grade": "D"}`.
- **Core rule**: Always write `political-raw.json` even if partial. Partial data > no data.
