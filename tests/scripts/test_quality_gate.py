"""Tests for quality-gate.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/quality-gate/scripts"))

from quality_gate import run_quality_gate, CHECKS


SAMPLE_RECOMMENDATION = {
    "recommendation_timestamp": "2026-03-17T12:00:00Z",
    "user_profile_hash": "abc123",
    "regime": "mid-cycle",
    "options": [
        {
            "option_id": "aggressive",
            "allocation": {"us_equity": 55, "kr_equity": 15, "bonds": 20, "alternatives": 5, "cash": 5, "total": 100},
            "holdings": [
                {"ticker": "VOO", "asset_class": "us_equity", "weight": 25, "source_tag": "[Portal]", "rationale": "Core US"},
                {"ticker": "QQQ", "asset_class": "us_equity", "weight": 30, "source_tag": "[Portal]", "rationale": "Growth"},
                {"ticker": "KODEX200", "asset_class": "kr_equity", "weight": 15, "source_tag": "[KR-Portal]", "rationale": "KR core"},
                {"ticker": "AGG", "asset_class": "bonds", "weight": 20, "source_tag": "[Portal]", "rationale": "Bonds"},
                {"ticker": "GLD", "asset_class": "alternatives", "weight": 5, "source_tag": "[Portal]", "rationale": "Gold"},
                {"ticker": "SHV", "asset_class": "cash", "weight": 5, "source_tag": "[Portal]", "rationale": "Cash"},
            ],
            "scenarios": {
                "bull": {"expected_return": 18.5, "probability": 25},
                "base": {"expected_return": 8.0, "probability": 50},
                "bear": {"expected_return": -12.0, "probability": 25},
            },
        },
        {
            "option_id": "moderate",
            "allocation": {"us_equity": 45, "kr_equity": 10, "bonds": 27.5, "alternatives": 7.5, "cash": 10, "total": 100},
            "holdings": [
                {"ticker": "VTI", "asset_class": "us_equity", "weight": 45, "source_tag": "[Portal]", "rationale": "Broad US"},
                {"ticker": "KODEX200", "asset_class": "kr_equity", "weight": 10, "source_tag": "[KR-Portal]", "rationale": "KR"},
                {"ticker": "BND", "asset_class": "bonds", "weight": 27.5, "source_tag": "[Portal]", "rationale": "Bonds"},
                {"ticker": "IAU", "asset_class": "alternatives", "weight": 7.5, "source_tag": "[Portal]", "rationale": "Gold"},
                {"ticker": "SGOV", "asset_class": "cash", "weight": 10, "source_tag": "[Portal]", "rationale": "Cash"},
            ],
            "scenarios": {
                "bull": {"expected_return": 12.0, "probability": 25},
                "base": {"expected_return": 6.0, "probability": 50},
                "bear": {"expected_return": -8.0, "probability": 25},
            },
        },
        {
            "option_id": "conservative",
            "allocation": {"us_equity": 35, "kr_equity": 5, "bonds": 35, "alternatives": 7.5, "cash": 17.5, "total": 100},
            "holdings": [
                {"ticker": "VIG", "asset_class": "us_equity", "weight": 35, "source_tag": "[Portal]", "rationale": "Dividend"},
                {"ticker": "KODEX\ubc30\ub2f9", "asset_class": "kr_equity", "weight": 5, "source_tag": "[KR-Portal]", "rationale": "KR div"},
                {"ticker": "TLT", "asset_class": "bonds", "weight": 20, "source_tag": "[Portal]", "rationale": "Long treasury"},
                {"ticker": "SHY", "asset_class": "bonds", "weight": 15, "source_tag": "[Portal]", "rationale": "Short treasury"},
                {"ticker": "GLD", "asset_class": "alternatives", "weight": 7.5, "source_tag": "[Portal]", "rationale": "Gold"},
                {"ticker": "BIL", "asset_class": "cash", "weight": 17.5, "source_tag": "[Portal]", "rationale": "T-bills"},
            ],
            "scenarios": {
                "bull": {"expected_return": 8.0, "probability": 25},
                "base": {"expected_return": 4.5, "probability": 50},
                "bear": {"expected_return": -4.0, "probability": 25},
            },
        },
    ],
    "key_risks": [{"risk": "Rate hike", "mechanism": "Rates up \u2192 Bond prices down \u2192 Portfolio drag"}],
    "disclaimer": "This is not investment advice.",
}

SAMPLE_USER_PROFILE = {
    "budget": 50000000,
    "budget_currency": "KRW",
    "investment_period_months": 12,
    "risk_tolerance": "moderate",
}


class TestRunQualityGate:
    def test_all_checks_defined(self):
        assert len(CHECKS) == 7

    def test_valid_recommendation_passes(self):
        result = run_quality_gate(SAMPLE_RECOMMENDATION, SAMPLE_USER_PROFILE)
        assert result["overall"] == "PASS"
        assert all(c["status"] == "PASS" for c in result["checks"])

    def test_allocation_not_100_fails(self):
        bad = json.loads(json.dumps(SAMPLE_RECOMMENDATION))
        bad["options"][0]["allocation"]["total"] = 95
        bad["options"][0]["allocation"]["us_equity"] = 50
        result = run_quality_gate(bad, SAMPLE_USER_PROFILE)
        # Check 1 should fail
        check1 = next(c for c in result["checks"] if c["check_id"] == 1)
        assert check1["status"] == "FAIL"

    def test_missing_disclaimer_fails(self):
        bad = json.loads(json.dumps(SAMPLE_RECOMMENDATION))
        bad["disclaimer"] = ""
        result = run_quality_gate(bad, SAMPLE_USER_PROFILE)
        check4 = next(c for c in result["checks"] if c["check_id"] == 4)
        assert check4["status"] == "FAIL"

    def test_insufficient_differentiation_fails(self):
        bad = json.loads(json.dumps(SAMPLE_RECOMMENDATION))
        # Make all options have same equity weight
        for opt in bad["options"]:
            opt["allocation"]["us_equity"] = 45
            opt["allocation"]["kr_equity"] = 10
        result = run_quality_gate(bad, SAMPLE_USER_PROFILE)
        check7 = next(c for c in result["checks"] if c["check_id"] == 7)
        assert check7["status"] == "FAIL"
