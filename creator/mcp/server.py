"""Creator Mode MCP server — 7 tools for autonomous organisational architecture.

Phase 1 implements:
  - creator_info()    — documentation and capabilities
  - creator_status()  — dashboard and campaign management
  - creator_knowledge() — query the knowledge store

Remaining tools are wired up in later phases:
  - creator_explore()         → Phase 2 (planning) + Phase 3 (execution)
  - creator_spawn_directed()  → Phase 5
  - creator_spawn_emergent()  → Phase 5
  - creator_analyze()         → Phase 4
  - creator_recursive()       → Phase 6
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import __version__
from ..config import ALL_DIMENSIONS, ALL_PRESETS, DIMENSION_VALUES, EMERGENCE_DIMENSIONS
from ..knowledge.index import SearchIndex
from ..knowledge.models import (
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
    """Handle action=recommend.

    In Phase 1, this returns a basic recommendation based on findings.
    Phase 5 adds a proper recommendation engine (creator/reporting/designer.py).
    """
    findings = store.list_findings()

    if not findings:
        return json.dumps({
            "recommendation": None,
            "confidence": 0.0,
            "data_quality": "insufficient",
            "message": "No findings in knowledge store yet. Run a campaign first with creator_explore().",
        })

    # Filter by task type if provided
    relevant = findings
    if task_type:
        relevant = [f for f in findings if task_type in f.conditions.task_types] or findings

    # Sort by confidence
    relevant.sort(key=lambda f: f.confidence, reverse=True)
    best = relevant[0]

    return json.dumps({
        "recommendation": {
            "based_on": best.id,
            "statement": best.statement,
            "confidence": best.confidence,
        },
        "alternatives": [
            {"id": f.id, "statement": f.statement, "confidence": f.confidence}
            for f in relevant[1:4]
        ],
        "data_quality": (
            "strong" if len(relevant) >= 10
            else "good" if len(relevant) >= 5
            else "limited" if len(relevant) >= 2
            else "insufficient"
        ),
        "message": "Full config recommendations available after Phase 5 (designer.py).",
    }, indent=2, default=str)


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

    Use when you know exactly what configs to test.

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
    return json.dumps({
        "status": "not_yet_implemented",
        "phase": "Phase 5",
        "message": "creator_spawn_directed() arrives in Phase 5.",
    })


@mcp.tool()
async def creator_spawn_emergent(
    hypothesis: str,
    agents: int = 12,
    ticks: int = 100,
    conditions: dict[str, Any] | None = None,
    control: bool = True,
    variations: int = 1,
    campaign_id: str | None = None,
    sim_dir: str = str(None),
) -> str:
    """Spawn emergent civilisation simulations.

    Generates simulation config YAMLs and run commands. In v1, simulations
    are run manually (not autonomously) due to cost and duration.

    Args:
        hypothesis: What emergence pattern to investigate.
        agents: Agent count for simulation.
        ticks: Simulation length.
        conditions: Specific config overrides for treatment condition.
        control: Also generate a control config (default values).
        variations: Number of treatment variations to generate.
        campaign_id: Attach to existing campaign.
        sim_dir: Path to AgentCiv Simulation repo.
    """
    return json.dumps({
        "status": "not_yet_implemented",
        "phase": "Phase 5",
        "message": "creator_spawn_emergent() arrives in Phase 5.",
    })


@mcp.tool()
async def creator_analyze(
    campaign_id: str | None = None,
    directed_results: list[dict[str, Any]] | None = None,
    emergent_data_dirs: list[str] | None = None,
    analysis_type: str = "full",
    metrics: list[str] | None = None,
    format: str = "full",
) -> str:
    """Deep cross-run analysis with statistical comparison and finding extraction.

    Args:
        campaign_id: Analyze a specific campaign.
        directed_results: Engine run results (alternative to campaign_id).
        emergent_data_dirs: Simulation output directories.
        analysis_type: "full", "comparison", "emergence", or "cross_arm".
        metrics: Focus on specific metrics.
        format: "full" (detailed), "summary" (key findings), "table" (data only).
    """
    return json.dumps({
        "status": "not_yet_implemented",
        "phase": "Phase 4",
        "message": "creator_analyze() arrives in Phase 4.",
    })


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
) -> str:
    """Run the recursive emergence loop from Paper 7.

    Extracts emergent organisational forms → converts to configs → tests them
    → uses best as seeds for next generation. Discovers novel org structures.

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
    """
    return json.dumps({
        "status": "not_yet_implemented",
        "phase": "Phase 6",
        "message": "creator_recursive() arrives in Phase 6.",
    })


# ── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    """Run the Creator Mode MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
