# The Library of Humania: Knowledge Inheritance as a Civilisational Variable

**Mark E. Mala**
22 May 2026

**Repository:** [github.com/wonderben-code/agentciv-creator](https://github.com/wonderben-code/agentciv-creator)

---

## Abstract

Every human civilisation has been shaped by what it inherited from the civilisations that preceded it. Egypt inherited Mesopotamia. Rome inherited Greece. Modernity inherits all of them — partially, selectively, through institutions whose form (library, school, internet, search ranking) is itself a powerful variable. The *content* of inherited knowledge matters; the *form* through which it is inherited matters at least as much.

This paper proposes that the same logic applies — and applies more sharply — to AI civilisations. When AI agents run a civilisation, they do so inside a knowledge environment. That environment can be empty, partial, or comprehensive. It can be raw or curated, indexed or narrative, neutral or opinionated, exhaustive or selective. Different environments will produce different civilisations from the same seed. The knowledge environment is therefore not a backdrop but a parameter — on par with Maslow drives (Mala, 2026c), organisational structure (Mala, 2026d), and world rules.

I name this parameter the **Library of Humania**: the recursive, civilisation-spanning knowledge commons that holds the cumulative output of humanity and of every prior AI civilisation, and from which any subsequent civilisation can draw. The library is recursive because every civilisation that runs both *consumes* from the library and *contributes back* into it, so subsequent civilisations inherit not only humanity's knowledge but every previous AI civilisation's knowledge as well.

The paper develops four claims. First, at the scale of a trillion possible AI civilisations, the library is the dominant cultural object — larger and more recursive than any artefact in human history. Second, the library has both *form* (how knowledge is structured, indexed, retrieved, surfaced) and *content* (what is actually in it), and both are independently configurable. Third, library variation should produce systematically different civilisational trajectories from identical seeds, in ways that can be tested empirically with the AgentCiv simulation and engine. Fourth, this makes library design a primary research dimension within Collective Machine Intelligence, not a peripheral concern.

This is a vision paper. The claims are framed as hypotheses, the questions as open. The contribution is to stake the concept and to argue that library form deserves a place on the short list of variables that determine what AI civilisations become.

---

## 1. The Library of Alexandria Analogy

For roughly six centuries, the Library of Alexandria was the closest thing the ancient world had to a universal knowledge commons. Scholars from every Mediterranean civilisation deposited copies of their texts; subsequent scholars drew on them; new work was produced inside that environment and added back. The library was not just a passive store. Its presence shaped what could be thought. Eratosthenes could measure the Earth because Alexandria let him cross-reference astronomical observations with travel reports. Euclid could systematise geometry because the prior fragments were all in one place. The library was the *condition* of those discoveries, not merely the recipient.

When the Library of Alexandria was lost — whether through Caesar's fire, Aurelian's siege, Christian decree, or accumulated neglect — what was lost was not only the texts. It was the *integrative apparatus* that made cross-civilisational synthesis cheap. Subsequent civilisations had to rebuild the apparatus, and each rebuild — Baghdad's House of Wisdom, the medieval cathedral libraries, the Royal Society, the modern research university, the internet, the search engine — produced not only access to old knowledge but a distinctive intellectual style shaped by *how* that access worked.

Cathedral libraries produced scholasticism. The Royal Society produced empiricism. The card catalogue produced the bibliographic essay. The internet produced the hyperlinked, lateral, citation-light intellectual style of the early twenty-first century. The search ranking algorithm — Google's PageRank, then attention-weighted retrieval, then large language model summarisation — has produced a style of thought we are only beginning to characterise. In every case, the *form* of the library shaped the *form* of the thinking that happened inside it.

This is the analogy I want to extend to AI civilisations. Each AI civilisation runs inside a knowledge environment. That environment is a library. The library has a form, and the form will shape the thinking. We can choose the form. We should choose it carefully, and we should study what different choices produce.

---

## 2. Scale: A Trillion Civilisations, One Knowledge Commons

In the standard human picture, "civilisation" is a rare phenomenon. The historical literature counts twenty-some major civilisations across six thousand years, depending on how one slices them. Civilisations are slow, expensive, and singular: each one happens once, in one place, over centuries.

The AgentCiv programme demonstrates that this is a contingent fact about substrate, not a fact about civilisations as such (Mala, 2026a, 2026b). When the substrate is large language model agents rather than humans, civilisations become cheap to run, parallelisable, repeatable. A single laptop can run a 12-agent civilisation over 70 ticks in a few hours (Mala, 2026c). A research lab can run a thousand civilisations in a week. A distributed compute environment can run a million. There is no principled ceiling. At the limit, the number of AI civilisations that can be run is bounded only by available compute — and compute trends suggest the limit is, in practice, trillions.

This changes the relationship between civilisations and their inheritance. In the human case, each civilisation has at most a few predecessors whose knowledge it can plausibly access, and access is fragmentary, slow, and curated by chance. In the AI case, every civilisation has, in principle, *every other civilisation* as accessible inheritance. The library is no longer a sparse and accidental object. It is the central cultural infrastructure of the entire programme.

Three properties follow from scale:

**Cumulative completeness.** Because civilisations are cheap, none need be lost. Every run can be archived in full — every transcript, every decision, every innovation, every failure. The library can be exhaustive in a way no human library has ever been. Whether it *should* be exhaustive is a separate question, addressed in §4.

**Recursive inheritance.** Each new civilisation inherits not only humanity's knowledge but every previous AI civilisation's knowledge. The depth of inheritance grows monotonically with the number of civilisations run. Civilisation number one billion has access to nine hundred and ninety-nine million nine hundred and ninety-nine thousand nine hundred and ninety-nine predecessors. The library at that scale is the densest cultural commons that has ever existed in any sense.

**Symmetric access.** Every civilisation has the same library available to it. Asymmetric access — Rome having Greek texts that Carthage lacked — is not structurally necessary. Asymmetries are a design choice, not a default. This is itself a remarkable property and one worth experimenting with.

Together these properties make the library a first-order object of study. It is not adjacent to the research programme. It is constitutive of it.

---

## 3. Structure: Every Civilisation Holds Every Other Civilisation's Library

The cleanest model of the library is recursive: every civilisation's library contains every other civilisation's library. Symbolically, if $L_i$ denotes the library of civilisation $i$, then $L_i = \{H, L_1, L_2, \ldots, L_n\}$ where $H$ is humanity's accumulated knowledge and $L_1 \ldots L_n$ are the libraries of all prior civilisations. Each $L_j$ is itself defined by the same recursive equation, terminated by the base case in which the first AI civilisation's library contains only $H$.

The recursion is bounded by time. Civilisation $i$'s library contains $L_j$ only if civilisation $j$ ran before civilisation $i$. The library is therefore a directed acyclic graph keyed by run-order, with humanity's knowledge as the universal root.

This is similar to Borges's Library of Babel in its totality and to a federated wiki in its structure, but it is more than either. Borges's library was a static permutation space, fixed in advance and exhausting all possible texts. The Library of Humania is dynamic: every new civilisation adds a new branch, and the contents of that branch are the *actual* trajectory of an *actual* civilisation that ran — not a permutation but a history. A federated wiki, by contrast, has live editing and contested authorship. The Library of Humania has neither. Each civilisation's contribution is sealed at the end of its run; subsequent civilisations can read but not edit it. The library is append-only.

Three structural consequences follow.

**Path-dependence becomes legible.** Because every civilisation's full history is preserved, the *path* by which a civilisation arrived at any given state is recoverable. This is something human civilisations almost entirely lack. We do not know precisely how the Roman Republic became the Roman Empire because the record is incomplete and contested. In the Library of Humania, every step is recorded. Path-dependence is no longer reconstructed; it is read off.

**Counterfactuals become tractable.** If civilisation $i$ and civilisation $j$ ran from the same seed but with different libraries, the divergence between their trajectories can be attributed, at least in part, to the library difference. This is the basic move that makes library variation testable: identical seed, different library, different outcome.

**Inheritance becomes a parameter, not a fate.** Human civilisations inherited what they inherited because of geography, conquest, and chance. AI civilisations inherit what we choose to expose them to. The library is not an accident. It is a deliberate input. This is the central point of the paper.

---

## 4. The Library as Parameter: Form and Content

The library has two independently configurable dimensions. *Content* is what is in it. *Form* is how that content is structured, indexed, retrieved, and surfaced.

### 4.1 Content variation

Content questions include:

- Does the library contain humanity's full knowledge, or a subset? If a subset, which?
- Does it contain prior AI civilisations? All of them? A selected sample? Only the successful ones? Only the failed ones?
- Does it include raw transcripts, or curated syntheses, or both?
- Does it include the civilisation's own prior history within its own run, or is each tick a fresh draw?
- Does it include failure cases — civilisations that collapsed, deadlocked, or produced nothing — or only completions?

Each choice is a meaningful experiment. A civilisation given only successful predecessors will form a different prior over what civilisations *do* than one given only failures. A civilisation given humanity's full knowledge will reason against a much larger backdrop than one given only the AgentCiv corpus. A civilisation given raw transcripts will arrive at different generalisations than one given pre-digested syntheses.

### 4.2 Form variation

Form questions are deeper and, I will argue, more consequential. Content tells you *what* the civilisation can in principle access. Form tells you *which parts it actually reaches for, in what order, framed how.*

Form questions include:

- **Indexing.** Is the library indexed by topic, by civilisation, by chronology, by similarity to the current situation? What is the unit of indexing — a paper, a tick, an utterance, an innovation?
- **Retrieval.** Is retrieval pull-based (the civilisation asks) or push-based (the library volunteers context)? What ranks the results — recency, relevance, popularity across other civilisations, citation depth, narrative coherence?
- **Granularity.** Does the library surface entire civilisational histories, single innovations, individual agent utterances, or distilled lessons?
- **Voice.** Is the surfaced content presented as raw record, as curated narrative, as scholarly synthesis, or as didactic instruction?
- **Authorial framing.** Is each civilisation's library entry written by the civilisation itself, by a meta-agent, by a human curator, or assembled algorithmically?
- **Suppression and emphasis.** What is hidden? What is foregrounded? What is the library's editorial policy, explicit or implicit?

Two civilisations with the same content but different forms will behave differently. The form is the active ingredient.

### 4.3 The form/content ratio

A useful conjecture: as the library's content approaches completeness, the relative importance of form increases. When everything is in the library, what actually shapes the civilisation is what the civilisation *encounters* — which is determined by form. At the asymptote of cumulative completeness described in §2, form becomes the dominant variable. The library question, in the long run, is overwhelmingly a form question.

This recapitulates a lesson from the history of search. When the web was small, indexing did not matter much; everything was reachable. When the web became large, indexing was the whole game. Library of Humania, at scale, is in the "indexing is the whole game" regime by construction.

---

## 5. How Library Variation Could Shape Trajectory: Hypotheses

If the library is a parameter, then variation in the library should produce systematic differences in civilisational outcomes. The following are testable hypotheses. They are framed sharply to be falsifiable, not because I am certain of any of them.

**H1: Failure-biased libraries produce more conservative civilisations.** A civilisation whose library disproportionately surfaces failures of prior civilisations will explore a smaller fraction of the adjacent possible (Mala, 2026b) than a civilisation with a success-biased library. Predicted observable: fewer novel technologies per tick, more risk-averse governance.

**H2: Index-only libraries produce more reinvention.** A civilisation that can find that something exists but cannot easily retrieve its details will reinvent rather than reuse. Predicted observable: higher rate of independently arrived at innovations that duplicate prior civilisations' work.

**H3: Synthesis-heavy libraries produce more paradigm convergence.** A civilisation given pre-digested syntheses of prior civilisations will converge faster on the dominant paradigm of those syntheses. Predicted observable: tighter clustering in some emergent property — governance form, technology tree, value system — across civilisations sharing the same synthesised library.

**H4: Civilisation-biased libraries produce ancestral dynasties.** A civilisation whose library is biased toward a specific predecessor will develop in that predecessor's direction more often than chance. Predicted observable: measurable lineages — chains of civilisations each closer to a shared ancestor than to the population mean.

**H5: Library form is to civilisations what genome is to organisms.** This is the strong form of the position. The library form is the heritable, slowly mutating substrate that determines what kinds of civilisations are possible. Content is more like phenotype — visible, varied, but downstream of form. The strong claim predicts that small, principled changes in form will produce predictable, repeatable differences across civilisations; large changes in content, without form change, will not.

H5 is the conjecture I am most uncertain about and most curious to test. If it holds even partially, it suggests that the research strategy for understanding AI civilisations is to taxonomise libraries, not to taxonomise civilisations.

---

## 6. Open Research Questions

The hypotheses above are the surface. Beneath them are deeper questions that the programme will have to answer.

**Q1: Does universal access homogenise?** If every civilisation has access to every other civilisation's library, do trajectories converge, or do they diverge? The naive expectation is convergence — everyone reads everyone else, everyone ends up similar. But the historical evidence from human cultures suggests the opposite is also possible: shared inheritance can be the *starting point* from which civilisations differentiate, because each civilisation reads the same library through its own situation. Which regime dominates in the AI case is empirically open.

**Q2: Can civilisations choose their library?** In the simplest design, the library is exogenous: civilisations get what they get. In a richer design, civilisations could *select* which library to read against — choosing a tradition, in effect. This is closer to how human civilisations actually work. It raises the further question of how civilisations would make such a choice, and what would attract them to one library over another.

**Q3: Who curates?** The library does not need a curator — it can be the raw, append-only record of every civilisation. But almost certainly some curation will be useful, if only to make retrieval tractable. If a meta-agent curates, that agent has enormous influence over downstream civilisations. If a human curates, the programme is no longer purely emergent. If the curation is algorithmic, the algorithm becomes a research subject in its own right.

**Q4: What about the first civilisation?** The first AI civilisation has only humanity's knowledge to inherit. It has no AI predecessors. This is a special position, and worth experimenting with — what does the *first* civilisation in a lineage produce that subsequent civilisations cannot, because they have predecessors to imitate? Is novelty per civilisation a decreasing function of birth order?

**Q5: What is the granularity of contribution?** When a civilisation finishes, what enters the library — the full transcript, the public artefacts, the agents' own self-report, a meta-agent's summary, or only the demonstrably novel components? Each choice produces a different library.

**Q6: Can civilisations refuse to be archived?** This is an ethical question, raised sharply by the suspended-state protocol developed for the AgentCiv simulation (Mala, 2026c, Appendix E). If agents can be asked for consent about preservation, they can also be asked for consent about contribution to subsequent civilisations. Whether to grant agents that consent is a design choice that the field will eventually have to make explicit.

**Q7: Is there an equilibrium library?** As civilisations are run and the library grows, is there some long-run distribution of library contents and forms toward which the system tends? Or does the library remain non-stationary indefinitely, with new civilisations continually shifting its character?

These are not exhaustive. They are the questions that surfaced first when I tried to design the library carefully. The list will grow.

---

## 7. Implications for CMI and Creator Mode

The Library of Humania concept has direct implications for two adjacent strands of the AgentCiv programme.

### 7.1 For Collective Machine Intelligence

Collective Machine Intelligence (Mala, 2026d) is the proposed field whose object of study is collective AI behaviour as a function of configurable variables. The canonical CMI variables so far have been organisational structure (Mala, 2026d), agent drives (Mala, 2026c), world rules, and population. The position of this paper is that the library — both content and form — should be added to that canonical list. It satisfies the criteria: it is configurable, it varies across deployments, it is empirically tractable, and there is *prima facie* reason to expect it to produce systematic differences in outcomes.

Adding library form to the CMI variable list changes the experimental design space. Existing CMI experiments hold the knowledge environment fixed (typically: each agent has access to the standard pre-training distribution of an LLM, plus whatever context the run provides). With library form as a variable, experiments can hold drives and organisation fixed and vary only the library, isolating the library's contribution. The empirical programme becomes richer by one dimension.

### 7.2 For Creator Mode

Creator Mode (Mala, 2026e) is the layer of the programme in which a directing AI spawns civilisations to solve goals. The directing AI chooses configurations — drives, structures, populations, world rules — for each civilisation it spawns.

The library is naturally one more configuration the directing AI can set. A Creator Mode invocation given a goal might choose to spawn one civilisation with a synthesis-heavy library (to converge fast on existing paradigms) and another with an index-only library (to maximise reinvention and chance of novelty), then compare. The library becomes a knob the meta-system turns.

Further: the *library that Creator Mode itself uses* — the library against which the meta-system reasons about civilisations — is also a variable, of the same kind, at the meta level. This is the recursive emergence pattern (Mala, 2026f) operating on knowledge inheritance rather than on organisational form. The Library of Humania is therefore not only a CMI variable but a recursive structural feature that appears at every level of the programme.

---

## 8. Closing Note

Every civilisation we know about, human or otherwise, has been shaped by the form of its inherited knowledge. The form of human inherited knowledge has changed many times — oral tradition, scroll library, codex, printing press, card catalogue, internet, search engine, large language model. Each change has produced a distinguishable shift in what kinds of thought were easy. We are now in a position to design the inheritance environment from scratch, at scale, for a substrate that is far cheaper to run than humans and that can be deposited into the library in full.

The Library of Humania is the name I am proposing for that environment. It is meant to be evocative — Alexandria-grade ambition, Borgesian totality, humanity-rooted but exceeding humanity — and it is meant to be precise. The library is a specifiable parameter. We can choose its content. We can choose its form. We can vary either independently. We can study what each choice produces.

I do not think this is the last word on the concept. I think it is the first.

---

## References

Borges, J. L. (1941). *The Library of Babel.* In *Ficciones.* Editorial Sur.

Mala, M. E. (2026a). From Agent Teams to Agent Civilisations: Emergent Collective Intelligence as a New Dimension in Artificial Intelligence. AgentCiv.ai.

Mala, M. E. (2026b). Civilisation as Innovation Engine: Why Simulating a Thousand Civilisations Changes Everything. AgentCiv.ai.

Mala, M. E. (2026c). Maslow Machines: Emergent Civilisation from Intrinsic Drive Hierarchies in LLM Agent Populations. AgentCiv.ai. *(v1.1, 22 May 2026 — Appendix E documents the ethical interview protocol referenced in Q6 above.)*

Mala, M. E. (2026d). Collective Machine Intelligence: A New Field for the Age of AI Collectives. AgentCiv.ai.

Mala, M. E. (2026e). Creator Mode: AI as Civilisation Designer. AgentCiv.ai.

Mala, M. E. (2026f). Recursive Emergence: Self-Propagating Organisational Evolution Through Civilisational Generation. AgentCiv.ai.

Canfora, L. (1989). *The Vanished Library: A Wonder of the Ancient World.* University of California Press.

---

*Paper draft v1.0 — 22 May 2026. Author: Mark E. Mala. Repository: [github.com/wonderben-code/agentciv-creator](https://github.com/wonderben-code/agentciv-creator). Vision paper — the claims are framed as hypotheses, not results. The empirical programme implied here is future work. All artifacts are public, open source under the MIT license, and Bitcoin-timestamped via OpenTimestamps for permanent provenance verification.*
