"""Tests for the meta-reasoner, translator, emergence strategies, and cross-mode knowledge.

Covers Phases 3-5 of the Creator Mode v1 build:
  - Emergence strategies (grid, sweep, hypothesis)
  - Emergence→Engine translator
  - Meta-reasoner (goal analysis → arm recommendation)
  - Auto-arm campaign creation
  - Cross-mode knowledge retrieval
  - Emergence coverage tracking
"""

from __future__ import annotations

from pathlib import Path

import pytest

from creator.campaign.meta_reasoner import (
    MetaRecommendation,
    ReasoningFactor,
    recommend,
)
from creator.campaign.strategies import (
    plan_emergence_from_hypotheses,
    plan_emergence_grid,
    plan_emergence_sweep,
)
from creator.knowledge.index import SearchIndex
from creator.knowledge.models import (
    Arm,
    EvidenceItem,
    Finding,
    FindingConditions,
    FindingType,
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    RunConfig,
    RunResult,
    TestDesign,
)
from creator.knowledge.store import KnowledgeStore
from creator.simulation.translator import (
    DimensionMapping,
    TranslationResult,
    translate_emergence_to_engine,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def store(tmp_path: Path) -> KnowledgeStore:
    return KnowledgeStore(root_dir=tmp_path / ".agentciv-creator")


@pytest.fixture
def search(store: KnowledgeStore) -> SearchIndex:
    return SearchIndex(store)


def _make_emergence_result(
    preset: str = "default",
    emergence_score: float = 0.6,
    metrics: dict | None = None,
) -> RunResult:
    """Helper to create a mock emergence RunResult."""
    default_metrics = {
        "rules_established": 4,
        "rules_proposed": 6,
        "cooperation_events": 8,
        "total_messages": 120,
        "network_density": 0.6,
        "agents_with_specialisation": 4,
        "total_specialisations": 5,
        "resource_sharing_events": 4,
        "bonded_pairs": 3,
        "relationship_count": 8,
        "innovation_count": 4,
        "composition_count": 2,
    }
    if metrics:
        default_metrics.update(metrics)

    return RunResult(
        id="run001",
        config=RunConfig(preset=preset),
        agent_count=12,
        model="claude-sonnet-4-6",
        max_ticks=100,
        arm=Arm.EMERGENT,
        success=True,
        emergence_score=emergence_score,
        emergence_metrics=default_metrics,
    )


# ── Emergence Strategies ─────────────────────────────────────────────────────


class TestEmergenceStrategies:
    def test_emergence_grid(self):
        configs, rationale = plan_emergence_grid(max_runs=15, runs_per_config=3)
        assert len(configs) == 5  # 15 / 3 = 5 configs
        assert "Emergence grid" in rationale

    def test_emergence_grid_focus(self):
        configs, _ = plan_emergence_grid(
            max_runs=9, runs_per_config=3,
            focus_conditions=["default", "scarce", "dense"],
        )
        presets = [c.preset for c in configs]
        assert "default" in presets
        assert "scarce" in presets

    def test_emergence_sweep(self):
        configs, rationale = plan_emergence_sweep(
            base_condition="default",
            max_runs=15, runs_per_config=3,
        )
        assert len(configs) >= 2
        assert configs[0].preset == "default"
        assert "Emergence sweep" in rationale

    def test_emergence_hypothesis(self):
        hypotheses = [
            Hypothesis(
                id="H001",
                statement="Resource scarcity increases governance emergence",
                test_design=TestDesign(
                    independent_variable="condition",
                    treatment="scarce",
                    control="abundant",
                ),
            ),
        ]
        configs, rationale = plan_emergence_from_hypotheses(
            hypotheses=hypotheses, max_runs=12, runs_per_config=3,
        )
        assert len(configs) >= 2
        presets = [c.preset for c in configs]
        assert "scarce" in presets or any(
            c.overrides and "scarce" in str(c.overrides) for c in configs
        )
        assert "Emergence hypothesis" in rationale


# ── Translator ───────────────────────────────────────────────────────────────


class TestTranslator:
    def test_empty_results(self):
        result = translate_emergence_to_engine([])
        assert result.config.preset == "collaborative"
        assert "No emergence data" in result.summary

    def test_no_successful_runs(self):
        failed = RunResult(
            id="r1", config=RunConfig(preset="default"),
            agent_count=12, model="test", max_ticks=100,
            arm=Arm.EMERGENT, success=False,
        )
        result = translate_emergence_to_engine([failed])
        assert "No successful" in result.summary

    def test_basic_translation(self):
        runs = [_make_emergence_result()]
        result = translate_emergence_to_engine(runs)

        assert isinstance(result, TranslationResult)
        assert result.overall_confidence > 0
        assert len(result.mappings) > 0
        assert result.config.preset == "collaborative"

    def test_high_governance_maps_to_consensus(self):
        runs = [_make_emergence_result(metrics={"rules_established": 8})]
        result = translate_emergence_to_engine(runs)

        authority_mappings = [m for m in result.mappings if m.dimension == "authority"]
        assert len(authority_mappings) >= 1
        assert authority_mappings[0].value == "consensus"

    def test_high_density_maps_to_mesh(self):
        runs = [_make_emergence_result(metrics={"network_density": 0.8})]
        result = translate_emergence_to_engine(runs)

        comm_mappings = [m for m in result.mappings if m.dimension == "communication"]
        assert len(comm_mappings) >= 1
        assert comm_mappings[0].value == "mesh"

    def test_multiple_runs_aggregated(self):
        runs = [
            _make_emergence_result(metrics={"rules_established": 2}),
            _make_emergence_result(metrics={"rules_established": 6}),
        ]
        # Give them different IDs
        runs[0].id = "r1"
        runs[1].id = "r2"
        result = translate_emergence_to_engine(runs)

        assert len(result.source_runs) == 2
        assert result.overall_confidence > 0

    def test_confidence_threshold(self):
        """Mappings below 0.4 confidence should be excluded from overrides."""
        runs = [_make_emergence_result(metrics={
            "rules_established": 0,
            "rules_proposed": 0,
            "cooperation_events": 0,
            "total_messages": 5,
            "network_density": 0.1,
        })]
        result = translate_emergence_to_engine(runs)
        # Low activity should produce low-confidence mappings
        # Some may be excluded from overrides
        included = [m for m in result.mappings if m.confidence >= 0.4]
        if result.config.overrides:
            assert len(result.config.overrides) <= len(included)

    def test_custom_base_preset(self):
        runs = [_make_emergence_result()]
        result = translate_emergence_to_engine(runs, base_preset="hierarchical")
        assert result.config.preset == "hierarchical"


# ── Meta-Reasoner ────────────────────────────────────────────────────────────


class TestMetaReasoner:
    def test_optimisation_routes_directed(self, store: KnowledgeStore, search: SearchIndex):
        rec = recommend(
            "What is the best org structure for code review?",
            "Build a REST API",
            store, search,
        )
        assert isinstance(rec, MetaRecommendation)
        assert rec.arm == Arm.DIRECTED
        assert rec.confidence > 0
        assert len(rec.factors) == 4

    def test_emergence_routes_emergent(self, store: KnowledgeStore, search: SearchIndex):
        rec = recommend(
            "What governance structures emerge when AI civilisations self-organise?",
            "observe",
            store, search,
        )
        assert rec.arm == Arm.EMERGENT

    def test_understanding_routes_both(self, store: KnowledgeStore, search: SearchIndex):
        rec = recommend(
            "Why does the relationship between cooperation and governance cause innovation?",
            "analyse",
            store, search,
        )
        assert rec.arm == Arm.BOTH

    def test_reasoning_string_present(self, store: KnowledgeStore, search: SearchIndex):
        rec = recommend("Best org for testing?", "test", store, search)
        assert "Recommended approach" in rec.reasoning
        assert "Strategy" in rec.reasoning

    def test_factors_have_explanations(self, store: KnowledgeStore, search: SearchIndex):
        rec = recommend("What emerges under scarcity?", "observe", store, search)
        for factor in rec.factors:
            assert factor.name
            assert factor.signal in ("directed", "emergent", "both")
            assert 0 <= factor.weight <= 1
            assert factor.explanation

    def test_confidence_range(self, store: KnowledgeStore, search: SearchIndex):
        rec = recommend("Test question", "task", store, search)
        assert 0 <= rec.confidence <= 1

    def test_hybrid_reasoning_includes_plan(self, store: KnowledgeStore, search: SearchIndex):
        rec = recommend(
            "Why does the relationship between cooperation and governance cause patterns?",
            "analyse",
            store, search,
        )
        if rec.arm == Arm.BOTH:
            assert "HYBRID plan" in rec.reasoning


# ── Auto-Arm Campaign Creation ───────────────────────────────────────────────


class TestAutoArm:
    @pytest.mark.asyncio
    async def test_auto_arm_resolves(self, store: KnowledgeStore, search: SearchIndex):
        from creator.campaign.manager import CampaignManager

        manager = CampaignManager(store, search)
        result = await manager.create_campaign(
            question="What governance structures emerge in AI civilisations?",
            task="observe emergence",
            arm="auto",
        )

        assert "campaign_id" in result
        # Auto should have resolved to a concrete arm
        assert result["arm"] in ("directed", "emergent", "both")
        # Meta-reasoning should be present
        assert "meta_reasoning" in result
        mr = result["meta_reasoning"]
        assert "recommended_arm" in mr
        assert "confidence" in mr
        assert "factors" in mr
        assert len(mr["factors"]) == 4

    @pytest.mark.asyncio
    async def test_explicit_arm_no_meta_reasoning(self, store: KnowledgeStore, search: SearchIndex):
        from creator.campaign.manager import CampaignManager

        manager = CampaignManager(store, search)
        result = await manager.create_campaign(
            question="Test question",
            task="test task",
            arm="directed",
            strategy="grid",
        )

        assert result["arm"] == "directed"
        assert "meta_reasoning" not in result

    @pytest.mark.asyncio
    async def test_auto_arm_emergence_question(self, store: KnowledgeStore, search: SearchIndex):
        from creator.campaign.manager import CampaignManager

        manager = CampaignManager(store, search)
        result = await manager.create_campaign(
            question="What happens when AI civilisations evolve and self-organise spontaneously?",
            task="observe",
            arm="auto",
        )

        assert result["arm"] == "emergent"


# ── Cross-Mode Knowledge ─────────────────────────────────────────────────────


class TestCrossModeKnowledge:
    def test_cross_arm_empty_store(self, store: KnowledgeStore, search: SearchIndex):
        results = search.query_cross_arm("governance cooperation", source_arm=Arm.DIRECTED)
        assert len(results) == 0

    def test_cross_arm_finds_opposite(self, store: KnowledgeStore, search: SearchIndex):
        # Save an emergence finding
        store.save_finding(Finding(
            id="F001",
            statement="AI agents develop governance rules under resource scarcity",
            confidence=0.8,
            type=FindingType.EMERGENCE,
            tags=["governance", "scarcity", "emergence"],
            conditions=FindingConditions(presets=["default"]),
        ))
        # Save a directed finding
        store.save_finding(Finding(
            id="F002",
            statement="Consensus authority improves quality score for code review",
            confidence=0.75,
            type=FindingType.COMPARATIVE,
            tags=["authority", "quality", "code_review"],
            conditions=FindingConditions(presets=["collaborative"]),
        ))

        # From directed source → should find emergence findings
        results = search.query_cross_arm("governance scarcity", source_arm=Arm.DIRECTED)
        assert len(results) >= 1
        assert results[0].finding.id == "F001"

        # From emergence source → should find directed findings
        results = search.query_cross_arm("authority quality", source_arm=Arm.EMERGENT)
        assert len(results) >= 1
        assert results[0].finding.id == "F002"

    def test_cross_arm_both_returns_all(self, store: KnowledgeStore, search: SearchIndex):
        store.save_finding(Finding(
            id="F001",
            statement="Governance emergence under scarcity",
            confidence=0.8,
            type=FindingType.EMERGENCE,
            tags=["governance"],
            conditions=FindingConditions(presets=["default"]),
        ))
        store.save_finding(Finding(
            id="F002",
            statement="Governance improves quality",
            confidence=0.7,
            type=FindingType.COMPARATIVE,
            tags=["governance"],
            conditions=FindingConditions(presets=["collaborative"]),
        ))

        results = search.query_cross_arm("governance", source_arm=Arm.BOTH)
        assert len(results) == 2


# ── Emergence Coverage Tracking ──────────────────────────────────────────────


class TestEmergenceCoverage:
    def test_empty_coverage(self, search: SearchIndex):
        coverage = search.compute_coverage()
        assert coverage.emergent.simulations_run == 0
        assert len(coverage.emergent.conditions_untested) > 0

    def test_conditions_untested_from_config(self, search: SearchIndex):
        from creator.config import SIM_CONDITIONS
        coverage = search.compute_coverage()
        assert len(coverage.emergent.conditions_untested) == len(SIM_CONDITIONS)
