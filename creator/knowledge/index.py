"""Search index — keyword + tag-based retrieval over findings and hypotheses.

This is the brain behind creator_knowledge(action="query"). It handles:
- Natural language queries matched against finding statements and tags
- Tag-based filtering
- Confidence-weighted ranking
- Coverage gap detection
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..config import ALL_DIMENSIONS, ALL_PRESETS, SIM_CONDITIONS
from .models import (
    Arm,
    Coverage,
    CoverageArm,
    Finding,
    Hypothesis,
    HypothesisStatus,
)
from .store import KnowledgeStore


@dataclass
class SearchResult:
    """A finding matched by a query, with a relevance score."""
    finding: Finding
    score: float  # 0.0 – 1.0, higher = more relevant
    match_reasons: list[str] = field(default_factory=list)


@dataclass
class CoverageGap:
    """An identified gap in the knowledge store."""
    area: str
    description: str
    priority: str = "medium"  # low, medium, high


def _tokenise(text: str) -> set[str]:
    """Extract lowercase word tokens from text, stripping punctuation."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _compute_relevance(finding: Finding, query_tokens: set[str]) -> tuple[float, list[str]]:
    """Score a finding's relevance to a query. Returns (score, reasons)."""
    score = 0.0
    reasons: list[str] = []

    statement_tokens = _tokenise(finding.statement)
    tag_tokens = {t.lower().replace("-", "").replace("_", "") for t in finding.tags}

    # Direct token overlap with statement
    statement_overlap = query_tokens & statement_tokens
    if statement_overlap:
        overlap_ratio = len(statement_overlap) / max(len(query_tokens), 1)
        score += overlap_ratio * 0.5
        reasons.append(f"statement match: {', '.join(sorted(statement_overlap))}")

    # Tag matches (strong signal)
    normalised_query = {t.replace("-", "").replace("_", "") for t in query_tokens}
    tag_overlap = normalised_query & tag_tokens
    if tag_overlap:
        score += len(tag_overlap) * 0.2
        reasons.append(f"tag match: {', '.join(sorted(tag_overlap))}")

    # Require at least one keyword or tag match — don't return unrelated findings
    if not statement_overlap and not tag_overlap:
        return 0.0, []

    # Confidence boost — higher-confidence findings rank higher when scores are close
    score += finding.confidence * 0.1

    # Evidence volume boost — more evidence = more trustworthy
    evidence_count = len(finding.evidence)
    if evidence_count >= 6:
        score += 0.1
        reasons.append(f"strong evidence ({evidence_count} runs)")
    elif evidence_count >= 3:
        score += 0.05

    return min(score, 1.0), reasons


class SearchIndex:
    """Query engine over the knowledge store."""

    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    def query_findings(
        self,
        question: str,
        min_confidence: float = 0.0,
        max_results: int = 10,
        tags: list[str] | None = None,
    ) -> list[SearchResult]:
        """Search findings by natural language question and optional tag filter.

        Returns results sorted by relevance (highest first).
        """
        query_tokens = _tokenise(question)
        if not query_tokens:
            return []

        all_findings = self._store.list_findings()

        # Tag filter
        if tags:
            tag_set = {t.lower() for t in tags}
            all_findings = [
                f for f in all_findings
                if tag_set & {t.lower() for t in f.tags}
            ]

        # Confidence filter
        all_findings = [f for f in all_findings if f.confidence >= min_confidence]

        # Score and rank
        scored: list[SearchResult] = []
        for finding in all_findings:
            score, reasons = _compute_relevance(finding, query_tokens)
            if score > 0:
                scored.append(SearchResult(finding=finding, score=score, match_reasons=reasons))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:max_results]

    def find_related_hypotheses(
        self,
        question: str,
        status: HypothesisStatus | None = None,
        max_results: int = 5,
    ) -> list[Hypothesis]:
        """Find hypotheses related to a question."""
        query_tokens = _tokenise(question)
        if not query_tokens:
            return []

        hypotheses = self._store.list_hypotheses(status=status)

        scored: list[tuple[float, Hypothesis]] = []
        for h in hypotheses:
            h_tokens = _tokenise(h.statement)
            tag_tokens = {t.lower().replace("-", "").replace("_", "") for t in h.tags}
            normalised_query = {t.replace("-", "").replace("_", "") for t in query_tokens}

            overlap = len(query_tokens & h_tokens) / max(len(query_tokens), 1)
            tag_match = len(normalised_query & tag_tokens) * 0.3
            priority_boost = {"critical": 0.3, "high": 0.2, "medium": 0.1, "low": 0.0}.get(
                h.priority.value, 0.0
            )
            score = overlap * 0.5 + tag_match + priority_boost

            if score > 0:
                scored.append((score, h))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [h for _, h in scored[:max_results]]

    def compute_coverage(self) -> Coverage:
        """Compute what has been explored and what hasn't.

        Analyzes all findings and campaigns to build a coverage map.
        """
        findings = self._store.list_findings()
        campaigns = self._store.list_campaigns()

        # Directed arm coverage
        presets_tested: set[str] = set()
        dimensions_varied: set[str] = set()
        agent_counts: set[int] = set()
        task_types: set[str] = set()

        for f in findings:
            presets_tested.update(f.conditions.presets)
            dimensions_varied.update(f.conditions.dimensions.keys())
            task_types.update(f.conditions.task_types)
            lo, hi = f.conditions.agent_count_range
            if lo is not None:
                agent_counts.add(lo)
            if hi is not None:
                agent_counts.add(hi)

        for c in campaigns:
            for batch in c.batches:
                for cfg in batch.configs:
                    presets_tested.add(cfg.preset)
                    if cfg.overrides:
                        dimensions_varied.update(cfg.overrides.keys())
            if c.constraints.agents:
                agent_counts.add(c.constraints.agents)

        presets_untested = [p for p in ALL_PRESETS if p not in presets_tested]
        dims_unvaried = [d for d in ALL_DIMENSIONS if d not in dimensions_varied]

        directed = CoverageArm(
            presets_tested=sorted(presets_tested),
            presets_untested=presets_untested,
            dimensions_varied=sorted(dimensions_varied),
            dimensions_unvaried=dims_unvaried,
            agent_counts_tested=sorted(agent_counts),
            task_types_tested=sorted(task_types),
        )

        # Emergent arm — track simulation campaigns
        sim_conditions_tested: set[str] = set()
        sim_ticks_tested: set[int] = set()
        sim_runs = 0

        for c in campaigns:
            if c.arm in (Arm.EMERGENT, Arm.BOTH):
                for batch in c.batches:
                    for cfg in batch.configs:
                        sim_conditions_tested.add(cfg.preset)
                    sim_runs += len(batch.run_ids)
                if c.constraints.max_ticks:
                    sim_ticks_tested.add(c.constraints.max_ticks)

        # Also check run results for emergence data
        for c in campaigns:
            run_results = self._store.list_run_results(c.id)
            for r in run_results:
                if r.arm == Arm.EMERGENT:
                    sim_conditions_tested.add(r.config.preset)
                    sim_runs += 0  # Already counted above

        conditions_untested = [c for c in SIM_CONDITIONS if c not in sim_conditions_tested]

        emergent = CoverageArm(
            simulations_run=sim_runs,
            conditions_tested=sorted(sim_conditions_tested),
            conditions_untested=conditions_untested,
            max_ticks_tested=sorted(sim_ticks_tested),
        )

        return Coverage(directed=directed, emergent=emergent)

    def identify_gaps(self) -> list[CoverageGap]:
        """Identify the most valuable gaps in current knowledge."""
        coverage = self.compute_coverage()
        gaps: list[CoverageGap] = []

        d = coverage.directed

        if d.presets_untested:
            n = len(d.presets_untested)
            gaps.append(CoverageGap(
                area="presets",
                description=f"{n} presets never tested: {', '.join(d.presets_untested[:5])}",
                priority="medium" if n <= 5 else "high",
            ))

        if d.dimensions_unvaried:
            n = len(d.dimensions_unvaried)
            gaps.append(CoverageGap(
                area="dimensions",
                description=f"{n} dimensions never varied: {', '.join(d.dimensions_unvaried[:5])}",
                priority="medium",
            ))

        tested_counts = d.agent_counts_tested
        if not tested_counts or max(tested_counts, default=0) <= 8:
            gaps.append(CoverageGap(
                area="scale",
                description="No data above 8 agents — consider a scale-up campaign",
                priority="high",
            ))

        if coverage.emergent.simulations_run == 0:
            gaps.append(CoverageGap(
                area="emergent",
                description="No emergent arm data — no simulation campaigns have been run",
                priority="medium",
            ))

        return gaps

    def query_cross_arm(
        self,
        question: str,
        source_arm: Arm,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """Find findings from the OTHER arm that are relevant to this question.

        When planning an emergence campaign, retrieves directed findings that
        could inform hypotheses. When planning a directed campaign, retrieves
        emergence findings that suggest configurations to test.

        This is the core of cross-mode knowledge: Engine data informs Simulation
        hypotheses, and Simulation discoveries inform Engine configurations.
        """
        query_tokens = _tokenise(question)
        if not query_tokens:
            return []

        all_findings = self._store.list_findings()

        # Filter to findings from the OPPOSITE arm
        # Emergence findings have type=EMERGENCE, directed have other types
        if source_arm == Arm.DIRECTED:
            # Source is directed → find emergence findings
            cross_findings = [
                f for f in all_findings
                if f.type.value == "emergence"
            ]
        elif source_arm == Arm.EMERGENT:
            # Source is emergent → find directed findings
            cross_findings = [
                f for f in all_findings
                if f.type.value != "emergence"
            ]
        else:
            # BOTH → return all findings
            cross_findings = all_findings

        scored: list[SearchResult] = []
        for finding in cross_findings:
            score, reasons = _compute_relevance(finding, query_tokens)
            if score > 0:
                reasons.append(f"cross-arm: from {'emergence' if finding.type.value == 'emergence' else 'directed'} arm")
                scored.append(SearchResult(finding=finding, score=score, match_reasons=reasons))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:max_results]

    def suggest_next(self, max_suggestions: int = 5) -> list[str]:
        """Generate actionable suggestions for what to explore next."""
        gaps = self.identify_gaps()
        untested = self._store.list_hypotheses(status=HypothesisStatus.UNTESTED)

        suggestions: list[str] = []

        if untested:
            suggestions.append(f"{len(untested)} untested hypotheses ready to explore")

        for gap in gaps[:max_suggestions - len(suggestions)]:
            suggestions.append(gap.description)

        return suggestions[:max_suggestions]
