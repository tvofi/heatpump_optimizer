# Round 9 fix plan (step E2)

Final plan for tvofi, 2026-09-26. Drafted by the E2 fix-plan designer seat (strongest model) and
finished once the seven Phase D sweeps (S1–S7) had landed; section 9 lists what the sweeps changed. The
fourteen round-9 RCA seats then reported, and section 10 lists what their results changed (the RCA fold,
2026-09-26; tvofi's asks from them are collected in `TVOFI-ASKS.md` beside this file). Sections 11
and 12 carry tvofi's 19:05Z rules: every seat resumable from git after a crash, and every role routed to
the cheapest feasible model. It
is built from the judge's final class list (CLASSES-DRAFT.json at `bad458a3`, verdicts at `2f97b0a`), DEDUP.md, JUDGE.md/json,
RESUME.md ("PHASE F SHAPE", "FIX-PLAN CARRY-INS", "PR COUNT TARGET", "MODEL ROUTING", "NO HEAVY D3 RE-RUNS")
PLAN.md sections 7 and 8, and the sweep outputs `S1.json`–`S7.json` with their `SWEEP.md` files. Main at plan time: `db878b29` (after #1643). Baseline of every finding:
`1936d5ca` (v6.7.1).

Companion files, all generated from one data file so they cannot disagree:

- `handoff/round9/fix/F1.md` … `F11.md` — one fixer brief per lane (one cloud thread each).
- `.claude/workflows/wave-r9-groups.json` — the roster draft, one entry per PR, each with a `resume`
  field. `brief_lint.mjs` on it, run against an origin/main tree: exit 0, `TOTAL: 0 error(s)`.
- The tables at the end of this file (PR table, finding→PR, class→PR, owned files, merge queue).

## 1. The numbers

- **45 PRs in 11 lanes**, covering all 145 surviving findings (148 canonical less 3 refuted; the 7 merged
  ids travel with their canonical), all 14 counted instances beyond them (the sweeps' and the RCA
  fold's, sections 9 and 10) and 2 latent seams an RCA placed. tvofi (17:44Z): the PR count does
  not matter; the reasons for each PR are below.
- **Why not fewer.** `fixer.md` caps a PR at five findings and about 400 production lines, and PLAN
  §8.2 keeps that cap; a sweep instance counts toward it like a finding. So 145 findings need at least
  29 PRs. The rest come from three constraints: lanes own disjoint files, so a PR packs findings from
  one lane's files only and a lane's last PR is often part-full; 9 PRs need tvofi and are kept apart so
  nothing else waits on them; and one PR (F6.3) is a class barrier alone, because P9's barrier lives in
  `tests/card_browser.mjs`, which is code-owned.
- **Why 41 at the sweeps (superseded by the next bullet).** S7 raised "persisted future instant trusted without bound" from 2 to 7, so it
  owes an RCA seat and a barrier. Four of its five new instances are in `coordinator.py`, which only F1
  owns, and the instruction is that a class's sweep instances travel with its barrier PR where the lane
  allows. No F1 PR has more than two free slots, and one of the two
  roomiest, F1.10, is tvofi-gated, which would make the instances wait on tvofi. So the four
  instances and the barrier are a new PR, **F1.9** (the old F1.9 is now F1.10). Keeping 40 would mean
  merging two unrelated card PRs (F6.2 with F6.4), which delays the keyboard fix and the #1643 mutant pins
  behind F1.8 for no gain; I did not.
- **Why 45 after the RCA fold.** Four PRs were added, each forced by the five-item cap or by
  owner-gating: **F2.5** (the recompute RCA found the class's largest member, `peak_cost_batch`, and a
  closure the sweep mis-disposed, while F2.2 is at five); **F6.1b** (the P9 RCA's grid found four
  instances, while F6.1 is at five); **F1.11** (the old F1.10 would carry the P2, P3 and P6 barriers
  together, several hundred test lines, so P2 and P6 moved to their own PR); **F11.5** (the RCA seats
  drafted policy changes and landed none; the approved drafts need a PR, and it is tvofi-gated, so it is
  last in its lane and nothing waits on it). F1.9 stayed, shrunk: the future-instant barrier moved to
  F3.1, and F1.9 keeps the one seam no bound fixes plus the regression tests.
- **Why not more.** Classes are merged into one PR wherever they share a file set and fit the cap; a
  class over the cap (P2 with 27, I5 with 19, I1 with 11, P1 with 9) is split into instance PRs by
  subsystem with its barrier in the last one (PLAN §8.2). Instances fill PRs that already held their
  class where a slot is free: F1.6 (P1's two latent seams), F6.1 (one P9 instance), F2.2 (RC-sw1),
  F3.2 (FI-sw5's test), F4.2 (the new P5 instance, after D2-s4-02 moved to F4.1) and F1.9 (the
  future-instant tests); each is at five or under.

## 2. How the PRs were clustered

tvofi's order (13:04Z): class first, then shared file set, then fixer skill; owner-gated work in its
own PRs.

1. **Class first.** A class that fits one PR is one PR with its barrier (P5 in F4.2; the CPU-gate
   class in F10.2; the restart class in F1.4). A class whose instances sit in several lanes takes its
   barrier in a PR that waits on all of them (I5 in F10.4, I3 in F11.3, I4 in F11.4), unless its RCA
   measured the barrier's check not to read the later instances: P11's lands in F10.1 and the
   future-instant boundary in F3.1 (section 10), and the generator lists each such residual.
2. **Then file set.** The package has hub files that many classes touch: `coordinator.py`,
   `optimizer.py`, `config_flow.py` with the three translation files, the card, `sensor.py`. A class
   like P2 spans all of them, so one class PR would collide with every other lane. Instead **each file
   is owned by exactly one lane**, and each lane's PRs group that lane's findings by class where they
   can. This is what makes Phase F's "parallel groups have disjoint file sets" true.
3. **Borrowing, not sharing.** 16 PRs must edit a file another lane owns (a fix-together sibling
   pair across hubs, a cross-cutting finding, a barrier that reads every instance). Each lists the file
   under **Borrows** and carries an `after` edge on the owning lane's last PR on that file. The generator
   checks every pair of PRs that could be open at the same time and refuses the plan if any two touch the
   same file; it reports none. So, as declared, no two open branches ever edit one file, which is the property the
   disjointness rule protects, and conflicts are left only in the shared ledgers PLAN §9.4 already
   handles (`tests/features.py`, `tests/entities.py` by class-named sorted blocks; `closures.json` and
   `structure_budgets.json` re-recorded once at the hand-off; delivery rows one file per PR). The RCA fold
   adds two: `tools/audit/bugclasses.json`, where each barrier PR edits only its own class's entry, and the
   mutation ledger's `killed_by` rows.
4. **Then skill.** Lanes F5 (config flow and translated text), F8 (docs) and F9 (test pins) run on
   sonnet; everything else on the strongest model (tvofi 12:21Z).

The four fix-together sibling pairs DEDUP.md names each land in one PR: D12-s2-01 with D8-s1-03 in
**F2.4** (D12-s2-01 first, at both seams; D8-s1-03 then re-measures); D12-s1-01 with D12-s1-02 (merged
into D12-s3-01) in **F1.2**; D1-s5-01 with D1-s5-51 in **F4.1**; D8-s2-02 with D8-s2-03 in **F7.1**.
DEDUP's other "fix together" notes are honoured too (D1-s2-51/D1-s2-91 in F1.3; D7-s1-71/D5-s2-03 in
F2.3; D5-s1-01/D6-s2-01/D6-s2-02 in F8.1; D5-s1-05/D6-s1-02 in F8.2; the plausibility trio D1-s5-52 →
D1-s2-02, D1-s1-03 share F4.1's window and land in F1.6).

**Five findings are split across two PRs**, because their seams sit in two lanes' files; each closes
when its last PR merges, and the first PR's body says "leaves #N open":

- D14-s4-01 (high, P7): its `get_current_action` seam in F2.1 (first, and short), everything else plus
  the DST tracer barrier in F1.1, which waits on F2.1.
- D5-s1-02: the quick-setup text in `en.json`/`sv.json` (an L2 extra seam) in F5.1, `docs/setup.md` in F8.3.
- D6-s2-03: the figure in `strings.json` (an L2 extra seam) in F5.1, the docs in F8.3.
- D14-s4-02 (P11 RCA): the stub half (freeze normalisation, `utcnow` under an aware freeze) in F10.1, with
  the P11 barrier; the replay half in F1.1, which waits on F10.1.
- D6-s2-05 (I5 RCA): the `simulate_plan` field list in F8.1; the two service seams the I5 RCA found in F8.3.

## 3. Phase F shape (tvofi "Yes", 12:11Z)

- **Mac fix orchestrator** keeps PR authoring (`hpo-author` via `app_push.sh`), approvals
  (`hpo-approver`; tvofi's own review for code-owned and policy paths), merges one at a time with
  `--match-head-commit`, and the stamp.
- **One cloud fixer thread per lane (F1–F11)**, started from `fix/F<n>.md`, pushing each PR to
  `handoff/<lane topic>-<k>` (for example `handoff/r9-f1-coordinator-3` for F1.3). A thread works its
  lane's PRs in order and may prepare the next while the previous is in review; it merges `origin/main`
  (never rebases) before each hand-off and re-executes `fixer.md` steps 2–8.
- **Reviews** by the cloud helpers (Cloud compute helper, Cloud reviewer 2) on the strongest model,
  never the session that wrote the fix and never both reviewers on one PR. **Add a third reviewer when
  more than two hand-offs are waiting** — with ten lanes starting together that is likely within the
  first few hours.
- **RCA seats**: 15, one per `rca: true` class; fourteen ran before fixing (tvofi, 17:44Z) and
  have reported, and the fifteenth (the restart class) is RC2's, merged. Each named its barrier's form
  and left a prototype branch; the fixer of the PR that lands the barrier cherry-picks it (section 5).
- **Startable at once (wave 1):** F2.1, F3.1, F4.1, F5.1, F6.1, F7.1, F8.1, F10.1, F11.1 — nine
  threads, one per lane; F9's first PR now waits on F3.1 (F3.1 borrows `tests/finite_boundary.py`), and
  F1's thread starts with F1.1 once F2.1, F3.1 and F10.1 merge.

## 4. What needs tvofi, and why (answerable in one pass)

**Owner-gated PRs (9)** — each is its own PR so nothing else waits on it (generated from the
plan data; the old F1.10 is no longer gated: no barrier needs `tests/harness.py` after the RCA fold):

| PR | why tvofi |
|---|---|
| F6.3 | tests/card_browser.mjs is code-owned |
| F7.3 | the fix overturns the owner's recorded A3(e) decision pinned in tests/entities.py; tvofi rules first **Blocked on:** tvofi ruling on the A3(e) decision. |
| F10.2 | tests/stress.py is code-owned; new stress_budgets.json entries and the loop_cpu_ratio budget go through budget-raise-gate |
| F10.3 | tests/env_drift.py, tests/stress.py, tests/mutation_table.py, tests/closure.py and tests/derive_closures.sh are code-owned; the I1 prototype derives its counts at both ends and raises no mutation_budgets.json entry |
| F10.4 | D7-s1-01 prices coordinator state reached through module-level helpers, which likely raises coordinator budgets: ask before the push |
| F11.2 | workflows, CODEOWNERS, budget_raise_gate.py and docs/decisions are code-owned; D11-s1-01 and D11-s1-04 are owner decisions **Blocked on:** tvofi decisions on D11-s1-01 (ruleset setting) and D11-s1-04 (delegated identity). |
| F11.3 | policy (CLAUDE.md, .claude/rules, tools/audit/briefs) and web-fix-wave.js are code-owned **Blocked on:** tvofi approval (policy). |
| F11.4 | audit-find.js is code-owned |
| F11.5 | policy: tools/audit/briefs, .claude/rules and tests/README.md are code-owned; each draft needs tvofi's approval before this merges **Blocked on:** tvofi approval of each RCA policy draft (TVOFI-ASKS group a). |

**The RCA asks.** Every "needs tvofi" item from the fourteen RCA write-ups, with the plan's standing
rulings (D8-s2-01/A3(e), D11-s1-01, D11-s1-04, D13-s1-02), is collected in `TVOFI-ASKS.md`, grouped as
policy edits to approve, budget raises, and product or scope choices with the RCA's recommended
default, one line each.

**Other asks that may arrive during the wave:**
- Any budget raise a fixer hits (most likely in F1, whose coordinator class sits at zero headroom on several
  metrics; each F1 PR pays for its lines first).
- Any RCA seat that finds no barrier within "The bound" asks tvofi for a ruling rather than recording a
  refusal (PLAN §8.3).
- D0-s2-02 (F2.4) may end as a recorded refusal priced in money and CPU, standing on the #1294 refusal;
  that is the fixer's to record, reported to tvofi.

## 5. RCA seats (15, all on the strongest model)

All fourteen reported (write-ups under `/mnt/project-files/audit-r9/rca/<slug>/RCA.md`; the restart
class is RC2's). Each row names the prototype the barrier PR cherry-picks, whether its files are
code-owned or policy, and its line estimate.

| class | N judge | N sweep | N final | process state | barrier lands in | prototype | code-owned / policy | lines |
|---|---|---|---|---|---|---|---|---|
| P2 | 27 | 27 | 27 | (c); D12-s2-02 alone (d) | F1.11 | `handoff/r9-rca-p2@3938c8ea` | not code-owned; no policy file (the RCA's fixer.md step-8 draft is F11.5's, on tvofi's approval) | 0 production (the owners are created by the instance PRs); about 230 test lines |
| I5 | 19 | 19 | 19 | (c), recorded as (a) by earlier rounds | F10.4 | `handoff/r9-rca-i5@c6ba6036` | not code-owned; no policy file | 0 production; tests/doc_claims.py +230 (about 290 with the RCA's option 3); F11.3: policy_lint.mjs +35/-1 and a one-line fixture |
| I1 | 11 | 11 | 11 | (c) | F10.3 | `handoff/r9-rca-i1@8eda51a2` | code-owned (tests/mutation_table.py); no policy file | 0 production; about 76 changed lines in tests/mutation_table.py (+66/-10); about 40 test lines in tests/entities.py pinning the per-site refusal and its wiring |
| P1 | 9 | 11 | 9 | (c) | F1.6 | `handoff/r9-rca-p1@0ade2456` | not code-owned; no policy file | store.py +33/-19 production; tests/finite_boundary.py +402/-4; the two latent seams about +9/-4 in the demo, less once F3.1's parser exists |
| I3 | 7 | 7 | 7 | (c); D11-s1-01 alone (d) | F11.3 | `handoff/r9-rca-i3@844d14b7` | the governance.yml run step is code-owned; the program is not policy; F11.3 is tvofi's already | 287 for the barrier; instance fixes about +62 code and +148 data; the governance.yml step and the new file's classification not estimated |
| P11 | 6 | 6 | 6 | (c); the currency and Tibber routes (a) | F10.1 | `handoff/r9-rca-p11@82e645c3` | not code-owned (no CODEOWNERS entry for tests/ha_contract.py or tests/hastub); no policy file | 0 production; +168/-5 test in tests/ha_contract.py, plus about 10 in the stub fixes and the now-contract rewrite |
| I4 | 5 | 5 | 5 | (a) | F11.4 | `handoff/r9-rca-i4@06bae072` | audit-find.js and the governance.yml step are code-owned; no policy file | 235 for the barrier plus about 20 registry lines for classifying the shared grammars; instance fixes about +24/-20 |
| P6 | 5 | 5 | 5 | (c) | F1.11 | `handoff/r9-rca-p6@aa2026b7` | not code-owned; no policy file | 0 production; about 510 test lines (423 without comments and blank lines); may delete the hand-written six-code error check arm E subsumes |
| P9 | 4 | 5 | 8 | (c) | F6.3 | `handoff/r9-rca-p9@4f3b9d4f` | code-owned (tests/card_browser.mjs); no policy file | 0 production; +572 test, some of which the fixer may pay back by deleting per-instance witnesses the grid subsumes |
| N-solve-recompute | 4 | 5 | 7 | (c) | F10.2 | `handoff/r9-rca-avoidable-interpreter-bound-recomputation@ab04e39b` | code-owned (tests/stress.py); no policy file | 0 production; about 200 test lines in tests/stress.py after trimming (+287 as prototyped); the allowance constant re-derived at F10.2's merge base with the RCA's history evaluator |
| P3 | 3 | 3 | 3 | (c) | F1.10 | `handoff/r9-rca-p3@2ca057ae` | not code-owned; no policy file | about +60/-35 production (every floor moved into a ThermalParameters property; +63/-36 on the RCA's fixed tree, which included F2.1's instance fixes); about 210 test lines |
| P5 | 3 | 3 | 4 | (c) | F4.2 | `handoff/r9-rca-p5@d4cf63d9` | not code-owned; no policy file | 0 production (the fix is F4.2's); +79/-4 test |
| N-cpu-gate-blind | 3 | 3 | 3 | (c) | F10.2 | `handoff/r9-rca-cpu-gate-blind@8352c9e0` | code-owned (tests/stress.py); tests/replay.py is not; new stress_budgets.json entries go through budget-raise-gate; no policy file | 0 production; about 260 test lines after trimming, plus three valve scenario specs and their budget rows |
| N-restart | 2 | 2 | 2 | (RC2, merged as #1641) | F1.4 | `merged (#1641)` | not code-owned | as the surviving instances need |
| N-future-instant | 2 | 7 | 8 | (c) | F3.1 | `handoff/r9-rca-persisted-future-instant-trusted-without-bound@8795c4c2` | not code-owned; no policy file | about +64/-7 production (store.py +61/-1, boost.py +1, away.py +1, coordinator.py +4/-6, which re-records coordinator_loc down with the reason in the commit message); about +155 test (Arm 5) |

N final is judged findings plus counted instances (PLAN §7). Each barrier PR comes after every PR
holding an instance of its class, except the residual instances its RCA measured the barrier not to
read; the generator refuses the plan otherwise and prints the residuals.

**Barrier forms, as the seats chose them:**

- **P2** -> F1.11: a one-fact-one-owner registry run on every gate, as a class-named 'P2 owners' block in tests/entities.py: each entry names the fact, an AST shape, its owner function(s) and reasoned dispositions; any other hit fails, and OWNER-MISSING, DEAD-RULE and STALE-DISPOSITION refusals stop it going green by skipping. Facts with no syntactic shape are held by per-sibling censuses that assert their own preconditions.
- **I5** -> F10.4: per-PR, one arm per fact family: five corpus-wide arms in tests/doc_claims.py, each deriving its fact from executed production code (entity prose and counts, private card mentions, unit typography, service fields, option labels); plus, in F11.3, a quoted-line pass in policy_lint.mjs citations pinned in REQUIRED_ROT. The sweep's nightly lane of finder harnesses was refused: it fails open and 9 of its 19 harnesses enumerate listed sentences. Residual: D5-s1-02, D5-s1-03, D5-s2-02, D5-s2-03, D5-s2-51, D6-s1-02, D6-s2-02, D6-s2-03, D6-s2-04, D8-s3-02.
- **I1** -> F10.3: a per-site mutation ratchet: refuse any unpinned site the diff added, by content (a multiset difference on file, operator and stripped text), not only a grown total; and widen the inventory to every single-line guard and clamp shape. The sweep's non-UTC lane was refused (the Europe/Stockholm suite already runs inside tests/features.py).
- **P1** -> F1.6: the store-load boundary quarantines a leaf, numeric string or dict key of magnitude at or above 1e15 as it already does a non-finite one (extending the boundary predicate F3.1 widens, in the same module); Arm 4 in tests/finite_boundary.py seeds every store through its real saver at an aware clock, substitutes every leaf and container by kind, and scans everything the coordinator owns after the real loaders. The sweep's load helper was refused as the barrier (optional per call, reaches no instant, key, container or type).
- **I3** -> F11.3: field coverage of every registered governance check's input: each leaf of the input is enumerated from the artifact, perturbed to a property-violating value, and the real check run; a leaf the check stays green on is BLIND unless ignored with a reason; DEAD ignores and REFUSED loads fail. Scoped to runs whose inputs changed, plus nightly. Residual: D11-s1-02, D11-s1-03, D11-s1-04, D13-s1-03.
- **P11** -> F10.1: three arms in tests/ha_contract.py on the existing gate path: non-vacuity (a contract that reached none of its asserts fails), hook re-runs (each HOOK re-runs the FAITHFUL contracts it feeds in every hook state), declared drops (every accepted-and-unread stub parameter must be listed). Residual: D1-s1-51, D10-s1-03, D6-s1-81, D14-s4-02.
- **I4** -> F11.4: an agreement lane: each registered concept's real readers (imported, never copied) answer one corpus of live instances plus the findings' boundary cases, and any disagreement is refused; plus grammar discovery: a regex source in two or more governance code files must be registered with a disposition, and a stale entry is DEAD.
- **P6** -> F1.11: one 'every read has a producer' section in tests/entities.py with seven arms (payload keys, built entity ids, getattr probes, flow error codes, offered modes, pre-fill preview fields, solve seeds), each taking its universe from production, each asserting a non-empty universe, and a planted-defect null control per arm.
- **P9** -> F6.3: a property-keyed grid inside tests/card_browser.mjs: 31 states by 7 cells, WCAG AA contrast composited over what is underneath, zero shared glyph ink between text runs, pop-ups inside viewport and chart, distinct options, no unreachable clipped ink, 24 px targets or the 2.5.8 spacing exception; controls: every cell mounted and every driver step found, and reach (every colour-setting CSS rule matches a visible element in some cell). Reduced motion, frozen clock.
- **N-solve-recompute** -> F10.2: a production-call channel in the stress gate: every call production bytecode executes, per production file and scenario, captured on the branch and the merge base side by side in fresh interpreters and judged at 5 percent of the growth the evaluation and simulate counts vouch for; subset form (one scenario per family) recommended.
- **P3** -> F1.10: two arms in tests/features.py: (a) one floor per thermal parameter: every positive floor on a ThermalParameters quantity lives in one function with one constant and nothing divides by it raw, zero groups, no allow-list, with a fixture probe of the rule's own keying; (b) the per-pair check: one zone-kelvin under min_temp prices each zone at the single-zone room's linear floor price, in both comfort-term twins. The sweep's allow-listed lint was refused (1 of 3 instances, and blind to a new raw divisor by its key).
- **P5** -> F4.2: extends the R8-P5b #1524 block in tests/features.py: the adoption runner gains an axis for every quantity the experiment is told (the house keywords of SystemIdentification.step, plus a drifting reading); an enumerator arm refuses a told quantity with no axis; every perturbed night, single- and two-zone on all three presets, adopts within the bar of the plant's own heat loss or is refused; the #1524 liveness checks keep it from passing by refusing everything.
- **N-cpu-gate-blind** -> F10.2: derive the sampled population from production, in three parts: the production-call channel (shared with the recompute class), plant-axis coverage (every selectable topology.LAYOUTS key and mixing_valve.MODES value reached by some scenario's built plant), and a loop-thread cost figure in tests/replay.py banded like the whole-cycle ratio.
- **N-restart** -> F1.4: the RC2 barrier, merged as #1641; an instance that survives at origin/main extends it here.
- **N-future-instant** -> F3.1: the store-load boundary bounds every stored instant: QuarantiningStore gains a lead argument and rewrites any instant leaf later than now plus the store's lead to that bound before a loader sees it (lead zero by default; boost's is BOOST_HOURS, accuracy's the longest lead bucket; None opts a store out and must be listed with its reason); Arm 5 in tests/finite_boundary.py holds it. The sweep's AST lint was refused: keyed on parse call sites, it accepts the no-op use-time clamp and misses parse_datetime. Residual: FI-sw3.

## 6. Carry-ins from RESUME, placed

| carry-in | PR |
|---|---|
| #1643 card tests: pin its surviving mutants (ghi as a step mean; `overlays()` iterating covered; the null-stretch denominator in the step mean; askedThrough) | **F6.2** |
| Merged since baseline (#1641, #1642, #1643): findings measured at `1936d5ca` are re-checked before fixing | every brief (standing rule); named specifically in **F1.3** (button.py), **F1.4** (RC2 restart class, #1641), **F6.1** (card, #1643), **F8.3** (`docs/dashboard-card.md`, #1643) |
| L1 indoor-sensor lead, D4 side: a source-id attribute so the card draws the raw thermometer through a staleness gap | **F6.4** (after D1-s5-51's fix in F4.1) |
| Verifier: D9-s1-01's vectorised fix loses parity on Fortran-order batches | **F2.2** |
| Verifier: D14-s4-02's fix must also step `run_fixture` in UTC | **F1.1** |
| Verifier: D10-s1-01's seam misses services.py (`handle_assign_entity`, `services.py:629` at baseline) | **F1.8** |
| Judge/verifier notes carried to the fixer: D2-s2-01's missed coordinator seams (F1.7); D2-s2-03's baseline_end sibling (F2.3); refuted D0-s1-01's two-zone deep-anchor asymmetry as hygiene for the P4 fixer (F2.4); D8-s2-03's finder fix would reintroduce D8-s2-02 (F7.1); G1-V2's `boost.restore` naive-until observation (F3.1); every weakened or narrowed claim (in the finding's fix notes) | as listed |
| L2 extra seams for existing findings (en.json → D5-s1-02; strings.json and README → D6-s2-03; README → D8-s3-03; climate.py → D8-s1-03; config_flow `async_step_dhw` → D12-s1-02; the card's datetime-local handler → D1-s3-01; the price-unit fields → D4-s2-02) | F5.1, F8.3, F7.2, F2.4, F1.2, F3.1, F1.8 respectively |
| Owed round-9 driver fixes (Prepare rounds interpolation, earlier-rounds strip, env_drift warm step, Chromium path, the batch patch's defer and judge-flag arguments) and `tools/audit/README.md` naming `scopes.json`/`check_scopes.py` | optional fold into **F11.4**, tvofi's call |
| The RCA seats' carries (31, `finding-propagation.md`), each delivered into its destination's roster brief and lane brief | section 10 |

## 7. Findings I could not place

None. Every one of the 145 survivors, every one of the 14 counted instances and the 2 latent seams maps to a PR (tables below). FI-sw3 (F1.9) ends in tvofi's decision rather than a bound. Five findings may end without a code change,
by design: D8-s2-01 (tvofi's A3(e) ruling), D11-s1-01 (a ruleset setting tvofi changes; the PR records it),
D11-s1-04 (tvofi's identity decision), D13-s1-02 (tvofi decides whether to build the carry), and D0-s2-02
(a recorded refusal is a legitimate outcome).

## 8. Merge order, stamps and throughput

- **One merge at a time**, in the proposed queue below, which respects every `after` edge. When two PRs
  are ready together, the one on the longer remaining chain goes first: **F1 is the critical path**
  (eleven PRs, the coordinator), then F2.
- **Critical path (inferred, not measured):** F2.1 -> F1.1 -> F1.2 -> F1.3 -> F1.4 -> F1.5 -> F1.6 -> F2.4 -> F1.7 -> F1.8 -> F1.9 -> F1.10 -> F1.11 -> F10.4 -> F11.4 -> F11.5, 16 PRs deep (the longest chain of
  `after` edges, derived by the generator). The high findings all sit in the first waves: D14-s4-01
  (F2.1, F1.1), D1-s3-01 (F3.1), D1-s5-52 (F4.1), D8-s2-02 (F7.1), D12-s1-01 (F1.2), D2-s3-01 (F1.3).
- **Stamps.** The plan's standing rule holds: no new branch is cut between a fixture-mover's merge and
  its stamp. PRs marked fixture (drift plausible): F1.3, F1.7, F1.10, F2.1, F2.3, F2.4, F2.5, F10.1. If one of them
  merges with claimed drift, the orchestrator stamps before the next branch is cut; otherwise, proposed
  stamp points are (a) after the high-severity set above has merged, (b) after F1.6 (P1 barrier), and
  (c) after F11.5, the last PR.
- **Capacity:** ten fixer threads in wave 1, then as lanes finish their threads end; lanes F5, F8, F9 finish
  early (two or three PRs), F11 is mostly waiting on tvofi, F1/F2 run longest. Reviewers: two, plus a third
  when the queue passes two hand-offs.

## 9. Phase D: what the sweeps changed

All seven sweeps landed (commits in the class table). Every class's final N matches judged findings
plus the instances below, and every seam each sweep returned is listed, with its disposition, in the
lane brief of each lane holding the class.

- **P1** (S3): 9 → 11. Two new `ComfortLearner.from_dict` leaves (P1-sw1, P1-sw2), carried by F1.6
  with the P1 barrier. *Superseded (section 10): not store-reachable, N back to 9.*
- **P9** (S5): 4 → 5. The new instance is the chart's SVG axis number/unit label overlap (P9-sw1, F6.1).
  *Superseded (section 10): P9-sw1 is a box-metric artefact; N is 8 with the RCA's four.*
  The keyboard route is **not** a counted instance: S5 ran with the keyboard cells off and records it as
  exposure, so it is a check for F6.2 (below), not an instance.
- **avoidable interpreter-bound recomputation** (S5): 4 → 5. `cycling_penalty_batch` (RC-sw1, F2.2); the
  other ThermalParameters properties S5 found are folded into D9-s1-71.
- **persisted future instant trusted without bound** (S7): 2 → 7, now `rca: true` with its own RCA seat
  and barrier. The five instances: four in `coordinator.py` (fuse-advisor cooldown, heavy-snow damping,
  `_detect_outage`, and the lower-confidence immersion recency) in the new F1.9 with the barrier;
  `pump_arbiter.py`'s `hold()` echo grace in F3.2. *Superseded (section 10): the barrier is in F3.1,
  N is 8 with the legionella seam.*
- **P5** (S5): stays 3 (*section 10: 4 after the RCA*). `async_update_thermal_params` writing two gated parameters with no gate is a
  lead, not an instance: S5 disposed it not applicable, since there is no gate to key wrong.
- Every other class kept its N; a few PRs gained a borrow to reach a seam their finding already owned
  (F1.8 borrows `price_model.py` for P8's money-code seam).

**Barrier order corrected.** The draft stated that a barrier lands after every instance PR of its
class but did not check it. The generator now does, and it refused five barriers in the draft; each
moved to a PR that waits on all its class's instance PRs:

- I5: F8.3 → **F10.4** (instances in F2.1, F2.3, F6.2, F1.10 and F11.3 as well as F8); F10.4 now waits on F11.3,
  and F8.3 no longer borrows `tests/doc_claims.py`.
- P11: F10.1 → **F10.3** (instances in F1.1, F1.7 and F8.3); F10.3 now waits on F1.7 and edits `tests/ha_contract.py`.
  *Superseded (section 10): back to F10.1; its check reads none of those three.*
- I1: F10.3 stays, and now waits on F9.2 (the last I1 pin PR).
- I3: F11.2 → **F11.3** (D11-s2-01 is an I3 instance in F11.3, and the barrier's shape lives in its files).
- I4: F11.4 stays, and now waits on F10.4 (D7-s3-02, the dead_methods census), so F11.4 is the round's last PR.

The draft's critical path was 13 PRs deep and is now 16: F11.4 now follows F10.4. The new F1.9
sits between F1.8 and F1.10 at the depth F6.4 already had there, so it adds none.

Leads placed as instructions, not instances:

- **P9 keyboard route (S5, exposure, not counted)** -> F6.2: S5 ran its grid with the keyboard cells off, so the 204 pointer-only hits across 8 selectors (both chart pan surfaces, the six setup-picker entity rows) are unverified for a keyboard route. S7's pointer-only sweep disposed the chart pan as guarded (zoom buttons) and the picker surface as guarded (its own keydown handler); D4-s1-04's fixer re-checks the six setup-hit rows with the keyboard cells on and dispositions each.
- **P5 lead: async_update_thermal_params has no gate (S5)** -> F1.4: The set_thermal_parameters service writes house_heat_loss_scale and buffer_cooling_rate with no admission gate. S5 disposed it not applicable to P5 (no gate to key wrong), so it is not a P5 instance and not counted; it is D1-s2-53's seam. D1-s2-53's fixer decides, with the measurement, whether the service write is bounded like the sysid adoption, and says so; F4.2's P5 barrier does not cover this writer.

Ledger notes (not RCA triggers this round; no PR unless a finding already covers them):

- P4 (S6): the ledger's most recurring class, 14 historical instances in rounds 1-7, never barriered or given a detector; N=1 this round (D0-s2-02, F2.4), so no RCA seat. Flagged for whoever owns the ledger's cross-round view.
- P7 (S7): recurred in 4 of 6 swept rounds (2, 3, 5, 9) with no barrier; N=1 this round (D14-s4-01). F1.1's DST tracer barrier is D14-s4-01's own fix, not a class barrier.
- I2 (S7): recurred in 5 of 6 swept rounds (2, 3, 5, 7, 9) with no barrier; N=1 this round (D14-s5-01, F10.3).
- S4: the per-file policy-doc cap counts lines, with no byte or token guard. That is D11-s2-01 (F11.3), whose seams S4 widened to every capped file; no new PR.

## 10. The RCA fold (2026-09-26)

tvofi (17:44Z) asked for the RCA seats before fixing, with any cost-effective countermeasure folded
into this plan. All fourteen reported; every barrier's prototype branch was read back with
`git ls-remote`. The orchestrator's rulings on their plan folds are applied as follows.

**PR set** (45): new F2.5, F6.1b, F1.11 and F11.5 (section 1); F1.9 shrunk; D2-s4-02 moved from
F4.2 to F4.1.

**Barrier moves.**
- **Future instant → F3.1** (was F1.9). The store-load boundary is the fix for F3.1's own class
  findings and closes FI-sw1, FI-sw2, FI-sw4, FI-sw5 and the legionella seam in one place. F3.1 borrows
  `store.py` and two lines of `coordinator.py` from F1 and `tests/finite_boundary.py` from F9; F1.1 and
  F9.1 now wait on F3.1, so every F1 and F9 PR follows it. F1.9 keeps the FI-sw3 decision and the
  regression tests, after F3.1; F3.2 keeps FI-sw5's test.
- **The `store.py` order.** P1's barrier (the magnitude drop, F1.6) and the instant bound (F3.1) touch
  the same sanitising walk. Lane ownership stays (F1 owns `store.py`; F3.1 borrows it), and the edge
  orders them: F3.1 first, and F1.6 (after F3.3, after F3.2, after F3.1) extends the same predicate.
  F1.4, which also edits `store.py`, follows F3.1 through F1.1.
- **P11 → F10.1** (was F10.3). F10.3 drops P11, `tests/ha_contract.py` and its edges on F1.7 and F8.3;
  F1.1 gains an edge on F10.1; F1.7 borrows `tests/ha_contract.py` for its own contract.
- **Solve cost.** F2.5 carries `peak_cost_batch` (RC-rca1) and the terminal twin (RC-rca2), after
  F2.2 and F3.3; F10.2 now waits on F2.5.
- **P2 and P6 → F1.11**, **P3 → F1.10**. Neither is tvofi-gated: the P6 RCA showed the boost test hook
  can be dropped without `tests/harness.py`, and no other barrier needs it.
- **I5** is split: the `doc_claims.py` arms in F10.4, the `policy_lint.mjs` quoted-line pass in F11.3.
- **P9**: F6.3 after F6.1b (through F6.2); the grid's browser cost is scoped to card-surface diffs
  through the scoped gate, `main` forced full (orchestrator's ruling).

**N changes** (issue drafts and `INDEX.json` follow): P1 11 → 9 (P1-sw1, P1-sw2 not store-reachable);
P5 3 → 4 (the half slab mass); P9 5 → 8 (P9-sw1 out; three new and one candidate in); the recompute
class 5 → 7 (`peak_cost_batch`, the terminal closure); the future-instant class 7 → 8 (legionella).
Latent seams (P1-rca1, P1-rca2) fill F1.6's freed slots and are not counted.

**Carries** (31), delivered into each destination's roster brief (`carry`) and lane brief:

| to PR | from RCA | carry |
|---|---|---|
| F1.6 | P1 | Cherry-pick 0ade2456 only (99118d35 is demo instance fixes). Before merging, re-derive tests/closures.json for tests/finite_boundary.py with derive_closures.sh --single on Linux. The arm's out-of-scope residue (out-of-domain but bounded values, and a loader that discards a whole valid grid for one bad cell) stays per-seam in its instance PRs, pinned by their probes, unless tvofi commissions a declared-domain barrier (TVOFI-ASKS). Optional cost cut, not measured: sample nested grid rows first and last, as scalar lists already are; re-measure if taken. |
| F1.6 | P1 | Take each NaN-arm failing test from Arm 4 or a store-path probe, never a direct from_dict call: through QuarantiningStore a NaN leaf becomes None first, so a direct call measures a seam no store can reach. This applies to D14-s1-01's attempt_peak arm here. |
| F3.3 | P1 | D1-s4-01's duty and D1-s5-02's residual variance NaN probes call from_dict directly and bypass QuarantiningStore, which turns the NaN leaf into None; take the failing tests from a store-path probe or the P1 barrier's Arm 4 (prototype 0ade2456). The finite out-of-range cells are the reachable part and stay in scope. |
| F3.1 | P1 | The stored-instant rule must make every stored instant aware, or drop it, at load, including AccuracySample.from_dict, the immersion events and the snapshot's taken_at; F1.6 applies it at the two F1-owned seams (P1-rca1, P1-rca2). The P1 barrier's Arm 4 refuses a naive instant held live even where no consumer diffs it yet. Which zone a naive value is read in is this PR's decision (the P1 demo used UTC). |
| F3.1 | N-future-instant | Cherry-pick 8795c4c2: QuarantiningStore gains the lead argument and rewrites an instant leaf later than now plus the lead to that bound, in the leaf's own zone form, with one WARNING; boost's lead is BOOST_HOURS, accuracy's the longest lead bucket, away and the manual plan opt out with a listed reason until F1.4 bounds the plan's expiry. Arm 5 in tests/finite_boundary.py feeds every loader instants 400 days ahead and holds the opt-out list equal in both directions. The coordinator edit joins two argument lists, so coordinator_loc falls: re-record it down with the reason in the commit message. |
| F3.1 | N-future-instant | Re-read tests/features.py's #1532 check and its comment, which call a future last cycle 0 h ago: they stay valid only for an in-process clock step back, which the boundary does not touch. The age of a stamp ahead of the reading clock is unknowable, not 0 (#775). |
| F1.4 | N-future-instant | Once D1-s2-54 bounds the manual plan's expiry, set the manual-plan store's lead in its coordinator construction and remove manual_plan from the boundary arm's opt-out list in tests/finite_boundary.py (borrowed from F9); the arm refuses a list that disagrees with the stores in either direction. |
| F1.9 | N-future-instant | The RCA's three corrections to S7: a use-time clamp inside a parse is a no-op at the parse-at-use seams (snapshots due, the curve learner's step down, the immersion margin), FI-sw3 owes a decision rather than a bound, and FI-sw1 is month-bounded. S7's probes are not the failing tests for FI-sw1 or FI-sw3; the RCA's real-loader reproduction is the shape. |
| F2.4 | P2 | D12-s2-01 has a fourth copy of the on threshold, `_observe_compressor_start` in coordinator.py (baseline line 9736, operands reversed, so the sweep's grep missed it). This PR cannot edit it (F1 owns coordinator.py): create the owner, and F1.10 routes that copy through it before F1.11 registers the owner in the P2 registry. |
| F2.1 | P3 | D12-s2-03: send all four normalised-power sites (`_zone_setpoints`, `_power_to_setpoints`, `_power_to_displace_schedule`, `get_current_action`) through one helper that owns the floor, better the clipped fraction; otherwise F1.10's floor arm re-opens them. D2-s2-81: give each zone the full linear floor price; the P3 per-pair arm pins only the linear term and leaves how the quadratics combine the zones to you. |
| F4.2 | P5 | A fix that feeds the learned free-heat profile into the prior needs coordinator.py (the gains prior is built there from the configured internal gains); hand that part back to F1 as this brief already says. The barrier's check deliberately omits the #1524 check's peak clause: aborted free-heat nights peak at 0.846 and 0.880 K, which is D2-s4-02's abort-at-sample seam (now F4.1's) and not this class's. |
| F5.2 | P6 | D4-s2-01: the universe is the nine pre-fill preview fields modbus_prefill.infer can render, not three: each needs a label and a description in all three catalogues. The config error table owes three codes, not one: prefill_device_unreadable, flow_target_needs_two_zone and silent_mode_window_too_short. D10-s2-01: the climate entity's translation key needs the auto and economy preset states in all three catalogues and in icons.json, and setting the key engages the translation-file checks, so the climate block needs its name. Control: the P6 prototype's arms F, E and P at zero (aa2026b7). |
| F1.2 | P6 | D12-s1-01: the sweep's slab instance has no fix note; seed slab_temperature with the DHW state from the previous plan's trajectory, since the P6 solve-seed arm reads it at 22.0 on both solves. Watch the pinned premise in tests/entities.py that with no tank sensor the published tank temperature is the model default: it holds after one light cycle, but a fix that also publishes the advanced seed will move it. |
| F1.5 | P6 | D2-s1-51: fix at the producer, at the state write: write outdoor_temperature from the forecast's current hour when no outdoor reading is ok. Nine more coordinator readers of the outdoor state read the constructor default with no outdoor entity mapped; a producer fix covers them all, an advisor-only fix leaves the P6 solve-seed arm red and may not be declared away without evidence that no other reader is ungated. |
| F7.3 | P6 | The P6 solve-seed arm (F1.11) declares room, upper and lower under A3(e). Whichever way tvofi rules on D8-s2-01, update that declaration table in tests/entities.py in the same PR; the arm refuses a stale declaration. |
| F6.2 | P9 | The P9 grid (F6.3) is not a keyboard lane: the 204 pointer-only hits S5 recorded stay this PR's to re-check with keyboard cells on, as D4-s1-04's lead already says. |
| F1.1 | P11 | After F10.1, re-run the replay-clock finder harness (p7_replay_clock) on this branch: F10.1 lands freeze normalisation, the stub half of D14-s4-02; this PR keeps G3-V2's rule that run_fixture steps its clock in UTC. |
| F1.1 | I1 | The closure-scoped non-UTC lane is refused (I1 RCA): the Europe/Stockholm suite already runs inside every tests/features.py run. open_meteo.py's process-zone seam (baseline line 209) is killed by a tests/open_meteo.py pin that sets the process TZ in-process, since the stub's zone variable does not reach it; the coordinator's two tzinfo guards (baseline lines 8112 and 8384) need a tests/dst_checks.py arm with a naive stored stamp under the aware stub clock, live once F10.1 makes the stub clock aware by default. |
| F9.1 | I1 | Pins land as killed_by rows in the mutation ledger: once F10.3 merges, a pin PR that edits a guard line without one is refused by the per-site ratchet. |
| F9.2 | I1 | Pins land as killed_by rows in the mutation ledger: once F10.3 merges, a pin PR that edits a guard line without one is refused by the per-site ratchet. |
| F10.4 | I1 | This PR lands after F10.3's per-site mutation ratchet: any guard it adds or edits is refused until mutation-autofix pins it or you triage it; pure deletions add nothing. |
| F11.3 | I1 | This PR lands after F10.3's per-site mutation ratchet; the ratchet reads production guards only, so policy and workflow edits are not refused, but a guard added in a package file would be. |
| F11.1 | I3 | D11-s2-02's hooks fix must read each hook's type as well as its matcher: the I3 field-coverage run found three more blind leaves (the type of the SessionStart, PreToolUse and Stop hooks), which F11.3's barrier refuses. |
| F11.1 | I4 | Leave the readers importable so F11.4 needs no source-text reads or temp modules: export the paths reader and the merged-PR reader from policy_lint.mjs (or put the frontmatter parser in one shared module both files import); give rules_sync.mjs an exported parse and a main guard (today it writes .cursor/rules on import). D13-s1-01's fix decides whether subject mode reads both merge-subject shapes; if it deliberately does not, F11.4 registers that difference instead of the pair. Record in your body the reader pair and corpus for the governance-workflow pin (D11-s1-72) so F11.4 registers it. |
| F10.4 | I4 | Record in your body the reader pair and corpus for D7-s3-02 (dead_methods against bound_references over methods) so F11.4 registers it in the agreement lane. |
| F5.1 | I5 | D4-s2-09: fix the ninth bare-unit leaf too, config.step.user_sensors.data_description.solar_radiation_entity, in strings.json, en.json and sv.json, or delete it if it is not rendered; otherwise F10.4's unit-typography arm is red. |
| F8.2 | I5 | D6-s1-01, D6-s1-03 and D5-s1-05: every state in the sensor's options is named in its row (unknown excepted); every entity a bare entry disables is named in the list, in its row, or in a sentence saying disabled by default; options labels match en.json exactly (parentheticals ignored). These are what F10.4's arms check. |
| F6.2 | I5 | D5-s2-01: no backticked underscore-led name may stay in a card comment unless it resolves against the card's code outside backticks or against the package's py, json or yaml files; F10.4's private-mention arm checks exactly that. |
| F11.3 | I5 | D11-s2-04: quote the line closure.py prints, MODE: SCOPED -- <n> script(s) run; the quoted-line pass this PR lands refuses any other spelling. |
| F2.2 | N-solve-recompute | Accept a recomputation fix on the finding's cost metric re-measured on the fixed tree (share of solve, or the production-call count), not on the finding's proxy count: #985 met its proxy (97.02 to 1.02 entries per gradient) and left a per-row loop that is 62 percent of a tariff solve. Control: the fix must move the production-call count of the scenario the finding measured; the recompute RCA's call-count demo on its fixed arm is the shape. |
| F2.5 | N-solve-recompute | Accept the fix on the cost metric re-measured on the fixed tree (share of solve, or the production-call count), not on a proxy count: #985 met its proxy and left the per-row loop this PR removes. Control: the fix must move the production-call count of the winter capacity-tariff scenario. |

## 11. Resumability (tvofi, 2026-09-26 19:05Z)

tvofi: *"Make sure that the plan can always be resumed either by local or cloud threads and that any work
lost in threads, seats and subagents is minimal should this session crash."* The plan meets it with three
records, each on a remote branch or the shared project files, so no crash loses more than the last step.

1. **The seat's branch.** Every seat (fixer, reviewer, RCA, runner, subagent) commits and pushes to its
   remote handoff branch at each step boundary — failing test written, fix green, body drafted — and at
   least every ~30 minutes of work; it never holds unpushed work across a long run (a gate or stress run,
   a subagent), and reads `git ls-remote` back after each push. Fixer: `handoff/<lane topic>-<k>` (the
   roster's `resume.branch`). Reviewer: the same with `-review`. A runner or subagent pushes its output,
   or hands it to the seat that pushes, before it reports.
2. **The resume note.** On that branch, `handoff/round9/fix/resume/<PR-id>.md` (a review:
   `<PR-id>-review.md`): last completed step, next step, `branch@commit`, merge base, open questions,
   what is waiting on whom. Updated in the same commit as every push. For in-flight state it outranks the
   roster, which the orchestrator (or a sonnet record seat) brings up to date at each hand-off and merge.
3. **The run log.** One dated line per milestone (branch cut, failing test, green, body drafted, hand-off,
   verdict, merge) in `/mnt/project-files/audit-r9/RESUME.md`, and the same line in its mirror,
   `handoff/round9/RESUME.md` on `handoff/audit-r9-plan` (fetch, append, commit, push; re-fetch and
   re-append on a non-fast-forward; never force). The Mac cannot read `/mnt/project-files`, so the mirror
   is what makes the Mac able to resume from git alone; a Mac seat writes the mirror only and the
   orchestrator copies its lines into the `/mnt` log at its next pass.

**Picking up any PR.** The roster entry `R9-<PR-id>` in `.claude/workflows/wave-r9-groups.json` (on
`handoff/audit-r9-fixplan`) carries a concrete `resume` object: `branch`, `commit`, `last_step`,
`next_step`, `note_file`, `review_branch`, `plan` (the lane brief section and this file), `log`, and two
pickup recipes:

- **Cloud seat** (`pickup_cloud`): `git fetch origin <branch>`; if it exists, `git worktree add --detach
  $S/<lane topic>/wt FETCH_HEAD`, read the note, check its commit against the fetched head (if the branch
  is ahead, trust the branch and its log), `git merge origin/main` if main moved and re-run `fixer.md`
  steps 2-8, then continue at the note's next step. If the branch does not exist, cut from origin/main and
  start at `fixer.md` step 1. Plan and briefs from `handoff/audit-r9-fixplan`; the log from `/mnt`.
- **Mac seat** (`pickup_local`): the same git commands from the Mac checkout, with the plan, briefs and
  roster from `handoff/audit-r9-fixplan` and the log from `handoff/audit-r9-plan`'s mirror; nothing it
  needs lives only under `/mnt`.

A crashed seat is restarted from its branch and resume note, never from scratch. A crashed orchestrator is
restarted from the mirror log, the roster and `git ls-remote 'refs/heads/handoff/r9-*'`, which together
name every branch in flight and its last pushed step. This plan itself follows the rule: its generator
sources are committed beside it (`handoff/round9/fix/src/`), and each rebuild is pushed.

## 12. Model routing (tvofi, 2026-09-26 19:05Z)

tvofi: *"Work that is feasible for sonnet and haiku should be routed as such."* Each role goes to the
cheapest model that can do it; the roster's per-PR `model` object (`fixer`, `fixer_why`, `reviewer`,
`rca`, `runner`, `record`) and each lane brief name them, and `gen.py` refuses a strongest-model fixer
without a reason, or a barrier PR routed below the strongest model.

| role | model |
|---|---|
| fixer | per PR (above): the cheapest feasible; the reason is stated whenever it is the strongest |
| reviewer | opus: fix-review.md, adversarial, from a detached worktree; never the fixer's session |
| rca and judge | opus |
| runner | haiku: gate and stress re-runs, closure and budget re-records at the hand-off, build.sh rebuilds, report rendering and digests; reports numbers, decides nothing |
| record | sonnet: delivery rows, issue text, the #201 draft, RESUME.md lines, roster resume upkeep and V1-style checks |

Fixers per PR (17 sonnet, 28 strongest; no fixer is haiku, because every fix owes a
failing test and a mutation proof that need judgement):

| PR | fixer | why |
|---|---|---|
| F2.1 | opus | solver seams with golden drift; float equivalence needs judgement |
| F3.1 | opus | a class barrier carrying an RCA prototype (N-future-instant) across eight files |
| F4.1 | opus | input plausibility bounds and a clamp sized against the model curve |
| F7.1 | sonnet | small entity-attribute fixes |
| F5.1 | sonnet | translated text and config UX, small and mechanical |
| F6.1 | sonnet | card layout, text and keyboard fixes, small and mechanical |
| F8.1 | sonnet | documentation lane |
| F11.1 | sonnet | non-code-owned parsers with the finder's harness as oracle |
| F10.1 | opus | a class barrier carrying an RCA prototype (P11) in the Home Assistant stub |
| F1.1 | opus | DST wall-clock arithmetic across six files plus the gate's clock; a wrong offset passes most pins |
| F2.2 | opus | vectorising the solve while keeping its floats; golden drift claims |
| F3.2 | opus | pump-duty arbiter state machine |
| F4.2 | opus | a class barrier carrying an RCA prototype (P5) plus the fit integrator |
| F9.1 | sonnet | test-pin lane |
| F11.2 | opus | required-check boundaries and identity (decision 0011); a wrong boundary silently ungates main |
| F8.2 | sonnet | documentation lane |
| F6.1b | sonnet | card layout, text and keyboard fixes, small and mechanical |
| F1.2 | opus | presence inference and the solve seed change what the solver sees; needs design judgement |
| F3.3 | opus | five learner-store and feed-parser findings across four files |
| F6.2 | sonnet | card layout, text and keyboard fixes, small and mechanical |
| F8.3 | sonnet | documentation lane |
| F9.2 | sonnet | test-pin lane |
| F11.3 | opus | a class barrier carrying an RCA prototype (I3) plus policy text |
| F1.3 | opus | cycle fencing and failure reporting are ordering and concurrency judgements |
| F5.2 | sonnet | translated text and config UX, small and mechanical |
| F7.2 | sonnet | small entity-attribute fixes |
| F2.5 | opus | vectorising peak_cost_batch and its terminal twin with golden drift |
| F6.3 | opus | a class barrier carrying an RCA prototype (P9, +572 lines of browser harness) |
| F1.4 | opus | a class barrier carrying an RCA prototype (N-restart) plus restart durability |
| F2.3 | opus | plant-model physics with golden drift |
| F10.2 | opus | a class barrier carrying an RCA prototype (solve-recompute and cpu-gate-blind) in code-owned gate scripts |
| F1.5 | opus | error-path restructuring inside the cycle; a moved try changes which failures surface |
| F10.3 | opus | a class barrier carrying an RCA prototype (I1) in code-owned gate scripts |
| F1.6 | opus | a class barrier carrying an RCA prototype (P1) plus two latent seams |
| F2.4 | opus | on/off threshold semantics and multi-start seeds with golden drift |
| F1.7 | opus | cross-lane coordinator readers, the reauth route and a settlement scale with golden drift |
| F7.3 | sonnet | mechanical once tvofi rules on A3(e) |
| F1.8 | opus | currency and unit seams across eight sites and config-entry identity |
| F6.4 | sonnet | card layout, text and keyboard fixes, small and mechanical |
| F1.9 | sonnet | regression tests for instances F3.1 closes plus one branch whose rule tvofi decides (FI-sw3); stop and ask if unruled |
| F1.10 | opus | a class barrier carrying an RCA prototype (P3) |
| F1.11 | opus | a class barrier carrying an RCA prototype (P2 and P6) |
| F10.4 | opus | a class barrier carrying an RCA prototype (I5) plus ratchet truth |
| F11.4 | opus | a class barrier carrying an RCA prototype (I4) plus the owed driver fixes |
| F11.5 | sonnet | lands RCA drafts tvofi has approved, verbatim, and syncs the Cursor mirror |

---

## PR table (merge order within each lane; `after` gives the cross-lane edges)

| PR | lane | wave | findings | classes | sev | model | tvofi | RCA seat beside | barrier here | after |
|---|---|---|---|---|---|---|---|---|---|---|
| F1.1 | F1 | 2 | D14-s4-01*, D14-s4-02, D3-s1-91, D3-s3-01 | P7, P11, I1 | high | opus | - | - | - | F2.1, F10.1, F3.1 |
| F1.2 | F1 | 3 | D12-s1-01, D12-s3-01, D14-s2-01 | P6, P2 | high | opus | - | P6 | - | F1.1 |
| F1.3 | F1 | 4 | D2-s3-01, D1-s2-51, D1-s2-91, D1-s4-02, D10-s1-02 | P2 | high | opus | - | - | - | F1.2 |
| F1.4 | F1 | 5 | D1-s2-52, D1-s2-53, D1-s2-54, D1-s2-03 | N-restart, N-service-clamp, P1 | medium | opus | - | N-restart | N-restart | F1.3, F9.1 |
| F1.5 | F1 | 6 | D1-s2-04, D1-s2-55, D1-s2-05, D2-s1-51, D7-s2-02 | N-debug-swallow, N-late-try, N-reap-lock, P6, P2 | medium | opus | - | - | - | F1.4 |
| F1.6 | F1 | 7 | D1-s2-02, D1-s1-03, D14-s1-01, +P1-rca1, +P1-rca2 | N-plausibility, P1 | medium | opus | - | - | P1 | F1.5, F3.3, F4.1, F9.1 |
| F1.7 | F1 | 9 | D9-s1-03, D9-s2-01, D10-s1-03, D2-s2-01 | N-loop-cpu, P11, P2 | medium | opus | - | - | - | F1.6, F2.4, F4.2, F5.2, F10.1 |
| F1.8 | F1 | 10 | D14-s2-02, D12-s3-81, D10-s1-01 | P8, P2 | medium | opus | - | - | - | F1.7, F5.2, F6.2, F3.3 |
| F1.9 | F1 | 11 | +FI-sw1, +FI-sw2, +FI-sw3, +FI-sw4, +FI-rca1 | N-future-instant | barrier | sonnet | - | - | - | F1.8, F3.1 |
| F1.10 | F1 | 12 | D14-s3-01, D5-s2-02 | P3, I5 | low | opus | - | - | P3 | F1.9, F2.4 |
| F1.11 | F1 | 13 | D14-s1-02 | P6 | low | opus | - | - | P2, P6 | F1.10, F6.4 |
| F2.1 | F2 | 1 | D14-s4-01*, D12-s2-03, D2-s2-81, D2-s3-02, D5-s2-51 | P7, P3, N-sign-floor, I5 | high | opus | - | P3 | - | - |
| F2.2 | F2 | 2 | D9-s1-01, D9-s1-02, D9-s1-04, D9-s1-71, +RC-sw1 | N-solve-recompute | medium | opus | - | N-solve-recompute | - | F2.1 |
| F2.5 | F2 | 4 | +RC-rca1, +RC-rca2 | N-solve-recompute | barrier | opus | - | - | - | F2.2, F3.3 |
| F2.3 | F2 | 5 | D2-s1-01, D2-s1-02, D2-s2-03, D7-s1-71, D5-s2-03 | N-euler-coupled, P2, I5 | medium | opus | - | - | - | F2.5, F2.2, F4.1 |
| F2.4 | F2 | 8 | D12-s2-01, D8-s1-03, D0-s2-02 | P2, P4 | medium | opus | - | - | - | F2.3, F1.6, F7.2, F5.2 |
| F3.1 | F3 | 1 | D1-s3-01, D1-s1-01, D1-s1-04, D1-s3-05, D1-s1-02 | P2, P1, N-future-instant | high | opus | - | P2, P1, N-future-instant | N-future-instant | - |
| F3.2 | F3 | 2 | D1-s3-02, D1-s3-03, D12-s2-02, D1-s3-06, +FI-sw5 | P2, P1, N-future-instant | medium | opus | - | - | - | F3.1 |
| F3.3 | F3 | 3 | D1-s4-01, D1-s4-03, D1-s5-02, D1-s5-03, D1-s5-04 | P1, P2, N-min-gap | medium | opus | - | - | - | F3.2 |
| F4.1 | F4 | 1 | D1-s5-52, D1-s5-01, D1-s5-51, D2-s2-02, D2-s4-02 | P2, N-staleness, N-clamp-range | high | opus | - | - | - | - |
| F4.2 | F4 | 2 | D2-s4-01, D2-s4-81, D14-s3-03, D7-s2-01, +P5-rca1 | P5, N-fit-integrator | medium | opus | - | P5 | P5 | F4.1 |
| F5.1 | F5 | 1 | D4-s2-03, D4-s2-08, D4-s2-09, D8-s3-02, D8-s3-01, D5-s1-02*, D6-s2-03* | N-escape, N-service-icons, I5, N-name-sort | medium | sonnet | - | - | - | - |
| F5.2 | F5 | 4 | D4-s2-01, D4-s2-05, D4-s2-06, D4-s2-07, D10-s2-01 | P6, N-step-grid, P2, N-menu | medium | sonnet | - | - | - | F5.1, F1.2, F7.1 |
| F6.1 | F6 | 1 | D4-s1-01, D4-s1-02, D4-s1-03, D4-s1-05, +P9-rca1 | P9 | medium | sonnet | - | P9 | - | - |
| F6.1b | F6 | 2 | +P9-rca2, +P9-rca3, +P9-rca4 | P9 | barrier | sonnet | - | - | - | F6.1 |
| F6.2 | F6 | 3 | D4-s1-04, D5-s2-01 | N-keyboard, I5 | medium | sonnet | - | - | - | F6.1b, F6.1 |
| F6.3 | F6 | 4 | (class barrier) | - | barrier | opus | **yes** | - | P9 | F6.2 |
| F6.4 | F6 | 11 | D4-s2-81 | N-language | medium | sonnet | - | - | - | F6.3, F1.8 |
| F7.1 | F7 | 1 | D8-s2-02, D8-s2-03, D1-s3-04 | P2, N-shared-config | high | sonnet | - | - | - | - |
| F7.2 | F7 | 4 | D8-s1-02, D8-s3-03, D8-s3-61 | P2, N-dup-entity | low | sonnet | - | - | - | F7.1, F8.3 |
| F7.3 | F7 | 9 | D8-s2-01 | N-availability | medium | sonnet | **yes** | - | - | F7.2, F2.4 |
| F8.1 | F8 | 1 | D5-s1-01, D6-s2-01, D6-s2-02, D5-s1-04, D6-s2-05 | I5, N-markdown | medium | sonnet | - | I5 | - | - |
| F8.2 | F8 | 2 | D5-s1-05, D6-s1-02, D6-s2-04, D6-s1-01, D6-s1-03 | I5 | low | sonnet | - | - | - | F8.1 |
| F8.3 | F8 | 3 | D5-s1-02*, D6-s2-03*, D6-s1-81, D5-s1-03, D6-s2-05* | I5, P11 | medium | sonnet | - | - | - | F8.2, F5.1 |
| F9.1 | F9 | 2 | D3-s1-01, D3-s2-01, D3-s2-02, D3-s3-02, D3-s3-03 | I1 | medium | sonnet | - | I1 | - | F3.1 |
| F9.2 | F9 | 3 | D3-s3-04, D3-s3-05, D7-s3-51 | I1, N-finally-return | medium | sonnet | - | - | - | F9.1 |
| F10.1 | F10 | 1 | D1-s1-51, D1-s1-52, D1-s2-71, D14-s4-02* | P11 | low | opus | - | P11 | P11 | - |
| F10.2 | F10 | 5 | D9-s2-02, D9-s2-03, D9-s2-71 | N-cpu-gate-blind | medium | opus | **yes** | N-cpu-gate-blind | N-solve-recompute, N-cpu-gate-blind | F10.1, F1.1, F2.5 |
| F10.3 | F10 | 6 | D7-s1-02, D14-s5-02, D14-s5-01 | I1, I2 | medium | opus | **yes** | - | I1 | F10.2, F9.2 |
| F10.4 | F10 | 14 | D7-s3-01, D7-s3-72, D7-s3-02, D7-s1-01 | N-dead-member, I4, N-structure-blind | low | opus | **yes** | - | I5 | F10.3, F1.11, F7.3, F11.3 |
| F11.1 | F11 | 1 | D11-s1-71, D13-s1-01, D11-s2-02, D11-s1-02, D11-s1-72 | I4, I3 | medium | sonnet | - | I3, I4 | - | - |
| F11.2 | F11 | 2 | D11-s1-01, D11-s1-04, D11-s1-03, D13-s1-03 | I3 | medium | opus | **yes** | - | - | F11.1 |
| F11.3 | F11 | 3 | D11-s2-01, D11-s2-04, D13-s1-02 | I3, I5, N-approval-rebuy | medium | opus | **yes** | - | I3 | F11.2 |
| F11.4 | F11 | 15 | D14-s2-03 | I4 | low | opus | **yes** | - | I4 | F11.3, F10.4 |
| F11.5 | F11 | 16 | (class barrier) | - | barrier | sonnet | **yes** | - | - | F11.4 |

`*` = part of a finding; the finding closes when every PR listing it has merged (see the split list). `+` = a Phase D sweep instance (table below).

## Files per PR (package paths relative to custom_components/heatpump_optimizer/)

| PR | edits (owned by its lane) | borrows (file from lane) | tvofi because |
|---|---|---|---|
| F1.1 | coordinator.py, accuracy.py, dhw_learning.py, external_heat.py, tests/dst_checks.py, tests/open_meteo.py | tests/replay.py from F10 | - |
| F1.2 | coordinator.py | config_flow.py from F5, modbus_prefill.py from F5, topology.py from F5 | - |
| F1.3 | coordinator.py, button.py | - | - |
| F1.4 | coordinator.py, store.py, services.py, manual_plan.py | tests/finite_boundary.py from F9 | - |
| F1.5 | coordinator.py | - | - |
| F1.6 | coordinator.py, dhw_learning.py, manual_plan.py, store.py, accuracy.py | legionella.py from F3, boost.py from F3, pump_arbiter.py from F3, snapshots.py from F3, away.py from F3, comfort_learning.py from F3, inputs.py from F4, tests/finite_boundary.py from F9 | - |
| F1.7 | coordinator.py | sysid.py from F4, sensor.py from F7, topology.py from F5, optimizer.py from F2, tests/hastub/homeassistant/exceptions.py from F10, tests/hastub/homeassistant/helpers/update_coordinator.py from F10, tests/ha_contract.py from F10 | - |
| F1.8 | coordinator.py, services.py | inputs.py from F4, currency.py from F4, config_flow.py from F5, strings.json from F5, translations/en.json from F5, translations/sv.json from F5, tests/config_flow_steps.py from F5, www/heatpump-optimizer-card.js from F6, grid_fee.py from F3, price_model.py from F3 | - |
| F1.9 | coordinator.py | - | - |
| F1.10 | coordinator.py | defrost.py from F3, tariff.py from F3, away.py from F3, pump_arbiter.py from F3, const.py from F4, sysid.py from F4, optimizer.py from F2, thermal_model.py from F2 | - |
| F1.11 | coordinator.py | sensor.py from F7, boost.py from F3 | - |
| F2.1 | optimizer.py, pv.py | - | - |
| F2.2 | optimizer.py, thermal_model.py | - | - |
| F2.5 | optimizer.py | tariff.py from F3 | - |
| F2.3 | thermal_model.py, optimizer.py | const.py from F4 | - |
| F2.4 | optimizer.py | pump_arbiter.py from F3, entity.py from F7, sensor.py from F7, climate.py from F7 | - |
| F3.1 | away.py, boost.py, legionella.py, pump_arbiter.py, snapshots.py, curve_learning.py, comfort_learning.py, drift.py | store.py from F1, coordinator.py from F1, tests/finite_boundary.py from F9 | - |
| F3.2 | pump_arbiter.py, freq_control.py | - | - |
| F3.3 | defrost.py, price_model.py, tariff.py, open_meteo.py | - | - |
| F4.1 | inputs.py, const.py, flow_lift.py, sysid.py | - | - |
| F4.2 | sysid.py | - | - |
| F5.1 | strings.json, translations/en.json, translations/sv.json, icons.json | - | - |
| F5.2 | config_flow.py, strings.json, translations/en.json, translations/sv.json, icons.json, quality_scale.yaml, tests/config_flow_steps.py | climate.py from F7 | - |
| F6.1 | www/heatpump-optimizer-card.js, tests/card.mjs, tests/card_drift.mjs | - | - |
| F6.1b | www/heatpump-optimizer-card.js, tests/card.mjs, tests/card_drift.mjs | - | - |
| F6.2 | www/heatpump-optimizer-card.js, tests/card.mjs | - | - |
| F6.3 | tests/card_browser.mjs | - | tests/card_browser.mjs is code-owned |
| F6.4 | www/heatpump-optimizer-card.js | topology.py from F5, config_flow.py from F5, sensor.py from F7, strings.json from F5, translations/en.json from F5, translations/sv.json from F5 | - |
| F7.1 | climate.py, switch.py | - | - |
| F7.2 | sensor.py, binary_sensor.py | README.md from F8 | - |
| F7.3 | climate.py | - | the fix overturns the owner's recorded A3(e) decision pinned in tests/entities.py; tvofi rules first |
| F8.1 | docs/configuration.md | - | - |
| F8.2 | docs/configuration.md, docs/how-it-works.md, README.md | - | - |
| F8.3 | docs/setup.md, docs/ecl110.md, docs/configuration.md, docs/how-it-works.md, README.md, docs/dashboard-card.md | - | - |
| F9.1 | tests/finite_boundary.py | - | - |
| F9.2 | tests/nightly_ha.py | - | - |
| F10.1 | tests/hastub/homeassistant/helpers/storage.py, tests/hastub/homeassistant/util/dt.py, tests/hastub/homeassistant/helpers/update_coordinator.py, tests/ha_contract.py | - | - |
| F10.2 | tests/stress.py, tests/stress_budgets.json, tests/replay.py | - | tests/stress.py is code-owned; new stress_budgets.json entries and the loop_cpu_ratio budget go through budget-raise-gate |
| F10.3 | tests/env_drift.py, tests/stress.py, tests/mutation_table.py, tests/mutation_budgets.json, tests/closure.py, tests/derive_closures.sh, tests/deployment_shape.py, tests/doc_claims.py | - | tests/env_drift.py, tests/stress.py, tests/mutation_table.py, tests/closure.py and tests/derive_closures.sh are code-owned; the I1 prototype derives its counts at both ends and raises no mutation_budgets.json entry |
| F10.4 | tests/structure.py, tests/doc_claims.py | coordinator.py from F1, defrost.py from F3, open_meteo.py from F3, inputs.py from F4, optimizer.py from F2, thermal_model.py from F2, tests/open_meteo.py from F1 | D7-s1-01 prices coordinator state reached through module-level helpers, which likely raises coordinator budgets: ask before the push |
| F11.1 | .claude/workflows/policy_lint.mjs, .claude/workflows/rules_sync.mjs, tools/release/stamp.py | - | - |
| F11.2 | .github/workflows/tests.yml, .github/workflows/pr-contract.yml, .github/CODEOWNERS, .claude/workflows/budget_raise_gate.py, docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md | - | workflows, CODEOWNERS, budget_raise_gate.py and docs/decisions are code-owned; D11-s1-01 and D11-s1-04 are owner decisions |
| F11.3 | .claude/workflows/policy_lint.mjs, .claude/workflows/policy_budgets.json, .claude/rules/ratchet-budgets.md, .cursor/rules/ratchet-budgets.mdc, CLAUDE.md, tools/audit/briefs/fix-review.md, .claude/workflows/web-fix-wave.js, tools/audit/app_approve.sh, .claude/workflows/counts.mjs, .claude/workflows/fixtures/required-contexts.json, .claude/workflows/fixtures/policy-rot/citations.md, .github/workflows/governance.yml | - | policy (CLAUDE.md, .claude/rules, tools/audit/briefs) and web-fix-wave.js are code-owned |
| F11.4 | tools/audit/scopes.json, tools/audit/check_scopes.py, .claude/workflows/audit-find.js, .claude/workflows/check-wave-script.mjs, .github/workflows/governance.yml | - | audit-find.js is code-owned |
| F11.5 | tools/audit/briefs/fixer.md, tools/audit/briefs/root-cause.md, tools/audit/briefs/D1.md, tests/README.md, .claude/rules/defect-root-cause.md, .cursor/rules/defect-root-cause.mdc, .claude/workflows/policy_budgets.json | - | policy: tools/audit/briefs, .claude/rules and tests/README.md are code-owned; each draft needs tvofi's approval before this merges |

## Finding to PR (all 145 survivors)

| finding | sev | class | PR | title |
|---|---|---|---|---|
| D0-s2-02 | low | P4 | F2.4 | Multi-start seed set misses lower basins on shoulder prices, above the flat-price null |
| D1-s1-01 | medium | P1 | F3.1 | A tz-naive persisted timestamp raises on every cycle at three sibling loader seams (snapshots, curve, comfort) |
| D1-s1-02 | medium | P1 | F3.1 | A non-numeric snapshot temperature_bias makes best_restore raise and suppresses the accuracy_drift issue for good |
| D1-s1-03 | medium | N-plausibility | F1.6 | One out-of-range DHW thermometer sample is booked as a physically impossible draw and inflates the published p90 |
| D1-s1-04 | low | N-future-instant | F3.1 | A timestamp stored while the clock ran ahead is trusted verbatim and stretches stale timeouts by the clock error |
| D1-s1-51 | low | P11 | F10.1 | hastub Store decodes with stdlib json: 6 of 6 hostile number tokens load where HA's orjson Store drops the file |
| D1-s1-52 | low | P11 | F10.1 | hastub dt_util.now() is naive by default: the naive-vs-aware verdict of 6 of 6 stored-timestamp cells is inverted |
| D1-s2-02 | medium | N-plausibility | F1.6 | Finite-but-absurd weather forecast values reach the solve unbounded: failed plans and a runaway solve |
| D1-s2-03 | medium | P1 | F1.4 | A sample count past 2**64 in the thermal-learning store fails every cycle, across restarts |
| D1-s2-04 | medium | N-debug-swallow | F1.5 | Five cycle-path guards swallow a persistent failure at DEBUG, including pump and frequency actuation |
| D1-s2-05 | medium | N-reap-lock | F1.5 | Home Assistant stop waits out an in-flight solve before reaping the solve worker |
| D1-s2-51 | medium | P2 | F1.3 | A learner or arbiter raise on the cycle path fails the solve or the whole cycle and skips actuation and saves |
| D1-s2-52 | medium | N-restart | F1.4 | Five store writers do not wait for the startup read: a save in that window replaces persisted learned state |
| D1-s2-53 | medium | N-restart | F1.4 | set_thermal_parameters changes are silently lost at the next restart (24 of 26 fields) |
| D1-s2-54 (merged: D6-s1-04) | low | N-service-clamp | F1.4 | apply_manual_plan accepts expires_at past the horizon: the override owns all 96 steps unenforced |
| D1-s2-55 | medium | N-late-try | F1.5 | A solve worker that cannot start (Popen OSError) skips the in-process fallback: no plan, no fallback notice |
| D1-s2-71 | low | P11 | F10.1 | hastub DataUpdateCoordinator drops update_interval: the coordinator's cadence is unreadable in 4 of 4 cells |
| D1-s2-91 | medium | P2 | F1.3 | FlowCurveBias.observe raise aborts the cycle's accuracy pipeline and fails the whole update |
| D1-s3-01 | high | P2 | F3.1 | A tz-less return_time (card datetime-local) or a naive stored datetime wedges every cycle with TypeError |
| D1-s3-02 | medium | P2 | F3.2 | Pump-duty arbiter re-registers its timer and state listener on an unloaded coordinator and keeps writing the pump |
| D1-s3-03 | medium | P1 | F3.2 | pump_arbiter._load installs non-numeric set-point values that raise TypeError on every apply |
| D1-s3-04 | low | N-shared-config | F7.1 | Climate entity publishes the away setback as the user's target while the solve is in the executor |
| D1-s3-05 | low | N-future-instant | F3.1 | Boost 'two-hour maximum' is an absolute instant: a clock step back or a far-future store extends it without bound |
| D1-s3-06 | medium | P1 | F3.2 | FrequencyMap.from_dict admits an unbounded ratio or out-of-range decile that pins recommend() at hz_min for days |
| D1-s4-01 | low | P1 | F3.3 | DefrostDerate.from_dict admits non-finite/out-of-range duty; the bucket pins at DERATE_MIN and never recovers |
| D1-s4-02 | medium | P2 | F1.3 | A failed solve is returned as a plan with status 'failed (...)', so the coordinator counts it a success |
| D1-s4-03 | low | P1 | F3.3 | One unreadable cell in a v2 defrost store voids all 12 measured buckets and is labelled a pre-v5.3.0 upgrade |
| D1-s5-01 | medium | P2 | F4.1 | inputs.age_of ignores last_reported and accepts future stamps, diverging from InputReader's freshness rule |
| D1-s5-02 | medium | P1 | F3.3 | Learner-store loaders check finiteness but not the domain their own update path enforces (price shape, peak tracker) |
| D1-s5-03 | low | P2 | F3.3 | One huge JSON integer drops a whole price fetch (entity and Tibber) or Open-Meteo refresh instead of one row |
| D1-s5-04 | low | N-min-gap | F3.3 | One off-grid timestamp collapses Open-Meteo's inferred resolution and erases the whole solar horizon |
| D1-s5-51 | medium | N-staleness | F4.1 | A report-on-change indoor thermometer silent over 60 min turns Indoor Temperature unavailable |
| D1-s5-52 | high | P2 | F4.1 | InputReader has no plausibility window: -127 and 85 degC sentinels deliver as ok readings |
| D2-s1-01 | medium | N-euler-coupled | F2.3 | Euler sub-step guard judges each store's diagonal ratio only, so coupled stores in accepted configs diverge |
| D2-s1-02 | low | P2 | F2.3 | DHW refill coil debits the wood tank the full coil heat but spares the DHW tank only its scaled share |
| D2-s1-51 | low | P6 | F1.5 | DHW setpoint advisor prices candidates at the 5.0 degC ThermalState default when no outdoor thermometer is mapped |
| D2-s2-01 | medium | P2 | F1.7 | Settlement caps (slab_settlement_cap, hold_demand_kw) ignore the learned house_heat_loss_scale the dynamics apply |
| D2-s2-02 | medium | N-clamp-range | F4.1 | #1067 flow-lift bias clamp (15 K) cannot reach real supply: model curve tops out at 27.9 C, COP overstated up to 37% |
| D2-s2-03 | low | P2 | F2.3 | DHW-path savings settle-up replays space schedule without the DHW coil: end state differs from published trajectory |
| D2-s2-81 | medium | P3 | F2.1 | Two-zone comfort penalty halves each zone's floor price; shipped plans sit up to 0.46 K below min_temp |
| D2-s3-01 (merged: D8-s1-01) | high | P2 | F1.3 | _current_spot_price reads a quarter up to 45 min stale under 15-minute price entries |
| D2-s3-02 | low | N-sign-floor | F2.1 | PV piecewise cost clipped by import_margin's zero floor wherever import price < export price |
| D2-s4-01 | low | P5 | F4.2 | sysid adoption interval misses the true UA on 14 of 22 fits it admits; admitted fits biased high |
| D2-s4-02 | medium | P2 | F4.1 | sysid step sized to exactly the abort bound: sensor noise aborts 100 of 294 experiments, light_new 81 of 96 |
| D2-s4-81 | medium | P5 | F4.2 | sysid cannot adopt its own exact noise-free fit on 43 of 80 preset houses, yet arms on all 80 |
| D3-s1-01 | low | I1 | F9.1 | No closure script fails when _dhw_inlet_c's lower plausibility bound moves (-5.0 <= value -> -5.0 < value) |
| D3-s1-91 | medium | I1 | F1.1 | coordinator.py tzinfo guards (:8112, :8384) are dead under the gate's naive clock; unblinded they crash |
| D3-s2-01 | low | I1 | F9.1 | Store-parser non-finite guards in flow_lift, tariff, price_model survive deletion: no gate driver notices |
| D3-s2-02 | low | I1 | F9.1 | PriceShapeModel residual_var restore can discard every stored variance with the gate green |
| D3-s3-01 | medium | I1 | F1.1 | Every gate driver runs with process local time = UTC, so open_meteo's naive-stamp UTC guard is deletable |
| D3-s3-02 | medium | I1 | F9.1 | DrawStats.from_dict can zero the open draw occurrence and no gate check notices |
| D3-s3-03 | medium | I1 | F9.1 | MonthlyLedger.add's non-finite guard is unpinned; one NaN amount loses the month on reload |
| D3-s3-04 | medium | I1 | F9.2 | No gate check observes a positive draw folded by DhwProfileLearner.async_fold_draw_stats |
| D3-s3-05 | low | I1 | F9.2 | The disinfection write-failed notice memo is unpinned |
| D4-s1-01 | medium | P9 | F6.1 | Status text coloured by HA's --success/--error/--warning-color fails WCAG AA on the default themes |
| D4-s1-02 | low | P9 | F6.1 | Lane slot menu is placed at the tap point unclamped; near the right edge it spills past its chart and the viewport |
| D4-s1-03 | medium | P9 | F6.1 | Setup picker: two identically named sensors render as identical options at 375 and 768 px |
| D4-s1-04 | medium | N-keyboard | F6.2 | Setup layout editor: removing a pipe, drawing a pipe and moving a box have no keyboard route |
| D4-s1-05 | medium | P9 | F6.1 | Now-marker label prints over the measured-now reading on the live default view |
| D4-s2-01 | medium | P6 | F5.2 | Setup wizard's device pre-fill page shows raw keys: 3 unlabelled fields and 1 untranslated error |
| D4-s2-03 | medium | N-escape | F5.1 | The hot-water minimum error text shows literal '\u00b0C' (en) and 9 escaped letters (sv) |
| D4-s2-05 | low | N-step-grid | F5.2 | 12 number fields start off their own step grid: native validity flags them, one spinner click gives 5.1 not 5.5 |
| D4-s2-06 | low | P2 | F5.2 | The zones page computes the derivation-overwrite warning but never shows it for its 6 derived fields |
| D4-s2-07 | low | N-menu | F5.2 | After 'Quick setup (recommended)' the wizard returns to the identical menu, offering quick setup again |
| D4-s2-08 | low | N-service-icons | F5.1 | None of the 12 registered services has an icon in icons.json |
| D4-s2-09 | low | I5 | F5.1 | 8 help texts per language write '45 C' / 'W/m2' beside selectors that say °C and m² |
| D4-s2-81 | medium | N-language | F6.4 | Setup overview page and setup diagram publish English slot text on a Swedish install |
| D5-s1-01 | medium | I5 | F8.1 | configuration.md 'Initial setup' documents the pre-v6.6.5 flow: no finish menu, Tibber token required, 74 entities |
| D5-s1-02 | medium | I5 | F5.1 (L2 seam: the quick-setup text in en.json and sv.json), F8.3 (docs/setup.md) | setup.md Quick setup promises buffer storage and two-tank physics that the quick-setup answers cannot produce |
| D5-s1-03 | low | I5 | F8.3 | dashboard-card.md says the card version lags the integration; the stamp keeps them equal every release |
| D5-s1-04 | low | N-markdown | F8.1 | configuration.md has 9 lines a GFM renderer misplaces: 3 table rows as pipe text, 6 prose lines as rows |
| D5-s1-05 | low | I5 | F8.2 | Docs name 5 option fields by labels the options forms do not show |
| D5-s2-01 | low | I5 | F6.2 | Card comments cite 12 private members the card no longer has (17 mentions) |
| D5-s2-02 | low | I5 | F1.10 | Three comments cite a number the code beside them does not deliver |
| D5-s2-03 | low | I5 | F2.3 | DHW_COLD_WATER_TEMP comment claims the draw model heats from it; the draw reads the configured inlet |
| D5-s2-51 | low | I5 | F2.1 | Two optimizer comments describe a data flow the code does not have (warm-start alignment, buffer-series stash) |
| D6-s1-01 | low | I5 | F8.2 | README's Heat Pump Action state list omits idle and system_identification, which the sensor publishes |
| D6-s1-02 | low | I5 | F8.2 | README puts the two-zone split and the orientation factor on the wrong options pages |
| D6-s1-03 | low | I5 | F8.2 | README's disabled-by-default census omits six hot-water sensors that the no-hot-water install disables |
| D6-s1-81 | low | P11 | F8.3 | README's SEK currency fallback is unreachable under Home Assistant core, which defaults Config.currency to EUR |
| D6-s2-01 | low | I5 | F8.1 | configuration.md says 'All 74 entities'; the six platforms create 75 |
| D6-s2-02 | low | I5 | F8.1 | configuration.md: the weather page does not create the entry; the setup flowchart omits the menu and overview |
| D6-s2-03 | low | I5 | F5.1 (L2 seam: the curve-bias figure in strings.json), F8.3 (docs) | Curve-bias 'at most 0.5 K per week' is false: 0.6 K in a 7-day window |
| D6-s2-04 | low | I5 | F8.2 | how-it-works.md: space solve 'from two starting points'; it runs four, each refined and polished |
| D6-s2-05 (merged: D5-s1-06) | low | I5 | F8.1, F8.3 (the two seams the I5 RCA found beyond the simulate_plan list: assign_entity's manual_setpoint field, and apply_topology's dhw and wood fields, all undocumented in configuration.md's Services paragraphs) | configuration.md simulate_plan field list omits the five wood fields |
| D7-s1-01 | low | N-structure-blind | F10.4 | Structural ratchet does not price coordinator state reached via module-level _helper(self, ...) |
| D7-s1-02 | low | I1 | F10.3 | Drift-gate comparison and stress per-scenario budget verdict are deletable with every runnable check green |
| D7-s1-71 | low | P2 | F2.3 | Cold-water inlet default held three times: 3 of 5 sites ignore DEFAULT_DHW_INLET_TEMP when it moves |
| D7-s2-01 | medium | N-fit-integrator | F4.2 | sysid two-state fit rolls the candidate one Euler step per sample: UA 17-25% low, 0/3 presets adopt |
| D7-s2-02 | medium | P2 | F1.5 | Defrost derate fallback folds meter ratios _cop_fold_blocked refuses to the COP learner |
| D7-s3-01 | low | N-dead-member | F10.4 | 10 class members are reached by no production code; 9 are kept only by tests that pin them |
| D7-s3-02 | low | I4 | F10.4 | structure.py dead_methods reads 0 while 9 members are dead: properties skipped, bare-name loads count |
| D7-s3-51 | low | N-finally-return | F9.2 | nightly_ha._async_check_a4 returns inside finally: an in-flight CancelledError or KeyboardInterrupt is swallowed |
| D7-s3-72 | low | N-dead-member | F10.4 | 4 of 5 ThermalModel per-step scratch members are written every step and read by no production consumer |
| D8-s1-02 | low | P2 | F7.2 | DHW Heating Schedule counts 15-minute steps as 'heating periods', disagreeing with DHW Heating Plan's slot count |
| D8-s1-03 | low | P2 | F2.4 | Recommended Power publishes a sub-threshold draw at steps Heat Pump Action reports 'off' |
| D8-s2-01 | medium | N-availability | F7.3 | Climate entity is unavailable with no indoor thermometer, taking the thermostat control with it |
| D8-s2-02 | high | P2 | F7.1 | Climate hvac_action publishes off while an active boost runs the pump in optimizer mode off |
| D8-s2-03 | low | P2 | F7.1 | Mode actions publish a state that mixes the live mode with the stale payload mode |
| D8-s3-01 | low | N-name-sort | F5.1 | Accuracy and Energy-dashboard meter families split in both English and Swedish name sort |
| D8-s3-02 | low | I5 | F5.1 | Swedish name of Sensor-Gap Advisor reads 'sensor gap in the currency' and drops the advisor role |
| D8-s3-03 | low | N-dup-entity | F7.2 | Upper Floor Temperature, a byte duplicate of Indoor Temperature, is enabled by default on every install |
| D8-s3-61 | low | P2 | F7.2 | Valve Target Recommendation ships disabled where a mixing valve is set, and available-but-unknown where none is |
| D9-s1-01 | medium | N-solve-recompute | F2.2 | Per-row Python loop in _comfort_terms_batch costs 13-32% of every solve; a row-vectorized twin is bit-identical here |
| D9-s1-02 | medium | N-solve-recompute | F2.2 | L-BFGS-B asks the scalar objective for f(x) every iterate at ~19-26x a batched row: 9-19% of the solve |
| D9-s1-03 | low | N-loop-cpu | F1.7 | The sysid two-state fit runs inside one event-loop callback: 43-228 ms here (1.1-6x a reference solve) |
| D9-s1-04 | low | N-solve-recompute | F2.2 | DHW min-run repair: a full-suffix re-simulation per refused weak slot, 12-23% of a single-zone DHW solve |
| D9-s1-71 | low | N-solve-recompute | F2.2 | Constant DHW parameter helpers recomputed ~15-45k times per solve; a per-solve cache saves 3-17 % of CPU |
| D9-s2-01 | low | N-loop-cpu | F1.7 | sensor_advisor ranking re-simulated on the event loop at every plan-sensor write: ~32% of loop CPU |
| D9-s2-02 | medium | N-cpu-gate-blind | F10.2 | No budgeted check sees a 2x of the coordinator's loop-thread work; stress.py reaches none of it |
| D9-s2-03 | medium | N-cpu-gate-blind | F10.2 | stress.py misses a 2x solve regression in one scenario when the extra work is outside the simulate seams |
| D9-s2-71 | medium | N-cpu-gate-blind | F10.2 | stress.py samples 0 of 51 throttling-valve plants; a valve adds 1.3-2.7x solve CPU the gate never sees |
| D10-s1-01 | medium | P2 | F1.8 | Entry unique id is not re-derived after reauth or an options edit, so the same plant can be set up twice |
| D10-s1-02 | medium | P2 | F1.3 | Optimize-now button press returns normally when the solve did not run; the run_optimization action raises |
| D10-s1-03 | low | P11 | F1.7 | Tibber auth refusal reaches HA as ConfigEntryNotReady/UpdateFailed, never ConfigEntryAuthFailed |
| D10-s2-01 | low | P6 | F5.2 | Climate presets auto and economy are non-standard and have no translation or icon in any language |
| D11-s1-01 | medium | I3 | F11.2 | A code-owned change pushed after the owner approval merges on that stale approval (dismiss_stale_reviews=false) |
| D11-s1-02 | medium | I3 | F11.1 | A non-stamp direct push to main over the DeployKey bypass is reported by no enumerator |
| D11-s1-03 | low | I3 | F11.2 | Three pull_request jobs execute the PR's own code-owned scripts while holding contents:write + actions:write |
| D11-s1-04 (merged: D11-s2-03) | medium | I3 | F11.2 | Owner approvals given by the orchestrator are indistinguishable from the owner's in GitHub's record |
| D11-s1-71 | low | I4 | F11.1 | Two parsers of a rule's paths: frontmatter disagree on 2 of 6 legal shapes (rules_sync vs policy_lint) |
| D11-s1-72 | low | I4 | F11.1 | entities.py GOV pin reads governance.yml only: a new governance job in 3 of 3 other workflow files passes |
| D11-s2-01 | low | I3 | F11.3 | Per-file policy caps count lines, so a capped rule file grows in prose with its per-file budget check green |
| D11-s2-02 | low | I3 | F11.1 | policy_lint --hooks never reads a hook's matcher: a PreToolUse matcher naming no edit tool passes as wired |
| D11-s2-04 | low | I5 | F11.3 | CLAUDE.md rule 1 quotes a mode line the gate does not print, and says FULL prints a zero it does not |
| D12-s1-01 | high | P6 | F1.2 | Hot water without a tank probe: every solve starts from the 55 C ThermalState default, never advanced |
| D12-s2-01 | medium | P2 | F2.4 | On an on/off pump, the switch path switches off steps whose planned heat the plan books as delivered |
| D12-s2-02 | medium | P2 | F3.2 | The pump-duty arbiter writes the operating mode with select.select_option whatever domain the mode slot holds |
| D12-s2-03 | medium | P3 | F2.1 | On an on/off pump every full-power step publishes as 'eco' and power_normalized runs to -60 |
| D12-s3-01 (merged: D4-s2-04, D12-s1-02) | medium | P2 | F1.2 | Full config-flow wizard invents a DHW tank and a second zone the user never affirmed |
| D12-s3-81 | medium | P8 | F1.8 | Grid-fee bounds are SEK numbers: a 0.05 EUR/kWh fee is unenterable in HUF, ISK, JPY and KRW |
| D13-s1-01 | medium | I4 | F11.1 | --stats API-mode enumerator silently drops 52 of 253 window merges whose /commits/<sha>/pulls answers [] |
| D13-s1-02 | medium | N-approval-rebuy | F11.3 | 22 re-verification rounds after a moved head caught 0 defects; 12 heads moved only by merges or ci: commits |
| D13-s1-03 | medium | I3 | F11.2 | Body-answer blocks (8) exceed every engineering block class (max 1); record-and-body 12 vs engineering 7 |
| D14-s1-01 | medium | P1 | F1.6 | P1: a malformed store leaf raises out of a loader or consumer; a naive legionella timestamp wedges every refresh |
| D14-s1-02 | low | P6 | F1.11 | P6: horizon_hours read from coordinator.data but never written; boost probes a field only a test double defines |
| D14-s2-01 | medium | P2 | F1.2 | P2: the two-zone and wood-furnace facts are re-derived from a proxy key at three seams beside their canonical predicate |
| D14-s2-02 (merged: D4-s2-02) | medium | P8 | F1.8 | P8: a money figure's currency comes from the label source, never from the price feed that denominates it |
| D14-s2-03 | low | I4 | F11.4 | I4: class roster and finding grammar have disagreeing readers (P11 on no D14 seat; intake admits schema-refused ids) |
| D14-s3-01 | low | P3 | F1.10 | P3: 22 quantities are read through a positive floor at one seam and raw at a sibling; no check enumerates them |
| D14-s3-03 | medium | P5 | F4.2 | P5: sysid adoption gate keys on the UA half-width, which barely moves while unmodelled free heat biases UA to -21 % |
| D14-s4-01 | high | P7 | F1.1 (coordinator, accuracy, dhw_learning and external_heat seams, plus the DST tracer barrier), F2.1 (optimizer seam: get_current_action step length) | Eight production seams still do wall-clock datetime arithmetic across DST; the forecast grid lands 60 min off |
| D14-s4-02 | low | P11 | F1.1, F10.1 (the stub half: freeze normalises a frozen value into the configured zone, and utcnow derives from now, so it stays UTC under an aware freeze) | The replay lane freezes a fixed-offset clock, so a DST-day replay reports zero P7 seams |
| D14-s5-01 | medium | I2 | F10.3 | Python closures miss every file a spawned child process reads; select() skips the script on a change to it |
| D14-s5-02 | medium | I1 | F10.3 | Mutation ratchet inventory cannot see 528 of 2313 production guard seams; a new guard of those shapes raises it by 0 |

## Instances beyond the judged findings (Phase D sweeps and the RCA fold)

Line numbers are at baseline `1936d5ca`. A sweep instance's probe is under its sweep's commit; an RCA instance's failing test is its RCA prototype or evidence. N final = judged findings + the rows of kind `instance`; a `latent` seam fills a PR slot and is not counted. `closed by` names the PR whose change closes the seam when the row's PR carries only its regression test.

| instance | class | found by | kind | PR | closed by | seam | what fails | failing test |
|---|---|---|---|---|---|---|---|---|
| P1-rca1 | P1 | RCA (p1) | latent | F1.6 | - | accuracy.py: AccuracySample.from_dict keeps a naive stored instant (the accuracy and dhw_accuracy samples' t leaves) | latent: no current consumer raises, but the P1 barrier's Arm 4 refuses a naive instant held live; apply F3.1's stored-instant rule here (aware, or dropped, at load) | the P1 barrier's Arm 4 (handoff/r9-rca-p1@0ade2456), seeded with the accuracy samples |
| P1-rca2 | P1 | RCA (p1) | latent | F1.6 | - | coordinator.py: the thermal-learning store's immersion_events list (restored strings kept naive; its one consumer normalises them) | latent, same as P1-rca1: Arm 4 refuses the naive leaf held live | the P1 barrier's Arm 4 (handoff/r9-rca-p1@0ade2456), seeded with an immersion event |
| P5-rca1 | P5 | RCA (p5) | instance | F4.2 | - | sysid.py: adoption_decision on a plant whose slab mass is half the declared value (heavy_old, single zone) | admitted at a UA scale of 0.8827, outside the bar; graded 0.9 to 0.5 and refused only at 0.4. The sweep's p5_gate perturbs the declared room mass and slab transfer but never slab mass | the P5 barrier's axis sweep (handoff/r9-rca-p5@d4cf63d9, the slab-mass axis) |
| P9-rca1 | P9 | RCA (p9) | instance | F6.1 | - | www/heatpump-optimizer-card.js: the setup picker's armed clear button (button.sp-save.confirm, 'Confirm: clear this sensor') | white on the theme's error colour at 4.29:1, under 4.5, in 4 cells; same cause as D4-s1-01's wi-save confirm state, in a state the sweep never reached | the P9 barrier's grid (handoff/r9-rca-p9@4f3b9d4f), contrast rule |
| P9-rca2 | P9 | RCA (p9) | instance | F6.1b | - | www/heatpump-optimizer-card.js: the 'estimated prices' label on the estimated price band (every price estimated, a price source down) | 3.94:1 contrast, under 4.5, en and sv, 6 cells | the P9 barrier's grid (handoff/r9-rca-p9@4f3b9d4f), contrast rule |
| P9-rca3 | P9 | RCA (p9) | instance | F6.1b | - | www/heatpump-optimizer-card.js: the now label against the 'estimated prices' label | 17 to 153 px of shared glyph ink at 375, 768 and 1280 px, en and sv, 7 cells: D4-s1-05's mechanism at a second seam, contradicting the card's own comment that the two never meet | the P9 barrier's grid (handoff/r9-rca-p9@4f3b9d4f), shared-ink rule |
| P9-rca4 | P9 | RCA (p9) | instance | F6.1b | - | www/heatpump-optimizer-card.js: the candidate slot tap target (rect.slot-hit, 17.4 by 24.5 px in the shared-steps state at 375 px) | candidate, counted: overlapped 2.3 and 7.3 px by its neighbours' grown targets, so it fails the 2.5.8 spacing exception; the card grows each target against its neighbours' ink, not their grown targets. It needs a fix design: one attempt (half-gap growth) made 53 targets worse | the P9 barrier's grid (handoff/r9-rca-p9@4f3b9d4f), target rule |
| RC-sw1 | N-solve-recompute | S5 @ `51a2e98a86` | instance | F2.2 | - | optimizer.py: cycling_penalty_batch | the same per-row Python loop as D9-s1-01's, in an independent function called once per iterate | tools/audit/round9/D14/sweep/avoidable-interpreter-bound-recomputation/enumerate.py |
| RC-rca1 | N-solve-recompute | RCA (avoidable-interpreter-bound-recomputation) | instance | F2.5 | - | tariff.py: tariff.peak_cost_batch's per-row loop (metering windows, day peaks, plateau-aware day max and the smooth top-k sum re-entered per row) | 62 percent of a winter two-zone DHW capacity-tariff solve and 47 percent of the gate's dearest scenario; no round-9 finding, sweep, issue or brief named it (S5 scanned optimizer.py and ThermalParameters only) | the recompute RCA's share harness in its evidence folder, and the production-call channel (handoff/r9-rca-avoidable-interpreter-bound-recomputation@ab04e39b) |
| RC-rca2 | N-solve-recompute | RCA (avoidable-interpreter-bound-recomputation) | instance | F2.5 | - | optimizer.py: the per-row loop inside the closure _terminal_cost_batch returns (entered about 382 times per solve) | 2.2 to 3.1 percent of the solve; S5 keyed the loop to the outer builder, which runs once, and disposed it not applicable, a blind spot for every per-row twin #985 built as a closure | the recompute RCA's share harness in its evidence folder |
| FI-sw1 | N-future-instant | S7 @ `1152a74346` | instance | F1.9 | F3.1 | coordinator.py: the fuse advisor's 7-day recompute cooldown (_fuse_advisor_at restored from the ledger store; baseline lines 8007 and 8023-8024) | a restored instant written ahead of the clock holds the cooldown; the RCA corrected S7: month-bounded, at most min(skew, the rest of the month), because the ahead clock writes the month too | the future-instant RCA's real-loader reproduction (not S7's probe_fuse_advisor.py, which hard-codes same_month) |
| FI-sw2 | N-future-instant | S7 @ `1152a74346` | instance | F1.9 | F3.1 | coordinator.py: the heavy-snow damping window (_last_heavy_snow restored from the store; baseline lines 2953 and 6306) | damping stays on while the restored instant is ahead of now; closed by F3.1's boundary, F1.9 adds its test | the future-instant RCA's real-loader reproduction |
| FI-sw3 | N-future-instant | S7 @ `1152a74346` | instance | F1.9 | - | coordinator.py: _detect_outage's staggered-recovery window (the stored last_tick; baseline lines 7343 and 8099-8114) | a future last_tick masks a real outage, and no bound fixes it: restore and read share one now, so a clamp gives gap 0 and the outage stays masked. This seam owes a decision (tvofi): treat a stored last_tick ahead of now as an outage, or accept one masked recovery per clock-corrected restart | the future-instant RCA's real-loader reproduction (the outage row stays False on the prototype) |
| FI-sw4 | N-future-instant | S7 @ `1152a74346` | instance | F1.9 | F3.1 | coordinator.py: the immersion-event recency count (_immersion_events; baseline line 8381) | reproduced by the RCA through the real store (immersion margin 2.0 against 0.0 with three events); closed by F3.1's boundary, F1.9 adds its test | the future-instant RCA's real-loader reproduction |
| FI-sw5 | N-future-instant | S7 @ `1152a74346` | instance | F3.2 | F3.1 | pump_arbiter.py: hold()'s write-echo grace period (held.written restored in _load; baseline lines 629 and 405-407) | a restored write instant ahead of the clock keeps the grace period open; closed by F3.1's boundary, F3.2 adds the echo-grace row or records it closed | tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/probe_more_instances.py |
| FI-rca1 | N-future-instant | RCA (persisted-future-instant-trusted-without-bound) | instance | F1.9 | F3.1 | legionella.py: LegionellaGuard's restore of last_cycle and last_attempt through dt_util.parse_datetime (baseline lines 121 and 127) | with a stamp 400 days ahead, anti-legionella disinfection is postponed for the whole skew (due_in_hours 168 against -1032), because hours_since floors the age at zero; S7's fromisoformat grep cannot see parse_datetime | the future-instant RCA's real-loader reproduction (legionella row) |

Re-dispositioned at the RCA fold, no longer instances: **P1-sw1** and **P1-sw2** (not store-reachable; defence-in-depth, P1 RCA) and **P9-sw1** (a box-metric artefact, 0 px shared ink, P9 RCA).

## Class to PR

Seams are the sweep's own dispositions (`instance`, `guarded`, `not applicable`), every one listed in the lane brief of each lane that holds the class.

| class | N judge | N sweep | N final | rca | sweep | seams | PRs | barrier PR |
|---|---|---|---|---|---|---|---|---|
| P2 | 27 | 27 | 27 | yes | S1 @ `c44e7bcd60` | 27 instance | F1.3, F3.1, F3.2, F4.1, F3.3, F2.3, F1.7, F5.2, F1.5, F7.2, F2.4, F7.1, F1.8, F1.2 | F1.11 |
| I5 | 19 | 19 | 19 | yes | S2 @ `38f1230e92` | 16 instance, 4 not applicable | F5.1, F8.1, F8.3, F8.2, F6.2, F1.10, F2.3, F2.1, F11.3 | F10.4 |
| I1 | 11 | 11 | 11 | yes | S3 @ `053c4869ad` | 12 instance | F9.1, F1.1, F9.2, F10.3 | F10.3 |
| P1 | 9 | 11 | 9 | yes | S3 @ `053c4869ad` | 6 guarded, 14 instance, 2 not applicable | F3.1, F1.4, F3.2, F3.3, F1.6 | F1.6 |
| I3 | 7 | 7 | 7 | yes | S4 @ `b2e3560671` | 1 guarded, 26 instance, 3 not applicable | F11.2, F11.1, F11.3 | F11.3 |
| P11 | 6 | 6 | 6 | yes | S4 @ `b2e3560671` | 6 instance, 2 not applicable | F10.1, F8.3, F1.7, F1.1 | F10.1 |
| I4 | 5 | 5 | 5 | yes | S4 @ `b2e3560671` | 2 guarded, 8 instance | F10.4, F11.1, F11.4 | F11.4 |
| P6 | 5 | 5 | 5 | yes | S4 @ `b2e3560671` | 1 guarded, 12 instance | F1.5, F5.2, F1.2, F1.11 | F1.11 |
| P9 | 4 | 5 | 8 | yes | S5 @ `51a2e98a86` | 5 instance, 1 not applicable | F6.1, F6.1b | F6.3 |
| N-solve-recompute | 4 | 5 | 7 | yes | S5 @ `51a2e98a86` | 7 instance, 1 not applicable | F2.2, F2.5 | F10.2 |
| P3 | 3 | 3 | 3 | yes | S5 @ `51a2e98a86` | 1 guarded, 3 instance | F2.1, F1.10 | F1.10 |
| P5 | 3 | 3 | 4 | yes | S5 @ `51a2e98a86` | 3 instance, 1 not applicable | F4.2 | F4.2 |
| N-cpu-gate-blind | 3 | 3 | 3 | yes | S5 @ `51a2e98a86` | 3 instance | F10.2 | F10.2 |
| P8 | 2 | 2 | 2 | no | S6 @ `6b65c9c4a8` | 2 guarded, 8 instance, 1 not applicable | F1.8 | - (N below 3, not barriered) |
| N-loop-cpu | 2 | 2 | 2 | no | S7 @ `1152a74346` | 2 instance | F1.7 | - (N below 3, not barriered) |
| N-plausibility | 2 | 2 | 2 | no | S6 @ `6b65c9c4a8` | 2 guarded, 2 instance | F1.6 | - (N below 3, not barriered) |
| N-future-instant | 2 | 7 | 8 | yes | S7 @ `1152a74346` | 10 instance, 9 not applicable | F3.1, F1.9, F3.2 | F3.1 |
| N-dead-member | 2 | 2 | 2 | no | S6 @ `6b65c9c4a8` | 7 instance, 1 not applicable | F10.4 | - (N below 3, not barriered) |
| N-restart | 2 | 2 | 2 | yes (barriered) | S5 @ `51a2e98a86` | 1 guarded, 2 instance | F1.4 | F1.4 |
| I2 | 1 | 1 | 1 | no | S7 @ `1152a74346` | 2 instance | F10.3 | - (N below 3, not barriered) |
| P4 | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 2 instance | F2.4 | - (N below 3, not barriered) |
| P7 | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 guarded, 8 instance, 1 not applicable | F1.1, F2.1 | - (N below 3, not barriered) |
| N-sign-floor | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 3 instance, 1 not applicable | F2.1 | - (N below 3, not barriered) |
| N-approval-rebuy | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F11.3 | - (N below 3, not barriered) |
| N-name-sort | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 2 instance | F5.1 | - (N below 3, not barriered) |
| N-dup-entity | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 instance, 2 not applicable | F7.2 | - (N below 3, not barriered) |
| N-late-try | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance | F1.5 | - (N below 3, not barriered) |
| N-euler-coupled | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F2.3 | - (N below 3, not barriered) |
| N-fit-integrator | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance, 1 not applicable | F4.2 | - (N below 3, not barriered) |
| N-clamp-range | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F4.1 | - (N below 3, not barriered) |
| N-markdown | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 2 instance | F8.1 | - (N below 3, not barriered) |
| N-service-icons | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F5.1 | - (N below 3, not barriered) |
| N-debug-swallow | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 3 guarded, 1 instance | F1.5 | - (N below 3, not barriered) |
| N-keyboard | 1 | 1 | 1 | no | S7 @ `1152a74346` | 3 guarded, 1 instance | F6.2 | - (N below 3, not barriered) |
| N-finally-return | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance, 2 not applicable | F9.2 | - (N below 3, not barriered) |
| N-step-grid | 1 | 1 | 1 | no | S7 @ `1152a74346` | 2 instance, 1 not applicable | F5.2 | - (N below 3, not barriered) |
| N-min-gap | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance, 1 not applicable | F3.3 | - (N below 3, not barriered) |
| N-service-clamp | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 guarded, 1 instance, 1 not applicable | F1.4 | - (N below 3, not barriered) |
| N-reap-lock | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance | F1.5 | - (N below 3, not barriered) |
| N-shared-config | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F7.1 | - (N below 3, not barriered) |
| N-staleness | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 2 instance, 2 not applicable | F4.1 | - (N below 3, not barriered) |
| N-menu | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 guarded, 1 instance | F5.2 | - (N below 3, not barriered) |
| N-structure-blind | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 6 instance, 1 not applicable | F10.4 | - (N below 3, not barriered) |
| N-language | 1 | 1 | 1 | no | S7 @ `1152a74346` | 4 instance | F6.4 | - (N below 3, not barriered) |
| N-escape | 1 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 1 instance | F5.1 | - (N below 3, not barriered) |
| N-availability | 1 | 1 | 1 | no | S7 @ `1152a74346` | 1 instance, 2 not applicable | F7.3 | - (N below 3, not barriered) |

## Owned files and borrow edges

| lane | name | fixer models (per PR) | owns |
|---|---|---|---|
| F1 | Coordinator cycle, state and clock | F1.1 opus, F1.2 opus, F1.3 opus, F1.4 opus, F1.5 opus, F1.6 opus, F1.7 opus, F1.8 opus, F1.9 sonnet, F1.10 opus, F1.11 opus | coordinator.py, services.py, store.py, button.py, manual_plan.py, accuracy.py, external_heat.py, dhw_learning.py, tests/dst_checks.py, tests/open_meteo.py |
| F2 | Solver and plant model | F2.1 opus, F2.2 opus, F2.5 opus, F2.3 opus, F2.4 opus | optimizer.py, pv.py, thermal_model.py |
| F3 | Persisted stores and price/weather feeds | F3.1 opus, F3.2 opus, F3.3 opus | snapshots.py, curve_learning.py, comfort_learning.py, pump_arbiter.py, freq_control.py, defrost.py, legionella.py, boost.py, away.py, drift.py, disinfection.py, price_model.py, tariff.py, open_meteo.py, grid_fee.py, dhw_draws.py, ledger.py |
| F4 | Inputs, constants, sysid and flow-lift | F4.1 opus, F4.2 opus | inputs.py, const.py, sysid.py, flow_lift.py, currency.py |
| F5 | Config flow and translated text | F5.1 sonnet, F5.2 sonnet | config_flow.py, strings.json, translations/en.json, translations/sv.json, icons.json, quality_scale.yaml, quick_setup.py, modbus_prefill.py, topology.py, tests/config_flow_steps.py |
| F6 | Dashboard card | F6.1 sonnet, F6.1b sonnet, F6.2 sonnet, F6.3 opus, F6.4 sonnet | www/heatpump-optimizer-card.js, tests/card.mjs, tests/card_rig.mjs, tests/card_drift.mjs, tests/card_browser.mjs |
| F7 | Entities | F7.1 sonnet, F7.2 sonnet, F7.3 sonnet | sensor.py, climate.py, switch.py, entity.py, binary_sensor.py |
| F8 | User documentation | F8.1 sonnet, F8.2 sonnet, F8.3 sonnet | README.md, docs/configuration.md, docs/setup.md, docs/how-it-works.md, docs/dashboard-card.md, docs/ecl110.md |
| F9 | Test pins for unpinned guards | F9.1 sonnet, F9.2 sonnet | tests/finite_boundary.py, tests/nightly_ha.py |
| F10 | Gate, stub and ratchet infrastructure | F10.1 opus, F10.2 opus, F10.3 opus, F10.4 opus | tests/hastub/**, tests/ha_contract.py, tests/replay.py, tests/stress.py, tests/stress_budgets.json, tests/env_drift.py, tests/closure.py, tests/derive_closures.sh, tests/deployment_shape.py, tests/doc_claims.py, tests/mutation_table.py, tests/mutation_budgets.json, tests/structure.py, tests/harness.py |
| F11 | Governance tooling and policy | F11.1 sonnet, F11.2 opus, F11.3 opus, F11.4 opus, F11.5 sonnet | .claude/workflows/**, .github/**, CLAUDE.md, AGENTS.md, .claude/rules/**, .cursor/rules/**, .claude/settings.json, tools/audit/**, tools/release/**, docs/decisions/**, tests/README.md |

## Proposed merge queue (priority among PRs that are ready: review `merge`, CI green, `after` edges merged; one merge at a time)

Ordered by dependency depth, then severity, then non-owner-gated first. The orchestrator may swap two adjacent PRs that share no file and no edge; it may not move a PR ahead of its `after`.

1. F2.1 (high, fixture) - get_current_action seams, two-zone comfort floor, PV margin, stale comments
2. F3.1 (high) - Stored instants: naive and future timestamps
3. F4.1 (high) - Input freshness and plausibility; flow-lift clamp
4. F7.1 (high) - Climate entity: hvac_action during boost, mode reads, away target
5. F5.1 (medium) - Translated text, icons and names (no config_flow.py)
6. F6.1 (medium) - Card layout, colour and hit targets (P9)
7. F8.1 (medium) - configuration.md: initial setup, entity count, services
8. F11.1 (medium) - Governance parsers and enumerators (not code-owned)
9. F10.1 (low, fixture) - Home Assistant stub fidelity (P11) and its contracts
10. F1.1 (high) - DST wall-clock seams and the gate's clock
11. F2.2 (medium) - Interpreter-bound recomputation in the solve
12. F3.2 (medium) - Pump-duty arbiter and the frequency map
13. F4.2 (medium) - System identification: adoption gate and fit integrator (P5 and its barrier)
14. F9.1 (medium) - Pins for deletable guards (I1), part 1
15. F11.2 (medium, tvofi) - Required-check boundaries (I3, owner-gated)
16. F8.2 (low) - Labels, pages and solver description
17. F6.1b (barrier) - Card: the estimated-prices label and the slot tap-target spacing (P9 grid instances)
18. F1.2 (high) - Presence inferred from untouched defaults; DHW start state
19. F3.3 (medium) - Learner stores and feed parsers
20. F6.2 (medium) - Keyboard route in the layout editor; stale comments; #1643 surviving mutants
21. F8.3 (medium) - Setup promises, curve-bias figure, currency fallback, card version
22. F9.2 (medium) - Pins for deletable guards (I1), part 2; return inside finally
23. F11.3 (medium, tvofi) - Policy text: per-file caps, CLAUDE.md rule 1, verdict carry on merges-only moves; I3 barrier
24. F1.3 (high, fixture) - Cycle outcome: stale spot price, unfenced cycle calls, failures reported as success
25. F5.2 (medium) - Setup wizard and options UX
26. F7.2 (low) - Sensors: schedule count, duplicate entity, valve recommendation
27. F2.5 (barrier, fixture) - Recomputation the sweep missed: peak_cost_batch's row loop and the terminal-cost closure
28. F6.3 (barrier, tvofi) - P9 class barrier in the browser lane
29. F1.4 (medium) - Restart durability (barriered class) and store bounds
30. F2.3 (medium, fixture) - Plant-model physics and the thrice-held inlet default
31. F10.2 (medium, tvofi) - CPU gate blind spots; per-solve CPU budget
32. F1.5 (medium) - Cycle failures: swallowed errors, late try, reap, P6 defaults, defrost fold
33. F10.3 (medium, tvofi) - Owned gate scripts: verdict pins, mutation inventory, child-process closures; I1 and P11 barriers
34. F1.6 (medium) - Plausibility bounds and the P1 load-layer barrier
35. F2.4 (medium, fixture) - On/off pump threshold at both seams; multi-start seeds
36. F1.7 (medium, fixture) - Coordinator readers across lanes: loop CPU, auth, settlement scale
37. F7.3 (medium, tvofi) - Climate availability without an indoor thermometer (owner's ruling)
38. F1.8 (medium) - Currency and unit (P8) and entry identity
39. F6.4 (medium) - Language-aware setup text; raw-thermometer source for staleness gaps
40. F1.9 (barrier) - Persisted future instants: the outage decision and the coordinator regressions
41. F1.10 (low, fixture) - P3 class barrier: one floor per thermal parameter; comment drift; the fourth on-threshold copy
42. F1.11 (low) - Class barriers P2 and P6; horizon_hours and the boost test hook
43. F10.4 (low, tvofi) - Structural ratchet truth: dead members and uncounted helpers; I5 barrier
44. F11.4 (low, tvofi) - Class roster readers agree (I4 barrier); owed driver fixes
45. F11.5 (barrier, tvofi) - Round-9 RCA policy text (each draft as tvofi approves it)
