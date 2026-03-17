# Environment Scorer — SKILL.md

**Role**: Step 7 — Score each environment dimension on a 1-10 scale, assess direction, and classify the market regime. Hybrid step: script computes positions relative to historical ranges; LLM performs qualitative judgment and final regime classification.
**Triggered by**: Main agent (CLAUDE.md) after Step 6 (Data Validation) completes.
**Reads**: `output/validated-data.json`
**Writes**: `output/environment-assessment.json`
**References**: `references/macro-indicator-ranges.md` (historical ranges for scoring)
**Used by**: Main agent (CLAUDE.md)

---

## Instructions

### Step 7.1 — Invoke Environment Scorer Script

Run the environment scorer script to compute dimension scores based on historical range positioning:

```bash
python .claude/skills/environment-scorer/scripts/environment_scorer.py \
  --validated-data output/validated-data.json \
  --write \
  --output-dir output/
```

The script:
- Reads `output/validated-data.json` for graded indicator values
- Reads `references/macro-indicator-ranges.md` for historical ranges
- Computes each indicator's position within its historical range (percentile-based)
- Aggregates per-dimension scores on a 1-10 scale
- Outputs preliminary scores to `output/environment-assessment.json`

### Step 7.2 — LLM Regime Classification

After the script produces preliminary scores, the LLM performs qualitative judgment:

1. **Review the 6 dimension scores** produced by the script:
   - `macro_us` — US macroeconomic conditions
   - `macro_kr` — KR macroeconomic conditions
   - `political` — Political/geopolitical risk level
   - `fundamentals_us` — US market fundamentals
   - `fundamentals_kr` — KR market fundamentals
   - `sentiment` — Market sentiment conditions

2. **Assess direction** for each dimension:
   - `"positive"` — conditions improving
   - `"neutral-positive"` — stable with slight improvement
   - `"neutral"` — stable, no clear trend
   - `"neutral-negative"` — stable with slight deterioration
   - `"negative"` — conditions deteriorating

3. **Identify key drivers** for each dimension (2-3 most impactful factors).

4. **Classify the market regime** — one of 5 canonical regimes:
   - `"early-expansion"` — recovery accelerating, monetary easing
   - `"mid-cycle"` — steady growth, balanced conditions
   - `"late-cycle"` — growth slowing, tightening conditions, rising valuations
   - `"recession"` — contraction, risk-off, defensive positioning
   - `"recovery"` — bottoming out, early signs of improvement

5. **Write regime rationale** — 2-3 sentences explaining why this regime was chosen, referencing specific indicators.

6. **Self-check**: Verify regime classification is consistent with the dimension scores. If macro scores are high but you classify as recession, re-examine.

### Step 7.3 — Update environment-assessment.json

Merge the LLM's qualitative assessments into the script's output, producing the final `environment-assessment.json`.

**Output Schema**: `environment-assessment.json`
```json
{
  "assessment_timestamp": "2026-03-17T10:30:00Z",
  "data_grade": "B",
  "environment_scores": {
    "macro_us": {
      "score": 6.5,
      "direction": "neutral-positive",
      "grade": "B",
      "key_drivers": ["GDP growth steady at 2.3%", "CPI trending down to 3.1%"]
    },
    "macro_kr": {
      "score": 5.0,
      "direction": "neutral",
      "grade": "B",
      "key_drivers": ["GDP growth modest", "BOK holding rates steady"]
    },
    "political": {
      "score": 4.0,
      "direction": "negative",
      "grade": "C",
      "key_drivers": ["New tariff policy creating uncertainty", "US-China tensions elevated"]
    },
    "fundamentals_us": {
      "score": 7.0,
      "direction": "positive",
      "grade": "B",
      "key_drivers": ["S&P 500 P/E at 22.5 — moderate valuation", "Earnings growth estimates positive"]
    },
    "fundamentals_kr": {
      "score": 5.5,
      "direction": "neutral",
      "grade": "B",
      "key_drivers": ["KOSPI PER at 12.8 — historically low", "Value-Up program tailwind"]
    },
    "sentiment": {
      "score": 6.0,
      "direction": "neutral-positive",
      "grade": "B",
      "key_drivers": ["VIX at moderate 18.5", "Fear & Greed tilting toward fear"]
    }
  },
  "regime_classification": "mid-cycle",
  "regime_rationale": "GDP growth remains positive but moderating. Inflation trending down but above target. Valuations are fair, not stretched. Sentiment is cautious but not fearful. This combination points to mid-cycle conditions with no imminent recession signals.",
  "sanity_alerts": []
}
```

- `data_grade`: Inherited from `validated-data.json` `overall_data_grade`
- `sanity_alerts`: Any inconsistencies the LLM noticed during assessment (e.g., score-regime mismatch)

---

## Success Criteria

- [ ] Script executed without error (or fallback applied)
- [ ] All 6 dimension scores present (macro_us, macro_kr, political, fundamentals_us, fundamentals_kr, sentiment)
- [ ] All scores in 1-10 range
- [ ] All dimensions have direction assessment
- [ ] All dimensions have key_drivers (2-3 items each)
- [ ] Regime classification is one of 5 canonical values
- [ ] Regime rationale is present and references specific indicators
- [ ] `output/environment-assessment.json` written and is valid JSON

---

## Failure Handling

- **Script error** (crash, import failure): LLM scores directly using `references/macro-indicator-ranges.md` as reference. Read `output/validated-data.json` manually and assign scores based on qualitative judgment. Note in `sanity_alerts`: `"environment_scorer.py failed — LLM direct scoring applied"`.
- **Missing validated-data.json**: Cannot proceed. Report error to main agent.
- **Score-regime inconsistency**: If the LLM's regime classification contradicts the numeric scores, re-examine. Record the inconsistency in `sanity_alerts` if unresolved.
- **Core rule**: Always produce `environment-assessment.json`. Script failure degrades quality but does not block the pipeline.
