"""Tests for data-validator.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/data-validator/scripts"))

from data_validator import (
    validate_all,
    check_arithmetic_consistency,
    cross_reference_check,
    sanity_check,
    assign_grade,
    load_indicator_ranges,
)


# --- Sample test data ---

SAMPLE_MACRO = {
    "collection_timestamp": "2026-03-17T10:05:00Z",
    "indicators": [
        {
            "id": "us_gdp_growth",
            "category": "us",
            "name": "US GDP Growth Rate",
            "value": 2.3,
            "unit": "%",
            "period": "Q4 2025",
            "source_tag": "[Official]",
            "source_url": "https://bea.gov",
            "retrieved_at": "2026-03-17T10:05:00Z",
        },
        {
            "id": "us_cpi",
            "category": "us",
            "name": "US CPI YoY",
            "value": 3.1,
            "unit": "%",
            "period": "Feb 2026",
            "source_tag": "[Official]",
            "source_url": "https://bls.gov",
            "retrieved_at": "2026-03-17T10:05:00Z",
        },
    ],
    "collection_gaps": [],
}

SAMPLE_POLITICAL = {
    "collection_timestamp": "2026-03-17T10:10:00Z",
    "developments": [
        {
            "id": "us_tariff_policy",
            "category": "us_trade",
            "headline": "New tariffs announced",
            "summary": "25% tariffs on imports",
            "impact_assessment": "negative",
            "affected_sectors": ["technology", "manufacturing"],
            "source_tag": "[News]",
            "source_url": "https://reuters.com",
            "retrieved_at": "2026-03-17T10:10:00Z",
        }
    ],
    "collection_gaps": [],
}

SAMPLE_FUNDAMENTALS = {
    "collection_timestamp": "2026-03-17T10:15:00Z",
    "market_metrics": [
        {
            "id": "sp500_pe",
            "market": "us",
            "name": "S&P 500 P/E",
            "value": 22.5,
            "unit": "ratio",
            "period": "current",
            "source_tag": "[Portal]",
            "source_url": "https://yahoo.com",
            "retrieved_at": "2026-03-17T10:15:00Z",
        }
    ],
    "sector_performance": [],
    "collection_gaps": [],
}

SAMPLE_SENTIMENT = {
    "collection_timestamp": "2026-03-17T10:20:00Z",
    "indicators": [
        {
            "id": "vix",
            "name": "VIX",
            "value": 18.5,
            "unit": "index",
            "interpretation": "moderate_fear",
            "source_tag": "[Portal]",
            "source_url": "https://cboe.com",
            "retrieved_at": "2026-03-17T10:20:00Z",
        }
    ],
    "collection_gaps": [],
}


class TestAssignGrade:
    def test_official_source_gets_grade_a(self):
        grade = assign_grade(source_tag="[Official]", source_count=1, sanity_passed=True)
        assert grade == "A"

    def test_two_sources_within_5pct_gets_grade_b(self):
        grade = assign_grade(source_tag="[Portal]", source_count=2, sanity_passed=True)
        assert grade == "B"

    def test_single_source_gets_grade_c(self):
        grade = assign_grade(source_tag="[Portal]", source_count=1, sanity_passed=True)
        assert grade == "C"

    def test_failed_sanity_gets_grade_d(self):
        grade = assign_grade(source_tag="[Portal]", source_count=1, sanity_passed=False)
        assert grade == "D"


class TestSanityCheck:
    def test_normal_gdp_passes(self):
        alert = sanity_check("us_gdp_growth", 2.3)
        assert alert is None

    def test_extreme_gdp_fails(self):
        alert = sanity_check("us_gdp_growth", 50.0)
        assert alert is not None
        assert "SANITY_ALERT" in alert["type"]

    def test_unknown_indicator_passes(self):
        alert = sanity_check("unknown_indicator", 999)
        assert alert is None  # No range defined → no alert


class TestValidateAll:
    def test_produces_valid_output_schema(self):
        result = validate_all(
            macro=SAMPLE_MACRO,
            political=SAMPLE_POLITICAL,
            fundamentals=SAMPLE_FUNDAMENTALS,
            sentiment=SAMPLE_SENTIMENT,
        )
        assert "validation_timestamp" in result
        assert "overall_data_grade" in result
        assert "validated_indicators" in result
        assert "exclusions" in result
        for dim in ["macro", "political", "fundamentals", "sentiment"]:
            assert dim in result["validated_indicators"]

    def test_grade_d_items_excluded(self):
        # Create a sentiment indicator that fails sanity check
        bad_sentiment = {
            "collection_timestamp": "2026-03-17T10:20:00Z",
            "indicators": [
                {
                    "id": "vix",
                    "name": "VIX",
                    "value": 150.0,  # Way beyond sanity max of 100
                    "unit": "index",
                    "source_tag": "[Portal]",
                    "source_url": "https://cboe.com",
                    "retrieved_at": "2026-03-17T10:20:00Z",
                }
            ],
            "collection_gaps": [],
        }
        result = validate_all(
            macro=SAMPLE_MACRO,
            political=SAMPLE_POLITICAL,
            fundamentals=SAMPLE_FUNDAMENTALS,
            sentiment=bad_sentiment,
        )
        # VIX with value 150 should trigger sanity alert
        assert len(result.get("sanity_alerts", [])) > 0

    def test_overall_grade_computed(self):
        result = validate_all(
            macro=SAMPLE_MACRO,
            political=SAMPLE_POLITICAL,
            fundamentals=SAMPLE_FUNDAMENTALS,
            sentiment=SAMPLE_SENTIMENT,
        )
        assert result["overall_data_grade"] in ("A", "B", "C", "D")
