# Creator Mode Research Experiment Plan

## The Four-Phase Autonomous Discovery Protocol

**Purpose:** Demonstrate that Creator Mode is not just an experiment runner, but a learning system — one that gets smarter with every campaign, discovers novel configurations that outperform human-designed presets, and transfers knowledge across tasks.

**What this proves:** Creator Mode is the Neural Architecture Search of organisational structure for multi-agent AI systems.

---

## What Creator Mode IS (The USP)

Creator Mode's USP is that it's an AI that autonomously designs, spawns, observes, analyses, and iterates on AI civilisations — it turns the infinite possibility space of collective machine intelligence into something that can actually be explored systematically.

The key insight: the CMI possibility space (scale x intelligence x configuration x application x emergence) is infinite. No human can explore more than a tiny fraction. Creator Mode removes the human from the exploration loop and replaces them with an AI whose entire purpose is to design better civilisations based on what it learned from previous ones.

The dogfood run proves the pipeline works. The research experiment proves the pipeline **learns**.

## What the Research Demo Must Show

Three things, in order of importance:

### 1. Knowledge Accumulation (The Learning Curve)
Creator Mode gets SMARTER across campaigns. Campaign N+1 converges faster than Campaign N because it uses findings from N. This is THE proof that the system learns.

**Metric:** Runs-to-convergence decreasing across sequential campaigns on related tasks.

### 2. Autonomous Discovery (Beyond Named Presets)
The recursive emergence loop produces a novel configuration — a combination of organisational dimensions that wasn't in any of the 13 named presets — and it outperforms all of them.

**Metric:** Evolved config quality > max(all 13 named presets) on the same task.

### 3. Cross-Task Knowledge Transfer
Findings from Task A improve predictions on Task B. The system doesn't just learn about specific tasks — it learns about organisational dynamics that generalise.

**Metric:** Knowledge-informed search on new task outperforms blind grid search (fewer runs to find winner, or higher quality at same run budget).

---

## The Four Phases

### Phase 1: Blind Exploration — Baseline
**Question:** "What org structure produces the best utility functions?"
**Task:** "Write a Python module with 5 utility functions (string manipulation, list operations, date formatting, input validation, file path handling) with full test coverage."
**Strategy:** Grid search — all 13 presets x 3 runs = 39 runs
**Agents:** 4, Model: claude-sonnet-4-6, Max ticks: 30

**What this proves:** Creator Mode can systematically explore the full preset space and extract statistically significant findings from scratch. This is the baseline — no prior knowledge.

**Expected outputs:**
- Rankings of all 13 presets with confidence intervals
- 5-10 statistically significant findings (pairwise comparisons)
- Hypothesis generation from findings (what SHOULD work next)
- Coverage map: which dimensions actually matter for this task type

**Estimated cost:** ~39 runs x $6 = ~$234
**Estimated time:** ~2.5 hours (runs execute with bounded parallelism)

### Phase 2: Knowledge-Informed Search — Learning Proof
**Question:** "What org structure produces the best data structures?"
**Task:** "Write a Python module implementing Stack, Queue, and LinkedList with full test coverage and edge case handling."
**Strategy:** Hypothesis-driven (using Phase 1 findings)
**Agents:** 4, Model: claude-sonnet-4-6, Max ticks: 30

**What this proves:** Creator Mode uses Phase 1 findings to skip bad configs and focus on the promising region. It converges faster than blind grid search.

**Key comparison:** Phase 2 should reach a winner in ~12-15 runs (vs Phase 1's 39) because the hypothesis engine generates targeted experiments based on what it already knows.

**Expected outputs:**
- Faster convergence (fewer runs to identify winner)
- Hypotheses validated or refuted by Phase 1 knowledge
- NEW findings that combine with Phase 1 findings
- Cross-task patterns emerging (e.g., "auto mode's speed advantage generalises")

**Estimated cost:** ~15 runs x $6 = ~$90
**Estimated time:** ~1 hour

### Phase 3: Recursive Evolution — Novel Discovery
**Seed:** Best config from Phase 2
**Task:** Same as Phase 2 (data structures)
**Strategy:** Recursive emergence loop — 5 generations x 6 configs x 2 runs = 60 runs
**Mutation rate:** 0.3

**What this proves:** Evolution discovers a novel configuration that outperforms all named presets. The recursive loop extracts emergent organisational forms and breeds them.

**Key comparison:** Evolved config quality > best named preset quality on the same task.

**Expected outputs:**
- Evolution trajectory showing quality climbing across generations
- The final evolved config (a specific combination of dimension values)
- Statistical comparison: evolved vs best preset (with effect size and p-value)
- The "agents designed their own winning structure" moment

**Estimated cost:** ~60 runs x $6 = ~$360
**Estimated time:** ~4 hours

### Phase 4: Transfer Test — Generalisation Proof
**Question:** "What org structure produces the best API?"
**Task:** "Write a Python REST API with 3 endpoints (CRUD operations), input validation, error handling, and tests."
**Strategy:** Knowledge-gap (using ALL accumulated findings from Phases 1-3)
**Agents:** 4, Model: claude-sonnet-4-6, Max ticks: 30

**What this proves:** Knowledge from utility functions and data structures TRANSFERS to API development. The system predicts what will work on an unseen task type.

**Key comparison:** Knowledge-informed prediction vs actual winner. How close does the recommendation engine get?

**Expected outputs:**
- Recommendation accuracy: does the predicted config rank in top 3?
- Transfer efficiency: fewer runs needed than Phase 1 blind search
- Cross-domain findings: what organisational dynamics are universal?
- The cumulative knowledge store is now genuinely useful

**Estimated cost:** ~12 runs x $6 = ~$72
**Estimated time:** ~45 minutes

---

## Total Budget

| Phase | Runs | Estimated Cost | Time |
|-------|------|---------------|------|
| Phase 1: Blind Exploration | 39 | ~$234 | ~2.5h |
| Phase 2: Knowledge-Informed | 15 | ~$90 | ~1h |
| Phase 3: Recursive Evolution | 60 | ~$360 | ~4h |
| Phase 4: Transfer Test | 12 | ~$72 | ~45m |
| Hypothesis engine LLM calls | — | ~$5 | — |
| **Total** | **~126** | **~$761** | **~8.5h** |

### Budget-Constrained Alternative (~$200)
If full budget isn't available, run a scaled-down version:
- Phase 1: 5 presets x 3 runs = 15 runs (~$90)
- Phase 2: Hypothesis-driven, 3 configs x 2 runs = 6 runs (~$36)
- Phase 3: 3 generations x 4 configs x 2 runs = 24 runs (~$144) — SKIP if over budget
- Phase 4: 6 runs (~$36)

Scaled total: ~$200-300, still proves learning curve and transfer.

---

## Paper Outputs

### Figures
1. **Convergence Curve** — Runs-to-winner across phases (39 -> 15 -> 8). The SLOPE of this line is the learning rate.
2. **Evolution Trajectory** — Quality score by generation in Phase 3, with named preset baselines marked.
3. **Knowledge Graph** — Findings connected across campaigns. Finding from Phase 1 led to hypothesis in Phase 2 led to discovery in Phase 3.
4. **Transfer Matrix** — Which findings from Task A predicted success on Task B.

### Tables
1. **Full Rankings** — All configs tested, with mean quality, std, conflicts, ticks, p-values.
2. **Named Presets vs Evolved Config** — The money table. Does evolution beat human design?
3. **Hypothesis Verdicts** — All hypotheses generated, their predictions, and what actually happened.
4. **Cost Efficiency** — Dollar cost per unit of knowledge (findings per dollar, convergence rate per dollar).

### Narrative
The paper tells a story in four acts:
1. **Act 1:** Creator Mode explores the full space and maps the terrain (Phase 1)
2. **Act 2:** It uses what it learned to search smarter (Phase 2 — the learning proof)
3. **Act 3:** It evolves something nobody designed (Phase 3 — the discovery)
4. **Act 4:** Its knowledge transfers to new domains (Phase 4 — the generalisation)

---

## Dogfood Run Results (V1 System Test — 7 April 2026)

Preliminary system test with 3 campaigns, 14 runs, $83.53 cost.

### Key Findings:
- **Full pipeline works:** question -> hypotheses -> experiments -> analysis -> findings -> reports
- **Hypothesis engine works:** Generated 5 real hypotheses via Claude Sonnet, 1 supported, 4 inconclusive
- **Statistical analysis works:** Extracted 2 statistically significant findings (auto mode speed advantage, p < 0.0001)
- **Knowledge accumulates:** Recommendation engine correctly identified auto as best overall based on accumulated evidence
- **Auto mode uses fewer ticks** (7-8 vs 13-15 for hierarchical), the one clear signal
- **Quality scores compressed** at 3 agents / 15 ticks on simple tasks (0.408-0.485 range) — need more agents, ticks, and task complexity for the full experiment

### Lessons for Full Experiment:
1. Use 4 agents minimum, 30 ticks — gives enough room for org structure to matter
2. Use moderately complex tasks — simple tasks compress quality differences
3. Each run costs ~$6 (750K tokens) not ~$1.50 as originally estimated
4. Engine runs take 4-6 minutes each
5. Auto mode's consistent speed advantage suggests it self-organises quickly and efficiently

---

## Implementation Notes

The full experiment runs via the existing Creator Mode infrastructure:
- `creator_dogfood(action="start")` — begins data capture session
- `creator_explore(strategy="grid", execute=True)` — Phase 1
- `creator_explore(strategy="hypothesis", execute=True)` — Phase 2
- `creator_recursive(execute=True)` — Phase 3
- `creator_explore(strategy="knowledge", execute=True)` — Phase 4
- `creator_dogfood(action="complete")` — exports dataset

All data captured automatically: environment, costs, LLM responses, chronicles, findings, reports.
Dataset export produces a single JSON with everything needed for paper tables and figures.
