# FRED API Integration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate FRED API as the primary data source for US macroeconomic indicators and credit spreads, with web search fallback.

**Architecture:** A shared Python script (`.claude/scripts/fred_client.py`) fetches data from the FRED API and outputs JSON compatible with existing raw data schemas. The macro-collector and fundamentals-collector SKILL.md files are updated to call this script before falling back to web search.

**Tech Stack:** Python 3, `requests` library, FRED REST API, `pytest` for testing

**Spec:** `docs/superpowers/specs/2026-03-25-fred-api-integration-design.md`

---

## Chunk 1: fred_client.py Core Implementation (TDD)

### Task 1: Setup — Dependencies and Directory

**Files:**
- Modify: `requirements.txt`
- Create: `.claude/scripts/` (directory)

- [ ] **Step 1: Add `requests` to requirements.txt**

```
python-docx>=1.1.0
pytest>=8.0.0
requests>=2.31.0
```

- [ ] **Step 2: Create the shared scripts directory**

Run: `mkdir -p .claude/scripts`

- [ ] **Step 3: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: Successfully installed requests (if not already present)

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: add requests dependency for FRED API integration"
```

---

### Task 2: TDD — Period Formatting and Value Transforms

**Files:**
- Create: `tests/scripts/test_fred_client.py`
- Create: `.claude/scripts/fred_client.py`

- [ ] **Step 1: Write failing tests for period formatting and transforms**

Create `tests/scripts/test_fred_client.py`:

```python
"""Tests for fred_client.py"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/scripts"))


# --- Period formatting tests ---

def test_format_period_quarterly():
    from fred_client import format_period
    assert format_period("2025-10-01", "A191RL1Q225SBEA") == "Q4 2025"

def test_format_period_quarterly_q1():
    from fred_client import format_period
    assert format_period("2026-01-01", "A191RL1Q225SBEA") == "Q1 2026"

def test_format_period_monthly():
    from fred_client import format_period
    assert format_period("2026-02-01", "CPIAUCSL") == "Feb 2026"

def test_format_period_daily():
    from fred_client import format_period
    assert format_period("2026-03-24", "DGS10") == "2026-03-24"


# --- Transform tests ---

def test_apply_transform_none():
    from fred_client import apply_transform
    assert apply_transform(2.3, None) == 2.3

def test_apply_transform_multiply_100():
    from fred_client import apply_transform
    assert apply_transform(0.42, "multiply_100") == 42.0

def test_apply_transform_multiply_100_negative():
    from fred_client import apply_transform
    assert apply_transform(-1.08, "multiply_100") == -108.0


# --- SERIES_MAP completeness ---

def test_series_map_has_all_macro_indicators():
    from fred_client import SERIES_MAP
    macro_ids = [
        "us_gdp_growth", "us_cpi", "us_pce", "us_fed_rate",
        "us_unemployment", "us_10y_yield", "us_2y_yield", "us_yield_spread",
    ]
    for ind_id in macro_ids:
        assert ind_id in SERIES_MAP, f"Missing macro indicator: {ind_id}"
        assert "category" in SERIES_MAP[ind_id], f"Missing category for {ind_id}"
        assert SERIES_MAP[ind_id]["category"] == "us"

def test_series_map_has_all_fundamentals_indicators():
    from fred_client import SERIES_MAP
    fund_ids = ["us_ig_spread", "us_hy_spread"]
    for ind_id in fund_ids:
        assert ind_id in SERIES_MAP, f"Missing fundamentals indicator: {ind_id}"
        assert "market" in SERIES_MAP[ind_id], f"Missing market for {ind_id}"
        assert SERIES_MAP[ind_id]["market"] == "us"

def test_series_map_entries_have_required_fields():
    from fred_client import SERIES_MAP
    required = {"series_id", "name", "unit", "transform", "api_units"}
    for ind_id, config in SERIES_MAP.items():
        for field in required:
            assert field in config, f"Missing {field} in SERIES_MAP[{ind_id}]"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor && python -m pytest tests/scripts/test_fred_client.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'fred_client'`

- [ ] **Step 3: Implement `fred_client.py` — SERIES_MAP, format_period, apply_transform**

Create `.claude/scripts/fred_client.py`:

```python
#!/usr/bin/env python3
"""
FRED API Client — Shared script for fetching US economic indicators.

Fetches data from the Federal Reserve Economic Data (FRED) API
and outputs JSON compatible with the pipeline's raw data schemas.

Usage:
    python .claude/scripts/fred_client.py \
        --indicators us_gdp_growth,us_cpi,us_fed_rate \
        --output output/data/macro/fred-data.json --write
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library required. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

FRED_API_BASE = "https://api.stlouisfed.org/fred/series/observations"

SERIES_MAP = {
    # Macro indicators
    "us_gdp_growth": {
        "series_id": "A191RL1Q225SBEA",
        "name": "US GDP Growth Rate (QoQ annualized)",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": None,
    },
    "us_cpi": {
        "series_id": "CPIAUCSL",
        "name": "US CPI (YoY)",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": "pc1",
    },
    "us_pce": {
        "series_id": "PCEPI",
        "name": "US PCE Price Index (YoY)",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": "pc1",
    },
    "us_fed_rate": {
        "series_id": "DFF",
        "name": "Effective Federal Funds Rate",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": None,
    },
    "us_unemployment": {
        "series_id": "UNRATE",
        "name": "US Unemployment Rate",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": None,
    },
    "us_10y_yield": {
        "series_id": "DGS10",
        "name": "10-Year Treasury Yield",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": None,
    },
    "us_2y_yield": {
        "series_id": "DGS2",
        "name": "2-Year Treasury Yield",
        "category": "us",
        "unit": "%",
        "transform": None,
        "api_units": None,
    },
    "us_yield_spread": {
        "series_id": "T10Y2Y",
        "name": "2Y-10Y Treasury Spread",
        "category": "us",
        "unit": "bps",
        "transform": "multiply_100",
        "api_units": None,
    },
    # Fundamentals indicators
    "us_ig_spread": {
        "series_id": "BAMLC0A0CM",
        "name": "ICE BofA US Corporate IG OAS",
        "market": "us",
        "unit": "bps",
        "transform": "multiply_100",
        "api_units": None,
    },
    "us_hy_spread": {
        "series_id": "BAMLH0A0HYM2",
        "name": "ICE BofA US High Yield OAS",
        "market": "us",
        "unit": "bps",
        "transform": "multiply_100",
        "api_units": None,
    },
}

# Series IDs that publish quarterly data
_QUARTERLY_SERIES = {"A191RL1Q225SBEA"}

# Series IDs that publish monthly data
_MONTHLY_SERIES = {"CPIAUCSL", "PCEPI", "UNRATE", "BAMLC0A0CM", "BAMLH0A0HYM2"}


def format_period(date_str: str, series_id: str) -> str:
    """Format FRED observation date into human-readable period string."""
    year, month, _day = date_str.split("-")
    month_int = int(month)

    if series_id in _QUARTERLY_SERIES:
        quarter = (month_int - 1) // 3 + 1
        return f"Q{quarter} {year}"
    elif series_id in _MONTHLY_SERIES:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%b %Y")
    else:
        return date_str


def apply_transform(value: float, transform: str | None) -> float:
    """Apply unit transformation to raw FRED value."""
    if transform is None:
        return value
    if transform == "multiply_100":
        return round(value * 100, 1)
    return value
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor && python -m pytest tests/scripts/test_fred_client.py -v`
Expected: All 10 tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/scripts/fred_client.py tests/scripts/test_fred_client.py
git commit -m "feat: add fred_client.py core — SERIES_MAP, period formatting, transforms"
```

---

### Task 3: TDD — API Fetch Logic

**Files:**
- Modify: `tests/scripts/test_fred_client.py`
- Modify: `.claude/scripts/fred_client.py`

- [ ] **Step 1: Write failing tests for fetch_indicator (mocked HTTP)**

Append to `tests/scripts/test_fred_client.py`:

```python
from unittest.mock import patch, MagicMock


def _mock_fred_response(value: str, date: str):
    """Create a mock FRED API JSON response."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "observations": [
            {"date": date, "value": value}
        ]
    }
    return resp


def _mock_fred_error(status_code: int):
    resp = MagicMock()
    resp.status_code = status_code
    resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


@patch("fred_client.requests.get")
def test_fetch_indicator_success(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response("2.3", "2025-10-01")
    result = fetch_indicator("us_gdp_growth", "test_api_key")
    assert result["id"] == "us_gdp_growth"
    assert result["value"] == 2.3
    assert result["period"] == "Q4 2025"
    assert result["source_tag"] == "[Official]"
    assert result["category"] == "us"
    assert result["name"] == "US GDP Growth Rate (QoQ annualized)"


@patch("fred_client.requests.get")
def test_fetch_indicator_with_transform(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response("0.42", "2026-03-24")
    result = fetch_indicator("us_yield_spread", "test_api_key")
    assert result["value"] == 42.0
    assert result["unit"] == "bps"


@patch("fred_client.requests.get")
def test_fetch_indicator_with_api_units(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response("3.1", "2026-02-01")
    result = fetch_indicator("us_cpi", "test_api_key")
    # Verify api_units=pc1 was passed in the request
    call_args = mock_get.call_args
    assert call_args[1]["params"]["units"] == "pc1"
    assert result["value"] == 3.1


@patch("fred_client.requests.get")
def test_fetch_indicator_empty_observations(mock_get):
    from fred_client import fetch_indicator
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"observations": []}
    mock_get.return_value = resp
    result = fetch_indicator("us_gdp_growth", "test_api_key")
    assert result is None


@patch("fred_client.requests.get")
def test_fetch_indicator_dot_value_skipped(mock_get):
    """FRED returns '.' for missing values — should skip."""
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response(".", "2026-03-24")
    result = fetch_indicator("us_10y_yield", "test_api_key")
    assert result is None


@patch("fred_client.requests.get")
def test_fetch_indicator_http_error(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_error(500)
    result = fetch_indicator("us_gdp_growth", "test_api_key")
    assert result is None


@patch("fred_client.requests.get")
def test_fetch_indicator_429_retries_once(mock_get):
    """429 should retry once with 1s backoff."""
    from fred_client import fetch_indicator
    mock_get.side_effect = [
        _mock_fred_error(429),
        _mock_fred_response("4.5", "2026-03-24"),
    ]
    result = fetch_indicator("us_fed_rate", "test_api_key")
    assert result is not None
    assert result["value"] == 4.5
    assert mock_get.call_count == 2


@patch("fred_client.requests.get")
def test_fetch_indicator_connection_error(mock_get):
    """ConnectionError should return None without crashing."""
    from fred_client import fetch_indicator
    mock_get.side_effect = ConnectionError("Connection refused")
    result = fetch_indicator("us_gdp_growth", "test_api_key")
    assert result is None


@patch("fred_client.requests.get")
def test_fetch_indicator_fundamentals_has_market_field(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response("1.30", "2026-03-21")
    result = fetch_indicator("us_ig_spread", "test_api_key")
    assert result["market"] == "us"
    assert "category" not in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor && python -m pytest tests/scripts/test_fred_client.py::test_fetch_indicator_success -v`
Expected: FAIL with `cannot import name 'fetch_indicator'`

- [ ] **Step 3: Implement fetch_indicator in fred_client.py**

Add to `.claude/scripts/fred_client.py` after `apply_transform`:

```python
def fetch_indicator(indicator_id: str, api_key: str) -> dict | None:
    """
    Fetch a single indicator from the FRED API.

    Returns an indicator dict on success, None on failure.
    """
    if indicator_id not in SERIES_MAP:
        return None

    config = SERIES_MAP[indicator_id]
    series_id = config["series_id"]

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    if config["api_units"]:
        params["units"] = config["api_units"]

    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            resp = requests.get(FRED_API_BASE, params=params, timeout=10)
            if resp.status_code == 429 and attempt < max_attempts - 1:
                time.sleep(1)
                continue
            resp.raise_for_status()
        except Exception:
            return None

        data = resp.json()
        observations = data.get("observations", [])
        if not observations:
            return None

        obs = observations[0]
        raw_value = obs.get("value", ".")
        if raw_value == ".":
            return None

        value = apply_transform(float(raw_value), config["transform"])
        now = datetime.now(timezone.utc).isoformat()

        result = {
            "id": indicator_id,
            "name": config["name"],
            "value": value,
            "unit": config["unit"],
            "period": format_period(obs["date"], series_id),
            "source_tag": "[Official]",
            "source_url": f"https://fred.stlouisfed.org/series/{series_id}",
            "retrieved_at": now,
        }

        if "category" in config:
            result["category"] = config["category"]
        if "market" in config:
            result["market"] = config["market"]

        return result

    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor && python -m pytest tests/scripts/test_fred_client.py -v`
Expected: All 19 tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/scripts/fred_client.py tests/scripts/test_fred_client.py
git commit -m "feat: add fetch_indicator with retry, transforms, and error handling"
```

---

### Task 4: TDD — CLI Interface and fetch_all

**Files:**
- Modify: `tests/scripts/test_fred_client.py`
- Modify: `.claude/scripts/fred_client.py`

- [ ] **Step 1: Write failing tests for fetch_all and CLI**

Append to `tests/scripts/test_fred_client.py`:

```python
import json
import subprocess


@patch("fred_client.requests.get")
def test_fetch_all_success(mock_get):
    from fred_client import fetch_all
    mock_get.return_value = _mock_fred_response("2.3", "2025-10-01")
    result = fetch_all(["us_gdp_growth", "us_cpi"], "test_key")
    assert result["source"] == "FRED_API"
    assert len(result["indicators"]) == 2
    assert len(result["errors"]) == 0


@patch("fred_client.requests.get")
def test_fetch_all_partial_failure(mock_get):
    from fred_client import fetch_all
    mock_get.side_effect = [
        _mock_fred_response("2.3", "2025-10-01"),
        _mock_fred_error(500),
    ]
    result = fetch_all(["us_gdp_growth", "us_cpi"], "test_key")
    assert len(result["indicators"]) == 1
    assert len(result["errors"]) == 1
    assert result["errors"][0]["id"] == "us_cpi"


@patch("fred_client.requests.get")
def test_fetch_all_invalid_indicator_skipped(mock_get):
    from fred_client import fetch_all
    result = fetch_all(["not_real_indicator"], "test_key")
    assert len(result["indicators"]) == 0
    assert len(result["errors"]) == 1


def test_cli_missing_api_key():
    """CLI should exit 1 when no API key is available."""
    env = os.environ.copy()
    env.pop("FRED_API_KEY", None)
    proc = subprocess.run(
        [sys.executable, ".claude/scripts/fred_client.py", "--indicators", "us_gdp_growth"],
        capture_output=True, text=True, env=env,
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    assert proc.returncode == 1
    assert "API key" in proc.stderr
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor && python -m pytest tests/scripts/test_fred_client.py::test_fetch_all_success -v`
Expected: FAIL with `cannot import name 'fetch_all'`

- [ ] **Step 3: Implement fetch_all and main CLI**

Add to `.claude/scripts/fred_client.py`:

```python
def fetch_all(indicator_ids: list[str], api_key: str) -> dict:
    """
    Fetch multiple indicators from FRED API.

    Returns the complete output structure with indicators and errors.
    """
    now = datetime.now(timezone.utc).isoformat()
    indicators = []
    errors = []

    for ind_id in indicator_ids:
        if ind_id not in SERIES_MAP:
            errors.append({
                "id": ind_id,
                "series_id": None,
                "error": f"Unknown indicator: {ind_id}",
                "timestamp": now,
            })
            continue

        result = fetch_indicator(ind_id, api_key)
        if result:
            indicators.append(result)
        else:
            errors.append({
                "id": ind_id,
                "series_id": SERIES_MAP[ind_id]["series_id"],
                "error": "Fetch failed after retries",
                "timestamp": now,
            })

    return {
        "source": "FRED_API",
        "fetched_at": now,
        "indicators": indicators,
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch indicators from FRED API")
    parser.add_argument(
        "--indicators", required=True,
        help="Comma-separated indicator IDs (e.g., us_gdp_growth,us_cpi)",
    )
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--write", action="store_true", help="Write to --output file")
    parser.add_argument("--api-key", help="FRED API key (overrides FRED_API_KEY env var)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("FRED_API_KEY")
    if not api_key:
        print("ERROR: No API key. Set FRED_API_KEY env var or use --api-key.", file=sys.stderr)
        sys.exit(1)

    indicator_ids = [x.strip() for x in args.indicators.split(",") if x.strip()]
    result = fetch_all(indicator_ids, api_key)

    if not result["indicators"]:
        print("ERROR: All indicators failed to fetch.", file=sys.stderr)
        print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    if args.write and args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Written to {args.output} ({len(result['indicators'])} indicators, {len(result['errors'])} errors)")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor && python -m pytest tests/scripts/test_fred_client.py -v`
Expected: All 23 tests PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/scripts/fred_client.py tests/scripts/test_fred_client.py
git commit -m "feat: add fetch_all and CLI interface for fred_client"
```

---

## Chunk 2: SKILL.md and CLAUDE.md Updates

### Task 5: Update macro-collector SKILL.md

**Files:**
- Modify: `.claude/skills/macro-collector/SKILL.md`

- [ ] **Step 1: Add FRED API to source tag table**

In Step 2.3, move FRED from `[Portal]` to `[Official]`:

Change the `[Portal]` row from:
```
| `[Portal]` | Trading Economics, Yahoo Finance, FRED, MarketWatch |
```
To:
```
| `[Official]` | BLS, BEA, Federal Reserve, BOK, KOSIS, FRED API (via fred_client.py) |
| `[Portal]` | Trading Economics, Yahoo Finance, MarketWatch |
```

- [ ] **Step 2: Split Step 2.2 into 2.2a and 2.2b**

Replace the current Step 2.2 section with:

```markdown
### Step 2.2a — FRED API Collection (US indicators)

Run the FRED client script to collect US macroeconomic indicators:

\`\`\`bash
python .claude/scripts/fred_client.py \
  --indicators us_gdp_growth,us_cpi,us_pce,us_fed_rate,us_unemployment,us_10y_yield,us_2y_yield,us_yield_spread \
  --output output/data/macro/fred-data.json --write
\`\`\`

Read the output `fred-data.json`:
- **Exit code 0**: Read `fred-data.json`. Successfully fetched indicators go directly into `macro-raw.json` (they already have correct `source_tag`, `category`, `name`, etc.). Any indicator IDs listed in `errors[]` must be collected via web search in Step 2.2b.
- **Exit code 1**: Script failed entirely (bad API key, network down). Skip FRED, collect ALL US indicators via web search in Step 2.2b.

### Step 2.2b — Web Search Collection (KR + Global + FRED failures)

Collect the following via web search:
- **Always**: KR indicators (kr_gdp_growth, kr_cpi, kr_base_rate, kr_usd_fx) + Global indicators (ECB rate, BOJ rate, trade environment) + FOMC outlook (qualitative)
- **Only if FRED failed**: Any US indicators listed in `fred-data.json` `errors[]` or all US indicators if Step 2.2a exited with code 1
```

- [ ] **Step 3: Update Search Tool Priority**

Replace the Search Tool Priority list:

```markdown
**Search Tool Priority**:
1. `fred_client.py` (US indicators — via Step 2.2a, highest priority)
2. `mcp__tavily__search` (KR/Global + FRED fallback — real-time, structured)
3. `mcp__brave__search` (fallback)
4. `WebSearch` tool (Claude built-in, last resort)
5. `WebFetch` for direct URL access
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/macro-collector/SKILL.md
git commit -m "feat: add FRED API as primary source in macro-collector"
```

---

### Task 6: Update fundamentals-collector SKILL.md

**Files:**
- Modify: `.claude/skills/fundamentals-collector/SKILL.md`

- [ ] **Step 1: Split Step 4.2 into 4.2a and 4.2b**

Insert before the existing Step 4.2:

```markdown
### Step 4.2a — FRED API Collection (credit spreads)

Run the FRED client script to collect US credit spread indicators:

\`\`\`bash
python .claude/scripts/fred_client.py \
  --indicators us_ig_spread,us_hy_spread \
  --output output/data/fundamentals/fred-data.json --write
\`\`\`

Read the output `fred-data.json`:
- **Exit code 0**: Read `fred-data.json`. Successfully fetched indicators go directly into `fundamentals-raw.json` `market_metrics[]` (they already have correct `source_tag`, `market`, `name`, etc.). Any indicator IDs listed in `errors[]` must be collected via web search in Step 4.2b.
- **Exit code 1**: Script failed entirely. Skip FRED, collect credit spreads via web search in Step 4.2b.
```

Rename existing "Step 4.2" to "Step 4.2b" and add note:

```markdown
### Step 4.2b — Web Search Collection (valuations + sectors + FRED failures)

Collect via web search:
- **Always**: S&P 500 P/E, Shiller CAPE, KOSPI PER/PBR, sector performance, earnings estimates
- **Only if FRED failed**: Credit spreads (us_ig_spread, us_hy_spread) if listed in `fred-data.json` `errors[]` or if Step 4.2a exited with code 1
```

- [ ] **Step 2: Update Search Tool Priority**

```markdown
**Search Tool Priority**:
1. `fred_client.py` (credit spreads — via Step 4.2a, highest priority)
2. `mcp__tavily__search` (preferred — real-time, structured)
3. `mcp__brave__search` (fallback)
4. `WebSearch` tool (Claude built-in, last resort)
5. `WebFetch` for direct URL access
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/fundamentals-collector/SKILL.md
git commit -m "feat: add FRED API for credit spreads in fundamentals-collector"
```

---

### Task 7: Update CLAUDE.md File Path Tree

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add `.claude/scripts/` to Section 10 file path tree**

In the file path tree under `.claude/`, add after the `skills/` block:

```
    +-- scripts/
    |   +-- fred_client.py                 <- Shared FRED API client (macro + fundamentals)
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add .claude/scripts/ to file path tree in CLAUDE.md"
```

---

### Task 8: Live Integration Test

**Files:**
- No new files

- [ ] **Step 1: Set FRED_API_KEY environment variable**

Run: `export FRED_API_KEY=<your-api-key>`

- [ ] **Step 2: Run fred_client.py with a single indicator**

Run:
```bash
cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor && \
python .claude/scripts/fred_client.py --indicators us_fed_rate
```

Expected: JSON output with `source: "FRED_API"`, one indicator with `id: "us_fed_rate"`, `source_tag: "[Official]"`, a numeric value, and empty errors array.

- [ ] **Step 3: Run with all macro indicators**

Run:
```bash
python .claude/scripts/fred_client.py \
  --indicators us_gdp_growth,us_cpi,us_pce,us_fed_rate,us_unemployment,us_10y_yield,us_2y_yield,us_yield_spread \
  --output output/data/macro/fred-data.json --write
```

Expected: `Written to output/data/macro/fred-data.json (8 indicators, 0 errors)` (or close — some series may have `.` values on weekends/holidays)

- [ ] **Step 4: Run with fundamentals indicators**

Run:
```bash
python .claude/scripts/fred_client.py \
  --indicators us_ig_spread,us_hy_spread \
  --output output/data/fundamentals/fred-data.json --write
```

Expected: `Written to output/data/fundamentals/fred-data.json (2 indicators, 0 errors)`

- [ ] **Step 5: Verify output format is compatible with data_validator.py**

Run:
```bash
cat output/data/macro/fred-data.json | python -c "
import json, sys
data = json.load(sys.stdin)
for ind in data['indicators']:
    required = ['id', 'category', 'name', 'value', 'unit', 'period', 'source_tag', 'source_url', 'retrieved_at']
    missing = [f for f in required if f not in ind]
    if missing:
        print(f'FAIL: {ind[\"id\"]} missing fields: {missing}')
    else:
        print(f'OK: {ind[\"id\"]} = {ind[\"value\"]} {ind[\"unit\"]} ({ind[\"period\"]}) {ind[\"source_tag\"]}')
"
```

Expected: All indicators show `OK` with no missing fields.

- [ ] **Step 6: Run full test suite**

Run: `cd /Users/kpsfamily/코딩\ 프로젝트/investment-portfolio-advisor && python -m pytest tests/ -v`
Expected: All tests PASS (existing + new fred_client tests)
