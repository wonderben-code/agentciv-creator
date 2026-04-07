"""Dogfood session — captures all data from a real Creator Mode test run.

A DogfoodSession wraps multiple campaigns into a single research session with:
  - Environment snapshot (Python, engine, model, OS)
  - Cost tracking (tokens → dollars per run, per campaign, total)
  - Session journal (timestamped log of every action)
  - Raw LLM responses (hypothesis engine, analysis prompts)
  - Exportable dataset for paper tables and figures
"""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from ..knowledge.models import utcnow
from ..knowledge.store import KnowledgeStore, _atomic_write, _read_json


# ── Cost model ───────────────────────────────────────────────────────────────

# Approximate per-token costs (USD) as of April 2026
# Claude Sonnet 4.6 pricing
COST_PER_INPUT_TOKEN = 3.0 / 1_000_000   # $3.00 per 1M input tokens
COST_PER_OUTPUT_TOKEN = 15.0 / 1_000_000  # $15.00 per 1M output tokens

# Fallback: if we only have total tokens (no input/output split)
COST_PER_TOKEN_BLENDED = 8.0 / 1_000_000  # ~$8 per 1M (weighted average)


def estimate_cost(
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
) -> float:
    """Estimate USD cost from token counts."""
    if input_tokens > 0 or output_tokens > 0:
        return (input_tokens * COST_PER_INPUT_TOKEN
                + output_tokens * COST_PER_OUTPUT_TOKEN)
    return total_tokens * COST_PER_TOKEN_BLENDED


# ── Models ───────────────────────────────────────────────────────────────────

class EnvironmentSnapshot(BaseModel):
    """Frozen snapshot of the execution environment."""
    python_version: str = ""
    platform: str = ""
    os_version: str = ""
    creator_version: str = "0.1.0"
    engine_version: str = ""
    engine_installed: bool = False
    model: str = ""
    anthropic_sdk_version: str = ""
    timestamp: datetime = Field(default_factory=utcnow)

    @classmethod
    def capture(cls, model: str = "") -> EnvironmentSnapshot:
        """Capture the current environment."""
        env = cls(
            python_version=sys.version,
            platform=platform.platform(),
            os_version=platform.version(),
            model=model,
        )
        try:
            import anthropic
            env.anthropic_sdk_version = getattr(anthropic, "__version__", "unknown")
        except ImportError:
            env.anthropic_sdk_version = "not installed"
        try:
            import agentciv
            env.engine_version = getattr(agentciv, "__version__", "unknown")
            env.engine_installed = True
        except ImportError:
            env.engine_version = "not installed"
            env.engine_installed = False
        return env


class JournalEntry(BaseModel):
    """A timestamped log entry in the session journal."""
    timestamp: datetime = Field(default_factory=utcnow)
    action: str
    details: dict[str, Any] = Field(default_factory=dict)
    campaign_id: str = ""


class CostEntry(BaseModel):
    """Cost tracking for a single API call or run."""
    timestamp: datetime = Field(default_factory=utcnow)
    campaign_id: str = ""
    run_id: str = ""
    source: str = ""  # "engine_run", "hypothesis_engine", "analysis"
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_usd: float = 0.0


class LLMCapture(BaseModel):
    """Raw LLM request/response capture."""
    timestamp: datetime = Field(default_factory=utcnow)
    campaign_id: str = ""
    purpose: str = ""  # "hypothesis_generation", "analysis", etc.
    model: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    raw_response: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: float = 0.0


class DogfoodSession(BaseModel):
    """A complete dogfooding test session.

    Groups multiple campaigns into a single research session with
    full provenance for paper updates.
    """
    id: str
    name: str = ""
    description: str = ""
    started: datetime = Field(default_factory=utcnow)
    completed: datetime | None = None
    environment: EnvironmentSnapshot = Field(default_factory=EnvironmentSnapshot)
    campaign_ids: list[str] = Field(default_factory=list)
    journal: list[JournalEntry] = Field(default_factory=list)
    costs: list[CostEntry] = Field(default_factory=list)
    llm_captures: list[LLMCapture] = Field(default_factory=list)
    total_cost_usd: float = 0.0
    notes: str = ""


# ── Session Manager ──────────────────────────────────────────────────────────

class SessionManager:
    """Manages dogfood sessions on disk.

    Sessions live at ~/.agentciv-creator/sessions/{session_id}/
    """

    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store
        self._sessions_dir = store._root / "sessions"
        self._sessions_dir.mkdir(parents=True, exist_ok=True)
        self._active: DogfoodSession | None = None

    def _session_dir(self, session_id: str) -> Path:
        return self._sessions_dir / session_id

    def _session_path(self, session_id: str) -> Path:
        return self._session_dir(session_id) / "session.json"

    def start_session(
        self,
        name: str,
        description: str = "",
        model: str = "claude-sonnet-4-6",
    ) -> DogfoodSession:
        """Start a new dogfood session."""
        # Generate session ID
        existing = sorted(
            d.name for d in self._sessions_dir.iterdir()
            if d.is_dir() and d.name.startswith("S")
        ) if self._sessions_dir.exists() else []
        if existing:
            last_num = int(existing[-1][1:])
            session_id = f"S{last_num + 1:03d}"
        else:
            session_id = "S001"

        session = DogfoodSession(
            id=session_id,
            name=name,
            description=description,
            environment=EnvironmentSnapshot.capture(model=model),
        )

        sdir = self._session_dir(session_id)
        sdir.mkdir(parents=True, exist_ok=True)
        (sdir / "llm_captures").mkdir(exist_ok=True)
        (sdir / "chronicles").mkdir(exist_ok=True)

        self._save_session(session)
        self._active = session

        self.log("session_started", {
            "name": name,
            "description": description,
            "environment": session.environment.model_dump(),
        })

        return session

    def get_active(self) -> DogfoodSession | None:
        return self._active

    def load_session(self, session_id: str) -> DogfoodSession | None:
        data = _read_json(self._session_path(session_id))
        if data is None:
            return None
        session = DogfoodSession.model_validate(data)
        self._active = session
        return session

    def list_sessions(self) -> list[DogfoodSession]:
        sessions = []
        if not self._sessions_dir.exists():
            return sessions
        for sdir in sorted(self._sessions_dir.iterdir()):
            if sdir.is_dir() and sdir.name.startswith("S"):
                data = _read_json(sdir / "session.json")
                if data is not None:
                    sessions.append(DogfoodSession.model_validate(data))
        return sessions

    def _save_session(self, session: DogfoodSession | None = None) -> None:
        s = session or self._active
        if s is None:
            return
        _atomic_write(self._session_path(s.id), s.model_dump_json(indent=2))

    # ── Journal ────────────────────────────────────────────────────────

    def log(
        self,
        action: str,
        details: dict[str, Any] | None = None,
        campaign_id: str = "",
    ) -> None:
        """Add a journal entry to the active session."""
        if self._active is None:
            return
        entry = JournalEntry(
            action=action,
            details=details or {},
            campaign_id=campaign_id,
        )
        self._active.journal.append(entry)
        self._save_session()

    # ── Cost Tracking ──────────────────────────────────────────────────

    def track_cost(
        self,
        source: str,
        campaign_id: str = "",
        run_id: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
    ) -> CostEntry:
        """Record a cost entry and update totals."""
        usd = estimate_cost(input_tokens, output_tokens, total_tokens)
        entry = CostEntry(
            campaign_id=campaign_id,
            run_id=run_id,
            source=source,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_usd=usd,
        )
        if self._active is not None:
            self._active.costs.append(entry)
            self._active.total_cost_usd += usd
            self._save_session()
        return entry

    # ── LLM Capture ────────────────────────────────────────────────────

    def capture_llm(
        self,
        purpose: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        raw_response: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        duration_ms: float = 0.0,
        campaign_id: str = "",
    ) -> None:
        """Capture a raw LLM request/response pair."""
        capture = LLMCapture(
            campaign_id=campaign_id,
            purpose=purpose,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            raw_response=raw_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
        )
        if self._active is not None:
            self._active.llm_captures.append(capture)
            # Also save individually for large responses
            cap_dir = self._session_dir(self._active.id) / "llm_captures"
            cap_dir.mkdir(exist_ok=True)
            idx = len(self._active.llm_captures)
            _atomic_write(
                cap_dir / f"capture_{idx:03d}.json",
                capture.model_dump_json(indent=2),
            )
            self._save_session()

    # ── Campaign Registration ──────────────────────────────────────────

    def register_campaign(self, campaign_id: str) -> None:
        """Register a campaign as part of this session."""
        if self._active is not None and campaign_id not in self._active.campaign_ids:
            self._active.campaign_ids.append(campaign_id)
            self.log("campaign_registered", {"campaign_id": campaign_id}, campaign_id)

    # ── Chronicle Archival ─────────────────────────────────────────────

    def archive_chronicle(
        self,
        campaign_id: str,
        run_id: str,
        chronicle_text: str,
    ) -> Path | None:
        """Archive a full chronicle report for a run."""
        if self._active is None:
            return None
        chron_dir = self._session_dir(self._active.id) / "chronicles"
        chron_dir.mkdir(exist_ok=True)
        path = chron_dir / f"{campaign_id}_{run_id}_chronicle.txt"
        _atomic_write(path, chronicle_text)
        return path

    # ── Complete Session ───────────────────────────────────────────────

    def complete_session(self, notes: str = "") -> DogfoodSession | None:
        """Mark the session as complete."""
        if self._active is None:
            return None
        self._active.completed = utcnow()
        self._active.notes = notes
        self.log("session_completed", {
            "total_campaigns": len(self._active.campaign_ids),
            "total_cost_usd": self._active.total_cost_usd,
            "total_journal_entries": len(self._active.journal),
            "total_llm_captures": len(self._active.llm_captures),
        })
        self._save_session()
        return self._active

    # ── Export ─────────────────────────────────────────────────────────

    def export_dataset(self, session_id: str | None = None) -> dict[str, Any]:
        """Export a complete dataset for paper tables and figures.

        Returns a dict with:
          - session: session metadata
          - environment: frozen env snapshot
          - campaigns: list of campaign dicts with all runs, findings, hypotheses
          - cost_summary: per-campaign and total costs
          - journal: full timestamped journal
          - llm_interactions: all captured LLM exchanges
          - statistics: cross-campaign aggregate statistics
        """
        sid = session_id or (self._active.id if self._active else None)
        if sid is None:
            return {"error": "No session specified or active"}

        session = self.load_session(sid)
        if session is None:
            return {"error": f"Session {sid} not found"}

        store = self._store

        # Gather all campaign data
        campaigns_data = []
        all_runs = []
        all_findings = []
        all_hypotheses = []

        for cid in session.campaign_ids:
            campaign = store.get_campaign(cid)
            if campaign is None:
                continue

            runs = store.list_run_results(cid)
            all_runs.extend(runs)

            # Load related findings
            c_findings = []
            for fid in campaign.findings_generated:
                f = store.get_finding(fid)
                if f:
                    c_findings.append(f)
                    all_findings.append(f)

            # Load related hypotheses
            c_hypotheses = []
            for hid in campaign.hypotheses_generated:
                h = store.get_hypothesis(hid)
                if h:
                    c_hypotheses.append(h)
                    all_hypotheses.append(h)

            campaigns_data.append({
                "campaign": campaign.model_dump(mode="json"),
                "runs": [r.model_dump(mode="json") for r in runs],
                "findings": [f.model_dump(mode="json") for f in c_findings],
                "hypotheses": [h.model_dump(mode="json") for h in c_hypotheses],
                "run_count": len(runs),
                "success_count": sum(1 for r in runs if r.success),
                "fail_count": sum(1 for r in runs if not r.success),
            })

        # Cost summary
        cost_by_campaign: dict[str, float] = {}
        cost_by_source: dict[str, float] = {}
        for c in session.costs:
            cost_by_campaign[c.campaign_id] = cost_by_campaign.get(c.campaign_id, 0) + c.estimated_usd
            cost_by_source[c.source] = cost_by_source.get(c.source, 0) + c.estimated_usd

        # Cross-campaign statistics
        successful_runs = [r for r in all_runs if r.success]
        stats = {
            "total_campaigns": len(session.campaign_ids),
            "total_runs": len(all_runs),
            "successful_runs": len(successful_runs),
            "failed_runs": len(all_runs) - len(successful_runs),
            "total_findings": len(all_findings),
            "total_hypotheses": len(all_hypotheses),
            "hypotheses_supported": sum(1 for h in all_hypotheses if h.status.value == "supported"),
            "hypotheses_refuted": sum(1 for h in all_hypotheses if h.status.value == "refuted"),
            "hypotheses_inconclusive": sum(1 for h in all_hypotheses if h.status.value == "inconclusive"),
            "total_tokens": sum(r.total_tokens for r in successful_runs),
            "total_wall_time_seconds": sum(r.wall_time_seconds for r in successful_runs),
            "total_cost_usd": session.total_cost_usd,
            "presets_tested": sorted(set(r.config.preset for r in all_runs)),
            "models_used": sorted(set(r.model for r in all_runs)),
        }

        if successful_runs:
            qualities = [r.quality_score for r in successful_runs]
            stats["quality_mean"] = sum(qualities) / len(qualities)
            stats["quality_min"] = min(qualities)
            stats["quality_max"] = max(qualities)

        return {
            "session": {
                "id": session.id,
                "name": session.name,
                "description": session.description,
                "started": session.started.isoformat(),
                "completed": session.completed.isoformat() if session.completed else None,
                "total_cost_usd": session.total_cost_usd,
            },
            "environment": session.environment.model_dump(mode="json"),
            "campaigns": campaigns_data,
            "cost_summary": {
                "total_usd": session.total_cost_usd,
                "by_campaign": cost_by_campaign,
                "by_source": cost_by_source,
                "entries": [c.model_dump(mode="json") for c in session.costs],
            },
            "journal": [j.model_dump(mode="json") for j in session.journal],
            "llm_interactions": [cap.model_dump(mode="json") for cap in session.llm_captures],
            "statistics": stats,
        }

    def export_to_file(self, session_id: str | None = None) -> Path:
        """Export dataset to a JSON file in the session directory."""
        sid = session_id or (self._active.id if self._active else None)
        if sid is None:
            raise ValueError("No session specified or active")

        dataset = self.export_dataset(sid)
        export_path = self._session_dir(sid) / "dataset_export.json"
        _atomic_write(export_path, json.dumps(dataset, indent=2, default=str))

        self.log("dataset_exported", {"path": str(export_path)})
        return export_path
