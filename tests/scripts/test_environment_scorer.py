"""Tests for environment-scorer.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/environment-scorer/scripts"))

from environment_scorer import (
    compute_position,
    score_dimension,
    compute_all_positions,
    HISTORICAL_RANGES,
)


class TestComputePosition:
    def test_at_historical_low(self):
        pos = compute_position(9.0, low=9.0, high=82.0)
        assert pos == 0.0

    def test_at_historical_high(self):
        pos = compute_position(82.0, low=9.0, high=82.0)
        assert pos == 1.0

    def test_at_median(self):
        pos = compute_position(45.5, low=9.0, high=82.0)
        assert 0.4 < pos < 0.6

    def test_below_low_clamped(self):
        pos = compute_position(5.0, low=9.0, high=82.0)
        assert pos == 0.0

    def test_above_high_clamped(self):
        pos = compute_position(90.0, low=9.0, high=82.0)
        assert pos == 1.0


class TestScoreDimension:
    def test_returns_valid_structure(self):
        indicators = [
            {"id": "us_gdp_growth", "value": 2.3, "grade": "A"},
            {"id": "us_cpi", "value": 3.1, "grade": "B"},
            {"id": "us_fed_rate", "value": 4.5, "grade": "B"},
            {"id": "us_unemployment", "value": 4.0, "grade": "B"},
        ]
        result = score_dimension("macro_us", indicators)
        assert "positions" in result
        assert "average_position" in result
        assert "indicator_count" in result

    def test_empty_indicators_returns_null(self):
        result = score_dimension("macro_us", [])
        assert result["average_position"] is None
        assert result["indicator_count"] == 0


class TestComputeAllPositions:
    def test_returns_all_six_dimensions(self):
        validated = {
            "macro": [
                {"id": "us_gdp_growth", "value": 2.3, "grade": "A"},
                {"id": "kr_gdp_growth", "value": 2.0, "grade": "B"},
            ],
            "political": [],
            "fundamentals": [
                {"id": "sp500_pe", "value": 22.0, "grade": "B"},
                {"id": "kospi_per", "value": 12.0, "grade": "B"},
            ],
            "sentiment": [
                {"id": "vix", "value": 18.0, "grade": "B"},
            ],
        }
        result = compute_all_positions(validated)
        assert "macro_us" in result
        assert "macro_kr" in result
        assert "political" in result
        assert "fundamentals_us" in result
        assert "fundamentals_kr" in result
        assert "sentiment" in result
