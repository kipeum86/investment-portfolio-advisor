"""Tests for recommendation-archiver.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/data-manager/scripts"))

from recommendation_archiver import archive_recommendation, update_latest


SAMPLE_RECOMMENDATION = {
    "recommendation_timestamp": "2026-03-17T12:00:00Z",
    "regime": "mid-cycle",
    "options": [{"option_id": "aggressive"}],
}

SAMPLE_MACRO = {"collection_timestamp": "2026-03-17T10:00:00Z", "indicators": []}


class TestArchiveRecommendation:
    def test_creates_archive_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = os.path.join(tmpdir, "data", "recommendations")
            os.makedirs(out_dir, exist_ok=True)
            path = archive_recommendation(SAMPLE_RECOMMENDATION, out_dir)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0

    def test_archive_filename_contains_date(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = os.path.join(tmpdir, "data", "recommendations")
            os.makedirs(out_dir, exist_ok=True)
            path = archive_recommendation(SAMPLE_RECOMMENDATION, out_dir)
            assert "2026-03-17" in os.path.basename(path)


class TestUpdateLatest:
    def test_creates_latest_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dim_dir = os.path.join(tmpdir, "macro")
            os.makedirs(dim_dir, exist_ok=True)
            update_latest(SAMPLE_MACRO, dim_dir)
            latest_path = os.path.join(dim_dir, "latest.json")
            assert os.path.exists(latest_path)
            with open(latest_path) as f:
                data = json.load(f)
            assert data["collection_timestamp"] == SAMPLE_MACRO["collection_timestamp"]
