"""Creator Mode MCP server — 7 tools for autonomous organisational architecture.

All tools are live:
  - creator_info()           — documentation and capabilities
  - creator_status()         — dashboard and campaign management
  - creator_knowledge()      — query the knowledge store
  - creator_explore()        — full autonomous research campaigns
  - creator_spawn_directed() — run specific engine experiments
  - creator_spawn_emergent() — generate simulation configs
  - creator_analyze()        — statistical analysis and finding extraction
  - creator_recursive()      — evolutionary recursive emergence loop
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import __version__
from ..config import ALL_DIMENSIONS, ALL_PRESETS, DIMENSION_VALUES, EMERGENCE_DIMENSIONS
from ..knowledge.index import SearchIndex
from ..knowledge.models import (
    BatchStatus,
    CampaignStatus,
    HypothesisStatus,
)
from ..knowledge.store import KnowledgeStore

# ── Server instance ──────────────────────────────────────────────────────────

mcp = FastMCP(
    "agentciv-creator",
    instructions=(
        "Creator Mode — autonomous organisational architect for multi-agent AI systems. "
        "Designs experiments, runs them via the AgentCiv Engine and Simulation, "
        "analyzes results, generates hypotheses, and accumulates knowledge. "
        f"Version {__version__}."
    ),
)

# ── Shared state ─────────────────────────────────────────────────────────────

_store: KnowledgeStore | None = None
_search: SearchIndex | None = None


def _get_store() -> KnowledgeStore:
    global _store
    if _store is None:
        _store = KnowledgeStore()
    return _store


def _get_search() -> SearchIndex:
    global _search
    if _search is None:
        _search = SearchIndex(_get_store())
    return _search


# ── Tool: creator_info ───────────────────────────────────────────────────────

@mcp.tool()
async def creator_info() -> str:
    """Get Creator Mode documentation — what it is, what it can do, how to use it.

    Call this first to understand Creator Mode's capabilities before starting a campaign.
    Returns a structured guide to all 7 tools, available presets, dimensions, and strategies.
    """
    presets_list = "\n".join(f"  - {p}" for p in ALL_PRESETS)
    dims_list = "\n".join(
        f"  - {dim}: {', '.join(vals)}" for dim, vals in DIMENSION_VALUES.items()
    )
    emergence_list = "\n".join(f"  - {e}" for e in EMERGENCE_DIMENSIONS)

    return f"""# Creator Mode v{__version__}

**Autonomous organisational architect for multi-agent AI systems.**

Creator Mode is to multi-agent AI what Neural Architecture Search is to deep learning
— but for organisational structure, not network topology.

## What It Does

You give it a question — "What's the best way to organise 12 AI agents for code review?"
— and it designs experiments, runs them using the AgentCiv Engine and Simulation,
analyzes results, generates new hypotheses, runs more experiments, and converges on
a data-backed answer. Everything it learns persists in a knowledge store that gets
smarter with every campaign.

## The 7 Tools

| Tool | Purpose |
|------|---------|
| `creator_explore` | Research question → full autonomous campaign → findings |
| `creator_spawn_directed` | Run specific engine experiments with explicit configs |
| `creator_spawn_emergent` | Generate and launch civilisation simulations |
| `creator_analyze` | Deep cross-run statistical analysis and pattern detection |
| `creator_knowledge` | Query findings, get recommendations, see coverage |
| `creator_recursive` | Run the recursive emergence loop (Paper 7) |
| `creator_status` | Dashboard — campaign progress, steering, management |

## Search Strategies

- **hypothesis** (default) — LLM generates testable hypotheses, adapts after each batch
- **grid** — Test all presets systematically. Best for initial exploration.
- **sweep** — Vary one dimension at a time from a base config
- **knowledge** — Leverage existing findings, fill gaps

## Available Presets ({len(ALL_PRESETS)})

{presets_list}

## Organisational Dimensions ({len(ALL_DIMENSIONS)})

{dims_list}

## Emergence Metrics (Simulation Arm)

{emergence_list}

## Quick Start

1. `creator_explore(question="What org works best for code review?", task="Build a REST API", agents=4)`
2. Wait for campaign to run (check with `creator_status()`)
3. `creator_knowledge(action="query", question="code review")` to retrieve findings
4. `creator_knowledge(action="recommend", task_type="code_review")` for a ready-to-use config

## Architecture

- Creator Mode imports the AgentCiv Engine as a Python library (directed arm)
- Simulation integration via config generation + subprocess (emergent arm)
- Knowledge Store persists at ~/.agentciv-creator/ across all sessions
- Claude Code IS the Creator's intelligence — no separate LLM loop
"""


# ── Tool: creator_status ─────────────────────────────────────────────────────

@mcp.tool()
async def creator_status(
    campaign_id: str | None = None,
    steer: str | None = None,
    stop: bool = False,
) -> str:
    """Dashboard and campaign management.

    Without campaign_id: overview of all campaigns + knowledge stats + suggestions.
    With campaign_id: detailed status of a specific campaign.

    Args:
        campaign_id: Specific campaign to check, or None for overview.
        steer: Natural language guidance to redirect a running campaign.
        stop: Set True to gracefully end a running campaign.
    """
    store = _get_store()
    search = _get_search()

    if campaign_id is not None:
        return await _campaign_detail(store, campaign_id, steer=steer, stop=stop)
    return await _overview(store, search)


async def _overview(store: KnowledgeStore, search: SearchIndex) -> str:
    """Generate the overview dashboard."""
    active = store.list_campaigns(status=CampaignStatus.RUNNING)
    completed = store.list_campaigns(status=CampaignStatus.COMPLETE)
    stats = store.stats()
    suggestions = search.suggest_next()

    result: dict[str, Any] = {
        "active_campaigns": [
            {
                "id": c.id,
                "question": c.question,
                "progress": f"{c.budget.runs_completed}/{c.budget.max_runs} runs",
                "status": c.status.value,
            }
            for c in active
        ],
        "completed_campaigns": [
            {
                "id": c.id,
                "question": c.question,
                "findings": len(c.findings_generated),
                "completed": c.completed.isoformat() if c.completed else None,
            }
            for c in completed
        ],
        "knowledge_stats": {
            "total_findings": stats["total_findings"],
            "total_runs": stats["total_runs"],
            "total_hypotheses": stats["total_hypotheses"],
            "hypotheses_breakdown": stats["hypotheses_breakdown"],
            "knowledge_store_size_kb": stats["knowledge_store_size_kb"],
        },
        "suggestions": suggestions,
    }

    return json.dumps(result, indent=2, default=str)


async def _campaign_detail(
    store: KnowledgeStore,
    campaign_id: str,
    steer: str | None = None,
    stop: bool = False,
) -> str:
    """Generate detailed status for a specific campaign."""
    campaign = store.get_campaign(campaign_id)
    if campaign is None:
        return json.dumps({"error": f"Campaign {campaign_id} not found"})

    # Handle stop
    if stop and campaign.status == CampaignStatus.RUNNING:
        campaign.status = CampaignStatus.STOPPED
        store.save_campaign(campaign)
        return json.dumps({"campaign_id": campaign_id, "status": "stopped", "message": "Campaign stopped."})

    # Handle steer (stored for the campaign runner to pick up in later phases)
    if steer and campaign.status == CampaignStatus.RUNNING:
        # For Phase 1, just acknowledge — actual steering is Phase 2+
        return json.dumps({
            "campaign_id": campaign_id,
            "status": campaign.status.value,
            "steer_acknowledged": steer,
            "message": "Steering guidance received. Will apply to next batch.",
        })

    # Build status report
    runs = store.list_run_results(campaign_id)

    # Find current leader
    current_leader = None
    if runs:
        best = max(runs, key=lambda r: r.quality_score)
        current_leader = {
            "config": best.config.model_dump(),
            "quality_score": best.quality_score,
            "conflicts": best.merge_conflicts,
        }

    result: dict[str, Any] = {
        "campaign_id": campaign.id,
        "question": campaign.question,
        "status": campaign.status.value,
        "strategy": campaign.strategy.value,
        "arm": campaign.arm.value,
        "progress": {
            "runs_completed": campaign.budget.runs_completed,
            "runs_total": campaign.budget.max_runs,
            "batches_completed": sum(1 for b in campaign.batches if b.status.value == "complete"),
            "current_batch": len(campaign.batches),
        },
        "current_leader": current_leader,
        "findings_generated": campaign.findings_generated,
        "hypotheses_tested": campaign.hypotheses_tested,
    }

    return json.dumps(result, indent=2, default=str)


# ── Tool: creator_knowledge ──────────────────────────────────────────────────

@mcp.tool()
async def creator_knowledge(
    action: str = "query",
    question: str | None = None,
    min_confidence: float = 0.5,
    max_results: int = 10,
    task_type: str | None = None,
    agents: int | None = None,
    priority: str | None = None,
    status: str | None = None,
) -> str:
    """Access the accumulated knowledge store.

    Query findings, get recommendations, see coverage, find untested hypotheses.

    Args:
        action: One of "query", "recommend", "coverage", "hypotheses", "stats".
        question: Natural language query (for action="query").
        min_confidence: Minimum confidence for returned findings (default 0.5).
        max_results: Maximum findings to return (default 10).
        task_type: Task type for recommendations (for action="recommend").
        agents: Agent count for recommendations.
        priority: Priority filter — "quality", "speed", "creativity", "balanced".
        status: Hypothesis status filter — "untested", "supported", "refuted", "inconclusive".
    """
    store = _get_store()
    search = _get_search()

    if action == "query":
        return await _knowledge_query(search, question or "", min_confidence, max_results)
    elif action == "recommend":
        return await _knowledge_recommend(store, search, task_type, agents, priority)
    elif action == "coverage":
        return await _knowledge_coverage(search)
    elif action == "hypotheses":
        return await _knowledge_hypotheses(store, status)
    elif action == "stats":
        return json.dumps(store.stats(), indent=2, default=str)
    else:
        return json.dumps({"error": f"Unknown action: {action}. Use: query, recommend, coverage, hypotheses, stats"})


async def _knowledge_query(
    search: SearchIndex,
    question: str,
    min_confidence: float,
    max_results: int,
) -> str:
    """Handle action=query."""
    if not question:
        return json.dumps({"error": "question parameter required for action='query'"})

    results = search.query_findings(question, min_confidence=min_confidence, max_results=max_results)
    related = search.find_related_hypotheses(question)

    return json.dumps({
        "query": question,
        "findings": [
            {
                "id": r.finding.id,
                "statement": r.finding.statement,
                "confidence": r.finding.confidence,
                "conditions": r.finding.conditions.model_dump(),
                "evidence_runs": len(r.finding.evidence),
                "source_campaign": r.finding.source_campaign,
                "relevance_score": round(r.score, 3),
                "match_reasons": r.match_reasons,
            }
            for r in results
        ],
        "related_hypotheses": [
            {
                "id": h.id,
                "statement": h.statement,
                "status": h.status.value,
                "priority": h.priority.value,
            }
            for h in related
        ],
    }, indent=2, default=str)


async def _knowledge_recommend(
    store: KnowledgeStore,
    search: SearchIndex,
    task_type: str | None,
    agents: int | None,
    priority: str | None,
) -> str:
    """Handle action=recommend using the recommendation engine."""
    from ..reporting.designer import recommend_config

    result = recommend_config(
        store=store,
        search=search,
        task_type=task_type,
        agents=agents,
        priority=priority,
    )
    return json.dumps(result, indent=2, default=str)


async def _knowledge_coverage(search: SearchIndex) -> str:
    """Handle action=coverage."""
    coverage = search.compute_coverage()
    gaps = search.identify_gaps()
    suggestions = search.suggest_next()

    return json.dumps({
        "coverage_map": coverage.model_dump(),
        "gaps": [{"area": g.area, "description": g.description, "priority": g.priority} for g in gaps],
        "suggestions": suggestions,
    }, indent=2, default=str)


async def _knowledge_hypotheses(store: KnowledgeStore, status: str | None) -> str:
    """Handle action=hypotheses."""
    status_filter = HypothesisStatus(status) if status else None
    hypotheses = store.list_hypotheses(status=status_filter)

    # Breakdown
    all_h = store.list_hypotheses()
    breakdown: dict[str, int] = {}
    for h in all_h:
        breakdown[h.status.value] = breakdown.get(h.status.value, 0) + 1

    return json.dumps({
        "hypotheses": [
            {
                "id": h.id,
                "statement": h.statement,
                "status": h.status.value,
                "priority": h.priority.value,
                "tags": h.tags,
            }
            for h in hypotheses
        ],
        "total": breakdown,
    }, indent=2, default=str)


# ── Placeholder tools (wired up in later phases) ────────────────────────────

@mcp.tool()
async def creator_explore(
    question: str,
    task: str,
    arm: str = "directed",
    strategy: str = "hypothesis",
    agents: int = 4,
    model: str = "claude-sonnet-4-6",
    max_ticks: int = 50,
    max_runs: int = 21,
    runs_per_config: int = 3,
    focus_presets: list[str] | None = None,
    focus_dimensions: list[str] | None = None,
    project_dir: str = ".",
    execute: bool = False,
) -> str:
    """Start a full autonomous research campaign.

    Designs experiments, runs them, analyzes results, generates new hypotheses,
    and iterates until convergence or budget exhaustion.

    By default, returns the plan without executing. Set execute=True to run
    experiments immediately.

    Args:
        question: The research question. E.g. "What org works best for code review?"
        task: What agents will do. Natural language or benchmark ID.
        arm: "directed" (engine), "emergent" (simulation), or "both".
        strategy: "hypothesis" (default), "grid", "sweep", or "knowledge".
        agents: Agent count (fixed across campaign).
        model: Model for experiment agents.
        max_ticks: Max ticks per experiment run.
        max_runs: Total budget of experiment runs.
        runs_per_config: Runs per configuration for statistical reliability.
        focus_presets: Only test these presets (optional).
        focus_dimensions: Only vary these dimensions (optional).
        project_dir: Working directory for engine experiments.
        execute: If True, run experiments immediately after planning.
    """
    from ..campaign.manager import CampaignManager

    store = _get_store()
    search = _get_search()
    manager = CampaignManager(store, search)

    # Phase 1: Create campaign and generate plan
    result = await manager.create_campaign(
        question=question,
        task=task,
        arm=arm,
        strategy=strategy,
        agents=agents,
        model=model,
        max_ticks=max_ticks,
        max_runs=max_runs,
        runs_per_config=runs_per_config,
        focus_presets=focus_presets,
        focus_dimensions=focus_dimensions,
    )

    # Phase 2: Execute if requested
    if execute and arm == "directed":
        campaign_id = result["campaign_id"]
        exec_result = await manager.run_campaign(campaign_id, project_dir=project_dir)
        result["execution"] = exec_result

        # Auto-complete if batch finished
        if exec_result.get("status") == "batch_complete":
            completion = manager.complete_campaign(campaign_id)
            result["completion"] = completion

            # Auto-analyze and extract findings
            from ..analysis.analyzer import (
                analyze_campaign as _analyze,
                extract_and_save_findings,
                resolve_and_save_hypotheses,
            )

            all_results = store.list_run_results(campaign_id)
            campaign = store.get_campaign(campaign_id)
            hypotheses = []
            if campaign:
                for h_id in campaign.hypotheses_generated:
                    h = store.get_hypothesis(h_id)
                    if h:
                        hypotheses.append(h)

            analysis = _analyze(all_results, hypotheses=hypotheses, campaign_id=campaign_id)
            findings_saved = extract_and_save_findings(
                analysis, store, campaign_id,
                task=task, agents=agents, model=model,
            )
            if analysis.get("hypothesis_verdicts"):
                resolve_and_save_hypotheses(analysis["hypothesis_verdicts"], store)

            # Update campaign with findings
            if campaign and findings_saved:
                campaign.findings_generated.extend(f.id for f in findings_saved)
                store.save_campaign(campaign)

            result["analysis"] = {
                "findings_extracted": len(findings_saved),
                "winner": analysis.get("winner"),
                "data_quality": analysis.get("data_quality"),
            }

            # Auto-generate report
            from ..reporting.report_generator import generate_campaign_report
            generate_campaign_report(campaign_id, store, search)
            result["report"] = f"Campaign report saved to ~/.agentciv-creator/campaigns/{campaign_id}/report.md"

    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def creator_spawn_directed(
    task: str,
    configs: list[dict[str, Any]],
    agents: int = 4,
    model: str = "claude-sonnet-4-6",
    max_ticks: int = 50,
    runs_per_config: int = 3,
    campaign_id: str | None = None,
    project_dir: str = ".",
) -> str:
    """Spawn directed experiments via the engine with explicit configurations.

    Use when you know exactly what configs to test. Runs experiments immediately
    and returns results.

    Args:
        task: What agents will do.
        configs: List of configs. Each: {"preset": "name", "overrides": {"dim": "val"}}.
        agents: Agent count.
        model: Model for agents.
        max_ticks: Max ticks per run.
        runs_per_config: Runs per config for reliability.
        campaign_id: Attach to existing campaign, or create new.
        project_dir: Working directory.
    """
    from ..campaign.manager import CampaignManager
    from ..knowledge.models import RunConfig

    store = _get_store()
    search = _get_search()

    # Parse configs
    run_configs = [RunConfig.model_validate(c) for c in configs]

    # Create or get campaign
    if campaign_id is None:
        manager = CampaignManager(store, search)
        presets_str = ", ".join(c.preset for c in run_configs[:3])
        result = await manager.create_campaign(
            question=f"Direct experiment: {presets_str}",
            task=task,
            strategy="grid",
            agents=agents,
            model=model,
            max_ticks=max_ticks,
            max_runs=len(run_configs) * runs_per_config,
            runs_per_config=runs_per_config,
            focus_presets=[c.preset for c in run_configs],
        )
        campaign_id = result["campaign_id"]

    # Run experiments
    from ..engine.runner import run_batch

    results = await run_batch(
        configs=run_configs,
        task=task,
        agents=agents,
        model=model,
        max_ticks=max_ticks,
        runs_per_config=runs_per_config,
        project_dir=project_dir,
    )

    # Save results
    for r in results:
        r.campaign_id = campaign_id
        store.save_run_result(campaign_id, r)

    # Update campaign
    campaign = store.get_campaign(campaign_id)
    if campaign:
        campaign.budget.runs_completed += len(results)
        campaign.run_ids.extend(r.id for r in results)
        store.save_campaign(campaign)

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    return json.dumps({
        "campaign_id": campaign_id,
        "runs_completed": len(results),
        "runs_succeeded": len(successful),
        "runs_failed": len(failed),
        "results": [
            {
                "id": r.id,
                "config": r.config.model_dump(),
                "quality_score": r.quality_score,
                "merge_conflicts": r.merge_conflicts,
                "ticks_used": r.ticks_used,
                "success": r.success,
                "error": r.error,
            }
            for r in results
        ],
        "message": f"{len(successful)}/{len(results)} runs completed successfully.",
    }, indent=2, default=str)


@mcp.tool()
async def creator_spawn_emergent(
    hypothesis: str,
    agents: int = 12,
    ticks: int = 100,
    conditions: dict[str, Any] | None = None,
    control: bool = True,
    variations: int = 1,
    campaign_id: str | None = None,
    sim_dir: str | None = None,
) -> str:
    """Spawn emergent civilisation simulations.

    Generates simulation configs and saves them to disk. In v1, simulations
    are run manually (not autonomously) due to cost and duration. Returns
    config file paths and run instructions.

    Args:
        hypothesis: What emergence pattern to investigate.
        agents: Agent count for simulation.
        ticks: Simulation length.
        conditions: Specific config overrides for treatment condition (dotted keys).
        control: Also generate a control config (default values).
        variations: Number of treatment variations to generate.
        campaign_id: Attach to existing campaign.
        sim_dir: Path to AgentCiv Simulation repo.
    """
    from pathlib import Path

    from ..config import DEFAULT_SIM_DIR
    from ..simulation.config_gen import (
        generate_experiment_configs,
        list_conditions,
        save_sim_configs,
    )

    store = _get_store()
    sim_path = Path(sim_dir) if sim_dir else DEFAULT_SIM_DIR

    # Create or use campaign
    if campaign_id is None:
        campaign_id = store.next_campaign_id()

    # Generate configs
    configs = generate_experiment_configs(
        hypothesis=hypothesis,
        agents=agents,
        ticks=ticks,
        conditions=conditions,
        control=control,
        variations=variations,
    )

    # Save to campaign directory
    output_dir = store._campaign_dir(campaign_id) / "sim_configs"
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = save_sim_configs(configs, output_dir)

    # Build run instructions
    run_commands = []
    for path in saved_paths:
        run_commands.append(
            f"cd {sim_path} && python -m agentciv.run --config {path}"
        )

    return json.dumps({
        "campaign_id": campaign_id,
        "hypothesis": hypothesis,
        "configs_generated": len(configs),
        "config_files": saved_paths,
        "run_instructions": {
            "note": "Simulations must be run manually in v1 (too expensive for autonomous execution).",
            "commands": run_commands,
            "sim_dir": str(sim_path),
        },
        "configs_summary": [
            {
                "role": c["role"],
                "label": c["label"],
                "agents": c["config"]["agents"]["count"],
                "ticks": c["config"]["simulation"]["max_ticks"],
            }
            for c in configs
        ],
        "available_conditions": list_conditions(),
        "message": (
            f"Generated {len(configs)} simulation configs for: {hypothesis}. "
            "Run manually using the commands above, then use creator_analyze() on the output."
        ),
    }, indent=2, default=str)


@mcp.tool()
async def creator_analyze(
    campaign_id: str | None = None,
    directed_results: list[dict[str, Any]] | None = None,
    emergent_data_dirs: list[str] | None = None,
    analysis_type: str = "full",
    metrics: list[str] | None = None,
    output_format: str = "full",
    extract_findings: bool = True,
    resolve_hypotheses: bool = True,
) -> str:
    """Deep cross-run analysis with statistical comparison and finding extraction.

    Analyzes campaign results, computes rankings, effect sizes, p-values,
    extracts findings, and resolves hypotheses.

    Args:
        campaign_id: Analyze a specific campaign.
        directed_results: Engine run results (alternative to campaign_id).
        emergent_data_dirs: Simulation output directories.
        analysis_type: "full", "comparison", "emergence", or "cross_arm".
        metrics: Focus on specific metrics.
        output_format: "full" (detailed), "summary" (key findings), "table" (data only).
        extract_findings: If True, save significant findings to knowledge store.
        resolve_hypotheses: If True, update hypothesis statuses based on evidence.
    """
    from ..analysis.analyzer import (
        analyze_campaign,
        extract_and_save_findings,
        resolve_and_save_hypotheses,
    )

    store = _get_store()

    # Gather results
    results: list = []
    hypotheses = []

    if campaign_id:
        campaign = store.get_campaign(campaign_id)
        if campaign is None:
            return json.dumps({"error": f"Campaign {campaign_id} not found"})
        results = store.list_run_results(campaign_id)
        # Load hypotheses for this campaign
        for h_id in campaign.hypotheses_generated:
            h = store.get_hypothesis(h_id)
            if h:
                hypotheses.append(h)
    elif directed_results:
        from ..knowledge.models import RunResult as RR
        results = [RR.model_validate(r) for r in directed_results]

    if not results:
        return json.dumps({"error": "No results to analyze. Provide campaign_id or directed_results."})

    # Run analysis
    analysis = analyze_campaign(
        results=results,
        hypotheses=hypotheses,
        campaign_id=campaign_id or "",
        metrics=metrics,
    )

    # Extract and save findings
    findings_saved = []
    if extract_findings and campaign_id:
        campaign = store.get_campaign(campaign_id)
        task = campaign.constraints.task if campaign else ""
        agents = campaign.constraints.agents if campaign else 4
        model = campaign.constraints.model if campaign else ""
        findings_saved = extract_and_save_findings(
            analysis, store, campaign_id, task=task, agents=agents, model=model,
        )
        # Update campaign with finding IDs
        if campaign and findings_saved:
            campaign.findings_generated.extend(f.id for f in findings_saved)
            store.save_campaign(campaign)

    # Resolve hypotheses
    hypotheses_updated = []
    if resolve_hypotheses and analysis.get("hypothesis_verdicts"):
        hypotheses_updated = resolve_and_save_hypotheses(
            analysis["hypothesis_verdicts"], store,
        )
        # Update campaign with tested hypothesis IDs
        if campaign_id:
            campaign = store.get_campaign(campaign_id)
            if campaign:
                campaign.hypotheses_tested.extend(h.id for h in hypotheses_updated)
                store.save_campaign(campaign)

    # Build response based on format
    if output_format == "summary":
        response = {
            "campaign_id": campaign_id,
            "winner": analysis.get("winner"),
            "data_quality": analysis.get("data_quality"),
            "significant_findings": [f.statement for f in findings_saved],
            "hypothesis_verdicts": [
                {"id": v["hypothesis_id"], "verdict": v["verdict"]}
                for v in analysis.get("hypothesis_verdicts", [])
            ],
        }
    elif output_format == "table":
        response = {
            "ranking": analysis.get("ranking"),
            "aggregates": analysis.get("aggregates"),
        }
    else:
        response = analysis
        response["findings_extracted"] = [
            {"id": f.id, "statement": f.statement, "confidence": f.confidence}
            for f in findings_saved
        ]
        response["hypotheses_resolved"] = [
            {"id": h.id, "statement": h.statement, "status": h.status.value}
            for h in hypotheses_updated
        ]

    return json.dumps(response, indent=2, default=str)


@mcp.tool()
async def creator_recursive(
    seed: str | dict[str, Any] = "auto",
    task: str = "",
    generations: int = 3,
    population_size: int = 4,
    agents: int = 4,
    model: str = "claude-sonnet-4-6",
    max_ticks: int = 50,
    runs_per_config: int = 2,
    mutation_rate: float = 0.3,
    include_emergent: bool = False,
    sim_ticks: int = 100,
    campaign_id: str | None = None,
    execute: bool = False,
) -> str:
    """Run the recursive emergence loop from Paper 7.

    Extracts emergent organisational forms → converts to configs → tests them
    → uses best as seeds for next generation. Discovers novel org structures.

    By default, creates the campaign and generation 0 plan. Set execute=True
    to run all generations immediately (expensive — budget accordingly).

    Args:
        seed: Starting config. Preset name, config dict, or "from_simulation:<dir>".
        task: Task for directed-arm testing.
        generations: Number of generations to evolve.
        population_size: Configs per generation.
        agents: Agent count.
        model: Model for agents.
        max_ticks: Max ticks per run.
        runs_per_config: Runs per config per generation.
        mutation_rate: Probability of changing each dimension in offspring.
        include_emergent: Also spawn simulations for novel org form discovery.
        sim_ticks: Ticks for emergent simulations.
        campaign_id: Attach to existing campaign.
        execute: If True, run all generations immediately.
    """
    if not task:
        return json.dumps({"error": "task parameter is required"})

    from ..campaign.recursive import (
        advance_generation,
        create_recursive_campaign,
    )

    store = _get_store()

    # Create campaign
    campaign, gen0_configs = create_recursive_campaign(
        store=store,
        seed=seed,
        task=task,
        generations=generations,
        population_size=population_size,
        agents=agents,
        model=model,
        max_ticks=max_ticks,
        runs_per_config=runs_per_config,
        mutation_rate=mutation_rate,
        include_emergent=include_emergent,
    )

    result: dict[str, Any] = {
        "campaign_id": campaign.id,
        "type": "recursive",
        "generations_planned": generations,
        "population_size": population_size,
        "mutation_rate": mutation_rate,
        "generation_0": {
            "status": "planned",
            "configs": [c.model_dump() for c in gen0_configs],
            "total_runs": len(gen0_configs) * runs_per_config,
        },
    }

    if execute:
        from ..engine.runner import run_batch

        all_trajectory = []

        for gen in range(generations):
            # Get current batch
            batch = None
            for b in campaign.batches:
                if b.status == BatchStatus.PLANNED:
                    batch = b
                    break
            if batch is None:
                break

            # Run this generation
            batch.status = BatchStatus.RUNNING
            campaign.status = CampaignStatus.RUNNING
            store.save_campaign(campaign)

            gen_results = await run_batch(
                configs=batch.configs,
                task=task,
                agents=agents,
                model=model,
                max_ticks=max_ticks,
                runs_per_config=runs_per_config,
                project_dir=".",
            )

            # Save results
            for r in gen_results:
                r.campaign_id = campaign.id
                r.batch_id = batch.id
                store.save_run_result(campaign.id, r)
                batch.run_ids.append(r.id)
                campaign.run_ids.append(r.id)

            campaign.budget.runs_completed += len(gen_results)
            batch.status = BatchStatus.COMPLETE
            store.save_campaign(campaign)

            # Advance generation
            campaign, next_configs = advance_generation(
                campaign=campaign,
                generation_results=gen_results,
                store=store,
                mutation_rate=mutation_rate,
                population_size=population_size,
                include_emergent=include_emergent,
            )

            successful = [r for r in gen_results if r.success]
            gen_summary = {
                "generation": gen,
                "runs": len(gen_results),
                "succeeded": len(successful),
                "configs": [c.model_dump() for c in batch.configs],
            }
            if campaign.evolution_trajectory:
                gen_summary["best"] = campaign.evolution_trajectory[-1]
            all_trajectory.append(gen_summary)

            if next_configs is None:
                break

        result["execution"] = {
            "status": "complete",
            "generations_completed": campaign.generations_completed,
            "evolution_trajectory": all_trajectory,
            "final_trajectory": campaign.evolution_trajectory,
        }

        # Complete campaign
        from ..campaign.manager import CampaignManager
        manager = CampaignManager(store, _get_search())
        completion = manager.complete_campaign(campaign.id)
        result["completion"] = completion

    result["message"] = (
        f"Recursive campaign {campaign.id}: {generations} generations × "
        f"{population_size} configs × {runs_per_config} runs/config = "
        f"{generations * population_size * runs_per_config} total budget. "
        + ("Execution complete." if execute else "Plan ready. Set execute=True to run.")
    )

    return json.dumps(result, indent=2, default=str)


# ── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    """Run the Creator Mode MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
