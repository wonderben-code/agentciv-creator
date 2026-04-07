"""Recommendation engine — data-driven config recommendations from knowledge store.

Given a task type, agent count, and priority, produces:
  - Recommended config (preset + overrides)
  - Confidence level
  - Alternatives ranked by quality
  - Justification from evidence
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..knowledge.index import SearchIndex
from ..knowledge.models import DataQuality, Finding, RunResult
from ..knowledge.store import KnowledgeStore


def recommend_config(
    store: KnowledgeStore,
    search: SearchIndex,
    task_type: str | None = None,
    agents: int | None = None,
    priority: str | None = None,
) -> dict[str, Any]:
    """Generate a data-driven recommendation for an organisational config.

    Args:
        store: Knowledge store.
        search: Search index.
        task_type: Type of task (e.g., "code_review", "api_dev").
        agents: Agent count.
        priority: Optimisation priority — "quality", "speed", "creativity", "balanced".

    Returns:
        Recommendation dict with config, confidence, justification, alternatives.
    """
    findings = store.list_findings()
    campaigns = store.list_campaigns()

    if not findings and not campaigns:
        return {
            "recommendation": None,
            "confidence": 0.0,
            "data_quality": DataQuality.INSUFFICIENT.value,
            "message": "No data in knowledge store. Run campaigns first.",
        }

    # Gather all evidence: findings + raw run results
    relevant_findings = _filter_findings(findings, task_type, agents)
    all_results = _gather_all_results(store, campaigns)
    relevant_results = _filter_results(all_results, task_type, agents)

    # Score each config
    config_scores = _score_configs(relevant_findings, relevant_results, priority or "balanced")

    if not config_scores:
        return {
            "recommendation": None,
            "confidence": 0.0,
            "data_quality": DataQuality.LIMITED.value,
            "message": "Not enough relevant data. Try a broader search.",
        }

    # Sort by score
    ranked = sorted(config_scores.items(), key=lambda x: x[1]["score"], reverse=True)
    best_key, best_data = ranked[0]

    # Build justification
    justification = _build_justification(best_key, best_data, relevant_findings)

    # Determine data quality
    total_evidence = sum(d.get("n_runs", 0) for _, d in ranked)
    if total_evidence >= 30:
        quality = DataQuality.STRONG
    elif total_evidence >= 15:
        quality = DataQuality.GOOD
    elif total_evidence >= 5:
        quality = DataQuality.LIMITED
    else:
        quality = DataQuality.INSUFFICIENT

    return {
        "recommendation": {
            "preset": best_data.get("preset", best_key),
            "overrides": best_data.get("overrides"),
            "full_config": _expand_config(best_data.get("preset", best_key)),
        },
        "confidence": round(best_data["score"], 3),
        "justification": justification,
        "alternatives": [
            {
                "preset": d.get("preset", k),
                "overrides": d.get("overrides"),
                "score": round(d["score"], 3),
                "quality_delta": round(d["score"] - best_data["score"], 3),
                "n_runs": d.get("n_runs", 0),
            }
            for k, d in ranked[1:4]
        ],
        "data_quality": quality.value,
        "evidence_runs": total_evidence,
    }


def _filter_findings(
    findings: list[Finding],
    task_type: str | None,
    agents: int | None,
) -> list[Finding]:
    """Filter findings relevant to the requested context."""
    if not task_type and not agents:
        return findings

    relevant = []
    for f in findings:
        task_match = not task_type or (
            task_type in f.conditions.task_types or not f.conditions.task_types
        )
        agent_match = not agents or (
            f.conditions.agent_count_range == [None, None]
            or (
                (f.conditions.agent_count_range[0] is None or agents >= f.conditions.agent_count_range[0])
                and (f.conditions.agent_count_range[1] is None or agents <= f.conditions.agent_count_range[1])
            )
        )
        if task_match and agent_match:
            relevant.append(f)

    return relevant or findings  # Fall back to all if nothing matches


def _gather_all_results(
    store: KnowledgeStore,
    campaigns: list[Any],
) -> list[RunResult]:
    """Gather all run results across all campaigns."""
    results = []
    for c in campaigns:
        results.extend(store.list_run_results(c.id))
    return results


def _filter_results(
    results: list[RunResult],
    task_type: str | None,
    agents: int | None,
) -> list[RunResult]:
    """Filter run results by context."""
    filtered = results
    if agents:
        filtered = [r for r in filtered if r.agent_count == agents]
    return filtered


def _score_configs(
    findings: list[Finding],
    results: list[RunResult],
    priority: str,
) -> dict[str, dict[str, Any]]:
    """Score each config based on findings and raw results."""
    scores: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "score": 0.0, "n_runs": 0, "quality_sum": 0.0, "conflict_sum": 0.0,
        "ticks_sum": 0.0, "finding_support": 0, "preset": "", "overrides": None,
    })

    # Score from raw results
    for r in results:
        if not r.success:
            continue
        key = r.config.preset
        if r.config.overrides:
            key += "+" + "+".join(f"{k}={v}" for k, v in sorted(r.config.overrides.items()))

        entry = scores[key]
        entry["preset"] = r.config.preset
        entry["overrides"] = r.config.overrides
        entry["n_runs"] += 1
        entry["quality_sum"] += r.quality_score
        entry["conflict_sum"] += r.merge_conflicts
        entry["ticks_sum"] += r.ticks_used

    # Compute averages and scores
    for key, data in scores.items():
        n = data["n_runs"]
        if n == 0:
            continue

        avg_quality = data["quality_sum"] / n
        avg_conflicts = data["conflict_sum"] / n
        avg_ticks = data["ticks_sum"] / n

        # Priority weighting
        if priority == "quality":
            data["score"] = avg_quality
        elif priority == "speed":
            data["score"] = avg_quality * 0.5 + (1 - avg_ticks / 100) * 0.5
        elif priority == "creativity":
            data["score"] = avg_quality * 0.7 + (1 - avg_conflicts / 30) * 0.3
        else:  # balanced
            data["score"] = avg_quality * 0.6 + (1 - avg_conflicts / 30) * 0.2 + (1 - avg_ticks / 100) * 0.2

    # Boost from findings
    for f in findings:
        for preset in f.conditions.presets:
            if preset in scores:
                scores[preset]["score"] += f.confidence * 0.1
                scores[preset]["finding_support"] += 1

    return dict(scores)


def _build_justification(
    config_key: str,
    data: dict[str, Any],
    findings: list[Finding],
) -> str:
    """Build a human-readable justification for the recommendation."""
    parts = [f"Recommended based on {data.get('n_runs', 0)} experiment runs."]

    n = data.get("n_runs", 0)
    if n > 0:
        avg_q = data["quality_sum"] / n
        avg_c = data["conflict_sum"] / n
        parts.append(f"Average quality: {avg_q:.3f}, average conflicts: {avg_c:.1f}.")

    supporting = [f for f in findings if config_key in f.conditions.presets or data.get("preset") in f.conditions.presets]
    if supporting:
        parts.append(f"Supported by {len(supporting)} finding(s):")
        for f in supporting[:3]:
            parts.append(f"  - {f.statement} (confidence: {f.confidence})")

    return " ".join(parts)


def _expand_config(preset: str) -> dict[str, str]:
    """Expand a preset name into full dimension values.

    This is a best-effort mapping — actual values come from the engine's
    EngineConfig.from_preset(). We provide a reference mapping here.
    """
    # Known preset → dimension mappings (from engine documentation)
    preset_configs: dict[str, dict[str, str]] = {
        "collaborative": {
            "authority": "flat", "communication": "mesh", "roles": "fluid",
            "decisions": "consensus", "incentives": "collaborative", "information": "transparent",
            "conflict": "negotiated", "groups": "self-selected", "adaptation": "evolving",
        },
        "competitive": {
            "authority": "flat", "communication": "broadcast", "roles": "fixed",
            "decisions": "autonomous", "incentives": "competitive", "information": "transparent",
            "conflict": "authority", "groups": "imposed", "adaptation": "static",
        },
        "hierarchical": {
            "authority": "hierarchy", "communication": "hub-spoke", "roles": "assigned",
            "decisions": "top-down", "incentives": "collaborative", "information": "curated",
            "conflict": "authority", "groups": "imposed", "adaptation": "static",
        },
        "auto": {
            "authority": "distributed", "communication": "mesh", "roles": "emergent",
            "decisions": "consensus", "incentives": "collaborative", "information": "transparent",
            "conflict": "voted", "groups": "self-selected", "adaptation": "real-time",
        },
    }

    if preset in preset_configs:
        return preset_configs[preset]

    # Default: return empty — engine will fill in from preset
    return {}
