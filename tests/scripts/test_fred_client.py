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


# --- fetch_indicator tests (mocked HTTP) ---

from unittest.mock import patch, MagicMock


def _mock_fred_response(value: str, date: str):
    """Create a mock FRED API JSON response."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "observations": [
            {"date": date, "value": value}
        ]
    }
    return resp


def _mock_fred_error(status_code: int):
    resp = MagicMock()
    resp.status_code = status_code
    resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


@patch("fred_client.requests.get")
def test_fetch_indicator_success(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response("2.3", "2025-10-01")
    result = fetch_indicator("us_gdp_growth", "test_api_key")
    assert result["id"] == "us_gdp_growth"
    assert result["value"] == 2.3
    assert result["period"] == "Q4 2025"
    assert result["source_tag"] == "[Official]"
    assert result["category"] == "us"
    assert result["name"] == "US GDP Growth Rate (QoQ annualized)"


@patch("fred_client.requests.get")
def test_fetch_indicator_with_transform(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response("0.42", "2026-03-24")
    result = fetch_indicator("us_yield_spread", "test_api_key")
    assert result["value"] == 42.0
    assert result["unit"] == "bps"


@patch("fred_client.requests.get")
def test_fetch_indicator_with_api_units(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response("3.1", "2026-02-01")
    result = fetch_indicator("us_cpi", "test_api_key")
    call_args = mock_get.call_args
    assert call_args[1]["params"]["units"] == "pc1"
    assert result["value"] == 3.1


@patch("fred_client.requests.get")
def test_fetch_indicator_empty_observations(mock_get):
    from fred_client import fetch_indicator
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"observations": []}
    mock_get.return_value = resp
    result = fetch_indicator("us_gdp_growth", "test_api_key")
    assert result is None


@patch("fred_client.requests.get")
def test_fetch_indicator_dot_value_skipped(mock_get):
    """FRED returns '.' for missing values — should skip."""
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response(".", "2026-03-24")
    result = fetch_indicator("us_10y_yield", "test_api_key")
    assert result is None


@patch("fred_client.requests.get")
def test_fetch_indicator_http_error(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_error(500)
    result = fetch_indicator("us_gdp_growth", "test_api_key")
    assert result is None


@patch("fred_client.requests.get")
def test_fetch_indicator_connection_error(mock_get):
    """ConnectionError should return None without crashing."""
    from fred_client import fetch_indicator
    mock_get.side_effect = ConnectionError("Connection refused")
    result = fetch_indicator("us_gdp_growth", "test_api_key")
    assert result is None


@patch("fred_client.requests.get")
def test_fetch_indicator_429_retries_once(mock_get):
    """429 should retry once with 1s backoff."""
    from fred_client import fetch_indicator
    mock_get.side_effect = [
        _mock_fred_error(429),
        _mock_fred_response("4.5", "2026-03-24"),
    ]
    result = fetch_indicator("us_fed_rate", "test_api_key")
    assert result is not None
    assert result["value"] == 4.5
    assert mock_get.call_count == 2


@patch("fred_client.requests.get")
def test_fetch_indicator_fundamentals_has_market_field(mock_get):
    from fred_client import fetch_indicator
    mock_get.return_value = _mock_fred_response("1.30", "2026-03-21")
    result = fetch_indicator("us_ig_spread", "test_api_key")
    assert result["market"] == "us"
    assert "category" not in result
