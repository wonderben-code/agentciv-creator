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
        """
        campaign_id = self._store.next_campaign_id()
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
        )

        # Update campaign with plan
        campaign.batches.append(batch)
        campaign.hypotheses_generated.extend(h.id for h in hypotheses)
        self._store.save_campaign(campaign)

        # Build response
        return {
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

    async def run_campaign(
        self,
        campaign_id: str,
        project_dir: str = ".",
        session_manager: object | None = None,
    ) -> dict[str, Any]:
        """Execute the planned batch of experiments.

        Uses the engine runner to run experiments in parallel.
        If session_manager is provided, tracks costs and archives chronicles.
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

        # Import engine runner (deferred to avoid import at module load)
        from ..engine.runner import run_batch

        try:
            results = await run_batch(
                configs=batch.configs,
                task=campaign.constraints.task,
                agents=campaign.constraints.agents,
                model=campaign.constraints.model,
                max_ticks=campaign.constraints.max_ticks,
                runs_per_config=batch.runs_per_config,
                project_dir=project_dir,
                session_manager=session_manager,
                campaign_id=campaign_id,
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
                "runs_completed": len(results),
                "runs_succeeded": len(successful),
                "runs_failed": len(failed),
                "results_summary": _summarise_results(successful),
                "message": (
                    f"Batch {batch.batch_number} complete: "
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

    def complete_campaign(self, campaign_id: str) -> dict[str, Any]:
        """Mark a campaign as complete and generate final results."""
        campaign = self._store.get_campaign(campaign_id)
        if campaign is None:
            return {"error": f"Campaign {campaign_id} not found"}

        # Load all run results
        results = self._store.list_run_results(campaign_id)
        successful = [r for r in results if r.success]

        if successful:
            # Determine winner
            best = max(successful, key=lambda r: r.quality_score)
            campaign.result.winner = {
                "config": best.config,
                "metrics": {
                    "quality_score": {"mean": best.quality_score},
                    "merge_conflicts": {"mean": float(best.merge_conflicts)},
                    "ticks_used": {"mean": float(best.ticks_used)},
                },
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

            ranking = []
            for key, runs in by_config.items():
                avg_quality = sum(r.quality_score for r in runs) / len(runs)
                ranking.append({"config": key, "quality_mean": round(avg_quality, 3), "n": len(runs)})

            ranking.sort(key=lambda x: x["quality_mean"], reverse=True)
            campaign.result.full_ranking = ranking

        campaign.status = CampaignStatus.COMPLETE
        campaign.completed = utcnow()
        self._store.save_campaign(campaign)

        return {
            "campaign_id": campaign_id,
            "status": "complete",
            "total_runs": len(results),
            "winner": campaign.result.winner,
            "ranking": campaign.result.full_ranking,
        }


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
