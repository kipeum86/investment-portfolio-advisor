# Data Manager — SKILL.md

**Role**: Step 12 — Archive the recommendation and update latest.json files for staleness tracking.
**Triggered by**: Main agent (CLAUDE.md) after Step 11 (Output Generation) completes.
**Reads**: `output/portfolio-recommendation.json`, `output/data/macro/macro-raw.json`, `output/data/political/political-raw.json`, `output/data/fundamentals/fundamentals-raw.json`, `output/data/sentiment/sentiment-raw.json`
**Writes**: `output/data/recommendations/{date}_recommendation.json`, `output/data/macro/latest.json`, `output/data/political/latest.json`, `output/data/fundamentals/latest.json`, `output/data/sentiment/latest.json`
**References**: None
**Used by**: Main agent (CLAUDE.md)

---

## Instructions

### Step 12.1 — Invoke Recommendation Archiver Script

Run the recommendation archiver script to snapshot the recommendation and update latest.json files:

```bash
python .claude/skills/data-manager/scripts/recommendation_archiver.py \
  --output-dir output/
```

The script performs two operations:

### Step 12.2 — Recommendation Archival

The script copies `output/portfolio-recommendation.json` to a date-stamped archive:
```
output/data/recommendations/{date}_recommendation.json
```
Where `{date}` is the current date in `YYYY-MM-DD` format (e.g., `2026-03-17_recommendation.json`).

This creates a historical record of all recommendations generated.

### Step 12.3 — Latest.json Updates

For each of the 4 data dimensions, the script copies the current raw data file to `latest.json`:
- `output/data/macro/macro-raw.json` → `output/data/macro/latest.json`
- `output/data/political/political-raw.json` → `output/data/political/latest.json`
- `output/data/fundamentals/fundamentals-raw.json` → `output/data/fundamentals/latest.json`
- `output/data/sentiment/sentiment-raw.json` → `output/data/sentiment/latest.json`

These `latest.json` files are what the staleness-checker reads in Step 0 of the next pipeline run to determine if data can be reused.

### Step 12.4 — Verify Output

After the script completes, verify:
1. Archive file exists at `output/data/recommendations/{date}_recommendation.json`
2. Archive file size > 0 bytes
3. All 4 `latest.json` files have been updated (or created)

---

## Success Criteria

- [ ] Script executed without error
- [ ] Archive file created at `output/data/recommendations/{date}_recommendation.json`
- [ ] Archive file size > 0 bytes
- [ ] All 4 dimension `latest.json` files updated
- [ ] `latest.json` files contain valid JSON matching their corresponding raw files

---

## Failure Handling

- **Script error** (crash, file permission issue): Log the error. This step is **non-blocking** — the recommendation has already been delivered to the user in Step 11. Skip archival and proceed.
- **Partial failure** (archive created but some latest.json not updated): Log warning. The recommendation is preserved; staleness tracking may be inaccurate for the affected dimensions on the next run (they will default to FULL collection, which is the safe default).
- **Missing raw data file**: If a dimension's raw data file doesn't exist (e.g., it was REUSE'd and not re-collected), do NOT overwrite its existing `latest.json`. Only update `latest.json` for dimensions that were freshly collected.
- **Core rule**: This is the final step. Never fail the pipeline here. Log errors, skip what cannot be done, and let the user receive their recommendation.
