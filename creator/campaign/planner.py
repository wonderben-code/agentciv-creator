"""Campaign planner — generates experiment plans from questions + strategies.

The hypothesis engine uses the Anthropic API (Sonnet for speed) to generate
testable predictions from research questions + existing knowledge.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ..config import ALL_PRESETS, DIMENSION_VALUES, SIM_CONDITIONS, SIM_SWEEP_PARAMS
from ..knowledge.index import SearchIndex
from ..knowledge.models import (
    Arm,
    Batch,
    BatchStatus,
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    Strategy,
    TestDesign,
)
from ..knowledge.store import KnowledgeStore
from .strategies import (
    plan_emergence_from_hypotheses,
    plan_emergence_grid,
    plan_emergence_sweep,
    plan_from_hypotheses,
    plan_grid,
    plan_knowledge,
    plan_sweep,
)

log = logging.getLogger(__name__)

# ── Hypothesis Engine ────────────────────────────────────────────────────────

HYPOTHESIS_SYSTEM_PROMPT = """\
You are a research scientist designing organisational experiments for multi-agent AI systems.

You will be given:
- A research question about how to organise AI agent teams
- A task description that agents will perform
- Constraints (agent count, model, etc.)
- Any existing knowledge from prior experiments

Your job: generate 3-5 specific, testable hypotheses about what organisational structure \
will work best and why. Each hypothesis must specify:
- statement: The prediction (clear, falsifiable)
- independent_variable: Which organisational dimension to vary
- treatment: The condition you expect to win
- control: The baseline comparison
- outcome_metric: What to measure (quality_score, merge_conflicts, ticks_used)
- expected_direction: "treatment > control" or "treatment < control"
- rationale: WHY you expect this (1-2 sentences)
- priority: "high", "medium", or "low"
- tags: relevant keywords

Available organisational presets (each is a full configuration):
{presets}

Available dimensions (can override individually):
{dimensions}

Respond with a JSON array of hypotheses. Nothing else — no markdown, no explanation.

Example:
[
  {{
    "statement": "Distributed authority outperforms hierarchical for code review at 8+ agents",
    "independent_variable": "authority",
    "treatment": "distributed",
    "control": "hierarchy",
    "outcome_metric": "quality_score",
    "expected_direction": "treatment > control",
    "rationale": "Single coordinator becomes a throughput bottleneck above 6-8 agents",
    "priority": "high",
    "tags": ["authority", "scaling", "code_review"]
  }}
]
"""

HYPOTHESIS_USER_TEMPLATE = """\
Research question: {question}

Task: {task}

Constraints:
- Agent count: {agents}
- Model: {model}
- Max ticks: {max_ticks}

{knowledge_context}

Generate 3-5 testable hypotheses for this research question."""


async def generate_hypotheses(
    question: str,
    task: str,
    agents: int,
    model: str,
    max_ticks: int,
    store: KnowledgeStore,
    search: SearchIndex,
    session_manager: Any = None,
    campaign_id: str = "",
) -> list[Hypothesis]:
    """Use LLM to generate testable hypotheses from a research question.

    Falls back to heuristic hypotheses if the API call fails.
    If session_manager is provided, captures raw LLM request/response.
    """
    # Gather existing knowledge context
    existing = search.query_findings(question, max_results=5)
    knowledge_lines: list[str] = []
    if existing:
        knowledge_lines.append("Existing knowledge from prior experiments:")
        for r in existing:
            knowledge_lines.append(f"  - {r.finding.statement} (confidence: {r.finding.confidence})")
    else:
        knowledge_lines.append("No prior experiments — this is a fresh exploration.")

    untested = store.list_hypotheses(status=HypothesisStatus.UNTESTED)
    if untested:
        knowledge_lines.append(f"\n{len(untested)} untested hypotheses from prior campaigns:")
        for h in untested[:3]:
            knowledge_lines.append(f"  - {h.statement}")

    knowledge_context = "\n".join(knowledge_lines)

    # Format prompts
    presets_str = ", ".join(ALL_PRESETS)
    dims_str = "\n".join(f"  {d}: {', '.join(v)}" for d, v in DIMENSION_VALUES.items())

    system = HYPOTHESIS_SYSTEM_PROMPT.format(presets=presets_str, dimensions=dims_str)
    user = HYPOTHESIS_USER_TEMPLATE.format(
        question=question,
        task=task,
        agents=agents,
        model=model,
        max_ticks=max_ticks,
        knowledge_context=knowledge_context,
    )

    try:
        import time as _time

        import anthropic
        client = anthropic.AsyncAnthropic()
        t0 = _time.monotonic()
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        duration_ms = (_time.monotonic() - t0) * 1000

        raw = response.content[0].text.strip()

        # Capture raw LLM interaction if session is active
        if session_manager is not None:
            input_tok = getattr(response.usage, "input_tokens", 0)
            output_tok = getattr(response.usage, "output_tokens", 0)
            session_manager.capture_llm(
                purpose="hypothesis_generation",
                model="claude-sonnet-4-6",
                system_prompt=system,
                user_prompt=user,
                raw_response=raw,
                input_tokens=input_tok,
                output_tokens=output_tok,
                duration_ms=duration_ms,
                campaign_id=campaign_id,
            )
            session_manager.track_cost(
                source="hypothesis_engine",
                campaign_id=campaign_id,
                input_tokens=input_tok,
                output_tokens=output_tok,
            )

        # Handle markdown code fences
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        hypotheses_data = json.loads(raw)
        return _parse_hypotheses(hypotheses_data, store)

    except Exception as e:
        log.warning("LLM hypothesis generation failed (%s), using heuristics", e)
        return _heuristic_hypotheses(question, task, agents, store)


def _parse_hypotheses(data: list[dict[str, Any]], store: KnowledgeStore) -> list[Hypothesis]:
    """Parse LLM output into Hypothesis objects."""
    hypotheses: list[Hypothesis] = []
    for item in data:
        h_id = store.next_hypothesis_id()
        # Save immediately so next_hypothesis_id increments
        h = Hypothesis(
            id=h_id,
            statement=item.get("statement", ""),
            status=HypothesisStatus.UNTESTED,
            test_design=TestDesign(
                independent_variable=item.get("independent_variable", ""),
                treatment=item.get("treatment", ""),
                control=item.get("control", ""),
                outcome_metric=item.get("outcome_metric", "quality_score"),
                expected_direction=item.get("expected_direction", ""),
            ),
            source="hypothesis_engine",
            generated_from="LLM analysis of research question",
            priority=HypothesisPriority(item.get("priority", "medium")),
            tags=item.get("tags", []),
        )
        store.save_hypothesis(h)
        hypotheses.append(h)
    return hypotheses


def _heuristic_hypotheses(
    question: str,
    task: str,
    agents: int,
    store: KnowledgeStore,
) -> list[Hypothesis]:
    """Generate basic hypotheses when LLM is unavailable."""
    hypotheses: list[Hypothesis] = []
    q_lower = question.lower()

    # Always test: does the purpose-built preset matter?
    if any(word in q_lower for word in ["code", "review"]):
        base_preset = "code-review"
    elif any(word in q_lower for word in ["creative", "innovation", "explore"]):
        base_preset = "research-lab"
    elif any(word in q_lower for word in ["fast", "speed", "quick"]):
        base_preset = "hackathon"
    else:
        base_preset = "collaborative"

    # H1: Purpose-built vs generic
    h1 = Hypothesis(
        id=store.next_hypothesis_id(),
        statement=f"{base_preset} preset will outperform generic presets for this task",
        status=HypothesisStatus.UNTESTED,
        test_design=TestDesign(
            independent_variable="preset",
            treatment=base_preset,
            control="collaborative",
            outcome_metric="quality_score",
            expected_direction="treatment > control",
        ),
        priority=HypothesisPriority.HIGH,
        tags=["preset", base_preset],
    )
    store.save_hypothesis(h1)
    hypotheses.append(h1)

    # H2: Hierarchical bottleneck at agent count
    if agents >= 6:
        h2 = Hypothesis(
            id=store.next_hypothesis_id(),
            statement=f"Hierarchical bottlenecks at {agents} agents due to coordinator throughput ceiling",
            status=HypothesisStatus.UNTESTED,
            test_design=TestDesign(
                independent_variable="authority",
                treatment="hierarchy",
                control="distributed",
                outcome_metric="quality_score",
                expected_direction="control > treatment",
                agent_count=agents,
            ),
            priority=HypothesisPriority.HIGH,
            tags=["authority", "scaling", "bottleneck"],
        )
        store.save_hypothesis(h2)
        hypotheses.append(h2)

    # H3: Auto mode converges on effective structure
    h3 = Hypothesis(
        id=store.next_hypothesis_id(),
        statement="Auto mode (self-organisation) converges on an effective structure within budget",
        status=HypothesisStatus.UNTESTED,
        test_design=TestDesign(
            independent_variable="preset",
            treatment="auto",
            control=base_preset,
            outcome_metric="quality_score",
            expected_direction="treatment >= control",
        ),
        priority=HypothesisPriority.MEDIUM,
        tags=["auto", "self_organisation"],
    )
    store.save_hypothesis(h3)
    hypotheses.append(h3)

    return hypotheses


# ── Emergence Hypothesis Engine ──────────────────────────────────────────────

EMERGENCE_SYSTEM_PROMPT = """\
You are a research scientist designing emergence experiments for AI civilisation simulations.

You will be given:
- A research question about emergent behaviour in AI civilisations
- Constraints (agent count, ticks, model)
- Any existing knowledge from prior experiments

The simulation creates a world where AI agents with Maslow-like drives interact, communicate, \
build structures, discover innovations, form social bonds, propose governance rules, and develop \
specialisations. Your job: generate 3-5 testable hypotheses about what environmental conditions \
produce the most interesting emergent behaviour.

Each hypothesis must specify:
- statement: The prediction (clear, falsifiable)
- independent_variable: Which environmental parameter to vary
- treatment: The condition you expect to produce more emergence
- control: The baseline comparison
- outcome_metric: What to measure (emergence_score, governance, cooperation, innovation, etc.)
- expected_direction: "treatment > control" or "treatment < control"
- rationale: WHY you expect this (1-2 sentences)
- priority: "high", "medium", or "low"
- tags: relevant keywords

Available simulation conditions (named environments):
{conditions}

Available sweep parameters (continuous variables):
{sweep_params}

Respond with a JSON array of hypotheses. Nothing else — no markdown, no explanation.

Example:
[
  {{
    "statement": "Resource scarcity increases governance emergence as agents need rules to manage shared resources",
    "independent_variable": "condition",
    "treatment": "scarce",
    "control": "abundant",
    "outcome_metric": "emergence_score",
    "expected_direction": "treatment > control",
    "rationale": "Scarcity creates coordination pressure that incentivises collective rule-making",
    "priority": "high",
    "tags": ["scarcity", "governance", "cooperation"]
  }}
]
"""

EMERGENCE_USER_TEMPLATE = """\
Research question: {question}

Constraints:
- Agent count: {agents}
- Ticks: {ticks}
- Model: {model}

{knowledge_context}

Generate 3-5 testable hypotheses about emergent behaviour under different conditions."""


async def generate_emergence_hypotheses(
    question: str,
    agents: int,
    model: str,
    ticks: int,
    store: KnowledgeStore,
    search: SearchIndex,
    session_manager: Any = None,
    campaign_id: str = "",
) -> list[Hypothesis]:
    """Use LLM to generate emergence-specific hypotheses.

    Falls back to heuristic hypotheses if the API call fails.
    """
    # Gather existing knowledge
    existing = search.query_findings(question, max_results=5)
    knowledge_lines: list[str] = []
    if existing:
        knowledge_lines.append("Existing knowledge from prior experiments:")
        for r in existing:
            knowledge_lines.append(f"  - {r.finding.statement} (confidence: {r.finding.confidence})")
    else:
        knowledge_lines.append("No prior experiments — this is a fresh exploration.")

    knowledge_context = "\n".join(knowledge_lines)

    conditions_str = ", ".join(SIM_CONDITIONS)
    sweep_str = "\n".join(f"  {p}: {v}" for p, v in SIM_SWEEP_PARAMS.items())

    system = EMERGENCE_SYSTEM_PROMPT.format(
        conditions=conditions_str, sweep_params=sweep_str,
    )
    user = EMERGENCE_USER_TEMPLATE.format(
        question=question, agents=agents, ticks=ticks,
        model=model, knowledge_context=knowledge_context,
    )

    try:
        import time as _time

        import anthropic
        client = anthropic.AsyncAnthropic()
        t0 = _time.monotonic()
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        duration_ms = (_time.monotonic() - t0) * 1000

        raw = response.content[0].text.strip()

        if session_manager is not None:
            input_tok = getattr(response.usage, "input_tokens", 0)
            output_tok = getattr(response.usage, "output_tokens", 0)
            session_manager.capture_llm(
                purpose="emergence_hypothesis_generation",
                model="claude-sonnet-4-6",
                system_prompt=system, user_prompt=user,
                raw_response=raw,
                input_tokens=input_tok, output_tokens=output_tok,
                duration_ms=duration_ms, campaign_id=campaign_id,
            )
            session_manager.track_cost(
                source="emergence_hypothesis_engine",
                campaign_id=campaign_id,
                input_tokens=input_tok, output_tokens=output_tok,
            )

        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        hypotheses_data = json.loads(raw)
        return _parse_hypotheses(hypotheses_data, store)

    except Exception as e:
        log.warning("LLM emergence hypothesis generation failed (%s), using heuristics", e)
        return _heuristic_emergence_hypotheses(question, agents, store)


def _heuristic_emergence_hypotheses(
    question: str,
    agents: int,
    store: KnowledgeStore,
) -> list[Hypothesis]:
    """Generate basic emergence hypotheses when LLM is unavailable."""
    hypotheses: list[Hypothesis] = []

    # H1: Scarcity drives governance
    h1 = Hypothesis(
        id=store.next_hypothesis_id(),
        statement="Resource scarcity increases governance emergence",
        status=HypothesisStatus.UNTESTED,
        test_design=TestDesign(
            independent_variable="condition",
            treatment="scarce",
            control="abundant",
            outcome_metric="emergence_score",
            expected_direction="treatment > control",
        ),
        priority=HypothesisPriority.HIGH,
        tags=["scarcity", "governance", "emergence"],
    )
    store.save_hypothesis(h1)
    hypotheses.append(h1)

    # H2: Density increases social structure
    h2 = Hypothesis(
        id=store.next_hypothesis_id(),
        statement="High population density accelerates social structure formation",
        status=HypothesisStatus.UNTESTED,
        test_design=TestDesign(
            independent_variable="condition",
            treatment="dense",
            control="sparse",
            outcome_metric="emergence_score",
            expected_direction="treatment > control",
        ),
        priority=HypothesisPriority.HIGH,
        tags=["density", "social_structure", "emergence"],
    )
    store.save_hypothesis(h2)
    hypotheses.append(h2)

    # H3: Innovation features produce richer emergence
    h3 = Hypothesis(
        id=store.next_hypothesis_id(),
        statement="Enabling all innovation features produces higher composite emergence",
        status=HypothesisStatus.UNTESTED,
        test_design=TestDesign(
            independent_variable="condition",
            treatment="innovative",
            control="default",
            outcome_metric="emergence_score",
            expected_direction="treatment > control",
        ),
        priority=HypothesisPriority.MEDIUM,
        tags=["innovation", "emergence"],
    )
    store.save_hypothesis(h3)
    hypotheses.append(h3)

    return hypotheses


# ── Plan Generation ──────────────────────────────────────────────────────────

async def generate_plan(
    question: str,
    task: str,
    strategy: Strategy,
    agents: int,
    model: str,
    max_ticks: int,
    max_runs: int,
    runs_per_config: int,
    focus_presets: list[str] | None,
    focus_dimensions: list[str] | None,
    store: KnowledgeStore,
    search: SearchIndex,
    arm: Arm = Arm.DIRECTED,
) -> tuple[Batch, list[Hypothesis], str]:
    """Generate a batch plan using the specified strategy.

    Dispatches to directed (Engine) or emergent (Simulation) strategies
    based on the campaign arm.

    Returns (batch, hypotheses, message).
    """
    hypotheses: list[Hypothesis] = []

    if arm == Arm.EMERGENT:
        # Emergence-specific planning
        configs, rationale, hypotheses = await _plan_emergence(
            question=question,
            strategy=strategy,
            agents=agents,
            model=model,
            ticks=max_ticks,
            max_runs=max_runs,
            runs_per_config=runs_per_config,
            focus_conditions=focus_presets,
            focus_params=focus_dimensions,
            store=store,
            search=search,
        )
    else:
        # Directed (Engine) planning — existing logic
        if strategy == Strategy.GRID:
            configs, rationale = plan_grid(max_runs, runs_per_config, focus_presets)

        elif strategy == Strategy.SWEEP:
            base = focus_presets[0] if focus_presets else "collaborative"
            configs, rationale = plan_sweep(base, max_runs, runs_per_config, focus_dimensions)

        elif strategy == Strategy.HYPOTHESIS:
            hypotheses = await generate_hypotheses(
                question, task, agents, model, max_ticks, store, search,
            )
            configs, rationale = plan_from_hypotheses(
                hypotheses, max_runs, runs_per_config, focus_presets,
            )

        elif strategy == Strategy.KNOWLEDGE:
            configs, gap_hypotheses, rationale = plan_knowledge(
                store, search, question, max_runs, runs_per_config, focus_presets,
            )
            hypotheses = gap_hypotheses

        else:
            configs, rationale = plan_grid(max_runs, runs_per_config, focus_presets)

    batch = Batch(
        id="B001",
        batch_number=1,
        status=BatchStatus.PLANNED,
        configs=configs,
        runs_per_config=runs_per_config,
        total_runs=len(configs) * runs_per_config,
        rationale=rationale,
    )

    arm_label = "emergence" if arm == Arm.EMERGENT else "directed"
    message = (
        f"Batch 1 planned ({arm_label}): {len(configs)} configs × {runs_per_config} runs = "
        f"{batch.total_runs} experiments. Strategy: {strategy.value}."
    )

    return batch, hypotheses, message


async def _plan_emergence(
    question: str,
    strategy: Strategy,
    agents: int,
    model: str,
    ticks: int,
    max_runs: int,
    runs_per_config: int,
    focus_conditions: list[str] | None,
    focus_params: list[str] | None,
    store: KnowledgeStore,
    search: SearchIndex,
) -> tuple[list[RunConfig], str, list[Hypothesis]]:
    """Generate an emergence experiment plan. Returns (configs, rationale, hypotheses)."""
    hypotheses: list[Hypothesis] = []

    if strategy == Strategy.GRID:
        configs, rationale = plan_emergence_grid(max_runs, runs_per_config, focus_conditions)

    elif strategy == Strategy.SWEEP:
        base = focus_conditions[0] if focus_conditions else "default"
        configs, rationale = plan_emergence_sweep(base, max_runs, runs_per_config, focus_params)

    elif strategy == Strategy.HYPOTHESIS:
        hypotheses = await generate_emergence_hypotheses(
            question, agents, model, ticks, store, search,
        )
        configs, rationale = plan_emergence_from_hypotheses(
            hypotheses, max_runs, runs_per_config, focus_conditions,
        )

    else:
        # Default to grid for emergence
        configs, rationale = plan_emergence_grid(max_runs, runs_per_config, focus_conditions)

    return configs, rationale, hypotheses
