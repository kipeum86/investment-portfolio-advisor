"""Tests for return-estimator.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/agents/portfolio-analyst/scripts"))

from return_estimator import (
    estimate_portfolio_return,
    compute_risk_return_score,
    validate_scenario_probabilities,
)


SAMPLE_ALLOCATION = {
    "us_equity": 45,
    "kr_equity": 15,
    "bonds": 25,
    "alternatives": 10,
    "cash": 5,
    "total": 100,
}

SAMPLE_RETURN_ASSUMPTIONS = {
    "bull": {
        "us_equity": 18.0,
        "kr_equity": 22.0,
        "bonds": 5.0,
        "alternatives": 12.0,
        "cash": 4.0,
    },
    "base": {
        "us_equity": 8.0,
        "kr_equity": 6.0,
        "bonds": 3.5,
        "alternatives": 5.0,
        "cash": 3.0,
    },
    "bear": {
        "us_equity": -12.0,
        "kr_equity": -18.0,
        "bonds": 2.0,
        "alternatives": -5.0,
        "cash": 2.0,
    },
}

SAMPLE_PROBABILITIES = {"bull": 25, "base": 50, "bear": 25}


class TestValidateScenarioProbabilities:
    def test_valid_probabilities(self):
        assert validate_scenario_probabilities({"bull": 25, "base": 50, "bear": 25}) is True

    def test_sum_not_100(self):
        assert validate_scenario_probabilities({"bull": 30, "base": 50, "bear": 25}) is False

    def test_negative_probability(self):
        assert validate_scenario_probabilities({"bull": -10, "base": 60, "bear": 50}) is False


class TestEstimatePortfolioReturn:
    def test_returns_three_scenarios(self):
        result = estimate_portfolio_return(
            SAMPLE_ALLOCATION, SAMPLE_RETURN_ASSUMPTIONS, SAMPLE_PROBABILITIES
        )
        assert "bull" in result["scenarios"]
        assert "base" in result["scenarios"]
        assert "bear" in result["scenarios"]

    def test_weighted_return_computed(self):
        result = estimate_portfolio_return(
            SAMPLE_ALLOCATION, SAMPLE_RETURN_ASSUMPTIONS, SAMPLE_PROBABILITIES
        )
        bull_return = result["scenarios"]["bull"]["expected_return"]
        # Weighted: 45*18 + 15*22 + 25*5 + 10*12 + 5*4 = 810+330+125+120+20 = 1405 / 100 = 14.05
        assert abs(bull_return - 14.05) < 0.1

    def test_probability_preserved(self):
        result = estimate_portfolio_return(
            SAMPLE_ALLOCATION, SAMPLE_RETURN_ASSUMPTIONS, SAMPLE_PROBABILITIES
        )
        total_prob = sum(
            s["probability"] for s in result["scenarios"].values()
        )
        assert total_prob == 100


class TestComputeRiskReturnScore:
    def test_positive_score(self):
        scenarios = {
            "bull": {"expected_return": 15.0, "probability": 25},
            "base": {"expected_return": 7.0, "probability": 50},
            "bear": {"expected_return": -10.0, "probability": 25},
        }
        score = compute_risk_return_score(scenarios)
        # weighted_return = 15*0.25 + 7*0.50 = 3.75 + 3.50 = 7.25
        # weighted_loss = |-10*0.25| = 2.50
        # score = 7.25 / 2.50 = 2.90
        assert abs(score - 2.90) < 0.1

    def test_zero_loss_returns_max(self):
        scenarios = {
            "bull": {"expected_return": 10.0, "probability": 25},
            "base": {"expected_return": 5.0, "probability": 50},
            "bear": {"expected_return": 1.0, "probability": 25},
        }
        score = compute_risk_return_score(scenarios)
        assert score == 99.99  # Capped at max
