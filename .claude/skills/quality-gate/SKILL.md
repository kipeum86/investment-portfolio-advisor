# Quality Gate — SKILL.md

**Role**: Step 9 — Perform 7 deterministic quality checks on the portfolio recommendation. No LLM judgment — script-only validation.
**Triggered by**: Main agent (CLAUDE.md) after Step 8 (Portfolio Construction by portfolio-analyst agent) completes.
**Reads**: `output/portfolio-recommendation.json`, `output/user-profile.json`
**Writes**: `output/quality-report.json`
**References**: None
**Used by**: Main agent (CLAUDE.md)

---

## Instructions

### Step 9.1 — Invoke Quality Gate Script

Run the quality gate script to perform all 7 deterministic checks:

```bash
python .claude/skills/quality-gate/scripts/quality_gate.py \
  --recommendation output/portfolio-recommendation.json \
  --user-profile output/user-profile.json \
  --write \
  --output-dir output/
```

### Step 9.2 — 7 Quality Checks

The script performs these 7 deterministic checks (no LLM judgment involved):

| # | Check Item | Method | PASS Criteria |
|---|-----------|--------|--------------|
| 1 | **Allocation Sum** | Check `allocation.total` for each of 3 options | Each exactly 100 |
| 2 | **Source Tag Coverage** | Count `source_tag` presence ratio in holdings | >= 80% of holdings have source_tag |
| 3 | **Required Fields Present** | Schema comparison against expected fields | All required fields present in each option |
| 4 | **Disclaimer Present** | Check `disclaimer` field exists | Non-empty string |
| 5 | **Grade D Exclusion Compliance** | Cross-reference excluded items (from validated-data.json) with holdings | 0 violations — no Grade D items in holdings |
| 6 | **User Profile Reflected** | Verify budget/period/risk_tolerance values from user-profile match output | Values match between input and output |
| 7 | **Option Differentiation (numeric)** | Compare equity weight (us_equity + kr_equity) across 3 options | Minimum 10 percentage point difference between aggressive and conservative |

### Step 9.3 — Verify Output

After the script completes, read `output/quality-report.json` and check results.

**Output Schema**: `quality-report.json`
```json
{
  "quality_check_timestamp": "2026-03-17T10:45:00Z",
  "overall_result": "PASS",
  "checks": [
    {
      "check_id": 1,
      "name": "Allocation Sum",
      "result": "PASS",
      "details": "aggressive=100, moderate=100, conservative=100"
    },
    {
      "check_id": 2,
      "name": "Source Tag Coverage",
      "result": "PASS",
      "details": "15/16 holdings have source_tag (93.8%)"
    },
    {
      "check_id": 3,
      "name": "Required Fields Present",
      "result": "PASS",
      "details": "All required fields present in all options"
    },
    {
      "check_id": 4,
      "name": "Disclaimer Present",
      "result": "PASS",
      "details": "Disclaimer field contains non-empty string"
    },
    {
      "check_id": 5,
      "name": "Grade D Exclusion Compliance",
      "result": "PASS",
      "details": "0 Grade D items found in holdings"
    },
    {
      "check_id": 6,
      "name": "User Profile Reflected",
      "result": "PASS",
      "details": "budget=50000000, period=12, risk_tolerance=moderate — all reflected"
    },
    {
      "check_id": 7,
      "name": "Option Differentiation",
      "result": "PASS",
      "details": "Equity weight: aggressive=60%, moderate=45%, conservative=30% — 30pp spread"
    }
  ],
  "failed_checks": [],
  "recommendations": []
}
```

- `overall_result`: `"PASS"` if all 7 checks pass, `"FAIL"` if any check fails
- `failed_checks`: Array of check IDs that failed
- `recommendations`: Specific remediation instructions for failed checks

### Step 9.4 — Handle Results

- **All PASS**: Proceed to Step 10 (Critic Review).
- **Any FAIL**: The `quality-report.json` contains specific failure details and remediation instructions. The main agent sends these back to portfolio-analyst for patching, then re-runs quality-gate.

---

## Success Criteria

- [ ] Script executed without error
- [ ] `output/quality-report.json` written successfully
- [ ] All 7 checks executed and reported
- [ ] `overall_result` is either `"PASS"` or `"FAIL"` (no other values)
- [ ] Failed checks (if any) have specific `details` and `recommendations`

---

## Failure Handling

- **Script error** (crash, import failure): Report error to main agent. The main agent may attempt to run checks manually or proceed with `[Quality gate failed]` flag attached to outputs.
- **Missing input file**: If `portfolio-recommendation.json` is missing, cannot run checks — report error. If `user-profile.json` is missing, checks 6 (User Profile Reflected) cannot run — mark as `"SKIP"` and run remaining checks.
- **Core rule**: Quality gate is a checkpoint, not a blocker. If the script fails entirely, the pipeline continues with a quality flag. Individual check failures trigger the patch loop with portfolio-analyst.
