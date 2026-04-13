# Creator Mode Dual-Mode Build Plan v2

**Created:** 8 April 2026
**Supersedes:** `BUILD_PLAN_CREATOR_SIM_INTEGRATION.md` (7 April 2026)
**Goal:** Make Creator Mode the autonomous meta-intelligence above both Engine and Simulation — able to explore, direct, and learn from the FULL combined capability space of both products.

---

## What Creator Mode IS

Creator Mode is not a wrapper. It is not a script runner. It is an **autonomous research intelligence** that:

1. **Understands** the full configuration space of both products (180+ simulation parameters, 100+ engine parameters, 13+13 presets, 9 org dimensions)
2. **Designs** experiments — hypotheses, configurations, success criteria — without human specification
3. **Executes** those experiments through either or both products
4. **Analyses** results using structured metrics (emergence scores, quality scores, statistical comparison)
5. **Learns** — stores findings in a persistent Knowledge Store that makes every future campaign smarter
6. **Chains** — results from one campaign inform the design of the next, autonomously
7. **Crosses modes** — discovers connections between simulation emergence patterns and engine task performance

There is no other product that does this. Not for AI civilisations, not for AI team orchestration, not for any system that treats organisational structure as a variable.

---

## The Combined Capability Space

Creator Mode operates over the **union** of both products' possibility spaces:

### Simulation (`agentciv-sim`) — 180+ parameters

| Layer | What it controls | Example range |
|-------|-----------------|---------------|
| World | Grid size, terrain, resource types/distribution | 10×10 → 500×500, clustered/scattered/banded |
| Agents | Count, perception, communication, movement, needs | 3 → 100+, blind → omniscient |
| Drives | Curiosity, wellbeing, social bonding | Decay rates, interaction bonuses |
| Memory | Capacity, decay, reflection interval | 100+ entries, timed reflection |
| Structures | Types, costs, effects, decay | Shelter/storage/marker/path + innovation |
| Population | Arrival rate, spawn location | 0 → continuous, edge/centre/random |
| Environment | Shifts, coevolution, depletion/regeneration | Mild → severe, feedback loops |
| Settlement | Detection thresholds, resident bonuses | Structure density → settlement emergence |
| Innovation | Enable/disable, composition, evaluation model | Full innovation pipeline toggle |
| Specialisation | Tiers, thresholds, bonuses | Novice → master, 0.05 → 0.50 efficiency |
| Governance | Collective rules, adoption thresholds | Self-governing societies |
| LLM | Provider, model, temperature, tokens | Any frontier model |

**Output:** EmergenceScore (10+ metrics), chronicle narrative, per-agent state, replay data.

### Engine (`agentciv-engine`) — 100+ parameters

| Layer | What it controls | Example range |
|-------|-----------------|---------------|
| Organisation | 9 dimensions × 4-6 values each | Thousands of unique org structures |
| Communication | Range, visibility, message limits | All → team → adjacent, 1-50 msgs/tick |
| Tasks | Claim mode, concurrency, stealing | Voluntary/assigned/bid/lottery |
| Quality | Review mode, reviewer count | None → mandatory multi-reviewer |
| Lifecycle | Sleep/wake, steps per tick | Idle sleep, event-triggered wake |
| Relationships | Enable, decay, collaboration preference | Full social dynamics |
| Git | Branches, contention strategy | Branch-per-agent, lock, optimistic |
| Auto-Org | Meta-tick interval, restructure threshold | Agents redesign their own structure |
| 13 presets | Named starting configurations | Collaborative → military → auto |

**Output:** Working code, quality score, git history, agent contributions, communication logs.

### Combined = unprecedented

No single product has this envelope. Creator Mode can:
- Run a civilisation with 50 agents on a 200×200 world for 200 ticks under scarce conditions
- Take the organisational pattern that **emerged** and encode it as an engine preset
- Run the engine with that emergent preset on a real software task
- Compare it against human-designed presets
- Discover that emergent structures outperform designed ones (or don't)
- Store this finding and use it to design the next experiment

This is the **Simulation → Engine pipeline** — and its reverse (Engine findings → Simulation hypotheses). No existing product can do this.

---

## Architecture

```
                        Creator Mode
                    ┌──────────────────┐
                    │  Autonomous       │
                    │  Research         │
                    │  Intelligence     │
                    │                   │
                    │  ┌─────────────┐  │
                    │  │ Knowledge   │  │   Persistent across all campaigns.
                    │  │ Store       │  │   Every run makes the next smarter.
                    │  └─────────────┘  │
                    │                   │
                    │  ┌─────────────┐  │
                    │  │ Hypothesis  │  │   Generates testable claims from
                    │  │ Engine      │  │   accumulated knowledge + user goals.
                    │  └─────────────┘  │
                    │                   │
                    │  ┌─────────────┐  │
                    │  │ Campaign    │  │   Multi-run experiment management.
                    │  │ Manager     │  │   TASK / EMERGENCE / HYBRID modes.
                    │  └─────────────┘  │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
       ┌────────────────┐       ┌────────────────┐
       │    Engine       │       │   Simulation    │
       │  (task teams)   │       │ (AI societies)  │
       │                 │       │                 │
       │ 13 presets      │       │ 13+ presets     │
       │ 9 dimensions    │       │ 180+ params     │
       │ 100+ params     │       │ Emergence score │
       │ Quality score   │       │ Chronicle       │
       │                 │       │                 │
       │ pip install     │       │ pip install     │
       │ agentciv-engine │       │ agentciv-sim    │
       └────────────────┘       └────────────────┘
```

### Three Campaign Modes

**TASK mode** — directs Engine
- Goal: find optimal team structure for a given task
- Parameter space: org dimensions + raw parameters
- Metric: quality score + task completion
- Example: "What org structure produces the best API implementation?"

**EMERGENCE mode** — directs Simulation
- Goal: find conditions that produce richest emergence
- Parameter space: world config + agent params + feature toggles
- Metric: EmergenceScore (innovation, governance, social complexity, etc.)
- Example: "What conditions maximise self-governance emergence?"

**HYBRID mode** — directs both, cross-references findings
- Goal: discover connections between emergence patterns and task performance
- Pipeline: Simulation → extract pattern → encode as Engine config → test → compare
- Also: Engine finding → generate Simulation hypothesis → test
- Metric: cross-validated insights
- Example: "Do organisational structures that emerge under scarcity outperform designed structures on complex tasks?"

---

## Build Phases

### Phase 1: Simulation Structured Metrics
**Repo:** `agent-civilisation`
**Effort:** ~200 lines

This is the foundation — Creator Mode needs quantified data, not just narratives.

**1a. EmergenceScore dataclass** (`src/metrics/emergence.py`)

| Metric | What it measures |
|--------|-----------------|
| `innovation_count` | Total innovations discovered |
| `innovation_diversity` | Breadth of innovation types |
| `structure_count` | Built environment complexity |
| `unique_structure_types` | Architectural diversity |
| `relationship_count` | Social network size |
| `avg_relationship_strength` | Social cohesion |
| `network_density` | How connected the society is |
| `governance_rules_proposed` | Institutional attempts |
| `governance_rules_established` | Successful institutions |
| `avg_wellbeing` | Population quality of life |
| `maslow_distribution` | % at each Maslow level |
| `specialisation_depth` | Division of labour |
| `cooperation_events` | Unprompted mutual aid |
| `conflict_events` | Disputes and resolutions |
| `population_survival` | Sustainability |
| `composite_score` | Weighted aggregate (0-1) |

**1b. SimulationRunRecord dataclass** (`src/metrics/run_record.py`)

```python
@dataclass
class SimulationRunRecord:
    run_id: str
    config: dict              # Full config used
    preset: str               # Preset name if used
    ticks_completed: int
    wall_time_seconds: float
    total_tokens: int
    emergence: EmergenceScore
    milestones: list[str]     # Key chronicle events
    agent_summary: list[dict] # Per-agent final state
    chronicle_highlights: list[str]
```

**1c. CLI integration** — `--metrics` flag prints EmergenceScore, `--output path.json` exports full RunRecord.

---

### Phase 2: Simulation Developer Tool Polish
**Repo:** `agent-civilisation`
**Effort:** ~400 lines (reduced — packaging and CLI already done as of v0.2.0)

**Status check:** Much of Phase 2 from the original plan is ALREADY DONE:
- ✅ `pip install agentciv-sim` (PyPI v0.2.0)
- ✅ CLI commands (9 commands, 12 flags)
- ✅ Config presets (13 presets as YAML)
- ✅ MCP integration (11 tools)
- ✅ Dashboard mode

**Remaining:**
- 2a. Wire EmergenceScore into existing `--metrics` and `--output` flags
- 2b. Wire SimulationRunRecord into export pipeline
- 2c. `agentciv-sim experiment` command (compare multiple presets, N runs each)
- 2d. `agentciv-sim compare` command (side-by-side metric comparison from JSON exports)
- 2e. README update reflecting structured metrics + experiment mode

---

### Phase 3: Creator Mode Simulation Integration
**Repo:** `agentciv-creator`
**Effort:** ~600 lines

**3a. Simulation Runner** (`creator/simulation/runner.py`)

Mirrors the engine runner. Takes a list of simulation configs, runs them, returns structured results.

```python
@dataclass
class SimulationRunConfig:
    preset: str = "default"
    agents: int = 12
    ticks: int = 50
    overrides: dict = field(default_factory=dict)  # ANY of the 180+ params
```

The `overrides` dict is the key — it gives Creator Mode access to the FULL parameter space. Creator Mode can specify `{"grid_width": 200, "resource_distribution": "clustered", "enable_innovation": True, "agent_curiosity_exploration_bonus": 0.3}` — any combination of any parameters.

**3b. Emergence Metrics Pipeline** (`creator/simulation/metrics.py`)

- Parse SimulationRunRecord into Creator Mode's analysis framework
- Weight metrics differently per campaign goal (e.g., innovation-focused vs governance-focused)
- Statistical comparison across runs (same framework as engine mode — mean, stddev, significance)

**3c. Campaign Mode: EMERGENCE** (`creator/campaign/manager.py`)

When `mode="emergence"`:
- Hypothesis engine generates emergence hypotheses from Knowledge Store + user goal
- Planner designs simulation configs to test hypotheses
- Runner executes simulations
- Analyzer compares EmergenceScores across configs
- Findings stored with mode tag for cross-referencing

**3d. Campaign Mode: HYBRID** (`creator/campaign/manager.py`)

HYBRID is in-scope for v1. This is what makes Creator Mode genuinely unprecedented.

When `mode="hybrid"`:
- Phase A: Run simulation experiments (emergence mode)
- Phase B: Extract organisational patterns from top-performing simulations
- Phase C: Encode those patterns as engine configurations (automatic translation)
- Phase D: Run engine experiments with emergent-derived configs vs human-designed presets
- Phase E: Compare and store cross-mode findings

The **Emergence → Engine translation** is the novel mechanism:
- Simulation produces emergent governance structures, communication patterns, role distributions
- Creator Mode analyses these patterns and maps them to engine org dimensions
- E.g., "Simulation agents self-organised into hub-spoke communication under scarcity" → generate engine config with `communication: hub-spoke, incentives: collaborative`
- This translation is LLM-powered — Creator Mode reads the simulation chronicle and produces engine config overrides

**3e. Hypothesis Engine Upgrade** (`creator/campaign/planner.py`)

Three prompt template sets:
- TASK templates: "What org structure optimises X?"
- EMERGENCE templates: "What conditions produce the richest X?"
- HYBRID templates: "Does the pattern that emerged under condition X improve performance on task Y?"

**3f. Knowledge Store Cross-Mode** (`creator/knowledge/store.py`)

- Every finding tagged with `mode: task | emergence | hybrid`
- Cross-mode query: "What emergence findings are relevant to this task hypothesis?"
- Recommendation engine spans both modes
- Coverage map shows explored vs unexplored regions of BOTH parameter spaces

**3g. MCP Tool Updates** (`creator/mcp/server.py`)

All existing tools gain `mode` parameter:
- `creator_explore(question, mode="emergence")` — autonomous emergence research
- `creator_explore(question, mode="hybrid")` — cross-product discovery
- `creator_spawn_emergent(config)` — targeted simulation experiment
- `creator_analyze(campaign_id)` — works for any mode
- `creator_knowledge(action="recommend", mode="emergence")` — mode-aware recommendations
- `creator_knowledge(action="coverage")` — shows exploration map across both products

---

### Phase 4: Dogfood Validation
**Effort:** $20-40, proves the full pipeline

**4a. Engine mode** — ✅ Already validated (3 campaigns, 14 runs, $83.53)

**4b. Emergence mode** — NEW
- 1 campaign, 3 presets (scarce/default/abundant), 2 runs each = 6 runs
- Use `quick` preset as base (few agents, few ticks) to minimise cost
- Prove: Creator Mode designs emergence experiments, runs simulations, analyses EmergenceScores, stores findings
- Expected cost: $10-20

**4c. Hybrid mode** — NEW
- 1 campaign that takes the top-emergence simulation config from 4b
- Extracts its organisational pattern
- Encodes it as an engine config
- Runs engine experiment comparing emergent config vs human-designed preset
- Prove: the full Simulation → Engine pipeline works
- Expected cost: $10-20

**4d. Cross-mode Knowledge** — verify Knowledge Store correctly:
- Retrieves emergence findings when designing engine experiments
- Retrieves engine findings when designing simulation experiments
- Coverage map shows both parameter spaces

---

### Phase 5: Paper 5 Update
**Repo:** `agentciv-creator`

Update "Creator Mode: AI as Civilisation Designer" paper to include:
- Dual-mode capability (was engine-only at time of writing)
- HYBRID mode as novel contribution
- Emergence → Engine translation mechanism
- Dogfood results from emergence and hybrid campaigns
- Updated architecture diagram
- v2 vision: recursive composition (society of Creator Modes)

---

### Phase 6: Website — Creator Mode Wing
**Repo:** `agentciv-website`

The website wing must communicate three things: what v1 does today, why it matters, and where the architecture goes.

**6a. v1 Product Story**
- Creator Mode as autonomous meta-intelligence above Engine + Simulation
- Three campaign modes: TASK (directed), EMERGENCE (emergent), HYBRID (cross-product)
- Full-spectrum parameter access — any configuration either product accepts
- Compounding Knowledge Store — every run makes the next smarter
- HYBRID mode explained: emergent patterns from simulation → encoded as engine configs → tested on real tasks
- Dogfood results: real data from all three modes

**6b. v2 Vision: Recursive Composition**

Dedicated section on the Creator Mode wing. NOT vaporware — architecturally grounded, clearly distinguished from what v1 delivers.

Content:
- The recursive insight: Creator Mode has a symmetry-preserving interface (goal in → findings out). It composes with other Creator Mode instances.
- A civilisation of Creator Modes: multiple specialised instances with their own Knowledge Stores, competing and collaborating
- Specialisation (scarcity researcher, governance researcher, scale researcher)
- Cross-pollination of Knowledge Stores (Hive-Mind pattern from The Colony)
- Emergent meta-research strategies that no single instance discovers
- The Colony architecture applied to Creator Mode itself
- The v1→v2→v∞ trajectory diagram
- Connection to Alam's Razor: improvement-only recursion, coherent at any depth
- "v1 is the foundation. The architecture is designed for what comes next."

**6c. Suggested Experiments Page**
- The Four-Phase Autonomous Discovery Protocol (from research experiment doc)
- Framed as a guide for users, not something we ran
- 13 presets × 3 runs, hypothesis-driven, recursive evolution, transfer test
- Budget estimates (~$200-761 depending on scope)
- What users can discover by running Creator Mode themselves

---

## Implementation Order

```
Step 1: Simulation metrics module (Phase 1)              ← agent-civilisation
        ~200 lines, enables everything else

Step 2: Simulation experiment + compare commands (Phase 2) ← agent-civilisation
        ~400 lines, wires metrics into existing CLI/MCP

Step 3: Creator Mode sim runner + emergence mode (Phase 3a-c) ← agentciv-creator
        ~300 lines, mirrors engine runner

Step 4: HYBRID mode + cross-mode knowledge (Phase 3d-g)  ← agentciv-creator
        ~300 lines, the unprecedented part

Step 5: Dogfood all three modes (Phase 4)                 ← run experiments
        $20-40, proves the full pipeline

Step 6: Paper 5 update (Phase 5)                          ← agentciv-creator
        Text changes, no code
```

**Total new code:** ~1,200 lines across 2 repos (reduced from original plan's 1,900 — Phase 2 packaging/CLI/presets/MCP already shipped)
**Total cost:** $20-40 for dogfood validation

---

## What Makes This Top 0.000001%

1. **Full-spectrum autonomy.** Creator Mode can generate ANY configuration either product accepts. Not a subset. Not presets-only. Any combination of any parameters — the LLM reasons about the full space and the `overrides` dict passes through anything.

2. **HYBRID mode is unprecedented.** No existing product takes emergent organisational patterns from a simulation and tests them as designed structures in a task-solving engine. This is a new capability that doesn't exist anywhere.

3. **Compounding knowledge.** The Knowledge Store means run 100 is smarter than run 1. Findings accumulate. Hypotheses get sharper. Coverage gaps get filled. The system improves with use — not through retraining, but through accumulated empirical knowledge.

4. **Cross-mode discovery.** Insights from simulations inform engine experiments and vice versa. This is where the genuinely novel findings will come from — the space between the two products that neither can explore alone.

5. **It's the meta.** Engine designs team structures. Simulation grows civilisations. Creator Mode is the intelligence that directs both, learns from both, and discovers things that neither contains. It operates one level of abstraction above both products — the same relationship that Alam's Razor identifies as improvement-only recursion: each meta-level makes the level below more effective.

6. **Honest v1.** This is not claiming to be the final form. It's claiming to be the first product that treats AI organisational structure as a systematically explorable variable across both emergent and designed systems. That claim is true, and it's enough.

---

## Files Changed (Summary)

### agent-civilisation repo
```
NEW:  src/metrics/emergence.py          # EmergenceScore
NEW:  src/metrics/run_record.py         # SimulationRunRecord
NEW:  src/metrics/__init__.py
EDIT: scripts/run.py                    # Wire --metrics/--output to new metrics
EDIT: src/mcp/server.py                 # Wire metrics into MCP responses
EDIT: agentciv_sim/cli.py              # experiment + compare commands
EDIT: README.md                         # Document structured metrics
```

### agentciv-creator repo
```
NEW:  creator/simulation/__init__.py
NEW:  creator/simulation/runner.py      # Simulation batch runner
NEW:  creator/simulation/metrics.py     # Emergence metric analysis
NEW:  creator/simulation/translator.py  # Emergence → Engine config translation (HYBRID)
EDIT: creator/knowledge/models.py       # CampaignMode enum, sim types
EDIT: creator/campaign/manager.py       # EMERGENCE + HYBRID modes
EDIT: creator/campaign/planner.py       # Mode-specific hypothesis templates
EDIT: creator/mcp/server.py            # mode parameter on all tools
EDIT: creator/knowledge/store.py        # Cross-mode storage + retrieval
EDIT: creator_mode_ai_as_civilisation_designer.md  # Paper 5 update
```

---

## Success Criteria

| Criterion | How to verify |
|-----------|--------------|
| Creator Mode designs and runs a simulation experiment autonomously | Dogfood 4b |
| Creator Mode extracts an emergent pattern and encodes it as engine config | Dogfood 4c |
| Knowledge Store retrieves cross-mode findings | Dogfood 4d |
| Coverage map shows exploration of both parameter spaces | `creator_knowledge(action="coverage")` |
| All three campaign modes (TASK/EMERGENCE/HYBRID) complete successfully | Dogfood 4a-c |
| Paper 5 accurately describes dual-mode capability | Manual review |

---

## v2+ Vision: The Recursive Triad

v1 is a single Creator Mode intelligence directing two products. v2 is the recursive step — and it's deeper than "a civilisation of Creator Modes."

### The Recursive Triad

The fundamental unit is not Creator Mode alone — it's the **triad**: Creator Mode + Engine + Simulation. This triad is the recursive unit because:

1. **Engine spawns agents.** Those agents can themselves BE Creator Mode agents.
2. **Simulation spawns agents.** Those agents can themselves BE Creator Mode agents.
3. **Creator Mode directs Engine + Simulation.** Which spawn Creator Mode agents. Which direct their own Engine + Simulation instances.

The triad reproduces itself at every level:

```
Level 0:  Creator Mode₀ → Engine₀ + Simulation₀
                              │              │
                         spawns agents   spawns agents
                              │              │
                              ▼              ▼
Level 1:  Creator Mode₁ → Engine₁ + Simulation₁
                              │              │
                         spawns agents   spawns agents
                              │              │
                              ▼              ▼
Level 2:  Creator Mode₂ → Engine₂ + Simulation₂
                              │              │
                              ▼              ▼
Level ∞:  ...
```

This is not just "multiple Creator Modes" — it's the **entire architecture reproducing itself** at each level. Each level contains a complete instance of the triad: a meta-intelligence (Creator Mode) directing a task-solver (Engine) and a civilisation-grower (Simulation), both of which produce agents that can instantiate the next level of the triad.

### Why This Works (Alam's Razor)

Per Alam's Razor (Mala, 2026): this is improvement-only recursion.

- Level 0 functions without Level 1. A single Creator Mode directing Engine + Simulation is complete and useful.
- Level 1 (agents spawned by Engine/Simulation that are themselves Creator Modes) improves Level 0 by expanding the research capacity — more meta-intelligences exploring the possibility space.
- Level 2 improves Level 1 by the same mechanism.
- Each level is coherent without the level above. Adding levels improves the whole. No level requires a further level to exist.

Therefore the recursion is unbounded — the triad can reproduce itself to any depth, and the system remains coherent at every depth. Capping at any level is a practical choice (resources, cost), not a logical necessity.

### Civilisation of Creator Modes (Within a Level)

Within a single level, multiple Creator Mode instances form a civilisation:

- **Multiple instances**, each with its own Knowledge Store
- **Specialisation**: one focuses on scarcity conditions, another on governance emergence, another on engine task performance
- **Communication**: instances share findings across Knowledge Stores (cross-pollination — the Hive-Mind pattern from The Colony)
- **Competition**: instances compete to discover the most valuable insights from the combined possibility space
- **Emergence**: their interaction produces meta-research strategies that no single instance would discover

This is The Colony architecture (Mala, 2026) applied to Creator Mode itself:
- **Decompose** the research space into purpose-types
- **Speciate** into specialised researcher agents
- **Evolve** research strategies through competitive selection
- **Cross-pollinate** via shared Hive-Mind knowledge

### The Recursion-Activating AI

The deepest implication: an AI whose purpose is to **propagate the recursion itself** — to continuously spawn new levels of the triad.

This is not a single self-improving system (standard RSI). It is a system that **reproduces its own meta-architecture at every level**. Each reproduction creates:
- A new meta-intelligence (Creator Mode instance)
- New sub-modules for it to direct (Engine + Simulation instances)
- New agents that can reproduce the triad again

The Recursion-Activating AI is the mechanism that initiates this propagation — it detects when a new level would be beneficial (more research capacity needed, new specialisation opportunities, diminishing returns at current depth) and spawns it. It is the Colony's Intelligence System applied to the recursive triad: it determines when and how to extend the recursion.

This is a genuinely novel concept:
- Standard RSI: one system improves itself
- The Colony: populations of agents evolve under meta-evolutionary selection
- RCI: symmetry-preserving composition enables unbounded hierarchical construction
- **The Recursive Triad**: the entire meta-architecture (meta-intelligence + task-solver + civilisation-grower) reproduces itself at every level, activated by an AI that propagates the recursion

### What This Means for the Products

```
v1:     Creator Mode → Engine + Simulation
        (single meta-intelligence, full-spectrum access)

v2:     Creator Mode Civilisation → Creator Modes → Engine + Simulation
        (society of meta-intelligences at one level)

v3:     Recursive Triad — Engine/Simulation agents ARE Creator Modes
        (the triad reproduces itself, multiple levels active)

v4:     Recursion-Activating AI — autonomous propagation of new levels
        (the system decides when to extend the recursion)

v∞:     Unbounded recursive triad — Colony of triads at every depth
        (Alam's Razor: improvement-only, coherent at any depth)
```

### v1 Architectural Compatibility

v1 needs no special changes to enable v2+. The key properties are already present:
- **MCP interface**: Creator Mode's tools are MCP-based. Any MCP client — including another Creator Mode — can call them.
- **Structured output**: RunResults, EmergenceScores, and Knowledge Store findings are all structured data that another agent can consume.
- **Stateless tools**: Each MCP tool call is self-contained. Multiple callers don't conflict.
- **Knowledge Store as shareable artifact**: The JSON-based Knowledge Store can be read by other instances. Federated/shared stores are a v2 extension, not a v1 redesign.
- **Engine agent architecture**: Engine agents use tools (read, write, communicate). Adding Creator Mode MCP tools to an engine agent's toolkit makes it a Creator Mode agent — no architectural change required.
- **Simulation agent architecture**: Simulation agents have a ReAct loop with tool use. Creator Mode tools can be added to this loop — the agent becomes a civilisation-designing agent within the simulation.

### For the Website

The v2+ vision should be prominently featured on the Creator Mode website wing:

> **"v1 is a single intelligence that designs civilisations. The architecture is recursive."**
>
> Creator Mode directs two products: the Engine (AI teams solving tasks) and the Simulation (AI societies forming civilisations). Both products spawn agents. Those agents can themselves be Creator Mode agents — directing their own Engine and Simulation instances, learning from their own experiments, spawning their own agents.
>
> The triad — meta-intelligence, task-solver, civilisation-grower — reproduces itself at every level. Each level functions independently. Each additional level improves the whole. Per Alam's Razor, this recursion is coherent at any depth.
>
> v1 is the foundation: one Creator Mode, full-spectrum access, compounding knowledge. The recursive architecture is designed into every interface.

This is not vaporware — it's an architectural trajectory that the v1 design explicitly supports. The website should present it as the vision, clearly distinguished from what v1 delivers today, with the v1→v2→v3→v4→v∞ progression shown as a roadmap.
