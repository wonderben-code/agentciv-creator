"""Campaign planner — generates experiment plans from questions + strategies.

The hypothesis engine uses the Anthropic API (Sonnet for speed) to generate
testable predictions from research questions + existing knowledge.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ..config import ALL_PRESETS, DIMENSION_VALUES
from ..knowledge.index import SearchIndex
from ..knowledge.models import (
    Batch,
    BatchStatus,
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    Strategy,
    TestDesign,
)
from ..knowledge.store import KnowledgeStore
from .strategies import plan_from_hypotheses, plan_grid, plan_knowledge, plan_sweep

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
) -> list[Hypothesis]:
    """Use LLM to generate testable hypotheses from a research question.

    Falls back to heuristic hypotheses if the API call fails.
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
        import anthropic
        client = anthropic.AsyncAnthropic()
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        raw = response.content[0].text.strip()
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
) -> tuple[Batch, list[Hypothesis], str]:
    """Generate a batch plan using the specified strategy.

    Returns (batch, hypotheses, message).
    """
    hypotheses: list[Hypothesis] = []

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

    message = (
        f"Batch 1 planned: {len(configs)} configs × {runs_per_config} runs = "
        f"{batch.total_runs} experiments. Strategy: {strategy.value}."
    )

    return batch, hypotheses, message
