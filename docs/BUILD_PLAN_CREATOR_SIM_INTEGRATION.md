# Build Plan: Creator Mode Dual-Mode + Simulation Dev Tool Upgrade

**Created:** 7 April 2026
**Goal:** Make Creator Mode direct both the Engine AND the Simulation. Upgrade the Simulation from a research script to a polished developer tool on par with the Engine. Ship the Creator Mode website wing with the complete story.

---

## The Three Products After This Build

### 1. The Simulation (`agentciv-sim`)
**What it is:** AI agents with Maslow drives forming societies. Emergence, governance, innovation, relationships — civilisation dynamics.
**Current state:** Research script. Clean Python API internally but no packaging, no CLI, no presets, no structured metrics.
**Target state:** Polished developer tool. `pip install agentciv-sim`. CLI with commands. Config presets. Structured emergence metrics. MCP integration.

### 2. The Engine (`agentciv-engine`) — already polished
**What it is:** AI teams solving real tasks under configurable org structures. 13 presets, 9 dimensions, quality scoring.
**Current state:** On PyPI, CLI with 6 commands, MCP server, learning system. Production-ready.
**Target state:** No changes needed. Already the benchmark.

### 3. Creator Mode (`agentciv-creator`)
**What it is:** The meta-layer. An AI that autonomously designs experiments, runs them through EITHER tool, analyses results, and learns.
**Current state:** MCP server with 9 tools. Directs the Engine only. Dogfood validated.
**Target state:** Directs both Engine and Simulation. Dual-mode campaigns. The complete autonomous organisational architect.

---

## Architecture After Build

```
                     Creator Mode
                    (the architect)
                    ┌─────────────┐
                    │  MCP Server  │
                    │  9+1 tools   │
                    │  Knowledge   │
                    │  Store       │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
     ┌────────────────┐       ┌────────────────┐
     │    Engine       │       │   Simulation    │
     │  (task teams)   │       │ (AI societies)  │
     │                 │       │                 │
     │ 13 presets      │       │ N presets (new) │
     │ 9 dimensions    │       │ World configs   │
     │ Quality scoring │       │ Emergence score │
     │                 │       │                 │
     │ pip install     │       │ pip install     │
     │ agentciv-engine │       │ agentciv-sim    │
     └────────────────┘       └────────────────┘
```

---

## Phase 1: Simulation Structured Metrics (agent-civilisation repo)

**Why first:** Creator Mode needs structured data to analyse. The simulation currently outputs narratives (prose), not metrics. We need quantifiable emergence data.

### 1a. Emergence Metrics Module

**File:** `src/metrics/emergence.py`

Extract quantifiable metrics from a completed simulation run:

| Metric | Source | What it measures |
|--------|--------|-----------------|
| `innovation_count` | world_state.discovered_recipes | Total innovations discovered |
| `innovation_diversity` | recipe types / categories | Breadth of innovation |
| `structure_count` | world_state.structures | Built environment complexity |
| `relationship_count` | agent.relationships | Social network size |
| `avg_relationship_strength` | relationship.trust values | Social cohesion |
| `network_density` | edges / possible edges | How connected the society is |
| `governance_rules` | world_state.collective_rules | Institutional complexity |
| `avg_wellbeing` | agent.wellbeing across all agents | Population quality of life |
| `maslow_distribution` | agent.current_need level | What % at each Maslow level |
| `specialisation_depth` | agent.specialisations | Division of labour |
| `cooperation_events` | event_bus log | Unprompted mutual aid |
| `conflict_events` | event_bus log | Disputes and resolutions |
| `population_survival` | alive agents / initial agents | Sustainability |

**Output:** `EmergenceScore` dataclass with all metrics + a composite `emergence_score` (0-1 weighted aggregate).

### 1b. Run Record for Simulation

**File:** `src/metrics/run_record.py`

Structured output equivalent to the Engine's `RunRecord`:

```python
@dataclass
class SimulationRunRecord:
    config: dict              # Full config used
    ticks_completed: int
    wall_time_seconds: float
    total_tokens: int         # LLM token usage
    emergence: EmergenceScore # From 1a
    milestones: list[str]     # Key chronicle events
    agent_summary: list[dict] # Per-agent final state summary
    chronicle_highlights: list[str]  # Top narrative moments
```

### 1c. Metrics CLI Flag

Update `scripts/run.py`:
- `--metrics` flag: after simulation completes, compute and print EmergenceScore
- `--output path.json` flag: export SimulationRunRecord to JSON
- These are small additions to the existing runner

**Estimated effort:** ~200 lines of new code. No changes to core simulation logic.

---

## Phase 2: Simulation Developer Tool Upgrade (agent-civilisation repo)

**Why:** The simulation should be installable, configurable, and runnable with the same ease as the Engine. Currently it's `python3 scripts/run.py` — it should be `agentciv-sim run`.

### 2a. Packaging

**File:** `pyproject.toml`

```toml
[project]
name = "agentciv-sim"
version = "0.1.0"
description = "AI civilisation simulation — Maslow-driven agents forming emergent societies"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
    "anthropic>=0.30",
    "openai>=1.0",
    "pydantic>=2.0",
    "fastapi>=0.115",
    "uvicorn>=0.34",
]

[project.scripts]
agentciv-sim = "agentciv_sim.cli:main"
```

**Package rename:** `src/` → `agentciv_sim/` (standard Python packaging convention)

### 2b. Configuration Presets

**Directory:** `agentciv_sim/presets/`

Named presets for common experiment configurations:

| Preset | Description | Key settings |
|--------|-------------|-------------|
| `default` | Balanced starting point | 12 agents, 50x50, moderate resources |
| `scarce` | Resource scarcity pressure | Low resources, high depletion, clustered |
| `abundant` | Resource abundance | High resources, low depletion, scattered |
| `dense` | High population density | 20 agents, 30x30, close proximity |
| `sparse` | Low population density | 6 agents, 80x80, wide spread |
| `cooperative` | Conditions favouring cooperation | Clustered resources, high communication range |
| `competitive` | Conditions favouring competition | Scattered resources, low communication range |
| `innovative` | Maximise innovation potential | All innovation features enabled, long runs |
| `minimal` | Cheapest possible run | 4 agents, 20x20, 20 ticks, fast |
| `quick` | Fast validation run | 6 agents, 30x30, 30 ticks |

Each preset is a YAML file that overrides specific SimulationConfig fields.

**Loading:** `SimulationConfig.from_preset("scarce")` — load preset YAML, merge with defaults.

### 2c. CLI Commands

**File:** `agentciv_sim/cli.py`

```
agentciv-sim run --preset default --ticks 100
agentciv-sim run --config custom.yaml --ticks 50 --fast
agentciv-sim run --preset scarce --agents 8 --ticks 30 --output results.json

agentciv-sim experiment --preset default,scarce,abundant --ticks 50 --runs 3
    → Runs 3 presets × 3 runs = 9 simulations, compares emergence scores

agentciv-sim info
    → Lists all presets, key parameters, what each measures

agentciv-sim replay --data path/to/run/
    → Starts API server for fishbowl visualisation of saved run

agentciv-sim compare results1.json results2.json
    → Side-by-side emergence metric comparison
```

**Key flags (available on all run commands):**
- `--preset NAME` — use a named preset
- `--agents N` — override agent count
- `--ticks N` — override tick count
- `--fast` — no real-time pacing
- `--output PATH` — export SimulationRunRecord JSON
- `--model NAME` — override LLM model
- `--seed N` — reproducible world generation
- `--override key=value` — override any config parameter

### 2d. MCP Integration

**File:** `agentciv_sim/mcp/server.py`

MCP tools for Claude Code integration (mirrors Engine's MCP server):

| Tool | What it does |
|------|-------------|
| `agentciv_sim_run` | Run a simulation with given config |
| `agentciv_sim_experiment` | Compare multiple configs |
| `agentciv_sim_info` | List presets and parameters |
| `agentciv_sim_status` | Check running simulation status |
| `agentciv_sim_intervene` | Gardener mode — change world mid-run |

### 2e. README Upgrade

Rewrite README to match Engine quality:
- Quickstart (pip install → first run in 60 seconds)
- What emerges (key findings from past runs)
- All presets documented
- Architecture overview
- MCP integration guide
- Example output

**Estimated effort:** ~800-1200 lines of new code. Mostly packaging, CLI, and preset YAML files. Core simulation logic untouched.

---

## Phase 3: Creator Mode Simulation Integration (agentciv-creator repo)

**Why:** This is the payoff. Creator Mode can now direct the Simulation, not just the Engine.

### 3a. Simulation Runner

**File:** `creator/simulation/runner.py`

Mirrors `creator/engine/runner.py` but for the Simulation:

```python
async def run_simulation_batch(
    configs: list[SimulationRunConfig],
    ticks: int,
    runs_per_config: int,
    session_manager=None,
    campaign_id="",
) -> list[SimulationRunResult]:
    """Run a batch of simulation experiments."""
```

**SimulationRunConfig:**
```python
@dataclass
class SimulationRunConfig:
    preset: str = "default"
    agents: int = 12
    ticks: int = 50
    overrides: dict = field(default_factory=dict)
    # e.g., {"resource_distribution": "clustered", "enable_innovation": True}
```

**SimulationRunResult:**
```python
@dataclass
class SimulationRunResult:
    id: str
    config: SimulationRunConfig
    emergence_score: float          # Composite 0-1
    emergence_metrics: dict         # Full EmergenceScore breakdown
    chronicle_highlights: list[str] # Top moments
    ticks_completed: int
    total_tokens: int
    wall_time_seconds: float
    success: bool
```

### 3b. Emergence Metrics Extraction

**File:** `creator/simulation/metrics.py`

Wraps the simulation's EmergenceScore into Creator Mode's analysis pipeline:
- Compute composite emergence score from raw metrics
- Weight different metrics based on campaign goal
- Compare emergence across configs (same statistical framework as Engine mode)

### 3c. Campaign Mode Extension

**Update:** `creator/knowledge/models.py`

```python
class CampaignMode(str, Enum):
    TASK = "task"            # Engine — optimise org for task quality
    EMERGENCE = "emergence"  # Simulation — optimise config for emergence
    HYBRID = "hybrid"        # Both — future
```

**Update:** `creator/campaign/manager.py`

- `create_campaign()` gains `mode` parameter
- When `mode="emergence"`, planner generates simulation configs instead of engine configs
- When `mode="emergence"`, runner calls simulation runner instead of engine runner
- Analysis pipeline works the same (statistical comparison of scores)

### 3d. Hypothesis Engine Update

**Update:** `creator/campaign/planner.py`

The hypothesis engine needs to reason about emergence, not just task quality:
- For `mode="task"`: "Hypothesis: hierarchical org produces higher code quality" (existing)
- For `mode="emergence"`: "Hypothesis: resource scarcity increases innovation rate"
- Different prompt templates for each mode
- Different dimension space: world config params instead of org structure params

### 3e. MCP Tool Update

**Update:** `creator/mcp/server.py`

`creator_explore` gains `mode` parameter:

```python
creator_explore(
    question="What conditions produce the richest emergence?",
    task=None,  # Not needed for emergence mode
    mode="emergence",  # NEW: "task" (default) or "emergence"
    strategy="hypothesis",
    agents=12,  # Simulation agents, not engine agents
    max_ticks=50,
    ...
)
```

### 3f. Knowledge Store Extension

**Update:** `creator/knowledge/store.py`

- Run results now include `mode` field
- Findings can reference emergence metrics, not just quality scores
- Recommendations work across both modes
- Cross-mode findings: "Innovation rate correlates with flat authority structures"

**Estimated effort:** ~500-700 lines of new code in creator repo. Mostly runner + campaign mode extension.

---

## Phase 4: Dogfood Validation

### 4a. Engine Mode Validation (already done)
- ✓ 3 campaigns, 14 runs, $83.53
- ✓ Full pipeline validated

### 4b. Simulation Mode Validation (NEW — cheap run)
- 1 campaign, 2-3 configs, 2 runs each = 4-6 simulation runs
- Use `minimal` or `quick` preset (small agent count, few ticks)
- Prove: Creator Mode can design, run, analyse, and learn from simulation experiments
- **Estimated cost:** $10-30 (depends on LLM costs for agent cognition)

### 4c. Cross-Mode Validation (stretch goal)
- 1 campaign that references findings from BOTH engine and simulation campaigns
- Prove: knowledge transfers across modes
- **Estimated cost:** $5-10 (just a few targeted runs)

---

## Phase 5: Website — Creator Mode Wing Update

With all of the above built, the website can honestly tell the full story. This is Phase D in the master roadmap — planned separately.

---

## Implementation Order

```
Step 1: Simulation metrics module (Phase 1)           ← agent-civilisation repo
        ~200 lines, no core changes, enables everything else

Step 2: Simulation packaging + CLI (Phase 2a-2c)      ← agent-civilisation repo
        ~600 lines, pyproject.toml + CLI + presets
        Makes simulation a proper dev tool

Step 3: Creator Mode sim runner (Phase 3a-3b)         ← agentciv-creator repo
        ~300 lines, mirrors engine runner

Step 4: Campaign mode extension (Phase 3c-3f)         ← agentciv-creator repo
        ~400 lines, dual-mode support throughout

Step 5: Dogfood validation (Phase 4b)                 ← run cheap sim experiments
        $10-30, proves the full pipeline

Step 6: Simulation MCP + README (Phase 2d-2e)         ← agent-civilisation repo
        ~400 lines, MCP server + docs
        (Can be done in parallel with Step 5)
```

**Total new code:** ~1,900 lines across 2 repos
**Total cost:** $10-30 for dogfood validation
**No changes to core simulation logic or engine**

---

## What This Unlocks

After this build, we have three products that form a complete stack:

| Product | Install | What it does | Status |
|---------|---------|-------------|--------|
| `agentciv-engine` | `pip install agentciv-engine` | AI teams solving tasks under configurable org structures | ✓ Published |
| `agentciv-sim` | `pip install agentciv-sim` | AI civilisations with Maslow drives, emergence, governance | After this build |
| `agentciv-creator` | MCP server | Autonomous architect directing both tools, learning from results | After this build |

And the website can say:

> **"An AI that designs its own AI civilisations."**
>
> Creator Mode autonomously designs experiments, spawns teams through the Engine or civilisations through the Simulation, analyses results, and learns which configurations work best.
>
> Give it a task — it finds the optimal team structure.
> Give it curiosity — it finds the conditions for richest emergence.
> Give it both — it discovers what no human could explore alone.

That's the real headline. And every word is true.

---

## Risk & Dependencies

| Risk | Mitigation |
|------|-----------|
| Simulation package rename breaks imports | Do it carefully with find-and-replace. All internal imports update from `src.` to `agentciv_sim.` |
| Simulation API costs more than expected per run | Use `minimal` preset for dogfood. 4 agents × 20 ticks = ~80 LLM calls = ~$2-4 per run |
| Emergence metrics are hard to composite into a single score | Start with simple weighted average. Can refine later. The individual metrics are more interesting than the composite. |
| Cross-repo changes require coordination | Build simulation changes first (Phase 1-2), commit and push, then build creator changes (Phase 3-4) that import from it |

---

## Files Changed (Summary)

### agent-civilisation repo (Simulation)
```
NEW:  agentciv_sim/metrics/emergence.py       # Emergence metrics extraction
NEW:  agentciv_sim/metrics/run_record.py      # Structured run output
NEW:  agentciv_sim/metrics/__init__.py
NEW:  agentciv_sim/cli.py                     # CLI commands
NEW:  agentciv_sim/presets/*.yaml              # 10 named presets
NEW:  agentciv_sim/mcp/server.py              # MCP integration
NEW:  pyproject.toml                           # Packaging
EDIT: scripts/run.py                           # Add --metrics, --output flags
EDIT: README.md                                # Rewrite for developer audience
```

### agentciv-creator repo (Creator Mode)
```
NEW:  creator/simulation/__init__.py
NEW:  creator/simulation/runner.py             # Simulation batch runner
NEW:  creator/simulation/metrics.py            # Emergence metric analysis
EDIT: creator/knowledge/models.py              # CampaignMode enum, sim result types
EDIT: creator/campaign/manager.py              # Dual-mode campaign support
EDIT: creator/campaign/planner.py              # Emergence hypothesis templates
EDIT: creator/mcp/server.py                    # mode parameter on creator_explore
EDIT: creator/knowledge/store.py               # Mode-aware storage
```
