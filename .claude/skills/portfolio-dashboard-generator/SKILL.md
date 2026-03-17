# Portfolio Dashboard Generator — SKILL.md

**Role**: Step 11 (HTML) — Generate an interactive HTML dashboard comparing 3 portfolio options.
**Design**: Professional light theme with gradient header, white cards with subtle shadows, Inter font. Styled after stock-analysis-agent dashboard.
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

### Step 11.2 — Load Style References

Load in this order:
1. Read `references/output-templates/dashboard-template.md` — complete HTML skeleton with all sections, placeholder patterns, and structural guidance
2. Read `references/output-templates/color-system.md` — Tailwind CSS classes, Chart.js color configs, CDN block, CSS styles, and brand color system

**Required CDNs** (all 4 must be in `<head>`):
- TailwindCSS: `<script src="https://cdn.tailwindcss.com"></script>`
- Chart.js: `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`
- FontAwesome 6.4.2: `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">`
- Inter font: `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">`
- (Korean output) Noto Sans KR: `<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">`

**Required CSS & Config** (from `color-system.md`):
- Include the full `<style>` block (card, stat-card, animations, scrollbar, source-tag, severity classes)
- Include the Tailwind config block (brand color palette)

### Step 11.3 — Generate HTML Dashboard

Generate a single self-contained HTML file following the skeleton in `dashboard-template.md`.

**Theme**: Light (`bg-gray-50 text-gray-800`). NOT dark theme.

The HTML dashboard must include these 10 sections in order:

| # | Section | Key Styling |
|---|---------|-------------|
| 1 | **Header** | Blue gradient background (`linear-gradient(135deg, ...)`), white text, portfolio icon, user profile grid, data confidence badge, pulse animation on budget |
| 2 | **Environment Overview** | `stat-card` pattern with colored left border matching score range, FontAwesome icons for directions, grade badge per dimension |
| 3 | **Portfolio Comparison** | White `.card` per option, recommended option highlighted with `border-2 border-brand-400`, allocation table with asset-class colors |
| 4 | **Asset Allocation Pie Charts** | Chart.js pie/doughnut in white cards, 3 side-by-side |
| 5 | **Holdings Tables** | White `.card` with `bg-gray-50` header row, semantic source tags (colored per source type), ticker in `font-mono text-brand-600` |
| 6 | **Risk/Return Scatter Plot** | Chart.js scatter in white card |
| 7 | **Scenario Comparison** | Gradient card (`grad-ani`), glassmorphism inner cards (`bg-white/10 backdrop-blur-sm`), R/R score badges, bull/base/bear per option |
| 8 | **Key Risks** | White cards with severity left border (`severity-high/medium/low`), Risk → Impact → Response chain with colored step badges |
| 9 | **Rebalancing Triggers** | White card with icon items (`bg-brand-400` rounded icon + text) |
| 10 | **Disclaimer** | Dark footer (`bg-gray-900`), muted text |

### Step 11.4 — Chart.js Implementation

Use `color-system.md` for all Chart.js colors. Charts render on light (`bg-gray-50`) background.

**Pie/Doughnut Charts** (Section 4):
- One chart per portfolio option (3 total)
- Segments: US Equity, KR Equity, Bonds, Alternatives, Cash
- Use `pieColors` from color-system.md
- Show percentage labels on hover
- Apply `globalChartOptions` tooltip styling

**Scatter Plot** (Section 6):
- X-axis: Risk metric (use bear scenario return magnitude as proxy)
- Y-axis: Base case expected return
- 3 data points (one per option), labeled with option name
- Use `scatterColors` from color-system.md

### Step 11.5 — Source Tag Styling

Each holding's source tag must use the semantic color system:
- `[Official]` → blue (`#2563eb`)
- `[Portal]` → gray (`#4b5563`)
- `[KR-Portal]` → purple (`#7c3aed`)
- `[Calc]` → green (`#059669`)
- `[Est]` → yellow (`#d97706`)
- `[News]` → orange (`#ea580c`)

Pattern: `<code class="source-tag" style="color: {color}">[{tag}]</code>`

### Step 11.6 — Language & Formatting

- All text content in the language specified by `output_language`
- Numbers formatted with appropriate locale (KRW with commas, USD with $ prefix)
- Budget displayed in original currency
- Percentages to 1 decimal place
- Section headers use FontAwesome icons (`<i class="fa-solid fa-{icon} mr-2 text-brand-400"></i>`)

### Step 11.7 — Write HTML File

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
- [ ] **Light theme** applied (`bg-gray-50`, white cards)
- [ ] **Gradient header** present (blue gradient, not flat dark)
- [ ] **FontAwesome icons** loaded and visible in section headers
- [ ] **Inter font** loaded as primary font
- [ ] **Brand color system** applied via Tailwind config
- [ ] All 10 sections present in HTML
- [ ] At least 3 Chart.js charts rendered (3 pie charts + 1 scatter)
- [ ] Source tags use semantic colors per source type
- [ ] Scenario section uses gradient card with glassmorphism
- [ ] Risk cards have severity-colored left borders
- [ ] Dark footer with disclaimer present
- [ ] Quality flags from critic-report displayed (if any)
- [ ] Content is in correct language (ko/en)

---

## Failure Handling

- **HTML generation failure**: Retry once. If still failing, output a simplified HTML without charts (tables only) as fallback.
- **Missing input file**: If `critic-report.json` is missing (critic was skipped), proceed without quality flags — add `[No critic review]` note in header.
- **Chart.js rendering concerns**: Charts render client-side — ensure the HTML structure is correct even if the CDN is temporarily unavailable for the end user.
- **Core rule**: Always deliver an HTML file. Simpler HTML > no HTML.
