"""Campaign manager — lifecycle management for research campaigns.

Handles: create → plan → run → analyze → complete.
Each transition is atomic — campaign state is persisted after every change.
"""

from __future__ import annotations

import logging
from typing import Any

from ..knowledge.index import SearchIndex
from ..knowledge.models import (
    Arm,
    BatchStatus,
    Campaign,
    CampaignBudget,
    CampaignConstraints,
    CampaignStatus,
    CampaignType,
    RunResult,
    Strategy,
    utcnow,
)
from ..knowledge.store import KnowledgeStore
from .meta_reasoner import recommend as meta_recommend
from .planner import generate_plan

log = logging.getLogger(__name__)


class CampaignManager:
    """Manages the full lifecycle of research campaigns."""

    def __init__(self, store: KnowledgeStore, search: SearchIndex) -> None:
        self._store = store
        self._search = search

    async def create_campaign(
        self,
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
    ) -> dict[str, Any]:
        """Create a new campaign, generate the first batch plan, and return status.

        This is the entry point for creator_explore().

        When arm="auto", the meta-reasoner analyses the goal against the Knowledge
        Store and recommends the optimal arm (DIRECTED, EMERGENT, or BOTH) with
        transparent reasoning.
        """
        campaign_id = self._store.next_campaign_id()

        # Meta-reasoning: resolve "auto" to a concrete arm + strategy
        meta_reasoning: dict[str, Any] | None = None
        if arm == "auto":
            rec = meta_recommend(
                question=question,
                task=task,
                store=self._store,
                search=self._search,
            )
            arm = rec.arm.value
            strategy = rec.strategy.value
            meta_reasoning = {
                "recommended_arm": rec.arm.value,
                "recommended_strategy": rec.strategy.value,
                "confidence": rec.confidence,
                "reasoning": rec.reasoning,
                "factors": [
                    {
                        "name": f.name,
                        "signal": f.signal,
                        "weight": f.weight,
                        "explanation": f.explanation,
                    }
                    for f in rec.factors
                ],
            }
            log.info(
                "Meta-reasoner → arm=%s, strategy=%s (confidence=%.0f%%)",
                arm, strategy, rec.confidence * 100,
            )

        strategy_enum = Strategy(strategy)
        arm_enum = Arm(arm)

        campaign = Campaign(
            id=campaign_id,
            question=question,
            status=CampaignStatus.PLANNING,
            type=CampaignType.EXPLORE,
            arm=arm_enum,
            strategy=strategy_enum,
            constraints=CampaignConstraints(
                agents=agents,
                model=model,
                max_ticks=max_ticks,
                task=task,
            ),
            budget=CampaignBudget(
                max_runs=max_runs,
                runs_per_config=runs_per_config,
            ),
        )
        self._store.save_campaign(campaign)

        # Generate batch 1 plan
        batch, hypotheses, plan_message = await generate_plan(
            question=question,
            task=task,
            strategy=strategy_enum,
            agents=agents,
            model=model,
            max_ticks=max_ticks,
            max_runs=max_runs,
            runs_per_config=runs_per_config,
            focus_presets=focus_presets,
            focus_dimensions=focus_dimensions,
            store=self._store,
            search=self._search,
            arm=arm_enum,
        )

        # Update campaign with plan
        campaign.batches.append(batch)
        campaign.hypotheses_generated.extend(h.id for h in hypotheses)
        self._store.save_campaign(campaign)

        # Build response
        response: dict[str, Any] = {
            "campaign_id": campaign_id,
            "status": "planning",
            "strategy": strategy,
            "arm": arm,
            "initial_hypotheses": [
                {
                    "id": h.id,
                    "statement": h.statement,
                    "priority": h.priority.value,
                    "tags": h.tags,
                }
                for h in hypotheses
            ],
            "plan": {
                "batch_1": {
                    "configs": [c.model_dump() for c in batch.configs],
                    "runs_per_config": batch.runs_per_config,
                    "total_runs": batch.total_runs,
                    "rationale": batch.rationale,
                },
                "remaining_budget": max_runs - batch.total_runs,
            },
            "constraints": {
                "agents": agents,
                "model": model,
                "max_ticks": max_ticks,
                "task": task,
            },
            "message": plan_message,
        }

        if meta_reasoning is not None:
            response["meta_reasoning"] = meta_reasoning

        return response

    async def run_campaign(
        self,
        campaign_id: str,
        project_dir: str = ".",
        session_manager: object | None = None,
    ) -> dict[str, Any]:
        """Execute the planned batch of experiments.

        Dispatches to Engine runner (directed arm) or Simulation runner
        (emergent arm) based on the campaign's arm setting.
        Returns results summary.
        """
        campaign = self._store.get_campaign(campaign_id)
        if campaign is None:
            return {"error": f"Campaign {campaign_id} not found"}

        if campaign.status == CampaignStatus.COMPLETE:
            return {"error": f"Campaign {campaign_id} is already complete"}

        # Find the batch to run
        batch = None
        for b in campaign.batches:
            if b.status == BatchStatus.PLANNED:
                batch = b
                break

        if batch is None:
            return {"error": "No planned batches to run"}

        # Mark campaign and batch as running
        campaign.status = CampaignStatus.RUNNING
        batch.status = BatchStatus.RUNNING
        self._store.save_campaign(campaign)

        try:
            if campaign.arm == Arm.BOTH:
                results = await self._run_hybrid_batch(
                    batch=batch,
                    campaign=campaign,
                    project_dir=project_dir,
                    session_manager=session_manager,
                )
            elif campaign.arm == Arm.EMERGENT:
                results = await self._run_emergence_batch(
                    batch=batch,
                    campaign=campaign,
                    session_manager=session_manager,
                )
            else:
                results = await self._run_directed_batch(
                    batch=batch,
                    campaign=campaign,
                    project_dir=project_dir,
                    session_manager=session_manager,
                )

            # Save individual run results
            for result in results:
                result.campaign_id = campaign_id
                result.batch_id = batch.id
                self._store.save_run_result(campaign_id, result)
                batch.run_ids.append(result.id)
                campaign.run_ids.append(result.id)

            # Update budget
            campaign.budget.runs_completed += len(results)

            # Mark batch complete
            batch.status = BatchStatus.COMPLETE
            campaign.status = CampaignStatus.ANALYZING
            self._store.save_campaign(campaign)

            # Build results summary
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]

            return {
                "campaign_id": campaign_id,
                "batch_id": batch.id,
                "status": "batch_complete",
                "arm": campaign.arm.value,
                "runs_completed": len(results),
                "runs_succeeded": len(successful),
                "runs_failed": len(failed),
                "results_summary": _summarise_by_arm(successful, campaign.arm),
                "message": (
                    f"Batch {batch.batch_number} complete ({campaign.arm.value}): "
                    f"{len(successful)}/{len(results)} runs succeeded."
                ),
            }

        except Exception as e:
            log.exception("Campaign %s batch execution failed", campaign_id)
            batch.status = BatchStatus.FAILED
            campaign.status = CampaignStatus.FAILED
            self._store.save_campaign(campaign)
            return {
                "campaign_id": campaign_id,
                "status": "failed",
                "error": str(e),
            }

    async def _run_directed_batch(
        self,
        batch: "Batch",
        campaign: Campaign,
        project_dir: str,
        session_manager: object | None,
    ) -> list[RunResult]:
        """Run a batch of Engine experiments."""
        from ..engine.runner import run_batch

        return await run_batch(
            configs=batch.configs,
            task=campaign.constraints.task,
            agents=campaign.constraints.agents,
            model=campaign.constraints.model,
            max_ticks=campaign.constraints.max_ticks,
            runs_per_config=batch.runs_per_config,
            project_dir=project_dir,
            session_manager=session_manager,
            campaign_id=campaign.id,
        )

    async def _run_emergence_batch(
        self,
        batch: "Batch",
        campaign: Campaign,
        session_manager: object | None,
    ) -> list[RunResult]:
        """Run a batch of Simulation experiments and convert results."""
        from ..simulation.runner import (
            SimRunConfig,
            run_simulation_batch,
            sim_result_to_run_result,
        )

        # Convert RunConfig → SimRunConfig
        sim_configs = []
        for rc in batch.configs:
            overrides = {}
            if rc.overrides:
                for k, v in rc.overrides.items():
                    # Try to convert numeric strings back to numbers
                    try:
                        overrides[k] = float(v) if "." in v else int(v)
                    except (ValueError, TypeError):
                        overrides[k] = v
            sim_configs.append(SimRunConfig(
                condition_name=rc.preset,
                agents=campaign.constraints.agents,
                ticks=campaign.constraints.max_ticks,
                overrides=overrides,
            ))

        # Run simulations
        sim_results = await run_simulation_batch(
            configs=sim_configs,
            ticks=campaign.constraints.max_ticks,
            runs_per_config=batch.runs_per_config,
            model=campaign.constraints.model,
            session_manager=session_manager,
            campaign_id=campaign.id,
        )

        # Convert to unified RunResult
        return [
            sim_result_to_run_result(
                sr,
                agent_count=campaign.constraints.agents,
                model=campaign.constraints.model,
                max_ticks=campaign.constraints.max_ticks,
            )
            for sr in sim_results
        ]

    async def _run_hybrid_batch(
        self,
        batch: "Batch",
        campaign: Campaign,
        project_dir: str,
        session_manager: object | None,
    ) -> list[RunResult]:
        """Run HYBRID: emergence first → translate patterns → test as Engine configs.

        This is the world-first capability: emergent patterns from AI civilisations
        translated into practical team configurations and tested on real tasks.

        Returns combined results from both arms.
        """
        from ..simulation.translator import translate_emergence_to_engine

        # Step 1: Run emergence experiments
        log.info("HYBRID Step 1: Running emergence experiments for campaign %s", campaign.id)
        emergence_results = await self._run_emergence_batch(
            batch=batch,
            campaign=campaign,
            session_manager=session_manager,
        )

        successful_emergence = [r for r in emergence_results if r.success]
        if not successful_emergence:
            log.warning("HYBRID: No successful emergence runs — skipping translation")
            return emergence_results

        # Step 2: Translate emergent patterns → Engine config
        log.info("HYBRID Step 2: Translating %d emergence runs → Engine config", len(successful_emergence))
        translation = translate_emergence_to_engine(successful_emergence)
        log.info(
            "HYBRID translation (confidence=%.2f): %s",
            translation.overall_confidence,
            {m.dimension: m.value for m in translation.mappings if m.confidence >= 0.4},
        )

        # Step 3: Build Engine batch from translated config + comparison presets
        from ..engine.runner import run_batch

        # The translated config + a few baselines for comparison
        engine_configs = [translation.config]
        comparison_presets = ["collaborative", "hierarchical", "auto"]
        for preset in comparison_presets:
            if preset != translation.config.preset:
                engine_configs.append(RunConfig(preset=preset))

        log.info("HYBRID Step 3: Running %d Engine configs against task", len(engine_configs))
        from ..knowledge.models import RunConfig as _RC  # noqa: just for type
        engine_results = await run_batch(
            configs=engine_configs,
            task=campaign.constraints.task,
            agents=campaign.constraints.agents,
            model=campaign.constraints.model,
            max_ticks=campaign.constraints.max_ticks,
            runs_per_config=batch.runs_per_config,
            project_dir=project_dir,
            session_manager=session_manager,
            campaign_id=campaign.id,
        )

        # Tag the translated config's results so we can identify them
        for r in engine_results:
            if r.config.overrides and translation.config.overrides:
                if r.config.overrides == translation.config.overrides:
                    r.run_record["hybrid_translated"] = True
                    r.run_record["translation_confidence"] = translation.overall_confidence
                    r.run_record["translation_summary"] = translation.summary

        # Return all results — emergence + engine
        return emergence_results + engine_results

    def complete_campaign(self, campaign_id: str) -> dict[str, Any]:
        """Mark a campaign as complete and generate final results."""
        campaign = self._store.get_campaign(campaign_id)
        if campaign is None:
            return {"error": f"Campaign {campaign_id} not found"}

        # Load all run results
        results = self._store.list_run_results(campaign_id)
        successful = [r for r in results if r.success]
        is_emergence = campaign.arm == Arm.EMERGENT

        if successful:
            # Determine winner using arm-appropriate metric
            best = max(successful, key=lambda r: r.primary_score)

            if is_emergence:
                winner_metrics = {
                    "emergence_score": {"mean": best.emergence_score},
                    "ticks_used": {"mean": float(best.ticks_used)},
                }
            else:
                winner_metrics = {
                    "quality_score": {"mean": best.quality_score},
                    "merge_conflicts": {"mean": float(best.merge_conflicts)},
                    "ticks_used": {"mean": float(best.ticks_used)},
                }

            campaign.result.winner = {
                "config": best.config,
                "metrics": winner_metrics,
            }

            # Build ranking
            from collections import defaultdict
            by_config: dict[str, list[RunResult]] = defaultdict(list)
            for r in successful:
                key = r.config.preset + (
                    f"+{'+'.join(f'{k}={v}' for k, v in sorted(r.config.overrides.items()))}"
                    if r.config.overrides else ""
                )
                by_config[key].append(r)

            score_label = "emergence_mean" if is_emergence else "quality_mean"
            ranking = []
            for key, runs in by_config.items():
                avg_score = sum(r.primary_score for r in runs) / len(runs)
                ranking.append({"config": key, score_label: round(avg_score, 3), "n": len(runs)})

            ranking.sort(key=lambda x: list(x.values())[1], reverse=True)
            campaign.result.full_ranking = ranking

        campaign.status = CampaignStatus.COMPLETE
        campaign.completed = utcnow()
        self._store.save_campaign(campaign)

        return {
            "campaign_id": campaign_id,
            "status": "complete",
            "arm": campaign.arm.value,
            "total_runs": len(results),
            "winner": campaign.result.winner,
            "ranking": campaign.result.full_ranking,
        }


def _summarise_by_arm(
    results: list[RunResult], arm: Arm,
) -> dict[str, list[dict[str, Any]]]:
    """Summarise results, splitting by arm for HYBRID campaigns."""
    if arm == Arm.BOTH:
        emergence = [r for r in results if r.arm == Arm.EMERGENT]
        directed = [r for r in results if r.arm == Arm.DIRECTED]
        summary: dict[str, Any] = {}
        if emergence:
            summary["emergence"] = _summarise_emergence_results(emergence)
        if directed:
            summary["directed"] = _summarise_results(directed)
        return summary
    elif arm == Arm.EMERGENT:
        return {"emergence": _summarise_emergence_results(results)}
    else:
        return {"directed": _summarise_results(results)}


def _summarise_emergence_results(results: list[RunResult]) -> list[dict[str, Any]]:
    """Create a per-condition summary from emergence run results."""
    from collections import defaultdict
    by_config: dict[str, list[RunResult]] = defaultdict(list)

    for r in results:
        key = r.config.preset + (
            f" ({', '.join(f'{k}={v}' for k, v in sorted(r.config.overrides.items()))})"
            if r.config.overrides else ""
        )
        by_config[key].append(r)

    summaries = []
    for key, runs in sorted(by_config.items()):
        avg_emergence = sum(r.emergence_score for r in runs) / len(runs)
        avg_ticks = sum(r.ticks_used for r in runs) / len(runs)
        # Extract key emergence sub-metrics if available
        governance = _avg_metric(runs, "rules_established")
        cooperation = _avg_metric(runs, "cooperation_events")
        innovation = _avg_metric(runs, "innovation_count")
        summaries.append({
            "condition": key,
            "runs": len(runs),
            "emergence_mean": round(avg_emergence, 4),
            "ticks_mean": round(avg_ticks, 1),
            "governance_mean": round(governance, 1) if governance else None,
            "cooperation_mean": round(cooperation, 1) if cooperation else None,
            "innovation_mean": round(innovation, 1) if innovation else None,
        })

    summaries.sort(key=lambda x: x["emergence_mean"], reverse=True)
    return summaries


def _avg_metric(runs: list[RunResult], metric_key: str) -> float | None:
    """Extract average of a sub-metric from emergence_metrics dicts."""
    values = [r.emergence_metrics.get(metric_key, 0) for r in runs if r.emergence_metrics]
    if not values:
        return None
    return sum(values) / len(values)


def _summarise_results(results: list[RunResult]) -> list[dict[str, Any]]:
    """Create a per-config summary from run results."""
    from collections import defaultdict
    by_config: dict[str, list[RunResult]] = defaultdict(list)

    for r in results:
        key = r.config.preset + (
            f" ({', '.join(f'{k}={v}' for k, v in sorted(r.config.overrides.items()))})"
            if r.config.overrides else ""
        )
        by_config[key].append(r)

    summaries = []
    for key, runs in sorted(by_config.items()):
        avg_quality = sum(r.quality_score for r in runs) / len(runs)
        avg_conflicts = sum(r.merge_conflicts for r in runs) / len(runs)
        avg_ticks = sum(r.ticks_used for r in runs) / len(runs)
        summaries.append({
            "config": key,
            "runs": len(runs),
            "quality_mean": round(avg_quality, 3),
            "conflicts_mean": round(avg_conflicts, 1),
            "ticks_mean": round(avg_ticks, 1),
        })

    summaries.sort(key=lambda x: x["quality_mean"], reverse=True)
    return summaries
