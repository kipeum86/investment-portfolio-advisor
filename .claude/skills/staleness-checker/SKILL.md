# Staleness Checker — SKILL.md

**Role**: Step 0 — Check existing environment data freshness, determine per-dimension REUSE/FULL routing.
**Triggered by**: Main agent (CLAUDE.md) at pipeline start, before any collection begins.
**Reads**: `output/data/macro/latest.json`, `output/data/political/latest.json`, `output/data/fundamentals/latest.json`, `output/data/sentiment/latest.json` (if they exist)
**Writes**: `output/staleness-routing.json`
**References**: None
**Used by**: Main agent (CLAUDE.md)

---

## Instructions

### Step 0.1 — Invoke Staleness Checker Script

Run the staleness checker script to evaluate data freshness across all 4 dimensions:

```bash
python .claude/skills/staleness-checker/scripts/staleness_checker.py \
  --output-dir output/ \
  --write
```

The script examines `output/data/{dimension}/latest.json` for each dimension and compares timestamps against staleness thresholds.

### Step 0.2 — Staleness Rules

The script applies these thresholds:

| Dimension | Reuse (REUSE) | Full Collection (FULL) |
|-----------|---------------|------------------------|
| Macroeconomic (`macro`) | < 24 hours old | >= 24 hours old |
| Political/Geopolitical (`political`) | < 7 days old | >= 7 days old |
| Fundamentals (`fundamentals`) | < 3 days old | >= 3 days old |
| Sentiment (`sentiment`) | < 12 hours old | >= 12 hours old |

If a dimension's `latest.json` does not exist, it is automatically routed to `FULL`.

### Step 0.3 — Verify Output

After the script completes, verify that `output/staleness-routing.json` exists and contains routing decisions for all 4 dimensions.

**Output Schema**: `staleness-routing.json`
```json
{
  "routing_timestamp": "2026-03-17T10:00:00Z",
  "dimensions": {
    "macro": {
      "routing": "FULL",
      "reason": "No existing data found",
      "last_collected": null
    },
    "political": {
      "routing": "REUSE",
      "reason": "Data is 2 days old (threshold: 7 days)",
      "last_collected": "2026-03-15T10:00:00Z"
    },
    "fundamentals": {
      "routing": "FULL",
      "reason": "Data is 4 days old (threshold: 3 days)",
      "last_collected": "2026-03-13T10:00:00Z"
    },
    "sentiment": {
      "routing": "FULL",
      "reason": "Data is 18 hours old (threshold: 12 hours)",
      "last_collected": "2026-03-16T16:00:00Z"
    }
  }
}
```

---

## Success Criteria

- [ ] Script executed without error
- [ ] `output/staleness-routing.json` written successfully
- [ ] Routing decision exists for all 4 dimensions (macro, political, fundamentals, sentiment)
- [ ] Each routing value is exactly `"REUSE"` or `"FULL"` (no other values)

---

## Failure Handling

- **Script error** (crash, import failure, file permission issue): Fall back to FULL for all dimensions. Write a manual `staleness-routing.json` with all dimensions set to `"FULL"` and reason `"Staleness check script failed — conservative default"`.
- **Partial output** (some dimensions missing): Set missing dimensions to `"FULL"`.
- **Core rule**: When in doubt, always default to `FULL` (conservative). Reusing stale data is worse than re-collecting.
