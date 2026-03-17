"""Tests for staleness-checker.py"""
import json
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/staleness-checker/scripts"))

from staleness_checker import check_staleness, STALENESS_RULES


class TestStalenessRules:
    """Test staleness rule definitions."""

    def test_all_four_dimensions_defined(self):
        assert set(STALENESS_RULES.keys()) == {"macro", "political", "fundamentals", "sentiment"}

    def test_macro_threshold_24h(self):
        assert STALENESS_RULES["macro"]["threshold_hours"] == 24

    def test_political_threshold_7d(self):
        assert STALENESS_RULES["political"]["threshold_hours"] == 168  # 7 * 24

    def test_fundamentals_threshold_3d(self):
        assert STALENESS_RULES["fundamentals"]["threshold_hours"] == 72  # 3 * 24

    def test_sentiment_threshold_12h(self):
        assert STALENESS_RULES["sentiment"]["threshold_hours"] == 12


class TestCheckStaleness:
    """Test the main staleness check function."""

    def _make_latest_json(self, tmpdir, dimension, hours_ago):
        """Helper: create a latest.json file with a timestamp N hours ago."""
        dim_dir = os.path.join(tmpdir, "data", dimension)
        os.makedirs(dim_dir, exist_ok=True)
        ts = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()
        data = {"collection_timestamp": ts, "indicators": []}
        path = os.path.join(dim_dir, "latest.json")
        with open(path, "w") as f:
            json.dump(data, f)
        return path

    def test_no_existing_data_returns_all_full(self):
        """When no latest.json files exist, all dimensions should be FULL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_staleness(tmpdir)
            for dim in ["macro", "political", "fundamentals", "sentiment"]:
                assert result["dimensions"][dim]["routing"] == "FULL"

    def test_fresh_macro_returns_reuse(self):
        """Macro data < 24h old should be REUSE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "macro", hours_ago=6)
            result = check_staleness(tmpdir)
            assert result["dimensions"]["macro"]["routing"] == "REUSE"

    def test_stale_macro_returns_full(self):
        """Macro data >= 24h old should be FULL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "macro", hours_ago=25)
            result = check_staleness(tmpdir)
            assert result["dimensions"]["macro"]["routing"] == "FULL"

    def test_fresh_political_7_days(self):
        """Political data < 7 days old should be REUSE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "political", hours_ago=120)  # 5 days
            result = check_staleness(tmpdir)
            assert result["dimensions"]["political"]["routing"] == "REUSE"

    def test_stale_political(self):
        """Political data >= 7 days old should be FULL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "political", hours_ago=170)  # 7+ days
            result = check_staleness(tmpdir)
            assert result["dimensions"]["political"]["routing"] == "FULL"

    def test_mixed_staleness(self):
        """Different dimensions can have different routing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_latest_json(tmpdir, "macro", hours_ago=6)       # REUSE
            self._make_latest_json(tmpdir, "political", hours_ago=200) # FULL
            self._make_latest_json(tmpdir, "fundamentals", hours_ago=48) # FULL (>72h? no, 48<72)
            # sentiment: no file → FULL
            result = check_staleness(tmpdir)
            assert result["dimensions"]["macro"]["routing"] == "REUSE"
            assert result["dimensions"]["political"]["routing"] == "FULL"
            assert result["dimensions"]["fundamentals"]["routing"] == "REUSE"
            assert result["dimensions"]["sentiment"]["routing"] == "FULL"

    def test_output_schema(self):
        """Output should have correct schema structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_staleness(tmpdir)
            assert "check_timestamp" in result
            assert "dimensions" in result
            for dim in ["macro", "political", "fundamentals", "sentiment"]:
                assert "routing" in result["dimensions"][dim]
                assert "reason" in result["dimensions"][dim]
                assert result["dimensions"][dim]["routing"] in ("REUSE", "FULL")

    def test_corrupted_json_falls_back_to_full(self):
        """Corrupted latest.json should fall back to FULL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dim_dir = os.path.join(tmpdir, "data", "macro")
            os.makedirs(dim_dir, exist_ok=True)
            with open(os.path.join(dim_dir, "latest.json"), "w") as f:
                f.write("NOT VALID JSON{{{")
            result = check_staleness(tmpdir)
            assert result["dimensions"]["macro"]["routing"] == "FULL"
