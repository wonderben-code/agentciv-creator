"""Tests for campaign planning and strategies.

Tests the strategy functions and campaign manager planning flow.
Engine execution (Phase 3) is tested separately with mocks.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from creator.campaign.strategies import (
    plan_from_hypotheses,
    plan_grid,
    plan_knowledge,
    plan_sweep,
)
from creator.knowledge.index import SearchIndex
from creator.knowledge.models import (
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    TestDesign,
)
from creator.knowledge.store import KnowledgeStore


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def store(tmp_path: Path) -> KnowledgeStore:
    return KnowledgeStore(root_dir=tmp_path / ".agentciv-creator")


@pytest.fixture
def search(store: KnowledgeStore) -> SearchIndex:
    return SearchIndex(store)


# ── Grid Strategy ────────────────────────────────────────────────────────────

class TestGridStrategy:
    def test_basic_grid(self):
        configs, rationale = plan_grid(max_runs=39, runs_per_config=3)
        assert len(configs) == 13  # all presets
        assert "Grid search" in rationale

    def test_grid_with_budget(self):
        configs, _ = plan_grid(max_runs=12, runs_per_config=3)
        assert len(configs) == 4  # 12 / 3 = 4 configs

    def test_grid_focus_presets(self):
        configs, _ = plan_grid(
            max_runs=21, runs_per_config=3,
            focus_presets=["collaborative", "competitive", "auto"],
        )
        presets = [c.preset for c in configs]
        assert "collaborative" in presets
        assert "competitive" in presets
        assert "auto" in presets

    def test_grid_adds_auto(self):
        configs, _ = plan_grid(
            max_runs=21, runs_per_config=3,
            focus_presets=["collaborative", "competitive"],
        )
        presets = [c.preset for c in configs]
        assert "auto" in presets


# ── Sweep Strategy ───────────────────────────────────────────────────────────

class TestSweepStrategy:
    def test_basic_sweep(self):
        configs, rationale = plan_sweep(
            base_preset="collaborative",
            max_runs=30, runs_per_config=3,
        )
        assert len(configs) >= 2
        assert configs[0].preset == "collaborative"
        assert configs[0].overrides is None  # base config has no overrides
        assert "Dimension sweep" in rationale

    def test_sweep_focus_dimensions(self):
        configs, _ = plan_sweep(
            base_preset="collaborative",
            max_runs=30, runs_per_config=3,
            focus_dimensions=["authority"],
        )
        # Should have base + one per authority value
        assert len(configs) >= 2
        authority_configs = [c for c in configs if c.overrides and "authority" in c.overrides]
        assert len(authority_configs) >= 1


# ── Hypothesis Strategy ──────────────────────────────────────────────────────

class TestHypothesisStrategy:
    def test_plan_from_hypotheses(self):
        hypotheses = [
            Hypothesis(
                id="H001",
                statement="Distributed beats hierarchical",
                status=HypothesisStatus.UNTESTED,
                test_design=TestDesign(
                    independent_variable="authority",
                    treatment="distributed",
                    control="hierarchy",
                    outcome_metric="quality_score",
                    expected_direction="treatment > control",
                ),
                priority=HypothesisPriority.HIGH,
            ),
            Hypothesis(
                id="H002",
                statement="Meritocratic improves quality",
                status=HypothesisStatus.UNTESTED,
                test_design=TestDesign(
                    independent_variable="preset",
                    treatment="meritocratic",
                    control="collaborative",
                    outcome_metric="quality_score",
                    expected_direction="treatment > control",
                ),
                priority=HypothesisPriority.MEDIUM,
            ),
        ]

        configs, rationale = plan_from_hypotheses(
            hypotheses=hypotheses, max_runs=21, runs_per_config=3,
        )
        assert len(configs) >= 2
        assert "Hypothesis-driven" in rationale

    def test_auto_always_included(self):
        hypotheses = [
            Hypothesis(
                id="H001",
                statement="Test",
                test_design=TestDesign(
                    independent_variable="preset",
                    treatment="competitive",
                    control="collaborative",
                ),
            ),
        ]
        configs, _ = plan_from_hypotheses(
            hypotheses=hypotheses, max_runs=21, runs_per_config=3,
        )
        presets = [c.preset for c in configs]
        assert "auto" in presets


# ── Knowledge Strategy ───────────────────────────────────────────────────────

class TestKnowledgeStrategy:
    def test_empty_store(self, store: KnowledgeStore, search: SearchIndex):
        configs, hypotheses, rationale = plan_knowledge(
            store=store, search=search,
            question="Best org for code review?",
            max_runs=21, runs_per_config=3,
        )
        # Should suggest untested presets
        assert len(configs) >= 1
        assert "Knowledge-informed" in rationale

    def test_generates_gap_hypotheses(self, store: KnowledgeStore, search: SearchIndex):
        _, hypotheses, _ = plan_knowledge(
            store=store, search=search,
            question="Best org for code review?",
            max_runs=21, runs_per_config=3,
        )
        assert len(hypotheses) >= 1
        assert any("Gap" in h.statement or "gap" in h.statement for h in hypotheses)


# ── Campaign Manager ─────────────────────────────────────────────────────────

class TestCampaignManager:
    @pytest.mark.asyncio
    async def test_create_campaign(self, store: KnowledgeStore, search: SearchIndex):
        from creator.campaign.manager import CampaignManager

        manager = CampaignManager(store, search)

        result = await manager.create_campaign(
            question="Best org for 4-agent API development?",
            task="Build a REST API",
            strategy="grid",
            agents=4,
            max_runs=12,
            runs_per_config=3,
        )

        assert "campaign_id" in result
        assert result["status"] == "planning"
        assert result["strategy"] == "grid"
        assert result["plan"]["batch_1"]["total_runs"] > 0

        # Campaign should be persisted
        campaign = store.get_campaign(result["campaign_id"])
        assert campaign is not None
        assert campaign.question == "Best org for 4-agent API development?"
        assert len(campaign.batches) == 1

    @pytest.mark.asyncio
    async def test_create_hypothesis_campaign(self, store: KnowledgeStore, search: SearchIndex):
        """Hypothesis strategy without API key falls back to heuristics."""
        from creator.campaign.manager import CampaignManager

        manager = CampaignManager(store, search)

        result = await manager.create_campaign(
            question="Best org for code review?",
            task="Build a REST API with auth",
            strategy="hypothesis",
            agents=8,
            max_runs=21,
            runs_per_config=3,
        )

        assert "campaign_id" in result
        # Should have hypotheses (from heuristic fallback)
        assert len(result["initial_hypotheses"]) >= 1
        assert result["plan"]["batch_1"]["total_runs"] > 0

    @pytest.mark.asyncio
    async def test_create_sweep_campaign(self, store: KnowledgeStore, search: SearchIndex):
        from creator.campaign.manager import CampaignManager

        manager = CampaignManager(store, search)

        result = await manager.create_campaign(
            question="Which dimensions matter most?",
            task="Build a calculator",
            strategy="sweep",
            agents=4,
            max_runs=30,
            runs_per_config=3,
            focus_presets=["collaborative"],
            focus_dimensions=["authority", "communication"],
        )

        assert result["plan"]["batch_1"]["total_runs"] > 0
