# Color System

## TailwindCSS Classes (CDN)

Dashboard uses dark theme. Include CDN:
```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### Background & Layout

- Page: `bg-gray-950 text-gray-100`
- Cards: `bg-gray-900 border border-gray-800 rounded-xl p-6`
- Section headers: `text-xl font-bold text-gray-100 mb-4`

### Risk Level Badges

| Level | Classes |
|-------|---------|
| Aggressive | `bg-red-900/50 text-red-300 border border-red-700 px-3 py-1 rounded-full text-sm` |
| Moderate | `bg-yellow-900/50 text-yellow-300 border border-yellow-700 px-3 py-1 rounded-full text-sm` |
| Conservative | `bg-blue-900/50 text-blue-300 border border-blue-700 px-3 py-1 rounded-full text-sm` |

### Data Confidence Badges

| Grade | Classes |
|-------|---------|
| A | `bg-emerald-900/50 text-emerald-300 border border-emerald-700` |
| B | `bg-blue-900/50 text-blue-300 border border-blue-700` |
| C | `bg-amber-900/50 text-amber-300 border border-amber-700` |
| D | `bg-red-900/50 text-red-300 border border-red-700` |

### Environment Score Colors

| Score Range | Color |
|-------------|-------|
| 8.0–10.0 | `text-emerald-400` (very positive) |
| 6.0–7.9 | `text-blue-400` (positive) |
| 4.0–5.9 | `text-yellow-400` (neutral) |
| 2.0–3.9 | `text-orange-400` (negative) |
| 1.0–1.9 | `text-red-400` (very negative) |

### Direction Indicators

| Direction | Display | Color |
|-----------|---------|-------|
| positive | ▲ | `text-emerald-400` |
| neutral-positive | ↗ | `text-blue-400` |
| neutral | → | `text-yellow-400` |
| neutral-negative | ↘ | `text-orange-400` |
| negative | ▼ | `text-red-400` |

### Chart.js Configuration

#### Pie Chart (Asset Allocation)

```javascript
const pieColors = {
  us_equity: '#3b82f6',   // blue-500
  kr_equity: '#8b5cf6',   // violet-500
  bonds: '#10b981',       // emerald-500
  alternatives: '#f59e0b', // amber-500
  cash: '#6b7280'         // gray-500
};
```

#### Scatter Plot (Risk/Return)

```javascript
const scatterColors = {
  aggressive: '#ef4444',   // red-500
  moderate: '#eab308',     // yellow-500
  conservative: '#3b82f6'  // blue-500
};
```

#### Scenario Bar Chart

```javascript
const scenarioColors = {
  bull: '#10b981',  // emerald-500
  base: '#6b7280',  // gray-500
  bear: '#ef4444'   // red-500
};
```
