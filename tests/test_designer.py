"""Tests for the recommendation engine (Phase 5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from creator.knowledge.index import SearchIndex
from creator.knowledge.models import (
    Finding,
    FindingConditions,
    FindingType,
    RunConfig,
    RunResult,
)
from creator.knowledge.store import KnowledgeStore
from creator.reporting.designer import recommend_config


@pytest.fixture
def store(tmp_path: Path) -> KnowledgeStore:
    return KnowledgeStore(root_dir=tmp_path / ".creator")


@pytest.fixture
def search(store: KnowledgeStore) -> SearchIndex:
    return SearchIndex(store)


class TestRecommendConfig:
    def test_empty_store(self, store: KnowledgeStore, search: SearchIndex):
        result = recommend_config(store, search)
        assert result["recommendation"] is None
        assert result["data_quality"] == "insufficient"

    def test_with_findings(self, store: KnowledgeStore, search: SearchIndex):
        # Add a finding
        f = Finding(
            id="F001",
            statement="Auto mode is best",
            confidence=0.85,
            type=FindingType.COMPARATIVE,
            conditions=FindingConditions(
                task_types=["code_review"],
                presets=["auto"],
            ),
            tags=["auto"],
        )
        store.save_finding(f)

        # Add some run results in a campaign
        from creator.knowledge.models import (
            Campaign,
            CampaignConstraints,
            CampaignBudget,
        )
        c = Campaign(
            id="C001",
            question="Test",
            constraints=CampaignConstraints(task="Test"),
            budget=CampaignBudget(runs_completed=3),
        )
        store.save_campaign(c)
        for i in range(3):
            store.save_run_result("C001", RunResult(
                id=f"run_{i:03d}",
                config=RunConfig(preset="auto"),
                agent_count=4,
                model="test",
                max_ticks=50,
                quality_score=0.85 + i * 0.02,
                success=True,
            ))

        result = recommend_config(store, search, task_type="code_review")
        assert result["recommendation"] is not None
        assert result["recommendation"]["preset"] == "auto"
        assert result["data_quality"] in ("insufficient", "limited", "good")

    def test_priority_speed(self, store: KnowledgeStore, search: SearchIndex):
        # Add campaigns with different configs
        from creator.knowledge.models import Campaign, CampaignConstraints, CampaignBudget
        c = Campaign(
            id="C001",
            question="Test",
            constraints=CampaignConstraints(task="Test"),
            budget=CampaignBudget(runs_completed=6),
        )
        store.save_campaign(c)

        # Fast but lower quality
        for i in range(3):
            store.save_run_result("C001", RunResult(
                id=f"run_a{i}",
                config=RunConfig(preset="hackathon"),
                agent_count=4,
                model="test",
                max_ticks=50,
                quality_score=0.7,
                ticks_used=15,
                success=True,
            ))

        # High quality but slow
        for i in range(3):
            store.save_run_result("C001", RunResult(
                id=f"run_b{i}",
                config=RunConfig(preset="code-review"),
                agent_count=4,
                model="test",
                max_ticks=50,
                quality_score=0.9,
                ticks_used=45,
                success=True,
            ))

        # With speed priority, hackathon might rank higher
        result = recommend_config(store, search, priority="speed")
        assert result["recommendation"] is not None
