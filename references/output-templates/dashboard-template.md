# Dashboard Template

Design: Professional light theme with gradient header. White cards, subtle shadows, Inter font. Green/red for semantic values only. Styled after stock-analysis-agent dashboard.

---

## CDN Block (always include in `<head>`)

```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<!-- For Korean output: -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
```

---

## Full HTML Skeleton

```html
<!DOCTYPE html>
<html lang="{LANG_CODE}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{PAGE_TITLE} | {DATE}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  {KOREAN_FONT_IF_KR}
  <style>
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Noto Sans KR', sans-serif; }
    @keyframes pulse-price { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    @keyframes grad { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .pulse-price { animation: pulse-price 2s ease-in-out infinite; }
    .grad-ani { background-size: 200% 200%; animation: grad 4s ease infinite; }
    .card { background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06); transition: transform 0.2s, box-shadow 0.2s; }
    .card:hover { transform: translateY(-2px); box-shadow: 0 4px 14px rgba(0,0,0,0.1); }
    .stat-card { border-left: 4px solid; }
    .source-tag { font-family: monospace; font-size: 0.7rem; padding: 1px 5px; border-radius: 3px; background: #f3f4f6; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
    .risk-row:hover { background-color: #fef2f2; }
    .severity-high { background: #fef2f2; border-left: 4px solid #ef4444; }
    .severity-medium { background: #fffbeb; border-left: 4px solid #f59e0b; }
    .severity-low { background: #f0fdf4; border-left: 4px solid #22c55e; }
  </style>
  <script>
    tailwind.config = { theme: { extend: { colors: {
      brand: { 50: '#eef3fc', 100: '#d4e2f9', 400: '#4285F4', 500: '#3367d6', 600: '#2a56b0', 700: '#1e3f80', 800: '#142a55', 900: '#0d1b38' }
    }}}}
  </script>
</head>
<body class="bg-gray-50 text-gray-800">

<!-- ============================================================ -->
<!-- SECTION 1: HEADER (dark gradient, portfolio-branded)          -->
<!-- ============================================================ -->
<header id="section-header" style="background: linear-gradient(135deg, #0d1b38 0%, #1e3f80 30%, #2a56b0 60%, #3367d6 100%);">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
            <i class="fa-solid fa-chart-pie text-2xl text-white"></i>
          </div>
          <div>
            <h1 class="text-3xl font-bold text-white tracking-tight">{PAGE_TITLE}</h1>
            <p class="text-blue-200 text-sm font-medium">AI-Powered Portfolio Recommendation</p>
          </div>
        </div>
        <div class="flex items-center gap-3 mt-4">
          <span class="text-2xl font-extrabold text-white pulse-price">{BUDGET_DISPLAY}</span>
          <span class="{RISK_BADGE_HEADER_CLASS}">
            {RISK_TOLERANCE_LABEL}
          </span>
        </div>
        <p class="text-blue-200/60 text-xs mt-1">{ANALYSIS_DATE} · {REGIME_LABEL}</p>
        <div class="flex items-center gap-3 mt-3">
          {DATA_CONFIDENCE_BADGE}
          {CRITIC_BADGE}
        </div>
      </div>
      <div class="flex flex-col gap-2 text-right">
        <div class="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
          <span class="text-blue-200/60">{BUDGET_LABEL}</span>
          <span class="text-white font-semibold">{BUDGET_VALUE}</span>
          <span class="text-blue-200/60">{PERIOD_LABEL}</span>
          <span class="text-white font-semibold">{PERIOD_VALUE}</span>
          <span class="text-blue-200/60">{RISK_LABEL}</span>
          <span class="text-white font-semibold">{RISK_VALUE}</span>
          <span class="text-blue-200/60">{SCOPE_LABEL}</span>
          <span class="text-white font-semibold">{SCOPE_VALUE}</span>
        </div>
      </div>
    </div>
    <div class="mt-4 pt-4 border-t border-white/10 flex flex-wrap gap-4 text-xs text-blue-200/50">
      <span>{DATE_INFO}</span>
      <span>·</span>
      <span>Regime: {REGIME}</span>
      <span>·</span>
      <span>{DATA_QUALITY_SUMMARY}</span>
    </div>
  </div>
</header>

<main class="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">

<!-- ============================================================ -->
<!-- SECTION 2: ENVIRONMENT OVERVIEW (stat-card grid)              -->
<!-- ============================================================ -->
<section id="section-environment">
  <h2 class="text-xl font-bold text-gray-900 mb-2"><i class="fa-solid fa-globe mr-2 text-brand-400"></i>{ENV_SECTION_TITLE}</h2>
  <p class="text-sm text-gray-500 mb-6">{ENV_SUMMARY_TEXT}</p>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    {ENVIRONMENT_CARDS}
    <!-- Each environment card pattern: -->
    <!--
    <div class="card p-5 stat-card" style="border-left-color: {SCORE_COLOR}">
      <div class="flex items-center justify-between mb-2">
        <p class="text-sm font-semibold text-gray-700">{DIMENSION_NAME}</p>
        <span class="{GRADE_BADGE_CLASS}">{GRADE}</span>
      </div>
      <div class="flex items-baseline gap-2 mb-3">
        <span class="text-3xl font-bold {SCORE_TEXT_COLOR}">{SCORE}</span>
        <span class="{DIRECTION_COLOR}"><i class="fa-solid fa-{DIRECTION_ICON}"></i></span>
        <span class="text-sm text-gray-400">{DIRECTION_LABEL}</span>
      </div>
      <ul class="space-y-1.5 text-xs text-gray-500">
        <li><i class="fa-solid fa-circle text-[4px] mr-2 align-middle {SCORE_TEXT_COLOR}"></i>{DRIVER_1}</li>
        <li><i class="fa-solid fa-circle text-[4px] mr-2 align-middle {SCORE_TEXT_COLOR}"></i>{DRIVER_2}</li>
        <li><i class="fa-solid fa-circle text-[4px] mr-2 align-middle {SCORE_TEXT_COLOR}"></i>{DRIVER_3}</li>
      </ul>
    </div>
    -->
  </div>
</section>

<!-- ============================================================ -->
<!-- SECTION 3: PORTFOLIO COMPARISON (3-column white cards)        -->
<!-- ============================================================ -->
<section id="section-comparison">
  <h2 class="text-xl font-bold text-gray-900 mb-4"><i class="fa-solid fa-columns mr-2 text-brand-400"></i>{COMPARISON_TITLE}</h2>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    {PORTFOLIO_CARDS}
    <!-- Each portfolio card pattern: -->
    <!--
    <div class="card p-6 {RECOMMENDED_BORDER}">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-gray-800">{OPTION_NAME}</h3>
        <span class="{RISK_BADGE_CLASS}">{RISK_LEVEL}</span>
      </div>
      {RECOMMENDED_TAG}
      <table class="w-full text-sm mt-3">
        <tbody>
          <tr class="border-b border-gray-100">
            <td class="py-2.5 text-gray-500">{ASSET_CLASS}</td>
            <td class="py-2.5 text-right font-semibold {ASSET_COLOR}">{WEIGHT}%</td>
          </tr>
          ...
          <tr class="bg-gray-50 rounded">
            <td class="py-2.5 font-semibold text-gray-700 pl-2">{EQUITY_TOTAL_LABEL}</td>
            <td class="py-2.5 text-right font-bold {RISK_COLOR} pr-2">{EQUITY_TOTAL}%</td>
          </tr>
        </tbody>
      </table>
    </div>
    -->
    <!-- Recommended option: add border-2 border-brand-400 ring-1 ring-brand-400/30 -->
    <!-- Recommended tag: <div class="text-xs text-brand-500 font-semibold uppercase tracking-wider mb-3"><i class="fa-solid fa-star mr-1"></i>Best Fit</div> -->
  </div>
</section>

<!-- ============================================================ -->
<!-- SECTION 4: ASSET ALLOCATION PIE CHARTS                        -->
<!-- ============================================================ -->
<section id="section-pies">
  <h2 class="text-xl font-bold text-gray-900 mb-4"><i class="fa-solid fa-chart-pie mr-2 text-brand-400"></i>{PIE_SECTION_TITLE}</h2>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <!-- One card per option, each containing a Chart.js pie/doughnut -->
    <div class="card p-5 text-center">
      <h3 class="text-sm font-semibold text-gray-700 mb-3">{OPTION_1_NAME}</h3>
      <canvas id="pieOption1" height="220"></canvas>
    </div>
    <div class="card p-5 text-center">
      <h3 class="text-sm font-semibold text-gray-700 mb-3">{OPTION_2_NAME}</h3>
      <canvas id="pieOption2" height="220"></canvas>
    </div>
    <div class="card p-5 text-center">
      <h3 class="text-sm font-semibold text-gray-700 mb-3">{OPTION_3_NAME}</h3>
      <canvas id="pieOption3" height="220"></canvas>
    </div>
  </div>
</section>

<!-- ============================================================ -->
<!-- SECTION 5: HOLDINGS TABLES                                    -->
<!-- ============================================================ -->
<section id="section-holdings">
  <h2 class="text-xl font-bold text-gray-900 mb-4"><i class="fa-solid fa-list-check mr-2 text-brand-400"></i>{HOLDINGS_TITLE}</h2>
  {HOLDINGS_TABLES}
  <!-- Each option's holdings table pattern: -->
  <!--
  <div class="card overflow-x-auto mb-4">
    <div class="p-5 border-b border-gray-100 flex items-center gap-3">
      <h3 class="text-base font-bold text-gray-800">{OPTION_NAME}</h3>
      <span class="{RISK_BADGE_CLASS}">{RISK_LEVEL}</span>
    </div>
    <table class="w-full text-sm">
      <thead>
        <tr class="bg-gray-50 text-gray-600 text-xs uppercase">
          <th class="text-left p-4 font-semibold">Ticker</th>
          <th class="text-left p-4 font-semibold">Name</th>
          <th class="text-left p-4 font-semibold">Asset Class</th>
          <th class="text-right p-4 font-semibold">Weight</th>
          <th class="text-left p-4 font-semibold">Rationale</th>
          <th class="text-center p-4 font-semibold">Source</th>
        </tr>
      </thead>
      <tbody>
        <tr class="border-b hover:bg-gray-50">
          <td class="py-3 px-4 font-mono font-medium text-brand-600">{TICKER}</td>
          <td class="py-3 px-4 text-gray-700">{NAME}</td>
          <td class="py-3 px-4"><span class="text-xs bg-{ASSET_BG} text-{ASSET_TEXT} px-2 py-0.5 rounded">{ASSET_CLASS}</span></td>
          <td class="py-3 px-4 text-right font-semibold">{WEIGHT}%</td>
          <td class="py-3 px-4 text-gray-500 text-xs leading-relaxed max-w-xs">{RATIONALE}</td>
          <td class="py-3 px-4 text-center"><code class="source-tag" style="color: {TAG_COLOR}">[{SOURCE}]</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  -->
</section>

<!-- ============================================================ -->
<!-- SECTION 6: RISK/RETURN SCATTER PLOT                           -->
<!-- ============================================================ -->
<section id="section-scatter">
  <h2 class="text-xl font-bold text-gray-900 mb-4"><i class="fa-solid fa-crosshairs mr-2 text-brand-400"></i>{SCATTER_TITLE}</h2>
  <div class="card p-5">
    <canvas id="scatterChart" height="300"></canvas>
  </div>
</section>

<!-- ============================================================ -->
<!-- SECTION 7: SCENARIO COMPARISON (gradient card)                -->
<!-- ============================================================ -->
<section id="section-scenarios" class="rounded-2xl overflow-hidden grad-ani" style="background: linear-gradient(135deg, #0d1b38, #1e3f80, #2a56b0, #142a55);">
  <div class="p-6 sm:p-8">
    <h2 class="text-lg font-bold text-blue-200 mb-1"><i class="fa-solid fa-bullseye mr-2"></i>{SCENARIO_TITLE}</h2>
    <p class="text-blue-200/50 text-xs mb-6">{SCENARIO_SUBTITLE}</p>

    <!-- R/R Score badges row -->
    <div class="flex flex-wrap gap-3 mb-6">
      {RR_SCORE_BADGES}
      <!-- Pattern: <div class="{RR_BADGE_CLASS}">R/R {OPTION}: {SCORE} · {INTERPRETATION}</div> -->
    </div>

    <!-- 3-column scenario cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      {SCENARIO_COLUMNS}
      <!-- Each column (one per option): -->
      <!--
      <div class="space-y-3">
        <h3 class="text-white font-semibold text-center mb-2">{OPTION_NAME}</h3>
        <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center border border-green-400/30">
          <p class="text-green-300 text-sm font-semibold mb-1"><i class="fa-solid fa-arrow-trend-up mr-1"></i>Bull ({PROB}%)</p>
          <p class="text-2xl font-extrabold text-white">{BULL_RETURN}%</p>
          <p class="text-blue-200/40 text-xs mt-1">{BULL_ASSUMPTION}</p>
        </div>
        <div class="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center border-2 border-blue-300/50">
          <p class="text-blue-200 text-sm font-semibold mb-1"><i class="fa-solid fa-equals mr-1"></i>Base ({PROB}%)</p>
          <p class="text-2xl font-extrabold text-white">{BASE_RETURN}%</p>
          <p class="text-blue-200/40 text-xs mt-1">{BASE_ASSUMPTION}</p>
        </div>
        <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center border border-red-400/30">
          <p class="text-red-300 text-sm font-semibold mb-1"><i class="fa-solid fa-arrow-trend-down mr-1"></i>Bear ({PROB}%)</p>
          <p class="text-2xl font-extrabold text-white">{BEAR_RETURN}%</p>
          <p class="text-blue-200/40 text-xs mt-1">{BEAR_ASSUMPTION}</p>
        </div>
      </div>
      -->
    </div>
  </div>
</section>

<!-- ============================================================ -->
<!-- SECTION 8: KEY RISKS + MECHANISM CHAINS                       -->
<!-- ============================================================ -->
<section id="section-risks">
  <h2 class="text-xl font-bold text-gray-900 mb-4"><i class="fa-solid fa-triangle-exclamation mr-2 text-brand-400"></i>{RISKS_TITLE}</h2>
  <div class="space-y-3">
    {RISK_CARDS}
    <!-- Each risk card pattern: -->
    <!--
    <div class="card p-5 {SEVERITY_CLASS}">
      <div class="flex items-center justify-between mb-2">
        <h3 class="font-semibold text-gray-800">{RISK_NAME}</h3>
        <div class="flex items-center gap-2">
          <span class="{SEVERITY_BADGE}">{SEVERITY}</span>
          <span class="text-xs text-gray-400">{AFFECTED_OPTIONS}</span>
        </div>
      </div>
      <div class="text-sm text-gray-600 space-y-1">
        <div class="flex items-center gap-2">
          <span class="bg-red-100 text-red-700 text-xs px-2 py-0.5 rounded font-medium">Risk</span>
          <span>{RISK_DESC}</span>
        </div>
        <div class="flex items-center gap-2 text-gray-400">→</div>
        <div class="flex items-center gap-2">
          <span class="bg-orange-100 text-orange-700 text-xs px-2 py-0.5 rounded font-medium">Impact</span>
          <span>{IMPACT_DESC}</span>
        </div>
        <div class="flex items-center gap-2 text-gray-400">→</div>
        <div class="flex items-center gap-2">
          <span class="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded font-medium">Response</span>
          <span>{RESPONSE_DESC}</span>
        </div>
      </div>
    </div>
    -->
  </div>
</section>

<!-- ============================================================ -->
<!-- SECTION 9: REBALANCING TRIGGERS                               -->
<!-- ============================================================ -->
<section id="section-rebalancing">
  <h2 class="text-xl font-bold text-gray-900 mb-4"><i class="fa-solid fa-arrows-rotate mr-2 text-brand-400"></i>{REBALANCING_TITLE}</h2>
  <div class="card p-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      {TRIGGER_ITEMS}
      <!-- Each trigger pattern: -->
      <!--
      <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
        <div class="w-8 h-8 bg-brand-400 rounded-full flex items-center justify-center flex-shrink-0">
          <i class="fa-solid fa-{ICON} text-white text-xs"></i>
        </div>
        <p class="text-sm text-gray-700">{TRIGGER_TEXT}</p>
      </div>
      -->
    </div>
  </div>
</section>

</main>

<!-- ============================================================ -->
<!-- FOOTER (DISCLAIMER)                                           -->
<!-- ============================================================ -->
<footer class="bg-gray-900 text-gray-400 mt-12">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
    <div class="flex flex-col md:flex-row justify-between items-start gap-4">
      <div>
        <p class="text-xs mb-2"><strong class="text-gray-300"><i class="fa-solid fa-shield-halved mr-1"></i>Disclaimer:</strong> {DISCLAIMER_TEXT}</p>
        <p class="text-xs">{FOOTER_INFO}</p>
      </div>
      <div class="text-xs text-right">
        <p>Powered by AI Portfolio Analysis</p>
        <p class="text-gray-500 mt-1">{ANALYSIS_DATE}</p>
      </div>
    </div>
  </div>
</footer>

<!-- ============================================================ -->
<!-- CHART.JS INITIALIZATION (light theme)                         -->
<!-- ============================================================ -->
<script>
{CHART_JS_CODE}
</script>

</body>
</html>
```

---

## Population Instructions

When generating a dashboard:

1. Replace ALL `{PLACEHOLDER}` values with actual data from input JSON files
2. For missing data (Grade D or not collected): replace with `<span class="text-gray-400">—</span>`
3. Source tags: use `<code class="source-tag" style="color: {TAG_COLOR}">[TAG]</code>` inline
4. Chart data arrays: convert to JS array syntax `[1.5, 2.3, ...]`
5. Positive metric changes: `text-green-600`, negative: `text-red-600`, neutral: `text-gray-500`
6. Stat-card border colors: match environment score color from `color-system.md`
7. Recommended option (matching user's risk_tolerance): highlight with `border-2 border-brand-400`

## Asset Class Badge Colors

| Asset Class | Badge Classes |
|-------------|--------------|
| US Equity | `bg-blue-50 text-blue-700` |
| KR Equity | `bg-violet-50 text-violet-700` |
| Bonds | `bg-emerald-50 text-emerald-700` |
| Alternatives | `bg-amber-50 text-amber-700` |
| Cash | `bg-gray-100 text-gray-600` |

## Missing Section Handling

If any section's data is unavailable or insufficient, render:
```html
<div class="text-gray-400 italic text-sm p-4 border border-gray-200 rounded-lg bg-gray-50">
  [Data unavailable — {reason}]
</div>
```
Never omit a section entirely — the structural skeleton must be preserved.

## Responsive Design

- Use `grid grid-cols-1 md:grid-cols-3 gap-4` for 3-option layouts
- Charts resize via Chart.js `responsive: true` option
- Mobile: columns stack vertically
- Header: `flex-col md:flex-row` for mobile/desktop adaptation
