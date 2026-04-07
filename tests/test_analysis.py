"""Tests for the statistical analysis module (Phase 4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from creator.analysis.analyzer import (
    _mean,
    _std,
    _t_test_independent,
    aggregate_by_config,
    analyze_campaign,
    cohens_d,
    compare_configs,
    config_key,
    extract_and_save_findings,
    rank_configs,
    resolve_and_save_hypotheses,
)
from creator.knowledge.models import (
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    RunConfig,
    RunResult,
    TestDesign,
)
from creator.knowledge.store import KnowledgeStore


# ── Helpers ─────────────────────────────────────────────────────────────────

def _make_result(
    preset: str = "collaborative",
    overrides: dict[str, str] | None = None,
    quality: float = 0.8,
    conflicts: int = 5,
    ticks: int = 30,
    success: bool = True,
    run_id: str = "run_001",
) -> RunResult:
    return RunResult(
        id=run_id,
        config=RunConfig(preset=preset, overrides=overrides),
        agent_count=4,
        model="test",
        max_ticks=50,
        quality_score=quality,
        merge_conflicts=conflicts,
        ticks_used=ticks,
        success=success,
    )


# ── Basic Stats ─────────────────────────────────────────────────────────────

class TestBasicStats:
    def test_mean(self):
        assert _mean([1, 2, 3, 4, 5]) == 3.0
        assert _mean([]) == 0.0

    def test_std(self):
        assert _std([1, 1, 1]) == 0.0
        assert _std([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(2.14, abs=0.1)
        assert _std([]) == 0.0
        assert _std([42]) == 0.0


class TestConfigKey:
    def test_no_overrides(self):
        assert config_key(RunConfig(preset="auto")) == "auto"

    def test_with_overrides(self):
        key = config_key(RunConfig(preset="auto", overrides={"authority": "flat"}))
        assert key == "auto+authority=flat"

    def test_sorted_overrides(self):
        key = config_key(RunConfig(
            preset="auto",
            overrides={"communication": "mesh", "authority": "flat"},
        ))
        assert key == "auto+authority=flat+communication=mesh"


# ── Aggregation ─────────────────────────────────────────────────────────────

class TestAggregation:
    def test_aggregate_by_config(self):
        results = [
            _make_result("auto", quality=0.8, run_id="r1"),
            _make_result("auto", quality=0.9, run_id="r2"),
            _make_result("auto", quality=0.85, run_id="r3"),
            _make_result("hierarchical", quality=0.7, run_id="r4"),
        ]
        agg = aggregate_by_config(results)
        assert "auto" in agg
        assert "hierarchical" in agg
        assert agg["auto"]["n"] == 3
        assert agg["auto"]["quality_score"]["mean"] == pytest.approx(0.85, abs=0.01)
        assert agg["hierarchical"]["n"] == 1

    def test_skips_failed_runs(self):
        results = [
            _make_result("auto", quality=0.8),
            _make_result("auto", quality=0.5, success=False),
        ]
        agg = aggregate_by_config(results)
        assert agg["auto"]["n"] == 1

    def test_rank_configs(self):
        agg = {
            "auto": {"quality_score": {"mean": 0.85}, "n": 3},
            "hierarchical": {"quality_score": {"mean": 0.7}, "n": 3},
            "competitive": {"quality_score": {"mean": 0.9}, "n": 3},
        }
        ranking = rank_configs(agg)
        assert ranking[0]["config_key"] == "competitive"
        assert ranking[0]["rank"] == 1
        assert ranking[1]["config_key"] == "auto"
        assert ranking[2]["config_key"] == "hierarchical"


# ── t-test and Effect Size ──────────────────────────────────────────────────

class TestStatistics:
    def test_t_test_identical(self):
        t, p = _t_test_independent([1, 2, 3], [1, 2, 3])
        assert abs(t) < 0.001
        assert p > 0.9

    def test_t_test_different(self):
        a = [10, 11, 12, 13, 14]
        b = [1, 2, 3, 4, 5]
        t, p = _t_test_independent(a, b)
        assert abs(t) > 3
        assert p < 0.01

    def test_t_test_insufficient_data(self):
        t, p = _t_test_independent([1], [2])
        assert t == 0.0
        assert p == 1.0

    def test_cohens_d_large(self):
        a = [10, 11, 12]
        b = [1, 2, 3]
        d = cohens_d(a, b)
        assert d > 2  # Very large effect

    def test_cohens_d_zero(self):
        a = [5, 5, 5]
        b = [5, 5, 5]
        d = cohens_d(a, b)
        assert abs(d) < 0.001


# ── Pairwise Comparison ────────────────────────────────────────────────────

class TestComparison:
    def test_compare_two_configs(self):
        results = [
            _make_result("auto", quality=0.9, run_id="r1"),
            _make_result("auto", quality=0.85, run_id="r2"),
            _make_result("auto", quality=0.88, run_id="r3"),
            _make_result("hierarchical", quality=0.6, run_id="r4"),
            _make_result("hierarchical", quality=0.65, run_id="r5"),
            _make_result("hierarchical", quality=0.62, run_id="r6"),
        ]
        comparison = compare_configs(results, "auto", "hierarchical")
        assert comparison["n_a"] == 3
        assert comparison["n_b"] == 3
        assert "quality_score" in comparison["comparisons"]
        qs = comparison["comparisons"]["quality_score"]
        assert qs["winner"] == "auto"
        assert qs["effect_size_d"] > 0

    def test_compare_missing_config(self):
        results = [_make_result("auto", quality=0.9)]
        comparison = compare_configs(results, "auto", "nonexistent")
        assert "error" in comparison


# ── Full Campaign Analysis ──────────────────────────────────────────────────

class TestCampaignAnalysis:
    def test_analyze_empty(self):
        result = analyze_campaign([])
        assert result["status"] == "no_data"

    def test_analyze_with_results(self):
        results = [
            _make_result("auto", quality=0.9, run_id="r1"),
            _make_result("auto", quality=0.85, run_id="r2"),
            _make_result("hierarchical", quality=0.6, run_id="r3"),
            _make_result("hierarchical", quality=0.65, run_id="r4"),
        ]
        analysis = analyze_campaign(results, campaign_id="C001")
        assert analysis["status"] == "analyzed"
        assert analysis["total_runs"] == 4
        assert analysis["configs_tested"] == 2
        assert len(analysis["ranking"]) == 2
        assert analysis["ranking"][0]["config_key"] == "auto"

    def test_analyze_with_hypotheses(self):
        results = [
            _make_result("auto", quality=0.9, run_id="r1"),
            _make_result("auto", quality=0.85, run_id="r2"),
            _make_result("auto", quality=0.88, run_id="r3"),
            _make_result("hierarchical", quality=0.6, run_id="r4"),
            _make_result("hierarchical", quality=0.65, run_id="r5"),
            _make_result("hierarchical", quality=0.62, run_id="r6"),
        ]
        hypotheses = [
            Hypothesis(
                id="H001",
                statement="Auto outperforms hierarchical",
                test_design=TestDesign(
                    independent_variable="preset",
                    treatment="auto",
                    control="hierarchical",
                    outcome_metric="quality_score",
                    expected_direction="treatment > control",
                ),
                priority=HypothesisPriority.HIGH,
            ),
        ]
        analysis = analyze_campaign(results, hypotheses=hypotheses)
        assert len(analysis["hypothesis_verdicts"]) == 1
        assert analysis["hypothesis_verdicts"][0]["verdict"] == "supported"


# ── Finding Extraction ──────────────────────────────────────────────────────

class TestFindingExtraction:
    def test_extract_findings(self, tmp_path: Path):
        store = KnowledgeStore(root_dir=tmp_path / ".creator")

        analysis = {
            "significant_findings": [
                {
                    "type": "comparative",
                    "statement": "Auto outperforms hierarchical on quality",
                    "config_a": "auto",
                    "config_b": "hierarchical",
                    "metric": "quality_score",
                    "effect_size": 1.2,
                    "p_value": 0.003,
                    "winner": "auto",
                    "campaign_id": "C001",
                },
            ],
        }

        findings = extract_and_save_findings(analysis, store, "C001", task="test")
        assert len(findings) == 1
        assert findings[0].confidence >= 0.75
        assert "auto" in findings[0].tags

        # Verify persisted
        loaded = store.get_finding(findings[0].id)
        assert loaded is not None
        assert loaded.statement == "Auto outperforms hierarchical on quality"

    def test_resolve_hypotheses(self, tmp_path: Path):
        store = KnowledgeStore(root_dir=tmp_path / ".creator")
        h = Hypothesis(
            id="H001",
            statement="Test hypothesis",
            status=HypothesisStatus.UNTESTED,
        )
        store.save_hypothesis(h)

        verdicts = [
            {
                "hypothesis_id": "H001",
                "verdict": "supported",
                "treatment_mean": 0.9,
                "control_mean": 0.6,
            },
        ]
        updated = resolve_and_save_hypotheses(verdicts, store)
        assert len(updated) == 1
        assert updated[0].status == HypothesisStatus.SUPPORTED

        # Verify persisted
        loaded = store.get_hypothesis("H001")
        assert loaded.status == HypothesisStatus.SUPPORTED
