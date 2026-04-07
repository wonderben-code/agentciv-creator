"""Tests for the report generator (Phase 7)."""

from __future__ import annotations

from pathlib import Path

import pytest

from creator.knowledge.index import SearchIndex
from creator.knowledge.models import (
    Batch,
    BatchStatus,
    Campaign,
    CampaignBudget,
    CampaignConstraints,
    CampaignStatus,
    Finding,
    FindingConditions,
    FindingType,
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    RunConfig,
    RunResult,
    StatisticalTest,
    Strategy,
)
from creator.knowledge.store import KnowledgeStore
from creator.reporting.report_generator import generate_campaign_report


@pytest.fixture
def store(tmp_path: Path) -> KnowledgeStore:
    return KnowledgeStore(root_dir=tmp_path / ".creator")


@pytest.fixture
def search(store: KnowledgeStore) -> SearchIndex:
    return SearchIndex(store)


def _populate_campaign(store: KnowledgeStore) -> str:
    """Create a complete campaign with results for testing."""
    campaign = Campaign(
        id="C001",
        question="Best org for code review with 4 agents?",
        status=CampaignStatus.COMPLETE,
        strategy=Strategy.GRID,
        constraints=CampaignConstraints(
            agents=4,
            model="claude-sonnet-4-6",
            max_ticks=50,
            task="Build a REST API",
        ),
        budget=CampaignBudget(
            max_runs=12,
            runs_per_config=3,
            runs_completed=12,
        ),
        batches=[
            Batch(
                id="B001",
                batch_number=1,
                status=BatchStatus.COMPLETE,
                configs=[
                    RunConfig(preset="auto"),
                    RunConfig(preset="collaborative"),
                    RunConfig(preset="hierarchical"),
                    RunConfig(preset="competitive"),
                ],
                runs_per_config=3,
                total_runs=12,
                rationale="Grid search across 4 presets",
            ),
        ],
    )
    store.save_campaign(campaign)

    # Add run results
    presets_scores = {
        "auto": [0.85, 0.88, 0.82],
        "collaborative": [0.78, 0.80, 0.79],
        "hierarchical": [0.65, 0.68, 0.62],
        "competitive": [0.55, 0.58, 0.50],
    }
    run_idx = 0
    for preset, scores in presets_scores.items():
        for i, score in enumerate(scores):
            result = RunResult(
                id=f"run_{run_idx:03d}",
                config=RunConfig(preset=preset),
                agent_count=4,
                model="claude-sonnet-4-6",
                max_ticks=50,
                quality_score=score,
                merge_conflicts=3 if preset != "competitive" else 15,
                ticks_used=30,
                success=True,
            )
            store.save_run_result("C001", result)
            run_idx += 1

    # Add a hypothesis
    h = Hypothesis(
        id="H001",
        statement="Auto mode outperforms hierarchical",
        status=HypothesisStatus.SUPPORTED,
        priority=HypothesisPriority.HIGH,
        tags=["auto", "hierarchical"],
    )
    store.save_hypothesis(h)
    campaign.hypotheses_generated.append("H001")

    # Add a finding
    f = Finding(
        id="F001",
        statement="Auto mode achieves highest quality for this task",
        confidence=0.85,
        type=FindingType.COMPARATIVE,
        conditions=FindingConditions(task_types=["api_dev"], presets=["auto"]),
        statistics=StatisticalTest(
            comparison="auto vs hierarchical",
            metric="quality_score",
            effect_size=1.5,
            p_value=0.002,
            significant=True,
        ),
        source_campaign="C001",
        tags=["auto", "quality"],
    )
    store.save_finding(f)
    campaign.findings_generated.append("F001")
    store.save_campaign(campaign)

    return "C001"


class TestReportGenerator:
    def test_nonexistent_campaign(self, store: KnowledgeStore, search: SearchIndex):
        report = generate_campaign_report("C999", store, search)
        assert "Error" in report
        assert "not found" in report

    def test_complete_report_structure(self, store: KnowledgeStore, search: SearchIndex):
        campaign_id = _populate_campaign(store)
        report = generate_campaign_report(campaign_id, store, search)

        # Check all sections present
        assert "# Campaign Report: C001" in report
        assert "## Executive Summary" in report
        assert "## Methodology" in report
        assert "## Results" in report
        assert "## Findings" in report
        assert "## Hypotheses" in report
        assert "## Recommendations" in report
        assert "## Coverage Analysis" in report
        assert "## Appendix" in report

    def test_report_contains_question(self, store: KnowledgeStore, search: SearchIndex):
        campaign_id = _populate_campaign(store)
        report = generate_campaign_report(campaign_id, store, search)
        assert "Best org for code review" in report

    def test_report_contains_winner(self, store: KnowledgeStore, search: SearchIndex):
        campaign_id = _populate_campaign(store)
        report = generate_campaign_report(campaign_id, store, search)
        assert "auto" in report  # Auto should be the winner

    def test_report_contains_findings(self, store: KnowledgeStore, search: SearchIndex):
        campaign_id = _populate_campaign(store)
        report = generate_campaign_report(campaign_id, store, search)
        assert "F001" in report
        assert "highest quality" in report

    def test_report_saved_to_disk(self, store: KnowledgeStore, search: SearchIndex):
        campaign_id = _populate_campaign(store)
        generate_campaign_report(campaign_id, store, search)
        report_path = store._campaign_dir(campaign_id) / "report.md"
        assert report_path.exists()
        content = report_path.read_text()
        assert "Campaign Report" in content

    def test_report_methodology_table(self, store: KnowledgeStore, search: SearchIndex):
        campaign_id = _populate_campaign(store)
        report = generate_campaign_report(campaign_id, store, search)
        assert "| Strategy | grid |" in report
        assert "| Agents | 4 |" in report
