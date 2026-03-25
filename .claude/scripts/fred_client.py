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
