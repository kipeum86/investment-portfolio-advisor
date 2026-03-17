#!/usr/bin/env python3
"""
Return Estimator — Step 8 (Stage 6) of the pipeline.

Computes expected portfolio returns per scenario using allocation weights
and per-asset return assumptions (provided by LLM).

Usage:
    python return_estimator.py --allocation <json> --returns <json> --probabilities <json>
"""

import argparse
import json
import sys


def validate_scenario_probabilities(probabilities: dict) -> bool:
    """Validate that scenario probabilities sum to 100 and are non-negative."""
    if any(p < 0 for p in probabilities.values()):
        return False
    return abs(sum(probabilities.values()) - 100) < 1


def estimate_portfolio_return(
    allocation: dict,
    return_assumptions: dict,
    probabilities: dict,
) -> dict:
    """
    Calculate weighted portfolio return for each scenario.

    Args:
        allocation: Asset class weights (e.g., {"us_equity": 45, ...})
        return_assumptions: Per-scenario, per-asset returns (%)
            e.g., {"bull": {"us_equity": 18.0, ...}, ...}
        probabilities: Per-scenario probabilities (%)
            e.g., {"bull": 25, "base": 50, "bear": 25}

    Returns:
        Dict with per-scenario expected returns and probabilities.
    """
    asset_classes = [k for k in allocation if k != "total"]
    scenarios = {}

    for scenario in ["bull", "base", "bear"]:
        assumptions = return_assumptions.get(scenario, {})
        weighted_return = 0.0

        for asset_class in asset_classes:
            weight = allocation.get(asset_class, 0) / 100.0  # Convert % to decimal
            asset_return = assumptions.get(asset_class, 0)
            weighted_return += weight * asset_return

        scenarios[scenario] = {
            "expected_return": round(weighted_return, 2),
            "probability": probabilities.get(scenario, 0),
            "per_asset_returns": {
                ac: assumptions.get(ac, 0) for ac in asset_classes
            },
        }

    return {
        "scenarios": scenarios,
        "risk_return_score": compute_risk_return_score(scenarios),
    }


def compute_risk_return_score(scenarios: dict) -> float:
    """
    Compute Risk/Return score.

    R/R = (bull_return * bull_prob + base_return * base_prob) / |bear_return * bear_prob|

    Returns capped at 99.99 if bear loss is near zero.
    """
    bull = scenarios.get("bull", {})
    base = scenarios.get("base", {})
    bear = scenarios.get("bear", {})

    bull_return = bull.get("expected_return", 0)
    base_return = base.get("expected_return", 0)
    bear_return = bear.get("expected_return", 0)

    bull_prob = bull.get("probability", 25) / 100.0
    base_prob = base.get("probability", 50) / 100.0
    bear_prob = bear.get("probability", 25) / 100.0

    weighted_upside = (bull_return * bull_prob) + (base_return * base_prob)
    weighted_downside = abs(bear_return * bear_prob) if bear_return < 0 else 0.0

    if weighted_downside < 0.01:
        return 99.99  # Cap when no meaningful downside

    return round(weighted_upside / weighted_downside, 2)


def main():
    parser = argparse.ArgumentParser(description="Estimate portfolio returns per scenario")
    parser.add_argument("--allocation", required=True, help="JSON string or file path for allocation")
    parser.add_argument("--returns", required=True, help="JSON string or file path for return assumptions")
    parser.add_argument("--probabilities", required=True, help="JSON string or file path for probabilities")
    args = parser.parse_args()

    def load_json(val):
        if val.startswith("{"):
            return json.loads(val)
        with open(val) as f:
            return json.load(f)

    allocation = load_json(args.allocation)
    returns = load_json(args.returns)
    probs = load_json(args.probabilities)

    result = estimate_portfolio_return(allocation, returns, probs)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
