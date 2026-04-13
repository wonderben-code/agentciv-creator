"""Search strategies — pure functions that generate experiment plans.

Four strategies, each producing a list of RunConfig objects:
  - grid:       Test all (or specified) presets systematically
  - sweep:      Hold N-1 dimensions constant, vary 1 at a time
  - hypothesis: LLM generates hypotheses → minimal experiment design
  - knowledge:  Leverage existing findings, fill coverage gaps
"""

from __future__ import annotations


from ..config import ALL_PRESETS, DIMENSION_VALUES, SIM_CONDITIONS, SIM_SWEEP_PARAMS
from ..knowledge.index import SearchIndex
from ..knowledge.models import (
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    RunConfig,
)
from ..knowledge.store import KnowledgeStore


def plan_grid(
    max_runs: int,
    runs_per_config: int,
    focus_presets: list[str] | None = None,
) -> tuple[list[RunConfig], str]:
    """Grid search — test every preset systematically.

    Returns (configs, rationale).
    """
    presets = focus_presets or ALL_PRESETS
    max_configs = max_runs // runs_per_config

    # Always include "auto" for self-organisation data
    if "auto" not in presets and len(presets) < max_configs:
        presets = list(presets) + ["auto"]

    # Trim to budget
    configs = [RunConfig(preset=p) for p in presets[:max_configs]]
    rationale = (
        f"Grid search across {len(configs)} presets, "
        f"{runs_per_config} runs each ({len(configs) * runs_per_config} total runs). "
        "Provides comprehensive baseline data."
    )
    return configs, rationale


def plan_sweep(
    base_preset: str,
    max_runs: int,
    runs_per_config: int,
    focus_dimensions: list[str] | None = None,
) -> tuple[list[RunConfig], str]:
    """Dimension sweep — hold N-1 dimensions constant, vary 1 at a time.

    Returns (configs, rationale).
    """
    dimensions = focus_dimensions or list(DIMENSION_VALUES.keys())
    configs: list[RunConfig] = []
    max_configs = max_runs // runs_per_config

    # Always include the base config for comparison
    configs.append(RunConfig(preset=base_preset))

    for dim in dimensions:
        if len(configs) >= max_configs:
            break
        for val in DIMENSION_VALUES.get(dim, []):
            if len(configs) >= max_configs:
                break
            configs.append(RunConfig(preset=base_preset, overrides={dim: val}))

    rationale = (
        f"Dimension sweep from {base_preset} base across {len(dimensions)} dimensions. "
        f"{len(configs)} configs × {runs_per_config} runs. "
        "Identifies which dimensions have the largest effect."
    )
    return configs, rationale


def plan_from_hypotheses(
    hypotheses: list[Hypothesis],
    max_runs: int,
    runs_per_config: int,
    focus_presets: list[str] | None = None,
) -> tuple[list[RunConfig], str]:
    """Design experiments to test a set of hypotheses.

    Each hypothesis specifies a treatment and control — we ensure both are in the plan.
    Returns (configs, rationale).
    """
    configs: list[RunConfig] = []
    seen: set[str] = set()
    max_configs = max_runs // runs_per_config

    # Add configs needed to test each hypothesis
    for h in hypotheses:
        if len(configs) >= max_configs:
            break

        td = h.test_design
        if td.independent_variable and td.treatment:
            # Treatment config
            treatment_key = f"{td.treatment}:{td.independent_variable}"
            if treatment_key not in seen:
                configs.append(RunConfig(
                    preset=td.treatment if td.treatment in ALL_PRESETS
                    else (focus_presets[0] if focus_presets else "collaborative"),
                    overrides={td.independent_variable: td.treatment}
                    if td.treatment not in ALL_PRESETS else None,
                ))
                seen.add(treatment_key)

            # Control config
            if td.control:
                control_key = f"{td.control}:{td.independent_variable}"
                if control_key not in seen and len(configs) < max_configs:
                    configs.append(RunConfig(
                        preset=td.control if td.control in ALL_PRESETS
                        else (focus_presets[0] if focus_presets else "collaborative"),
                        overrides={td.independent_variable: td.control}
                        if td.control not in ALL_PRESETS else None,
                    ))
                    seen.add(control_key)

    # Fill remaining budget with related presets
    if focus_presets:
        for p in focus_presets:
            if len(configs) >= max_configs:
                break
            key = f"preset:{p}"
            if key not in seen:
                configs.append(RunConfig(preset=p))
                seen.add(key)

    # Always include "auto" if budget allows
    if "preset:auto" not in seen and len(configs) < max_configs:
        configs.append(RunConfig(preset="auto"))

    rationale = (
        f"Hypothesis-driven: {len(hypotheses)} hypotheses → "
        f"{len(configs)} configs × {runs_per_config} runs. "
        "Experiments designed to test specific predictions."
    )
    return configs, rationale


def plan_knowledge(
    store: KnowledgeStore,
    search: SearchIndex,
    question: str,
    max_runs: int,
    runs_per_config: int,
    focus_presets: list[str] | None = None,
) -> tuple[list[RunConfig], list[Hypothesis], str]:
    """Knowledge-informed — leverage existing findings, fill coverage gaps.

    Returns (configs, new_hypotheses_from_gaps, rationale).
    """
    configs: list[RunConfig] = []
    new_hypotheses: list[Hypothesis] = []
    max_configs = max_runs // runs_per_config

    # Check what we already know
    coverage = search.compute_coverage()
    gaps = search.identify_gaps()
    search.query_findings(question, max_results=5)

    # Skip presets we've already tested well (unless they're in focus)
    tested = set(coverage.directed.presets_tested)
    untested = coverage.directed.presets_untested

    # Fill gaps — untested presets first
    for p in untested:
        if len(configs) >= max_configs:
            break
        if focus_presets and p not in focus_presets:
            continue
        configs.append(RunConfig(preset=p))

    # If still have budget and no focus, test untested dimensions
    if len(configs) < max_configs:
        unvaried = coverage.directed.dimensions_unvaried
        base = focus_presets[0] if focus_presets else "collaborative"
        for dim in unvaried:
            if len(configs) >= max_configs:
                break
            values = DIMENSION_VALUES.get(dim, [])
            if values:
                configs.append(RunConfig(preset=base, overrides={dim: values[0]}))

    # Generate hypotheses from gaps
    for gap in gaps[:3]:
        h_id = store.next_hypothesis_id()
        new_hypotheses.append(Hypothesis(
            id=h_id,
            statement=f"Gap exploration: {gap.description}",
            status=HypothesisStatus.UNTESTED,
            priority=HypothesisPriority.MEDIUM,
            tags=["knowledge_gap", gap.area],
        ))

    rationale = (
        f"Knowledge-informed: {len(tested)} presets already tested, "
        f"filling {len(configs)} gaps. "
        f"{len(new_hypotheses)} new hypotheses from coverage analysis."
    )
    return configs, new_hypotheses, rationale


# ── Emergence Strategies ─────────────────────────────────────────────────────


def plan_emergence_grid(
    max_runs: int,
    runs_per_config: int,
    focus_conditions: list[str] | None = None,
) -> tuple[list[RunConfig], str]:
    """Grid search across simulation conditions.

    Each condition tests a different environmental pressure (scarcity,
    density, cooperation incentives, etc.) to see how emergent behaviour
    changes.

    Returns (configs, rationale).
    """
    conditions = focus_conditions or SIM_CONDITIONS
    max_configs = max_runs // runs_per_config

    configs = [RunConfig(preset=c) for c in conditions[:max_configs]]
    rationale = (
        f"Emergence grid across {len(configs)} conditions, "
        f"{runs_per_config} runs each ({len(configs) * runs_per_config} total). "
        "Tests how environmental conditions shape emergent behaviour."
    )
    return configs, rationale


def plan_emergence_sweep(
    base_condition: str,
    max_runs: int,
    runs_per_config: int,
    focus_params: list[str] | None = None,
) -> tuple[list[RunConfig], str]:
    """Parameter sweep from a base condition — vary one sim parameter at a time.

    Sweeps over agent count, resource levels, grid size, etc. to isolate
    which environmental parameters have the largest effect on emergence.

    Returns (configs, rationale).
    """
    params = focus_params or list(SIM_SWEEP_PARAMS.keys())
    configs: list[RunConfig] = []
    max_configs = max_runs // runs_per_config

    # Always include the base condition
    configs.append(RunConfig(preset=base_condition))

    for param in params:
        if len(configs) >= max_configs:
            break
        values = SIM_SWEEP_PARAMS.get(param, [])
        for val in values:
            if len(configs) >= max_configs:
                break
            configs.append(RunConfig(
                preset=base_condition,
                overrides={param: str(val)},
            ))

    rationale = (
        f"Emergence sweep from '{base_condition}' base across {len(params)} parameters. "
        f"{len(configs)} configs × {runs_per_config} runs. "
        "Identifies which environmental factors have the largest effect on emergence."
    )
    return configs, rationale


def plan_emergence_from_hypotheses(
    hypotheses: list[Hypothesis],
    max_runs: int,
    runs_per_config: int,
    focus_conditions: list[str] | None = None,
) -> tuple[list[RunConfig], str]:
    """Design emergence experiments to test hypothesis predictions.

    Each hypothesis specifies a treatment condition and control condition.
    Returns (configs, rationale).
    """
    configs: list[RunConfig] = []
    seen: set[str] = set()
    max_configs = max_runs // runs_per_config

    for h in hypotheses:
        if len(configs) >= max_configs:
            break

        td = h.test_design
        if td.treatment:
            treatment_key = f"condition:{td.treatment}"
            if treatment_key not in seen:
                # Treatment is a condition name or a parameter override
                if td.treatment in SIM_CONDITIONS:
                    configs.append(RunConfig(preset=td.treatment))
                else:
                    base = focus_conditions[0] if focus_conditions else "default"
                    configs.append(RunConfig(
                        preset=base,
                        overrides={td.independent_variable: td.treatment},
                    ))
                seen.add(treatment_key)

            if td.control:
                control_key = f"condition:{td.control}"
                if control_key not in seen and len(configs) < max_configs:
                    if td.control in SIM_CONDITIONS:
                        configs.append(RunConfig(preset=td.control))
                    else:
                        base = focus_conditions[0] if focus_conditions else "default"
                        configs.append(RunConfig(
                            preset=base,
                            overrides={td.independent_variable: td.control},
                        ))
                    seen.add(control_key)

    # Fill remaining budget with untested conditions
    if focus_conditions:
        for c in focus_conditions:
            if len(configs) >= max_configs:
                break
            key = f"condition:{c}"
            if key not in seen:
                configs.append(RunConfig(preset=c))
                seen.add(key)

    rationale = (
        f"Emergence hypothesis-driven: {len(hypotheses)} hypotheses → "
        f"{len(configs)} configs × {runs_per_config} runs. "
        "Tests specific predictions about emergent behaviour."
    )
    return configs, rationale
