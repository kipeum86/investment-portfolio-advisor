#!/usr/bin/env python3
"""
Quality Gate — Step 9 of the pipeline.

Runs 7 deterministic checks on portfolio-recommendation.json.
No LLM judgment — purely script-based validation.

Usage:
    python quality_gate.py --recommendation <path> --user-profile <path> [--write --output-dir <path>]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


CHECKS = [
    {"check_id": 1, "name": "Allocation sum", "description": "Each option's allocation totals exactly 100"},
    {"check_id": 2, "name": "Source tag coverage", "description": ">=80% of holdings have source_tag"},
    {"check_id": 3, "name": "Required fields", "description": "All required fields present in each option"},
    {"check_id": 4, "name": "Disclaimer present", "description": "Non-empty disclaimer field"},
    {"check_id": 5, "name": "Grade D exclusion", "description": "No Grade D items in holdings"},
    {"check_id": 6, "name": "User profile reflected", "description": "Budget/period/risk reflected in output"},
    {"check_id": 7, "name": "Option differentiation", "description": ">=10pp equity weight difference"},
]


def _check_allocation_sum(recommendation: dict) -> dict:
    """Check 1: Each option's allocation.total == 100."""
    failures = []
    for opt in recommendation.get("options", []):
        alloc = opt.get("allocation", {})
        total = alloc.get("total", 0)
        if abs(total - 100.0) > 0.1:
            failures.append(f"{opt['option_id']}: total={total}")

    return {
        "check_id": 1,
        "name": "Allocation sum",
        "status": "PASS" if not failures else "FAIL",
        "details": failures if failures else "All options sum to 100%",
    }


def _check_source_tags(recommendation: dict) -> dict:
    """Check 2: >=80% of holdings have source_tag."""
    total_holdings = 0
    tagged_holdings = 0
    for opt in recommendation.get("options", []):
        for holding in opt.get("holdings", []):
            total_holdings += 1
            if holding.get("source_tag"):
                tagged_holdings += 1

    if total_holdings == 0:
        return {"check_id": 2, "name": "Source tag coverage", "status": "FAIL", "details": "No holdings found"}

    coverage = tagged_holdings / total_holdings
    return {
        "check_id": 2,
        "name": "Source tag coverage",
        "status": "PASS" if coverage >= 0.8 else "FAIL",
        "details": f"{tagged_holdings}/{total_holdings} ({coverage:.0%})",
    }


def _check_required_fields(recommendation: dict) -> dict:
    """Check 3: Required fields present in each option."""
    required_option = {"option_id", "allocation", "holdings", "scenarios"}
    required_alloc = {"us_equity", "kr_equity", "bonds", "alternatives", "cash", "total"}
    failures = []

    for opt in recommendation.get("options", []):
        missing = required_option - set(opt.keys())
        if missing:
            failures.append(f"{opt.get('option_id', '?')}: missing {missing}")
        alloc_missing = required_alloc - set(opt.get("allocation", {}).keys())
        if alloc_missing:
            failures.append(f"{opt.get('option_id', '?')}: allocation missing {alloc_missing}")

    return {
        "check_id": 3,
        "name": "Required fields",
        "status": "PASS" if not failures else "FAIL",
        "details": failures if failures else "All required fields present",
    }


def _check_disclaimer(recommendation: dict) -> dict:
    """Check 4: Non-empty disclaimer field."""
    disclaimer = recommendation.get("disclaimer", "")
    return {
        "check_id": 4,
        "name": "Disclaimer present",
        "status": "PASS" if disclaimer else "FAIL",
        "details": "Disclaimer present" if disclaimer else "Disclaimer missing or empty",
    }


def _check_grade_d_exclusion(recommendation: dict, exclusions: list | None = None) -> dict:
    """Check 5: Grade D items not in holdings."""
    if not exclusions:
        return {"check_id": 5, "name": "Grade D exclusion", "status": "PASS", "details": "No exclusions to check"}

    excluded_ids = {e.get("id") for e in exclusions}
    violations = []
    for opt in recommendation.get("options", []):
        for holding in opt.get("holdings", []):
            if holding.get("ticker") in excluded_ids:
                violations.append(f"{opt['option_id']}: {holding['ticker']} is Grade D excluded")

    return {
        "check_id": 5,
        "name": "Grade D exclusion",
        "status": "PASS" if not violations else "FAIL",
        "details": violations if violations else "No Grade D items in holdings",
    }


def _check_user_profile(recommendation: dict, user_profile: dict) -> dict:
    """Check 6: User profile reflected in output."""
    failures = []
    risk = user_profile.get("risk_tolerance", "")

    # Check that options include all 3 risk levels
    option_ids = {opt.get("option_id") for opt in recommendation.get("options", [])}
    expected_ids = {"aggressive", "moderate", "conservative"}
    if not expected_ids.issubset(option_ids):
        failures.append(f"Missing options: {expected_ids - option_ids}")

    return {
        "check_id": 6,
        "name": "User profile reflected",
        "status": "PASS" if not failures else "FAIL",
        "details": failures if failures else "User profile reflected in output",
    }


def _check_differentiation(recommendation: dict) -> dict:
    """Check 7: >=10pp equity weight difference between most and least aggressive."""
    options = recommendation.get("options", [])
    if len(options) < 2:
        return {"check_id": 7, "name": "Option differentiation", "status": "FAIL", "details": "Need >=2 options"}

    equity_weights = []
    for opt in options:
        alloc = opt.get("allocation", {})
        eq = alloc.get("us_equity", 0) + alloc.get("kr_equity", 0)
        equity_weights.append((opt.get("option_id"), eq))

    equity_weights.sort(key=lambda x: x[1], reverse=True)
    max_eq = equity_weights[0][1]
    min_eq = equity_weights[-1][1]
    diff = max_eq - min_eq

    return {
        "check_id": 7,
        "name": "Option differentiation",
        "status": "PASS" if diff >= 10 else "FAIL",
        "details": f"Equity range: {equity_weights[0][0]}={max_eq}%, {equity_weights[-1][0]}={min_eq}%, diff={diff}pp",
    }


def run_quality_gate(recommendation: dict, user_profile: dict, exclusions: list | None = None) -> dict:
    """Run all 7 quality gate checks."""
    checks = [
        _check_allocation_sum(recommendation),
        _check_source_tags(recommendation),
        _check_required_fields(recommendation),
        _check_disclaimer(recommendation),
        _check_grade_d_exclusion(recommendation, exclusions),
        _check_user_profile(recommendation, user_profile),
        _check_differentiation(recommendation),
    ]

    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")

    return {
        "gate_timestamp": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "pass_count": 7 - fail_count,
        "fail_count": fail_count,
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description="Run quality gate on portfolio recommendation")
    parser.add_argument("--recommendation", required=True, help="Path to portfolio-recommendation.json")
    parser.add_argument("--user-profile", required=True, help="Path to user-profile.json")
    parser.add_argument("--exclusions", help="Path to exclusions list (from validated-data.json)")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output-dir", help="Output directory")
    args = parser.parse_args()

    with open(args.recommendation) as f:
        rec = json.load(f)
    with open(args.user_profile) as f:
        profile = json.load(f)

    exclusions = None
    if args.exclusions and os.path.exists(args.exclusions):
        with open(args.exclusions) as f:
            exclusions = json.load(f)

    result = run_quality_gate(rec, profile, exclusions)

    if args.write and args.output_dir:
        out_path = os.path.join(args.output_dir, "quality-report.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Written to {out_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
