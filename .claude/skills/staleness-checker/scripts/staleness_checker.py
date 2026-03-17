#!/usr/bin/env python3
"""
Staleness Checker — Step 0 of the Investment Portfolio Advisor pipeline.

Checks existing environment data freshness and determines per-dimension
REUSE/FULL routing decisions.

Usage:
    python staleness_checker.py --output-dir <path_to_output_dir>
    python staleness_checker.py --output-dir output/ --write

Output: JSON routing decision to stdout (or writes to output/staleness-routing.json with --write)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta


STALENESS_RULES = {
    "macro": {
        "threshold_hours": 24,
        "description": "Macroeconomic data",
    },
    "political": {
        "threshold_hours": 168,  # 7 days
        "description": "Political/geopolitical data",
    },
    "fundamentals": {
        "threshold_hours": 72,  # 3 days
        "description": "Market fundamentals data",
    },
    "sentiment": {
        "threshold_hours": 12,
        "description": "Market sentiment data",
    },
}

DIMENSION_FILE_MAP = {
    "macro": "data/macro/latest.json",
    "political": "data/political/latest.json",
    "fundamentals": "data/fundamentals/latest.json",
    "sentiment": "data/sentiment/latest.json",
}


def _read_timestamp(filepath: str) -> datetime | None:
    """Read collection_timestamp from a latest.json file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        ts_str = data.get("collection_timestamp")
        if not ts_str:
            return None
        return datetime.fromisoformat(ts_str)
    except (json.JSONDecodeError, FileNotFoundError, KeyError, ValueError):
        return None


def check_staleness(output_dir: str) -> dict:
    """
    Check staleness of all 4 dimensions.

    Args:
        output_dir: Path to the output directory containing data/ subdirectories.

    Returns:
        dict with routing decisions per dimension.
    """
    now = datetime.now(timezone.utc)
    dimensions = {}

    for dim, rule in STALENESS_RULES.items():
        filepath = os.path.join(output_dir, DIMENSION_FILE_MAP[dim])
        timestamp = _read_timestamp(filepath)

        if timestamp is None:
            dimensions[dim] = {
                "routing": "FULL",
                "reason": "No existing data found",
                "last_collected": None,
                "age_hours": None,
                "threshold_hours": rule["threshold_hours"],
            }
        else:
            # Ensure timezone-aware comparison
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            age = now - timestamp
            age_hours = age.total_seconds() / 3600

            if age_hours < rule["threshold_hours"]:
                routing = "REUSE"
                reason = f"Data is {age_hours:.1f}h old (threshold: {rule['threshold_hours']}h)"
            else:
                routing = "FULL"
                reason = f"Data is {age_hours:.1f}h old, exceeds threshold of {rule['threshold_hours']}h"

            dimensions[dim] = {
                "routing": routing,
                "reason": reason,
                "last_collected": timestamp.isoformat(),
                "age_hours": round(age_hours, 1),
                "threshold_hours": rule["threshold_hours"],
            }

    return {
        "check_timestamp": now.isoformat(),
        "dimensions": dimensions,
    }


def main():
    parser = argparse.ArgumentParser(description="Check data staleness for environment dimensions")
    parser.add_argument("--output-dir", required=True, help="Path to output/ directory")
    parser.add_argument("--write", action="store_true", help="Write result to staleness-routing.json")
    args = parser.parse_args()

    result = check_staleness(args.output_dir)

    if args.write:
        out_path = os.path.join(args.output_dir, "staleness-routing.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Written to {out_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
