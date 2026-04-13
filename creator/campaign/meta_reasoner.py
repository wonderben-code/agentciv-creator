"""Meta-reasoner — decides which sub-modules to use for a given goal.

Given a research question or goal, analyses it against Knowledge Store
findings, assesses coverage density in each arm, and recommends the
optimal campaign mode (DIRECTED, EMERGENT, or BOTH/HYBRID).

This is Concept 3: Creator Mode reasons about WHETHER and HOW to utilise
Engine and Simulation as sub-modules to achieve a goal.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..knowledge.index import SearchIndex
from ..knowledge.models import Arm, Coverage, Strategy
from ..knowledge.store import KnowledgeStore

log = logging.getLogger(__name__)


@dataclass
class ReasoningFactor:
    """A single factor in the meta-reasoner's decision."""

    name: str
    signal: str  # "directed", "emergent", or "both"
    weight: float  # 0.0 to 1.0
    explanation: str


@dataclass
class MetaRecommendation:
    """The meta-reasoner's recommendation for how to approach a goal."""

    arm: Arm
    strategy: Strategy
    confidence: float
    reasoning: str
    factors: list[ReasoningFactor] = field(default_factory=list)


def recommend(
    question: str,
    task: str,
    store: KnowledgeStore,
    search: SearchIndex,
) -> MetaRecommendation:
    """Analyse a goal and recommend the optimal campaign approach.

    Considers:
    1. Goal type (optimisation vs exploration vs understanding)
    2. Prior coverage (what do we already know in each arm?)
    3. Knowledge density (are prior findings relevant?)
    4. Task specificity (narrow → Engine, broad → Simulation, bridge → HYBRID)

    Returns a MetaRecommendation with the chosen arm, strategy, and
    transparent reasoning for the user.
    """
    factors: list[ReasoningFactor] = []

    # Factor 1: Goal type analysis
    goal_factor = _analyse_goal_type(question, task)
    factors.append(goal_factor)

    # Factor 2: Coverage analysis
    coverage = search.compute_coverage()
    coverage_factor = _analyse_coverage(question, coverage)
    factors.append(coverage_factor)

    # Factor 3: Existing knowledge relevance
    knowledge_factor = _analyse_knowledge(question, search)
    factors.append(knowledge_factor)

    # Factor 4: Task specificity
    task_factor = _analyse_task_specificity(question, task)
    factors.append(task_factor)

    # Aggregate signals
    directed_score = sum(
        f.weight for f in factors if f.signal == "directed"
    )
    emergent_score = sum(
        f.weight for f in factors if f.signal == "emergent"
    )
    both_score = sum(
        f.weight for f in factors if f.signal == "both"
    )

    # Decide arm
    if both_score >= directed_score and both_score >= emergent_score:
        arm = Arm.BOTH
    elif emergent_score > directed_score:
        arm = Arm.EMERGENT
    else:
        arm = Arm.DIRECTED

    # Decide strategy based on arm + knowledge state
    strategy = _pick_strategy(arm, store, search, question)

    # Confidence based on how decisive the signal is
    total = directed_score + emergent_score + both_score
    if total == 0:
        confidence = 0.5
    else:
        max_score = max(directed_score, emergent_score, both_score)
        confidence = max_score / total

    # Build reasoning string
    reasoning = _build_reasoning(arm, strategy, factors, confidence)

    return MetaRecommendation(
        arm=arm,
        strategy=strategy,
        confidence=round(confidence, 2),
        reasoning=reasoning,
        factors=factors,
    )


# ── Factor Analysers ─────────────────────────────────────────────────────────


def _analyse_goal_type(question: str, task: str) -> ReasoningFactor:
    """Determine if the goal is optimisation, exploration, or understanding."""
    q = question.lower()

    # Optimisation keywords → Engine (directed)
    optimisation_words = [
        "best", "optimal", "fastest", "most efficient", "highest quality",
        "improve", "maximise", "minimize", "outperform", "compare",
    ]
    # Exploration keywords → Simulation (emergent)
    exploration_words = [
        "emerge", "discover", "what happens", "explore", "observe",
        "evolve", "self-organise", "spontaneous", "natural", "civilisation",
    ]
    # Understanding keywords → Both
    understanding_words = [
        "why", "understand", "how does", "relationship between",
        "mechanism", "cause", "correlation", "pattern",
    ]

    opt_count = sum(1 for w in optimisation_words if w in q)
    exp_count = sum(1 for w in exploration_words if w in q)
    und_count = sum(1 for w in understanding_words if w in q)

    if opt_count > exp_count and opt_count > und_count:
        return ReasoningFactor(
            name="goal_type",
            signal="directed",
            weight=0.3,
            explanation=f"Goal appears to be optimisation/comparison — Engine is more efficient for finding best configs",
        )
    elif exp_count > opt_count and exp_count > und_count:
        return ReasoningFactor(
            name="goal_type",
            signal="emergent",
            weight=0.3,
            explanation=f"Goal is about emergence/exploration — Simulation reveals patterns Engine can't produce",
        )
    elif und_count > 0:
        return ReasoningFactor(
            name="goal_type",
            signal="both",
            weight=0.3,
            explanation="Goal seeks understanding — both arms provide complementary evidence",
        )
    else:
        return ReasoningFactor(
            name="goal_type",
            signal="directed",
            weight=0.15,
            explanation="Goal type unclear — defaulting to Engine (faster, cheaper)",
        )


def _analyse_coverage(question: str, coverage: Coverage) -> ReasoningFactor:
    """Check where we have coverage gaps — recommend filling them."""
    directed_tested = len(coverage.directed.presets_tested)
    emergent_tested = coverage.emergent.simulations_run

    if directed_tested > 5 and emergent_tested == 0:
        return ReasoningFactor(
            name="coverage",
            signal="emergent",
            weight=0.25,
            explanation=f"Dense Engine data ({directed_tested} presets tested) but zero Simulation data — emergence arm would fill a major gap",
        )
    elif emergent_tested > 3 and directed_tested == 0:
        return ReasoningFactor(
            name="coverage",
            signal="directed",
            weight=0.25,
            explanation=f"Simulation data exists ({emergent_tested} runs) but no Engine data — directed experiments would add precision",
        )
    elif directed_tested > 0 and emergent_tested > 0:
        return ReasoningFactor(
            name="coverage",
            signal="both",
            weight=0.15,
            explanation=f"Both arms have some data (Engine: {directed_tested} presets, Sim: {emergent_tested} runs) — HYBRID would connect them",
        )
    else:
        return ReasoningFactor(
            name="coverage",
            signal="directed",
            weight=0.1,
            explanation="No prior data in either arm — Engine is cheaper for initial exploration",
        )


def _analyse_knowledge(question: str, search: SearchIndex) -> ReasoningFactor:
    """Check if existing findings suggest a particular arm."""
    results = search.query_findings(question, max_results=5)

    if not results:
        return ReasoningFactor(
            name="knowledge",
            signal="directed",
            weight=0.1,
            explanation="No prior findings relevant to this question — starting with Engine for quick data",
        )

    # Check if findings are from emergence or directed
    emergence_findings = sum(1 for r in results if r.finding.type.value == "emergence")
    directed_findings = len(results) - emergence_findings

    if emergence_findings > directed_findings:
        return ReasoningFactor(
            name="knowledge",
            signal="both",
            weight=0.2,
            explanation=f"Prior emergence findings exist ({emergence_findings}) — HYBRID would test them as Engine configs",
        )
    else:
        return ReasoningFactor(
            name="knowledge",
            signal="directed",
            weight=0.15,
            explanation=f"Prior directed findings exist ({directed_findings}) — continue building on Engine data",
        )


def _analyse_task_specificity(question: str, task: str) -> ReasoningFactor:
    """Narrow tasks → Engine. Broad questions → Simulation."""
    q = question.lower()

    # Narrow/specific tasks → Engine
    narrow_signals = ["code review", "build", "implement", "write", "test", "refactor"]
    # Broad questions → Simulation
    broad_signals = [
        "society", "civilisation", "culture", "governance", "social",
        "cooperation", "conflict", "innovation", "emergence",
    ]

    narrow = sum(1 for s in narrow_signals if s in q or s in task.lower())
    broad = sum(1 for s in broad_signals if s in q)

    if narrow > broad:
        return ReasoningFactor(
            name="task_specificity",
            signal="directed",
            weight=0.2,
            explanation="Specific task identified — Engine directly tests team configurations for this task",
        )
    elif broad > narrow:
        return ReasoningFactor(
            name="task_specificity",
            signal="emergent",
            weight=0.2,
            explanation="Broad civilisational question — Simulation reveals emergent dynamics",
        )
    else:
        return ReasoningFactor(
            name="task_specificity",
            signal="both",
            weight=0.1,
            explanation="Question spans both task-specific and emergent concerns",
        )


# ── Strategy Selection ───────────────────────────────────────────────────────


def _pick_strategy(
    arm: Arm,
    store: KnowledgeStore,
    search: SearchIndex,
    question: str,
) -> Strategy:
    """Pick the best strategy for this arm based on knowledge state."""
    findings = search.query_findings(question, max_results=3)
    coverage = search.compute_coverage()

    # If we have prior data, use hypothesis-driven approach
    if findings:
        return Strategy.HYPOTHESIS

    # If we have some coverage, fill gaps
    tested = len(coverage.directed.presets_tested) + coverage.emergent.simulations_run
    if tested > 5:
        return Strategy.KNOWLEDGE

    # Fresh territory — grid search for broad baseline
    return Strategy.GRID


# ── Reasoning Output ─────────────────────────────────────────────────────────


def _build_reasoning(
    arm: Arm,
    strategy: Strategy,
    factors: list[ReasoningFactor],
    confidence: float,
) -> str:
    """Build human-readable reasoning for the recommendation."""
    arm_names = {
        Arm.DIRECTED: "Engine (directed experiments)",
        Arm.EMERGENT: "Simulation (emergence exploration)",
        Arm.BOTH: "HYBRID (emergence → translation → directed testing)",
    }

    lines = [
        f"Recommended approach: {arm_names[arm]}",
        f"Strategy: {strategy.value}",
        f"Confidence: {confidence:.0%}",
        "",
        "Reasoning:",
    ]

    for f in factors:
        lines.append(f"  [{f.name}] {f.explanation}")

    if arm == Arm.BOTH:
        lines.extend([
            "",
            "HYBRID plan: Run simulations to discover emergent patterns → translate those",
            "patterns into Engine configurations → test translated configs against baselines",
            "on your actual task. This reveals whether structures that AI civilisations",
            "naturally evolve outperform the ones humans design.",
        ])

    return "\n".join(lines)
