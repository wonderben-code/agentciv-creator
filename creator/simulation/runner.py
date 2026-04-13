"""Simulation runner — executes emergence experiments via subprocess.

Calls the agent-civilisation simulation's run.py with custom configs,
collects structured results, and returns them in a format compatible
with Creator Mode's campaign and analysis pipeline.

The simulation repo is NOT imported as a library — it's called via
subprocess to preserve repo independence and avoid import path issues.
The Bitcoin-timestamped simulation code remains completely untouched.
"""

from __future__ import annotations

import asyncio
import json
import logging
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..config import DEFAULT_SIM_DIR, DEFAULT_SIM_AGENTS, DEFAULT_SIM_TICKS

log = logging.getLogger(__name__)


@dataclass
class SimRunConfig:
    """Configuration for a single simulation run."""

    condition_name: str = "default"
    agents: int = DEFAULT_SIM_AGENTS
    ticks: int = DEFAULT_SIM_TICKS
    overrides: dict[str, Any] = field(default_factory=dict)

    def label(self) -> str:
        parts = [self.condition_name]
        if self.overrides:
            parts.append("+".join(f"{k}={v}" for k, v in sorted(self.overrides.items())))
        return " ".join(parts)


@dataclass
class SimRunResult:
    """Result from a single simulation run."""

    id: str = ""
    config: SimRunConfig = field(default_factory=SimRunConfig)
    emergence_score: float = 0.0
    emergence_metrics: dict[str, Any] = field(default_factory=dict)
    milestones: list[str] = field(default_factory=list)
    chronicle_highlights: list[str] = field(default_factory=list)
    ticks_completed: int = 0
    total_tokens: int = 0
    wall_time_seconds: float = 0.0
    success: bool = False
    error: str = ""
    campaign_id: str = ""
    batch_id: str = ""


def _build_yaml_config(
    run_config: SimRunConfig,
    model: str = "claude-sonnet-4-6",
    api_key_env: str = "ANTHROPIC_API_KEY",
) -> dict[str, Any]:
    """Build a simulation YAML config from a SimRunConfig.

    Maps Creator Mode's condition-based config to the simulation's
    flat SimulationConfig parameters.
    """
    config: dict[str, Any] = {
        "initial_agent_count": run_config.agents,
        "ticks_per_real_minute": 0,  # always fast mode
        "model_provider": "anthropic",
        "model_name": model,
        "api_key_env_var": api_key_env,
        "log_level": "WARNING",  # quiet output
        "show_agent_reasoning": False,
        "show_conversations": False,
        "save_interval": 999999,  # don't auto-save during run
    }

    # Apply condition-specific overrides
    condition_map = _get_condition_overrides()
    if run_config.condition_name in condition_map:
        config.update(condition_map[run_config.condition_name])

    # Apply direct overrides
    for key, value in run_config.overrides.items():
        config[key] = value

    return config


def _get_condition_overrides() -> dict[str, dict[str, Any]]:
    """Map named conditions to simulation config overrides."""
    return {
        "default": {},
        "scarce": {
            "resource_max_per_tile": 0.4,
            "resource_regeneration_rate": 0.02,
            "resource_cluster_count": 2,
        },
        "abundant": {
            "resource_max_per_tile": 1.0,
            "resource_regeneration_rate": 0.1,
            "resource_cluster_count": 5,
        },
        "dense": {
            "grid_width": 30,
            "grid_height": 30,
            "initial_agent_count": 20,
        },
        "sparse": {
            "grid_width": 80,
            "grid_height": 80,
            "initial_agent_count": 6,
        },
        "cooperative": {
            "resource_distribution": "clustered",
            "agent_communication_range": 5,
            "agent_wellbeing_interaction_bonus": 0.1,
        },
        "competitive": {
            "resource_distribution": "scattered",
            "agent_communication_range": 1,
            "resource_max_per_tile": 0.5,
        },
        "innovative": {
            "enable_innovation": True,
            "enable_composition": True,
            "enable_specialisation": True,
            "enable_collective_rules": True,
            "agent_curiosity_decay_rate": 0.001,
            "agent_curiosity_discovery_bonus": 0.08,
        },
        "minimal": {
            "grid_width": 20,
            "grid_height": 20,
            "initial_agent_count": 4,
        },
        "no_governance": {
            "enable_collective_rules": False,
        },
        "no_innovation": {
            "enable_innovation": False,
            "enable_composition": False,
        },
    }


async def run_simulation(
    run_config: SimRunConfig,
    run_id: str,
    sim_dir: Path | str = DEFAULT_SIM_DIR,
    model: str = "claude-sonnet-4-6",
    session_manager: Any = None,
    campaign_id: str = "",
) -> SimRunResult:
    """Run a single simulation experiment via subprocess.

    Args:
        run_config: Configuration for this run.
        run_id: Unique identifier for this run.
        sim_dir: Path to the agent-civilisation repo.
        model: LLM model for agent cognition.
        session_manager: Optional dogfood session manager.
        campaign_id: Campaign this run belongs to.

    Returns:
        SimRunResult with emergence metrics and highlights.
    """
    sim_dir = Path(sim_dir)
    run_script = sim_dir / "scripts" / "run.py"

    if not run_script.exists():
        return SimRunResult(
            id=run_id,
            config=run_config,
            error=f"Simulation not found at {sim_dir}",
        )

    # Build config YAML
    yaml_config = _build_yaml_config(run_config, model=model)

    result = SimRunResult(id=run_id, config=run_config, campaign_id=campaign_id)
    start = time.monotonic()

    with tempfile.TemporaryDirectory(prefix="creator_sim_") as tmpdir:
        # Write config file
        config_path = Path(tmpdir) / "config.yaml"
        config_path.write_text(yaml.dump(yaml_config, default_flow_style=False))

        # Output path for structured results
        output_path = Path(tmpdir) / "results.json"

        # Save path for simulation state
        save_dir = Path(tmpdir) / "state"
        save_dir.mkdir()

        # Override save_path in config
        yaml_config["save_path"] = str(save_dir)
        config_path.write_text(yaml.dump(yaml_config, default_flow_style=False))

        # Build command
        cmd = [
            "python3",
            str(run_script),
            "--config", str(config_path),
            "--ticks", str(run_config.ticks),
            "--fast",
            "--metrics",
            "--output", str(output_path),
            "--preset", run_config.condition_name,
            "--run-id", run_id,
        ]

        log.info("Running simulation: %s (condition=%s, agents=%d, ticks=%d)",
                 run_id, run_config.condition_name, run_config.agents, run_config.ticks)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(sim_dir),
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=600,  # 10 minute timeout per simulation
            )

            result.wall_time_seconds = time.monotonic() - start

            if proc.returncode != 0:
                result.error = stderr.decode()[:500] if stderr else f"Exit code {proc.returncode}"
                log.error("Simulation %s failed: %s", run_id, result.error)
                return result

            # Parse structured output
            if output_path.exists():
                data = json.loads(output_path.read_text())
                emergence = data.get("emergence", {})
                result.emergence_score = emergence.get("composite_score", 0.0)
                result.emergence_metrics = emergence
                result.milestones = data.get("milestones", [])
                result.chronicle_highlights = data.get("chronicle_highlights", [])
                result.ticks_completed = data.get("ticks_completed", 0)
                result.total_tokens = data.get("total_tokens", 0)
                result.success = data.get("success", True)
            else:
                result.success = True  # ran but no output file
                result.ticks_completed = run_config.ticks
                log.warning("Simulation %s completed but no output file", run_id)

        except asyncio.TimeoutError:
            result.error = "Simulation timed out (10 minutes)"
            result.wall_time_seconds = time.monotonic() - start
            log.error("Simulation %s timed out", run_id)
        except Exception as e:
            result.error = str(e)
            result.wall_time_seconds = time.monotonic() - start
            log.exception("Simulation %s error", run_id)

    # Track cost and log if session manager is available
    if session_manager:
        sm = session_manager
        if result.total_tokens > 0:
            sm.track_cost(
                source="simulation_run",
                campaign_id=campaign_id,
                run_id=run_id,
                total_tokens=result.total_tokens,
            )
        sm.log(
            "simulation_run_complete",
            {
                "run_id": run_id,
                "condition": run_config.condition_name,
                "success": result.success,
                "emergence_score": result.emergence_score,
                "ticks": result.ticks_completed,
                "wall_time": round(result.wall_time_seconds, 1),
            },
            campaign_id=campaign_id,
        )

    return result


async def run_simulation_batch(
    configs: list[SimRunConfig],
    ticks: int = DEFAULT_SIM_TICKS,
    runs_per_config: int = 1,
    sim_dir: Path | str = DEFAULT_SIM_DIR,
    model: str = "claude-sonnet-4-6",
    session_manager: Any = None,
    campaign_id: str = "",
    max_parallel: int = 1,  # Simulations are expensive — default to sequential
) -> list[SimRunResult]:
    """Run a batch of simulation experiments.

    Simulations are expensive (each agent makes LLM calls each tick),
    so we default to sequential execution. Set max_parallel > 1 for
    parallel execution if you have the budget.

    Args:
        configs: List of simulation configs to run.
        ticks: Override tick count for all configs.
        runs_per_config: Number of runs per config.
        sim_dir: Path to the agent-civilisation repo.
        model: LLM model for agent cognition.
        session_manager: Optional dogfood session manager.
        campaign_id: Campaign this batch belongs to.
        max_parallel: Max parallel simulations.

    Returns:
        List of SimRunResult objects.
    """
    results: list[SimRunResult] = []
    run_counter = 0

    # Build the full list of runs
    runs: list[tuple[SimRunConfig, str]] = []
    for config in configs:
        config.ticks = ticks
        for rep in range(runs_per_config):
            run_id = f"sim_{run_counter:03d}"
            runs.append((config, run_id))
            run_counter += 1

    # Execute with bounded parallelism
    sem = asyncio.Semaphore(max_parallel)

    async def _bounded_run(cfg: SimRunConfig, rid: str) -> SimRunResult:
        async with sem:
            return await run_simulation(
                run_config=cfg,
                run_id=rid,
                sim_dir=sim_dir,
                model=model,
                session_manager=session_manager,
                campaign_id=campaign_id,
            )

    if max_parallel == 1:
        # Sequential execution
        for cfg, rid in runs:
            result = await _bounded_run(cfg, rid)
            results.append(result)
    else:
        # Parallel execution
        tasks = [_bounded_run(cfg, rid) for cfg, rid in runs]
        results = list(await asyncio.gather(*tasks))

    return results


def sim_result_to_run_result(
    sim: SimRunResult,
    agent_count: int = 12,
    model: str = "claude-sonnet-4-6",
    max_ticks: int = 100,
) -> "RunResult":
    """Convert a SimRunResult into a unified RunResult for the knowledge pipeline.

    This bridges the simulation runner's output format with the canonical
    RunResult schema used by campaigns, analysis, and the Knowledge Store.
    """
    from ..knowledge.models import Arm, RunConfig, RunResult

    return RunResult(
        id=sim.id,
        campaign_id=sim.campaign_id,
        batch_id=sim.batch_id,
        arm=Arm.EMERGENT,
        config=RunConfig(
            preset=sim.config.condition_name,
            overrides={str(k): str(v) for k, v in sim.config.overrides.items()}
            if sim.config.overrides else None,
        ),
        agent_count=agent_count,
        model=model,
        max_ticks=max_ticks,
        # Emergence-specific
        emergence_score=sim.emergence_score,
        emergence_metrics=sim.emergence_metrics,
        milestones=sim.milestones,
        chronicle_highlights=sim.chronicle_highlights,
        # Shared fields
        ticks_used=sim.ticks_completed,
        total_tokens=sim.total_tokens,
        wall_time_seconds=sim.wall_time_seconds,
        success=sim.success,
        error=sim.error or None,
    )


def list_conditions() -> list[dict[str, str]]:
    """Return all available simulation conditions."""
    conditions = _get_condition_overrides()
    return [
        {"name": name, "description": _condition_description(name)}
        for name in conditions
    ]


def _condition_description(name: str) -> str:
    """Human-readable description of a condition."""
    descriptions = {
        "default": "Balanced starting point — moderate resources, standard agent config",
        "scarce": "Resource scarcity — forces cooperation or competition pressure",
        "abundant": "Resource abundance — do agents still cooperate?",
        "dense": "High population density — 20 agents, small world, forced interaction",
        "sparse": "Low population density — 6 agents, large world, isolation pressure",
        "cooperative": "Conditions favouring cooperation — clustered resources, high communication",
        "competitive": "Conditions favouring competition — scattered resources, low communication",
        "innovative": "Maximise innovation — all features enabled, high curiosity drive",
        "minimal": "Cheapest possible run — 4 agents, small world, minimal ticks",
        "no_governance": "Governance disabled — can order emerge without rules?",
        "no_innovation": "Innovation disabled — baseline for comparison",
    }
    return descriptions.get(name, name)
