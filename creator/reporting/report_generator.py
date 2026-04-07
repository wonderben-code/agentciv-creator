"""Report generator — produces markdown campaign reports.

Generates structured reports with:
  - Executive summary
  - Methodology
  - Results table
  - Statistical findings
  - Hypothesis verdicts
  - Recommendations
  - Coverage analysis
"""

from __future__ import annotations

from typing import Any

from ..analysis.analyzer import (
    analyze_campaign,
    config_key,
)
from ..knowledge.index import SearchIndex
from ..knowledge.models import (
    Campaign,
    CampaignStatus,
    Finding,
    Hypothesis,
    RunResult,
)
from ..knowledge.store import KnowledgeStore


def generate_campaign_report(
    campaign_id: str,
    store: KnowledgeStore,
    search: SearchIndex,
) -> str:
    """Generate a full markdown report for a completed campaign.

    Returns markdown string. Also saves to campaign directory as report.md.
    """
    campaign = store.get_campaign(campaign_id)
    if campaign is None:
        return f"# Error\n\nCampaign {campaign_id} not found."

    results = store.list_run_results(campaign_id)
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    # Load related data
    hypotheses = []
    for h_id in campaign.hypotheses_generated:
        h = store.get_hypothesis(h_id)
        if h:
            hypotheses.append(h)

    findings = []
    for f_id in campaign.findings_generated:
        f = store.get_finding(f_id)
        if f:
            findings.append(f)

    # Run analysis
    analysis = {}
    if successful:
        analysis = analyze_campaign(successful, hypotheses=hypotheses, campaign_id=campaign_id)

    # Build report
    sections = [
        _header(campaign),
        _executive_summary(campaign, successful, failed, analysis),
        _methodology(campaign),
        _results_table(successful, analysis),
        _findings_section(findings),
        _hypotheses_section(hypotheses),
        _recommendations(campaign, analysis, search),
        _coverage_section(search),
        _appendix(campaign, results),
    ]

    report = "\n\n".join(s for s in sections if s)

    # Save to campaign directory
    report_path = store._campaign_dir(campaign_id) / "report.md"
    report_path.write_text(report)

    return report


def _header(campaign: Campaign) -> str:
    """Report header."""
    status_emoji = {
        CampaignStatus.COMPLETE: "Complete",
        CampaignStatus.RUNNING: "Running",
        CampaignStatus.FAILED: "Failed",
        CampaignStatus.ANALYZING: "Analyzing",
    }
    status = status_emoji.get(campaign.status, campaign.status.value)

    return f"""# Campaign Report: {campaign.id}

**Question:** {campaign.question}
**Status:** {status}
**Strategy:** {campaign.strategy.value}
**Arm:** {campaign.arm.value}
**Created:** {campaign.created.strftime('%Y-%m-%d %H:%M UTC')}
{f'**Completed:** {campaign.completed.strftime("%Y-%m-%d %H:%M UTC")}' if campaign.completed else ''}

---"""


def _executive_summary(
    campaign: Campaign,
    successful: list[RunResult],
    failed: list[RunResult],
    analysis: dict[str, Any],
) -> str:
    """Executive summary section."""
    if not successful:
        return "## Executive Summary\n\nNo successful runs to analyze."

    winner = analysis.get("winner", {})
    winner_key = winner.get("config_key", "unknown")
    winner_score = winner.get("mean", 0)

    total = len(successful) + len(failed)
    success_rate = len(successful) / total * 100 if total > 0 else 0

    lines = [
        "## Executive Summary",
        "",
        f"- **{total} experiments** run across **{analysis.get('configs_tested', 0)} configurations**",
        f"- **{len(successful)} succeeded** ({success_rate:.0f}% success rate)",
        f"- **Winner:** `{winner_key}` with quality score **{winner_score:.3f}**",
        f"- **Data quality:** {analysis.get('data_quality', 'unknown')}",
    ]

    # Key insight
    if campaign.result.key_insight:
        lines.append(f"- **Key insight:** {campaign.result.key_insight}")

    # Significant findings count
    sig_findings = analysis.get("significant_findings", [])
    if sig_findings:
        lines.append(f"- **{len(sig_findings)} statistically significant findings** extracted")

    return "\n".join(lines)


def _methodology(campaign: Campaign) -> str:
    """Methodology section."""
    c = campaign.constraints
    b = campaign.budget

    lines = [
        "## Methodology",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
        f"| Strategy | {campaign.strategy.value} |",
        f"| Agents | {c.agents} |",
        f"| Model | {c.model} |",
        f"| Max ticks | {c.max_ticks} |",
        f"| Task | {c.task} |",
        f"| Runs per config | {b.runs_per_config} |",
        f"| Total budget | {b.max_runs} |",
        f"| Runs completed | {b.runs_completed} |",
    ]

    # Batch details
    if campaign.batches:
        lines.append("")
        lines.append("### Batches")
        lines.append("")
        for batch in campaign.batches:
            configs_str = ", ".join(
                config_key(c) for c in batch.configs[:5]
            )
            if len(batch.configs) > 5:
                configs_str += f" (+{len(batch.configs) - 5} more)"
            lines.append(f"- **Batch {batch.batch_number}** ({batch.status.value}): {configs_str}")
            lines.append(f"  - Rationale: {batch.rationale}")

    return "\n".join(lines)


def _results_table(
    results: list[RunResult],
    analysis: dict[str, Any],
) -> str:
    """Results ranking table."""
    ranking = analysis.get("ranking", [])
    if not ranking:
        return ""

    lines = [
        "## Results",
        "",
        "### Rankings (by quality score)",
        "",
        "| Rank | Config | Quality (mean) | Quality (std) | N |",
        "|------|--------|---------------|---------------|---|",
    ]

    for entry in ranking:
        lines.append(
            f"| {entry['rank']} | `{entry['config_key']}` | "
            f"{entry['mean']:.3f} | {entry['std']:.3f} | {entry['n']} |"
        )

    # Aggregates detail
    aggregates = analysis.get("aggregates", {})
    if aggregates:
        lines.append("")
        lines.append("### Detailed Metrics")
        lines.append("")
        lines.append("| Config | Quality | Conflicts | Ticks | N |")
        lines.append("|--------|---------|-----------|-------|---|")

        for key in [r["config_key"] for r in ranking]:
            agg = aggregates.get(key, {})
            q = agg.get("quality_score", {})
            c = agg.get("merge_conflicts", {})
            t = agg.get("ticks_used", {})
            n = agg.get("n", 0)
            lines.append(
                f"| `{key}` | {q.get('mean', 0):.3f} | "
                f"{c.get('mean', 0):.1f} | {t.get('mean', 0):.1f} | {n} |"
            )

    return "\n".join(lines)


def _findings_section(findings: list[Finding]) -> str:
    """Findings section."""
    if not findings:
        return ""

    lines = [
        "## Findings",
        "",
    ]

    for f in findings:
        sig_marker = ""
        if f.statistics:
            if f.statistics.p_value < 0.01:
                sig_marker = " (p < 0.01)"
            elif f.statistics.p_value < 0.05:
                sig_marker = " (p < 0.05)"

        lines.append(f"### {f.id}: {f.statement}")
        lines.append("")
        lines.append(f"- **Confidence:** {f.confidence:.2f}{sig_marker}")
        lines.append(f"- **Type:** {f.type.value}")
        if f.statistics:
            lines.append(f"- **Effect size (d):** {f.statistics.effect_size:.3f}")
            lines.append(f"- **p-value:** {f.statistics.p_value:.6f}")
        if f.conditions.task_types:
            lines.append(f"- **Task types:** {', '.join(f.conditions.task_types)}")
        if f.tags:
            lines.append(f"- **Tags:** {', '.join(f.tags)}")
        lines.append("")

    return "\n".join(lines)


def _hypotheses_section(hypotheses: list[Hypothesis]) -> str:
    """Hypotheses section."""
    if not hypotheses:
        return ""

    lines = [
        "## Hypotheses",
        "",
        "| ID | Statement | Status | Priority |",
        "|----|-----------|--------|----------|",
    ]

    for h in hypotheses:
        status_marker = {
            "supported": "Supported",
            "refuted": "Refuted",
            "inconclusive": "Inconclusive",
            "untested": "Untested",
        }.get(h.status.value, h.status.value)

        lines.append(
            f"| {h.id} | {h.statement[:60]}{'...' if len(h.statement) > 60 else ''} | "
            f"{status_marker} | {h.priority.value} |"
        )

    return "\n".join(lines)


def _recommendations(
    campaign: Campaign,
    analysis: dict[str, Any],
    search: SearchIndex,
) -> str:
    """Recommendations section."""
    lines = ["## Recommendations", ""]

    winner = analysis.get("winner", {})
    if winner:
        lines.append(f"**Recommended config:** `{winner.get('config_key', 'unknown')}`")
        lines.append(f"**Quality score:** {winner.get('mean', 0):.3f}")
        lines.append("")

    # Suggestions from search index
    suggestions = search.suggest_next()
    if suggestions:
        lines.append("### Next Steps")
        lines.append("")
        for s in suggestions:
            lines.append(f"- {s}")

    return "\n".join(lines)


def _coverage_section(search: SearchIndex) -> str:
    """Coverage analysis section."""
    coverage = search.compute_coverage()
    gaps = search.identify_gaps()

    lines = [
        "## Coverage Analysis",
        "",
        f"- **Presets tested:** {', '.join(coverage.directed.presets_tested) or 'none'}",
        f"- **Presets untested:** {', '.join(coverage.directed.presets_untested) or 'all covered'}",
        f"- **Dimensions varied:** {', '.join(coverage.directed.dimensions_varied) or 'none'}",
        f"- **Dimensions unvaried:** {', '.join(coverage.directed.dimensions_unvaried) or 'all covered'}",
    ]

    if gaps:
        lines.append("")
        lines.append("### Gaps")
        lines.append("")
        for g in gaps:
            lines.append(f"- **{g.area}:** {g.description} (priority: {g.priority})")

    return "\n".join(lines)


def _appendix(campaign: Campaign, results: list[RunResult]) -> str:
    """Appendix with raw data summary."""
    lines = [
        "## Appendix",
        "",
        f"- Campaign ID: {campaign.id}",
        f"- Total runs: {len(results)}",
        f"- Successful: {sum(1 for r in results if r.success)}",
        f"- Failed: {sum(1 for r in results if not r.success)}",
    ]

    # Failed run details
    failed = [r for r in results if not r.success]
    if failed:
        lines.append("")
        lines.append("### Failed Runs")
        lines.append("")
        for r in failed:
            lines.append(f"- `{r.id}` ({config_key(r.config)}): {r.error}")

    lines.append("")
    lines.append("---")
    lines.append("*Generated by Creator Mode v0.1.0*")

    return "\n".join(lines)
