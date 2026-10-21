# Pre-study: designer/architect and design-review seats (2026-10-21)

The owner asked whether two new seats should be added to the working process: a designer/architect and a design/architecture reviewer. Under the proposal, roster groups above a size threshold gain two steps, design and design review, before the fixer starts. This pre-study:
- grounds both roles in published, widely used role definitions;
- measures the programme's own review history;
- models the effect on completion time, first-pass yield (FPY), token use and how often bugs are introduced.

It is a study on the reading branch, not a proposal for `main`. The draft contracts are `designer.md` and `design-review.md` in this directory.

## 1. Answer

| variant | completion time (round 10, from adoption) | FPY, groups that get the steps | tokens, whole programme | bugs introduced | verdict |
|---|---|---|---|---|---|
| **As asked: serial steps on every group at or above L** | **+1 to +24 h** (mid +12 h: 86 → 98 h; 104 h at today's slip) | L/XL 0.17 → 0.18–0.31 | +1.4 to +5% | −1 to −20% (mid −6%) | **negative**: the round breaches its 100-h demand at today's slip |
| Serial, threshold M | +7 to +27 h | M 0.47 → 0.49–0.61 | +5 to +11% | about the same as L | negative |
| **Pipelined:** the design is drafted while the group's predecessor is in flight, reviewed before dispatch, revalidated at dispatch | 0 to +1 h at low/mid effect; −6 h only at the optimistic effect. **+6 h if revalidation takes 2 h, +16 h at 4 h** | as above | +1.4 to +5% | −1 to −20% (mid −6%) | **neutral** on time; slightly negative on tokens; positive on bugs |
| Pipelined, XL only | 0 h | XL as above | about +1 to +2% | about −3% | neutral, and small |

**Conclusion: neutral at best for round 10.** The steps don't pay for themselves inside the round:
- **Throughput:** with serial steps it gets worse; pipelined it is unchanged unless designs need little revalidation.
- **Tokens:** they rise by a few per cent.
- **Bugs:** the gain is real but modest: about 6% fewer bugs introduced overall at the mid estimate, and about a quarter fewer design-class bugs.

The case for the seats is the next round's architecture debt, not this round's time. In round 10, 40% of the audit findings (49 of 123) came from the architecture dimension (D7, ARCH2, ARCH3). Six of the eight critical-chain links are L/XL, and two are pure architecture remediation (LIVESTATE, PARAMS-OWNER).

**Recommendation:** a narrow pipelined variant, piloted in round 11 (section 8), not adopted mid-round. Decision 0012's moratorium also bars new role contracts until 2026-10-31: `dev/governance/roles/*.md` matches `POLICY_GLOBS` (`tools/policy/policy_lint.mjs:258`).

## 2. Why the in-round gain is small: what the reviewers actually block

Measured by `tools/review_rounds.py` over every `review/<N>` bus ref: 146 reviewed pull requests, 148 blocked verdicts, #2206–#2580.

| measure | value |
|---|---|
| first-pass yield (first verdict is `merge`) | **0.42** |
| blocked verdicts per reviewed PR | **1.01**; rounds to merge 1.95 (133 PRs with a merge verdict) |
| wall time from a blocked verdict to the next verdict (h, p25/p50/p75/p90) | 0.60 / **1.35** / 2.52 / 5.63 |
| by size, where the delivery record names a group (39 PRs) | S n=23: FPY 0.39, 0.70 blocks/PR · M n=8: 0.38, 0.75 · L n=5: **0.00, 1.80** |

**Block classes:**
- **Evidence and bookkeeping, which a design step cannot remove:**
  - `harness` 33, `carry-missing` 27, `root-cause-*` 11;
  - the mutation classes, about 16;
  - `ci-red`, `tests-red` and `closures-red` 9, `head-moved` 5, body and figure staleness about 6.
- **Design-addressable:**
  - strict: `architecture-unsound` 1, `product-tradeoff-regression` 1, `policy-regression` 1, `defect` 1, `regression` 1, `metric-gamed` 2 — **7 of 148 (4.7%)**;
  - broad: adds `class-open` 8, a defect class still open at sibling sites, which a design that enumerates the sites would catch — **15 of 148 (10%)**.
- On the five L pull requests, the blocks were `carry-missing` 4, `harness` 2, `class-open` 1, `mutation-untriaged` 1 and `claims` 1. These are evidence classes, not design classes.

**What this means.**
- Inside a round, review rework comes mostly from evidence and bookkeeping, which the flow groups already target (JIDOKA, BODY-PATCH, the K14 path). A design step addresses only the 5–10% of blocks that are design-class.
- The model's mid case assumes the design also removes some evidence blocks, by naming the harness, the carries and the sibling sites up front: 15% in total.
- The high case, 35%, needs the published planning gains to transfer (self-planning up to +25.4% relative pass@1; a vendor spec benchmark at +17% relative merges). That is more than this block mix supports.

**Where the design defects actually surface: in the audits, after merge.**
- **Findings by dimension:** round 9's roster has 10 of 143 findings from D7 (7%). Round 10's has 49 of 123 from D7, ARCH2 and ARCH3 (40%), with 7 groups of kind `arch`.
- **Recurring classes:** the shared-config class `N-shared-config` recurs (2 groups in round 9, 5 in round 10). `dev/audit/rca/R10-N-no-expiry.md:53` records a shape "introduced by **fixes**".
- **Existing practice:** a written `architect_note` (`orchestrator.md` section 5, binding through `fixer.md` step 17) is on 32 of 108 round-10 groups. Fix review checks it at step 15. Six of the twelve not-started L/XL groups already carry an approved design or a prototype patch.

## 3. Published evidence (as fetched 2026-10-21)

**Role definitions with adoption signals**, used for the draft contracts:

| source | what it defines | adoption |
|---|---|---|
| BMAD-METHOD Architect agent | "turns product requirements and UX into technical architecture" | 54.4k stars |
| GitHub spec-kit | specify → plan → tasks → implement | 142.3k stars |
| Kiro specs | `design.md` = "technical architecture, sequence diagrams, and implementation considerations", plus data models, error handling, testing | — |
| obra/superpowers | `brainstorming` "Activates before building anything"; `writing-plans` breaks work into 2–5-min tasks with exact paths and verification steps | 303.0k stars |
| wshobson/agents `architect-review` | "Architectural consistency analysis and pattern validation" | 41.4k stars |
| wshobson/agents `backend-architect` | "API design, microservice boundaries, database schemas" | (same repo) |
| VoltAgent awesome-claude-code-subagents `architect-reviewer` | "Architecture review specialist" | 25.9k stars |
| Anthropic's Claude Code best practices | "Separate research and planning from implementation to avoid solving the wrong problem"; **"If you could describe the diff in one sentence, skip the plan."** | — |

**Effects, all with weak provenance.** None is a clean ablation on a programme like this one.

| claim | figure | provenance |
|---|---|---|
| A plan step improves pass@1 (Jiang et al. 2023) | up to +25.4% relative vs direct; +11.9% vs chain-of-thought | abstract snippet |
| Spec-driven vs none (vendor) | 42 vs 36 of 50 tickets merged | single run |
| Aider architect/editor split | 85% vs previous best 79.7% | different models per row, not an ablation |
| MetaGPT (roles with an architect) | human revision cost 2.25 → 0.83 with executable feedback | secondary |
| MAST multi-agent failures | specification issues about 42% of failures | secondary |
| Agents vs chat; multi-agent vs chat | about 4× and about 15× tokens | Anthropic, primary |
| ChatDev | 59.4% of tokens go to code review | secondary |

**Human software engineering.**

| claim | figure | provenance |
|---|---|---|
| Defects by origin (Jones, per function point) | requirements 1.00, **design 1.25 (25%)**, code 1.75, documents 0.60, bad fixes 0.40 | |
| Removal efficiency by origin, all methods | design-origin about 85% vs code 95% | |
| Cost to fix relative to requirements (Boehm, secondary) | design 3.27, code 7.03, test 51.33, production 101.45 | critiques put small projects nearer 1:4 or 5:1 |
| Google design reviews | a tool cut median time to approval by 25% | no effect on defects reported |

No measured design-review-only removal rate was found. The model's 20/40/60% range is an assumption, bracketed by the "design-origin 85% by all methods" figure.

## 4. Model

**The projection.** `../tools/simulate.py` gained switches DESIGN, DTH, DSCALE, DFRAC, REWORK_H and REVAL_H (defaults off). The baseline is the revision-10 plan: `EFF=1 PAR=1 PRIO=1 RESERVE=1 CUT=gap`, roster base f424d993d, 86 h; 91 h with in-progress groups at 2× lead. For each not-yet-dispatched group at or above the threshold:
- **Serial:** lead += design hours − avoided rework.
- **Pipelined:** the group cannot dispatch before (its predecessors' latest dispatch + design hours), and lead += revalidation − avoided rework.
- **Design hours** (design seat plus design review, wall time), at DSCALE 1: M 2 h, L 3 h, XL 4 h. Where an approved design or prototype exists, the review only: 1, 1, 1.5 h. DSCALE 0.5 and 1.5 bracket them.
- **Avoided rework** = DFRAC × measured blocks per PR (S .70, M .75, L/XL 1.80) × 2.0 h per round. DFRAC low/mid/high is 0.05 / 0.15 / 0.35.

**FPY.** Blocks are treated as Poisson: FPY = e^(−λ), which fits the measured 0.42 against λ = 1.01. With design, λ' = λ(1 − DFRAC).

**Tokens**, in relative seat units:
- A fixer is 1.0, each review round 0.5, each rework round of the fixer 0.3.
- Design is 0.3 / 0.4 / 0.5 for M / L / XL, and design review 0.2 / 0.25 / 0.3.
- The programme share is weighted by size × measured lead: L/XL is 27% of the work, M and above 57%.

**Bugs introduced.** The change is −(design-origin share × design-review removal × share of design-origin defects the threshold covers):
- low: 0.07 × 0.2 × 0.6;
- mid: 0.25 × 0.4 × 0.6;
- high: 0.40 × 0.6 × 0.85.

The design-origin shares come from round 9's audit mix (7%), Jones (25%) and round 10's audit mix (40%).

The full grid is in `model-grid.txt`. Every figure is reproducible: `cd ../tools && env EFF=1 PAR=1 PRIO=1 RESERVE=1 CUT=gap DESIGN=pipe DTH=L DFRAC=0.15 python3 simulate.py ../roster/shadow-r10-groups.json 300`.

## 5. Results

**Completion time** (last roster merge, hours from adoption; baseline 86):

| | DFRAC 0.05 | 0.15 | 0.35 |
|---|---|---|---|
| serial, L+, DSCALE 0.5 / 1 / 1.5 | 92 / 102 / 110 | 90 / 98 / 108 | 87 / 96 / 104 |
| serial, M+, DSCALE 1 | 104 | 100 | 97 |
| pipelined, L+ or M+, DSCALE 0.5–1.5 | 86–87 | 86–87 | 80–81 |
| pipelined, L+, revalidation 2 h / 4 h | — | 92 / 102 | 90 / 102 |

At 2× in-progress lead, every row is 5–6 h later: serial mid 104 h, pipelined mid 91 h, against a 91-h baseline.

- **Serial steps put about 3 h on each L/XL link of the critical chain.** Six of its eight links are L/XL, so the round grows by 12–18 h.
- **Pipelining hides the design behind the predecessor's 10–17 h lead.** The cost moves into revalidation. That is the crux: a design drafted before its predecessor's code exists is only cheap if that code doesn't move the design. Round 10's chain is a sequence of refactors of the same coordinator (LIVESTATE → PARAMS-OWNER → HEAT-METER), which is the case most likely to need redesign.

**FPY** for groups that get the steps:
- L/XL: 0.17 → 0.18 / 0.22 / 0.31 (measured 0 of 5).
- M: 0.47 → 0.49 / 0.53 / 0.61.

Programme-wide FPY moves by about 0.2–2.4 points at the L threshold and about 0.6–4.5 points at M. The design review has its own first pass as well, which this model folds into the design hours.

**Tokens.** Per group that gets the steps: +20% / +15% / +5% (L) and +22% / +20% / +14% (M). Programme-wide that is +5.3% / +4.0% / +1.4% at the L threshold and about +11% / +10% / +5% at M. A pipelined design that needs reworking adds to this.

**Bugs introduced:** −0.8% (low), **−6%** (mid), −20% (high). Design-class bugs fall by 12%, 24% and 51%. This lands after the round, as fewer `arch` groups in the next audit, which the round-10 model does not credit.

## 6. Where the seats would pay

- **Architecture-kind groups and groups whose hot files include `coordinator.py`.** That is where round 10's 40% architecture findings and the recurring `N-shared-config` class live.
- **Groups with no prototype or approved design.** Six of the twelve not-started L/XL groups already have one, so there the reviewer step alone applies.
- **Groups off the critical chain, or pipelined with a short revalidation.**
- **Not:** S groups (Anthropic's own rule: "If you could describe the diff in one sentence, skip the plan"), or groups whose diff is a measured fix with a finder's harness. Those already carry their design in the finding and the architect note.

## 7. What the roles are (drafts)

The drafts are `designer.md` and `design-review.md`, written in the shape of `fixer.md` and `fix-review.md`:
- The **designer** produces one design note per group: owning seam, shape and interfaces, invariants, alternatives with the reason each was rejected, sibling sites, the harness and evidence plan, carries, and hot files. It extends the `architect_note` the orchestrator writes today rather than adding a second document.
- The **design reviewer** returns `Design review: approve|revise <sha>`. It reviews against the architecture brief (D7), `fixer.md` step 17, and the published reviewer definitions (consistency, pattern validation, boundaries). It reruns nothing, because there is no code yet. A design that changes behaviour the finding does not name is `revise`.

Both are time-boxed, never write production code, and are skipped below the threshold.

## 8. If the owner wants it: a round-11 pilot, not a round-10 change

1. **Scope:** L/XL groups that are of kind `arch`, or whose hot files include `coordinator.py`, and that have no prototype. Pipelined: the design starts when the group's last predecessor dispatches, and is revalidated within a 1-h box at dispatch. A redesign over that box is logged as a revalidation failure.
2. **Controls:** alternate eligible groups, design and no design, in roster order.
3. **Measures**, with `review_rounds.py` and the flow toolkit:
   - FPY and blocks per PR by arm;
   - design-review rounds;
   - revalidation hours;
   - seat token counts per group, if the seats report them (the tree records none today: `dev/audit` has no token or cost figures, only seat-hour estimates in RCA records);
   - the next audit's architecture findings attributed to pilot groups.
4. **Kill criteria:** median revalidation above 1 h, or no FPY gain after 8 designed groups. **Keep criteria:** design-class blocks and next-round D7 findings on designed groups fall by at least a quarter.
5. **Landing:** the two contracts are policy files, so they need the owner's review, after 2026-10-31. `policy_budgets.json` caps apply. Use new roster stages `design` and `design-review` in `roster_edit.py set-stage`, and bus refs `design/<group>` and `design-verdict/<group>` beside `review/<N>`. Use no new verdict class (moratorium): the reviewer uses `architecture-unsound` in fix review.

## 9. Limits of this study

- The size mapping covers 39 of 146 reviewed PRs: only PRs whose delivery record names a group. The L sample is 5.
- The design-addressable share is a classification of the verdict words, not a re-read of each review.
- Several external figures come from abstracts or secondary summaries (marked in section 3). arXiv and NIST were unreachable from this session.
- The token units are relative and assumed, not measured.
- The bug-introduction effect is modelled, not observed. The design-review removal rate has no published LLM figure.
