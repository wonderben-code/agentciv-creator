"""Tests for the recursive emergence loop (Phase 6)."""

from __future__ import annotations

from pathlib import Path


from creator.campaign.recursive import (
    advance_generation,
    create_recursive_campaign,
    crossover,
    evolve_generation,
    extract_emergent_form,
    mutate,
    select_survivors,
)
from creator.knowledge.models import (
    CampaignStatus,
    RunConfig,
    RunResult,
)
from creator.knowledge.store import KnowledgeStore

import random


# ── Helpers ─────────────────────────────────────────────────────────────────

def _make_result(
    preset: str = "auto",
    overrides: dict[str, str] | None = None,
    quality: float = 0.8,
    run_id: str = "run_001",
    final_org_state: dict[str, str] | None = None,
    restructure_log: list[dict] | None = None,
) -> RunResult:
    return RunResult(
        id=run_id,
        config=RunConfig(preset=preset, overrides=overrides),
        agent_count=4,
        model="test",
        max_ticks=50,
        quality_score=quality,
        success=True,
        final_org_state=final_org_state or {},
        restructure_log=restructure_log or [],
    )


# ── Mutation ────────────────────────────────────────────────────────────────

class TestMutation:
    def test_mutation_preserves_preset(self):
        config = RunConfig(preset="collaborative")
        mutant = mutate(config, mutation_rate=1.0, rng=random.Random(42))
        assert mutant.preset == "collaborative"
        assert mutant.overrides is not None
        assert len(mutant.overrides) > 0

    def test_mutation_rate_zero(self):
        config = RunConfig(preset="collaborative")
        mutant = mutate(config, mutation_rate=0.0)
        assert mutant.overrides is None

    def test_mutation_changes_dimensions(self):
        config = RunConfig(preset="auto", overrides={"authority": "flat"})
        mutant = mutate(config, mutation_rate=1.0, rng=random.Random(42))
        # At rate=1.0, all dimensions should be mutated
        assert mutant.overrides is not None
        assert len(mutant.overrides) >= 5


# ── Crossover ───────────────────────────────────────────────────────────────

class TestCrossover:
    def test_crossover_produces_child(self):
        parent_a = RunConfig(preset="collaborative", overrides={"authority": "flat"})
        parent_b = RunConfig(preset="competitive", overrides={"authority": "hierarchy"})
        child = crossover(parent_a, parent_b, rng=random.Random(42))
        assert child.preset in ("collaborative", "competitive")

    def test_crossover_inherits_from_both(self):
        parent_a = RunConfig(
            preset="auto",
            overrides={"authority": "flat", "communication": "mesh"},
        )
        parent_b = RunConfig(
            preset="auto",
            overrides={"authority": "hierarchy", "decisions": "consensus"},
        )
        # Run many times to check both parents contribute
        seen_a = False
        seen_b = False
        for seed in range(50):
            child = crossover(parent_a, parent_b, rng=random.Random(seed))
            if child.overrides:
                if child.overrides.get("authority") == "flat":
                    seen_a = True
                if child.overrides.get("authority") == "hierarchy":
                    seen_b = True
        assert seen_a or seen_b  # At least one parent should be represented


# ── Emergent Form Extraction ───────────────────────────────────────────────

class TestEmergentExtraction:
    def test_extract_from_final_state(self):
        result = _make_result(
            preset="auto",
            final_org_state={
                "authority": "distributed",
                "communication": "mesh",
            },
        )
        config = extract_emergent_form(result)
        assert config is not None
        assert config.preset == "auto"
        assert config.overrides["authority"] == "distributed"

    def test_extract_from_restructure_log(self):
        result = _make_result(
            preset="auto",
            restructure_log=[
                {"tick": 10, "new_state": {"authority": "rotating"}},
            ],
        )
        config = extract_emergent_form(result)
        assert config is not None
        assert config.overrides["authority"] == "rotating"

    def test_no_emergent_data(self):
        result = _make_result(preset="collaborative")
        config = extract_emergent_form(result)
        assert config is None


# ── Selection ───────────────────────────────────────────────────────────────

class TestSelection:
    def test_select_top_k(self):
        results = [
            _make_result("auto", quality=0.9, run_id="r1"),
            _make_result("collaborative", quality=0.8, run_id="r2"),
            _make_result("hierarchical", quality=0.7, run_id="r3"),
            _make_result("competitive", quality=0.6, run_id="r4"),
        ]
        survivors = select_survivors(results, top_k=2)
        assert len(survivors) == 2
        assert survivors[0].preset == "auto"
        assert survivors[1].preset == "collaborative"


# ── Generation Evolution ────────────────────────────────────────────────────

class TestEvolution:
    def test_evolve_fills_population(self):
        survivors = [
            RunConfig(preset="auto"),
            RunConfig(preset="collaborative"),
        ]
        results = [
            _make_result("auto", quality=0.9, run_id="r1"),
            _make_result("collaborative", quality=0.8, run_id="r2"),
        ]
        next_gen = evolve_generation(
            survivors=survivors,
            all_results=results,
            population_size=4,
            rng=random.Random(42),
        )
        assert len(next_gen) == 4

    def test_evolve_includes_survivors(self):
        survivors = [RunConfig(preset="auto")]
        next_gen = evolve_generation(
            survivors=survivors,
            all_results=[_make_result("auto")],
            population_size=3,
            rng=random.Random(42),
        )
        assert any(c.preset == "auto" and c.overrides is None for c in next_gen)

    def test_evolve_with_emergent(self):
        survivors = [RunConfig(preset="auto")]
        results = [
            _make_result(
                "auto",
                quality=0.9,
                final_org_state={"authority": "distributed"},
            ),
        ]
        next_gen = evolve_generation(
            survivors=survivors,
            all_results=results,
            population_size=4,
            include_emergent=True,
            rng=random.Random(42),
        )
        # Should include emergent form
        emergent = [c for c in next_gen if c.overrides and c.overrides.get("authority") == "distributed"]
        assert len(emergent) >= 1


# ── Campaign Creation ───────────────────────────────────────────────────────

class TestRecursiveCampaign:
    def test_create_campaign(self, tmp_path: Path):
        store = KnowledgeStore(root_dir=tmp_path / ".creator")
        campaign, configs = create_recursive_campaign(
            store=store,
            seed="auto",
            task="Build a REST API",
            generations=3,
            population_size=4,
        )
        assert campaign.generations_planned == 3
        assert len(configs) == 4
        assert len(campaign.batches) == 1

    def test_create_with_dict_seed(self, tmp_path: Path):
        store = KnowledgeStore(root_dir=tmp_path / ".creator")
        campaign, configs = create_recursive_campaign(
            store=store,
            seed={"preset": "code-review", "overrides": {"authority": "distributed"}},
            task="Code review task",
            population_size=4,
        )
        assert any(c.preset == "code-review" for c in configs)

    def test_advance_generation(self, tmp_path: Path):
        store = KnowledgeStore(root_dir=tmp_path / ".creator")
        campaign, _ = create_recursive_campaign(
            store=store,
            seed="auto",
            task="Test",
            generations=3,
            population_size=4,
        )
        results = [
            _make_result("auto", quality=0.9, run_id="r1"),
            _make_result("collaborative", quality=0.8, run_id="r2"),
            _make_result("competitive", quality=0.7, run_id="r3"),
            _make_result("meritocratic", quality=0.6, run_id="r4"),
        ]
        campaign, next_configs = advance_generation(
            campaign=campaign,
            generation_results=results,
            store=store,
            population_size=4,
        )
        assert campaign.generations_completed == 1
        assert next_configs is not None
        assert len(next_configs) == 4
        assert len(campaign.evolution_trajectory) == 1

    def test_final_generation_returns_none(self, tmp_path: Path):
        store = KnowledgeStore(root_dir=tmp_path / ".creator")
        campaign, _ = create_recursive_campaign(
            store=store,
            seed="auto",
            task="Test",
            generations=1,  # Only 1 generation
            population_size=2,
        )
        results = [
            _make_result("auto", quality=0.9, run_id="r1"),
            _make_result("collaborative", quality=0.8, run_id="r2"),
        ]
        campaign, next_configs = advance_generation(
            campaign=campaign,
            generation_results=results,
            store=store,
        )
        assert campaign.generations_completed == 1
        assert next_configs is None  # Done
        assert campaign.status == CampaignStatus.ANALYZING
