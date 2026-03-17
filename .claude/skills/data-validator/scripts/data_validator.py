#!/usr/bin/env python3
"""
Data Validator — Step 6 of the Investment Portfolio Advisor pipeline.

Validates 4 raw data JSON files through 3-stage validation:
  1. Arithmetic consistency check
  2. Cross-reference check (multi-source comparison)
  3. Sanity check (against historical ranges)

Assigns confidence grades (A/B/C/D) to each data point.

Usage:
    python data_validator.py --output-dir <path> [--write]
    python data_validator.py --macro <file> --political <file> --fundamentals <file> --sentiment <file>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def load_indicator_ranges() -> dict:
    """Return sanity ranges per indicator ID (hardcoded from macro-indicator-ranges.md)."""
    _SANITY_RANGES = {
        "us_gdp_growth": (-35.0, 40.0),
        "us_cpi": (-5.0, 15.0),
        "us_pce": (-5.0, 12.0),
        "us_fed_rate": (0.0, 10.0),
        "us_unemployment": (0.0, 20.0),
        "us_10y_yield": (0.0, 8.0),
        "us_2y_yield": (0.0, 8.0),
        "us_yield_spread": (-200, 400),
        "kr_gdp_growth": (-10.0, 12.0),
        "kr_cpi": (-2.0, 10.0),
        "kr_base_rate": (0.0, 8.0),
        "kr_usd_fx": (800, 1800),
        "sp500_pe": (5.0, 50.0),
        "sp500_cape": (8.0, 55.0),
        "kospi_per": (4.0, 35.0),
        "kospi_pbr": (0.3, 3.0),
        "us_ig_spread": (50, 800),
        "us_hy_spread": (200, 2500),
        "vix": (5.0, 100.0),
        "fear_greed": (0, 100),
        "put_call_ratio": (0.3, 3.0),
        "aaii_bull": (0.0, 100.0),
    }
    return _SANITY_RANGES


_SANITY_RANGES = load_indicator_ranges()


def sanity_check(indicator_id: str, value: float) -> dict | None:
    """
    Check if a value falls within sanity bounds.

    Returns None if OK, or a SANITY_ALERT dict if outside bounds.
    """
    if indicator_id not in _SANITY_RANGES:
        return None

    sanity_min, sanity_max = _SANITY_RANGES[indicator_id]
    if value < sanity_min or value > sanity_max:
        return {
            "type": "SANITY_ALERT",
            "indicator_id": indicator_id,
            "value": value,
            "sanity_min": sanity_min,
            "sanity_max": sanity_max,
            "message": f"{indicator_id}={value} outside sanity range [{sanity_min}, {sanity_max}]",
        }
    return None


def check_arithmetic_consistency(indicators: list[dict]) -> list[dict]:
    """
    Layer 1: Check arithmetic consistency between related indicators.

    For portfolio-advisor, this is simpler than stock-analysis since
    we deal with macro indicators rather than financial ratios.
    Currently checks: yield spread = 10Y - 2Y
    """
    inconsistencies = []
    values = {ind["id"]: ind["value"] for ind in indicators if ind.get("value") is not None}

    # Check yield spread consistency
    if all(k in values for k in ("us_10y_yield", "us_2y_yield", "us_yield_spread")):
        calculated = (values["us_10y_yield"] - values["us_2y_yield"]) * 100  # to bps
        reported = values["us_yield_spread"]
        if abs(calculated - reported) > 20:  # 20 bps tolerance
            inconsistencies.append({
                "type": "ARITHMETIC_INCONSISTENCY",
                "indicator": "us_yield_spread",
                "reported": reported,
                "calculated": round(calculated, 1),
                "difference_bps": round(abs(calculated - reported), 1),
            })

    return inconsistencies


def cross_reference_check(indicators: list[dict]) -> list[dict]:
    """
    Layer 2: Cross-reference check.

    In Phase 1, most indicators come from single web searches.
    This layer groups by indicator ID and checks for multi-source agreement.
    """
    # Group by id
    by_id = {}
    for ind in indicators:
        ind_id = ind["id"]
        if ind_id not in by_id:
            by_id[ind_id] = []
        by_id[ind_id].append(ind)

    cross_refs = []
    for ind_id, sources in by_id.items():
        if len(sources) >= 2:
            values = [s["value"] for s in sources if s.get("value") is not None]
            if len(values) >= 2:
                avg = sum(values) / len(values)
                max_diff = max(abs(v - avg) / avg * 100 for v in values) if avg != 0 else 0
                cross_refs.append({
                    "indicator_id": ind_id,
                    "source_count": len(values),
                    "values": values,
                    "max_difference_pct": round(max_diff, 2),
                    "agreement": max_diff <= 5.0,
                })
    return cross_refs


def assign_grade(source_tag: str, source_count: int = 1, sanity_passed: bool = True) -> str:
    """
    Assign confidence grade based on source authority and verification.

    Grade A: Official government statistics + sanity passed
    Grade B: 2+ independent sources or official cross-referenced
    Grade C: Single source, sanity passed
    Grade D: Unverifiable or sanity failed
    """
    if not sanity_passed:
        return "D"
    if source_tag == "[Official]":
        return "A"
    if source_count >= 2:
        return "B"
    if source_count == 1:
        return "C"
    return "D"


def _validate_dimension_indicators(indicators: list[dict], dimension: str) -> tuple[list[dict], list[dict], list[dict]]:
    """Validate indicators for a single dimension. Returns (validated, exclusions, sanity_alerts)."""
    validated = []
    exclusions = []
    sanity_alerts = []

    for ind in indicators:
        ind_id = ind.get("id", "unknown")
        value = ind.get("value")

        if value is None:
            exclusions.append({
                "id": ind_id,
                "reason": "Value is null",
                "original_grade": "D",
            })
            continue

        # Sanity check
        alert = sanity_check(ind_id, value)
        sanity_passed = alert is None
        if alert:
            sanity_alerts.append(alert)

        # Determine source count (Phase 1: usually 1)
        source_count = 1
        source_tag = ind.get("source_tag", "")

        grade = assign_grade(source_tag, source_count, sanity_passed)

        if grade == "D":
            exclusions.append({
                "id": ind_id,
                "reason": alert["message"] if alert else "Unverifiable",
                "original_grade": "D",
            })
        else:
            validated.append({
                "id": ind_id,
                "value": value,
                "grade": grade,
                "source_tag": source_tag,
            })

    return validated, exclusions, sanity_alerts


def _validate_political(developments: list[dict]) -> tuple[list[dict], list[dict]]:
    """Validate political developments (qualitative — simpler grading)."""
    validated = []
    exclusions = []

    for dev in developments:
        dev_id = dev.get("id", "unknown")
        source_tag = dev.get("source_tag", "")
        # Political data is qualitative — grade based on source presence
        if source_tag:
            grade = "C" if source_tag == "[News]" else "B"
            validated.append({
                "id": dev_id,
                "headline": dev.get("headline", ""),
                "impact_assessment": dev.get("impact_assessment", "neutral"),
                "grade": grade,
                "source_tag": source_tag,
            })
        else:
            exclusions.append({
                "id": dev_id,
                "reason": "No source tag",
                "original_grade": "D",
            })

    return validated, exclusions


def _compute_overall_grade(all_grades: list[str]) -> str:
    """Compute overall data grade from individual grades."""
    if not all_grades:
        return "D"

    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for g in all_grades:
        grade_counts[g] = grade_counts.get(g, 0) + 1

    total = len(all_grades)
    a_b_ratio = (grade_counts["A"] + grade_counts["B"]) / total

    if a_b_ratio >= 0.8:
        return "A" if grade_counts["A"] > grade_counts["B"] else "B"
    elif a_b_ratio >= 0.5:
        return "B"
    elif grade_counts["D"] / total < 0.3:
        return "C"
    else:
        return "D"


def validate_all(
    macro: dict,
    political: dict,
    fundamentals: dict,
    sentiment: dict,
) -> dict:
    """
    Main validation entry point. Validates all 4 raw data files.

    Returns validated-data.json structure.
    """
    now = datetime.now(timezone.utc)
    all_exclusions = []
    all_sanity_alerts = []
    all_grades = []

    # Macro indicators
    macro_validated, macro_excl, macro_alerts = _validate_dimension_indicators(
        macro.get("indicators", []), "macro"
    )
    all_exclusions.extend(macro_excl)
    all_sanity_alerts.extend(macro_alerts)
    all_grades.extend(v["grade"] for v in macro_validated)

    # Political developments
    political_validated, political_excl = _validate_political(
        political.get("developments", [])
    )
    all_exclusions.extend(political_excl)
    all_grades.extend(v["grade"] for v in political_validated)

    # Fundamentals
    fund_indicators = fundamentals.get("market_metrics", [])
    fund_validated, fund_excl, fund_alerts = _validate_dimension_indicators(
        fund_indicators, "fundamentals"
    )
    all_exclusions.extend(fund_excl)
    all_sanity_alerts.extend(fund_alerts)
    all_grades.extend(v["grade"] for v in fund_validated)

    # Sentiment
    sent_validated, sent_excl, sent_alerts = _validate_dimension_indicators(
        sentiment.get("indicators", []), "sentiment"
    )
    all_exclusions.extend(sent_excl)
    all_sanity_alerts.extend(sent_alerts)
    all_grades.extend(v["grade"] for v in sent_validated)

    # Arithmetic consistency (macro only for now)
    arith_inconsistencies = check_arithmetic_consistency(macro.get("indicators", []))

    overall_grade = _compute_overall_grade(all_grades)

    return {
        "validation_timestamp": now.isoformat(),
        "overall_data_grade": overall_grade,
        "validated_indicators": {
            "macro": macro_validated,
            "political": political_validated,
            "fundamentals": fund_validated,
            "sentiment": sent_validated,
        },
        "exclusions": all_exclusions,
        "arithmetic_inconsistencies": arith_inconsistencies,
        "sanity_alerts": all_sanity_alerts,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate raw environment data")
    parser.add_argument("--output-dir", help="Path to output/ directory (reads raw files from data/)")
    parser.add_argument("--macro", help="Path to macro-raw.json")
    parser.add_argument("--political", help="Path to political-raw.json")
    parser.add_argument("--fundamentals", help="Path to fundamentals-raw.json")
    parser.add_argument("--sentiment", help="Path to sentiment-raw.json")
    parser.add_argument("--write", action="store_true", help="Write to validated-data.json")
    args = parser.parse_args()

    if args.output_dir:
        base = args.output_dir
        paths = {
            "macro": os.path.join(base, "data/macro/macro-raw.json"),
            "political": os.path.join(base, "data/political/political-raw.json"),
            "fundamentals": os.path.join(base, "data/fundamentals/fundamentals-raw.json"),
            "sentiment": os.path.join(base, "data/sentiment/sentiment-raw.json"),
        }
    else:
        paths = {
            "macro": args.macro,
            "political": args.political,
            "fundamentals": args.fundamentals,
            "sentiment": args.sentiment,
        }

    data = {}
    for key, path in paths.items():
        if path and os.path.exists(path):
            with open(path) as f:
                data[key] = json.load(f)
        else:
            data[key] = {"indicators": [], "developments": [], "market_metrics": [], "collection_gaps": []}

    result = validate_all(**data)

    if args.write and args.output_dir:
        out_path = os.path.join(args.output_dir, "validated-data.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Written to {out_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
