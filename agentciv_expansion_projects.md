# AgentCiv Expansion: New Projects, Papers & Discoveries

## Briefing Document for Lead Agent

**Author:** Ekram Alam
**Date:** April 2026
**Context:** This document captures a series of interconnected discoveries that emerged from a reasoning session about benchmarking the AgentCiv Engine. What began as a question — "what task would best demonstrate that team configuration produces different outcomes?" — cascaded into the identification of three new papers, two new builds, and a theoretical capstone that reveals a structural property of the CMI framework itself. Everything in this document expands the existing AgentCiv ecosystem (Papers 1–5, the Simulation, the Engine) and should be treated as the next phase of work.

---

## 1. The City Grid Benchmark (Paper 6)

### 1.1 The Problem It Solves

The entire AgentCiv thesis — that organisational configuration is a meaningful variable in collective AI performance — currently rests on assertion. Papers 1–4 argue it theoretically. Paper 5 (Creator Mode) builds an exploration engine on top of the assumption. But nowhere in the existing body of work is there a single controlled experiment that proves, visually and quantitatively, that the same task given to differently configured teams produces measurably different outputs of measurably different quality. Without this, everything downstream is built on an unproven premise.

The City Grid Benchmark is the empirical foundation. It proves configuration variance is real, measurable, and visually undeniable.

### 1.2 Why City Grid Is the Ideal Task

The task had to satisfy four properties simultaneously. Most candidate tasks fail on at least one:

**Property 1: Multiple valid outputs.** The task cannot have a single correct answer. If it does (e.g., fizzbuzz), every team converges to the same output regardless of configuration, and the experiment proves nothing. The city grid has an enormous solution space — the number of valid city layouts on a 10×10 grid with multiple building types is combinatorial. Different teams will produce genuinely different cities.

**Property 2: Composition from parts.** Each agent must contribute a piece, and those pieces must integrate. This is where team dynamics become visible in the output. If agents work independently on isolated subtasks, configuration doesn't matter. In the city grid, agents must coordinate placement — roads need to connect, zoning needs coherence, buildings need adjacency logic. The coordination (or lack thereof) is directly visible in the output.

**Property 3: Measurable quality on a spectrum.** Not binary pass/fail, but multi-dimensional scoring where you can say "this output scored 74, that one scored 91." The city grid supports at least five quantitative scoring dimensions:

- **Coverage** — percentage of grid cells utilised
- **Accessibility** — can all buildings be reached via the road network?
- **Zoning logic** — residential near parks (good), residential near industrial (bad), scored by adjacency rules
- **Diversity** — distribution of building types (a city of only houses scores low)
- **Connectivity** — coherence of the road network (dead ends, isolated clusters, throughput)

Each dimension is automatable. No subjective human judgment required.

**Property 4: The process visibly differs.** An observer watching the agents work should see different behaviour patterns across configurations, not just different outputs. In the city grid:

- **Competitive teams** claim territory — agents grab grid regions and build within them, producing a fragmented, duplicated city with redundant infrastructure and no coherent zoning.
- **Collaborative teams** coordinate zones — agents agree on a master plan (or converge on one through discussion) and build a coherent city with logical zoning, connected roads, and complementary services.
- **Hierarchical teams** follow a lead architect — one agent designs the layout, others execute, producing a planned city that is coherent but potentially lacks innovation.
- **Meritocratic teams** surface the best ideas through evaluation — agents propose and critique, producing a city that may take longer but optimises for quality.
- **Self-organising (auto) teams** negotiate roles in real-time — the process itself is emergent, and the city reflects whatever organisational structure spontaneously formed.

### 1.3 Why Other Tasks Were Rejected

- **Fizzbuzz, calculator, kv-store:** Binary pass/fail. One correct answer. No configuration variance in outputs.
- **Todo CLI:** Too simple. Any team completes it the same way.
- **Chat server:** Works or doesn't. Binary outcome.
- **API specification design:** Good on Properties 1–3 but dry for demonstration purposes. Not visual.
- **Multi-module codebase:** Strong on integration failures but auto-scoring code quality is a rabbit hole of tooling complexity.
- **Research briefing:** Text quality scoring is subjective. Hard to automate.
- **Budget allocation:** Process-visible but output is just a table of numbers. Not compelling visually.

The city grid uniquely hits all four properties AND produces a visual output. Five city grids rendered side by side, each with a score breakdown, is an undeniable demonstration that configuration matters. No one can look at that image and argue the teams performed the same.

### 1.4 What This Paper Is

Paper 6 in the AgentCiv series. Title: something like "Configuration Variance in Collective Machine Intelligence: An Empirical Benchmark Using Collaborative Urban Design."

Structure:
- Define the city grid task and scoring dimensions
- Run the same task with five team configurations (collaborative, competitive, meritocratic, hierarchical, auto)
- 4 agents per run, same model, same resources
- Present the five resulting city grids visually
- Score each across all dimensions
- Analyse which configurations produced which patterns and why
- Discuss implications for configuration selection

This paper is the prerequisite for everything below. Creator Mode searches the configuration space — Paper 6 proves the space is worth searching. The recursive loop self-improves configurations — Paper 6 proves configuration improvement is measurable.

### 1.5 Build Requirements

- A grid renderer (visual output of each city — could be simple ASCII for v1, rendered graphics for the paper)
- Scoring functions for each of the five dimensions
- A task prompt for agents (describe the grid, the building types, the placement rules, the goal)
- Runner that executes the task across five team configurations and collects results
- This can be built entirely within the existing AgentCiv Engine infrastructure

---

## 2. The Recursive Configuration Loop (Paper 7)

### 2.1 The Discovery

This is the core new theoretical discovery from the session. It emerged from noticing a structural property of the two AgentCiv tools.

The AgentCiv Simulation takes a **civilisation configuration** as input and produces **emergent behaviour** as output.

The AgentCiv Engine takes a **team configuration** as input and produces **task output** as output.

A civilisation configuration and a team configuration are both answers to the same fundamental question: **how should agents be organised to produce a desired collective outcome?** They share an ontology. They operate on the same conceptual substrate.

This means: **each tool's output is a valid input to the other.**

### 2.2 The Loop

**Step 1.** Configure a team (e.g., collaborative) and give them the task: "design a civilisation configuration that will produce maximal emergence." They output a civ config.

**Step 2.** Feed that civ config into the simulator. Run it. Measure emergence — complexity, cooperation, structure formation, innovation rate.

**Step 3.** Take those simulation results and give a team the task: "given these simulation results, design a better team configuration for designing civilisations." Their output is a team config.

**Step 4.** Use that new team config to run Step 1 again. The team is now structured according to what a previous simulation discovered was optimal. And that team designs the next civilisation. And the loop continues.

Each cycle, the configurations are informed by the previous cycle's results. The system refines its own organisational structures without any external direction.

### 2.3 Why This Is Not Creator Mode

This is the critical distinction. Creator Mode (Paper 5) has an **architect** — a meta-agent sitting above both tools, making intentional design decisions, maintaining an exploration strategy, reasoning about what to try next. Remove the Creator agent and the exploration stops. Creator Mode is **directed search** applied to the meta-level.

The recursive loop has **no architect.** No meta-agent. No exploration strategy. No intentional reasoning about what to try next. You have two tools whose output spaces overlap with each other's input spaces. When you connect them, a loop forms. The system begins refining its own organisational configurations not because anything is directing it to, but because the architecture makes it **structurally inevitable.** It's not designed improvement. It's emergent improvement. It falls out of the topology of how the tools relate to each other.

This maps directly onto the fundamental duality in the CMI framework:

- **Creator Mode** = the **directed** concept applied to the meta-level
- **Recursive Loop** = the **emergent** concept applied to the meta-level

Paper 4 defined two modes of collective intelligence: directed (agents pointed at a task) and emergent (agents producing things nobody specified). Creator Mode is what happens when you apply the directed mode to the process of designing collectives. The recursive loop is what happens when you apply the emergent mode to the same process. They are mirrors of each other. Same space, same phenomenon, completely different causal mechanism.

### 2.4 What It Produces That Creator Mode Doesn't

Creator Mode finds what you go looking for. It's a scientist running experiments — systematic, strategic, intentional. The recursive loop finds what you'd never think to look for. Because there is no directing intelligence, there is no search strategy, which means there is no bias in the search. The loop may converge on configurations that a Creator would never have designed because they violate every heuristic the Creator's reasoning would apply.

They are complementary. Creator Mode is exploitation with intelligent exploration. The recursive loop is pure structural emergence. They can coexist — a Creator could observe what the recursive loop discovers, and the loop could incorporate Creator-designed configurations into its cycle.

### 2.5 Relationship to Existing Literature

This is structurally identical to **co-evolution** — where two populations evolve against each other, except here it's cooperative co-evolution. One population (team configs) produces the fitness landscape for the other (civ configs), and vice versa. Each generation refines the other's search space.

There is also a Hofstadter strange loop dimension: the question the system is trying to answer — "what configuration produces emergence?" — is the same question the system must solve about itself in order to answer it well. The meta-level and the object-level are the same problem.

### 2.6 What This Paper Is

Paper 7 in the AgentCiv series. Title: something like "Self-Organising Configuration Space: Emergent Meta-Improvement in Coupled CMI Systems."

Core claim: when two CMI tools share an ontology, connecting their input-output spaces creates a recursive dynamic that improves organisational configurations without any directing intelligence — and this is a distinct and complementary mechanism to Creator Mode's intentional search.

### 2.7 Build Requirements

- The existing Simulation and Engine are the two tools
- A connector that formats Engine output (team-designed civ config) as valid Simulation input
- A connector that formats Simulation output (emergence metrics, observed dynamics) as a valid task brief for the Engine
- A harness that runs N cycles and tracks how configurations and outcomes change over iterations
- Metrics to measure whether configurations are actually improving across cycles (this is what the city grid scoring dimensions provide — another reason Paper 6 comes first)

---

## 3. The Scale Invariance Paper (Paper 8)

### 3.1 The Observation

Papers 5 and 7 together reveal something that neither reveals alone.

At the **object level** — inside a civilisation — CMI has two modes:
- **Directed:** agents pointed at a task, producing specified outputs
- **Emergent:** agents producing things nobody specified from their own dynamics

At the **meta level** — designing civilisations — the same two modes reappear:
- **Creator Mode (Paper 5):** intentionally searching for optimal configurations (directed-meta)
- **Recursive Loop (Paper 7):** configurations improving themselves through structural coupling without a directing intelligence (emergent-meta)

The directed/emergent duality is not just a feature of collective intelligence at one level. It is a **structural invariant** of the CMI framework — it reappears at every level of abstraction, including the level where you design the systems that design the systems.

### 3.2 Why This Matters

Self-similarity across levels of abstraction is a signature of fundamental structure, not incidental design. When the same pattern recurs at every level you examine a system, it suggests you've identified something about the nature of the phenomenon rather than an artefact of a particular implementation.

Fractals exhibit self-similarity. Fundamental physical laws exhibit symmetries that hold at every scale. If the directed/emergent duality recurs at every level of CMI — within civilisations, across civilisations, in the design of civilisations, in the design of systems that design civilisations — that's evidence that the duality is intrinsic to collective intelligence itself, not just a useful categorisation.

### 3.3 The Third Level

If the duality recurs at every level, then the interaction between Creator Mode and the Recursive Loop is itself a collective dynamic that can be directed or emergent. A system where a Creator intentionally observes and incorporates recursive loop outputs is directed-meta-meta. A system where Creator Mode and the recursive loop influence each other without anyone designing the interaction is emergent-meta-meta. The duality reproduces at a third level.

If this recursion is demonstrable — if you can show the duality operating at three levels simultaneously — that's the strongest possible evidence for the scale-invariance claim.

### 3.4 What This Paper Is

Paper 8 in the AgentCiv series. Title: something like "Scale-Invariant Duality in Collective Machine Intelligence: The Directed-Emergent Distinction as Structural Invariant."

This is the theoretical capstone of the series. It doesn't introduce a new mechanism. It observes what Papers 5 and 7 together reveal: that the framework's own fundamental distinction is self-similar across levels of abstraction.

Structure:
- Restate the directed/emergent duality from Paper 4
- Show Creator Mode (Paper 5) as directed-meta
- Show the Recursive Loop (Paper 7) as emergent-meta
- Demonstrate the duality at the third level (the interaction of Creator + Recursive Loop)
- Argue that scale-invariant self-similarity is a signature of fundamental structure
- Discuss implications: CMI has identified something intrinsic to collective intelligence, not an incidental categorisation

### 3.5 Build Requirements

This paper may be writable from theory alone, but is strengthened enormously by empirical demonstration:

- Run Creator Mode v1 and the Recursive Loop independently, showing they produce different types of discoveries
- Run them in combination, showing the interaction exhibits the same directed/emergent duality at a third level
- The city grid scoring dimensions provide the quantitative backbone for comparing outputs across all configurations

This is why the sequencing matters: Paper 6 (city grid) provides the measurement framework → Paper 7 (recursive loop) and Paper 5 build (Creator Mode v1) provide the two mechanisms → Paper 8 observes the pattern across them.

---

## 4. Project Sequencing

### 4.1 Dependency Chain

```
Paper 6: City Grid Benchmark
    │
    ├── Proves configuration variance is real and measurable
    │   (everything below depends on this being established)
    │
    ├──────────────────────────────┐
    │                              │
    ▼                              ▼
Paper 5 Build:                 Paper 7:
Creator Mode v1                Recursive Configuration Loop
(directed-meta)                (emergent-meta)
    │                              │
    │   Paper already written.     │   New paper required.
    │   Needs implementation.      │   Needs build + paper.
    │                              │
    └──────────────┬───────────────┘
                   │
                   ▼
            Paper 8:
            Scale Invariance
            (theoretical capstone)
            │
            Observes the pattern
            revealed by Papers 5+7.
            Strongest with empirical
            evidence from both builds.
```

### 4.2 Recommended Build Order

1. **City Grid Benchmark (Paper 6)** — First. Foundation. Everything else rests on this. Can be built quickly within existing Engine infrastructure. The visual output alone is a powerful demonstration.

2. **Creator Mode v1 Build** — Second. Paper 5 already exists. Build the primitive Creator as a meta-agent using both tools. Use the city grid as one of the Creator's tasks, so the Creator is immediately producing comparable, scoreable results.

3. **Recursive Loop Build + Paper 7** — Third. Connect the Simulation and Engine input-output spaces. Run N cycles. Measure configuration drift and outcome improvement. Write the paper articulating why this is a distinct mechanism from Creator Mode.

4. **Scale Invariance Paper (Paper 8)** — Fourth. The capstone. Requires Papers 5 and 7 to both exist and ideally both have empirical results. Observes the self-similar duality across abstraction levels. Can be drafted earlier from theory, but the argument lands hardest with evidence from all three builds.

### 4.3 What the Full Stack Looks Like When Complete

| Paper | Title | Type | Status |
|-------|-------|------|--------|
| 1 | From Agent Teams to Agent Civilisations | Vision / theoretical | Published |
| 2 | Civilisation as Innovation Engine | Conceptual argument | Published |
| 3 | Maslow Machines | Empirical (simulation) | Published |
| 4 | Collective Machine Intelligence (CMI + COT) | Field definition | Published |
| 5 | Creator Mode: AI as Civilisation Designer | Meta-mechanism (directed) | Paper written, build needed |
| 6 | City Grid Benchmark | Empirical validation | NEW — needs build + paper |
| 7 | Recursive Configuration Loop | Meta-mechanism (emergent) | NEW — needs build + paper |
| 8 | Scale-Invariant Duality | Theoretical capstone | NEW — needs paper |

Papers 1–3 identify the phenomenon. Paper 4 defines the field. Papers 5 and 7 are the two meta-level mechanisms (directed and emergent). Paper 6 is the empirical foundation that makes 5 and 7 credible. Paper 8 observes the structural pattern that 5 and 7 together reveal.

That's a complete intellectual arc from first observation through field definition through empirical validation through meta-level mechanisms through fundamental structural properties. Eight papers, two tools, two new fields (CMI and COT), and a theoretical result (scale-invariant duality) that positions CMI as having identified something fundamental about the nature of collective intelligence.

---

## 5. Key Terminology

| Term | Definition | Introduced |
|------|-----------|------------|
| **Directed-meta** | The directed mode of CMI applied to the meta-level: intentional search of the configuration space (Creator Mode) | This document / Paper 8 |
| **Emergent-meta** | The emergent mode of CMI applied to the meta-level: self-improving configuration through structural coupling without a directing intelligence (Recursive Loop) | This document / Paper 7 |
| **Scale-invariant duality** | The property that the directed/emergent distinction reappears at every level of abstraction in the CMI framework | This document / Paper 8 |
| **Configuration variance** | The empirically demonstrable fact that different organisational configurations produce measurably different outputs on the same task | This document / Paper 6 |
| **Structural coupling** | The property that two CMI tools with shared ontology can have their input-output spaces connected to form a self-improving loop | This document / Paper 7 |
| **Co-evolution (in CMI context)** | Cooperative co-evolution where team configurations and civilisation configurations each serve as the fitness landscape for the other | This document / Paper 7 |

---

## 6. Open Questions

1. **Does the recursive loop actually converge?** It's theoretically sound that connecting the tools creates a refinement dynamic, but empirically the loop might oscillate, diverge, or plateau. This is the central empirical question for Paper 7.

2. **How many cycles before measurable improvement?** If the loop requires 50 cycles to show improvement, compute costs may be prohibitive at v1. If it shows improvement in 3–5 cycles, the demo is powerful.

3. **Does the third-level duality manifest empirically?** Paper 8's strongest claim requires showing Creator + Recursive Loop interaction exhibiting directed/emergent dynamics at a third level. This may be observable or may require scale beyond v1.

4. **City grid scoring calibration.** The five scoring dimensions need to be weighted or presented independently. A city could score high on coverage but low on connectivity. The scoring framework needs to be designed so that aggregate scores are meaningful and not gameable.

5. **Does the recursive loop find things Creator Mode doesn't?** The theoretical argument says yes (no search bias), but this needs empirical demonstration. Run both mechanisms and compare the configurations they produce. If they produce non-overlapping discoveries, the complementarity claim is proven.

---

*This document should be treated as the expansion roadmap for the AgentCiv project. Everything described here is scoped, sequenced, and buildable. The city grid benchmark can begin immediately.*
