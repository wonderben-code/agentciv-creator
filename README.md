# AgentCiv Creator Mode

**Give it a goal. It spawns a civilisation to solve it.**

An AI system that orchestrates the [AgentCiv Engine](https://github.com/wonderben-code/agentciv-engine) and [Simulation](https://github.com/wonderben-code/agent-civilisation) as sub-modules — spawning civilisations of AI agents toward directed goals, emergent discovery, or autonomous research.

*Mark E. Mala, April 2026*

## Install

```bash
pip install git+https://github.com/wonderben-code/agentciv-creator.git
```

## Use with Claude Code (or any MCP client)

```bash
claude mcp add agentciv-creator -- python -m creator.mcp
```

Then in conversation:

```
> Build a REST API with auth, rate limiting, and tests.

Analysing goal...
  Mode: directed · Confidence: 0.91
  Strategy: grid comparison

Spawning 5 civilisations...
```

## What it does

**Three campaign modes:**

- **Directed** — spawn civilisations with different team structures, all working your task. Measures everything. The data shows which approach wins.
- **Emergent** — give agents a domain and let them self-organise. No hierarchy, no assigned roles. Extract what's valuable from what they create.
- **Auto** — describe your goal. Creator Mode analyses it, picks the right mode and strategy, and runs it.

**v1 capabilities:**

- **Meta-reasoner** — 4-factor heuristic that analyses your goal and selects the best campaign mode
- **9-dimension translator** — maps emergence findings (governance, cooperation, innovation, etc.) to Engine organisational configurations with confidence scores
- **Knowledge Store** — findings, hypotheses, and results persist across campaigns. Cross-mode retrieval surfaces relevant discoveries.
- **7 MCP tools** — explore, spawn directed/emergent campaigns, analyse results, retrieve knowledge, recursive evolution

## v1 is a proof of concept

A handful of conditions. Dozens of agents. Heuristic reasoning. Keyword-based search. It's primitive — and nothing like it has ever existed.

It proves the architecture works: civilisations can be spawned toward goals, knowledge persists across runs, directed and emergent exploration can be orchestrated by a single system.

## Architecture

```
Creator Mode
  ├── Meta-reasoner (goal → mode selection)
  ├── Campaign Manager (plan → run → analyse)
  ├── Translator (emergence → engine config)
  └── Knowledge Store (findings, hypotheses, results)
        │
        ├── AgentCiv Engine (directed campaigns)
        │   13 presets · 9 organisational dimensions
        │
        └── AgentCiv Simulation (emergence campaigns)
            12 presets · 7 dimensions · Maslow-driven agents
```

## The AgentCiv Research Programme

| # | Paper | Repo |
|---|-------|------|
| 1 | From Agent Teams to Agent Civilisations | [agent-civilisation](https://github.com/wonderben-code/agent-civilisation) |
| 2 | Civilisation as Innovation Engine | [agent-civilisation](https://github.com/wonderben-code/agent-civilisation) |
| 3 | Maslow Machines | [agent-civilisation](https://github.com/wonderben-code/agent-civilisation) |
| 4 | Collective Machine Intelligence | [agentciv-engine](https://github.com/wonderben-code/agentciv-engine) |
| **5** | **Creator Mode: AI as Civilisation Designer** | **this repo** |
| 6 | The Creator Mode Architecture | this repo |
| 7 | Same City, Different Architects | [agentciv-engine](https://github.com/wonderben-code/agentciv-engine) |

Website: [agentciv.ai](https://agentciv.ai)

## Provenance

All commits Bitcoin-timestamped via OpenTimestamps. Papers published on [Zenodo](https://zenodo.org) with DOIs.

## License

MIT — see [LICENSE](LICENSE).
