"""Statistical analyzer — rankings, effect sizes, significance tests, confidence.

Takes RunResult lists and produces structured analysis:
  - Per-config aggregate metrics (mean, std, n)
  - Pairwise comparisons with effect size (Cohen's d) and p-values
  - Hypothesis resolution based on evidence
  - Finding extraction from significant results
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from ..knowledge.models import (
    DataQuality,
    EvidenceItem,
    Finding,
    FindingConditions,
    FindingType,
    Hypothesis,
    HypothesisStatus,
    RunConfig,
    RunResult,
    StatisticalTest,
    utcnow,
)
from ..knowledge.store import KnowledgeStore

# ── Metric Descriptors ──────────────────────────────────────────────────────

METRICS = {
    "quality_score": {"higher_is_better": True, "label": "Quality Score"},
    "merge_conflicts": {"higher_is_better": False, "label": "Merge Conflicts"},
    "ticks_used": {"higher_is_better": False, "label": "Ticks Used"},
    "total_tokens": {"higher_is_better": False, "label": "Total Tokens"},
    "total_messages": {"higher_is_better": False, "label": "Total Messages"},
    "wall_time_seconds": {"higher_is_better": False, "label": "Wall Time (s)"},
    "files_produced": {"higher_is_better": True, "label": "Files Produced"},
}

DEFAULT_METRICS = ["quality_score", "merge_conflicts", "ticks_used"]


# ── Config Key ──────────────────────────────────────────────────────────────

def config_key(config: RunConfig) -> str:
    """Generate a stable string key for a RunConfig."""
    base = config.preset
    if config.overrides:
        parts = "+".join(f"{k}={v}" for k, v in sorted(config.overrides.items()))
        return f"{base}+{parts}"
    return base


# ── Aggregate Statistics ────────────────────────────────────────────────────

def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def aggregate_by_config(
    results: list[RunResult],
    metrics: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Group results by config and compute aggregate statistics.

    Returns: {config_key: {metric: {mean, std, min, max, n, values}, ...}}
    """
    metrics = metrics or DEFAULT_METRICS
    grouped: dict[str, list[RunResult]] = defaultdict(list)

    for r in results:
        if r.success:
            grouped[config_key(r.config)].append(r)

    aggregates: dict[str, dict[str, Any]] = {}
    for key, runs in sorted(grouped.items()):
        agg: dict[str, Any] = {"config": runs[0].config.model_dump(), "n": len(runs)}
        for metric in metrics:
            values = [getattr(r, metric, 0) for r in runs]
            float_values = [float(v) for v in values]
            agg[metric] = {
                "mean": round(_mean(float_values), 4),
                "std": round(_std(float_values), 4),
                "min": round(min(float_values), 4) if float_values else 0,
                "max": round(max(float_values), 4) if float_values else 0,
                "n": len(float_values),
                "values": [round(v, 4) for v in float_values],
            }
        aggregates[key] = agg

    return aggregates


def rank_configs(
    aggregates: dict[str, dict[str, Any]],
    primary_metric: str = "quality_score",
) -> list[dict[str, Any]]:
    """Rank configs by primary metric.

    Returns sorted list of {config_key, config, quality_mean, quality_std, n, rank}.
    """
    higher_is_better = METRICS.get(primary_metric, {}).get("higher_is_better", True)

    ranking = []
    for key, agg in aggregates.items():
        metric_data = agg.get(primary_metric, {})
        ranking.append({
            "config_key": key,
            "config": agg.get("config"),
            "mean": metric_data.get("mean", 0),
            "std": metric_data.get("std", 0),
            "n": agg.get("n", 0),
        })

    ranking.sort(key=lambda x: x["mean"], reverse=higher_is_better)

    for i, entry in enumerate(ranking):
        entry["rank"] = i + 1

    return ranking


# ── Pairwise Comparison (Independent Samples t-test) ───────────────────────

def _t_test_independent(
    values_a: list[float],
    values_b: list[float],
) -> tuple[float, float]:
    """Welch's t-test for independent samples.

    Returns (t_statistic, p_value).
    Uses t-distribution approximation via the Abramowitz & Stegun formula.
    """
    n_a, n_b = len(values_a), len(values_b)
    if n_a < 2 or n_b < 2:
        return 0.0, 1.0

    mean_a, mean_b = _mean(values_a), _mean(values_b)
    var_a = sum((x - mean_a) ** 2 for x in values_a) / (n_a - 1)
    var_b = sum((x - mean_b) ** 2 for x in values_b) / (n_b - 1)

    se = math.sqrt(var_a / n_a + var_b / n_b)
    if se == 0:
        return 0.0, 1.0

    t_stat = (mean_a - mean_b) / se

    # Welch-Satterthwaite degrees of freedom
    num = (var_a / n_a + var_b / n_b) ** 2
    denom = (var_a / n_a) ** 2 / (n_a - 1) + (var_b / n_b) ** 2 / (n_b - 1)
    if denom == 0:
        return t_stat, 1.0
    df = num / denom

    # Approximate p-value using the regularised incomplete beta function
    # For small df, this is reasonable for our purposes
    p_value = _t_to_p(abs(t_stat), df) * 2  # Two-tailed
    return t_stat, min(p_value, 1.0)


def _t_to_p(t: float, df: float) -> float:
    """Approximate one-tailed p-value from t-statistic and degrees of freedom.

    Uses the approximation: p ≈ 0.5 * (1 + erf(-t / sqrt(2))) for large df,
    with a correction for small df via the Student's t CDF approximation.
    """
    if df <= 0:
        return 1.0
    # For df > 30, normal approximation is very close
    if df > 30:
        return 0.5 * math.erfc(t / math.sqrt(2))
    # For smaller df, use a simple approximation
    # p ≈ 0.5 * (1 - t * (1 - t^2/(4*df)) / sqrt(df * (1 + t^2/df)))
    x = t * t / df
    if x > 20:  # Very large t, p ≈ 0
        return 0.0
    # Beta function approximation for Student's t
    a = df / 2
    b = 0.5
    x_beta = df / (df + t * t)
    return 0.5 * _incomplete_beta(a, b, x_beta)


def _incomplete_beta(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta function I_x(a, b) via continued fraction.

    Lentz's algorithm. Sufficient accuracy for p-value estimation.
    """
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    # Use the continued fraction expansion
    # For numerical stability, use the Lentz method
    max_iter = 200
    eps = 1e-10

    # Compute the log of the prefactor
    try:
        log_prefactor = (
            math.lgamma(a + b)
            - math.lgamma(a)
            - math.lgamma(b)
            + a * math.log(x)
            + b * math.log(1 - x)
        )
        prefactor = math.exp(log_prefactor)
    except (ValueError, OverflowError):
        return 0.5  # Fallback

    # Continued fraction via modified Lentz's method
    f = 1.0
    c = 1.0
    d = 1.0 - (a + b) * x / (a + 1)
    if abs(d) < eps:
        d = eps
    d = 1.0 / d
    f = d

    for m in range(1, max_iter + 1):
        # Even step
        m2 = 2 * m
        num = m * (b - m) * x / ((a + m2 - 1) * (a + m2))
        d = 1.0 + num * d
        if abs(d) < eps:
            d = eps
        c = 1.0 + num / c
        if abs(c) < eps:
            c = eps
        d = 1.0 / d
        f *= c * d

        # Odd step
        num = -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1))
        d = 1.0 + num * d
        if abs(d) < eps:
            d = eps
        c = 1.0 + num / c
        if abs(c) < eps:
            c = eps
        d = 1.0 / d
        delta = c * d
        f *= delta

        if abs(delta - 1.0) < eps:
            break

    return prefactor * f / a


def cohens_d(values_a: list[float], values_b: list[float]) -> float:
    """Compute Cohen's d effect size between two groups.

    Uses pooled standard deviation. Returns 0 if insufficient data.
    """
    n_a, n_b = len(values_a), len(values_b)
    if n_a < 2 or n_b < 2:
        return 0.0

    mean_a, mean_b = _mean(values_a), _mean(values_b)
    var_a = sum((x - mean_a) ** 2 for x in values_a) / (n_a - 1)
    var_b = sum((x - mean_b) ** 2 for x in values_b) / (n_b - 1)

    pooled_std = math.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
    if pooled_std == 0:
        return 0.0

    return (mean_a - mean_b) / pooled_std


def compare_configs(
    results: list[RunResult],
    config_a: str,
    config_b: str,
    metrics: list[str] | None = None,
) -> dict[str, Any]:
    """Pairwise statistical comparison between two configs.

    Returns comparison with t-test, Cohen's d, and significance for each metric.
    """
    metrics = metrics or DEFAULT_METRICS

    grouped: dict[str, list[RunResult]] = defaultdict(list)
    for r in results:
        if r.success:
            grouped[config_key(r.config)].append(r)

    runs_a = grouped.get(config_a, [])
    runs_b = grouped.get(config_b, [])

    if not runs_a or not runs_b:
        return {
            "config_a": config_a,
            "config_b": config_b,
            "error": "One or both configs have no successful runs",
            "n_a": len(runs_a),
            "n_b": len(runs_b),
        }

    comparisons: dict[str, Any] = {}
    for metric in metrics:
        vals_a = [float(getattr(r, metric, 0)) for r in runs_a]
        vals_b = [float(getattr(r, metric, 0)) for r in runs_b]

        t_stat, p_value = _t_test_independent(vals_a, vals_b)
        d = cohens_d(vals_a, vals_b)
        higher_is_better = METRICS.get(metric, {}).get("higher_is_better", True)

        mean_a, mean_b = _mean(vals_a), _mean(vals_b)
        if higher_is_better:
            winner = config_a if mean_a > mean_b else config_b
        else:
            winner = config_a if mean_a < mean_b else config_b

        comparisons[metric] = {
            "config_a_mean": round(mean_a, 4),
            "config_b_mean": round(mean_b, 4),
            "difference": round(mean_a - mean_b, 4),
            "effect_size_d": round(d, 4),
            "effect_magnitude": _effect_magnitude(abs(d)),
            "t_statistic": round(t_stat, 4),
            "p_value": round(p_value, 6),
            "significant_at_05": p_value < 0.05,
            "significant_at_01": p_value < 0.01,
            "winner": winner,
        }

    return {
        "config_a": config_a,
        "config_b": config_b,
        "n_a": len(runs_a),
        "n_b": len(runs_b),
        "comparisons": comparisons,
    }


def _effect_magnitude(d: float) -> str:
    """Classify Cohen's d magnitude."""
    if d < 0.2:
        return "negligible"
    if d < 0.5:
        return "small"
    if d < 0.8:
        return "medium"
    return "large"


# ── Full Campaign Analysis ──────────────────────────────────────────────────

def analyze_campaign(
    results: list[RunResult],
    hypotheses: list[Hypothesis] | None = None,
    campaign_id: str = "",
    metrics: list[str] | None = None,
) -> dict[str, Any]:
    """Full statistical analysis of a campaign's results.

    Returns:
        - aggregates: per-config stats
        - ranking: ordered by primary metric
        - pairwise: all pairwise comparisons
        - hypothesis_verdicts: resolved hypotheses
        - data_quality: assessment of statistical power
    """
    metrics = metrics or DEFAULT_METRICS
    successful = [r for r in results if r.success]

    if not successful:
        return {
            "campaign_id": campaign_id,
            "status": "no_data",
            "message": "No successful runs to analyze",
        }

    aggregates = aggregate_by_config(successful, metrics)
    ranking = rank_configs(aggregates)

    # Pairwise comparisons (top configs only to avoid combinatorial explosion)
    config_keys = [r["config_key"] for r in ranking[:8]]
    pairwise = []
    for i, key_a in enumerate(config_keys):
        for key_b in config_keys[i + 1:]:
            comparison = compare_configs(successful, key_a, key_b, metrics)
            pairwise.append(comparison)

    # Hypothesis resolution
    verdicts = []
    if hypotheses:
        for h in hypotheses:
            verdict = _resolve_hypothesis(h, successful, aggregates)
            verdicts.append(verdict)

    # Data quality assessment
    total_runs = len(successful)
    n_configs = len(aggregates)
    min_runs_per = min((agg["n"] for agg in aggregates.values()), default=0)

    if total_runs >= 30 and min_runs_per >= 5:
        quality = DataQuality.STRONG
    elif total_runs >= 15 and min_runs_per >= 3:
        quality = DataQuality.GOOD
    elif total_runs >= 6:
        quality = DataQuality.LIMITED
    else:
        quality = DataQuality.INSUFFICIENT

    # Extract key findings
    significant_findings = _extract_significant_findings(pairwise, ranking, campaign_id)

    return {
        "campaign_id": campaign_id,
        "status": "analyzed",
        "total_runs": total_runs,
        "configs_tested": n_configs,
        "data_quality": quality.value,
        "ranking": ranking,
        "aggregates": {k: _clean_aggregate(v) for k, v in aggregates.items()},
        "pairwise_comparisons": pairwise,
        "hypothesis_verdicts": verdicts,
        "significant_findings": significant_findings,
        "winner": ranking[0] if ranking else None,
    }


def _clean_aggregate(agg: dict[str, Any]) -> dict[str, Any]:
    """Remove raw values from aggregate for cleaner output."""
    cleaned = {}
    for k, v in agg.items():
        if isinstance(v, dict) and "values" in v:
            cleaned[k] = {mk: mv for mk, mv in v.items() if mk != "values"}
        else:
            cleaned[k] = v
    return cleaned


# ── Hypothesis Resolution ───────────────────────────────────────────────────

def _resolve_hypothesis(
    hypothesis: Hypothesis,
    results: list[RunResult],
    aggregates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Determine whether a hypothesis is supported, refuted, or inconclusive."""
    td = hypothesis.test_design

    if not td.treatment or not td.outcome_metric:
        return {
            "hypothesis_id": hypothesis.id,
            "statement": hypothesis.statement,
            "verdict": "inconclusive",
            "reason": "No test design specified",
        }

    # Find configs matching treatment and control
    treatment_runs = _find_matching_runs(results, td.treatment, td.independent_variable)
    control_runs = _find_matching_runs(results, td.control, td.independent_variable) if td.control else []

    if not treatment_runs or not control_runs:
        return {
            "hypothesis_id": hypothesis.id,
            "statement": hypothesis.statement,
            "verdict": "inconclusive",
            "reason": f"Insufficient data: {len(treatment_runs)} treatment, {len(control_runs)} control runs",
        }

    metric = td.outcome_metric
    treatment_vals = [float(getattr(r, metric, 0)) for r in treatment_runs]
    control_vals = [float(getattr(r, metric, 0)) for r in control_runs]

    t_stat, p_value = _t_test_independent(treatment_vals, control_vals)
    d = cohens_d(treatment_vals, control_vals)
    treatment_mean = _mean(treatment_vals)
    control_mean = _mean(control_vals)

    # Determine direction
    direction = td.expected_direction.lower()
    if "treatment > control" in direction or "treatment>control" in direction:
        hypothesis_supported = treatment_mean > control_mean
    elif "treatment < control" in direction or "treatment<control" in direction:
        hypothesis_supported = treatment_mean < control_mean
    elif "control > treatment" in direction or "control>treatment" in direction:
        hypothesis_supported = control_mean > treatment_mean
    elif "control < treatment" in direction or "control<treatment" in direction:
        hypothesis_supported = control_mean < treatment_mean
    else:
        hypothesis_supported = treatment_mean != control_mean

    significant = p_value < 0.05

    if significant and hypothesis_supported:
        verdict = "supported"
    elif significant and not hypothesis_supported:
        verdict = "refuted"
    else:
        verdict = "inconclusive"

    return {
        "hypothesis_id": hypothesis.id,
        "statement": hypothesis.statement,
        "verdict": verdict,
        "treatment_mean": round(treatment_mean, 4),
        "control_mean": round(control_mean, 4),
        "effect_size_d": round(d, 4),
        "p_value": round(p_value, 6),
        "significant": significant,
        "n_treatment": len(treatment_runs),
        "n_control": len(control_runs),
    }


def _find_matching_runs(
    results: list[RunResult],
    value: str,
    dimension: str,
) -> list[RunResult]:
    """Find runs that match a treatment/control value."""
    from ..config import ALL_PRESETS

    matching = []
    for r in results:
        if not r.success:
            continue
        # Check if value matches preset name
        if value in ALL_PRESETS and r.config.preset == value:
            matching.append(r)
        # Check if value matches an override
        elif r.config.overrides and r.config.overrides.get(dimension) == value:
            matching.append(r)
        # Check if preset matches and the dimension matches the value
        elif r.config.preset == value:
            matching.append(r)
    return matching


# ── Finding Extraction ──────────────────────────────────────────────────────

def _extract_significant_findings(
    pairwise: list[dict[str, Any]],
    ranking: list[dict[str, Any]],
    campaign_id: str,
) -> list[dict[str, Any]]:
    """Extract statistically significant findings from pairwise comparisons."""
    findings = []

    for comparison in pairwise:
        if "comparisons" not in comparison:
            continue
        for metric, data in comparison["comparisons"].items():
            if data.get("significant_at_05") and data.get("effect_magnitude") in ("medium", "large"):
                findings.append({
                    "type": "comparative",
                    "statement": (
                        f"{data['winner']} outperforms "
                        f"{'config_b' if data['winner'] == comparison['config_a'] else 'config_a'} "
                        f"on {metric} (d={data['effect_size_d']}, p={data['p_value']:.4f})"
                    ),
                    "config_a": comparison["config_a"],
                    "config_b": comparison["config_b"],
                    "metric": metric,
                    "effect_size": data["effect_size_d"],
                    "p_value": data["p_value"],
                    "winner": data["winner"],
                    "campaign_id": campaign_id,
                })

    return findings


def extract_and_save_findings(
    analysis: dict[str, Any],
    store: KnowledgeStore,
    campaign_id: str,
    task: str = "",
    agents: int = 4,
    model: str = "",
) -> list[Finding]:
    """Convert significant analysis results into Finding objects and persist them."""
    significant = analysis.get("significant_findings", [])
    saved: list[Finding] = []

    for sf in significant:
        finding_id = store.next_finding_id()
        evidence = [
            EvidenceItem(
                campaign=campaign_id,
                run="aggregate",
                config=RunConfig(preset=sf.get("winner", "")),
                metric=sf["metric"],
                value=sf.get("effect_size", 0),
            ),
        ]

        # Determine confidence from p-value and effect size
        p_val = sf.get("p_value", 1.0)
        effect = abs(sf.get("effect_size", 0))
        if p_val < 0.01 and effect >= 0.8:
            confidence = 0.90
        elif p_val < 0.05 and effect >= 0.5:
            confidence = 0.75
        elif p_val < 0.05:
            confidence = 0.65
        else:
            confidence = 0.50

        finding = Finding(
            id=finding_id,
            statement=sf["statement"],
            confidence=confidence,
            type=FindingType.COMPARATIVE,
            evidence=evidence,
            conditions=FindingConditions(
                task_types=[task] if task else [],
                agent_count_range=[agents, agents],
                model=model or None,
                presets=[sf.get("config_a", ""), sf.get("config_b", "")],
            ),
            statistics=StatisticalTest(
                comparison=f"{sf.get('config_a', '')} vs {sf.get('config_b', '')}",
                metric=sf["metric"],
                effect_size=sf.get("effect_size", 0),
                p_value=sf.get("p_value", 1.0),
                significant=sf.get("p_value", 1.0) < 0.05,
                n_runs=0,
            ),
            source_campaign=campaign_id,
            tags=_generate_tags(sf),
        )
        store.save_finding(finding)
        saved.append(finding)

    return saved


def resolve_and_save_hypotheses(
    verdicts: list[dict[str, Any]],
    store: KnowledgeStore,
) -> list[Hypothesis]:
    """Update hypothesis statuses based on analysis verdicts."""
    updated: list[Hypothesis] = []

    for verdict in verdicts:
        h_id = verdict.get("hypothesis_id", "")
        h = store.get_hypothesis(h_id)
        if h is None:
            continue

        status_map = {
            "supported": HypothesisStatus.SUPPORTED,
            "refuted": HypothesisStatus.REFUTED,
            "inconclusive": HypothesisStatus.INCONCLUSIVE,
        }
        new_status = status_map.get(verdict["verdict"], HypothesisStatus.INCONCLUSIVE)

        # Add evidence
        if verdict.get("treatment_mean") is not None:
            item = EvidenceItem(
                campaign=verdict.get("campaign_id", ""),
                run="aggregate",
                config=RunConfig(preset=h.test_design.treatment),
                metric=h.test_design.outcome_metric,
                value=verdict["treatment_mean"],
            )
            if verdict["verdict"] == "supported":
                h.evidence.supporting.append(item)
            elif verdict["verdict"] == "refuted":
                h.evidence.contradicting.append(item)

        h.status = new_status
        h.resolved = utcnow()
        store.save_hypothesis(h)
        updated.append(h)

    return updated


def _generate_tags(sf: dict[str, Any]) -> list[str]:
    """Generate tags from a significant finding."""
    tags = []
    for key in ("config_a", "config_b", "winner"):
        val = sf.get(key, "")
        if val:
            # Extract preset name and any override keys
            parts = val.split("+")
            tags.append(parts[0])
            for part in parts[1:]:
                if "=" in part:
                    dim = part.split("=")[0]
                    tags.append(dim)
    metric = sf.get("metric", "")
    if metric:
        tags.append(metric)
    return list(set(tags))
