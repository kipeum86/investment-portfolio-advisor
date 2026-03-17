# Query Interpreter — SKILL.md

**Role**: Step 1 — Parse user natural language input into a structured investment profile.
**Triggered by**: Main agent (CLAUDE.md) after Step 0 (Staleness Check) completes.
**Reads**: User's natural language input (from conversation)
**Writes**: `output/user-profile.json`
**References**: None
**Used by**: Main agent (CLAUDE.md)

---

## Instructions

### Step 1.1 — Extract Investment Profile

Parse the user's natural language input and extract the following fields. This is an LLM-only step (no script).

**Required Fields** (must be extracted or asked for):

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `budget` | number | Investment amount in original currency | 50000000 |
| `investment_period_months` | integer | Investment horizon in months | 12 |
| `risk_tolerance` | string | One of: `"aggressive"`, `"moderate"`, `"conservative"` | "moderate" |

**Derived Fields** (computed from required fields):

| Field | Derivation Rule |
|-------|----------------|
| `budget_currency` | Detect from input: KRW if Korean Won/원/만원, USD if dollars/$ |
| `budget_usd_equivalent` | Convert if KRW (use approximate rate); same value if USD |
| `investment_horizon` | < 6 months = `"short"`, 6-36 months = `"medium"`, > 36 months = `"long"` |
| `output_language` | `"ko"` if input is Korean, `"en"` if English |
| `query_timestamp` | Current ISO 8601 timestamp |

**Optional Fields** (extract if mentioned, use defaults otherwise):

| Field | Default | Description |
|-------|---------|-------------|
| `asset_scope` | `"etf_and_stocks"` | `"etf_only"` / `"etf_and_stocks"` / `"broad"` |
| `sector_preferences` | `[]` | Sectors the user wants to emphasize |
| `sector_exclusions` | `[]` | Sectors the user wants to avoid |
| `existing_holdings` | `[]` | Current portfolio positions |
| `market_preference` | `"mixed"` | `"us"` / `"kr"` / `"mixed"` — set only if user explicitly mentions one market |

**Asset Scope Determination**:
- "ETF로만" / "ETF only" / "only ETFs" → `"etf_only"`
- "개별주도 포함" / "include individual stocks" / default → `"etf_and_stocks"`
- "대안자산 포함" / "include alternatives" / "REITs" → `"broad"`

### Step 1.2 — Normalize Values

- **Budget normalization**: Convert Korean shorthand (e.g., "5천만원" = 50,000,000 KRW, "1억" = 100,000,000 KRW)
- **Period normalization**: "1 year" = 12, "6 months" = 6, "3 years" = 36
- **Risk tolerance normalization**: Map synonyms — "공격적" / "high risk" → `"aggressive"`, "중립" / "balanced" → `"moderate"`, "안정적" / "low risk" → `"conservative"`

### Step 1.3 — Write user-profile.json

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

### Step 1.4 — Validate Output

Confirm:
1. All 3 required fields are present and non-null
2. `risk_tolerance` is one of the 3 allowed values
3. `investment_period_months` is a positive integer
4. `budget` is a positive number
5. `asset_scope` is one of: `"etf_only"`, `"etf_and_stocks"`, `"broad"`

---

## Success Criteria

- [ ] All 3 required fields extracted (budget, investment_period_months, risk_tolerance)
- [ ] Values normalized to correct types (number, integer, enum string)
- [ ] `output/user-profile.json` written and valid JSON
- [ ] `investment_horizon` correctly derived from `investment_period_months`
- [ ] `asset_scope` correctly determined (default `"etf_and_stocks"` if not specified)
- [ ] `output_language` set based on user's input language

---

## Failure Handling

- **Required field missing**: Ask the user a follow-up question to obtain the missing field. Do NOT proceed to Step 2 until all 3 required fields are present.
  - Budget missing: "How much would you like to invest?"
  - Period missing: "What is your investment time horizon?"
  - Risk tolerance missing: "What is your risk tolerance? (aggressive / moderate / conservative)"
- **Ambiguous input**: Make reasonable assumptions and state them explicitly to the user. Example: "I'll assume a moderate risk tolerance since you didn't specify — let me know if you'd prefer aggressive or conservative."
- **Invalid values**: Ask for clarification rather than guessing.
