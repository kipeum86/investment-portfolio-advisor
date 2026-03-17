# Color System

## CDN Block (always include in `<head>`)

```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<!-- For Korean output, also add: -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
```

## Tailwind Config (brand colors)

```html
<script>
  tailwind.config = { theme: { extend: { colors: {
    brand: { 50: '#eef3fc', 100: '#d4e2f9', 400: '#4285F4', 500: '#3367d6', 600: '#2a56b0', 700: '#1e3f80', 800: '#142a55', 900: '#0d1b38' }
  }}}}
</script>
```

## CSS Block (include in `<style>`)

```css
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
```

## Background & Layout (Light Theme)

- Page: `bg-gray-50 text-gray-800`
- Cards: `.card` class (white bg + shadow) or `.card p-6`
- Stat cards: `.card p-5 stat-card` with `style="border-left-color: {color}"`
- Section headers: `text-xl font-bold text-gray-900 mb-4` with FontAwesome icon `<i class="fa-solid fa-{icon} mr-2 text-brand-400"></i>`
- Section subtext: `text-sm text-gray-500 mb-6`
- Max width: `max-w-7xl mx-auto px-4 sm:px-6`

## Header (Gradient)

```
background: linear-gradient(135deg, #0d1b38 0%, #1e3f80 30%, #2a56b0 60%, #3367d6 100%);
```

- Title: `text-3xl font-bold text-white tracking-tight`
- Subtitle: `text-blue-200 text-sm font-medium`
- Info grid: `text-blue-200/60` labels, `text-white font-semibold` values
- Footer bar: `border-t border-white/10`, `text-xs text-blue-200/50`

## Risk Level Badges

| Level | Classes |
|-------|---------|
| Aggressive | `bg-red-50 text-red-700 border border-red-200 px-3 py-1 rounded-full text-sm font-semibold` |
| Moderate | `bg-yellow-50 text-yellow-700 border border-yellow-200 px-3 py-1 rounded-full text-sm font-semibold` |
| Conservative | `bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1 rounded-full text-sm font-semibold` |

## Data Confidence Badges

**In header (on gradient background):**

| Grade | Classes |
|-------|---------|
| A | `bg-emerald-50 text-emerald-700 text-xs font-semibold px-2.5 py-1 rounded-full border border-emerald-200` |
| B | `bg-blue-50 text-blue-700 text-xs font-semibold px-2.5 py-1 rounded-full border border-blue-200` |
| C | `bg-amber-50 text-amber-700 text-xs font-semibold px-2.5 py-1 rounded-full border border-amber-200` |
| D | `bg-red-50 text-red-700 text-xs font-semibold px-2.5 py-1 rounded-full border border-red-200` |

**Inline (on white background):**

| Grade | Classes |
|-------|---------|
| A | `inline-block bg-emerald-50 text-emerald-700 text-xs px-1.5 py-0.5 rounded` |
| B | `inline-block bg-blue-50 text-blue-700 text-xs px-1.5 py-0.5 rounded` |
| C | `inline-block bg-amber-50 text-amber-700 text-xs px-1.5 py-0.5 rounded` |
| D | `inline-block bg-red-50 text-red-700 text-xs px-1.5 py-0.5 rounded` |

## Environment Score Colors

| Score Range | Text Color | Stat-card Border |
|-------------|------------|-----------------|
| 8.0–10.0 | `text-emerald-600` (very positive) | `#10b981` |
| 6.0–7.9 | `text-blue-600` (positive) | `#3b82f6` |
| 4.0–5.9 | `text-yellow-600` (neutral) | `#eab308` |
| 2.0–3.9 | `text-orange-600` (negative) | `#f97316` |
| 1.0–1.9 | `text-red-600` (very negative) | `#ef4444` |

## Direction Indicators

| Direction | Display | Color |
|-----------|---------|-------|
| positive | `<i class="fa-solid fa-arrow-trend-up"></i>` ▲ | `text-emerald-600` |
| neutral-positive | `<i class="fa-solid fa-arrow-right"></i>` ↗ | `text-blue-600` |
| neutral | `<i class="fa-solid fa-minus"></i>` → | `text-yellow-600` |
| neutral-negative | `<i class="fa-solid fa-arrow-right"></i>` ↘ | `text-orange-600` |
| negative | `<i class="fa-solid fa-arrow-trend-down"></i>` ▼ | `text-red-600` |

## Source Tags

| Tag | Style |
|-----|-------|
| `[Official]` | `<code class="source-tag" style="color: #2563eb">[Official]</code>` |
| `[Portal]` | `<code class="source-tag" style="color: #4b5563">[Portal]</code>` |
| `[KR-Portal]` | `<code class="source-tag" style="color: #7c3aed">[KR-Portal]</code>` |
| `[Calc]` | `<code class="source-tag" style="color: #059669">[Calc]</code>` |
| `[Est]` | `<code class="source-tag" style="color: #d97706">[Est]</code>` |
| `[News]` | `<code class="source-tag" style="color: #ea580c">[News]</code>` |

## Scenario Section (Gradient Card)

The scenario comparison section uses a gradient card matching the header:
```
class="rounded-2xl overflow-hidden grad-ani"
style="background: linear-gradient(135deg, #0d1b38, #1e3f80, #2a56b0, #142a55);"
```

Inside cards use glassmorphism:
- Default: `bg-white/10 backdrop-blur-sm rounded-xl p-5 text-center`
- Bull: `border border-green-400/30`
- Base (emphasized): `bg-white/15 border-2 border-blue-300/50 scale-105`
- Bear: `border border-red-400/30`

## Risk-Return Score Badges

| R/R Score | Classes |
|-----------|---------|
| > 3.0 (Favorable) | `bg-emerald-900 text-emerald-300 border border-emerald-600 text-lg font-bold px-5 py-2 rounded-xl` |
| 1.0–3.0 (Neutral) | `bg-gray-600 text-white text-lg font-bold px-5 py-2 rounded-xl` |
| < 1.0 (Unfavorable) | `bg-red-900 text-red-300 border border-red-600 text-lg font-bold px-5 py-2 rounded-xl` |

## Chart.js Configuration

### Base Chart Colors

```javascript
const blue = 'rgba(59,130,246,';      // #3b82f6
const green = 'rgba(52,168,83,';      // #34a853
const yellow = 'rgba(251,188,5,';     // #fbbc05
const red = 'rgba(234,67,53,';        // #ea4335
const gray = 'rgba(107,114,128,';     // #6b7280
const violet = 'rgba(139,92,246,';    // #8b5cf6
```

### Global Chart Options (Light Theme)

```javascript
const globalChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#4b5563', font: { size: 11 }, usePointStyle: true }
    },
    tooltip: {
      backgroundColor: '#1f2937',
      titleColor: '#f9fafb',
      bodyColor: '#d1d5db',
      borderColor: '#374151',
      borderWidth: 1
    }
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#6b7280', font: { size: 10 } } },
    y: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { color: '#6b7280', font: { size: 10 } } }
  }
};
```

### Pie Chart (Asset Allocation)

```javascript
const pieColors = {
  us_equity: '#3b82f6',    // blue-500
  kr_equity: '#8b5cf6',    // violet-500
  bonds: '#10b981',        // emerald-500
  alternatives: '#f59e0b', // amber-500
  cash: '#6b7280'          // gray-500
};
```

### Scatter Plot (Risk/Return)

```javascript
const scatterColors = {
  aggressive: '#ef4444',    // red-500
  moderate: '#eab308',      // yellow-500
  conservative: '#3b82f6'   // blue-500
};
```

### Scenario Colors

```javascript
const scenarioColors = {
  bull: '#10b981',  // emerald-500
  base: '#6b7280',  // gray-500
  bear: '#ef4444'   // red-500
};
```

## Positive/Negative Semantic Colors

- Positive values: `text-green-600`
- Negative values: `text-red-600`
- Neutral values: `text-gray-500`

## Table Styling

- Header row: `bg-gray-50 text-gray-600 text-xs uppercase`
- Subject/highlight row: `bg-blue-50/60 border-b font-semibold`
- Regular row: `border-b hover:bg-gray-50`
- Cell padding: `p-4` (header), `py-3 px-4` (body)

## Missing Data Handling

```html
<!-- Single value missing -->
<span class="text-gray-400">—</span>

<!-- Entire section unavailable -->
<div class="text-gray-400 italic text-sm p-4 border border-gray-200 rounded-lg bg-gray-50">
  [Data unavailable — {reason}]
</div>
```
