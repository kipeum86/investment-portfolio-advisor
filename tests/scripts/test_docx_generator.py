"""Tests for docx-generator.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/memo-generator/scripts"))

from docx_generator import generate_memo, create_allocation_table, create_holdings_table


SAMPLE_RECOMMENDATION = {
    "recommendation_timestamp": "2026-03-17T12:00:00Z",
    "regime": "mid-cycle",
    "options": [
        {
            "option_id": "aggressive",
            "label": "Aggressive Portfolio",
            "allocation": {"us_equity": 55, "kr_equity": 15, "bonds": 20, "alternatives": 5, "cash": 5, "total": 100},
            "holdings": [
                {"ticker": "VOO", "name": "Vanguard S&P 500", "asset_class": "us_equity", "weight": 30, "rationale": "Core", "source_tag": "[Portal]"},
                {"ticker": "QQQ", "name": "Invesco QQQ", "asset_class": "us_equity", "weight": 25, "rationale": "Growth", "source_tag": "[Portal]"},
            ],
            "scenarios": {
                "bull": {"expected_return": 18.5, "probability": 25, "assumptions": "Strong growth"},
                "base": {"expected_return": 8.0, "probability": 50, "assumptions": "Steady"},
                "bear": {"expected_return": -12.0, "probability": 25, "assumptions": "Recession"},
            },
            "risk_return_score": 2.5,
        },
    ],
    "key_risks": [{"risk": "Rising rates", "mechanism": "Rates up → Bonds down", "severity": "high"}],
    "disclaimer": "This is not investment advice.",
}

SAMPLE_ENVIRONMENT = {
    "assessment_timestamp": "2026-03-17T11:00:00Z",
    "data_grade": "B",
    "regime_classification": "mid-cycle",
    "regime_rationale": "Steady growth with moderate inflation",
}

SAMPLE_PROFILE = {
    "budget": 50000000,
    "budget_currency": "KRW",
    "investment_period_months": 12,
    "risk_tolerance": "moderate",
    "output_language": "en",
}


class TestGenerateMemo:
    def test_generates_docx_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "test_memo.docx")
            generate_memo(SAMPLE_RECOMMENDATION, SAMPLE_ENVIRONMENT, SAMPLE_PROFILE, out_path)
            assert os.path.exists(out_path)
            assert os.path.getsize(out_path) > 0

    def test_output_is_valid_docx(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "test_memo.docx")
            generate_memo(SAMPLE_RECOMMENDATION, SAMPLE_ENVIRONMENT, SAMPLE_PROFILE, out_path)
            # python-docx can open it
            from docx import Document
            doc = Document(out_path)
            assert len(doc.paragraphs) > 0


class TestCreateAllocationTable:
    def test_returns_table_data(self):
        alloc = {"us_equity": 55, "kr_equity": 15, "bonds": 20, "alternatives": 5, "cash": 5, "total": 100}
        rows = create_allocation_table(alloc)
        assert len(rows) == 5  # 5 asset classes (no total row in data)
        assert rows[0][0] == "US Equity"
        assert rows[0][1] == "55.0%"


class TestCreateHoldingsTable:
    def test_returns_table_data(self):
        holdings = [
            {"ticker": "VOO", "name": "Vanguard S&P 500", "weight": 30, "rationale": "Core", "source_tag": "[Portal]"},
        ]
        rows = create_holdings_table(holdings)
        assert len(rows) == 1
        assert rows[0][0] == "VOO"
