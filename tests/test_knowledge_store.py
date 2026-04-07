"""Tests for the Knowledge Store — CRUD, search, coverage, and index.

Uses a temporary directory via KnowledgeStore(root_dir=...) to avoid
polluting ~/.agentciv-creator/.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from creator.knowledge.models import (
    Campaign,
    CampaignBudget,
    CampaignConstraints,
    CampaignStatus,
    CampaignType,
    EvidenceItem,
    Finding,
    FindingConditions,
    FindingType,
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    RunConfig,
    RunResult,
    StatisticalTest,
    TestDesign,
)
from creator.knowledge.store import KnowledgeStore
from creator.knowledge.index import SearchIndex


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def store(tmp_path: Path) -> KnowledgeStore:
    return KnowledgeStore(root_dir=tmp_path / ".agentciv-creator")


@pytest.fixture
def search(store: KnowledgeStore) -> SearchIndex:
    return SearchIndex(store)


def _make_finding(
    id: str = "F001",
    statement: str = "Distributed authority outperforms hierarchical for code review",
    confidence: float = 0.88,
    tags: list[str] | None = None,
    source_campaign: str = "C001",
) -> Finding:
    return Finding(
        id=id,
        statement=statement,
        confidence=confidence,
        type=FindingType.COMPARATIVE,
        evidence=[
            EvidenceItem(
                campaign="C001",
                run="run_001",
                config=RunConfig(preset="code-review", overrides={"authority": "distributed"}),
                metric="quality_score",
                value=0.91,
            ),
        ],
        conditions=FindingConditions(
            task_types=["code_review"],
            agent_count_range=[8, None],
            presets=["code-review"],
        ),
        statistics=StatisticalTest(
            comparison="distributed vs hierarchical",
            metric="quality_score",
            effect_size=0.73,
            p_value=0.003,
            significant=True,
            n_runs=6,
        ),
        source_campaign=source_campaign,
        tags=tags or ["authority", "code_review", "scaling"],
    )


def _make_hypothesis(
    id: str = "H001",
    statement: str = "Hierarchical bottlenecks at 8 agents",
    status: HypothesisStatus = HypothesisStatus.UNTESTED,
    priority: HypothesisPriority = HypothesisPriority.HIGH,
    tags: list[str] | None = None,
) -> Hypothesis:
    return Hypothesis(
        id=id,
        statement=statement,
        status=status,
        test_design=TestDesign(
            independent_variable="authority",
            treatment="hierarchy",
            control="distributed",
            outcome_metric="quality_score",
            expected_direction="control > treatment",
            agent_count=8,
        ),
        priority=priority,
        tags=tags or ["authority", "scaling"],
    )


# ── Store: Findings ──────────────────────────────────────────────────────────

class TestFindingsCRUD:
    def test_save_and_get(self, store: KnowledgeStore):
        f = _make_finding()
        store.save_finding(f)
        loaded = store.get_finding("F001")
        assert loaded is not None
        assert loaded.id == "F001"
        assert loaded.statement == f.statement
        assert loaded.confidence == 0.88

    def test_list_findings(self, store: KnowledgeStore):
        store.save_finding(_make_finding("F001"))
        store.save_finding(_make_finding("F002", statement="Second finding", tags=["scaling"]))
        findings = store.list_findings()
        assert len(findings) == 2
        assert findings[0].id == "F001"
        assert findings[1].id == "F002"

    def test_delete_finding(self, store: KnowledgeStore):
        store.save_finding(_make_finding("F001"))
        assert store.delete_finding("F001") is True
        assert store.get_finding("F001") is None
        assert store.delete_finding("F001") is False

    def test_get_nonexistent(self, store: KnowledgeStore):
        assert store.get_finding("F999") is None

    def test_index_updated_on_save(self, store: KnowledgeStore):
        store.save_finding(_make_finding("F001", tags=["authority", "scaling"]))
        idx = store.index
        assert "authority" in idx.findings_by_tag
        assert "F001" in idx.findings_by_tag["authority"]

    def test_next_finding_id(self, store: KnowledgeStore):
        assert store.next_finding_id() == "F001"
        store.save_finding(_make_finding("F001"))
        assert store.next_finding_id() == "F002"
        store.save_finding(_make_finding("F002"))
        assert store.next_finding_id() == "F003"


# ── Store: Hypotheses ────────────────────────────────────────────────────────

class TestHypothesesCRUD:
    def test_save_and_get(self, store: KnowledgeStore):
        h = _make_hypothesis()
        store.save_hypothesis(h)
        loaded = store.get_hypothesis("H001")
        assert loaded is not None
        assert loaded.statement == h.statement
        assert loaded.status == HypothesisStatus.UNTESTED

    def test_resolve_hypothesis(self, store: KnowledgeStore):
        store.save_hypothesis(_make_hypothesis("H001"))
        resolved = store.resolve_hypothesis("H001", HypothesisStatus.SUPPORTED)
        assert resolved is not None
        assert resolved.status == HypothesisStatus.SUPPORTED
        assert resolved.resolved is not None

    def test_list_by_status(self, store: KnowledgeStore):
        store.save_hypothesis(_make_hypothesis("H001", status=HypothesisStatus.UNTESTED))
        store.save_hypothesis(_make_hypothesis("H002", status=HypothesisStatus.SUPPORTED))
        store.save_hypothesis(_make_hypothesis("H003", status=HypothesisStatus.UNTESTED))

        untested = store.list_hypotheses(status=HypothesisStatus.UNTESTED)
        assert len(untested) == 2

        supported = store.list_hypotheses(status=HypothesisStatus.SUPPORTED)
        assert len(supported) == 1

        all_h = store.list_hypotheses()
        assert len(all_h) == 3

    def test_delete_hypothesis(self, store: KnowledgeStore):
        store.save_hypothesis(_make_hypothesis("H001"))
        assert store.delete_hypothesis("H001") is True
        assert store.get_hypothesis("H001") is None

    def test_next_hypothesis_id(self, store: KnowledgeStore):
        assert store.next_hypothesis_id() == "H001"
        store.save_hypothesis(_make_hypothesis("H001"))
        assert store.next_hypothesis_id() == "H002"


# ── Store: Campaigns ─────────────────────────────────────────────────────────

class TestCampaignsCRUD:
    def test_save_and_get(self, store: KnowledgeStore):
        c = Campaign(
            id="C001",
            question="Best org for code review?",
            type=CampaignType.EXPLORE,
            constraints=CampaignConstraints(agents=8, task="Build REST API"),
            budget=CampaignBudget(max_runs=21, runs_per_config=3),
        )
        store.save_campaign(c)
        loaded = store.get_campaign("C001")
        assert loaded is not None
        assert loaded.question == "Best org for code review?"

    def test_list_campaigns(self, store: KnowledgeStore):
        store.save_campaign(Campaign(id="C001", question="Q1"))
        store.save_campaign(Campaign(id="C002", question="Q2", status=CampaignStatus.COMPLETE))

        all_c = store.list_campaigns()
        assert len(all_c) == 2

        complete = store.list_campaigns(status=CampaignStatus.COMPLETE)
        assert len(complete) == 1
        assert complete[0].id == "C002"

    def test_delete_campaign(self, store: KnowledgeStore):
        store.save_campaign(Campaign(id="C001", question="Q1"))
        assert store.delete_campaign("C001") is True
        assert store.get_campaign("C001") is None

    def test_campaign_creates_subdirectories(self, store: KnowledgeStore):
        store.save_campaign(Campaign(id="C001", question="Q1"))
        cdir = store._campaigns_dir / "C001"
        assert (cdir / "runs").is_dir()
        assert (cdir / "analysis").is_dir()
        assert (cdir / "sim_configs").is_dir()

    def test_next_campaign_id(self, store: KnowledgeStore):
        assert store.next_campaign_id() == "C001"
        store.save_campaign(Campaign(id="C001", question="Q1"))
        assert store.next_campaign_id() == "C002"


# ── Store: Run Results ───────────────────────────────────────────────────────

class TestRunResults:
    def test_save_and_get(self, store: KnowledgeStore):
        store.save_campaign(Campaign(id="C001", question="Q1"))

        result = RunResult(
            id="run_001",
            campaign_id="C001",
            batch_id="B001",
            config=RunConfig(preset="collaborative"),
            agent_count=4,
            model="claude-sonnet-4-6",
            max_ticks=50,
            quality_score=0.85,
            merge_conflicts=3,
        )
        store.save_run_result("C001", result)

        loaded = store.get_run_result("C001", "run_001")
        assert loaded is not None
        assert loaded.quality_score == 0.85

    def test_list_run_results(self, store: KnowledgeStore):
        store.save_campaign(Campaign(id="C001", question="Q1"))
        for i in range(3):
            store.save_run_result("C001", RunResult(
                id=f"run_{i:03d}",
                campaign_id="C001",
                config=RunConfig(preset="collaborative"),
                agent_count=4,
                model="claude-sonnet-4-6",
                max_ticks=50,
                quality_score=0.7 + i * 0.05,
            ))
        results = store.list_run_results("C001")
        assert len(results) == 3


# ── Store: Stats ─────────────────────────────────────────────────────────────

class TestStats:
    def test_empty_stats(self, store: KnowledgeStore):
        stats = store.stats()
        assert stats["total_findings"] == 0
        assert stats["total_hypotheses"] == 0
        assert stats["total_campaigns"] == 0
        assert stats["total_runs"] == 0

    def test_populated_stats(self, store: KnowledgeStore):
        store.save_finding(_make_finding("F001"))
        store.save_finding(_make_finding("F002"))
        store.save_hypothesis(_make_hypothesis("H001"))
        c = Campaign(id="C001", question="Q1", budget=CampaignBudget(runs_completed=12))
        store.save_campaign(c)

        stats = store.stats()
        assert stats["total_findings"] == 2
        assert stats["total_hypotheses"] == 1
        assert stats["total_campaigns"] == 1
        assert stats["total_runs"] == 12


# ── Search Index ─────────────────────────────────────────────────────────────

class TestSearchIndex:
    def test_query_by_keyword(self, store: KnowledgeStore, search: SearchIndex):
        store.save_finding(_make_finding("F001", statement="Distributed authority wins for code review"))
        store.save_finding(_make_finding("F002", statement="Meritocratic teams are creative", tags=["creativity"]))

        results = search.query_findings("authority code review")
        assert len(results) >= 1
        assert results[0].finding.id == "F001"

    def test_query_by_tag(self, store: KnowledgeStore, search: SearchIndex):
        store.save_finding(_make_finding("F001", tags=["authority", "scaling"]))
        store.save_finding(_make_finding("F002", tags=["creativity"]))

        results = search.query_findings("something about scaling", tags=["scaling"])
        assert len(results) == 1
        assert results[0].finding.id == "F001"

    def test_confidence_filter(self, store: KnowledgeStore, search: SearchIndex):
        store.save_finding(_make_finding("F001", confidence=0.9))
        store.save_finding(_make_finding("F002", confidence=0.3, statement="Low confidence authority result"))

        results = search.query_findings("authority", min_confidence=0.5)
        assert all(r.finding.confidence >= 0.5 for r in results)

    def test_related_hypotheses(self, store: KnowledgeStore, search: SearchIndex):
        store.save_hypothesis(_make_hypothesis("H001", statement="Hierarchical bottlenecks at 8 agents"))
        store.save_hypothesis(_make_hypothesis("H002", statement="Creative tasks need flat structures"))

        related = search.find_related_hypotheses("hierarchical authority scaling")
        assert len(related) >= 1
        assert related[0].id == "H001"

    def test_empty_query(self, store: KnowledgeStore, search: SearchIndex):
        results = search.query_findings("")
        assert results == []

    def test_no_matches(self, store: KnowledgeStore, search: SearchIndex):
        store.save_finding(_make_finding("F001"))
        results = search.query_findings("quantum physics entanglement")
        assert results == []


# ── Coverage ─────────────────────────────────────────────────────────────────

class TestCoverage:
    def test_empty_coverage(self, store: KnowledgeStore, search: SearchIndex):
        coverage = search.compute_coverage()
        assert coverage.directed.presets_tested == []
        assert len(coverage.directed.presets_untested) == 13

    def test_coverage_from_findings(self, store: KnowledgeStore, search: SearchIndex):
        store.save_finding(_make_finding("F001"))
        coverage = search.compute_coverage()
        assert "code-review" in coverage.directed.presets_tested
        assert "code-review" not in coverage.directed.presets_untested

    def test_gaps_identified(self, store: KnowledgeStore, search: SearchIndex):
        gaps = search.identify_gaps()
        areas = [g.area for g in gaps]
        assert "presets" in areas
        assert "scale" in areas

    def test_suggestions(self, store: KnowledgeStore, search: SearchIndex):
        store.save_hypothesis(_make_hypothesis("H001", status=HypothesisStatus.UNTESTED))
        suggestions = search.suggest_next()
        assert len(suggestions) >= 1
        assert "untested" in suggestions[0].lower()


# ── Index Rebuild ────────────────────────────────────────────────────────────

class TestIndexRebuild:
    def test_rebuild_from_disk(self, store: KnowledgeStore):
        store.save_finding(_make_finding("F001", tags=["authority"]))
        store.save_finding(_make_finding("F002", tags=["scaling"]))
        store.save_hypothesis(_make_hypothesis("H001"))

        # Clear cached index
        store._index = None

        idx = store.rebuild_index()
        assert idx.stats.total_findings == 2
        assert idx.stats.total_hypotheses == 1
        assert "authority" in idx.findings_by_tag


# ── Model Validation ─────────────────────────────────────────────────────────

class TestModels:
    def test_finding_confidence_bounds(self):
        with pytest.raises(Exception):
            Finding(id="F001", statement="test", confidence=1.5)
        with pytest.raises(Exception):
            Finding(id="F001", statement="test", confidence=-0.1)

    def test_finding_serialisation_roundtrip(self):
        f = _make_finding()
        data = json.loads(f.model_dump_json())
        f2 = Finding.model_validate(data)
        assert f2.id == f.id
        assert f2.confidence == f.confidence
        assert len(f2.evidence) == len(f.evidence)

    def test_campaign_serialisation_roundtrip(self):
        c = Campaign(
            id="C001",
            question="Test question",
            status=CampaignStatus.RUNNING,
            constraints=CampaignConstraints(agents=8, task="Build API"),
        )
        data = json.loads(c.model_dump_json())
        c2 = Campaign.model_validate(data)
        assert c2.id == c.id
        assert c2.status == CampaignStatus.RUNNING
        assert c2.constraints.agents == 8

    def test_run_result_serialisation(self):
        r = RunResult(
            id="run_001",
            config=RunConfig(preset="auto", overrides={"authority": "rotating"}),
            agent_count=4,
            model="claude-sonnet-4-6",
            max_ticks=50,
            quality_score=0.91,
            restructure_log=[{"tick": 8, "dimension": "authority", "new": "rotating"}],
            final_org_state={"authority": "rotating", "communication": "mesh"},
        )
        data = json.loads(r.model_dump_json())
        r2 = RunResult.model_validate(data)
        assert r2.quality_score == 0.91
        assert r2.final_org_state["authority"] == "rotating"
