"""Tests for fred_client.py"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/scripts"))


# --- Period formatting tests ---

def test_format_period_quarterly():
    from fred_client import format_period
    assert format_period("2025-10-01", "A191RL1Q225SBEA") == "Q4 2025"

def test_format_period_quarterly_q1():
    from fred_client import format_period
    assert format_period("2026-01-01", "A191RL1Q225SBEA") == "Q1 2026"

def test_format_period_monthly():
    from fred_client import format_period
    assert format_period("2026-02-01", "CPIAUCSL") == "Feb 2026"

def test_format_period_daily():
    from fred_client import format_period
    assert format_period("2026-03-24", "DGS10") == "2026-03-24"


# --- Transform tests ---

def test_apply_transform_none():
    from fred_client import apply_transform
    assert apply_transform(2.3, None) == 2.3

def test_apply_transform_multiply_100():
    from fred_client import apply_transform
    assert apply_transform(0.42, "multiply_100") == 42.0

def test_apply_transform_multiply_100_negative():
    from fred_client import apply_transform
    assert apply_transform(-1.08, "multiply_100") == -108.0


# --- SERIES_MAP completeness ---

def test_series_map_has_all_macro_indicators():
    from fred_client import SERIES_MAP
    macro_ids = [
        "us_gdp_growth", "us_cpi", "us_pce", "us_fed_rate",
        "us_unemployment", "us_10y_yield", "us_2y_yield", "us_yield_spread",
    ]
    for ind_id in macro_ids:
        assert ind_id in SERIES_MAP, f"Missing macro indicator: {ind_id}"
        assert "category" in SERIES_MAP[ind_id], f"Missing category for {ind_id}"
        assert SERIES_MAP[ind_id]["category"] == "us"

def test_series_map_has_all_fundamentals_indicators():
    from fred_client import SERIES_MAP
    fund_ids = ["us_ig_spread", "us_hy_spread"]
    for ind_id in fund_ids:
        assert ind_id in SERIES_MAP, f"Missing fundamentals indicator: {ind_id}"
        assert "market" in SERIES_MAP[ind_id], f"Missing market for {ind_id}"
        assert SERIES_MAP[ind_id]["market"] == "us"

def test_series_map_entries_have_required_fields():
    from fred_client import SERIES_MAP
    required = {"series_id", "name", "unit", "transform", "api_units"}
    for ind_id, config in SERIES_MAP.items():
        for field in required:
            assert field in config, f"Missing {field} in SERIES_MAP[{ind_id}]"
