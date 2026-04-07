"""Creator Mode configuration — paths, defaults, constants."""

from __future__ import annotations

from pathlib import Path

# ── Disk layout ──────────────────────────────────────────────────────────────
CREATOR_HOME = Path.home() / ".agentciv-creator"
KNOWLEDGE_DIR = CREATOR_HOME / "knowledge"
FINDINGS_DIR = KNOWLEDGE_DIR / "findings"
HYPOTHESES_DIR = KNOWLEDGE_DIR / "hypotheses"
CAMPAIGNS_DIR = CREATOR_HOME / "campaigns"
INDEX_PATH = KNOWLEDGE_DIR / "index.json"
CONFIG_PATH = CREATOR_HOME / "config.json"

# ── ID prefixes ──────────────────────────────────────────────────────────────
CAMPAIGN_PREFIX = "C"
FINDING_PREFIX = "F"
HYPOTHESIS_PREFIX = "H"
BATCH_PREFIX = "B"
RUN_PREFIX = "run"

# ── Defaults ─────────────────────────────────────────────────────────────────
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_AGENT_COUNT = 4
DEFAULT_MAX_TICKS = 50
DEFAULT_RUNS_PER_CONFIG = 3
DEFAULT_MAX_RUNS = 21
DEFAULT_STRATEGY = "hypothesis"
DEFAULT_ARM = "directed"
DEFAULT_MUTATION_RATE = 0.3

# ── Simulation defaults ─────────────────────────────────────────────────────
DEFAULT_SIM_DIR = Path.home() / "agent-civilisation"
DEFAULT_SIM_AGENTS = 12
DEFAULT_SIM_TICKS = 100

# ── Engine presets (all 13) ──────────────────────────────────────────────────
ALL_PRESETS = [
    "collaborative",
    "competitive",
    "hierarchical",
    "meritocratic",
    "auto",
    "startup",
    "pair-programming",
    "open-source",
    "military",
    "research-lab",
    "swarm",
    "hackathon",
    "code-review",
]

# ── Organisational dimensions ────────────────────────────────────────────────
DIMENSION_VALUES: dict[str, list[str]] = {
    "authority": ["hierarchy", "flat", "distributed", "rotating", "consensus", "anarchic"],
    "communication": ["hub-spoke", "mesh", "clustered", "broadcast", "whisper"],
    "roles": ["assigned", "emergent", "rotating", "fixed", "fluid"],
    "decisions": ["top-down", "consensus", "majority", "meritocratic", "autonomous"],
    "incentives": ["collaborative", "competitive", "reputation", "market"],
    "information": ["transparent", "need-to-know", "curated", "filtered"],
    "conflict": ["authority", "negotiated", "voted", "adjudicated"],
    "groups": ["imposed", "self-selected", "task-based", "persistent", "temporary"],
    "adaptation": ["static", "evolving", "cyclical", "real-time"],
}

ALL_DIMENSIONS = list(DIMENSION_VALUES.keys())

# ── Emergence metrics ────────────────────────────────────────────────────────
EMERGENCE_DIMENSIONS = [
    "governance",
    "cooperation",
    "innovation",
    "social_structure",
    "specialisation",
    "wellbeing",
]

# ── Confidence thresholds ────────────────────────────────────────────────────
MIN_RUNS_FOR_CONFIDENCE = 3
HIGH_CONFIDENCE_THRESHOLD = 0.80
MODERATE_CONFIDENCE_THRESHOLD = 0.60

# ── Version ──────────────────────────────────────────────────────────────────
KNOWLEDGE_STORE_VERSION = 1


def ensure_directories() -> None:
    """Create the Creator Mode directory structure if it doesn't exist."""
    for d in (CREATOR_HOME, KNOWLEDGE_DIR, FINDINGS_DIR, HYPOTHESES_DIR, CAMPAIGNS_DIR):
        d.mkdir(parents=True, exist_ok=True)
