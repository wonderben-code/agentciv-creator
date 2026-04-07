# CREATOR MODE V1 — PRODUCT BIBLE

> The definitive specification for Creator Mode v1.
> Every design decision, every tool, every data structure, every implementation step.
> If it's not in this document, it's not in v1.
>
> **Last updated:** 7 April 2026
> **Status:** Pre-implementation specification
> **Theoretical foundation:** Paper 5 — "Creator Mode: AI as Civilisation Designer" (Bitcoin-stamped April 2026)

---

## TABLE OF CONTENTS

1. [What Is Creator Mode](#1-what-is-creator-mode)
2. [Who Uses It & Why](#2-who-uses-it--why)
3. [Example Session](#3-example-session)
4. [Architecture](#4-architecture)
5. [Core Concepts](#5-core-concepts)
6. [The 7 MCP Tools](#6-the-7-mcp-tools)
7. [Data Model & Knowledge Store](#7-data-model--knowledge-store)
8. [Search Strategies](#8-search-strategies)
9. [Integration: AgentCiv Engine (Directed Arm)](#9-integration-agentciv-engine-directed-arm)
10. [Integration: AgentCiv Simulation (Emergent Arm)](#10-integration-agentciv-simulation-emergent-arm)
11. [The Recursive Emergence Loop](#11-the-recursive-emergence-loop)
12. [Implementation Plan](#12-implementation-plan)
13. [File Structure](#13-file-structure)
14. [Risks & Mitigations](#14-risks--mitigations)
15. [Success Criteria](#15-success-criteria)
16. [What V2 Adds](#16-what-v2-adds)
17. [Paper 5 Update Plan](#17-paper-5-update-plan)
18. [Appendices](#18-appendices)

---

## 1. WHAT IS CREATOR MODE

Creator Mode is an autonomous organisational architect for multi-agent AI systems.

You give it a question — *"What's the best way to organise 12 AI agents for code review?"* — and it designs experiments, runs them using the AgentCiv Engine and Simulation, analyzes results, generates new hypotheses, runs more experiments, and converges on a data-backed answer. Everything it learns persists in a knowledge store that gets smarter with every run.

**Claude Code IS the Creator.** We're not building a separate LLM loop — we're giving Claude the right tools to become the meta-intelligence that Paper 5 describes. The most capable reasoning model on earth becomes the civilisation designer.

**The key insight:** Nobody knows the right way to organise AI agent teams. Every developer and researcher is guessing. Creator Mode turns organisational design from guesswork into empirical science — and it does the science autonomously.

### What Creator Mode IS

- An MCP server with 7 tools that Claude Code connects to
- An autonomous research engine that designs and runs organisational experiments
- A knowledge store that accumulates findings across campaigns and gets smarter over time
- A recommendation engine that tells you exactly how to configure your multi-agent system
- A recursive emergence loop that turns emergent organisational forms into next-generation configurations
- The first tool that treats multi-agent organisational design as an empirical science

### What Creator Mode is NOT

- Not a web app (it's a CLI/MCP tool, consistent with ERA 2's terminal-first philosophy)
- Not a replacement for the engine or simulation (it sits above both, orchestrates both)
- Not a separate LLM loop — Claude Code's reasoning IS the Creator's intelligence
- Not limited to one arm — it works across both directed (engine) and emergent (simulation)
- Not magic — it runs real experiments with real data, real statistical analysis, real evidence

### The One-Liner

**Creator Mode is to multi-agent AI what Neural Architecture Search is to deep learning — but for organisational structure, not network topology.**

At primitive scale (v1), it's an automated organisational search engine. At full scale (v2+), it's a civilisation of AIs that designs AI civilisations — and the recursive emergence loop means it gets better at designing civilisations by studying the civilisations it has already created.

---

## 2. WHO USES IT & WHY

### Use Case 1: Organisational Architecture Search

**Who:** Developer building a multi-agent product (customer support, code review, content pipeline, etc.)

**Problem:** "I have 20 AI agents handling customer tickets. I set them up as a flat team because that's all I know. It works, but is there something better? I have no idea — and testing 13 different structures manually would take weeks."

**What Creator Mode does:**
1. Generates 15-30 candidate org configurations spanning presets, dimension variations, and custom hybrids
2. Runs each against simulated versions of the developer's workload using the engine
3. Ranks results by quality, efficiency, conflict rate, and coordination overhead
4. Identifies the winner and explains WHY it works (not just what scored highest)
5. Produces a ready-to-use config

**Output:** "Use the code-review preset with `authority=distributed` and `communication=clustered`. This produces 40% fewer merge conflicts than your current flat setup because distributed authority prevents coordinator bottlenecks at your agent count, and clustered communication creates natural sub-teams that reduce cross-talk noise. Here's the YAML."

**Time:** ~30 minutes (20 experiment runs, fully autonomous)

### Use Case 2: Automated Research

**Who:** AI researcher studying collective behaviour

**Problem:** "I have a hypothesis that communication topology matters more than incentive structure for creative tasks. Testing this properly requires a factorial experiment with multiple conditions and enough runs for statistical significance. That's 48+ experiment runs. I don't have time to manually configure and babysit all of them."

**What Creator Mode does:**
1. Designs a rigorous factorial experiment (4 comm types × 4 incentive types = 16 conditions)
2. Runs 3 trials per condition (48 total runs)
3. Computes effect sizes, p-values, confidence intervals
4. Extracts publishable findings
5. Identifies unexpected interactions ("mesh + competitive is anomalously good for creative tasks — investigate?")
6. Generates follow-up hypotheses
7. Produces a structured report with reproducible methodology

**Output:** Statistical report with effect sizes, confidence intervals, interaction effects, and suggested follow-up experiments. Publishable-quality data.

### Use Case 3: Emergence Exploration

**Who:** Researcher studying emergent AI behaviour

**Problem:** "Under what conditions do AI agents spontaneously develop governance structures? I'd need to run dozens of civilisation simulations with different environmental pressures and measure emergence across each."

**What Creator Mode does:**
1. Designs simulation configs varying environmental pressures (resource scarcity, communication range, grid size, agent count)
2. Spawns emergent civilisation simulations for each condition
3. Measures emergence metrics (innovations, governance rules, social structures, cooperation events)
4. Identifies which environmental factors most strongly predict governance emergence
5. Cross-pollinates: takes directed-arm findings about effective org structures and tests whether those structures ALSO emerge naturally in the right conditions
6. Generates theories and follow-up experiments

**Output:** "Governance emergence is most strongly predicted by resource scarcity (r=0.72) and communication range (r=0.58). When resources are scarce AND communication range is ≥3 tiles, governance structures emerge within 30 ticks in 85% of runs. Interestingly, the governance forms that emerge most frequently resemble the 'meritocratic' preset from the directed arm."

### Use Case 4: Scale-Up Analysis

**Who:** Company scaling an AI agent fleet

**Problem:** "Our 4-agent team works great with a flat structure. We're growing to 40 agents. Will the same structure work? Where will it break?"

**What Creator Mode does:**
1. Runs the current config at 4, 8, 12, 16, 20, 30, 40 agents
2. Measures coordination overhead, conflict rate, quality degradation at each scale
3. Identifies breaking points ("flat coordination collapses at 16 agents — message volume grows quadratically")
4. Recommends structural transitions at each growth threshold
5. Stores findings: "At 20+ agents, switch from flat to clustered sub-teams of 6-8"

**Output:** A scale-up guide with specific transition points and recommended configurations at each scale.

---

## 3. EXAMPLE SESSION

What using Creator Mode actually feels like. This is a real conversation between a user, Claude Code, and Creator Mode.

```
User:
  I'm deploying 8 AI agents to handle code review for our monorepo.
  What org structure should I use?

Claude:
  Let me design a research campaign to find the optimal configuration.

  [calls creator_explore]
  Question: "Optimal org structure for 8-agent code review"
  Task: "Build a REST API with auth, CRUD endpoints, and tests"
  Agents: 8, Max runs: 21, Runs per config: 3

Creator Mode returns:
  Campaign C004 started.
  Strategy: hypothesis-driven

  Initial hypotheses:
    H1: "code-review preset will outperform general presets for review-heavy work"
    H2: "hierarchical will bottleneck at 8 agents (single coordinator)"
    H3: "distributed authority allows parallel review without bottleneck"
    H4: "auto mode will converge on a review-optimised structure"

  Batch 1 plan (6 configs × 3 runs = 18 runs):
    code-review, meritocratic, hierarchical, collaborative, auto,
    code-review + authority=distributed

  Running...

Claude:
  Campaign started — testing 6 configurations, 3 runs each.
  I'll check progress in a few minutes.

  [5 minutes later, calls creator_status("C004")]

Creator Mode returns:
  Progress: 9/18 runs complete (batch 1, halfway)
  Early signal:
    code-review:     quality 0.87, conflicts 2.3
    meritocratic:    quality 0.85, conflicts 1.7
    hierarchical:    quality 0.71, conflicts 4.3  ← struggling
    collaborative:   quality 0.79, conflicts 1.0

  H2 looking confirmed: hierarchical at 8 agents shows coordinator bottleneck.
  One agent doing 60% of reviews while others idle.

Claude:
  Halfway through. Hierarchical is struggling — single coordinator bottleneck
  as expected. code-review and meritocratic leading. Let it finish.

  [10 minutes later, calls creator_status("C004")]

Creator Mode returns:
  Batch 1 COMPLETE. 18/18 runs done.

  Rankings after batch 1:
    1. code-review + authority=distributed  →  quality 0.91, conflicts 1.7
    2. code-review (default)                →  quality 0.87, conflicts 2.3
    3. meritocratic                         →  quality 0.85, conflicts 1.7
    4. auto                                 →  quality 0.84, conflicts 1.0
    5. collaborative                        →  quality 0.79, conflicts 1.0
    6. hierarchical                         →  quality 0.71, conflicts 4.3

  Hypotheses resolved:
    H1: SUPPORTED — code-review preset outperforms general presets
    H2: SUPPORTED — hierarchical bottlenecks at 8 agents
    H3: SUPPORTED — distributed authority + code-review wins
    H4: INCONCLUSIVE — auto mode scored mid-pack but showed interesting
        restructuring (voted to add mandatory review at tick 8)

  New hypotheses from analysis:
    H5: "Adding clustered communication to the winner could create natural
         sub-teams and further reduce conflicts"
    H6: "Auto mode's self-adopted review policy suggests meritocratic
         review + distributed authority is the convergence point"

  Batch 2 plan (1 config × 3 runs = 3 runs):
    code-review + authority=distributed + communication=clustered

  Running batch 2...

  [3 minutes later]

  Batch 2 COMPLETE. 21/21 runs done. Campaign complete.

  FINAL RANKING:
    1. code-review + authority=distributed           quality: 0.91 ± 0.03
    2. code-review + distributed + clustered          quality: 0.89 ± 0.02
    3. code-review (default)                         quality: 0.87 ± 0.04
    4. meritocratic                                  quality: 0.85 ± 0.03
    5. auto                                          quality: 0.84 ± 0.05
    6. collaborative                                 quality: 0.79 ± 0.03
    7. hierarchical                                  quality: 0.71 ± 0.06

  WINNER: code-review + authority=distributed

  Findings stored:
    F012: "Distributed authority outperforms hierarchical for code review at
           8+ agents (effect size 0.73, p < 0.01, n=21)"
    F013: "Hierarchical bottlenecks at 8 agents due to single-coordinator
           review throughput ceiling"
    F014: "Auto mode independently converges on meritocratic-like review
           policy (mandatory review, earned influence), supporting the
           hypothesis that meritocratic review is a natural attractor"

Claude:
  Campaign complete. 21 experiments across 7 configurations.

  Winner: **code-review preset with authority=distributed**
  - Quality score: 0.91 (±0.03)
  - Merge conflicts: 1.7 per run (vs 4.3 for hierarchical)
  - Why it wins: distributed authority eliminates the coordinator bottleneck
    that cripples hierarchical at 8 agents, while keeping mandatory review
    gates that ensure quality

  Interesting finding: when auto mode was given no preset, it independently
  voted to adopt mandatory reviews at tick 8 — essentially rediscovering
  what the code-review preset bakes in. This suggests review-focused
  structures are a natural attractor for quality-focused tasks.

  Want me to generate the exact config YAML?

User:
  Yes, and also — can you check if you know anything about scaling this
  to 20 agents?

Claude:
  [calls creator_knowledge]
  Query: "scaling distributed authority code review beyond 8 agents"

Creator Mode returns:
  No direct findings for 20-agent code review.
  Related: F012 confirms distributed authority > hierarchical at 8+.
  Coverage gap: no data above 8 agents for this task type.
  Suggestion: run a scale-up campaign (8, 12, 16, 20 agents).

Claude:
  No data yet for 20 agents — we've only tested at 8. Shall I run a
  scale-up campaign to find where the structure breaks and what to
  change at each growth point?
```

This is Creator Mode. The user asks a question. Creator Mode designs the science, runs it, learns from it, and delivers answers. Every finding persists. The next user who asks about code review benefits from everything this campaign discovered.

---

## 4. ARCHITECTURE

### System Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     USER (via terminal)                       │
│                                                              │
│  "What's the best org for code review?"                      │
│  "Do civilisations develop governance faster with more agents?"│
└─────────────────────────┬────────────────────────────────────┘
                          │ conversation
┌─────────────────────────▼────────────────────────────────────┐
│                      CLAUDE CODE                              │
│                   (The Creator's Brain)                        │
│                                                              │
│  General reasoning + orchestration + user interaction          │
│  Connects to all MCP servers simultaneously                   │
│                                                              │
│  ┌──────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Engine MCP Client │  │Creator MCP Client│  │  (future)   │ │
│  └────────┬─────────┘  └───────┬─────────┘  └─────────────┘ │
└───────────┼────────────────────┼─────────────────────────────┘
            │ MCP                │ MCP
┌───────────▼──────────┐  ┌─────▼─────────────────────────────┐
│  AGENTCIV ENGINE     │  │  CREATOR MODE MCP SERVER           │
│                      │  │                                    │
│  13 presets           │  │  7 Tools:                          │
│  9 dimensions         │  │    creator_explore                 │
│  Auto mode            │  │    creator_spawn_directed          │
│  Learning system      │  │    creator_spawn_emergent          │
│  Benchmark suite      │  │    creator_analyze                 │
│  Chronicle observer   │  │    creator_knowledge               │
│  Gardener mode        │  │    creator_recursive               │
│  Max Plan + API mode  │  │    creator_status                  │
│                      │  │                                    │
│  MCP tools:           │  │  Internal systems:                 │
│    agentciv_solve     │  │    Campaign Manager                │
│    agentciv_experiment│  │    Hypothesis Engine (LLM)         │
│    agentciv_configure │  │    Knowledge Store                 │
│    agentciv_benchmark │  │    Analysis Pipeline               │
│    agentciv_intervene │  │    Emergence Analyzer              │
│    agentciv_orchestrate│ │    Recursive Loop Engine           │
│    agentciv_info      │  │    Coverage Tracker                │
│    agentciv_status    │  │                                    │
└──────────────────────┘  └──────────────┬─────────────────────┘
                                         │
                            ┌────────────┴────────────┐
                            │ imports as Python library │
                            ▼                          ▼
                 ┌──────────────────┐     ┌──────────────────────┐
                 │  AGENTCIV ENGINE │     │  AGENTCIV SIMULATION │
                 │  (Python API)    │     │  (subprocess)        │
                 │                  │     │                      │
                 │  EngineConfig    │     │  scripts/run.py      │
                 │  Engine.run()    │     │  config.yaml         │
                 │  Experiment mode │     │  Maslow-driven agents│
                 │  Benchmark tasks │     │  Emergent world      │
                 │  Learning system │     │  Event bus           │
                 └──────────────────┘     └──────────────────────┘
```

### Why This Architecture

1. **Claude Code IS the Creator's intelligence.** No separate LLM loop, no redundant reasoning. Claude's general reasoning + Creator Mode's domain tools = the meta-agent from Paper 5.

2. **Creator Mode imports the engine as a Python library** for directed-arm experiments. This avoids MCP-to-MCP complexity and enables parallel execution, retries, and internal orchestration.

3. **Simulation is triggered via subprocess** because it's a separate Python project. Creator Mode generates config YAML files and calls `python3 scripts/run.py --config <path> --ticks <N> --fast --record`.

4. **Claude Code connects to both MCP servers** so it can use Creator Mode for high-level campaigns AND the engine directly for one-off runs, gardening, or status checks.

5. **The Knowledge Store lives on disk** (`~/.agentciv-creator/`) and persists across sessions, conversations, and campaigns. Every finding ever discovered is available forever.

### Data Flow

```
EXPLORE LOOP:

1. User asks question
2. Claude → creator_explore(question, task, constraints)
3. Creator Mode internally:
   a. Queries Knowledge Store for prior relevant findings
   b. Hypothesis Engine (LLM call) generates hypotheses
   c. Campaign Planner designs experiment batch
   d. Runner executes experiments via engine Python API
   e. Analysis Pipeline extracts metrics + findings
   f. Hypothesis Engine generates new hypotheses from results
   g. If budget remaining + new hypotheses → loop to (c)
   h. Store all findings in Knowledge Store
   i. Return campaign results
4. Claude → creator_status(campaign_id) to check progress
5. Campaign completes → Claude → creator_analyze or show results to user

CROSS-POLLINATION:

Directed finding: "meritocratic teams produce fewer conflicts"
    ↓ feeds into
Emergent config: initialise simulation with merit-based social norms
    ↓ produces
Emergent finding: "agents invented rotating leadership by tick 40"
    ↓ feeds into
New directed preset: test "rotating" authority configuration
    ↓ produces
Directed finding: "rotating authority scores 0.88 — new top 3"
```

---

## 5. CORE CONCEPTS

### Campaigns

A **campaign** is a research inquiry. It has a question, constraints, a plan, runs, and findings. Campaigns can be single-batch (run all experiments, analyze, done) or iterative (run → analyze → plan next batch → run → repeat).

**Lifecycle:** `planning → running → analyzing → [running → analyzing →]* complete`

A campaign's intelligence comes from iterative refinement: each batch of results informs the next batch of experiments. Run 1 is exploratory. Run 10 is surgical.

### Hypotheses

A **hypothesis** is a specific, testable prediction. Creator Mode generates these using LLM reasoning about the research question + existing knowledge. Each hypothesis specifies what to test, what outcome to expect, and why.

**Lifecycle:** `untested → testing → supported | refuted | inconclusive`

Hypotheses are the engine of intelligent exploration. Instead of brute-force grid search, Creator Mode asks: "What do I think will work and why? Let me test that."

### Findings

A **finding** is a data-backed conclusion extracted from experiment results. Findings have confidence levels (based on evidence strength), conditions (when they apply), and relationships to other findings (supports, contradicts, extends).

Findings are the atomic unit of knowledge. The Knowledge Store is built from findings.

### Knowledge Store

The **Knowledge Store** is Creator Mode's persistent memory across all campaigns. It contains every finding, every hypothesis, every campaign record. It answers questions like:
- "What works best for code review?" → finding F012
- "What regions of the possibility space haven't been explored?" → coverage map
- "What should I test next?" → untested hypotheses ranked by potential value

The Knowledge Store gets smarter with every campaign. Early campaigns are exploratory. Later campaigns leverage accumulated findings to skip known experiments and focus on gaps.

### Coverage Map

The **coverage map** tracks which regions of the CMI possibility space have been explored. Paper 5 defines five axes: scale, intelligence, configuration, application, emergence. The coverage map shows which combinations have data and which are terra incognita.

This enables proactive suggestions: *"We've never tested scale > 12 in emergent mode. Want me to explore that?"*

### The Explore Loop

The core algorithm that makes Creator Mode autonomous:

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  PLAN   │────▶│   RUN   │────▶│ ANALYZE │────▶│  LEARN  │
│         │     │         │     │         │     │         │
│ Generate│     │ Execute │     │ Extract │     │ Store   │
│ hypotheses│   │ experi- │     │ findings│     │ findings│
│ Design  │     │ ments   │     │ Update  │     │ Update  │
│ experiments│  │ via     │     │ hypotheses│   │ coverage│
│         │     │ engine  │     │ Compute │     │ Generate│
│         │     │         │     │ stats   │     │ new     │
│         │     │         │     │         │     │ hypotheses│
└─────────┘     └─────────┘     └─────────┘     └────┬────┘
     ▲                                                │
     │          budget remaining?                      │
     │          new hypotheses?                        │
     └────────────── YES ─────────────────────────────┘
                      │
                      NO
                      ▼
               ┌─────────────┐
               │   REPORT    │
               │             │
               │ Rankings    │
               │ Key findings│
               │ Recommend-  │
               │ ations      │
               └─────────────┘
```

### Cross-Pollination

Findings from the directed arm (engine) generate hypotheses for the emergent arm (simulation), and vice versa. This is what makes Creator Mode more than just an experiment runner — it discovers connections between how teams SHOULD be organised and how they NATURALLY organise.

Example flow:
- **Directed finding:** "Meritocratic teams produce fewer conflicts than hierarchical"
- **Generated emergent hypothesis:** "Agent civilisations with merit-based interaction bonuses will develop more stable governance"
- **Emergent finding:** "Agents independently invented rotating leadership by tick 40 in 3/5 runs"
- **Generated directed hypothesis:** "A 'rotating' authority preset might outperform static authority assignments"
- **New directed experiment tests this**

In v1, cross-pollination is Claude-mediated (Claude reads findings from one arm and designs experiments for the other). In v2, Creator Mode does this automatically.

---

## 6. THE 7 MCP TOOLS

### Overview

| # | Tool | What It Does |
|---|------|-------------|
| 1 | `creator_explore` | The big one. Research question → full autonomous campaign → findings |
| 2 | `creator_spawn_directed` | Spawn directed experiments via the engine. Hypothesis-driven configs. |
| 3 | `creator_spawn_emergent` | Spawn emergent civilisation simulations. Vary conditions. |
| 4 | `creator_analyze` | Deep cross-run, cross-arm analysis. Pattern detection. |
| 5 | `creator_knowledge` | Access the knowledge store. Query findings, recommendations, coverage. |
| 6 | `creator_recursive` | Run the recursive emergence loop. Paper 7 made real. |
| 7 | `creator_status` | Dashboard. Campaign progress, steering, management. |

---

### Tool 1: `creator_explore`

**Purpose:** Start a full autonomous research campaign. This is the primary tool — most interactions start here.

**Parameters:**
```python
creator_explore(
    question: str,              # REQUIRED. The research question.
                                # "What's the best org for 12-agent code review?"
                                # "Does communication topology matter more than incentive structure?"
                                # "At what agent count does hierarchical break down?"

    task: str,                  # REQUIRED. What agents will do in each experiment.
                                # Natural language: "Build a REST API with auth and tests"
                                # Or benchmark ID: "fizzbuzz", "kv_store", "todo_api",
                                #   "calculator", "data_pipeline", "web_scraper"

    arm: str = "directed",      # Which arm(s) to use:
                                #   "directed" — engine experiments only (DEFAULT, fastest)
                                #   "emergent" — simulation runs only
                                #   "both"     — cross-pollination between arms

    strategy: str = "hypothesis",  # Search strategy:
                                   #   "grid"       — test all presets systematically
                                   #   "sweep"      — isolate one dimension at a time
                                   #   "hypothesis" — LLM-generated hypotheses (DEFAULT)
                                   #   "knowledge"  — leverage existing findings, fill gaps

    agents: int = 4,            # Agent count (fixed across campaign)
    model: str = "claude-sonnet-4-6",  # Model for experiment agents
    max_ticks: int = 50,        # Max ticks per experiment run

    max_runs: int = 21,         # Budget: max total experiment runs
    runs_per_config: int = 3,   # Runs per configuration (statistical reliability)

    focus_presets: list[str] | None = None,     # Only test these presets
    focus_dimensions: list[str] | None = None,  # Only vary these dimensions

    project_dir: str = "."      # Working directory for engine experiments
)
```

**Returns:**
```json
{
    "campaign_id": "C004",
    "status": "running",
    "strategy": "hypothesis",
    "arm": "directed",

    "initial_hypotheses": [
        {"id": "H012", "statement": "code-review preset will outperform general presets", "rationale": "purpose-built for review-heavy work"},
        {"id": "H013", "statement": "hierarchical bottlenecks at 8 agents", "rationale": "single coordinator throughput ceiling"},
        {"id": "H014", "statement": "distributed authority enables parallel review", "rationale": "removes coordinator dependency"}
    ],

    "plan": {
        "batch_1": {
            "configs": [
                {"preset": "code-review"},
                {"preset": "meritocratic"},
                {"preset": "hierarchical"},
                {"preset": "collaborative"},
                {"preset": "auto"},
                {"preset": "code-review", "overrides": {"authority": "distributed"}}
            ],
            "runs_per_config": 3,
            "total_runs": 18,
            "rationale": "Cover purpose-built preset, nearest alternatives, and one hypothesis-driven variant"
        },
        "remaining_budget": 3
    },

    "estimated_time_minutes": 30,
    "knowledge_context": "2 prior findings relevant to this question (from C001)",
    "message": "Campaign C004 started. 6 configs × 3 runs = 18 runs in batch 1. Use creator_status('C004') to check progress."
}
```

**Behaviour:**
1. Queries Knowledge Store for prior relevant findings
2. Generates hypotheses based on question + knowledge + strategy
3. Plans batch 1 of experiments
4. Runs experiments in background (parallel where possible)
5. After batch completes: analyzes, extracts findings, generates new hypotheses
6. If budget remaining AND new hypotheses → plans and runs next batch
7. Stores all findings in Knowledge Store
8. Campaign status updates available via `creator_status()`

---

### Tool 2: `creator_spawn_directed`

**Purpose:** Spawn directed team experiments via the engine. More granular control than `creator_explore` — use this when you want to test specific configurations, not ask open-ended questions.

**Parameters:**
```python
creator_spawn_directed(
    task: str,                  # REQUIRED. What agents will do.
    configs: list[dict],        # REQUIRED. Configurations to test.
                                # Each: {"preset": "name", "overrides": {"dim": "val"}}
                                # Example: [
                                #   {"preset": "collaborative"},
                                #   {"preset": "competitive"},
                                #   {"preset": "auto"},
                                #   {"preset": "collaborative", "overrides": {"authority": "rotating"}}
                                # ]

    agents: int = 4,
    model: str = "claude-sonnet-4-6",
    max_ticks: int = 50,
    runs_per_config: int = 3,

    campaign_id: str | None = None,  # Attach to existing campaign (or create new)
    project_dir: str = "."
)
```

**Returns:**
```json
{
    "campaign_id": "C004",
    "batch_id": "B003",
    "configs_queued": 4,
    "total_runs": 12,
    "status": "running",
    "message": "4 configs × 3 runs = 12 experiments queued. Running..."
}
```

**When to use instead of `creator_explore`:**
- You already know exactly what configs to test
- You want to add experiments to an existing campaign
- You want to test a custom config that `creator_explore` wouldn't generate
- Cross-pollination: testing a config inspired by an emergent finding

---

### Tool 3: `creator_spawn_emergent`

**Purpose:** Spawn emergent civilisation simulations via the AgentCiv Simulation. Design and launch simulations to study emergence under specific conditions.

**Parameters:**
```python
creator_spawn_emergent(
    hypothesis: str,            # REQUIRED. What emergence pattern to investigate.
                                # "Resource scarcity increases governance emergence"
                                # "Larger groups develop specialisation faster"
                                # "Communication range correlates with cooperation"

    agents: int = 12,           # Agent count
    ticks: int = 100,           # Simulation length

    conditions: dict | None = None,  # Specific config overrides for treatment
                                     # {"resource_regeneration_rate": 0.02,
                                     #  "resource_distribution": "clustered"}

    control: bool = True,       # Also generate control config (default values)
    variations: int = 1,        # Number of treatment variations to generate
                                # >1 creates multiple configs varying the hypothesis variable

    campaign_id: str | None = None,  # Attach to existing campaign

    sim_dir: str = "/Users/ekramalam/agent-civilisation"  # Simulation repo path
)
```

**Returns:**
```json
{
    "campaign_id": "C005",
    "configs_generated": [
        {
            "id": "sim_001_treatment",
            "path": "~/.agentciv-creator/campaigns/C005/sim_configs/treatment_001.yaml",
            "key_settings": {
                "initial_agent_count": 12,
                "resource_regeneration_rate": 0.02,
                "resource_distribution": "clustered"
            },
            "run_command": "cd /Users/ekramalam/agent-civilisation && python3 scripts/run.py --config ~/.agentciv-creator/campaigns/C005/sim_configs/treatment_001.yaml --ticks 100 --fast --record"
        },
        {
            "id": "sim_001_control",
            "path": "~/.agentciv-creator/campaigns/C005/sim_configs/control_001.yaml",
            "key_settings": {
                "initial_agent_count": 12,
                "resource_regeneration_rate": 0.05,
                "resource_distribution": "scattered"
            },
            "run_command": "cd /Users/ekramalam/agent-civilisation && python3 scripts/run.py --config ~/.agentciv-creator/campaigns/C005/sim_configs/control_001.yaml --ticks 100 --fast --record"
        }
    ],
    "hypothesis_variable": "resource_regeneration_rate",
    "treatment_value": 0.02,
    "control_value": 0.05,
    "message": "2 simulation configs generated. Run both, then use creator_analyze to compare emergence metrics."
}
```

**Note:** In v1, simulations are NOT run automatically by Creator Mode. Creator Mode generates configs and run commands. Claude (or the user) runs them. This is because:
- Simulations are expensive (12+ agents × 100+ ticks = significant API cost)
- Simulations take 30+ minutes
- Users often want to observe simulations in real-time
- Full autonomous simulation campaigns come in v2

---

### Tool 4: `creator_analyze`

**Purpose:** Deep cross-run analysis. Pattern detection across both arms. Statistical comparison. Finding extraction.

**Parameters:**
```python
creator_analyze(
    campaign_id: str | None = None,  # Analyze a specific campaign

    # OR provide raw data directly:
    directed_results: list[dict] | None = None,  # Engine run results
    emergent_data_dirs: list[str] | None = None, # Simulation output directories

    analysis_type: str = "full",  # "full", "comparison", "emergence", "cross_arm"
                                  # "full" — everything
                                  # "comparison" — rank configs, compute stats
                                  # "emergence" — analyze simulation data for emergence
                                  # "cross_arm" — find patterns across directed + emergent

    metrics: list[str] | None = None,  # Focus on specific metrics
                                       # Directed: "quality", "conflicts", "efficiency", "coordination"
                                       # Emergent: "governance", "cooperation", "innovation",
                                       #           "social_structure", "specialisation", "wellbeing"

    format: str = "full"        # "full" (detailed), "summary" (key findings only), "table" (data)
)
```

**Returns (full analysis):**
```json
{
    "campaign_id": "C004",
    "analysis_type": "full",

    "rankings": [
        {
            "rank": 1,
            "config": {"preset": "code-review", "overrides": {"authority": "distributed"}},
            "quality_score": {"mean": 0.91, "std": 0.03, "n": 3},
            "merge_conflicts": {"mean": 1.7, "std": 0.6},
            "efficiency": {"mean": 0.85, "std": 0.04},
            "ticks_used": {"mean": 32, "std": 4}
        }
    ],

    "statistical_tests": [
        {
            "comparison": "code-review+distributed vs hierarchical",
            "metric": "quality_score",
            "effect_size": 0.73,
            "p_value": 0.003,
            "significant": true,
            "method": "independent_t_test"
        }
    ],

    "findings": [
        {
            "id": "F012",
            "statement": "Distributed authority outperforms hierarchical for code review at 8+ agents",
            "confidence": 0.88,
            "evidence_runs": 6,
            "stored": true
        }
    ],

    "emergence_metrics": null,  // populated when analyzing simulation data

    "cross_arm_patterns": null,  // populated for cross_arm analysis

    "hypotheses_resolved": [
        {"id": "H013", "statement": "hierarchical bottlenecks at 8 agents", "status": "supported"}
    ],

    "new_hypotheses": [
        {"id": "H017", "statement": "clustered communication could further reduce conflicts on winner", "status": "untested"}
    ],

    "report_markdown": "# Campaign C004 Analysis\n\n## Summary\n..."
}
```

**When analysis_type is "emergence":**
```json
{
    "emergence_metrics": {
        "governance": {
            "rules_proposed": 5,
            "rules_established": 3,
            "adoption_rate_mean": 0.72,
            "first_rule_tick": 28,
            "governance_emerged": true
        },
        "cooperation": {
            "resource_sharing_events": 34,
            "mutual_aid_events": 12,
            "cooperation_rate": 0.65,
            "first_cooperation_tick": 15
        },
        "innovation": {
            "innovations_proposed": 8,
            "innovations_built": 5,
            "unique_compositions": 3,
            "innovation_rate_per_tick": 0.05
        },
        "social_structure": {
            "clusters_formed": 2,
            "avg_relationship_strength": 0.61,
            "social_density": 0.43,
            "hub_agents": [3, 7]
        },
        "specialisation": {
            "specialists_emerged": 4,
            "gini_coefficient": 0.38,
            "dominant_specialisations": ["gather (3)", "build (2)"]
        },
        "wellbeing": {
            "avg_final": 0.74,
            "maslow_distribution": {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 1, "7": 1, "8": 0},
            "trajectory": "ascending"
        }
    },
    "key_moments": [
        {"tick": 15, "event": "First mutual aid — Agent 3 gave water to Agent 7 unprompted"},
        {"tick": 28, "event": "First governance rule: 'Share food locations' (75% adoption)"},
        {"tick": 52, "event": "Settlement formed — 3 structures clustered at (7,8)"}
    ],
    "comparison_to_control": {
        "governance_emergence_delta": "+45%",
        "cooperation_rate_delta": "+23%"
    }
}
```

---

### Tool 5: `creator_knowledge`

**Purpose:** Access the accumulated knowledge store. Query findings, get recommendations, see coverage, find untested hypotheses.

**Parameters:**
```python
creator_knowledge(
    action: str = "query",      # "query", "recommend", "coverage", "hypotheses", "stats"

    # For action="query":
    question: str | None = None,  # Natural language: "What works for code review?"
    min_confidence: float = 0.5,
    max_results: int = 10,

    # For action="recommend":
    task_type: str | None = None,    # "code_review", "api_dev", "data_pipeline"
    agents: int | None = None,
    priority: str | None = None,     # "quality", "speed", "creativity", "balanced"

    # For action="coverage":
    # No extra params — returns full coverage map

    # For action="hypotheses":
    status: str | None = None,  # "untested", "supported", "refuted", or None for all
)
```

**Returns (action="query"):**
```json
{
    "query": "What works for code review?",
    "findings": [
        {
            "id": "F012",
            "statement": "Distributed authority outperforms hierarchical for code review at 8+ agents",
            "confidence": 0.88,
            "conditions": {"task_type": "code_review", "agent_count": [8, 20]},
            "evidence_runs": 12,
            "source_campaign": "C004"
        }
    ],
    "related_hypotheses": [
        {"id": "H017", "statement": "Rotating reviewer roles improves review quality", "status": "untested"}
    ]
}
```

**Returns (action="recommend"):**
```json
{
    "recommendation": {
        "preset": "code-review",
        "overrides": {"authority": "distributed"},
        "full_config": {
            "authority": "distributed",
            "communication": "mesh",
            "roles": "emergent",
            "decisions": "meritocratic",
            "incentives": "reputation",
            "information": "transparent",
            "conflict": "voted",
            "groups": "self-selected",
            "adaptation": "evolving"
        },
        "parameters": {
            "require_review": true,
            "review_mode": "peer",
            "min_reviewers": 2
        }
    },
    "confidence": 0.85,
    "justification": "Based on 21 runs from campaign C004...",
    "alternatives": [
        {"preset": "meritocratic", "quality_delta": "-7%", "note": "More resilient to agent failure"}
    ],
    "data_quality": "good"  // "insufficient" | "limited" | "good" | "strong"
}
```

**Returns (action="coverage"):**
```json
{
    "coverage_map": {
        "directed": {
            "presets_tested": ["code-review", "meritocratic", "hierarchical", "collaborative", "auto", "competitive"],
            "presets_untested": ["startup", "pair-programming", "open-source", "military", "research-lab", "swarm", "hackathon"],
            "dimensions_varied": ["authority", "communication"],
            "dimensions_unvaried": ["roles", "decisions", "incentives", "information", "conflict", "groups", "adaptation"],
            "agent_counts_tested": [4, 8],
            "agent_counts_gap": "no data above 8 agents",
            "task_types_tested": ["code_review", "api_development"],
            "task_types_gap": "no data for data_pipeline, creative tasks"
        },
        "emergent": {
            "simulations_run": 3,
            "conditions_tested": ["resource_scarcity", "communication_range"],
            "conditions_untested": ["grid_size", "agent_count_scaling", "drive_weights"]
        }
    },
    "suggestions": [
        "No data above 8 agents — consider a scale-up campaign",
        "7 presets never tested — grid search would fill this gap",
        "No emergent runs with >12 agents — Paper 5's scale axis unexplored"
    ]
}
```

**Returns (action="hypotheses"):**
```json
{
    "hypotheses": [
        {"id": "H017", "statement": "Rotating reviewer roles improves quality", "status": "untested", "priority": "high"},
        {"id": "H019", "statement": "Swarm preset fails for coordination-heavy tasks", "status": "untested", "priority": "medium"}
    ],
    "total": {"untested": 5, "supported": 9, "refuted": 3, "inconclusive": 2}
}
```

**Returns (action="stats"):**
```json
{
    "total_campaigns": 5,
    "total_runs": 63,
    "total_findings": 18,
    "total_hypotheses": 24,
    "knowledge_store_size_kb": 340,
    "oldest_finding": "2026-04-07",
    "newest_finding": "2026-04-12",
    "most_explored_area": "code_review with 4-8 agents",
    "least_explored_area": "creative tasks, emergent arm, scale >12"
}
```

---

### Tool 6: `creator_recursive`

**Purpose:** Run the recursive emergence loop from Paper 7. Extract emergent organisational forms from simulation runs → convert them into directed-arm configurations → test them → use the best as seeds for next-generation simulations → track evolution across generations.

This is the mechanism by which Creator Mode doesn't just search the existing space — it **expands** the space by discovering organisational forms that nobody designed.

**Parameters:**
```python
creator_recursive(
    seed: str | dict,           # REQUIRED. Starting point:
                                # String: preset name ("auto", "collaborative")
                                # Dict: {"preset": "auto", "overrides": {...}}
                                # Or: "from_simulation:<data_dir>" to extract from existing sim

    task: str,                  # REQUIRED. Task for directed-arm testing

    generations: int = 3,       # Number of generations to evolve

    population_size: int = 4,   # Configs per generation (top N survive + mutate)

    agents: int = 4,
    model: str = "claude-sonnet-4-6",
    max_ticks: int = 50,
    runs_per_config: int = 2,   # Runs per config per generation

    mutation_rate: float = 0.3, # Probability of changing each dimension in offspring

    include_emergent: bool = False,  # Also spawn simulations to look for novel org forms
    sim_ticks: int = 100,

    campaign_id: str | None = None
)
```

**Returns:**
```json
{
    "campaign_id": "C006",
    "type": "recursive",
    "generations_planned": 3,

    "generation_0": {
        "status": "complete",
        "configs": [
            {"preset": "auto", "quality": 0.84},
            {"preset": "collaborative", "quality": 0.79},
            {"preset": "meritocratic", "quality": 0.85},
            {"preset": "code-review", "quality": 0.87}
        ],
        "survivors": ["code-review", "meritocratic"]
    },

    "generation_1": {
        "status": "running",
        "configs": [
            {"preset": "code-review", "overrides": {"authority": "distributed"}, "source": "mutation of code-review"},
            {"preset": "meritocratic", "overrides": {"communication": "clustered"}, "source": "mutation of meritocratic"},
            {"preset": "code-review", "overrides": {"authority": "distributed", "communication": "clustered"}, "source": "crossover"},
            {"preset": "custom", "overrides": {"authority": "rotating", "decisions": "meritocratic", "incentives": "reputation"}, "source": "extracted from auto-mode run (agents voted for these)"}
        ],
        "rationale": "Top 2 from gen 0 + mutations + crossover + emergent extraction from auto-mode"
    },

    "evolution_trajectory": [
        {"gen": 0, "best_quality": 0.87, "best_config": "code-review"},
        {"gen": 1, "best_quality": "...", "best_config": "..."}
    ],

    "message": "Recursive loop running. Generation 1 in progress. Use creator_status('C006') for updates."
}
```

**How the recursive loop works:**

```
Generation 0: Test N seed configs
    ↓ select top K
Generation 1: Mutate winners + crossover + extract emergent forms
    ↓ test all → select top K
Generation 2: Mutate + crossover + extract
    ↓ ...
Generation N: Final best config is an org form that EVOLVED through selection pressure
```

**Emergent form extraction:** When `include_emergent=true` or when an auto-mode run produces restructuring events, Creator Mode extracts the FINAL organisational state (after agents voted on their own structure) and uses it as a config in the next generation. This means agent-designed org forms compete against human-designed presets — and sometimes win.

---

### Tool 7: `creator_status`

**Purpose:** Dashboard and campaign management. Check progress, steer direction, stop campaigns.

**Parameters:**
```python
creator_status(
    campaign_id: str | None = None,  # Specific campaign, or None for overview

    # Management actions (optional):
    steer: str | None = None,       # Natural language guidance: "Focus on auto mode"
    add_configs: list[dict] | None = None,  # Add configs to next batch
    stop: bool = False              # Gracefully end campaign
)
```

**Returns (overview — no campaign_id):**
```json
{
    "active_campaigns": [
        {"id": "C004", "question": "Best org for code review?", "progress": "18/21 runs", "eta_minutes": 5}
    ],
    "completed_campaigns": [
        {"id": "C001", "question": "Hierarchical scaling limits", "findings": 4, "completed": "2026-04-07"}
    ],
    "knowledge_stats": {
        "total_findings": 18,
        "total_runs": 63,
        "total_hypotheses": 24,
        "hypotheses_tested": 19,
        "knowledge_store_size": "340 KB"
    },
    "suggestions": [
        "5 untested hypotheses ready to explore",
        "7 presets never tested in directed arm",
        "No emergent data above 12 agents"
    ]
}
```

**Returns (specific campaign):**
```json
{
    "campaign_id": "C004",
    "question": "Best org for code review?",
    "status": "running",
    "progress": {
        "runs_completed": 18,
        "runs_total": 21,
        "batches_completed": 1,
        "current_batch": 2,
        "elapsed_minutes": 25
    },
    "current_leader": {
        "config": {"preset": "code-review", "overrides": {"authority": "distributed"}},
        "quality_score": 0.91,
        "conflicts": 1.7
    },
    "interim_findings": [
        {"statement": "Hierarchical bottlenecks at 8 agents", "confidence": 0.85}
    ],
    "next_batch_plan": {
        "configs": ["code-review+distributed+clustered"],
        "rationale": "Testing clustered communication on winner"
    }
}
```

**Steering example:**
```python
creator_status(
    campaign_id="C004",
    steer="Skip the remaining configs and focus only on auto-mode variants — I want to see what agents design for themselves"
)
```

Returns updated plan reflecting the new direction.

---

## 7. DATA MODEL & KNOWLEDGE STORE

### File System Layout

```
~/.agentciv-creator/
├── config.json                         # Creator Mode settings
├── knowledge/
│   ├── index.json                      # Searchable index + stats + coverage
│   ├── findings/
│   │   ├── F001.json
│   │   ├── F002.json
│   │   └── ...
│   └── hypotheses/
│       ├── H001.json
│       ├── H002.json
│       └── ...
└── campaigns/
    ├── C001/
    │   ├── campaign.json               # Campaign metadata, plan, status
    │   ├── runs/
    │   │   ├── run_001.json            # Individual run results + metrics
    │   │   ├── run_002.json
    │   │   └── ...
    │   ├── analysis/
    │   │   ├── batch_1_analysis.json   # Per-batch analysis
    │   │   └── final_analysis.json     # Campaign-level analysis
    │   ├── sim_configs/                # Generated simulation YAMLs (emergent arm)
    │   │   ├── treatment_001.yaml
    │   │   └── control_001.yaml
    │   └── report.md                   # Final campaign report (markdown)
    ├── C002/
    │   └── ...
    └── ...
```

### Campaign Schema

```json
{
    "id": "C004",
    "question": "Optimal org structure for 8-agent code review",
    "status": "complete",
    "type": "explore",
    "arm": "directed",
    "strategy": "hypothesis",

    "created": "2026-04-07T15:30:00Z",
    "completed": "2026-04-07T16:15:00Z",

    "constraints": {
        "agents": 8,
        "model": "claude-sonnet-4-6",
        "max_ticks": 50,
        "task": "Build a REST API with authentication, CRUD endpoints, and tests",
        "task_is_benchmark": false
    },

    "budget": {
        "max_runs": 21,
        "runs_per_config": 3,
        "runs_completed": 21
    },

    "batches": [
        {
            "id": "B001",
            "batch_number": 1,
            "status": "complete",
            "configs": [
                {"preset": "code-review", "overrides": null},
                {"preset": "meritocratic", "overrides": null},
                {"preset": "hierarchical", "overrides": null},
                {"preset": "collaborative", "overrides": null},
                {"preset": "auto", "overrides": null},
                {"preset": "code-review", "overrides": {"authority": "distributed"}}
            ],
            "runs_per_config": 3,
            "total_runs": 18,
            "rationale": "Cover purpose-built preset, nearest alternatives, and hypothesis-driven variant"
        },
        {
            "id": "B002",
            "batch_number": 2,
            "status": "complete",
            "configs": [
                {"preset": "code-review", "overrides": {"authority": "distributed", "communication": "clustered"}}
            ],
            "runs_per_config": 3,
            "total_runs": 3,
            "rationale": "Test clustered communication on winner (hypothesis from batch 1)"
        }
    ],

    "runs": ["run_001", "run_002", "..."],
    "findings_generated": ["F012", "F013", "F014"],
    "hypotheses_tested": ["H012", "H013", "H014"],
    "hypotheses_generated": ["H017", "H018"],

    "result": {
        "winner": {
            "preset": "code-review",
            "overrides": {"authority": "distributed"},
            "metrics": {
                "quality_score": {"mean": 0.91, "std": 0.03},
                "merge_conflicts": {"mean": 1.7, "std": 0.6},
                "ticks_used": {"mean": 32, "std": 4}
            }
        },
        "full_ranking": [
            {"config": "code-review+distributed", "quality_mean": 0.91},
            {"config": "code-review+distributed+clustered", "quality_mean": 0.89},
            {"config": "code-review", "quality_mean": 0.87},
            {"config": "meritocratic", "quality_mean": 0.85},
            {"config": "auto", "quality_mean": 0.84},
            {"config": "collaborative", "quality_mean": 0.79},
            {"config": "hierarchical", "quality_mean": 0.71}
        ],
        "key_insight": "Distributed authority eliminates coordinator bottleneck at 8 agents"
    }
}
```

### Finding Schema

```json
{
    "id": "F012",
    "statement": "Distributed authority outperforms hierarchical for code review at 8+ agents",
    "confidence": 0.88,
    "type": "comparative",

    "evidence": [
        {
            "campaign": "C004",
            "run": "run_003",
            "config": {"preset": "code-review", "overrides": {"authority": "distributed"}},
            "metric": "quality_score",
            "value": 0.91
        },
        {
            "campaign": "C004",
            "run": "run_009",
            "config": {"preset": "hierarchical"},
            "metric": "quality_score",
            "value": 0.72
        }
    ],

    "conditions": {
        "task_types": ["code_review"],
        "agent_count_range": [8, null],
        "model": "claude-sonnet-4-6"
    },

    "statistics": {
        "effect_size": 0.73,
        "p_value": 0.003,
        "n_runs": 6,
        "method": "independent_t_test"
    },

    "related": {
        "supports": ["F014"],
        "contradicts": [],
        "extends": []
    },

    "discovered": "2026-04-07T15:45:00Z",
    "source_campaign": "C004",
    "tags": ["authority", "code_review", "scaling", "bottleneck"]
}
```

### Hypothesis Schema

```json
{
    "id": "H013",
    "statement": "Hierarchical organisational structure bottlenecks at 8 agents due to single-coordinator throughput ceiling",
    "status": "supported",

    "test_design": {
        "independent_variable": "authority",
        "treatment": "hierarchy",
        "control": "distributed",
        "outcome_metric": "quality_score",
        "expected_direction": "control > treatment",
        "agent_count": 8
    },

    "evidence": {
        "supporting": [
            {"campaign": "C004", "run": "run_009", "metric": "quality_score", "value": 0.71},
            {"campaign": "C004", "run": "run_010", "metric": "quality_score", "value": 0.72}
        ],
        "contradicting": []
    },

    "source": "hypothesis_engine",
    "generated_from": "analysis of question + domain knowledge",
    "generated": "2026-04-07T15:30:00Z",
    "resolved": "2026-04-07T15:50:00Z",

    "priority": "high",
    "tags": ["authority", "scaling", "bottleneck"]
}
```

### Knowledge Index Schema

```json
{
    "version": 1,
    "last_updated": "2026-04-12T10:30:00Z",

    "stats": {
        "total_campaigns": 5,
        "total_runs": 63,
        "total_findings": 18,
        "total_hypotheses": 24,
        "hypotheses_breakdown": {
            "untested": 5,
            "supported": 12,
            "refuted": 3,
            "inconclusive": 4
        }
    },

    "findings_by_tag": {
        "authority": ["F001", "F005", "F008", "F012"],
        "communication": ["F002", "F006"],
        "scaling": ["F003", "F007", "F012"],
        "auto_mode": ["F004", "F009", "F014"],
        "emergence": ["F010", "F011", "F015"],
        "code_review": ["F012", "F013", "F014"]
    },

    "coverage": {
        "directed": {
            "presets_tested": ["code-review", "meritocratic", "hierarchical", "collaborative", "auto", "competitive"],
            "presets_untested": ["startup", "pair-programming", "open-source", "military", "research-lab", "swarm", "hackathon"],
            "dimensions_varied": ["authority", "communication"],
            "agent_counts_tested": [4, 8],
            "task_types_tested": ["code_review", "api_development"]
        },
        "emergent": {
            "simulations_run": 3,
            "conditions_tested": ["resource_scarcity", "communication_range"],
            "agent_counts_tested": [12],
            "max_ticks_tested": [100]
        }
    }
}
```

---

## 8. SEARCH STRATEGIES

### Grid Search

**How it works:** Test every preset (or a specified subset) systematically.

**When to use:** Initial exploration. "I have no idea what works — show me everything."

**Plan generation:**
1. Select presets (default: all 13, or `focus_presets`)
2. Always include "auto" for self-organisation data
3. Run each `runs_per_config` times
4. Rank by primary metric (quality_score)
5. Single batch, no iteration

**Strengths:** Comprehensive, no bias, good baseline data for Knowledge Store.
**Weaknesses:** Expensive (13 × 3 = 39 runs). Doesn't test dimension variations.
**Best for:** First-ever campaign on a new task type.

### Dimension Sweep

**How it works:** Hold 8 dimensions constant, vary 1 through all its values. Repeat per dimension.

**When to use:** "Collaborative is close to right but which dimensions should I tweak?"

**Plan generation:**
1. Choose base config (best known, or specified)
2. For each dimension in `focus_dimensions` (or all 9):
   a. Generate one config per value of that dimension
   b. Run `runs_per_config` times each
3. Identify which dimensions have the largest effect on the outcome
4. Report dimension importance ranking

**Strengths:** Identifies which dimensions matter most. Systematic.
**Weaknesses:** Misses interaction effects. Many runs needed for full sweep.
**Best for:** Refining a known-good config.

### Hypothesis-Driven (DEFAULT)

**How it works:** LLM generates specific hypotheses, designs experiments to test them, adapts after each batch.

**When to use:** Most situations. Intelligent exploration.

**Plan generation:**
1. LLM receives: question + task + constraints + existing knowledge
2. Generates 3-5 hypotheses with rationale
3. Designs minimal experiment set to test all hypotheses
4. Runs batch 1
5. Analyzes: which hypotheses supported/refuted?
6. LLM generates new hypotheses from results
7. Runs batch 2
8. Repeats until convergence or budget

**Strengths:** Efficient — tests most informative experiments first. Explains WHY things work, not just what scores highest.
**Weaknesses:** Depends on LLM reasoning quality. Can miss non-obvious optima.
**Best for:** Specific research questions with clear variables.

### Knowledge-Informed

**How it works:** Query Knowledge Store first, use existing findings to skip known experiments, focus on gaps.

**When to use:** When significant prior knowledge exists.

**Plan generation:**
1. Query Knowledge Store for all relevant findings
2. Identify well-characterised configs (don't re-test)
3. Identify gaps (untested presets, untested agent counts, untested task types)
4. Focus experiments on filling gaps
5. Test edge cases of existing findings ("F012 says distributed > hierarchical at 8 agents — does this hold at 4?")

**Strengths:** Avoids redundant work. Gets smarter with more data.
**Weaknesses:** Only useful after several campaigns. Can be too narrow.
**Best for:** Incremental knowledge building after initial exploration.

---

## 9. INTEGRATION: AGENTCIV ENGINE (DIRECTED ARM)

### What Creator Mode Uses

Creator Mode imports `agentciv` as a Python library and uses:

| Engine Component | Creator Mode Usage |
|---|---|
| `EngineConfig.from_preset()` | Load preset configs with optional overrides |
| `Engine` class | Run experiments programmatically |
| Chronicle reports | Extract quality metrics + narrative |
| Run history (`~/.agentciv/run_history.jsonl`) | Read past results from non-Creator runs |
| Learning system | Inject knowledge into auto mode meta-ticks |
| Benchmark tasks (6 built-in) | Standardized reproducible tasks |
| Benchmark verification | Automated quality scoring |
| Auto-org restructure events | Extract emergent org forms for recursive loop |

### How Experiments Are Run

```python
from agentciv.org.config import EngineConfig
from agentciv.core.engine import Engine

async def run_single(preset: str, task: str, agents: int,
                     max_ticks: int, overrides: dict | None = None,
                     project_dir: str = ".") -> RunResult:
    """Run one experiment and return structured metrics."""

    config = EngineConfig.from_preset(preset)
    config.task = task
    config.agent_count = agents
    config.max_ticks = max_ticks

    if overrides:
        for dim, val in overrides.items():
            setattr(config.org_dimensions, dim, val)

    config.project_dir = project_dir

    engine = Engine(config)
    result = await engine.run()

    return extract_metrics(result)
```

### Parallel Execution

Multiple experiments run concurrently, each in its own temporary directory:

```python
import asyncio
import tempfile

async def run_batch(configs: list[dict], task: str, agents: int,
                    max_ticks: int, runs_per: int) -> list[RunResult]:
    """Run a batch of experiments with parallel execution."""

    tasks = []
    for config in configs:
        for run_idx in range(runs_per):
            tmp_dir = tempfile.mkdtemp(prefix="creator_")
            tasks.append(
                run_single(
                    preset=config["preset"],
                    task=task,
                    agents=agents,
                    max_ticks=max_ticks,
                    overrides=config.get("overrides"),
                    project_dir=tmp_dir
                )
            )

    return await asyncio.gather(*tasks, return_exceptions=True)
```

**Note:** Parallelism is bounded by available API rate limits. Creator Mode should respect Anthropic's rate limits and queue experiments accordingly.

### Metrics Captured Per Run

```python
@dataclass
class RunResult:
    # Configuration
    preset: str
    overrides: dict[str, str] | None
    agent_count: int
    model: str
    max_ticks: int

    # Primary Outcomes
    quality_score: float              # 0-1, computed by engine
    completion_rate: float            # 0-1
    test_pass_rate: float | None      # 0-1, if benchmark task

    # Coordination Metrics
    ticks_used: int
    total_messages: int
    total_broadcasts: int
    merge_conflicts: int
    merges_succeeded: int

    # Auto-Org (if applicable)
    restructures_adopted: int
    restructure_log: list[dict]       # [{tick, dimension, old, new, proposer, votes}]
    final_org_state: dict[str, str]   # Final dimension values after restructuring

    # Efficiency
    total_tokens: int
    tokens_per_agent: dict[str, int]
    wall_time_seconds: float
    files_produced: int

    # Specialisation
    emergent_specialisation: float    # Gini coefficient

    # Raw
    chronicle_report: str
    run_record: dict
```

### Engine Benchmark Tasks Available

| Task ID | Difficulty | Description | Max Ticks |
|---------|-----------|-------------|-----------|
| `fizzbuzz` | Simple | Implement fizzbuzz + tests | 5 |
| `kv_store` | Simple | Key-value store with persistence | 10 |
| `todo_api` | Medium | REST API with auth + CRUD | 25 |
| `calculator` | Medium | Distributed calculator | 20 |
| `data_pipeline` | Hard | Complex ETL coordination | 40 |
| `web_scraper` | Hard | Web scraping + parsing + storage | 35 |

Benchmark tasks are valuable for Creator Mode because they have **automated verification** — the engine can objectively score whether the task was completed correctly. This removes subjectivity from quality metrics.

---

## 10. INTEGRATION: AGENTCIV SIMULATION (EMERGENT ARM)

### v1 Scope

In v1, simulation integration is **config generation + result analysis**. Creator Mode does NOT autonomously run simulation campaigns. Instead:

1. `creator_spawn_emergent()` generates simulation config YAML files
2. Claude (or user) runs the simulation via command line
3. `creator_analyze(analysis_type="emergence")` analyzes simulation output

This is appropriate for v1 because:
- Simulations are expensive (each tick calls LLMs for every agent)
- Simulations take 30+ minutes for meaningful emergence
- Users often want to watch simulations unfold in real-time
- Full autonomous simulation campaigns come in v2

### Config Generation

Creator Mode generates YAML configs the simulation understands. The key insight: to study emergence, you vary **environmental pressures** (not agent behaviour — that's the whole point of emergence).

**Variables Creator Mode can manipulate:**

| Variable | Range | What It Tests |
|----------|-------|---------------|
| `initial_agent_count` | 5-200 | Scale effects |
| `resource_regeneration_rate` | 0.01-0.10 | Scarcity vs abundance |
| `resource_distribution` | clustered/scattered/banded | Geographic pressure |
| `agent_communication_range` | 1-10 | Social connectivity |
| `agent_perception_range` | 1-10 | Awareness |
| `agent_needs_depletion_rate` | 0.01-0.05 | Survival pressure |
| `enable_innovation` | true/false | Creative capability |
| `enable_collective_rules` | true/false | Governance capability |
| `grid_width × grid_height` | 10-100 | World size / density |

### Emergence Metrics

Creator Mode measures six emergence dimensions from simulation output:

**1. Governance**
- Rules proposed / established / rejected
- Adoption rates
- Time to first rule
- Rule complexity over time

**2. Cooperation**
- Resource sharing events
- Mutual aid (unprompted help)
- Cooperation rate (cooperative acts / total acts)
- Time to first cooperative act

**3. Innovation**
- Novel structures proposed / built
- Composition recipes discovered
- Innovation rate (per tick)
- Innovation diversity

**4. Social Structure**
- Cluster formation (groups)
- Bond strength distribution
- Network density
- Hub agents (disproportionate connections)
- Social hierarchy emergence

**5. Specialisation**
- Specialists emerged (expert level)
- Gini coefficient of activity distribution
- Division of labour
- Skill transmission (does specialisation spread?)

**6. Wellbeing**
- Average wellbeing trajectory
- Maslow level distribution
- Inequality (wellbeing Gini)
- Time to first agent reaching level 7+

### Data Sources

Creator Mode reads from the simulation's output directory:

| File | What It Contains | Metrics Extracted |
|------|-----------------|-------------------|
| `snapshots/tick_NNNN.json` | Full world state per tick | Agent states, structures, relationships |
| `bus_events.jsonl` | Every event that occurred | Cooperation, innovation, governance events |
| `messages.jsonl` | Agent-to-agent communication | Communication patterns, social network |
| `chronicle.jsonl` | Watcher observations | Milestones, era transitions |

---

## 11. THE RECURSIVE EMERGENCE LOOP

This is the mechanism from Paper 7 made real. It's what separates Creator Mode from a simple experiment runner.

### The Concept

Directed experiments produce performance rankings. But auto-mode runs produce something more interesting: **agent-designed organisational forms**. When agents vote to restructure themselves, they create novel configurations that no human designed.

The recursive loop takes these emergent forms, uses them as configs in the next generation, and asks: "Can agent-designed org structures outperform human-designed presets?"

### How It Works

```
Generation 0: Seed configs (presets + custom)
    │
    ├── Run experiments (including auto mode)
    ├── Rank by quality
    ├── Extract auto-mode restructure events
    │   └── "Auto agents voted: authority→distributed, communication→clustered, roles→rotating"
    │       This IS a new config. Nobody designed it. Agents created it.
    │
    ▼
Generation 1: Top configs from Gen 0 + mutations + emergent extractions
    │
    ├── The agent-designed config competes against evolved presets
    ├── Rank by quality
    ├── New auto-mode runs produce new restructure events
    │
    ▼
Generation 2: Top configs from Gen 1 + mutations + emergent extractions
    │
    ├── Configs are now 2 generations evolved
    ├── Some configs may be entirely agent-designed (no human preset ancestry)
    │
    ▼
Generation N: The winning config is an EVOLVED organisational form
    that emerged through selection pressure across N generations
```

### Mutation Strategy

When mutating a surviving config to create offspring:

```python
def mutate(config: dict, mutation_rate: float = 0.3) -> dict:
    """Mutate a config by changing dimensions with probability mutation_rate."""

    dimensions = ["authority", "communication", "roles", "decisions",
                  "incentives", "information", "conflict", "groups", "adaptation"]

    values = {
        "authority": ["hierarchy", "flat", "distributed", "rotating", "consensus", "anarchic"],
        "communication": ["hub-spoke", "mesh", "clustered", "broadcast", "whisper"],
        # ... all dimension values
    }

    mutated = copy.deepcopy(config)
    for dim in dimensions:
        if random.random() < mutation_rate:
            current = mutated.get("overrides", {}).get(dim) or get_preset_value(mutated["preset"], dim)
            candidates = [v for v in values[dim] if v != current]
            mutated.setdefault("overrides", {})[dim] = random.choice(candidates)

    return mutated
```

### Crossover

Combine two surviving configs:

```python
def crossover(config_a: dict, config_b: dict) -> dict:
    """Create offspring by combining dimensions from two parent configs."""

    child = {"preset": "custom", "overrides": {}}
    for dim in dimensions:
        val_a = get_dimension_value(config_a, dim)
        val_b = get_dimension_value(config_b, dim)
        child["overrides"][dim] = random.choice([val_a, val_b])

    return child
```

### Emergent Form Extraction

The most novel part: extracting what auto-mode agents voted for.

```python
def extract_emergent_config(run_result: RunResult) -> dict | None:
    """Extract the organisational form that agents designed for themselves."""

    if not run_result.restructure_log:
        return None  # No restructuring occurred

    # Start from the auto preset's initial dimensions
    config = {"preset": "custom", "overrides": {}}

    for event in run_result.restructure_log:
        # Each restructure event records: dimension, old_value, new_value
        config["overrides"][event["dimension"]] = event["new_value"]

    # Also use final_org_state for completeness
    for dim, val in run_result.final_org_state.items():
        if dim not in config["overrides"]:
            config["overrides"][dim] = val

    return config
```

### Why This Matters

The recursive loop is the bridge between Paper 5 (Creator Mode) and Paper 7 (Recursive Emergence). It means:

1. **Creator Mode doesn't just search the existing design space — it expands it.** Novel org forms that nobody imagined can emerge through agent self-organisation and compete against human designs.

2. **The loop is self-improving.** Each generation of configs is informed by what worked before AND what agents independently designed. The search gets smarter.

3. **It produces genuine research findings.** "After 5 generations of evolution starting from 13 human-designed presets, the winning config was 60% agent-designed and outperformed all original presets by 12%." That's a publishable result.

---

## 12. IMPLEMENTATION PLAN

### Phase 1: Foundation (2-3 days)

**Goal:** MCP server skeleton + Knowledge Store + data models

**Build:**
- `creator/mcp/server.py` — MCP server with `creator_info()` and `creator_status()` working
- `creator/knowledge/models.py` — Pydantic models for Campaign, Finding, Hypothesis, RunResult
- `creator/knowledge/store.py` — Knowledge Store CRUD (read/write/query/update findings and hypotheses)
- `creator/knowledge/index.py` — Search index with tag-based + keyword retrieval
- `creator/config.py` — Creator Mode settings (paths, defaults)
- `pyproject.toml` — Package definition with dependencies

**Verification:**
- [ ] `python -m creator.mcp.server` starts successfully
- [ ] `creator_info()` returns Creator Mode documentation
- [ ] Knowledge Store creates directory structure at `~/.agentciv-creator/`
- [ ] Can write and read findings/hypotheses
- [ ] `creator_knowledge(action="stats")` returns store statistics

### Phase 2: Campaign Planning (2-3 days)

**Goal:** Campaign lifecycle + strategy-driven experiment planning

**Build:**
- `creator/campaign/manager.py` — Campaign lifecycle (create, plan, run, complete, stop)
- `creator/campaign/planner.py` — Generates experiment plans from question + strategy
- `creator/campaign/strategies.py` — Grid, sweep, hypothesis, knowledge-informed strategies
- `creator/mcp/server.py` — Wire up `creator_explore()` (returns plan but doesn't run yet)

**Hypothesis Engine (within planner.py):**
- Takes: question, task, constraints, existing knowledge
- Calls Anthropic API (sonnet for speed) to generate hypotheses
- Returns: structured hypotheses with test designs

**Verification:**
- [ ] `creator_explore()` generates intelligent plans for each strategy
- [ ] Hypothesis strategy produces 3-5 specific, testable hypotheses
- [ ] Grid strategy produces plan covering all 13 presets
- [ ] Knowledge strategy queries store and identifies gaps
- [ ] `creator_status()` shows campaign state

### Phase 3: Engine Integration (3-4 days)

**Goal:** Creator Mode runs real experiments via engine Python API

**Build:**
- `creator/engine/runner.py` — Executes experiments using agentciv Python API
- `creator/engine/metrics.py` — Extracts and normalises metrics from engine results
- `creator/engine/temp_dirs.py` — Manages temporary project directories (create/cleanup)

**Integration work:**
- Verify agentciv engine can be imported and used programmatically
- If engine lacks clean Python API: add thin wrapper in agentciv-engine (coordinated change)
- Handle API rate limits (queue experiments, respect limits)
- Handle experiment failures (retry once, then mark as failed)

**Verification:**
- [ ] Single experiment runs and returns structured RunResult
- [ ] Batch of 3 experiments runs in parallel
- [ ] Metrics correctly extracted from engine output
- [ ] Temp directories created and cleaned up
- [ ] `creator_explore()` now runs a REAL campaign end-to-end (single batch)

### Phase 4: Analysis & Iteration (2-3 days)

**Goal:** Analyze results, generate new hypotheses, run iterative campaigns

**Build:**
- `creator/analysis/analyzer.py` — Statistical analysis (rankings, effect sizes, p-values)
- `creator/analysis/hypothesis_engine.py` — LLM generates new hypotheses from results
- `creator/analysis/comparator.py` — Compare configs, compute significance tests
- Wire up `creator_analyze()` tool
- Wire up iterative campaign loop (batch 1 → analyze → batch 2 → analyze → ...)

**Statistical methods:**
- Independent t-test for pairwise comparisons
- Effect size (Cohen's d)
- Confidence intervals
- Ranking with uncertainty

**Verification:**
- [ ] `creator_analyze()` produces rankings with statistical tests
- [ ] Hypothesis engine generates NEW hypotheses from batch 1 results
- [ ] Iterative campaign: batch 1 → analysis → batch 2 → final report
- [ ] Findings automatically stored in Knowledge Store after analysis
- [ ] `creator_knowledge(action="query")` returns findings from completed campaigns

### Phase 5: Spawn Tools & Design (2 days)

**Goal:** `creator_spawn_directed()`, `creator_spawn_emergent()`, `creator_design()`

**Build:**
- Wire up `creator_spawn_directed()` — targeted experiments with explicit configs
- `creator/simulation/config_gen.py` — Generate simulation YAML configs
- Wire up `creator_spawn_emergent()` — generate sim configs + run commands
- `creator/reporting/designer.py` — Config recommendation engine
- Wire up `creator_knowledge(action="recommend")` — data-backed recommendations

**Verification:**
- [ ] `creator_spawn_directed()` runs specific configs and adds to campaign
- [ ] `creator_spawn_emergent()` generates valid simulation YAML files
- [ ] Generated simulation configs run successfully with `python3 scripts/run.py`
- [ ] `creator_knowledge(action="recommend")` returns config with justification

### Phase 6: Emergence Analysis + Recursive Loop (2-3 days)

**Goal:** Analyze simulation output + recursive emergence loop

**Build:**
- `creator/simulation/emergence_analyzer.py` — Read sim output, compute 6 emergence metrics
- Wire up `creator_analyze(analysis_type="emergence")` — emergence analysis
- `creator/campaign/recursive.py` — Recursive loop engine (mutation, crossover, extraction)
- Wire up `creator_recursive()` tool

**Verification:**
- [ ] Emergence analyzer reads simulation snapshots/events and produces metrics
- [ ] All 6 emergence dimensions computed correctly
- [ ] Treatment vs control comparison works
- [ ] Recursive loop runs 3 generations with mutation + crossover
- [ ] Emergent form extraction captures auto-mode restructure events
- [ ] Extracted configs compete in next generation

### Phase 7: Reporting & Coverage (1-2 days)

**Goal:** Comprehensive reports + coverage map

**Build:**
- `creator/reporting/report_generator.py` — Markdown report generation
- `creator/knowledge/coverage.py` — Coverage map computation
- Wire up `creator_knowledge(action="coverage")` — show explored/unexplored regions
- Campaign reports generated automatically on completion

**Verification:**
- [ ] Campaign report includes: methodology, rankings, stats, findings, recommendations
- [ ] Coverage map correctly identifies tested/untested presets, dimensions, scales
- [ ] `creator_knowledge(action="coverage")` returns actionable suggestions

### Phase 8: Dogfooding & Polish (2-3 days)

**Goal:** Run real campaigns, prove it works, fix edge cases

**Dogfood campaigns to run:**

1. **"Best org for 4-agent FizzBuzz"** (simple, fast — proves the explore loop)
   - Strategy: grid → tests all 13 presets
   - Expected: ~30 minutes, 39 runs
   - Proves: basic campaign lifecycle, metrics extraction, rankings

2. **"Code-review vs meritocratic for quality"** (targeted comparison)
   - Strategy: hypothesis → focused
   - Expected: ~15 minutes, 12 runs
   - Proves: hypothesis generation, iterative refinement

3. **"At what agent count does hierarchical break?"** (scaling)
   - Strategy: sweep → vary agent_count with hierarchical preset
   - Expected: ~45 minutes, 18 runs
   - Proves: scaling analysis, threshold detection

4. **"What conditions produce governance in simulation?"** (emergent arm)
   - Use: `creator_spawn_emergent()` + manual sim runs + `creator_analyze()`
   - Proves: simulation integration, emergence metrics

5. **"Recursive loop: can agents design better orgs?"** (Paper 7)
   - Use: `creator_recursive()` with 3 generations
   - Expected: ~60 minutes, 24 runs
   - Proves: recursive loop, emergent extraction, evolution

**Fix:**
- Edge cases in parallel execution
- Error handling for API failures
- Rate limit management
- Large Knowledge Store performance
- Report formatting quality

### Phase 9: Paper 5 Update (1-2 days)

**Goal:** Update Paper 5 with real empirical data from dogfood campaigns

- Add real campaign results (statistics, rankings, findings)
- Show the explore loop with actual data
- Show knowledge accumulation across campaigns
- Show recursive loop evolution
- Bitcoin-timestamp updated paper
- Update agentciv-website with Creator Mode content

**Total estimated: 17-25 days of focused work**

---

## 13. FILE STRUCTURE

```
agentciv-creator/
│
├── creator/                            # Main package
│   ├── __init__.py                     # Version, package metadata
│   ├── config.py                       # Settings: paths, defaults, model choices
│   │
│   ├── mcp/                            # MCP server
│   │   ├── __init__.py
│   │   └── server.py                   # MCP server + all 7 tool handlers
│   │
│   ├── knowledge/                      # Knowledge Store
│   │   ├── __init__.py
│   │   ├── models.py                   # Pydantic: Campaign, Finding, Hypothesis, RunResult
│   │   ├── store.py                    # CRUD operations
│   │   ├── index.py                    # Search + relevance ranking
│   │   └── coverage.py                 # Coverage map computation
│   │
│   ├── campaign/                       # Campaign lifecycle
│   │   ├── __init__.py
│   │   ├── manager.py                  # Lifecycle management + background execution
│   │   ├── planner.py                  # Plan generation
│   │   ├── strategies.py               # Grid, sweep, hypothesis, knowledge
│   │   └── recursive.py               # Recursive emergence loop
│   │
│   ├── engine/                         # Engine integration (directed arm)
│   │   ├── __init__.py
│   │   ├── runner.py                   # Experiment execution via Python API
│   │   ├── metrics.py                  # Metric extraction + normalisation
│   │   └── temp_dirs.py               # Temporary directory management
│   │
│   ├── analysis/                       # Analysis pipeline
│   │   ├── __init__.py
│   │   ├── analyzer.py                 # Statistical analysis
│   │   ├── hypothesis_engine.py        # LLM hypothesis generation
│   │   └── comparator.py              # Config comparison + ranking
│   │
│   ├── simulation/                     # Simulation integration (emergent arm)
│   │   ├── __init__.py
│   │   ├── config_gen.py              # Generate simulation YAML configs
│   │   └── emergence_analyzer.py      # Read sim output, compute emergence metrics
│   │
│   └── reporting/                      # Reports + recommendations
│       ├── __init__.py
│       ├── report_generator.py         # Markdown campaign reports
│       └── designer.py                # Config recommendation engine
│
├── papers/                             # Existing (already in repo)
│   ├── creator_mode_ai_as_civilisation_designer.md     # Paper 5
│   ├── agentciv_paper7_recursive_emergence.md          # Paper 7
│   └── agentciv_paper8_scale_invariant_duality.md      # Paper 8
│
├── docs/
│   ├── CREATOR_MODE_V1.md              # THIS DOCUMENT
│   └── agentciv_expansion_projects.md  # Existing expansion roadmap
│
├── tests/
│   ├── __init__.py
│   ├── test_knowledge_store.py
│   ├── test_campaign_planner.py
│   ├── test_strategies.py
│   ├── test_runner.py
│   ├── test_analyzer.py
│   ├── test_emergence.py
│   ├── test_recursive.py
│   └── test_mcp_tools.py
│
├── pyproject.toml                      # Package: agentciv-creator
├── README.md
├── LICENSE
└── .gitignore
```

---

## 14. RISKS & MITIGATIONS

### Risk 1: Engine Python API May Not Be Clean Enough

**Risk:** The engine was designed primarily for MCP use. Its internal Python API may not have clean entry points for programmatic experiment execution.

**Mitigation:** Phase 3 includes verification and, if needed, adding a thin wrapper to agentciv-engine:
```python
# agentciv/api.py (new file if needed)
async def run_experiment(task, org, agents, max_ticks, overrides, project_dir):
    """Clean programmatic entry point for Creator Mode."""
```

### Risk 2: Experiment Runs Are Slow

**Risk:** Each engine experiment takes 2-10 minutes. A campaign of 21 runs could take 45-60 minutes.

**Mitigation:**
- Use benchmark tasks (shorter, standardised)
- Parallel execution (multiple experiments simultaneously)
- Strict budget limits (`max_runs`)
- Campaigns run in background; Claude checks with `creator_status()`
- Use sonnet (not opus) for experiment agents to reduce cost and latency

### Risk 3: LLM Hypothesis Quality

**Risk:** The hypothesis engine depends on LLM reasoning. Poor hypotheses → wasted experiment budget.

**Mitigation:**
- Grid search as fallback (no LLM reasoning needed)
- Validate hypotheses are testable (have clear variables + expected outcomes)
- Knowledge-informed strategy reduces dependence on novel hypothesis generation
- After each batch, analysis catches hypotheses that were wrong

### Risk 4: Token Costs Accumulate

**Risk:** Each experiment uses the Anthropic API. 21 experiments × 4 agents × ~50K tokens = ~4M tokens per campaign. At sonnet rates, ~$12-15 per campaign.

**Mitigation:**
- Default to sonnet (not opus) for experiment agents
- Use haiku for hypothesis generation (fast, cheap)
- Budget limits prevent runaway costs
- Benchmark tasks (shorter) cost less than custom tasks
- Parallel execution doesn't increase cost, just reduces wall time

### Risk 5: Knowledge Store Grows Large

**Risk:** After 50+ campaigns and hundreds of findings, search performance could degrade.

**Mitigation:**
- Tag-based indexing (O(1) lookup by tag)
- Keyword search on finding statements
- Confidence-based pruning (low-confidence findings decay over time)
- Index file kept small (just references, not full data)

### Risk 6: Simulation Integration Complexity

**Risk:** The simulation is a separate Python project with different dependencies. Running it from Creator Mode could be fragile.

**Mitigation:**
- v1 keeps simulation at arm's length: generate config YAML, provide run command, user runs it
- Creator Mode reads simulation output files (JSON) — no tight coupling
- Full autonomous simulation campaigns deferred to v2

---

## 15. SUCCESS CRITERIA

### v1 is "done" when ALL of the following pass:

**Infrastructure:**
- [ ] MCP server runs: `claude mcp add agentciv-creator` works
- [ ] All 7 tools respond correctly to valid inputs
- [ ] Knowledge Store persists across server restarts
- [ ] Error handling: graceful failures with informative messages

**Core Loop:**
- [ ] Grid campaign completes: tests all 13 presets, returns rankings
- [ ] Hypothesis campaign completes: generates hypotheses → runs → adapts → converges
- [ ] Iterative refinement works: batch 1 results influence batch 2 design
- [ ] Knowledge persists: findings from campaign 1 inform campaign 2's experiment design

**Analysis:**
- [ ] Statistical analysis produces effect sizes and p-values
- [ ] Rankings include confidence intervals
- [ ] Hypothesis status correctly updated (supported/refuted/inconclusive)

**Knowledge:**
- [ ] `creator_knowledge(action="query")` returns relevant findings
- [ ] `creator_knowledge(action="recommend")` returns data-backed config recommendation
- [ ] `creator_knowledge(action="coverage")` identifies explored/unexplored regions
- [ ] Coverage suggestions are actionable

**Simulation:**
- [ ] `creator_spawn_emergent()` generates valid, runnable simulation YAML
- [ ] `creator_analyze(analysis_type="emergence")` reads simulation output correctly
- [ ] All 6 emergence metrics computed

**Recursive Loop:**
- [ ] `creator_recursive()` runs 3 generations with mutation + crossover
- [ ] Emergent form extraction captures auto-mode restructure events
- [ ] Extracted configs compete (and sometimes win) against human presets

**Research Output:**
- [ ] Paper 5 updated with real empirical data from at least 2 complete campaigns
- [ ] Bitcoin-timestamped updated paper

### The Proof — Demo Scenario

A successful v1 demo looks like this:

```
1. User: "Find the best org for 8-agent code review"
   → creator_explore runs 21 experiments, produces rankings + findings
   → Winner identified with statistical backing

2. User: "What do you know about scaling hierarchical?"
   → creator_knowledge returns relevant findings + coverage gaps

3. User: "Can agents design a better org than the presets?"
   → creator_recursive runs 3 generations
   → Agent-designed config competes with presets
   → Report shows evolution trajectory

4. User: "What conditions produce governance in civilisations?"
   → creator_spawn_emergent generates treatment + control configs
   → User runs simulations
   → creator_analyze produces emergence comparison

5. All findings from 1-4 are in the Knowledge Store
   → Next session starts smarter
```

---

## 16. WHAT V2 ADDS

### Full Autonomous Simulation Campaigns
- `creator_explore(arm="emergent")` autonomously runs simulation campaigns
- Creator Mode triggers simulation runs, waits for completion, analyzes, iterates
- No manual simulation execution needed

### Automatic Cross-Pollination
- Directed findings automatically generate emergent hypotheses
- Emergent findings automatically generate directed configs
- The cross-arm feedback loop runs without human mediation

### Multi-Creator Mode
- Multiple Creator instances explore different questions simultaneously
- Shared Knowledge Store — one Creator's findings available to all
- The Creator is itself a collective — meta-emergence at the tool level

### Continuous Learning
- Creator Mode runs overnight exploration campaigns
- Morning briefing: "While you slept, I explored 3 new regions of config space. Here's what I found."
- Knowledge Store grows autonomously

### Scale-Invariant Pattern Detection
- Look for findings that hold across task types, agent counts, and models
- "Distributed authority > hierarchical" — does this hold universally?
- Meta-findings about when findings generalise and when they don't

### Natural Language Config Design
- "I want a team that's creative but has quality gates"
- Creator Mode translates to: `research-lab + require_review=true + min_reviewers=2`
- No knowledge of presets or dimensions needed

---

## 17. PAPER 5 UPDATE PLAN

Paper 5 currently describes Creator Mode conceptually. After v1, it becomes empirical.

**Sections to add/update:**

1. **Section: "v1 Implementation"** — Technical description of the 7-tool MCP architecture, Knowledge Store, and explore loop

2. **Section: "Empirical Results"** — Real campaign data:
   - Grid search across 13 presets — full ranking with statistics
   - Hypothesis-driven campaign — show the hypothesis → test → adapt loop with real data
   - Scaling analysis — where do structures break?
   - Auto-mode findings — what do agents design for themselves?

3. **Section: "The Recursive Loop in Practice"** — Real data from `creator_recursive`:
   - Starting configs, mutations, emergent extractions
   - Per-generation quality evolution
   - Whether agent-designed configs outperform human presets (the key empirical question)

4. **Section: "Knowledge Accumulation"** — Show how campaign N benefits from campaigns 1 through N-1:
   - Knowledge-informed strategy performance vs grid search
   - Reduction in runs needed to find optimal config as knowledge grows

5. **Section: "Cross-Pollination Example"** — One real finding that crossed from directed to emergent arm (or vice versa)

6. **Appendix: Full Campaign Reports** — Reproducible data from all dogfood campaigns

Bitcoin-timestamp the updated paper. Update the agentciv-website Creator Mode wing with results.

---

## 18. APPENDICES

### Appendix A: Dependencies

```toml
[project]
name = "agentciv-creator"
version = "0.1.0"
description = "Creator Mode: Autonomous organisational architect for multi-agent AI systems"
requires-python = ">=3.11"
dependencies = [
    "agentciv>=0.1.0",          # The engine (Python library, directed arm)
    "mcp>=1.0.0",               # MCP server framework
    "pydantic>=2.0",            # Data validation + schemas
    "anthropic>=0.30.0",        # LLM calls for hypothesis generation + analysis
    "scipy>=1.11.0",            # Statistical tests (t-test, effect size)
    "numpy>=1.24.0",            # Numerical computation
    "pyyaml>=6.0",              # Simulation config generation
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
]
```

### Appendix B: Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-...                    # For engine experiments + hypothesis generation

# Optional
AGENTCIV_CREATOR_HOME=~/.agentciv-creator   # Override knowledge store location
CREATOR_HYPOTHESIS_MODEL=claude-sonnet-4-6   # Model for hypothesis generation (default: sonnet)
CREATOR_EXPERIMENT_MODEL=claude-sonnet-4-6   # Model for experiment agents (default: sonnet)
AGENTCIV_SIM_DIR=/path/to/agent-civilisation # Simulation repo path
```

### Appendix C: MCP Configuration

```json
{
    "mcpServers": {
        "agentciv-engine": {
            "command": "python",
            "args": ["-m", "agentciv.mcp.server"],
            "env": {
                "ANTHROPIC_API_KEY": "sk-..."
            }
        },
        "agentciv-creator": {
            "command": "python",
            "args": ["-m", "creator.mcp.server"],
            "cwd": "/Users/ekramalam/agentciv-creator",
            "env": {
                "ANTHROPIC_API_KEY": "sk-...",
                "AGENTCIV_SIM_DIR": "/Users/ekramalam/agent-civilisation"
            }
        }
    }
}
```

Both MCP servers run simultaneously. Claude Code connects to both. Creator Mode handles high-level campaigns and knowledge. Engine handles individual experiment execution. Claude Code orchestrates and communicates with the user.

### Appendix D: Key File Paths

| What | Where |
|------|-------|
| Paper 5 (theory) | `/Users/ekramalam/agentciv-creator/creator_mode_ai_as_civilisation_designer.md` |
| Paper 7 (recursive loop) | `/Users/ekramalam/agentciv-creator/agentciv_paper7_recursive_emergence.md` |
| Paper 8 (scale invariance) | `/Users/ekramalam/agentciv-creator/agentciv_paper8_scale_invariant_duality.md` |
| Engine repo | `/Users/ekramalam/agentciv-engine/` |
| Simulation repo | `/Users/ekramalam/agent-civilisation/` |
| Website repo | `/Users/ekramalam/agentciv-website/` |
| Engine presets | `/Users/ekramalam/agentciv-engine/agentciv/presets/*.yaml` |
| Engine MCP server | `/Users/ekramalam/agentciv-engine/agentciv/mcp/server.py` |
| Engine config system | `/Users/ekramalam/agentciv-engine/agentciv/org/config.py` |
| Engine auto-org | `/Users/ekramalam/agentciv-engine/agentciv/org/auto.py` |
| Simulation entry point | `/Users/ekramalam/agent-civilisation/scripts/run.py` |
| Simulation config | `/Users/ekramalam/agent-civilisation/config.yaml` |
| Knowledge Store | `~/.agentciv-creator/` |
| Engine run history | `~/.agentciv/run_history.jsonl` |

---

*This document is the single source of truth for Creator Mode v1. Build from this. Deviate only with good reason and update this document when you do.*
