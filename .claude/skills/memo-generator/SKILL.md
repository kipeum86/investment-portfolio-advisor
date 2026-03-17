# Memo Generator — SKILL.md

**Role**: Step 11 (DOCX) — Generate a DOCX investment memo using python-docx.
**Triggered by**: Main agent (CLAUDE.md) after Step 10 (Critic Review) passes (or passes with flags). Runs alongside portfolio-dashboard-generator.
**Reads**: `output/portfolio-recommendation.json`, `output/environment-assessment.json`, `output/user-profile.json`, `output/critic-report.json`
**Writes**: `output/reports/portfolio_{lang}_{date}.docx`
**References**: `references/output-templates/memo-template.md`
**Used by**: Main agent (CLAUDE.md)

---

## Instructions

### Step 11.1 — Invoke DOCX Generator Script

Run the DOCX generator script:

```bash
python .claude/skills/memo-generator/scripts/docx_generator.py \
  --recommendation output/portfolio-recommendation.json \
  --environment output/environment-assessment.json \
  --profile output/user-profile.json \
  --output output/reports/portfolio_{lang}_{date}.docx
```

Replace `{lang}` with the `output_language` from `user-profile.json` (`"ko"` or `"en"`).
Replace `{date}` with the current date in `YYYY-MM-DD` format.

Example:
```bash
python .claude/skills/memo-generator/scripts/docx_generator.py \
  --recommendation output/portfolio-recommendation.json \
  --environment output/environment-assessment.json \
  --profile output/user-profile.json \
  --output output/reports/portfolio_ko_2026-03-17.docx
```

Ensure the `output/reports/` directory exists before running the script.

### Step 11.2 — DOCX Memo Sections

The script generates a DOCX document with the following sections (structure defined in `references/output-templates/memo-template.md`):

| # | Section | Content |
|---|---------|---------|
| 1 | **Executive Summary** | One-page overview: user profile, regime classification, recommended approach, data confidence |
| 2 | **Environment Analysis** | 4-dimension breakdown: macroeconomic, political, fundamentals, sentiment — scores, directions, key drivers |
| 3 | **Regime Diagnosis** | Current market regime, rationale, historical context |
| 4 | **Portfolio Option 1: Aggressive** | Allocation breakdown, holdings table, rationale per holding, scenario analysis |
| 5 | **Portfolio Option 2: Moderate** | Same structure as Option 1 |
| 6 | **Portfolio Option 3: Conservative** | Same structure as Option 1 |
| 7 | **Risk Analysis** | Key risks with mechanism chains (Risk → Impact → Response), severity, affected options |
| 8 | **Scenario Analysis** | Bull/base/bear comparison across all 3 options — returns, probabilities, assumptions |
| 9 | **Rebalancing Triggers** | Conditions that should prompt rebalancing |
| 10 | **Disclaimer** | "This is not investment advice. For informational purposes only." |

### Step 11.3 — Verify Output

After the script completes:
1. Verify the DOCX file exists at the expected path
2. Verify the file size is > 0 bytes
3. Confirm the output path to the main agent

---

## Success Criteria

- [ ] Script executed without error
- [ ] DOCX file generated at `output/reports/portfolio_{lang}_{date}.docx`
- [ ] File size > 0 bytes
- [ ] All required sections present in the document
- [ ] Content is in the correct language (matching `output_language`)
- [ ] Disclaimer is present

---

## Failure Handling

- **Script error** (python-docx not installed, import failure): Report error. Fallback: deliver HTML dashboard only. Output the memo content as plain text in the chat response so the user still receives the information.
- **Missing input file**: If `critic-report.json` is missing, proceed without quality flag content. If `environment-assessment.json` or `portfolio-recommendation.json` is missing, cannot generate memo — report error.
- **DOCX corruption**: If the file is generated but appears corrupt (size too small, unreadable), retry once. If still failing, fall back to chat text output.
- **Core rule**: DOCX is secondary to HTML. If DOCX fails, the pipeline still succeeds as long as the HTML dashboard is delivered.
