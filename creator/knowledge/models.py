"""Data models — the canonical schema for everything Creator Mode persists.

Every schema here mirrors the product bible (CREATOR_MODE_V1.md §7) exactly.
Pydantic v2 for validation, serialisation, and schema generation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class CampaignStatus(str, Enum):
    PLANNING = "planning"
    RUNNING = "running"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    STOPPED = "stopped"
    FAILED = "failed"


class CampaignType(str, Enum):
    EXPLORE = "explore"
    SPAWN_DIRECTED = "spawn_directed"
    SPAWN_EMERGENT = "spawn_emergent"
    RECURSIVE = "recursive"


class Arm(str, Enum):
    DIRECTED = "directed"
    EMERGENT = "emergent"
    BOTH = "both"


class Strategy(str, Enum):
    GRID = "grid"
    SWEEP = "sweep"
    HYPOTHESIS = "hypothesis"
    KNOWLEDGE = "knowledge"


class HypothesisStatus(str, Enum):
    UNTESTED = "untested"
    TESTING = "testing"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


class HypothesisPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingType(str, Enum):
    COMPARATIVE = "comparative"
    THRESHOLD = "threshold"
    CORRELATION = "correlation"
    EMERGENCE = "emergence"
    SCALING = "scaling"
    INTERACTION = "interaction"


class DataQuality(str, Enum):
    INSUFFICIENT = "insufficient"
    LIMITED = "limited"
    GOOD = "good"
    STRONG = "strong"


# ── Helpers ──────────────────────────────────────────────────────────────────

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Run Result ───────────────────────────────────────────────────────────────

class RunConfig(BaseModel):
    """The configuration that was used for a single experiment run."""
    preset: str
    overrides: dict[str, str] | None = None


class RunResult(BaseModel):
    """Structured metrics from a single engine experiment run.

    Maps directly to the RunResult dataclass in §9 of the product bible.
    """
    # Identity
    id: str = ""
    campaign_id: str = ""
    batch_id: str = ""
    run_index: int = 0

    # Configuration
    config: RunConfig
    agent_count: int
    model: str
    max_ticks: int

    # Primary outcomes
    quality_score: float = 0.0
    completion_rate: float = 0.0
    test_pass_rate: float | None = None

    # Coordination metrics
    ticks_used: int = 0
    total_messages: int = 0
    total_broadcasts: int = 0
    merge_conflicts: int = 0
    merges_succeeded: int = 0

    # Auto-org (if applicable)
    restructures_adopted: int = 0
    restructure_log: list[dict[str, Any]] = Field(default_factory=list)
    final_org_state: dict[str, str] = Field(default_factory=dict)

    # Efficiency
    total_tokens: int = 0
    tokens_per_agent: dict[str, int] = Field(default_factory=dict)
    wall_time_seconds: float = 0.0
    files_produced: int = 0

    # Specialisation
    emergent_specialisation: float = 0.0

    # Raw data (not indexed, but persisted for replay)
    chronicle_report: str = ""
    run_record: dict[str, Any] = Field(default_factory=dict)

    # Status
    success: bool = True
    error: str | None = None

    # Timestamps
    started: datetime = Field(default_factory=utcnow)
    completed: datetime | None = None


# ── Statistical Evidence ─────────────────────────────────────────────────────

class EvidenceItem(BaseModel):
    """A single piece of evidence linking a finding to a run."""
    campaign: str
    run: str
    config: RunConfig
    metric: str
    value: float


class StatisticalTest(BaseModel):
    """Result of a statistical comparison between two conditions."""
    comparison: str
    metric: str
    effect_size: float
    p_value: float
    significant: bool
    method: str = "independent_t_test"
    n_runs: int = 0


# ── Finding ──────────────────────────────────────────────────────────────────

class FindingConditions(BaseModel):
    """When a finding applies."""
    task_types: list[str] = Field(default_factory=list)
    agent_count_range: list[int | None] = Field(default_factory=lambda: [None, None])
    model: str | None = None
    presets: list[str] = Field(default_factory=list)
    dimensions: dict[str, str] = Field(default_factory=dict)


class FindingRelations(BaseModel):
    """How a finding relates to other findings."""
    supports: list[str] = Field(default_factory=list)
    contradicts: list[str] = Field(default_factory=list)
    extends: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    """A data-backed conclusion extracted from experiment results.

    The atomic unit of knowledge. Matches §7 Finding Schema exactly.
    """
    id: str
    statement: str
    confidence: float = Field(ge=0.0, le=1.0)
    type: FindingType = FindingType.COMPARATIVE

    evidence: list[EvidenceItem] = Field(default_factory=list)
    conditions: FindingConditions = Field(default_factory=FindingConditions)
    statistics: StatisticalTest | None = None
    related: FindingRelations = Field(default_factory=FindingRelations)

    discovered: datetime = Field(default_factory=utcnow)
    source_campaign: str = ""
    tags: list[str] = Field(default_factory=list)


# ── Hypothesis ───────────────────────────────────────────────────────────────

class TestDesign(BaseModel):
    """How to test a hypothesis — makes it concrete and falsifiable."""
    independent_variable: str = ""
    treatment: str = ""
    control: str = ""
    outcome_metric: str = "quality_score"
    expected_direction: str = ""  # e.g. "treatment > control"
    agent_count: int | None = None


class HypothesisEvidence(BaseModel):
    """Evidence collected while testing a hypothesis."""
    supporting: list[EvidenceItem] = Field(default_factory=list)
    contradicting: list[EvidenceItem] = Field(default_factory=list)


class Hypothesis(BaseModel):
    """A specific, testable prediction.

    Matches §7 Hypothesis Schema exactly.
    """
    id: str
    statement: str
    status: HypothesisStatus = HypothesisStatus.UNTESTED

    test_design: TestDesign = Field(default_factory=TestDesign)
    evidence: HypothesisEvidence = Field(default_factory=HypothesisEvidence)

    source: str = "hypothesis_engine"
    generated_from: str = ""
    generated: datetime = Field(default_factory=utcnow)
    resolved: datetime | None = None

    priority: HypothesisPriority = HypothesisPriority.MEDIUM
    tags: list[str] = Field(default_factory=list)


# ── Batch ────────────────────────────────────────────────────────────────────

class BatchStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class Batch(BaseModel):
    """A batch of experiments within a campaign."""
    id: str
    batch_number: int
    status: BatchStatus = BatchStatus.PLANNED
    configs: list[RunConfig] = Field(default_factory=list)
    runs_per_config: int = 3
    total_runs: int = 0
    rationale: str = ""
    run_ids: list[str] = Field(default_factory=list)


# ── Campaign ─────────────────────────────────────────────────────────────────

class CampaignConstraints(BaseModel):
    """Fixed parameters across all runs in a campaign."""
    agents: int = 4
    model: str = "claude-sonnet-4-6"
    max_ticks: int = 50
    task: str = ""
    task_is_benchmark: bool = False


class CampaignBudget(BaseModel):
    """Run budget tracking."""
    max_runs: int = 21
    runs_per_config: int = 3
    runs_completed: int = 0


class CampaignWinner(BaseModel):
    """The winning configuration from a completed campaign."""
    config: RunConfig
    metrics: dict[str, dict[str, float]] = Field(default_factory=dict)


class CampaignResult(BaseModel):
    """Final campaign results."""
    winner: CampaignWinner | None = None
    full_ranking: list[dict[str, Any]] = Field(default_factory=list)
    key_insight: str = ""


class Campaign(BaseModel):
    """A research inquiry — the top-level container.

    Matches §7 Campaign Schema exactly.
    """
    id: str
    question: str
    status: CampaignStatus = CampaignStatus.PLANNING
    type: CampaignType = CampaignType.EXPLORE
    arm: Arm = Arm.DIRECTED
    strategy: Strategy = Strategy.HYPOTHESIS

    created: datetime = Field(default_factory=utcnow)
    completed: datetime | None = None

    constraints: CampaignConstraints = Field(default_factory=CampaignConstraints)
    budget: CampaignBudget = Field(default_factory=CampaignBudget)

    batches: list[Batch] = Field(default_factory=list)
    run_ids: list[str] = Field(default_factory=list)

    findings_generated: list[str] = Field(default_factory=list)
    hypotheses_tested: list[str] = Field(default_factory=list)
    hypotheses_generated: list[str] = Field(default_factory=list)

    result: CampaignResult = Field(default_factory=CampaignResult)

    # Recursive loop fields (only for type=recursive)
    generations_planned: int = 0
    generations_completed: int = 0
    evolution_trajectory: list[dict[str, Any]] = Field(default_factory=list)


# ── Knowledge Index ──────────────────────────────────────────────────────────

class CoverageArm(BaseModel):
    """Coverage data for one arm (directed or emergent)."""
    presets_tested: list[str] = Field(default_factory=list)
    presets_untested: list[str] = Field(default_factory=list)
    dimensions_varied: list[str] = Field(default_factory=list)
    dimensions_unvaried: list[str] = Field(default_factory=list)
    agent_counts_tested: list[int] = Field(default_factory=list)
    task_types_tested: list[str] = Field(default_factory=list)
    # Emergent-specific
    simulations_run: int = 0
    conditions_tested: list[str] = Field(default_factory=list)
    conditions_untested: list[str] = Field(default_factory=list)
    max_ticks_tested: list[int] = Field(default_factory=list)


class HypothesesBreakdown(BaseModel):
    untested: int = 0
    supported: int = 0
    refuted: int = 0
    inconclusive: int = 0


class IndexStats(BaseModel):
    total_campaigns: int = 0
    total_runs: int = 0
    total_findings: int = 0
    total_hypotheses: int = 0
    hypotheses_breakdown: HypothesesBreakdown = Field(default_factory=HypothesesBreakdown)


class Coverage(BaseModel):
    directed: CoverageArm = Field(default_factory=CoverageArm)
    emergent: CoverageArm = Field(default_factory=CoverageArm)


class KnowledgeIndex(BaseModel):
    """The searchable index — rebuilt from findings/hypotheses on disk.

    Matches §7 Knowledge Index Schema.
    """
    version: int = 1
    last_updated: datetime = Field(default_factory=utcnow)
    stats: IndexStats = Field(default_factory=IndexStats)
    findings_by_tag: dict[str, list[str]] = Field(default_factory=dict)
    coverage: Coverage = Field(default_factory=Coverage)
