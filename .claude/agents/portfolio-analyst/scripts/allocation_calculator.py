#!/usr/bin/env python3
"""
Allocation Calculator — Step 8 (Stages 2-4) of the pipeline.

Computes portfolio allocations using:
  Stage 2: Regime → base allocation ranges
  Stage 3: Risk tolerance → position within ranges
  Stage 4: Horizon → adjustment + normalization

Usage:
    python allocation_calculator.py --regime <regime> --risk <risk> --horizon <horizon>
"""

import argparse
import json
import sys


REGIME_RANGES = {
    "early-expansion": {
        "us_equity": (50, 65),
        "kr_equity": (10, 20),
        "bonds": (15, 25),
        "alternatives": (5, 10),
        "cash": (0, 5),
    },
    "mid-cycle": {
        "us_equity": (40, 55),
        "kr_equity": (10, 15),
        "bonds": (20, 30),
        "alternatives": (5, 10),
        "cash": (5, 10),
    },
    "late-cycle": {
        "us_equity": (30, 45),
        "kr_equity": (5, 15),
        "bonds": (30, 40),
        "alternatives": (5, 10),
        "cash": (10, 15),
    },
    "recession": {
        "us_equity": (20, 35),
        "kr_equity": (5, 10),
        "bonds": (35, 50),
        "alternatives": (5, 10),
        "cash": (15, 25),
    },
    "recovery": {
        "us_equity": (45, 60),
        "kr_equity": (15, 20),
        "bonds": (15, 25),
        "alternatives": (5, 10),
        "cash": (5, 10),
    },
}

HORIZON_ADJUSTMENTS = {
    "short": {"us_equity": -5, "kr_equity": -5, "bonds": 0, "alternatives": 0, "cash": 10},
    "medium": {"us_equity": 0, "kr_equity": 0, "bonds": 0, "alternatives": 0, "cash": 0},
    "medium-long": {"us_equity": 3, "kr_equity": 2, "bonds": 0, "alternatives": 0, "cash": -5},
    "long": {"us_equity": 5, "kr_equity": 5, "bonds": -5, "alternatives": 0, "cash": -5},
}


def months_to_horizon(months: int) -> str:
    """Map investment_period_months to horizon string.

    Spec buckets: <6mo=short, 6-12mo=medium, 1-3yr=medium, 3-5yr=medium-long, 5+yr=long
    """
    if months < 6:
        return "short"
    elif months <= 36:
        return "medium"
    elif months <= 60:
        return "medium-long"
    else:
        return "long"


def get_base_allocation(regime: str) -> dict:
    """Stage 2: Get base allocation ranges for a regime."""
    if regime not in REGIME_RANGES:
        raise ValueError(f"Unknown regime: {regime}. Valid: {list(REGIME_RANGES.keys())}")
    return REGIME_RANGES[regime].copy()


def apply_risk_adjustment(ranges: dict, risk_tolerance: str) -> dict:
    """
    Stage 3: Position within ranges based on risk tolerance.

    Aggressive: upper equity, lower bonds/cash
    Moderate: midpoint
    Conservative: lower equity, upper bonds/cash
    """
    allocation = {}
    equity_classes = {"us_equity", "kr_equity"}
    defensive_classes = {"bonds", "cash"}

    for asset_class, (low, high) in ranges.items():
        if risk_tolerance == "aggressive":
            if asset_class in equity_classes:
                allocation[asset_class] = high
            elif asset_class in defensive_classes:
                allocation[asset_class] = low
            else:
                allocation[asset_class] = round((low + high) / 2, 1)
        elif risk_tolerance == "conservative":
            if asset_class in equity_classes:
                allocation[asset_class] = low
            elif asset_class in defensive_classes:
                allocation[asset_class] = high
            else:
                allocation[asset_class] = round((low + high) / 2, 1)
        else:  # moderate
            allocation[asset_class] = round((low + high) / 2, 1)

    return allocation


def apply_horizon_adjustment(allocation: dict, horizon: str) -> dict:
    """
    Stage 4: Adjust allocation based on investment horizon.

    Adjustments are additive. Values clamped to >= 0.
    """
    adjustments = HORIZON_ADJUSTMENTS.get(horizon, HORIZON_ADJUSTMENTS["medium"])
    adjusted = {}

    for asset_class, value in allocation.items():
        adj = adjustments.get(asset_class, 0)
        adjusted[asset_class] = max(0, round(value + adj, 1))

    return adjusted


def normalize_allocation(allocation: dict) -> dict:
    """
    Normalize allocation so total = exactly 100%.

    Distributes the delta proportionally across all non-zero classes.
    """
    total = sum(allocation.values())
    if total == 0:
        return allocation

    if abs(total - 100.0) < 0.01:
        # Close enough, just fix rounding
        normalized = {k: round(v, 1) for k, v in allocation.items()}
        diff = round(100.0 - sum(normalized.values()), 1)
        if diff != 0:
            # Add to the largest class
            largest = max(normalized, key=normalized.get)
            normalized[largest] = round(normalized[largest] + diff, 1)
        return normalized

    # Proportional scaling
    scale = 100.0 / total
    normalized = {k: round(v * scale, 1) for k, v in allocation.items()}

    # Fix rounding error
    diff = round(100.0 - sum(normalized.values()), 1)
    if diff != 0:
        largest = max(normalized, key=normalized.get)
        normalized[largest] = round(normalized[largest] + diff, 1)

    return normalized


def calculate_allocation(regime: str, risk_tolerance: str, horizon: str) -> dict:
    """
    Full allocation pipeline: regime → ranges → risk adjust → horizon adjust → normalize.

    Returns allocation dict with total = 100.
    """
    # Stage 2: Base ranges
    ranges = get_base_allocation(regime)

    # Stage 3: Risk adjustment
    allocation = apply_risk_adjustment(ranges, risk_tolerance)

    # Stage 4: Horizon adjustment
    allocation = apply_horizon_adjustment(allocation, horizon)

    # Normalize to 100%
    allocation = normalize_allocation(allocation)

    # Enforce constraints
    for key, val in allocation.items():
        if val > 70:
            overflow = val - 70
            allocation[key] = 70
            # Distribute overflow to cash
            allocation["cash"] = round(allocation.get("cash", 0) + overflow, 1)
            allocation = normalize_allocation(allocation)

    allocation["total"] = round(sum(v for k, v in allocation.items() if k != "total"), 1)

    return {
        "regime": regime,
        "risk_tolerance": risk_tolerance,
        "horizon": horizon,
        "allocation": allocation,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate portfolio allocation")
    parser.add_argument("--regime", required=True, choices=list(REGIME_RANGES.keys()))
    parser.add_argument("--risk", required=True, choices=["aggressive", "moderate", "conservative"])
    parser.add_argument("--horizon", required=True, choices=["short", "medium", "medium-long", "long"])
    args = parser.parse_args()

    result = calculate_allocation(args.regime, args.risk, args.horizon)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
