# Stage 2: Creator Mode — Complete Plan

**Created:** 8 April 2026
**Status:** Planning
**Outcome:** Creator Mode v1 shipped + Paper 5 upgraded + Website wing built

This document is the single source of truth for everything in Stage 2.

---

## Stage 2 has THREE deliverables

| Deliverable | What it is | Where it ships |
|-------------|-----------|---------------|
| **A. Creator Mode v1 Build** | Working code — dual-mode, HYBRID, compounding knowledge | `agentciv-creator` + `agent-civilisation` repos |
| **B. Paper 5 Upgrade** | Academic paper documenting v1 + formal contributions + v2+ vision | `agentciv-creator` repo |
| **C. Website Wing** | Creator Mode section on agentciv.ai | `agentciv-website` repo |

---

# A. CREATOR MODE v1 BUILD

## What v1 IS

Creator Mode is a **meta-intelligence whose reasoning steps are sub-module executions**.

Standard AI reasons in tokens: `LLM(prompt) → tokens → response`.

Creator Mode reasons in civilisations and teams: `CreatorMode(goal) → [spawns civilisations, spawns teams, analyses emergence, extracts patterns, tests hypotheses] → optimised configuration + accumulated knowledge`.

Each "thought" is not a line of text — it is an entire simulation of an AI civilisation or an entire team solving a task. Its memory is a persistent Knowledge Store where every run's findings compound. Its improvement is not retraining — it is empirical knowledge that makes every subsequent campaign more targeted.

This is a qualitatively new form of directed intelligence. It is general across the combined possibility space of both products (~280+ parameters, 26+ presets, thousands of possible configurations). Given any objective — "find the team structure that produces the best API" or "find the conditions that produce the richest self-governance" — it explores, learns, and converges.

## What's already built (v1 foundation)

| Component | Status | What it does |
|-----------|--------|-------------|
| Campaign Manager | ✅ Built | Multi-run experiment orchestration |
| Knowledge Store | ✅ Built | Persistent findings, recommendations, coverage maps |
| Hypothesis Engine | ✅ Built | Generates testable claims from accumulated knowledge |
| `creator_explore` | ✅ Built | Full autonomous research campaign |
| `creator_spawn_directed` | ✅ Built | Targeted engine experiment |
| `creator_analyze` | ✅ Built | Cross-run pattern detection |
| `creator_knowledge` | ✅ Built | Knowledge query, recommend, coverage |
| `creator_status` | ✅ Built | Dashboard + campaign management |
| Engine runner | ✅ Built | Batch execution of engine configs |
| TASK campaign mode | ✅ Built | Directs Engine toward task objectives |
| Dogfood (engine mode) | ✅ Done | 3 campaigns, 14 runs, $83.53 |
| Simulation packaging | ✅ Done | PyPI v0.2.0, CLI, 13 presets, 11 MCP tools |

## What v1 still needs (the build)

### Phase 1: Simulation Structured Metrics (~200 lines)
**Repo:** `agent-civilisation`

| File | What |
|------|------|
| `src/metrics/emergence.py` | EmergenceScore dataclass — 16 quantified metrics + composite score (0-1) |
| `src/metrics/run_record.py` | SimulationRunRecord — structured output (config, ticks, tokens, emergence, milestones, agent summaries) |
| `src/metrics/__init__.py` | Package init |
| `scripts/run.py` (edit) | Wire `--metrics` to print EmergenceScore, `--output` to export RunRecord JSON |

### Phase 2: Simulation Experiment Commands (~400 lines)
**Repo:** `agent-civilisation`

| File | What |
|------|------|
| `agentciv_sim/cli.py` (edit) | `experiment` command — run N presets × M runs, compare EmergenceScores |
| `agentciv_sim/cli.py` (edit) | `compare` command — side-by-side metric comparison from JSON exports |
| `src/mcp/server.py` (edit) | Wire EmergenceScore into MCP tool responses |
| `README.md` (edit) | Document structured metrics + experiment mode |

### Phase 3: Creator Mode Simulation Integration (~300 lines)
**Repo:** `agentciv-creator`

| File | What |
|------|------|
| `creator/simulation/__init__.py` | Package init |
| `creator/simulation/runner.py` | Simulation batch runner — takes list of SimulationRunConfig, returns structured results |
| `creator/simulation/metrics.py` | EmergenceScore → Creator Mode analysis pipeline (weighting, statistical comparison) |
| `creator/campaign/manager.py` (edit) | EMERGENCE campaign mode — planner generates sim configs, runner executes, analyzer compares |
| `creator/campaign/planner.py` (edit) | EMERGENCE hypothesis templates |

### Phase 4: HYBRID Mode (~300 lines)
**Repo:** `agentciv-creator`

| File | What |
|------|------|
| `creator/simulation/translator.py` | Emergence → Engine translator — reads simulation chronicle, maps emergent patterns to engine org dimensions, produces engine config overrides |
| `creator/campaign/manager.py` (edit) | HYBRID campaign mode — Sim experiments → extract patterns → encode as Engine configs → run Engine experiments → compare → store cross-mode findings |
| `creator/campaign/planner.py` (edit) | HYBRID hypothesis templates ("Does the pattern that emerged under X improve performance on task Y?") |

### Phase 5: Cross-Mode Knowledge (~100 lines)
**Repo:** `agentciv-creator`

| File | What |
|------|------|
| `creator/knowledge/models.py` (edit) | CampaignMode enum (TASK/EMERGENCE/HYBRID), sim result types |
| `creator/knowledge/store.py` (edit) | Mode-tagged findings, cross-mode retrieval, unified coverage map across both parameter spaces |
| `creator/mcp/server.py` (edit) | `mode` parameter on all creator tools |

### Phase 6: Dogfood Validation ($20-40)

| Test | What it proves | Cost |
|------|---------------|------|
| EMERGENCE mode | Creator Mode designs, runs, analyses simulation experiments autonomously | $10-20 |
| HYBRID mode | Full Sim → extract pattern → Engine config → test pipeline works | $10-20 |
| Cross-mode knowledge | Knowledge Store retrieves sim findings for engine hypotheses and vice versa | Included above |

### Build Summary

| | Lines | Repo |
|---|-------|------|
| Phase 1 | ~200 | agent-civilisation |
| Phase 2 | ~400 | agent-civilisation |
| Phase 3 | ~300 | agentciv-creator |
| Phase 4 | ~300 | agentciv-creator |
| Phase 5 | ~100 | agentciv-creator |
| **Total code** | **~1,300** | |
| **Total cost** | **$20-40** | dogfood |

---

# B. PAPER 5 UPGRADE

"Creator Mode: AI as Civilisation Designer" — upgraded from engine-only to full dual-mode + formal contributions.

## Paper sections

### Section 1: What Creator Mode Is (CORE — the novel reasoning concept)

**Title:** "Sub-Module Reasoning: A Meta-Intelligence Architecture"

Creator Mode introduces a qualitatively new form of AI reasoning. In standard AI, the reasoning unit is token generation — a language model produces sequences of tokens to solve problems. In Creator Mode, the reasoning unit is **sub-module execution** — the meta-intelligence spawns entire AI civilisations or AI teams as its "reasoning steps," analyses their emergent behaviour, extracts structural insights, and uses those insights to inform the next reasoning step.

This section formalises:
- **Definition:** Sub-module reasoning — a reasoning architecture in which each cognitive step is the execution of an autonomous sub-system (simulation, engine, or any future sub-module), with the meta-intelligence operating over the outputs of those sub-systems rather than over tokens directly.
- **The Knowledge Store as episodic memory** — each sub-module execution produces structured findings that compound. The meta-intelligence's "understanding" grows with each execution, not through parameter updates but through accumulated empirical knowledge.
- **Convergence dynamics** — given a directed objective, the meta-intelligence explores the possibility space through sub-module executions and converges on optimal configurations. The hypothesis engine ensures exploration is directed rather than random. The Knowledge Store ensures no ground is re-covered.
- **Generality** — the architecture is general across any set of sub-modules. v1 uses Engine + Simulation. The architecture imposes no limit on what sub-modules can be added. Each new sub-module expands the reasoning capacity of the meta-intelligence.

### Section 2: Dual-Mode Architecture (what v1 does)

- TASK mode: Creator Mode directs Engine toward task objectives
- EMERGENCE mode: Creator Mode directs Simulation toward emergence objectives
- Full-spectrum parameter access: any configuration either product accepts
- Compounding Knowledge Store across both modes

### Section 3: HYBRID Mode (novel contribution)

- The Emergence → Engine translation pipeline
- Emergent patterns extracted from simulation chronicles
- Patterns mapped to engine organisational dimensions
- Tested against human-designed presets on real tasks
- The question this answers: "Do organisational structures that emerge outperform ones that humans design?"

### Section 4: The Bigger Picture — Scaled-Up Reasoning

**Title:** "From Token Reasoning to Reality Reasoning"

The implications of sub-module reasoning at scale:

- **v1 reasoning steps** = simulations of 5-100 agents over 20-200 ticks. Already qualitatively different from token reasoning.
- **Scaled reasoning steps** = entire simulated realities with hundreds or thousands of AI agents forming complex societies over thousands of ticks. Each "thought" is a full civilisation lifecycle.
- **What this enables:**
  - Spawning entire simulated realities to reason about social dynamics, organisational structure, governance, cooperation, competition
  - Using those simulated realities to generate genuine knowledge and understanding (not just pattern-matched text)
  - Societies of AIs or emergent AIs producing insights that no single reasoning chain could reach
  - Optimisation toward directed tasks using civilisation-scale empirical evidence
- **The progression:** Token reasoning → tool-use reasoning → agent reasoning → **civilisation reasoning** (sub-module execution where the sub-module is an entire society of autonomous agents)
- **Why this matters:** This is not just "running simulations." It is a meta-intelligence whose cognitive substrate is populations of agents. Its "thoughts" have the richness, complexity, and emergent properties of social systems. It can reason about things that token-level reasoning cannot — because some truths only emerge from the interaction of many agents over time.

### Section 5: The Recursive Triad (formal contribution)

**Title:** "The Recursive Triad: Self-Reproducing Meta-Architecture"

**5a. Definition**

The fundamental recursive unit is the **triad**: meta-intelligence (Creator Mode) + task-solver (Engine) + civilisation-grower (Simulation). This triad is self-reproducing because:

1. Engine spawns agents. Those agents can be Creator Mode agents.
2. Simulation spawns agents. Those agents can be Creator Mode agents.
3. Creator Mode directs Engine + Simulation → which spawn Creator Mode agents → which direct their own Engine + Simulation → ...

**5b. Formal structure**

```
Triad(k) = { CreatorMode(k), Engine(k), Simulation(k) }

Engine(k).agents     ⊇ { CreatorMode(k+1) }
Simulation(k).agents ⊇ { CreatorMode(k+1) }
CreatorMode(k+1)     → Triad(k+1)
```

The triad at level k produces agents at level k+1 that instantiate the full triad at level k+1. The recursion is structural: the architecture reproduces itself.

**5c. Alam's Razor analysis**

Per Alam's Razor (Mala, 2026):
- Triad(0) functions without Triad(1). A single Creator Mode directing Engine + Simulation is complete.
- Triad(1) improves Triad(0) by expanding research capacity.
- Each level improves the level below without being required by it.
- Therefore: **improvement-only recursion**. Coherent at any depth. Unbounded.
- Capping at any level (v1 = depth 0, v3 = depth 2) is a practical choice, not a logical necessity.

**5d. RCI connection**

The triad satisfies RCI's symmetry-preserving composition:
- Interface: goal → findings (same at every level)
- The composed entity (a triad) has the same interface as its components (a Creator Mode)
- Therefore: unbounded hierarchical composition per Theorem 1 (Unbounded Composition)

**5e. The Recursion-Activating AI**

The deepest extension: an AI whose purpose is to propagate the recursion itself. It detects when a new triad level would be beneficial and spawns it. This is The Colony's Intelligence System applied to the recursive triad — autonomous determination of when and how to extend the recursion.

This is a genuinely novel concept distinct from:
- Standard RSI (one system improving itself)
- The Colony (populations evolving under meta-evolutionary selection)
- RCI (symmetry-preserving composition enabling unbounded construction)
- **The Recursive Triad** adds: an entire meta-architecture (meta-intelligence + task-solver + civilisation-grower) reproducing itself at every level, with an activating intelligence that propagates the recursion

### Section 6: Empirical Results

- Dogfood data from TASK, EMERGENCE, and HYBRID campaigns
- Knowledge Store compounding demonstrated
- Cross-mode findings demonstrated

### Section 7: Related Work

- AutoML / NAS (fixed search space, no civilisation-scale reasoning)
- Multi-agent LLM systems (AutoGPT, CrewAI — no meta-intelligence, no knowledge accumulation, no recursive architecture)
- Schmidhuber's Gödel Machine (single self-modifying system, not recursive triad)
- The Colony + RCI (Mala, 2026) — Creator Mode as implementation of both

### Section 8: Limitations and Future Work

- v1 is depth 0 (single Creator Mode). v2+ extends the recursion.
- Computational cost scales with sub-module execution cost
- Knowledge Store is local (v2: federated across instances)
- Honest about what v1 is and isn't

---

# C. WEBSITE — CREATOR MODE WING

## Page structure

### Page 1: Creator Mode Landing

**Hero section:**
> "An intelligence that reasons in civilisations."
>
> Creator Mode doesn't generate text. It spawns AI civilisations and AI teams, watches what emerges, extracts the patterns, and uses them. Each "thought" is an entire society of autonomous agents. Each run makes the next smarter.

**What it does (v1 product):**
- Three modes: TASK (directed), EMERGENCE (emergent), HYBRID (cross-product)
- Full-spectrum access to 280+ parameters across Engine + Simulation
- Compounding Knowledge Store — every run informs the next
- Autonomous hypothesis generation and experiment design
- Real dogfood results

**The novel reasoning concept:**
- Sub-module reasoning: cognitive steps are sub-module executions, not token generation
- Token reasoning → tool reasoning → agent reasoning → **civilisation reasoning**
- A meta-intelligence whose cognitive substrate is populations of agents

### Page 2: How It Works

- Architecture diagram: Creator Mode → Engine + Simulation
- Three campaign modes explained with examples
- HYBRID mode deep dive: Sim → extract → encode → Engine → compare
- Knowledge Store: how findings compound
- Hypothesis engine: how it designs experiments

### Page 3: The Bigger Picture — Scaled Reasoning

- What sub-module reasoning means at scale
- Spawning entire simulated realities as reasoning steps
- Societies of AIs generating knowledge no single model could
- Civilisation-scale empirical evidence for directed optimisation
- "When Creator Mode's reasoning steps are civilisations of thousands of agents, its cognitive capacity is qualitatively different from any token-based system."

### Page 4: The Recursive Triad (Vision)

**Clearly marked as architectural trajectory, not v1 feature.**

- The triad as the recursive unit (diagram)
- v1 → v2 → v3 → v4 → v∞ progression
- v2: Creator Mode Civilisation (multiple specialised instances)
- v3: Recursive Triad (Engine/Sim agents ARE Creator Modes)
- v4: Recursion-Activating AI (autonomous propagation)
- v∞: Unbounded (Alam's Razor: improvement-only)
- Connection to Colony + RCI papers
- "v1 is the foundation. The recursive architecture is designed into every interface."

### Page 5: Suggested Experiments

- Four-Phase Autonomous Discovery Protocol
- 13 presets × 3 runs, hypothesis-driven, recursive evolution, transfer test
- Budget estimates ($200-761)
- What users can discover by running Creator Mode themselves
- Framed as a guide, not results we claim

### Page 6: Paper 5

- Full paper embedded/linked
- Key sections highlighted

---

# COMPLETE CHECKLIST

## v1 Build — is everything covered?

| Item | In build plan | Phase |
|------|:---:|:---:|
| EmergenceScore (16 metrics + composite) | ✅ | 1 |
| SimulationRunRecord (structured output) | ✅ | 1 |
| `--metrics` and `--output` CLI flags | ✅ | 1 |
| `experiment` command (multi-preset comparison) | ✅ | 2 |
| `compare` command (JSON metric comparison) | ✅ | 2 |
| MCP tools return emergence metrics | ✅ | 2 |
| Simulation runner in Creator Mode | ✅ | 3 |
| EMERGENCE campaign mode | ✅ | 3 |
| Emergence hypothesis templates | ✅ | 3 |
| Emergence → Engine translator | ✅ | 4 |
| HYBRID campaign mode | ✅ | 4 |
| HYBRID hypothesis templates | ✅ | 4 |
| CampaignMode enum (TASK/EMERGENCE/HYBRID) | ✅ | 5 |
| Cross-mode Knowledge Store retrieval | ✅ | 5 |
| Unified coverage map (both parameter spaces) | ✅ | 5 |
| `mode` parameter on all MCP tools | ✅ | 5 |
| Dogfood EMERGENCE mode | ✅ | 6 |
| Dogfood HYBRID mode | ✅ | 6 |
| Dogfood cross-mode knowledge | ✅ | 6 |

## Paper 5 — is everything covered?

| Item | In paper plan | Section |
|------|:---:|:---:|
| Sub-module reasoning as novel concept | ✅ | 1 |
| Knowledge Store as episodic memory | ✅ | 1 |
| Convergence dynamics | ✅ | 1 |
| Generality across sub-modules | ✅ | 1 |
| Dual-mode architecture (TASK + EMERGENCE) | ✅ | 2 |
| Full-spectrum parameter access | ✅ | 2 |
| HYBRID mode (novel contribution) | ✅ | 3 |
| Emergence → Engine translation | ✅ | 3 |
| Scaled reasoning (civilisation-scale "thoughts") | ✅ | 4 |
| Token → tool → agent → civilisation reasoning progression | ✅ | 4 |
| Societies of AIs generating knowledge | ✅ | 4 |
| Recursive Triad definition | ✅ | 5a |
| Formal structure (Triad(k) notation) | ✅ | 5b |
| Alam's Razor analysis (improvement-only) | ✅ | 5c |
| RCI symmetry-preservation analysis | ✅ | 5d |
| Recursion-Activating AI | ✅ | 5e |
| Empirical results from dogfood | ✅ | 6 |
| Related work (AutoML, multi-agent LLM, Gödel Machine) | ✅ | 7 |
| Limitations and v2+ future work | ✅ | 8 |

## Website — is everything covered?

| Item | In website plan | Page |
|------|:---:|:---:|
| Hero: "intelligence that reasons in civilisations" | ✅ | 1 |
| v1 product: three modes, full-spectrum, knowledge | ✅ | 1 |
| Sub-module reasoning concept | ✅ | 1 |
| Architecture diagram | ✅ | 2 |
| Three campaign modes explained | ✅ | 2 |
| HYBRID mode deep dive | ✅ | 2 |
| Knowledge Store compounding | ✅ | 2 |
| Bigger picture: scaled reasoning | ✅ | 3 |
| Spawning realities as reasoning steps | ✅ | 3 |
| Societies of AIs generating knowledge | ✅ | 3 |
| Civilisation reasoning progression | ✅ | 3 |
| Recursive Triad (v2+ vision, clearly marked) | ✅ | 4 |
| v1→v2→v3→v4→v∞ progression diagram | ✅ | 4 |
| Alam's Razor connection (accessible) | ✅ | 4 |
| Colony + RCI paper connections | ✅ | 4 |
| Suggested Experiments guide | ✅ | 5 |
| Four-Phase protocol with budgets | ✅ | 5 |
| Paper 5 embedded/linked | ✅ | 6 |

---

# IMPLEMENTATION ORDER

```
Step 1:  Simulation metrics (Phase 1)                 ← agent-civilisation repo
         ~200 lines. Foundation for everything.

Step 2:  Simulation experiment commands (Phase 2)      ← agent-civilisation repo
         ~400 lines. Wires metrics into CLI/MCP.

Step 3:  Creator Mode sim runner + EMERGENCE (Phase 3) ← agentciv-creator repo
         ~300 lines. Creator Mode can now direct simulations.

Step 4:  HYBRID mode + translator (Phase 4)            ← agentciv-creator repo
         ~300 lines. The world-first capability.

Step 5:  Cross-mode knowledge + MCP (Phase 5)          ← agentciv-creator repo
         ~100 lines. Ties everything together.

Step 6:  Dogfood all three modes (Phase 6)             ← run experiments
         $20-40. Proves the full pipeline. Generates data for paper + website.

Step 7:  Paper 5 upgrade                               ← agentciv-creator repo
         All 8 sections. Uses dogfood data.

Step 8:  Website Creator Mode wing                     ← agentciv-website repo
         6 pages. Uses dogfood data + paper content.

Step 9:  Commit, Bitcoin stamp, deploy all repos
```

**Total: ~1,300 lines of code + $20-40 dogfood + paper + 6 website pages**
