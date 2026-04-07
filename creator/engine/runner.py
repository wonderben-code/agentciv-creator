"""Engine runner — executes directed-arm experiments via the AgentCiv Engine Python API.

Each experiment runs in an isolated temporary directory with its own workspace.
Supports parallel execution bounded by a semaphore to respect API rate limits.
"""

from __future__ import annotations

import asyncio
import logging
import shutil
import tempfile
import time
from pathlib import Path

from ..knowledge.models import RunConfig, RunResult, utcnow

log = logging.getLogger(__name__)

# Max parallel experiments — prevents overwhelming the Anthropic API
MAX_PARALLEL = 3


async def run_single_experiment(
    config: RunConfig,
    task: str,
    agents: int,
    model: str,
    max_ticks: int,
    project_dir: str = ".",
    run_id: str = "",
    run_index: int = 0,
) -> RunResult:
    """Run one experiment and return a structured RunResult.

    Creates a temp directory, runs the engine, extracts metrics.
    """
    start = time.monotonic()
    source = Path(project_dir).resolve()

    tmpdir = tempfile.mkdtemp(prefix=f"creator_{config.preset}_")
    project = Path(tmpdir) / "project"

    try:
        # Copy source project (or create empty workspace)
        if source.exists() and any(source.iterdir()):
            try:
                shutil.copytree(
                    source, project,
                    ignore=shutil.ignore_patterns(
                        ".git", ".agentciv", "__pycache__",
                        "node_modules", ".venv", "venv",
                    ),
                    copy_function=shutil.copy2,
                )
            except shutil.Error:
                if not project.exists():
                    project.mkdir(parents=True)
        else:
            project.mkdir(parents=True)

        # Import engine components (deferred to avoid import at module load)
        from agentciv.core.agent import Agent
        from agentciv.core.attention import AttentionMap
        from agentciv.core.engine import Engine
        from agentciv.core.event_bus import EventBus
        from agentciv.core.types import AgentIdentity, AgentState
        from agentciv.learning.recorder import compute_quality_score, save_run
        from agentciv.llm.client import create_client
        from agentciv.org.config import EngineConfig
        from agentciv.org.enforcer import OrgEnforcer
        from agentciv.workspace.executor import WorkspaceExecutor
        from agentciv.workspace.workspace import Workspace

        AGENT_NAMES = [
            "Atlas", "Nova", "Sage", "Flux", "Echo",
            "Drift", "Pulse", "Cinder", "Wren", "Quill",
        ]

        # Build engine config
        engine_config = EngineConfig.from_preset(config.preset)
        engine_config.task = task
        engine_config.agent_count = agents
        engine_config.model = model
        engine_config.max_ticks = max_ticks
        engine_config.project_dir = str(project)
        engine_config.enable_chronicle = True

        # Apply dimension overrides
        if config.overrides:
            for dim, val in config.overrides.items():
                if hasattr(engine_config.org_dimensions, dim):
                    setattr(engine_config.org_dimensions, dim, val)

        # Create workspace
        workspace = Workspace(project_dir=project, task_description=task)
        workspace.scan()

        # Create agents
        event_bus = EventBus()
        attention = AttentionMap()
        engine_agents: list[Agent] = []

        for i in range(agents):
            name = AGENT_NAMES[i % len(AGENT_NAMES)]
            agent_id = f"agent_{i}"
            agent_model = engine_config.models.get(agent_id) or engine_config.models.get(name) or model
            identity = AgentIdentity(id=agent_id, name=name, model=agent_model)
            state = AgentState(
                identity=identity,
                token_budget_remaining=engine_config.parameters.token_budget_per_agent,
            )
            llm = create_client(agent_model, max_tokens=4096)
            executor = WorkspaceExecutor(workspace, attention=attention)
            agent = Agent(state=state, llm=llm, executor=executor)
            workspace.register_agent(state)
            engine_agents.append(agent)

        # Create enforcer
        enforcer = OrgEnforcer(
            dimensions=engine_config.org_dimensions,
            parameters=engine_config.parameters,
        )
        enforcer.assign_initial_roles([a.state.identity.id for a in engine_agents])

        # Create and run engine
        engine = Engine(
            config=engine_config,
            workspace=workspace,
            agents=engine_agents,
            event_bus=event_bus,
            enforcer=enforcer,
            attention=attention,
        )

        await engine.run()
        report = engine.chronicle.generate_report()

        # Inject token consumption
        initial_budget = engine_config.parameters.token_budget_per_agent
        report.tokens_per_agent = {
            a.state.identity.id: max(0, initial_budget - a.state.token_budget_remaining)
            for a in engine_agents
        }

        # Save to engine's learning history
        try:
            save_run(
                report=report,
                org_dimensions=engine_config.org_dimensions,
                model=model,
                max_ticks=max_ticks,
            )
        except Exception as e:
            log.warning("Failed to save engine learning record: %s", e)

        wall_time = time.monotonic() - start

        return _extract_run_result(
            report=report,
            config=config,
            agents=agents,
            model=model,
            max_ticks=max_ticks,
            run_id=run_id,
            run_index=run_index,
            wall_time=wall_time,
            quality_score=compute_quality_score(report),
        )

    except Exception as e:
        wall_time = time.monotonic() - start
        log.exception("Experiment failed: %s (preset=%s)", e, config.preset)
        return RunResult(
            id=run_id,
            config=config,
            agent_count=agents,
            model=model,
            max_ticks=max_ticks,
            success=False,
            error=str(e),
            wall_time_seconds=wall_time,
        )

    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass


async def run_batch(
    configs: list[RunConfig],
    task: str,
    agents: int,
    model: str,
    max_ticks: int,
    runs_per_config: int,
    project_dir: str = ".",
) -> list[RunResult]:
    """Run a batch of experiments with bounded parallelism.

    Creates runs_per_config copies of each config and executes them.
    Returns all RunResults (both successful and failed).
    """
    semaphore = asyncio.Semaphore(MAX_PARALLEL)
    results: list[RunResult] = []

    async def _bounded_run(cfg: RunConfig, run_idx: int, global_idx: int) -> RunResult:
        async with semaphore:
            run_id = f"run_{global_idx:03d}"
            log.info(
                "Running experiment %s: preset=%s, overrides=%s (run %d/%d)",
                run_id, cfg.preset, cfg.overrides, run_idx + 1, runs_per_config,
            )
            return await run_single_experiment(
                config=cfg,
                task=task,
                agents=agents,
                model=model,
                max_ticks=max_ticks,
                project_dir=project_dir,
                run_id=run_id,
                run_index=run_idx,
            )

    # Build task list
    tasks = []
    global_idx = 0
    for cfg in configs:
        for run_idx in range(runs_per_config):
            tasks.append(_bounded_run(cfg, run_idx, global_idx))
            global_idx += 1

    # Execute all with bounded parallelism
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return list(results)


def _extract_run_result(
    report,  # ChronicleReport
    config: RunConfig,
    agents: int,
    model: str,
    max_ticks: int,
    run_id: str,
    run_index: int,
    wall_time: float,
    quality_score: float,
) -> RunResult:
    """Convert a ChronicleReport into a structured RunResult."""
    return RunResult(
        id=run_id,
        config=config,
        agent_count=agents,
        model=model,
        max_ticks=max_ticks,
        quality_score=quality_score,
        ticks_used=report.total_ticks,
        total_messages=report.total_messages,
        total_broadcasts=report.total_broadcasts,
        merge_conflicts=report.merge_conflicts,
        merges_succeeded=report.merges_succeeded,
        restructures_adopted=report.restructures_adopted,
        restructure_log=report.restructure_log,
        final_org_state={},  # Populated from restructure_log if present
        total_tokens=sum(report.tokens_per_agent.values()),
        tokens_per_agent=report.tokens_per_agent,
        wall_time_seconds=round(wall_time, 2),
        files_produced=len(report.files_created),
        chronicle_report=report.to_terminal(),
        success=True,
        completed=utcnow(),
    )
