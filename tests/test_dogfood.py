"""Tests for dogfood session data capture infrastructure."""

from __future__ import annotations

from pathlib import Path

import pytest

from creator.dogfood.session import (
    EnvironmentSnapshot,
    SessionManager,
    estimate_cost,
)
from creator.knowledge.store import KnowledgeStore


@pytest.fixture
def store(tmp_path: Path) -> KnowledgeStore:
    return KnowledgeStore(root_dir=tmp_path / ".creator")


@pytest.fixture
def sm(store: KnowledgeStore) -> SessionManager:
    return SessionManager(store)


class TestCostEstimation:
    def test_with_input_output(self):
        cost = estimate_cost(input_tokens=1000, output_tokens=500)
        assert cost > 0
        # $3/1M input + $15/1M output
        expected = 1000 * 3.0 / 1_000_000 + 500 * 15.0 / 1_000_000
        assert cost == pytest.approx(expected)

    def test_with_total_only(self):
        cost = estimate_cost(total_tokens=10_000)
        assert cost > 0
        expected = 10_000 * 8.0 / 1_000_000
        assert cost == pytest.approx(expected)

    def test_zero_tokens(self):
        assert estimate_cost() == 0.0


class TestEnvironmentSnapshot:
    def test_capture(self):
        env = EnvironmentSnapshot.capture(model="test-model")
        assert env.python_version != ""
        assert env.platform != ""
        assert env.model == "test-model"
        assert env.timestamp is not None


class TestSessionManager:
    def test_start_session(self, sm: SessionManager):
        session = sm.start_session(name="Test Run", description="Testing data capture")
        assert session.id == "S001"
        assert session.name == "Test Run"
        assert session.environment.python_version != ""
        assert len(session.journal) >= 1  # session_started entry

    def test_session_persistence(self, sm: SessionManager):
        session = sm.start_session(name="Persist Test")
        loaded = sm.load_session(session.id)
        assert loaded is not None
        assert loaded.name == "Persist Test"
        assert loaded.id == session.id

    def test_journal_logging(self, sm: SessionManager):
        sm.start_session(name="Journal Test")
        sm.log("test_action", {"key": "value"}, campaign_id="C001")
        session = sm.get_active()
        assert session is not None
        # 1 from start_session + 1 from log
        assert len(session.journal) >= 2
        last = session.journal[-1]
        assert last.action == "test_action"
        assert last.details["key"] == "value"
        assert last.campaign_id == "C001"

    def test_cost_tracking(self, sm: SessionManager):
        sm.start_session(name="Cost Test")
        entry = sm.track_cost(
            source="engine_run",
            campaign_id="C001",
            run_id="run_001",
            total_tokens=50_000,
        )
        assert entry.estimated_usd > 0
        session = sm.get_active()
        assert session is not None
        assert session.total_cost_usd == entry.estimated_usd
        assert len(session.costs) == 1

    def test_llm_capture(self, sm: SessionManager):
        sm.start_session(name="LLM Test")
        sm.capture_llm(
            purpose="hypothesis_generation",
            model="claude-sonnet-4-6",
            system_prompt="You are a researcher...",
            user_prompt="Generate hypotheses for...",
            raw_response='[{"statement": "Auto wins"}]',
            input_tokens=500,
            output_tokens=200,
            duration_ms=1234.5,
            campaign_id="C001",
        )
        session = sm.get_active()
        assert session is not None
        assert len(session.llm_captures) == 1
        assert session.llm_captures[0].purpose == "hypothesis_generation"
        assert session.llm_captures[0].raw_response == '[{"statement": "Auto wins"}]'

    def test_register_campaign(self, sm: SessionManager):
        sm.start_session(name="Campaign Reg Test")
        sm.register_campaign("C001")
        sm.register_campaign("C002")
        sm.register_campaign("C001")  # Duplicate — should not add twice
        session = sm.get_active()
        assert session is not None
        assert session.campaign_ids == ["C001", "C002"]

    def test_archive_chronicle(self, sm: SessionManager, store: KnowledgeStore):
        sm.start_session(name="Chronicle Test")
        path = sm.archive_chronicle("C001", "run_001", "=== Chronicle Report ===\nAgent Atlas did stuff.")
        assert path is not None
        assert path.exists()
        assert "Chronicle Report" in path.read_text()

    def test_complete_session(self, sm: SessionManager):
        sm.start_session(name="Complete Test")
        sm.register_campaign("C001")
        sm.track_cost(source="engine_run", total_tokens=10_000)
        session = sm.complete_session(notes="All good")
        assert session is not None
        assert session.completed is not None
        assert session.notes == "All good"

    def test_list_sessions(self, sm: SessionManager):
        sm.start_session(name="Session 1")
        sm.complete_session()
        sm.start_session(name="Session 2")
        sessions = sm.list_sessions()
        assert len(sessions) == 2
        assert sessions[0].name == "Session 1"
        assert sessions[1].name == "Session 2"

    def test_sequential_ids(self, sm: SessionManager):
        s1 = sm.start_session(name="First")
        sm.complete_session()
        s2 = sm.start_session(name="Second")
        assert s1.id == "S001"
        assert s2.id == "S002"


class TestDatasetExport:
    def test_export_empty_session(self, sm: SessionManager):
        sm.start_session(name="Empty Export")
        dataset = sm.export_dataset()
        assert dataset["session"]["name"] == "Empty Export"
        assert dataset["statistics"]["total_campaigns"] == 0

    def test_export_with_campaigns(self, sm: SessionManager, store: KnowledgeStore):
        sm.start_session(name="Full Export")

        # Create a minimal campaign
        from creator.knowledge.models import Campaign, CampaignConstraints, CampaignBudget, RunConfig, RunResult
        c = Campaign(
            id="C001",
            question="Test question",
            constraints=CampaignConstraints(task="Test task"),
            budget=CampaignBudget(runs_completed=2),
        )
        store.save_campaign(c)
        sm.register_campaign("C001")

        # Add run results
        for i in range(2):
            store.save_run_result("C001", RunResult(
                id=f"run_{i:03d}",
                config=RunConfig(preset="auto"),
                agent_count=4,
                model="test",
                max_ticks=50,
                quality_score=0.85 + i * 0.02,
                total_tokens=10_000,
                wall_time_seconds=30.0,
                success=True,
            ))

        # Track some cost
        sm.track_cost(source="engine_run", campaign_id="C001", total_tokens=20_000)

        dataset = sm.export_dataset()
        assert dataset["statistics"]["total_campaigns"] == 1
        assert dataset["statistics"]["total_runs"] == 2
        assert dataset["statistics"]["successful_runs"] == 2
        assert dataset["statistics"]["total_tokens"] == 20_000
        assert len(dataset["campaigns"]) == 1
        assert dataset["campaigns"][0]["run_count"] == 2
        assert dataset["cost_summary"]["total_usd"] > 0

    def test_export_to_file(self, sm: SessionManager, store: KnowledgeStore):
        sm.start_session(name="File Export")
        path = sm.export_to_file()
        assert path.exists()
        assert path.name == "dataset_export.json"

        import json
        data = json.loads(path.read_text())
        assert data["session"]["name"] == "File Export"
