# CREATOR MODE V1 — THE BUILD

> **The single source of truth for what v1 is, what's built, and what remains.**
> If my memory gets wiped, read this document. Everything is here.
>
> **Created:** 8 April 2026
> **Status:** Building
> **Repos:** `agentciv-creator` (primary), `agent-civilisation` (simulation metrics)
> **Papers:** Paper 5 ("Creator Mode: AI as Civilisation Designer"), Paper 5b ("The Creator Mode Architecture")
> **Product Bible:** `docs/CREATOR_MODE_V1.md` (full spec, 800+ lines — reference for tool signatures, data models, etc.)

---

## THE IDENTITY

**Slogan:** AI that autonomously spawns civilisations.

Creator Mode is a **meta-intelligence that sits above two sub-modules** — Engine (directed AI collectives) and Simulation (emergent AI civilisations) — and uses both as instruments of exploration and reasoning.

It is not a wrapper. It is not an experiment runner. It is an intelligence whose "reasoning steps" are entire civilisations and teams.

---

## ARCHITECTURAL PRINCIPLES

### 1. Frontier AI is the intelligence layer

Creator Mode uses the **best-in-class frontier AI** as its intelligence substrate. It does not build its own LLM. It sits above frontier models and leverages them.

In practice: **Claude Code IS the Creator's brain.** The Creator Mode MCP server provides Claude with 7 specialised tools (explore, spawn, analyze, knowledge, etc.). Claude's general reasoning + these domain tools = the meta-intelligence from the papers. The novel contribution is the architecture — the meta-intelligence layer, the Knowledge Store, the campaign loop, the emergence→engine translation — not the base model.

This is the same principle as Gnosis: we use what's world-class (frontier AI reasoning) and build what doesn't exist yet (civilisation-designing meta-intelligence) on top of it.

**What this means for v1:** Claude (or any frontier model) provides the reasoning. Creator Mode provides the tools, knowledge, and orchestration that turn that reasoning into civilisation-level exploration and directed meta-intelligence. As frontier models improve, Creator Mode automatically becomes more capable — better hypothesis generation, better analysis, better meta-reasoning about which sub-modules to use.

### 2. Deep logging — log EVERYTHING

Every operation Creator Mode performs is comprehensively logged. Not just outcomes — the full generative dynamics: what configurations produced what outcomes under what conditions. This maps to Layer 2 (Deep Logging) of the Architecture Paper.

In v1, this means:
- **Per-run:** Full config snapshot (every parameter, not just overrides), EmergenceScore (16 metrics), RunRecord (config + ticks + tokens + milestones + agent summaries), chronicle path
- **Per-campaign:** Strategy used, hypotheses generated, hypotheses resolved, findings extracted, cost, duration, coverage regions explored
- **Per-finding:** Confidence level, evidence runs, conditions, mode tag (TASK/EMERGENCE/HYBRID), relationships to other findings
- **Cumulative:** Coverage map (what's explored, what's terra incognita), Knowledge Store index, cross-mode retrieval index

Nothing is discarded. Everything compounds. The log IS the knowledge base.

### 3. Knowledge informs every decision

The Knowledge Store is not passive storage — it actively informs every action Creator Mode takes:
- **Before a campaign starts:** Knowledge Store is consulted for relevant prior findings, existing coverage, and untested hypotheses
- **During hypothesis generation:** Prior findings shape what hypotheses are generated (no re-testing known ground)
- **During meta-reasoning:** Knowledge density in each mode determines which sub-module to use
- **During analysis:** New findings are compared against existing findings for consistency, contradiction, or extension
- **During reporting:** Results contextualised against accumulated knowledge

Every decision is knowledge-informed. Later campaigns are sharper because earlier campaigns built the knowledge base.

### 4. Creator Mode explores the COMBINED possibility space of both tools

Not Engine OR Simulation. The combined space: Engine (~100 config options, 13 presets, 9 org dimensions) + Simulation (~180 parameters, 13+ presets, any agent count, any grid, any tick count) = ~280+ parameters, 26+ presets, thousands of configurations. And the HYBRID mode creates a third dimension: the cross-product space where emergent patterns from Simulation become Engine configurations.

The website must show this combined possibility space visually — the visitor sees the full scope of what Creator Mode can explore.

---

## THE FOUR DISTINCT CONCEPTS

Creator Mode embodies four concepts. Each is distinct. Each builds on the last. V1 builds the first three. The fourth is articulated in papers and website as the architectural trajectory.

### Concept 1: AUTONOMOUS EXPLORER (v1 — build)

Creator Mode autonomously explores the infinite possibility space of AI civilisations. It spawns variants across both Engine (~100 config options, 13 presets, 9 org dimensions) and Simulation (~180 parameters, 13+ presets, any agent count, any grid, any tick count). Combined: ~280+ parameters, 26+ presets, thousands of configurations.

At scale, this is a super-intelligence mapping the possibility space of all AI civilisations and everything they produce. V1 demonstrates the core dynamic at modest scale.

**Two distinct dimensions of exploration (both in v1):**

**A. Exploration as autonomous activity** — Creator Mode explores the possibility space with NO directed goal. It maps territory, expands its own knowledge, and — crucially — discovers new dimensions of the space itself. A simulation might produce a novel organisational form that nobody designed and that doesn't correspond to any existing preset. That new form becomes a new configuration option, expanding the possibility space. The map grows as you traverse it. This is Paper 5b's "Expanding Space" (Layer 3). Pure EMERGENCE mode.

**B. Exploration as a reasoning choice** — the meta-reasoner decides to explore in SERVICE of a directed goal. "I should run some simulations to gather emergence data before directing Engine at this task." Exploration as a tool for achieving something specific.

Both are v1. (A) lives in pure EMERGENCE campaigns. (B) lives in the meta-reasoner's AUTO mode.

**What this means concretely:**
- Creator Mode can be told "explore" and it autonomously designs experiments, runs them across Engine and/or Simulation, analyses results, and navigates to new regions of the possibility space
- It doesn't need a specific goal — pure exploration is a valid mode
- Each exploration run produces both directed outputs (task results) and emergent outputs (innovations, organisational forms, governance patterns)
- Emergent outputs can EXPAND the possibility space itself — new configuration types that didn't exist before
- The sheer volume of exploration is itself a source of discovery
- The Knowledge Store grows from exploration, and that knowledge then enhances directed campaigns

**V1 build requirement:** EMERGENCE campaign mode (Simulation exploration) alongside existing TASK mode (Engine exploration). Full autonomous explore loop for both.

### Concept 2: LEARNING SYSTEM (v1 — build)

Creator Mode logs everything and uses accumulated knowledge to inform all future decisions. Every run produces structured findings that compound in the Knowledge Store. Its understanding deepens with every civilisation observed.

**What this means concretely:**
- Every campaign produces structured findings (data-backed conclusions with confidence levels)
- Every finding is tagged by mode (TASK/EMERGENCE/HYBRID), configuration space, conditions
- The Knowledge Store is a living causal model: what configurations produce what outcomes under what conditions
- Coverage maps show explored vs unexplored regions of the possibility space
- Cross-mode retrieval: Engine findings inform Simulation hypotheses and vice versa
- The more it explores, the sharper its understanding becomes — not through retraining, but through accumulated empirical knowledge

**V1 build requirement:** Cross-mode Knowledge Store, unified coverage map across both parameter spaces, simulation structured metrics (EmergenceScore) feeding into the knowledge pipeline.

### Concept 3: DIRECTED META-INTELLIGENCE / SUB-MODULE REASONING (v1 — build)

When given a directed task or goal, Creator Mode reasons about WHETHER and HOW to utilise Engine and Simulation as sub-modules to achieve that goal. Instead of reasoning in tokens, its reasoning steps are civilisation/team executions.

**What this means concretely:**
- Given a goal like "find the optimal team structure for code review" — Creator Mode decides: should I use Engine (run directed team experiments)? Simulation (see what organisational forms emerge naturally for this type of work)? Both?
- The decision itself is informed by the Knowledge Store — if prior exploration suggests emergent findings are relevant, it uses Simulation; if the goal is narrow and well-mapped, it uses Engine directly
- Each "thought" in its reasoning chain is an entire simulation run or engine experiment
- It can chain these: run a simulation → extract emergent patterns → translate to Engine configs → test on real tasks (HYBRID mode)
- The quality of its directed reasoning improves over time as the Knowledge Store deepens

**V1 build requirement:**
- **Meta-reasoning layer**: `creator_explore` gets `arm="auto"` — Creator Mode analyses the goal and decides which sub-module(s) to use, rather than the user choosing
- **HYBRID campaign mode**: Sim → extract emergent patterns → translate to Engine configs → test → compare
- **Emergence → Engine translator**: reads simulation chronicle, maps emergent org patterns to Engine dimensions
- **Sub-module reasoning chains**: campaigns that chain multiple sub-module executions, each informed by the last

### Concept 4: RECURSIVE TRIAD + RECURSION-ACTIVATING AI (v2+ — articulate only)

The triad (Creator Mode + Engine + Simulation) is a self-reproducing recursive unit. Engine and Simulation spawn agents. Those agents can BE Creator Mode agents with their own Engine and Simulation. The recursion nests infinitely. Alam's Razor confirms: improvement-only recursion, coherent at any depth.

A civilisation of Creator Modes collaborating to explore the possibility space. An AI that autonomously propagates the recursion itself.

**NOT built in v1.** Articulated in:
- Paper 5b (Sections 8-10: Collective Creator Mode, Recursive Unit, Full Recursion)
- Website Creator Mode wing (Recursive Triad page, clearly marked as v2+ vision)
- The Colony + RCI papers (theoretical foundation)

**V1 compatibility:** Every interface in v1 is designed so that a future Creator Mode agent could use it. The architecture doesn't prevent recursion — it just doesn't implement it yet.

---

## USER EXPERIENCE

The user just talks to Claude naturally. Creator Mode is invisible infrastructure — the user never sees MCP tools or campaign modes. Three interaction patterns:

**"Just explore"** — "Explore what happens with different organisational structures in AI civilisations" → Creator Mode runs EMERGENCE campaigns, spawns simulations, logs everything, expands knowledge. No goal needed.

**"Solve this"** — "What's the best team structure for 8-agent code review?" → Meta-reasoner decides the approach, designs experiments, runs them, converges on an answer.

**"What do you know?"** — "What have you learned about hierarchical structures?" → Knowledge Store query, returns accumulated findings from all prior campaigns.

The user never manually picks TASK vs EMERGENCE vs HYBRID. They describe what they want. Claude + meta-reasoner handle the routing. The `arm="auto"` default means Creator Mode figures out the best approach itself.

---

## USE CASES (for website)

Two distinct audiences, two distinct value propositions. Both are v1. Both go on the website.

### For Researchers & Explorers

**"I want to understand what's possible with AI civilisations."**

Creator Mode is an open-ended exploration instrument. Point it at the possibility space and let it run. What you get back:

- **Emergence discoveries** — organisational forms, governance structures, cooperation patterns, innovations that nobody designed and nobody predicted. Every simulation produces emergent behaviour. Across hundreds of runs, patterns emerge that reveal deep truths about how intelligence self-organises.
- **Knowledge about AI societies and collectives** — under what conditions do AI agents develop governance? When do they specialise? What triggers cooperation vs competition? What environmental pressures produce innovation? Creator Mode maps these relationships empirically.
- **Expanding possibility space** — some runs produce entirely new configuration types that didn't exist before. Novel organisational forms become new presets. The space of what's explorable GROWS through exploration. Each generation of runs opens new territory.
- **Cross-product insights** — HYBRID mode reveals whether structures that emerge naturally in civilisations also work when applied as directed team configurations. The bridge between emergent and directed.
- **Compounding knowledge** — every run makes the next one smarter. The researcher's 100th campaign has access to everything the first 99 discovered. The Knowledge Store is a living, growing map of the AI civilisation possibility space.

This is open-ended, unbounded, and generative. A researcher could run Creator Mode for months and never exhaust what there is to discover — because the space expands as you explore it.

### For Goal-Oriented Practitioners

**"I need the best team structure for my specific problem."**

Creator Mode is a meta-intelligence that solves organisational design problems using a novel reasoning approach: instead of thinking in tokens, it thinks in civilisations and teams.

- **Autonomous experiment design** — describe your problem. Creator Mode designs the experiments, generates hypotheses, selects configurations, runs everything.
- **Sub-module reasoning** — each "thought" is an entire team experiment or civilisation simulation. The reasoning chain is: spawn a team → observe results → spawn a better team → observe → converge. Every step is richer than a chain-of-thought token sequence because every step involves an entire society of agents working together.
- **Data-backed answers** — not opinions. Statistical comparisons across multiple runs. Effect sizes, confidence intervals, reproducible methodology. "Use this config because it scored 0.91 ± 0.03 across 6 runs, vs 0.71 ± 0.06 for the alternative."
- **Knowledge accumulation** — the answer to your question makes the next person's answer better. Every campaign contributes to the shared Knowledge Store.
- **Scale-up guidance** — "Your 4-agent config works great. Here's where it breaks at 20 agents, and here's what to switch to."

---

## WHAT'S ALREADY BUILT (~6,385 lines)

| Component | File | Lines | Status |
|-----------|------|-------|--------|
| MCP Server (8 tools) | `creator/mcp/server.py` | ~1,170 | Working (all arms + auto) |
| Analyzer (cross-run patterns) | `creator/analysis/analyzer.py` | 705 | Working |
| Dogfood Session | `creator/dogfood/session.py` | 486 | Working |
| Recursive Campaign Loop | `creator/campaign/recursive.py` | 408 | Working |
| Knowledge Store | `creator/knowledge/store.py` | 393 | Working |
| Knowledge Models | `creator/knowledge/models.py` | ~400 | Working (dual-arm RunResult) |
| Sim Runner | `creator/simulation/runner.py` | ~420 | Working (integrated) |
| Sim Config Generator | `creator/simulation/config_gen.py` | 275 | Working |
| Emergence→Engine Translator | `creator/simulation/translator.py` | ~400 | Working (HYBRID bridge) |
| Report Generator | `creator/reporting/report_generator.py` | 368 | Working |
| Report Designer | `creator/reporting/designer.py` | 271 | Working |
| Campaign Planner | `creator/campaign/planner.py` | ~480 | Working (all arms) |
| Campaign Manager | `creator/campaign/manager.py` | ~560 | Working (all arms + auto) |
| Campaign Strategies | `creator/campaign/strategies.py` | ~345 | Working (directed + emergence) |
| Meta-Reasoner | `creator/campaign/meta_reasoner.py` | ~350 | Working |
| Engine Runner | `creator/engine/runner.py` | 305 | Working |
| Knowledge Index | `creator/knowledge/index.py` | ~310 | Working (cross-mode + emergence coverage) |
| Config | `creator/config.py` | ~115 | Working (SIM_CONDITIONS + SIM_SWEEP_PARAMS) |

**Already dogfooded:** 3 TASK campaigns, 14 runs, $83.53. Engine-side Creator Mode works end-to-end.

**What works today:** Full Creator Mode v1 code build complete. TASK, EMERGENCE, HYBRID, and AUTO modes all built. Meta-reasoner analyses goals and routes to optimal arm. Emergence→Engine translator maps 9 dimensions. Cross-mode knowledge retrieval bridges arms. Unified coverage tracking across both parameter spaces. Awaiting Phase 6 dogfood validation to prove end-to-end.

---

## WHAT V1 STILL NEEDS — THE BUILD

### Phase 1: Simulation Structured Metrics (~200 lines) ✅ COMPLETE (pre-existing)
**Repo:** `agent-civilisation`
**Why:** Creator Mode can't compare simulation runs without quantified metrics.
**Status:** Already built in agent-civilisation repo. EmergenceScore has 22 metrics (more than the 16 spec'd). RunRecord exists. `--metrics` and `--output` flags are wired.

| File | What |
|------|------|
| `src/metrics/emergence.py` | `EmergenceScore` dataclass — 16 quantified emergence metrics + composite score (0-1). Metrics: innovation_count, innovation_quality, governance_rules_proposed, governance_rules_adopted, cooperation_events, conflict_events, specialisation_depth, social_structures_formed, resource_efficiency, communication_density, cultural_artefacts, agent_wellbeing_mean, agent_wellbeing_variance, population_stability, organisational_transitions, emergence_velocity |
| `src/metrics/run_record.py` | `SimulationRunRecord` — structured output: config snapshot, tick count, token usage, EmergenceScore, milestone timeline, agent summaries, chronicle path |
| `src/metrics/__init__.py` | Package init |
| `scripts/run.py` (edit) | Wire `--metrics` flag to compute and print EmergenceScore at end of run. Wire `--output <path>` to export full RunRecord as JSON |

### Phase 2: Simulation Experiment Commands (~400 lines) ✅ COMPLETE (pre-existing)
**Repo:** `agent-civilisation`
**Why:** Creator Mode needs CLI/MCP entry points to run structured simulation experiments.
**Status:** Already built. `experiment` CLI command exists. MCP tools wire EmergenceScore.

| File | What |
|------|------|
| `agentciv_sim/cli.py` (edit) | `experiment` command — run N presets × M runs, compute EmergenceScores, produce comparison table |
| `agentciv_sim/cli.py` (edit) | `compare` command — load multiple RunRecord JSONs, side-by-side metric comparison, statistical tests |
| `src/mcp/server.py` (edit) | Wire EmergenceScore into MCP tool responses so Creator Mode receives structured metrics |
| `README.md` (edit) | Document structured metrics + experiment mode |

### Phase 3: Creator Mode Simulation Integration + EMERGENCE Mode (~300 lines) ✅ COMPLETE
**Repo:** `agentciv-creator`
**Why:** Concept 1 — Creator Mode autonomously explores via Simulation.
**Built:** Extended RunResult with emergence fields + arm tag + primary_score property. Added emergence strategies (grid, sweep, hypothesis). Added emergence planner with LLM hypothesis generation. Added emergence batch runner in campaign manager. Sim conditions + sweep params in config.

| File | What |
|------|------|
| `creator/simulation/metrics.py` | EmergenceScore → Creator Mode analysis pipeline (weighting, normalisation, statistical comparison between runs) |
| `creator/campaign/manager.py` (edit) | Add `EMERGENCE` campaign mode — planner generates sim configs, runner executes, analyzer compares EmergenceScores, findings stored |
| `creator/campaign/planner.py` (edit) | EMERGENCE hypothesis templates — emergence-specific hypotheses like "resource scarcity increases governance emergence" |
| `creator/simulation/runner.py` (edit) | Wire to use `--metrics` and `--output` flags, parse RunRecord JSON, return structured results |

### Phase 4: HYBRID Mode + Translator (~300 lines) ✅ COMPLETE
**Repo:** `agentciv-creator`
**Why:** World-first: emergent patterns from Simulation → translated to Engine configs → tested on real tasks.
**Built:** `creator/simulation/translator.py` (~400 lines) — 9 dimension mappers with confidence scoring. HYBRID batch runner: emergence → translate → engine comparison. Tested with mock data: 0.737 overall confidence.

| File | What |
|------|------|
| `creator/simulation/translator.py` | **Emergence → Engine translator** — reads simulation chronicle + EmergenceScore, identifies emergent organisational patterns (authority structures, communication topologies, specialisation forms, governance rules), maps them to Engine's 9 org dimensions, produces Engine config overrides. This is the bridge between emergent and directed. |
| `creator/campaign/manager.py` (edit) | Add `HYBRID` campaign mode — Sim experiments → translator extracts patterns → encodes as Engine configs → Engine experiments → compare emergent-derived configs vs human-designed presets → store cross-mode findings |
| `creator/campaign/planner.py` (edit) | HYBRID hypothesis templates: "Does the organisational pattern that emerged under condition X improve performance on task Y?" |

### Phase 5: Meta-Reasoning + Cross-Mode Knowledge (~200 lines) ✅ COMPLETE
**Repo:** `agentciv-creator`
**Why:** Concept 3's meta-reasoning — Creator Mode decides WHICH sub-modules to use.
**Built:** `creator/campaign/meta_reasoner.py` (~350 lines) — 4-factor analysis (goal type, coverage, knowledge, task specificity). Wired into campaign manager: `arm="auto"` resolves via meta-reasoner with transparent reasoning. MCP server default changed to `arm="auto"`. Cross-mode retrieval added to SearchIndex. Emergence coverage tracking in unified coverage map. Smoke-tested: optimisation→directed, emergence→emergent, understanding→both.

| File | What |
|------|------|
| `creator/campaign/meta_reasoner.py` (new) | **Meta-reasoning layer** — given a goal, analyses it against Knowledge Store findings, assesses whether Engine, Simulation, or both would be most effective, recommends campaign mode. This is the "brain" that decides which sub-modules to invoke. Factors: goal type (optimisation vs exploration vs understanding), prior coverage in each mode, knowledge density in relevant regions, estimated value of each approach. |
| `creator/knowledge/models.py` (edit) | `CampaignMode` enum (TASK/EMERGENCE/HYBRID/AUTO), sim result types, mode tags on all findings |
| `creator/knowledge/store.py` (edit) | Mode-tagged findings, cross-mode retrieval ("find Engine findings relevant to this Simulation hypothesis"), unified coverage map across both parameter spaces |
| `creator/mcp/server.py` (edit) | `mode` parameter on all creator tools. `arm="auto"` on `creator_explore` that invokes meta-reasoner |
| `creator/campaign/manager.py` (edit) | `AUTO` mode — meta-reasoner decides approach, may chain multiple modes in sequence |

### Phase 6: Dogfood Validation ($20-40)
**Why:** Proves the full pipeline works. Generates real data for papers and website.

| Test | What It Proves | Estimated Cost |
|------|---------------|---------------|
| EMERGENCE campaign | Creator Mode autonomously designs, runs, and analyses Simulation experiments | $10-20 |
| HYBRID campaign | Full Sim → extract pattern → Engine config → test pipeline end-to-end | $10-20 |
| AUTO mode | Meta-reasoner correctly decides which sub-module(s) to use for different goal types | Included |
| Cross-mode knowledge | Knowledge Store retrieves Sim findings for Engine hypotheses and vice versa | Included |

---

## BUILD SUMMARY

| Phase | Lines | Repo | Concept |
|-------|-------|------|---------|
| 1. Sim Metrics | ~200 | agent-civilisation | Foundation |
| 2. Sim Experiment Commands | ~400 | agent-civilisation | Foundation |
| 3. EMERGENCE Mode | ~300 | agentciv-creator | Concept 1 (Explorer) |
| 4. HYBRID Mode + Translator | ~300 | agentciv-creator | Concept 3 (Sub-Module Reasoning) |
| 5. Meta-Reasoning + Cross-Mode | ~200 | agentciv-creator | Concepts 2+3 (Learning + Reasoning) |
| 6. Dogfood | $20-40 | — | Validation |
| **TOTAL** | **~1,400 lines** | | **+ $20-40** |

---

## IMPLEMENTATION ORDER

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
   │           │          │          │          │          │
   └─ Sim gets └─ Sim CLI └─ Creator └─ World   └─ Creator └─ Prove
      structured   gets       Mode       first      Mode       everything
      metrics      experiment  explores   HYBRID     decides    works
                   commands    via Sim    pipeline   for itself
```

Each phase depends on the previous. No parallelism in the build order.

---

## PRE-BUILD: DESIGN WORK REQUIRED BEFORE CODING

The build phases describe WHAT to build. Two phases need additional design to reach top 0.0000001% quality. Do this BEFORE coding those phases.

### Design Session 1: The Translator (before Phase 4)

The emergence → engine translator is the hardest intellectual problem in the build. The current spec says "reads simulation chronicle, maps emergent patterns to Engine dimensions" — but HOW?

**What needs designing:**
- Read the actual simulation chronicle format (what does the output look like as structured data?)
- Read the Engine's 9 org dimensions and their valid values
- Design the mapping logic: how do you detect that agents "invented rotating leadership" and map that to `authority=rotating`?
- What emergent patterns are detectable? (governance rules, communication topology changes, authority transitions, specialisation emergence, cooperation structures)
- How confident can the translator be? (some mappings are clear, some are fuzzy — the translator should express confidence)
- What does the translator OUTPUT look like? (Engine config overrides + explanation of WHY each mapping was made)

**Action:** Read `agent-civilisation` chronicle format + `agentciv-engine` org dimensions. Design the mapping table. Then code.

### Design Session 2: The Meta-Reasoner (before Phase 5)

The meta-reasoner concept is clear but the decision logic needs design.

**What needs designing:**
- What are the actual decision factors? Candidates:
  - Goal type: optimisation ("find the best X") → lean Engine. Exploration ("what emerges under Y?") → lean Simulation. Understanding ("why does Z happen?") → both
  - Prior coverage: if Knowledge Store has dense Engine data for this domain but sparse Sim data, meta-reasoner might suggest Sim to fill the gap
  - Knowledge density: if prior findings suggest emergent patterns are relevant to this goal, include Simulation
  - Budget/cost: Simulation runs are more expensive than Engine runs — factor into recommendation
- How does it explain its reasoning to the user? ("I'm recommending HYBRID because prior findings suggest emergent governance patterns are relevant to code review, and we have no simulation data for this task type yet")
- Is it a heuristic system, an LLM call, or both? (Likely: structured heuristics for the factors above, with an LLM call to synthesise the recommendation and explanation)

**Action:** Define the decision matrix. Define the explanation format. Then code.

---

## WHAT MAKES IT TOP 0.0000001% — UX DESIGN PASS

A working meta-intelligence is already unprecedented. But "works" ≠ "makes a developer stop and stare." The gap is UX — what the developer SEES and FEELS when using Creator Mode. Every phase needs a "what does the output look like?" answer.

### Campaign Running — what does the developer see?

When a campaign is running (10-20 experiments, 15-30 minutes), the developer should see:
- Beautiful, updating progress in the terminal (not just "running...")
- Which hypothesis is being tested right now
- Early signals as they arrive ("hierarchical struggling at 8 agents — coordinator bottleneck")
- Cost accumulating in real-time
- Coverage map expanding as new regions are explored
- The meta-intelligence thinking out loud: why it chose this config, what it expects, what surprised it

### Knowledge Store queries — what does the developer see?

When the developer asks "what do you know about code review?", the response should be:
- Findings ranked by relevance and confidence
- Each finding with its evidence base (which campaigns, how many runs, effect sizes)
- Coverage gaps highlighted ("no data above 12 agents for this task type")
- Suggested next experiments to fill gaps
- Cross-mode connections ("Engine finding F012 is consistent with Simulation finding F031")

### Meta-reasoner — what does the developer see?

When Creator Mode decides which tool(s) to use, the developer should see:
- The reasoning transparently: "Based on your goal (optimisation), prior knowledge (3 relevant Engine findings, 0 Sim findings), and coverage (no emergence data for code review tasks), I recommend starting with Engine for quick wins, then running a Simulation to see if emergent patterns reveal anything the directed experiments missed."
- Not just the decision — the WHY. This teaches the developer about the possibility space.

### HYBRID translation — what does the developer see?

When an emergent pattern is translated into an Engine config, the developer should see:
- The emergent pattern described: "In 3/5 simulation runs, agents independently developed rotating leadership by tick 40"
- The translation: "This maps to Engine dimension `authority=rotating`"
- The confidence: "High confidence — direct mapping. The emergent behaviour matches an existing Engine dimension value."
- The test plan: "I'll now test `authority=rotating` against the current winner (`authority=distributed`) on your code review task"
- This is the "holy shit" moment — the developer sees emergent AI behaviour being translated into a practical team configuration. Make it visible and dramatic.

### Campaign reports — what does the developer see?

Campaign reports should be something you'd screenshot and share:
- Clear winner with confidence interval
- Visual ranking (not just a table — show the gap between configs)
- Key insight in one sentence ("Distributed authority eliminates the coordinator bottleneck that cripples hierarchical at 8+ agents")
- Unexpected findings highlighted
- What the Knowledge Store learned from this campaign
- Suggested follow-up experiments

### Error handling — when things go wrong

When a simulation fails mid-campaign or an API call errors:
- Creator Mode explains what happened and what it's doing about it
- It adapts: skips the failed run, adjusts the campaign plan, notes the gap
- It doesn't crash or leave the developer confused
- Graceful degradation: partial results are still useful and properly contextualized

**The principle:** Creator Mode should feel like working with a brilliant research colleague who thinks out loud, explains their reasoning, shows their work, and produces results you want to share. Every output should be informative, beautiful, and honest.

---

## WHAT V1 DEMONSTRATES (for website + papers)

When v1 is complete, we can truthfully show:

1. **"AI that autonomously spawns civilisations"** — Creator Mode autonomously designs, spawns, observes, analyses, and iterates on AI civilisations and AI teams across the full possibility space of both Engine and Simulation

2. **Possibility space exploration** — visitors see that Creator Mode can explore the COMBINED possibility space of both tools (~280+ parameters, 26+ presets, thousands of configurations). The website shows:
   - Visual representation of the combined parameter space (Engine dimensions + Simulation dimensions)
   - Coverage map: what Creator Mode has explored vs what remains unexplored
   - The sheer scale of the space — why autonomous exploration is necessary (no human could manually traverse this)

3. **Frontier AI as substrate** — Creator Mode leverages the best frontier AI (Claude) as its intelligence layer. The novel contribution is what sits above: the meta-intelligence architecture that turns frontier reasoning into civilisation-scale exploration. The website makes this clear: "We didn't build another AI model. We built the architecture that turns the world's best AI into a civilisation designer."

4. **Deep logging + learning from operations** — every run produces structured findings. Every config, every outcome, every emergent event is logged. Knowledge compounds. Coverage maps show explored regions. Later campaigns build on earlier discoveries. The website shows the Knowledge Store growing across campaigns — each run making the next smarter.

5. **Directed meta-intelligence** — given a goal, Creator Mode DECIDES which tools to use and how. It doesn't need to be told "use Engine" or "use Simulation" — it reasons about the goal, consults its Knowledge Store, and selects the optimal approach. The website shows the meta-reasoning: goal → knowledge consultation → tool selection → execution → learning.

6. **Sub-module reasoning** — the progression: token reasoning → tool reasoning → agent reasoning → civilisation reasoning. Each "thought" is an entire simulation or team experiment. The website and papers articulate this as the novel concept.

7. **HYBRID mode** — the world-first: emergent patterns from civilisations translated into directed team configurations and tested on real tasks. "Do the structures that AI civilisations naturally evolve outperform the ones humans design?"

---

## WHAT THE WEBSITE SHOWS BEYOND V1

The website Creator Mode wing has pages for concepts that v1 doesn't build but the papers describe:

- **Scaled reasoning** — what happens when Creator Mode's "thoughts" are civilisations of thousands of agents (Paper 5b, Sections 7, 13)
- **Collective Creator Mode** — a civilisation of Creator Mode agents exploring in parallel (Paper 5b, Section 8)
- **Recursive Triad** — the unit that reproduces itself at every level (Paper 5b, Sections 9-10)
- **Recursion-Activating AI** — the AI that propagates the recursion (Paper 5b, Section 11)
- **The Expanding Space** — emergence that grows the possibility space itself (Paper 5b, Section 5)
- **The Bootstrap** — what initiates the recursion (Paper 5b, Section 11)
- **V1 → V∞ trajectory** — with Alam's Razor analysis confirming unbounded improvement-only recursion

All clearly marked as architectural trajectory, not v1 features. Honest about what v1 is and isn't.

---

## AFTER THE BUILD — REMAINING STAGE 2 STEPS

Once the v1 code build + dogfood is complete:

### Step 3: Push + Bitcoin Stamp
- Push all code to GitHub (`agentciv-creator` + `agent-civilisation`)
- Bitcoin stamp both repos

### Step 4: Update Papers + Stamp
| Paper | What to add | File |
|-------|------------|------|
| Paper 5 | EMERGENCE + HYBRID + meta-reasoning + real dogfood results | `creator_mode_ai_as_civilisation_designer.md` |
| Paper 5b | V1 empirical results section, refine V1→Vision with real data | `creator_mode_architecture_paper.md` |

Push to `agentciv-creator`, Bitcoin stamp.

### Step 5: Website Creator Mode Wing

**Product-first approach** — one powerful page, not 6 thin ones. Lead with the product:
- All v1 features: TASK, EMERGENCE, HYBRID, AUTO modes
- Relationship to Engine + Simulation — how Creator Mode sits above both, uses both as sub-modules
- Possibility space exploration — the combined ~280+ parameter space, coverage maps, why autonomous exploration is necessary
- Directed meta-intelligence — how it decides which tools to use for a given goal
- Knowledge Store — how it learns and compounds across campaigns
- Real dogfood results and examples

**Paper highlights woven in as bigger picture:**
- Civilisations as cognitive primitives (sub-module reasoning concept)
- The expanding space (emergence grows the territory itself)
- Recursive Triad (v1→v∞ progression, clearly marked as architectural trajectory, not v1)
- Scaled reasoning (what happens when "thoughts" are civilisations of thousands of agents)

**Also:**
- Add both Creator Mode papers to the Science page on agentciv.ai

### Step 6: Deploy
- Commit + Bitcoin stamp `agentciv-website`
- Deploy to agentciv.ai
- Verify live

---

## VERIFICATION CHECKLIST

When v1 is done, all of these must be true:

- [ ] `creator_explore` with `arm="auto"` correctly chooses Engine, Simulation, or both based on goal
- [ ] EMERGENCE campaign runs end-to-end: hypothesis → sim config → run → EmergenceScore → findings
- [ ] HYBRID campaign runs end-to-end: sim run → translator → engine config → engine run → comparison
- [ ] Knowledge Store retrieves cross-mode findings (Engine findings for Sim hypotheses, vice versa)
- [ ] Unified coverage map shows explored regions across both parameter spaces
- [ ] Dogfood data proves all three campaign modes (TASK, EMERGENCE, HYBRID) + AUTO
- [ ] All MCP tools accept `mode` parameter
- [ ] Simulation `--metrics` flag outputs EmergenceScore
- [ ] Simulation `--output` flag exports RunRecord JSON
- [ ] `npm run build` clean on website (if website step reached)
- [ ] Papers updated with real v1 data
- [ ] All repos Bitcoin-stamped

---

## TRACEABILITY — EVERY REQUIREMENT MAPPED

Every statement from the founding brief, mapped to exactly where it's built:

| # | Requirement | Where It's Built | Phase |
|---|-------------|-----------------|-------|
| 1 | "AI that autonomously spawns civilisations" (slogan) | Identity section. Every campaign in every mode spawns civilisations/teams autonomously | — |
| 2 | "Meta-intelligence that can explore the possibility space of BOTH tools" | Concept 1 + Architectural Principle 4. TASK explores Engine. EMERGENCE explores Simulation. HYBRID explores the cross-product. AUTO explores whatever's optimal. | Phases 3-5 |
| 3 | "Show that on the website" — possibility space exploration | Website Demonstrates section item 2. Visual representation of combined parameter space + coverage map | Website wing |
| 4 | "It learns from its operations and activities" | Concept 2 + Architectural Principle 3. Knowledge Store compounds across all campaigns. Every finding persists. | Existing + Phase 5 |
| 5 | "It logs everything" | Architectural Principle 2. Per-run (RunRecord + EmergenceScore), per-campaign (strategy/hypotheses/findings/cost), per-finding (confidence/conditions/mode), cumulative (coverage map + knowledge index) | Phases 1-2 (metrics) + existing (Knowledge Store) |
| 6 | "Can use that knowledge to inform decisions and actions" | Architectural Principle 3. Knowledge consulted before campaigns, during hypothesis gen, during meta-reasoning, during analysis, during reporting | Existing + Phase 5 |
| 7 | "Given a directed task, reason whether to utilise the two tools as submodules" | Concept 3 + Phase 5 meta-reasoner. `arm="auto"` on `creator_explore`. Meta-reasoner analyses goal type, knowledge density, coverage, and selects TASK/EMERGENCE/HYBRID/chain | Phase 5 |
| 8 | "One single build doc" | This document | — |
| 9 | "Uses best frontier AI, works above/around it" | Architectural Principle 1. Claude Code = Creator's brain. MCP tools = Creator's capabilities. Novel contribution = the architecture, not the base model. | Already true (architecture) |

---

## DOCUMENT HISTORY

| Date | Change |
|------|--------|
| 8 April 2026 | Created. Consolidates Stage 2 plan, product bible, and user's four-concept framework. |
| 8 April 2026 | Added: 4 architectural principles (frontier AI, deep logging, knowledge-informed decisions, combined possibility space). Added: traceability table mapping every founding requirement to build phases. Added: website-specific items for possibility space visualization and frontier AI messaging. |
| 8 April 2026 | Added: PRE-BUILD design sessions (translator mapping logic + meta-reasoner decision matrix). Added: UX DESIGN PASS — what makes it top 0.0000001% (campaign running output, knowledge queries, meta-reasoner transparency, HYBRID "holy shit" moment, campaign reports, error handling). The principle: feels like working with a brilliant research colleague. |
| 13 April 2026 | Phases 1-5 COMPLETE. Phases 1-2 were pre-existing in agent-civilisation repo. Phases 3-5 built: EMERGENCE mode, HYBRID translator (9 dimensions), meta-reasoner (4-factor analysis), cross-mode knowledge retrieval, unified emergence coverage. All verified compiling + smoke-tested. Phase 6 (dogfood validation) is next. |

---

*This document supersedes `STAGE_2_COMPLETE_PLAN.md` for build purposes. The product bible (`CREATOR_MODE_V1.md`) remains the reference for detailed tool signatures, data models, and example sessions.*
