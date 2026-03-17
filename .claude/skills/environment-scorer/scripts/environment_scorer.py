#!/usr/bin/env python3
"""
Environment Scorer — Step 7 helper script.

Computes indicator positions relative to historical ranges.
The LLM uses these positions to assign final 1-10 scores and regime classification.

Usage:
    python environment_scorer.py --validated-data <path> [--write --output-dir <path>]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


# Historical ranges from macro-indicator-ranges.md
HISTORICAL_RANGES = {
    "us_gdp_growth": {"low": -31.2, "median": 2.5, "high": 33.8},
    "us_cpi": {"low": -2.1, "median": 2.3, "high": 9.1},
    "us_pce": {"low": -1.5, "median": 1.9, "high": 7.1},
    "us_fed_rate": {"low": 0.0, "median": 1.75, "high": 5.50},
    "us_unemployment": {"low": 3.4, "median": 5.0, "high": 14.7},
    "us_10y_yield": {"low": 0.52, "median": 2.60, "high": 5.00},
    "us_2y_yield": {"low": 0.10, "median": 1.80, "high": 5.10},
    "us_yield_spread": {"low": -108, "median": 80, "high": 290},
    "kr_gdp_growth": {"low": -6.8, "median": 3.0, "high": 6.8},
    "kr_cpi": {"low": 0.3, "median": 2.3, "high": 6.3},
    "kr_base_rate": {"low": 0.50, "median": 2.50, "high": 5.25},
    "kr_usd_fx": {"low": 905, "median": 1150, "high": 1450},
    "sp500_pe": {"low": 10.0, "median": 19.5, "high": 38.0},
    "sp500_cape": {"low": 13.3, "median": 25.0, "high": 44.0},
    "kospi_per": {"low": 7.0, "median": 12.5, "high": 27.0},
    "kospi_pbr": {"low": 0.75, "median": 1.05, "high": 1.60},
    "us_ig_spread": {"low": 80, "median": 130, "high": 550},
    "us_hy_spread": {"low": 300, "median": 450, "high": 2000},
    "vix": {"low": 9.0, "median": 17.0, "high": 82.0},
    "fear_greed": {"low": 0, "median": 50, "high": 100},
    "put_call_ratio": {"low": 0.50, "median": 0.85, "high": 1.80},
    "aaii_bull": {"low": 15.0, "median": 37.5, "high": 75.0},
}

# Dimension-to-indicator mapping
DIMENSION_INDICATORS = {
    "macro_us": ["us_gdp_growth", "us_cpi", "us_pce", "us_fed_rate", "us_unemployment",
                 "us_10y_yield", "us_2y_yield", "us_yield_spread"],
    "macro_kr": ["kr_gdp_growth", "kr_cpi", "kr_base_rate", "kr_usd_fx"],
    "political": [],  # Political is qualitative, not scored by this script
    "fundamentals_us": ["sp500_pe", "sp500_cape", "us_ig_spread", "us_hy_spread"],
    "fundamentals_kr": ["kospi_per", "kospi_pbr"],
    "sentiment": ["vix", "fear_greed", "put_call_ratio", "aaii_bull"],
}


def compute_position(value: float, low: float, high: float) -> float:
    """
    Compute a value's position within historical range [0.0, 1.0].
    Clamped to [0.0, 1.0] if outside range.
    """
    if high == low:
        return 0.5
    position = (value - low) / (high - low)
    return max(0.0, min(1.0, round(position, 4)))


def score_dimension(dimension: str, indicators: list[dict]) -> dict:
    """
    Score a dimension by computing positions for each indicator.

    Returns positions and average for the LLM to use in scoring.
    """
    if not indicators:
        return {
            "positions": [],
            "average_position": None,
            "indicator_count": 0,
        }

    dim_indicator_ids = DIMENSION_INDICATORS.get(dimension, [])
    positions = []

    for ind in indicators:
        ind_id = ind["id"]
        value = ind.get("value")

        if value is None or ind_id not in HISTORICAL_RANGES:
            continue

        # Filter to only this dimension's indicators
        if dim_indicator_ids and ind_id not in dim_indicator_ids:
            continue

        ranges = HISTORICAL_RANGES[ind_id]
        position = compute_position(value, ranges["low"], ranges["high"])
        median_position = compute_position(ranges["median"], ranges["low"], ranges["high"])

        positions.append({
            "indicator_id": ind_id,
            "value": value,
            "position": position,
            "median_position": median_position,
            "relative_to_median": "above" if position > median_position else "below" if position < median_position else "at",
            "grade": ind.get("grade", "C"),
        })

    avg_position = (
        round(sum(p["position"] for p in positions) / len(positions), 4)
        if positions else None
    )

    return {
        "positions": positions,
        "average_position": avg_position,
        "indicator_count": len(positions),
    }


def compute_all_positions(validated_indicators: dict) -> dict:
    """
    Compute positions for all 6 dimensions.

    Args:
        validated_indicators: The validated_indicators dict from validated-data.json

    Returns:
        Dict with positions per dimension, ready for LLM scoring.
    """
    macro = validated_indicators.get("macro", [])
    political = validated_indicators.get("political", [])
    fundamentals = validated_indicators.get("fundamentals", [])
    sentiment = validated_indicators.get("sentiment", [])

    return {
        "macro_us": score_dimension("macro_us", macro),
        "macro_kr": score_dimension("macro_kr", macro),
        "political": {
            "positions": [],
            "average_position": None,
            "indicator_count": len(political),
            "note": "Political scoring is qualitative — handled by LLM directly",
        },
        "fundamentals_us": score_dimension("fundamentals_us", fundamentals),
        "fundamentals_kr": score_dimension("fundamentals_kr", fundamentals),
        "sentiment": score_dimension("sentiment", sentiment),
    }


def main():
    parser = argparse.ArgumentParser(description="Compute environment indicator positions")
    parser.add_argument("--validated-data", required=True, help="Path to validated-data.json")
    parser.add_argument("--write", action="store_true", help="Write positions to file")
    parser.add_argument("--output-dir", help="Output directory for positions file")
    args = parser.parse_args()

    with open(args.validated_data) as f:
        validated = json.load(f)

    result = compute_all_positions(validated.get("validated_indicators", {}))
    result["computation_timestamp"] = datetime.now(timezone.utc).isoformat()
    result["data_grade"] = validated.get("overall_data_grade", "C")

    if args.write and args.output_dir:
        out_path = os.path.join(args.output_dir, "environment-positions.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Written to {out_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
