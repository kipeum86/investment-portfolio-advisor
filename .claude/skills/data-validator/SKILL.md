# Data Validator — SKILL.md

**Role**: Step 6 — Validate 4 raw data files and assign confidence grades. Deterministic validation only — no scoring, no opinion formation.
**Triggered by**: Main agent (CLAUDE.md) after all 4 collectors complete (environment-researcher returns).
**Reads**: `output/data/macro/macro-raw.json`, `output/data/political/political-raw.json`, `output/data/fundamentals/fundamentals-raw.json`, `output/data/sentiment/sentiment-raw.json`
**Writes**: `output/validated-data.json`
**References**: `references/macro-indicator-ranges.md` (historical ranges for sanity check)
**Used by**: Main agent (CLAUDE.md)

---

## Instructions

### Step 6.1 — Invoke Data Validator Script

Run the data validator script to perform 3-stage validation on all 4 raw data files:

```bash
python .claude/skills/data-validator/scripts/data_validator.py \
  --output-dir output/ \
  --write
```

The script reads from `output/data/{dimension}/{dimension}-raw.json` for each dimension.

### Step 6.2 — 3-Stage Validation

The script performs validation in 3 stages:

**Stage 1: Arithmetic Consistency**
- Check that numeric values are within plausible ranges (e.g., CPI not 500%, unemployment not -5%)
- Verify unit consistency (percentage values are actually percentages, not decimals)
- Cross-check derived values against their components

**Stage 2: Cross-Reference**
- Compare indicators from multiple sources (if available)
- Flag discrepancies > 5% between independent sources
- Confirm directional consistency between related indicators

**Stage 3: Sanity Check**
- Compare values against historical ranges from `references/macro-indicator-ranges.md`
- Flag extreme outliers (values > 2 standard deviations from historical mean)
- Verify temporal consistency (data periods are recent, not stale)

### Step 6.3 — Grading System

Each data point receives a confidence grade:

| Grade | Criteria |
|-------|---------|
| **A** | Official government statistics + arithmetic consistency confirmed |
| **B** | 2+ independent sources with values within 5% difference |
| **C** | Single source, arithmetic consistency confirmed |
| **D** | Unverifiable → `null` treatment, excluded from downstream analysis |

### Step 6.4 — Verify Output

After the script completes, verify that `output/validated-data.json` exists, contains all 4 dimensions, and all data points have been graded.

**Output Schema**: `validated-data.json`
```json
{
  "validation_timestamp": "2026-03-17T10:25:00Z",
  "overall_data_grade": "B",
  "validated_indicators": {
    "macro": [
      {
        "id": "us_gdp_growth",
        "value": 2.3,
        "grade": "A",
        "source_tag": "[Official]"
      },
      {
        "id": "us_cpi",
        "value": 3.1,
        "grade": "B",
        "source_tag": "[Official]"
      }
    ],
    "political": [
      {
        "id": "us_tariff_policy",
        "headline": "New tariffs announced on semiconductor imports",
        "impact_assessment": "negative",
        "grade": "C",
        "source_tag": "[News]"
      }
    ],
    "fundamentals": [
      {
        "id": "sp500_pe",
        "value": 22.5,
        "grade": "B",
        "source_tag": "[Portal]"
      }
    ],
    "sentiment": [
      {
        "id": "vix",
        "value": 18.5,
        "grade": "A",
        "source_tag": "[Official]"
      }
    ]
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

- `overall_data_grade`: The lowest grade among all non-excluded indicators (conservative)
- `exclusions`: Items graded D — these are excluded from all downstream analysis
- Grade D items have their `value` set to `null` and will display as "—" in outputs

---

## Success Criteria

- [ ] Script executed without error
- [ ] `output/validated-data.json` written successfully
- [ ] All raw data points from all 4 dimensions have been graded (A/B/C/D)
- [ ] Grade D items are properly recorded in `exclusions` array
- [ ] `overall_data_grade` field is set
- [ ] No ungraded data points remain

---

## Failure Handling

- **Script error** (crash, import failure, file read error): Assign blanket Grade C to all raw data. Write `validated-data.json` with all indicators graded C, `overall_data_grade` = `"C"`, and empty `exclusions`. Log the error to `output/logs/`.
- **Missing raw data file**: Skip that dimension in validation. Note in `validated-data.json` that the dimension was absent (empty array for that dimension key).
- **Core rule**: Validation must always produce output. Never block the pipeline because validation failed — degrade gracefully to Grade C.
