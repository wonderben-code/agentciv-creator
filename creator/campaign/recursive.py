"""Recursive emergence loop — evolutionary search over organisational structures.

Implements the Paper 7 mechanism:
  Generation 0: Test N seed configs
  → select top K
  Generation 1: Mutate winners + crossover + extract emergent forms
  → test all → select top K
  ...
  Generation N: Final best config evolved through selection pressure

Key operations:
  - mutate(): randomly change dimension values in a config
  - crossover(): combine dimensions from two parent configs
  - extract_emergent_form(): extract org structure from auto-mode restructure events
  - evolve_generation(): full evolution step
"""

from __future__ import annotations

import random
from typing import Any

from ..config import ALL_PRESETS, DIMENSION_VALUES
from ..knowledge.models import (
    Batch,
    BatchStatus,
    Campaign,
    CampaignBudget,
    CampaignConstraints,
    CampaignStatus,
    CampaignType,
    RunConfig,
    RunResult,
    Strategy,
    Arm,
)
from ..knowledge.store import KnowledgeStore


# ── Mutation ────────────────────────────────────────────────────────────────

def mutate(
    config: RunConfig,
    mutation_rate: float = 0.3,
    rng: random.Random | None = None,
) -> RunConfig:
    """Mutate a config by randomly changing dimension values.

    Each dimension has `mutation_rate` probability of being changed.
    Returns a new RunConfig with the mutations applied as overrides.
    """
    rng = rng or random.Random()
    overrides = dict(config.overrides) if config.overrides else {}

    for dim, values in DIMENSION_VALUES.items():
        if rng.random() < mutation_rate:
            current = overrides.get(dim)
            # Pick a different value than current
            candidates = [v for v in values if v != current]
            if candidates:
                overrides[dim] = rng.choice(candidates)

    return RunConfig(preset=config.preset, overrides=overrides or None)


def crossover(
    parent_a: RunConfig,
    parent_b: RunConfig,
    rng: random.Random | None = None,
) -> RunConfig:
    """Combine dimensions from two parent configs.

    For each dimension, randomly inherit from parent A or parent B.
    Uses parent_a's preset as the base.
    """
    rng = rng or random.Random()
    overrides_a = parent_a.overrides or {}
    overrides_b = parent_b.overrides or {}

    child_overrides: dict[str, str] = {}

    for dim in DIMENSION_VALUES:
        # Check if either parent has an override for this dimension
        val_a = overrides_a.get(dim)
        val_b = overrides_b.get(dim)

        if val_a and val_b:
            child_overrides[dim] = rng.choice([val_a, val_b])
        elif val_a:
            if rng.random() < 0.5:
                child_overrides[dim] = val_a
        elif val_b:
            if rng.random() < 0.5:
                child_overrides[dim] = val_b

    return RunConfig(
        preset=rng.choice([parent_a.preset, parent_b.preset]),
        overrides=child_overrides or None,
    )


# ── Emergent Form Extraction ───────────────────────────────────────────────

def extract_emergent_form(result: RunResult) -> RunConfig | None:
    """Extract the final organisational state from an auto-mode run.

    If the run had restructure events (agents voted on their own structure),
    extract that structure as a RunConfig for testing in the next generation.
    """
    if not result.final_org_state and not result.restructure_log:
        return None

    # Use final_org_state if available
    if result.final_org_state:
        overrides = {}
        for dim, val in result.final_org_state.items():
            if dim in DIMENSION_VALUES and val in DIMENSION_VALUES.get(dim, []):
                overrides[dim] = val
        if overrides:
            return RunConfig(preset="auto", overrides=overrides)

    # Fall back to last restructure event
    if result.restructure_log:
        last = result.restructure_log[-1]
        if isinstance(last, dict):
            overrides = {}
            new_state = last.get("new_state") or last.get("adopted") or {}
            if isinstance(new_state, dict):
                for dim, val in new_state.items():
                    if dim in DIMENSION_VALUES and val in DIMENSION_VALUES.get(dim, []):
                        overrides[dim] = val
            if overrides:
                return RunConfig(preset="auto", overrides=overrides)

    return None


# ── Selection ───────────────────────────────────────────────────────────────

def select_survivors(
    results: list[RunResult],
    top_k: int = 2,
    metric: str = "quality_score",
) -> list[RunConfig]:
    """Select the top K configs by metric from a generation's results.

    Groups results by config, averages the metric, selects top K.
    """
    from ..analysis.analyzer import aggregate_by_config, rank_configs

    aggregates = aggregate_by_config(results, [metric])
    ranking = rank_configs(aggregates, primary_metric=metric)

    survivors = []
    for entry in ranking[:top_k]:
        config = entry.get("config")
        if config:
            survivors.append(RunConfig.model_validate(config))

    return survivors


# ── Generation Evolution ────────────────────────────────────────────────────

def evolve_generation(
    survivors: list[RunConfig],
    all_results: list[RunResult],
    population_size: int = 4,
    mutation_rate: float = 0.3,
    include_emergent: bool = False,
    rng: random.Random | None = None,
) -> list[RunConfig]:
    """Create the next generation's configs from survivors.

    Population is filled with:
    1. Survivors (carried forward)
    2. Mutations of survivors
    3. Crossovers between survivors
    4. Emergent forms extracted from auto-mode runs (if available)
    """
    rng = rng or random.Random()
    next_gen: list[RunConfig] = []
    seen: set[str] = set()

    def _key(cfg: RunConfig) -> str:
        base = cfg.preset
        if cfg.overrides:
            base += "+" + "+".join(f"{k}={v}" for k, v in sorted(cfg.overrides.items()))
        return base

    def _add(cfg: RunConfig) -> bool:
        k = _key(cfg)
        if k not in seen and len(next_gen) < population_size:
            seen.add(k)
            next_gen.append(cfg)
            return True
        return False

    # 1. Carry survivors forward
    for s in survivors:
        _add(s)

    # 2. Extract emergent forms from auto-mode runs
    if include_emergent:
        for r in all_results:
            if r.success and r.config.preset == "auto":
                emergent = extract_emergent_form(r)
                if emergent:
                    _add(emergent)

    # 3. Crossovers
    if len(survivors) >= 2:
        for _ in range(population_size):
            if len(next_gen) >= population_size:
                break
            parents = rng.sample(survivors, 2)
            child = crossover(parents[0], parents[1], rng=rng)
            _add(child)

    # 4. Mutations
    for s in survivors:
        if len(next_gen) >= population_size:
            break
        mutant = mutate(s, mutation_rate=mutation_rate, rng=rng)
        _add(mutant)

    # 5. Fill remaining with random mutations of survivors
    attempts = 0
    while len(next_gen) < population_size and attempts < 50:
        parent = rng.choice(survivors)
        mutant = mutate(parent, mutation_rate=mutation_rate + 0.1, rng=rng)
        _add(mutant)
        attempts += 1

    return next_gen


# ── Campaign Setup ──────────────────────────────────────────────────────────

def create_recursive_campaign(
    store: KnowledgeStore,
    seed: str | dict[str, Any],
    task: str,
    generations: int = 3,
    population_size: int = 4,
    agents: int = 4,
    model: str = "claude-sonnet-4-6",
    max_ticks: int = 50,
    runs_per_config: int = 2,
    mutation_rate: float = 0.3,
    include_emergent: bool = False,
) -> tuple[Campaign, list[RunConfig]]:
    """Create a recursive loop campaign and its initial generation.

    Returns (campaign, generation_0_configs).
    """
    campaign_id = store.next_campaign_id()

    # Parse seed into initial configs
    initial_configs = _seed_to_configs(seed, population_size)

    # Create batch for generation 0
    batch = Batch(
        id="B001",
        batch_number=1,
        status=BatchStatus.PLANNED,
        configs=initial_configs,
        runs_per_config=runs_per_config,
        total_runs=len(initial_configs) * runs_per_config,
        rationale=f"Generation 0: {len(initial_configs)} seed configs × {runs_per_config} runs",
    )

    total_budget = generations * population_size * runs_per_config

    campaign = Campaign(
        id=campaign_id,
        question=f"Recursive search: best org for '{task}'",
        status=CampaignStatus.PLANNING,
        type=CampaignType.RECURSIVE,
        arm=Arm.DIRECTED,
        strategy=Strategy.HYPOTHESIS,
        constraints=CampaignConstraints(
            agents=agents,
            model=model,
            max_ticks=max_ticks,
            task=task,
        ),
        budget=CampaignBudget(
            max_runs=total_budget,
            runs_per_config=runs_per_config,
        ),
        batches=[batch],
        generations_planned=generations,
        generations_completed=0,
        evolution_trajectory=[],
    )

    store.save_campaign(campaign)
    return campaign, initial_configs


def _seed_to_configs(
    seed: str | dict[str, Any],
    population_size: int,
) -> list[RunConfig]:
    """Convert a seed specification into initial RunConfigs."""
    configs: list[RunConfig] = []

    if isinstance(seed, str):
        if seed in ALL_PRESETS:
            configs.append(RunConfig(preset=seed))
        elif seed.startswith("from_simulation:"):
            # Extract from simulation data dir — placeholder for now
            configs.append(RunConfig(preset="auto"))
        else:
            # Default seed set
            configs.append(RunConfig(preset="auto"))
    elif isinstance(seed, dict):
        preset = seed.get("preset", "auto")
        overrides = seed.get("overrides")
        configs.append(RunConfig(preset=preset, overrides=overrides))

    # Fill to population_size with diverse presets
    diversity_presets = ["collaborative", "competitive", "meritocratic", "auto", "hierarchical"]
    for p in diversity_presets:
        if len(configs) >= population_size:
            break
        if not any(c.preset == p and c.overrides is None for c in configs):
            configs.append(RunConfig(preset=p))

    return configs[:population_size]


def advance_generation(
    campaign: Campaign,
    generation_results: list[RunResult],
    store: KnowledgeStore,
    mutation_rate: float = 0.3,
    population_size: int = 4,
    include_emergent: bool = False,
) -> tuple[Campaign, list[RunConfig] | None]:
    """Advance a recursive campaign to the next generation.

    Selects survivors, evolves, creates new batch. Returns (updated_campaign, next_configs).
    If all generations complete, returns (campaign, None).
    """
    gen_num = campaign.generations_completed

    # Select survivors
    survivors = select_survivors(generation_results, top_k=max(2, population_size // 2))

    if not survivors:
        campaign.status = CampaignStatus.FAILED
        store.save_campaign(campaign)
        return campaign, None

    # Record evolution trajectory
    from ..analysis.analyzer import aggregate_by_config, rank_configs
    aggregates = aggregate_by_config(generation_results, ["quality_score"])
    ranking = rank_configs(aggregates)

    best = ranking[0] if ranking else {}
    campaign.evolution_trajectory.append({
        "generation": gen_num,
        "best_quality": best.get("mean", 0),
        "best_config": best.get("config_key", ""),
        "population_size": len(ranking),
        "survivors": [s.model_dump() for s in survivors],
    })

    campaign.generations_completed = gen_num + 1

    # Check if done
    if campaign.generations_completed >= campaign.generations_planned:
        campaign.status = CampaignStatus.ANALYZING
        store.save_campaign(campaign)
        return campaign, None

    # Evolve next generation
    rng = random.Random(gen_num + 42)
    next_configs = evolve_generation(
        survivors=survivors,
        all_results=generation_results,
        population_size=population_size,
        mutation_rate=mutation_rate,
        include_emergent=include_emergent,
        rng=rng,
    )

    # Create new batch
    batch_num = len(campaign.batches) + 1
    runs_per = campaign.budget.runs_per_config
    batch = Batch(
        id=f"B{batch_num:03d}",
        batch_number=batch_num,
        status=BatchStatus.PLANNED,
        configs=next_configs,
        runs_per_config=runs_per,
        total_runs=len(next_configs) * runs_per,
        rationale=(
            f"Generation {campaign.generations_completed}: "
            f"{len(next_configs)} evolved configs from {len(survivors)} survivors"
        ),
    )
    campaign.batches.append(batch)
    store.save_campaign(campaign)

    return campaign, next_configs
