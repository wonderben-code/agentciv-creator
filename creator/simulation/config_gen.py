"""Simulation config generator — creates YAML configs for emergent-arm experiments.

Generates treatment and control simulation configs for the AgentCiv Simulation.
In v1, these are generated and saved to disk for manual execution (simulations
are too expensive/slow to run autonomously). Future versions may automate this.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import DEFAULT_SIM_AGENTS, DEFAULT_SIM_TICKS

# ── Default Simulation Parameters ───────────────────────────────────────────

DEFAULT_SIM_CONFIG: dict[str, Any] = {
    "world": {
        "grid_size": 20,
        "resources": {
            "food": {"density": 0.3, "regen_rate": 0.1},
            "water": {"density": 0.2, "regen_rate": 0.05},
            "materials": {"density": 0.15, "regen_rate": 0.02},
        },
    },
    "agents": {
        "count": DEFAULT_SIM_AGENTS,
        "model": "claude-sonnet-4-6",
        "drives": {
            "hunger": {"weight": 1.0, "decay": 0.02},
            "thirst": {"weight": 1.0, "decay": 0.03},
            "safety": {"weight": 0.8, "decay": 0.01},
            "social": {"weight": 0.6, "decay": 0.01},
            "curiosity": {"weight": 0.4, "decay": 0.005},
        },
        "communication_range": 5,
        "memory_capacity": 50,
    },
    "simulation": {
        "max_ticks": DEFAULT_SIM_TICKS,
        "tick_duration_seconds": 1,
        "enable_building": True,
        "enable_governance": True,
        "enable_innovation": True,
    },
}

# ── Condition Templates ─────────────────────────────────────────────────────

CONDITION_TEMPLATES: dict[str, dict[str, Any]] = {
    "resource_scarcity": {
        "description": "Reduce resource density to force cooperation or competition",
        "overrides": {
            "world.resources.food.density": 0.1,
            "world.resources.water.density": 0.08,
            "world.resources.materials.density": 0.05,
        },
    },
    "resource_abundance": {
        "description": "Increase resource density to see if cooperation still emerges",
        "overrides": {
            "world.resources.food.density": 0.6,
            "world.resources.water.density": 0.5,
            "world.resources.materials.density": 0.4,
        },
    },
    "communication_limited": {
        "description": "Reduce communication range to force local cooperation",
        "overrides": {
            "agents.communication_range": 2,
        },
    },
    "communication_global": {
        "description": "Full communication range — all agents can hear everyone",
        "overrides": {
            "agents.communication_range": 100,
        },
    },
    "large_world": {
        "description": "Larger grid increases distance and travel cost",
        "overrides": {
            "world.grid_size": 40,
        },
    },
    "small_world": {
        "description": "Smaller grid forces proximity and interaction",
        "overrides": {
            "world.grid_size": 10,
        },
    },
    "high_social_drive": {
        "description": "Increase social drive weight — agents care more about relationships",
        "overrides": {
            "agents.drives.social.weight": 1.2,
        },
    },
    "high_curiosity": {
        "description": "Increase curiosity drive — agents explore and innovate more",
        "overrides": {
            "agents.drives.curiosity.weight": 1.0,
        },
    },
    "no_governance": {
        "description": "Disable governance mechanics — can cooperation emerge without rules?",
        "overrides": {
            "simulation.enable_governance": False,
        },
    },
    "no_building": {
        "description": "Disable building — agents can only gather, not construct",
        "overrides": {
            "simulation.enable_building": False,
        },
    },
}


# ── Config Generation ───────────────────────────────────────────────────────

def _deep_set(d: dict[str, Any], dotted_key: str, value: Any) -> None:
    """Set a value in a nested dict using dotted key notation."""
    keys = dotted_key.split(".")
    current = d
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def _deep_copy(d: dict[str, Any]) -> dict[str, Any]:
    """Deep copy a dict without importing copy."""
    return json.loads(json.dumps(d))


def generate_sim_config(
    agents: int = DEFAULT_SIM_AGENTS,
    ticks: int = DEFAULT_SIM_TICKS,
    conditions: dict[str, Any] | None = None,
    condition_name: str | None = None,
) -> dict[str, Any]:
    """Generate a single simulation config.

    Args:
        agents: Agent count.
        ticks: Max ticks.
        conditions: Direct overrides as dotted key → value.
        condition_name: Named condition template to apply.

    Returns:
        Complete simulation config dict.
    """
    config = _deep_copy(DEFAULT_SIM_CONFIG)
    config["agents"]["count"] = agents
    config["simulation"]["max_ticks"] = ticks

    # Apply named condition template
    if condition_name and condition_name in CONDITION_TEMPLATES:
        template = CONDITION_TEMPLATES[condition_name]
        for key, value in template["overrides"].items():
            _deep_set(config, key, value)

    # Apply direct overrides (these take precedence)
    if conditions:
        for key, value in conditions.items():
            _deep_set(config, key, value)

    return config


def generate_experiment_configs(
    hypothesis: str,
    agents: int = DEFAULT_SIM_AGENTS,
    ticks: int = DEFAULT_SIM_TICKS,
    conditions: dict[str, Any] | None = None,
    control: bool = True,
    variations: int = 1,
) -> list[dict[str, Any]]:
    """Generate treatment and control simulation configs for an experiment.

    Returns list of {role, label, config, hypothesis} dicts.
    """
    configs: list[dict[str, Any]] = []

    # Control: default config
    if control:
        configs.append({
            "role": "control",
            "label": "Default conditions",
            "config": generate_sim_config(agents=agents, ticks=ticks),
            "hypothesis": hypothesis,
        })

    # Treatment: with conditions applied
    treatment_config = generate_sim_config(
        agents=agents, ticks=ticks, conditions=conditions,
    )
    configs.append({
        "role": "treatment",
        "label": _describe_conditions(conditions) if conditions else "Modified conditions",
        "config": treatment_config,
        "hypothesis": hypothesis,
    })

    # Additional variations (slight perturbations of the treatment)
    for i in range(1, variations):
        varied = _deep_copy(treatment_config)
        # Perturb numeric values slightly
        _perturb(varied, seed=i)
        configs.append({
            "role": f"treatment_v{i + 1}",
            "label": f"Treatment variation {i + 1}",
            "config": varied,
            "hypothesis": hypothesis,
        })

    return configs


def save_sim_configs(
    configs: list[dict[str, Any]],
    output_dir: Path,
) -> list[str]:
    """Save simulation configs as JSON files.

    Returns list of saved file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []

    for i, cfg in enumerate(configs):
        role = cfg.get("role", f"config_{i}")
        filename = f"{role}_{i:03d}.json"
        path = output_dir / filename
        path.write_text(json.dumps(cfg, indent=2))
        paths.append(str(path))

    return paths


def _describe_conditions(conditions: dict[str, Any]) -> str:
    """Generate a human-readable description of conditions."""
    parts = []
    for key, value in conditions.items():
        short_key = key.split(".")[-1]
        parts.append(f"{short_key}={value}")
    return ", ".join(parts)


def _perturb(config: dict[str, Any], seed: int = 1) -> None:
    """Slightly perturb numeric values in a config for variation."""
    import random
    rng = random.Random(seed)

    def _walk(d: dict[str, Any]) -> None:
        for key, value in d.items():
            if isinstance(value, dict):
                _walk(value)
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                factor = 1.0 + rng.uniform(-0.1, 0.1)
                if isinstance(value, int):
                    d[key] = max(1, round(value * factor))
                else:
                    d[key] = round(value * factor, 4)

    _walk(config)


def list_conditions() -> list[dict[str, str]]:
    """Return all available named condition templates."""
    return [
        {"name": name, "description": template["description"]}
        for name, template in CONDITION_TEMPLATES.items()
    ]
