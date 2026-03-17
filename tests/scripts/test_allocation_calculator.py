"""Tests for allocation-calculator.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/agents/portfolio-analyst/scripts"))

from allocation_calculator import (
    get_base_allocation,
    apply_risk_adjustment,
    apply_horizon_adjustment,
    normalize_allocation,
    calculate_allocation,
    REGIME_RANGES,
)


class TestGetBaseAllocation:
    def test_mid_cycle_returns_ranges(self):
        ranges = get_base_allocation("mid-cycle")
        assert "us_equity" in ranges
        assert ranges["us_equity"] == (40, 55)
        assert ranges["kr_equity"] == (10, 15)

    def test_unknown_regime_raises(self):
        try:
            get_base_allocation("unknown")
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_all_regimes_defined(self):
        for regime in ["early-expansion", "mid-cycle", "late-cycle", "recession", "recovery"]:
            ranges = get_base_allocation(regime)
            assert len(ranges) == 5


class TestApplyRiskAdjustment:
    def test_aggressive_uses_upper_equity(self):
        ranges = {"us_equity": (40, 55), "kr_equity": (10, 15),
                  "bonds": (20, 30), "alternatives": (5, 10), "cash": (5, 10)}
        alloc = apply_risk_adjustment(ranges, "aggressive")
        assert alloc["us_equity"] == 55  # upper bound
        assert alloc["bonds"] == 20      # lower bound for defensive
        assert alloc["cash"] == 5        # lower bound

    def test_conservative_uses_lower_equity(self):
        ranges = {"us_equity": (40, 55), "kr_equity": (10, 15),
                  "bonds": (20, 30), "alternatives": (5, 10), "cash": (5, 10)}
        alloc = apply_risk_adjustment(ranges, "conservative")
        assert alloc["us_equity"] == 40  # lower bound
        assert alloc["bonds"] == 30      # upper bound for defensive
        assert alloc["cash"] == 10       # upper bound

    def test_moderate_uses_midpoint(self):
        ranges = {"us_equity": (40, 55), "kr_equity": (10, 15),
                  "bonds": (20, 30), "alternatives": (5, 10), "cash": (5, 10)}
        alloc = apply_risk_adjustment(ranges, "moderate")
        assert alloc["us_equity"] == 47.5  # midpoint


class TestApplyHorizonAdjustment:
    def test_short_horizon_adds_cash(self):
        alloc = {"us_equity": 50, "kr_equity": 10, "bonds": 25, "alternatives": 5, "cash": 10}
        adjusted = apply_horizon_adjustment(alloc, "short")
        assert adjusted["cash"] == 20    # +10
        assert adjusted["us_equity"] == 45  # -5
        assert adjusted["kr_equity"] == 5   # -5

    def test_medium_no_change(self):
        alloc = {"us_equity": 50, "kr_equity": 10, "bonds": 25, "alternatives": 5, "cash": 10}
        adjusted = apply_horizon_adjustment(alloc, "medium")
        assert adjusted == alloc

    def test_long_horizon_adds_equity(self):
        alloc = {"us_equity": 50, "kr_equity": 10, "bonds": 25, "alternatives": 5, "cash": 10}
        adjusted = apply_horizon_adjustment(alloc, "long")
        assert adjusted["us_equity"] == 55   # +5
        assert adjusted["kr_equity"] == 15   # +5
        assert adjusted["bonds"] == 20       # -5
        assert adjusted["cash"] == 5         # -5

    def test_no_negative_values(self):
        alloc = {"us_equity": 30, "kr_equity": 5, "bonds": 25, "alternatives": 5, "cash": 2}
        adjusted = apply_horizon_adjustment(alloc, "short")
        for v in adjusted.values():
            assert v >= 0


class TestNormalizeAllocation:
    def test_already_100_no_change(self):
        alloc = {"us_equity": 50, "kr_equity": 10, "bonds": 25, "alternatives": 5, "cash": 10}
        norm = normalize_allocation(alloc)
        assert sum(norm.values()) == 100.0

    def test_normalizes_over_100(self):
        alloc = {"us_equity": 55, "kr_equity": 15, "bonds": 20, "alternatives": 5, "cash": 10}
        # sum = 105
        norm = normalize_allocation(alloc)
        assert abs(sum(norm.values()) - 100.0) < 0.01

    def test_normalizes_under_100(self):
        alloc = {"us_equity": 40, "kr_equity": 10, "bonds": 20, "alternatives": 5, "cash": 5}
        # sum = 80
        norm = normalize_allocation(alloc)
        assert abs(sum(norm.values()) - 100.0) < 0.01


class TestCalculateAllocation:
    def test_full_pipeline(self):
        result = calculate_allocation("mid-cycle", "moderate", "medium")
        assert "allocation" in result
        assert abs(result["allocation"]["total"] - 100.0) < 0.01
        assert result["regime"] == "mid-cycle"
        assert result["risk_tolerance"] == "moderate"

    def test_three_options_differentiated(self):
        agg = calculate_allocation("mid-cycle", "aggressive", "medium")
        mod = calculate_allocation("mid-cycle", "moderate", "medium")
        con = calculate_allocation("mid-cycle", "conservative", "medium")

        agg_eq = agg["allocation"]["us_equity"] + agg["allocation"]["kr_equity"]
        con_eq = con["allocation"]["us_equity"] + con["allocation"]["kr_equity"]
        # At least 10pp difference
        assert agg_eq - con_eq >= 10

    def test_no_asset_exceeds_70(self):
        for regime in ["early-expansion", "mid-cycle", "late-cycle", "recession", "recovery"]:
            for risk in ["aggressive", "moderate", "conservative"]:
                result = calculate_allocation(regime, risk, "medium")
                for key, val in result["allocation"].items():
                    if key != "total":
                        assert val <= 70, f"{key}={val} exceeds 70% in {regime}/{risk}"
