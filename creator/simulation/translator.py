"""Emergence → Engine translator — the bridge between emergent and directed.

Reads structured emergence metrics from simulation runs and maps observed
patterns to Engine organisational dimensions. Produces Engine RunConfig
objects that encode what the simulation discovered.

This is the core of HYBRID mode: emergent patterns from AI civilisations
translated into practical team configurations and tested on real tasks.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..config import DIMENSION_VALUES
from ..knowledge.models import Arm, RunConfig, RunResult

log = logging.getLogger(__name__)


@dataclass
class DimensionMapping:
    """A single dimension mapping from an emergent pattern."""

    dimension: str
    value: str
    confidence: float  # 0.0 to 1.0
    evidence: str  # Human-readable explanation of why this mapping was made
    source_metric: str  # Which emergence metric drove this mapping


@dataclass
class TranslationResult:
    """Complete translation of emergence data into an Engine config."""

    config: RunConfig
    mappings: list[DimensionMapping] = field(default_factory=list)
    overall_confidence: float = 0.0
    summary: str = ""
    source_runs: list[str] = field(default_factory=list)


def translate_emergence_to_engine(
    results: list[RunResult],
    base_preset: str = "collaborative",
) -> TranslationResult:
    """Translate emergence patterns from simulation results into an Engine config.

    Analyses the aggregated emergence metrics across multiple runs and maps
    the dominant patterns to Engine organisational dimensions.

    Args:
        results: List of RunResult objects from emergence campaigns (arm=EMERGENT).
        base_preset: Engine preset to use as the base (overrides are applied on top).

    Returns:
        TranslationResult with the derived Engine config + explanation.
    """
    if not results:
        return TranslationResult(
            config=RunConfig(preset=base_preset),
            summary="No emergence data to translate.",
        )

    # Filter to successful emergence runs only
    emergence_runs = [r for r in results if r.success and r.arm == Arm.EMERGENT]
    if not emergence_runs:
        return TranslationResult(
            config=RunConfig(preset=base_preset),
            summary="No successful emergence runs to translate.",
        )

    # Aggregate metrics across runs
    agg = _aggregate_metrics(emergence_runs)
    mappings: list[DimensionMapping] = []

    # Map each emergence pattern to an Engine dimension
    mappings.extend(_map_authority(agg))
    mappings.extend(_map_communication(agg))
    mappings.extend(_map_roles(agg))
    mappings.extend(_map_decisions(agg))
    mappings.extend(_map_incentives(agg))
    mappings.extend(_map_information(agg))
    mappings.extend(_map_conflict(agg))
    mappings.extend(_map_groups(agg))
    mappings.extend(_map_adaptation(agg))

    # Build Engine config from highest-confidence mapping per dimension
    overrides: dict[str, str] = {}
    best_per_dim: dict[str, DimensionMapping] = {}
    for m in mappings:
        if m.dimension not in best_per_dim or m.confidence > best_per_dim[m.dimension].confidence:
            best_per_dim[m.dimension] = m

    for dim, mapping in best_per_dim.items():
        if mapping.confidence >= 0.4:  # Only include mappings with reasonable confidence
            overrides[dim] = mapping.value

    # Overall confidence is the mean of included mappings
    included = [m for m in best_per_dim.values() if m.confidence >= 0.4]
    overall = sum(m.confidence for m in included) / len(included) if included else 0.0

    # Build summary
    summary_parts = []
    for m in sorted(included, key=lambda x: -x.confidence):
        conf_label = "high" if m.confidence >= 0.7 else "moderate" if m.confidence >= 0.5 else "low"
        summary_parts.append(
            f"  {m.dimension}={m.value} ({conf_label} confidence): {m.evidence}"
        )

    summary = (
        f"Translated {len(emergence_runs)} emergence runs into Engine config.\n"
        f"Base preset: {base_preset}, {len(overrides)} dimension overrides applied.\n"
        + "\n".join(summary_parts)
    )

    return TranslationResult(
        config=RunConfig(preset=base_preset, overrides=overrides if overrides else None),
        mappings=list(best_per_dim.values()),
        overall_confidence=round(overall, 3),
        summary=summary,
        source_runs=[r.id for r in emergence_runs],
    )


# ── Aggregation ──────────────────────────────────────────────────────────────


def _aggregate_metrics(runs: list[RunResult]) -> dict[str, float]:
    """Aggregate emergence metrics across multiple runs into averages."""
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}

    for r in runs:
        for key, value in r.emergence_metrics.items():
            if isinstance(value, (int, float)):
                totals[key] = totals.get(key, 0.0) + float(value)
                counts[key] = counts.get(key, 0) + 1

    return {k: totals[k] / counts[k] for k in totals}


# ── Dimension Mappers ────────────────────────────────────────────────────────
#
# Each mapper reads aggregated emergence metrics and produces zero or more
# DimensionMapping candidates for its dimension. The main function picks
# the highest-confidence mapping per dimension.


def _map_authority(agg: dict[str, float]) -> list[DimensionMapping]:
    """Map governance patterns → authority dimension."""
    mappings = []
    rules = agg.get("rules_established", 0)
    rules_proposed = agg.get("rules_proposed", 0)

    if rules >= 3:
        # Agents created substantial governance → consensus-based authority
        mappings.append(DimensionMapping(
            dimension="authority",
            value="consensus",
            confidence=min(0.9, 0.5 + rules * 0.05),
            evidence=f"Agents established {rules:.0f} rules on average — strong self-governance",
            source_metric="rules_established",
        ))
    elif rules_proposed >= 2 and rules < 2:
        # Proposed but didn't adopt many → distributed (some structure, not consensus)
        mappings.append(DimensionMapping(
            dimension="authority",
            value="distributed",
            confidence=0.5,
            evidence=f"Rules proposed ({rules_proposed:.0f}) but few established ({rules:.0f}) — partial governance",
            source_metric="rules_proposed",
        ))
    else:
        # Minimal governance → flat
        mappings.append(DimensionMapping(
            dimension="authority",
            value="flat",
            confidence=0.4,
            evidence="Minimal governance emerged — agents operated without formal authority",
            source_metric="rules_established",
        ))

    return mappings


def _map_communication(agg: dict[str, float]) -> list[DimensionMapping]:
    """Map communication patterns → communication dimension."""
    mappings = []
    messages = agg.get("total_messages", 0)
    density = agg.get("network_density", 0)

    if density >= 0.5:
        mappings.append(DimensionMapping(
            dimension="communication",
            value="mesh",
            confidence=min(0.9, 0.4 + density),
            evidence=f"Network density {density:.2f} — agents communicated broadly",
            source_metric="network_density",
        ))
    elif messages > 50:
        mappings.append(DimensionMapping(
            dimension="communication",
            value="broadcast",
            confidence=0.5,
            evidence=f"High message volume ({messages:.0f}) with moderate density — broadcast pattern",
            source_metric="total_messages",
        ))
    else:
        mappings.append(DimensionMapping(
            dimension="communication",
            value="whisper",
            confidence=0.4,
            evidence=f"Low communication ({messages:.0f} messages) — selective interaction",
            source_metric="total_messages",
        ))

    return mappings


def _map_roles(agg: dict[str, float]) -> list[DimensionMapping]:
    """Map specialisation patterns → roles dimension."""
    mappings = []
    specialised = agg.get("agents_with_specialisation", 0)
    total_specs = agg.get("total_specialisations", 0)

    if specialised >= 3:
        mappings.append(DimensionMapping(
            dimension="roles",
            value="emergent",
            confidence=min(0.9, 0.5 + specialised * 0.06),
            evidence=f"{specialised:.0f} agents developed specialisations — roles emerged organically",
            source_metric="agents_with_specialisation",
        ))
    elif total_specs >= 1:
        mappings.append(DimensionMapping(
            dimension="roles",
            value="fluid",
            confidence=0.45,
            evidence=f"Some specialisation ({total_specs:.0f}) but not widespread — fluid roles",
            source_metric="total_specialisations",
        ))

    return mappings


def _map_decisions(agg: dict[str, float]) -> list[DimensionMapping]:
    """Map governance + cooperation patterns → decisions dimension."""
    mappings = []
    rules = agg.get("rules_established", 0)
    cooperation = agg.get("cooperation_events", 0)

    if rules >= 3 and cooperation >= 5:
        mappings.append(DimensionMapping(
            dimension="decisions",
            value="consensus",
            confidence=0.7,
            evidence=f"Governance ({rules:.0f} rules) + cooperation ({cooperation:.0f} events) → consensus-based decisions",
            source_metric="rules_established",
        ))
    elif cooperation >= 5:
        mappings.append(DimensionMapping(
            dimension="decisions",
            value="meritocratic",
            confidence=0.5,
            evidence=f"High cooperation ({cooperation:.0f}) without heavy governance → merit-driven decisions",
            source_metric="cooperation_events",
        ))
    else:
        mappings.append(DimensionMapping(
            dimension="decisions",
            value="autonomous",
            confidence=0.4,
            evidence="Low cooperation and governance — agents decided independently",
            source_metric="cooperation_events",
        ))

    return mappings


def _map_incentives(agg: dict[str, float]) -> list[DimensionMapping]:
    """Map cooperation/sharing patterns → incentives dimension."""
    mappings = []
    cooperation = agg.get("cooperation_events", 0)
    sharing = agg.get("resource_sharing_events", 0)

    if cooperation >= 5 or sharing >= 3:
        mappings.append(DimensionMapping(
            dimension="incentives",
            value="collaborative",
            confidence=min(0.9, 0.5 + (cooperation + sharing) * 0.03),
            evidence=f"Cooperation ({cooperation:.0f}) + sharing ({sharing:.0f}) — collaborative incentives natural",
            source_metric="cooperation_events",
        ))
    else:
        mappings.append(DimensionMapping(
            dimension="incentives",
            value="competitive",
            confidence=0.4,
            evidence="Low cooperation/sharing — competitive dynamics dominated",
            source_metric="cooperation_events",
        ))

    return mappings


def _map_information(agg: dict[str, float]) -> list[DimensionMapping]:
    """Map communication openness → information dimension."""
    density = agg.get("network_density", 0)
    messages = agg.get("total_messages", 0)

    if density >= 0.4 and messages >= 30:
        return [DimensionMapping(
            dimension="information",
            value="transparent",
            confidence=min(0.8, 0.4 + density),
            evidence=f"Dense communication network ({density:.2f}) — information flowed freely",
            source_metric="network_density",
        )]
    return [DimensionMapping(
        dimension="information",
        value="curated",
        confidence=0.4,
        evidence="Moderate communication density — information was selectively shared",
        source_metric="network_density",
    )]


def _map_conflict(agg: dict[str, float]) -> list[DimensionMapping]:
    """Map governance presence → conflict resolution dimension."""
    rules = agg.get("rules_established", 0)

    if rules >= 2:
        return [DimensionMapping(
            dimension="conflict",
            value="voted",
            confidence=min(0.7, 0.4 + rules * 0.05),
            evidence=f"Governance present ({rules:.0f} rules) — conflicts likely resolved by rules/voting",
            source_metric="rules_established",
        )]
    return [DimensionMapping(
        dimension="conflict",
        value="negotiated",
        confidence=0.4,
        evidence="No formal governance — conflicts resolved through direct negotiation",
        source_metric="rules_established",
    )]


def _map_groups(agg: dict[str, float]) -> list[DimensionMapping]:
    """Map social structure → groups dimension."""
    bonded = agg.get("bonded_pairs", 0)
    relationships = agg.get("relationship_count", 0)

    if bonded >= 3:
        return [DimensionMapping(
            dimension="groups",
            value="self-selected",
            confidence=min(0.8, 0.4 + bonded * 0.06),
            evidence=f"{bonded:.0f} bonded pairs formed — agents chose their own groups",
            source_metric="bonded_pairs",
        )]
    elif relationships >= 5:
        return [DimensionMapping(
            dimension="groups",
            value="task-based",
            confidence=0.5,
            evidence=f"{relationships:.0f} relationships but few bonds — task-driven grouping",
            source_metric="relationship_count",
        )]
    return []


def _map_adaptation(agg: dict[str, float]) -> list[DimensionMapping]:
    """Map innovation + change patterns → adaptation dimension."""
    innovations = agg.get("innovation_count", 0)
    compositions = agg.get("composition_count", 0)

    if innovations >= 3 or compositions >= 2:
        return [DimensionMapping(
            dimension="adaptation",
            value="evolving",
            confidence=min(0.8, 0.4 + (innovations + compositions) * 0.05),
            evidence=f"Innovation ({innovations:.0f}) + composition ({compositions:.0f}) — civilisation actively evolved",
            source_metric="innovation_count",
        )]
    return [DimensionMapping(
        dimension="adaptation",
        value="static",
        confidence=0.35,
        evidence="Low innovation — structure remained relatively stable",
        source_metric="innovation_count",
    )]
