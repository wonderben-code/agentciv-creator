"""Knowledge Store — persistent CRUD for findings, hypotheses, and campaigns.

All data lives as JSON files on disk at ~/.agentciv-creator/.
Writes are atomic (write to temp → rename) to prevent corruption.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from ..config import (
    CAMPAIGN_PREFIX,
    CREATOR_HOME,
    FINDING_PREFIX,
    HYPOTHESIS_PREFIX,
    KNOWLEDGE_STORE_VERSION,
)
from .models import (
    Campaign,
    CampaignStatus,
    Finding,
    Hypothesis,
    HypothesisStatus,
    KnowledgeIndex,
    RunResult,
    utcnow,
)


def _atomic_write(path: Path, data: str) -> None:
    """Write data to a file atomically — prevents corruption on crash."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        os.write(fd, data.encode("utf-8"))
        os.close(fd)
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _read_json(path: Path) -> dict[str, Any] | None:
    """Read a JSON file, returning None if it doesn't exist."""
    if not path.exists():
        return None
    return json.loads(path.read_text("utf-8"))


class KnowledgeStore:
    """Persistent knowledge across all campaigns.

    Thread-safe for single-process use (atomic writes, no shared mutable state).
    Not designed for multi-process concurrent access — that's a v2 concern.

    Accepts optional root_dir to override the default ~/.agentciv-creator/ path.
    This is used in tests to avoid polluting the real store.
    """

    def __init__(self, root_dir: Path | None = None) -> None:
        self._root = root_dir or CREATOR_HOME
        self._knowledge_dir = self._root / "knowledge"
        self._findings_dir = self._knowledge_dir / "findings"
        self._hypotheses_dir = self._knowledge_dir / "hypotheses"
        self._campaigns_dir = self._root / "campaigns"
        self._index_path = self._knowledge_dir / "index.json"

        # Create directory structure
        for d in (self._root, self._knowledge_dir, self._findings_dir,
                  self._hypotheses_dir, self._campaigns_dir):
            d.mkdir(parents=True, exist_ok=True)

        self._index: KnowledgeIndex | None = None

    # ── Index ────────────────────────────────────────────────────────────

    def _load_index(self) -> KnowledgeIndex:
        """Load the index from disk, or create a fresh one."""
        data = _read_json(self._index_path)
        if data is not None:
            return KnowledgeIndex.model_validate(data)
        return KnowledgeIndex(version=KNOWLEDGE_STORE_VERSION)

    def _save_index(self, index: KnowledgeIndex) -> None:
        """Persist the index to disk."""
        index.last_updated = utcnow()
        _atomic_write(self._index_path, index.model_dump_json(indent=2))
        self._index = index

    @property
    def index(self) -> KnowledgeIndex:
        if self._index is None:
            self._index = self._load_index()
        return self._index

    def rebuild_index(self) -> KnowledgeIndex:
        """Rebuild the index from all findings and hypotheses on disk."""
        findings = self.list_findings()
        hypotheses = self.list_hypotheses()
        campaigns = self.list_campaigns()

        # Stats
        total_runs = sum(c.budget.runs_completed for c in campaigns)
        breakdown = {"untested": 0, "supported": 0, "refuted": 0, "inconclusive": 0}
        for h in hypotheses:
            key = h.status.value
            if key in breakdown:
                breakdown[key] += 1

        # Findings by tag
        findings_by_tag: dict[str, list[str]] = {}
        for f in findings:
            for tag in f.tags:
                findings_by_tag.setdefault(tag, []).append(f.id)

        idx = KnowledgeIndex(
            version=KNOWLEDGE_STORE_VERSION,
            last_updated=utcnow(),
            stats={
                "total_campaigns": len(campaigns),
                "total_runs": total_runs,
                "total_findings": len(findings),
                "total_hypotheses": len(hypotheses),
                "hypotheses_breakdown": breakdown,
            },
            findings_by_tag=findings_by_tag,
        )
        self._save_index(idx)
        return idx

    # ── ID generation ────────────────────────────────────────────────────

    def _next_id(self, prefix: str, directory: Path) -> str:
        """Generate the next sequential ID for a given prefix."""
        existing = sorted(directory.glob(f"{prefix}*.json"))
        if not existing:
            return f"{prefix}001"
        last = existing[-1].stem
        # Extract numeric part after prefix
        num_str = last[len(prefix):]
        try:
            num = int(num_str) + 1
        except ValueError:
            num = len(existing) + 1
        return f"{prefix}{num:03d}"

    def next_finding_id(self) -> str:
        return self._next_id(FINDING_PREFIX, self._findings_dir)

    def next_hypothesis_id(self) -> str:
        return self._next_id(HYPOTHESIS_PREFIX, self._hypotheses_dir)

    def next_campaign_id(self) -> str:
        existing = sorted(
            d.name for d in self._campaigns_dir.iterdir()
            if d.is_dir() and d.name.startswith(CAMPAIGN_PREFIX)
        )
        if not existing:
            return f"{CAMPAIGN_PREFIX}001"
        last = existing[-1]
        num_str = last[len(CAMPAIGN_PREFIX):]
        try:
            num = int(num_str) + 1
        except ValueError:
            num = len(existing) + 1
        return f"{CAMPAIGN_PREFIX}{num:03d}"

    # ── Findings CRUD ────────────────────────────────────────────────────

    def save_finding(self, finding: Finding) -> Finding:
        """Persist a finding to disk and update the index."""
        path = self._findings_dir / f"{finding.id}.json"
        _atomic_write(path, finding.model_dump_json(indent=2))

        # Update index
        idx = self._load_index()
        for tag in finding.tags:
            tag_list = idx.findings_by_tag.setdefault(tag, [])
            if finding.id not in tag_list:
                tag_list.append(finding.id)
        idx.stats.total_findings = len(list(self._findings_dir.glob(f"{FINDING_PREFIX}*.json")))
        self._save_index(idx)

        return finding

    def get_finding(self, finding_id: str) -> Finding | None:
        """Load a single finding by ID."""
        path = self._findings_dir / f"{finding_id}.json"
        data = _read_json(path)
        if data is None:
            return None
        return Finding.model_validate(data)

    def list_findings(self) -> list[Finding]:
        """Load all findings from disk."""
        findings = []
        for path in sorted(self._findings_dir.glob(f"{FINDING_PREFIX}*.json")):
            data = _read_json(path)
            if data is not None:
                findings.append(Finding.model_validate(data))
        return findings

    def delete_finding(self, finding_id: str) -> bool:
        """Remove a finding from disk and update the index."""
        path = self._findings_dir / f"{finding_id}.json"
        if not path.exists():
            return False
        path.unlink()

        # Update index
        idx = self._load_index()
        for tag, ids in idx.findings_by_tag.items():
            if finding_id in ids:
                ids.remove(finding_id)
        idx.stats.total_findings = len(list(self._findings_dir.glob(f"{FINDING_PREFIX}*.json")))
        self._save_index(idx)
        return True

    # ── Hypotheses CRUD ──────────────────────────────────────────────────

    def save_hypothesis(self, hypothesis: Hypothesis) -> Hypothesis:
        """Persist a hypothesis to disk."""
        path = self._hypotheses_dir / f"{hypothesis.id}.json"
        _atomic_write(path, hypothesis.model_dump_json(indent=2))
        self._index = None  # Invalidate cached index
        return hypothesis

    def get_hypothesis(self, hypothesis_id: str) -> Hypothesis | None:
        """Load a single hypothesis by ID."""
        path = self._hypotheses_dir / f"{hypothesis_id}.json"
        data = _read_json(path)
        if data is None:
            return None
        return Hypothesis.model_validate(data)

    def list_hypotheses(self, status: HypothesisStatus | None = None) -> list[Hypothesis]:
        """Load all hypotheses, optionally filtered by status."""
        hypotheses = []
        for path in sorted(self._hypotheses_dir.glob(f"{HYPOTHESIS_PREFIX}*.json")):
            data = _read_json(path)
            if data is not None:
                h = Hypothesis.model_validate(data)
                if status is None or h.status == status:
                    hypotheses.append(h)
        return hypotheses

    def resolve_hypothesis(
        self,
        hypothesis_id: str,
        status: HypothesisStatus,
    ) -> Hypothesis | None:
        """Mark a hypothesis as resolved (supported/refuted/inconclusive)."""
        h = self.get_hypothesis(hypothesis_id)
        if h is None:
            return None
        h.status = status
        h.resolved = utcnow()
        return self.save_hypothesis(h)

    def delete_hypothesis(self, hypothesis_id: str) -> bool:
        """Remove a hypothesis from disk."""
        path = self._hypotheses_dir / f"{hypothesis_id}.json"
        if not path.exists():
            return False
        path.unlink()
        self._index = None
        return True

    # ── Campaign CRUD ────────────────────────────────────────────────────

    def _campaign_dir(self, campaign_id: str) -> Path:
        return self._campaigns_dir / campaign_id

    def _campaign_path(self, campaign_id: str) -> Path:
        return self._campaign_dir(campaign_id) / "campaign.json"

    def save_campaign(self, campaign: Campaign) -> Campaign:
        """Persist a campaign to disk."""
        cdir = self._campaign_dir(campaign.id)
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "runs").mkdir(exist_ok=True)
        (cdir / "analysis").mkdir(exist_ok=True)
        (cdir / "sim_configs").mkdir(exist_ok=True)

        _atomic_write(self._campaign_path(campaign.id), campaign.model_dump_json(indent=2))
        self._index = None
        return campaign

    def get_campaign(self, campaign_id: str) -> Campaign | None:
        """Load a single campaign by ID."""
        data = _read_json(self._campaign_path(campaign_id))
        if data is None:
            return None
        return Campaign.model_validate(data)

    def list_campaigns(self, status: CampaignStatus | None = None) -> list[Campaign]:
        """Load all campaigns, optionally filtered by status."""
        campaigns = []
        if not self._campaigns_dir.exists():
            return campaigns
        for cdir in sorted(self._campaigns_dir.iterdir()):
            if not cdir.is_dir() or not cdir.name.startswith(CAMPAIGN_PREFIX):
                continue
            data = _read_json(cdir / "campaign.json")
            if data is not None:
                c = Campaign.model_validate(data)
                if status is None or c.status == status:
                    campaigns.append(c)
        return campaigns

    def delete_campaign(self, campaign_id: str) -> bool:
        """Remove a campaign directory from disk."""
        cdir = self._campaign_dir(campaign_id)
        if not cdir.exists():
            return False
        shutil.rmtree(cdir)
        self._index = None
        return True

    # ── Run Results (within campaigns) ───────────────────────────────────

    def save_run_result(self, campaign_id: str, result: RunResult) -> RunResult:
        """Persist a run result within a campaign directory."""
        runs_dir = self._campaign_dir(campaign_id) / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        path = runs_dir / f"{result.id}.json"
        _atomic_write(path, result.model_dump_json(indent=2))
        return result

    def get_run_result(self, campaign_id: str, run_id: str) -> RunResult | None:
        """Load a single run result."""
        path = self._campaign_dir(campaign_id) / "runs" / f"{run_id}.json"
        data = _read_json(path)
        if data is None:
            return None
        return RunResult.model_validate(data)

    def list_run_results(self, campaign_id: str) -> list[RunResult]:
        """Load all run results for a campaign."""
        runs_dir = self._campaign_dir(campaign_id) / "runs"
        if not runs_dir.exists():
            return []
        results = []
        for path in sorted(runs_dir.glob("*.json")):
            data = _read_json(path)
            if data is not None:
                results.append(RunResult.model_validate(data))
        return results

    # ── Aggregate Stats ──────────────────────────────────────────────────

    def stats(self) -> dict[str, Any]:
        """Return high-level statistics about the knowledge store."""
        findings = self.list_findings()
        hypotheses = self.list_hypotheses()
        campaigns = self.list_campaigns()

        breakdown: dict[str, int] = {}
        for h in hypotheses:
            breakdown[h.status.value] = breakdown.get(h.status.value, 0) + 1

        total_runs = sum(c.budget.runs_completed for c in campaigns)

        oldest = min((f.discovered for f in findings), default=None)
        newest = max((f.discovered for f in findings), default=None)

        return {
            "total_campaigns": len(campaigns),
            "total_runs": total_runs,
            "total_findings": len(findings),
            "total_hypotheses": len(hypotheses),
            "hypotheses_breakdown": breakdown,
            "knowledge_store_size_kb": self._store_size_kb(),
            "oldest_finding": oldest.isoformat() if oldest else None,
            "newest_finding": newest.isoformat() if newest else None,
        }

    def _store_size_kb(self) -> int:
        """Calculate total size of all knowledge store files in KB."""
        total = 0
        for path in self._root.rglob("*.json"):
            total += path.stat().st_size
        return total // 1024
