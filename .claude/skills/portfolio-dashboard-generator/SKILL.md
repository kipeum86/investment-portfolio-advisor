# Portfolio Dashboard Generator — SKILL.md

**Role**: Step 11 (HTML) — Generate an interactive HTML dashboard comparing 3 portfolio options, using TailwindCSS CDN + Chart.js.
**Triggered by**: Main agent (CLAUDE.md) after Step 10 (Critic Review) passes (or passes with flags).
**Reads**: `output/portfolio-recommendation.json`, `output/environment-assessment.json`, `output/user-profile.json`, `output/critic-report.json`
**Writes**: `output/reports/portfolio_{lang}_{date}.html`
**References**: `references/output-templates/dashboard-template.md`, `references/output-templates/color-system.md`
**Used by**: Main agent (CLAUDE.md)

---

## Instructions

### Step 11.1 — Load Input Data

Read all 4 input files:
1. `output/portfolio-recommendation.json` — 3 portfolio options, holdings, scenarios, risks
2. `output/environment-assessment.json` — dimension scores, regime classification
3. `output/user-profile.json` — budget, horizon, risk tolerance, output_language
4. `output/critic-report.json` — quality flags (if any)

Determine output language from `user-profile.json` `output_language` (`"ko"` or `"en"`).
Determine output date from current date for filename.

### Step 11.2 — Generate HTML Dashboard

Generate a single self-contained HTML file with:
- **TailwindCSS** via CDN (`<script src="https://cdn.tailwindcss.com"></script>`)
- **Chart.js** via CDN (`<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`)
- All styles inline or via Tailwind classes — no external CSS files
- Responsive design (works on desktop and tablet)

Read `references/output-templates/dashboard-template.md` for section structure and layout guidance.
Read `references/output-templates/color-system.md` for color palette and styling rules.

### Step 11.3 — Dashboard Sections (10 sections)

The HTML dashboard must include these 10 sections in order:

| # | Section | Content |
|---|---------|---------|
| 1 | **Header** | User profile summary (budget, horizon, risk tolerance), analysis date, data confidence grade, Quality Flag if present from critic-report |
| 2 | **Environment Overview** | Summary cards for macro/political/fundamentals/sentiment dimensions — score, direction, key drivers |
| 3 | **3-Column Portfolio Comparison** | Side-by-side comparison of aggressive/moderate/conservative options — allocation breakdown |
| 4 | **Asset Allocation Pie Charts** | Chart.js doughnut/pie chart for each option (one chart per option) |
| 5 | **Holding Recommendation Tables** | Per-option table: ticker, name, weight %, asset class, rationale |
| 6 | **Risk/Return Scatter Plot** | Chart.js scatter plot comparing 3 options (x = risk/volatility, y = expected return) |
| 7 | **Scenario Comparison Table** | Bull/base/bear scenarios for all 3 options — expected return, probability, assumptions |
| 8 | **Key Risks + Mechanism Chains** | Each risk with "Risk → Portfolio Impact → Response Action" chain, severity, affected options |
| 9 | **Rebalancing Triggers** | List of conditions that should prompt portfolio rebalancing |
| 10 | **Disclaimer** | "This is not investment advice. For informational purposes only." (bilingual if Korean output) |

### Step 11.4 — Chart.js Implementation

**Pie/Doughnut Charts** (Section 4):
- One chart per portfolio option (3 total)
- Segments: US Equity, KR Equity, Bonds, Alternatives, Cash
- Use color system from `color-system.md`
- Show percentage labels on hover

**Scatter Plot** (Section 6):
- X-axis: Risk metric (use bear scenario return magnitude as proxy)
- Y-axis: Base case expected return
- 3 data points (one per option), labeled with option name
- Include risk-return efficiency line

### Step 11.5 — Language & Formatting

- All text content in the language specified by `output_language`
- Numbers formatted with appropriate locale (KRW with commas, USD with $ prefix)
- Budget displayed in original currency
- Percentages to 1 decimal place
- Color-code risk severity (high = red, medium = orange, low = green)

### Step 11.6 — Write HTML File

Write the complete HTML file to:
```
output/reports/portfolio_{lang}_{date}.html
```

Where:
- `{lang}` = `"ko"` or `"en"` from user-profile
- `{date}` = current date in `YYYY-MM-DD` format

Example: `output/reports/portfolio_ko_2026-03-17.html`

Ensure the `output/reports/` directory exists before writing.

---

## Success Criteria

- [ ] HTML file generated at correct path
- [ ] File size > 0 bytes
- [ ] All 10 sections present in HTML
- [ ] TailwindCSS CDN loaded
- [ ] Chart.js CDN loaded
- [ ] At least 3 Chart.js charts rendered (3 pie charts)
- [ ] Scatter plot included
- [ ] Disclaimer present
- [ ] Quality flags from critic-report displayed (if any)
- [ ] Content is in correct language (ko/en)

---

## Failure Handling

- **HTML generation failure**: Retry once. If still failing, output a simplified HTML without charts (tables only) as fallback.
- **Missing input file**: If `critic-report.json` is missing (critic was skipped), proceed without quality flags — add `[No critic review]` note in header.
- **Chart.js rendering concerns**: Charts render client-side — ensure the HTML structure is correct even if the CDN is temporarily unavailable for the end user.
- **Core rule**: Always deliver an HTML file. Simpler HTML > no HTML.
