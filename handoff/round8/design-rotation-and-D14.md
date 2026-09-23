# Design: rotating seat focus, the D14 bug-class dimension, and the convergence programme

Status: draft for implementation by the local fixing orchestrator, 2026-09-23. Requested by Tim in the round-8 audit thread.
Tim's inputs:
- a rotation design and a bug-class dimension ("draft a design for the rotation … an additional dimension, focusing on finding and eliminating the most common bug classes");
- moves 1, 2, 4 and 5 of the convergence strategy as plan input; move 3 (feature freeze) is NOT adopted;
- round-8 shape: 1 verifier per dimension, 1 common judge.

Policy status: sections A, B and D change code-owned files (`tools/audit/briefs/**`, `CLAUDE.md`'s brief table, `.claude/workflows/check-wave-script.mjs`), so they are policy. Tim's temporary mandate lets a thread approve them as tvofi/CODEOWNER until **2026-09-24T13:55Z**. After that the owner's own review is needed.

Evidence base: `/mnt/project-files/audit-r8/bugclasses/classes.md` and `findings.tsv`. These classify the 285 surviving findings of rounds 1-7 into 15 mechanism classes (enumerator: the classifier's own table; one row per finding). The class ids P1-P10 and I1-I5 below are that file's.

---

## A. Rotating seat focus

### Problem
A fresh seat handed a whole dimension brief drifts to the same entry points each round. Round 8 split each brief's numbered method steps across seats by hand. Its reports then named steps that ran shallow or not at all: D2-s1's capacity-envelope check, D1-s1's slow-Store race, D3's quiet-window re-take. Nothing carries those gaps into the next round's dispatch.

### Design
1. **Step ids.** Every `tools/audit/briefs/D<k>.md` already numbers its method steps (`1. **Thermal model.**` …). The id is `D<k>.M<n>`. Briefs that use headings rather than numbers (D6, D12, D13) are numbered once, with no wording change.
2. **A coverage ledger** at `tools/audit/rotation.json`, one entry per dimension:
   ```json
   {"D2": {"steps": ["M1","M2","M3","M4","M5"],
           "rounds": {"8": {"seats": [["M1","M2"],["M3","M4","M5"]],
                            "coverage": {"M1":"deep","M2":"deep","M3":"deep","M4":"spot","M5":"spot"},
                            "unfinished": ["capacity envelope (M2)"],
                            "yield": {"M1":0,"M2":1,"M3":1,"M4":1,"M5":0}}}}}
   ```
   `coverage` and `unfinished` come from each finder's JSON. `yield` is the judge-surviving findings per step.
3. **Finder output grows two fields** (the `reportSchema` in `audit-find.js`, plus `finding.schema.json` if its report shape carries them):
   - `coverage: [{step, depth: deep|spot|none, evidence}]`;
   - `unfinished: [{step, what}]`.
   A finding also names `step`.
4. **Dispatch rule** in `audit-find.js`. It is deterministic, so a relaunch replays; there is no `Math.random`. For each dimension with S seats:
   - Priority for each step is: rounds since last `deep`, then +2 if named in last round's `unfinished`, then +1 if last round's yield there was ≥1. The last term exists because a class that just yielded usually has siblings, and D14 will also chase it.
   - Assign the S highest-priority steps as each seat's deep focus, round-robin. Every other step becomes a spot check for the seat with the lightest load.
   - A step `deep` in each of the last two rounds with zero yield drops to spot for one round.
5. **Seat counts per round.** This is the round-8 recommendation, with Tim's move 4 applied:

   | seats | dims |
   |---|---|
   | 2 | D0, D1, D2, D7, D9, D12 |
   | 1 | D3, D4, D8, D10, D14 |
   | 1, alternate rounds | D5, D6 |
   | 1, every third round | D11, D13 |

   That is 17-19 finder seats per round. Keep the `SEATS` table in the workflow and derive the per-round set from the round number.
6. **Refusal.** Extend `check-wave-script.mjs`, which already derives DIMS/WAVES/ISOLATED from the briefs directory, to also refuse:
   - a `rotation.json` missing a dimension or a step the brief numbers;
   - a step the ledger names that the brief no longer has.

### Panel and judge shape (Tim, round 8)
`audit-verify.js` today dispatches 3 verifiers per panel and kills by majority refute. Change it to **1 verifier per dimension** (carrying both halves of `verifier.md`: its own harness plus the attack on the finder's) and **one common judge** over every finding. With one vote, nothing is killed at panel: every finding goes to the judge, and `judge.md` already re-measures every one. `verifier.md` states the panel size, so it changes by one sentence. That is policy, under the mandate.

---

## B. D14 — recurring bug classes (new dimension)

### Why
Classifying rounds 1-7:
- **7 of the 10 production classes recur in 6 or 7 of 7 rounds.**
- Several have explicit "fixed, then a sibling found next round" chains:
  - P2: #192's freeze-gate asymmetry R1→R2→R5; #1398 → R7 D8-02;
  - P5: the adoption gate narrower than the phenomenon four times, R1→R7;
  - P10: four generations of the GIL starvation;
  - P1: four different stores;
  - P3: #1487 filed right after #1450 merged.

A dimension that re-finds instances cannot end these chains. A barrier that enumerates every seam, and runs forever, can.

### Brief (`tools/audit/briefs/D14.md`, owner's words to be supplied by Tim; draft wording)
> *"Recurring bug classes. Take the classes the programme keeps re-finding, build the detector that enumerates every seam of each, and propose the barrier that makes the class impossible."*

Method:
1. **Class ledger.** `tools/audit/bugclasses.json` is seeded from `classes.md`: id, mechanism, rounds present, instance ids, `detector` (command), `barrier` (the CI check, once landed), `status: open|detector|barriered`.
2. **Pick.** Take the top 2-3 `open` production classes by recurrence, then by severity.
3. **Detector.** A harness under `tools/audit/round<N>/D14/` that enumerates every seam of the class across the package, not only the known instances. It must pass three checks:
   - it re-finds every historical instance listed for the class (a positive control; it runs against the pre-fix commits named in the ledger where possible);
   - it finds zero on a hand-written clean fixture (a null control);
   - it moves under a one-line re-introduction (the perturbation).
4. **Finding shape.** Exactly one finding per class: the property, the enumeration rule (the detector command), the seams it lists, and a proposed barrier. That is `COMMON.md`'s "group by phenomenon" rule taken literally.
5. **Barrier proposal.** Where the detector should live permanently (a `tests/` script, a lint class, a runtime assertion) and its cost in gate seconds.

Starting classes, with the detector idea from `classes.md`:

| class | mechanism | detector → barrier |
|---|---|---|
| P2 | one fact decided twice / guard at one seam, missing at its sibling | AST: callers of each named gate predicate vs structurally sibling functions → a `structure.py`-style check that siblings share the gate |
| P6 | consumer reads a key no producer writes (e.g. R7 D8-01) | static cross-reference of `coordinator.data[...]` / `.get(...)` reads vs `_build_data_dict` writes → a `tests/` check with 0 orphan reads |
| P1 | non-finite or malformed value crosses a persisted-store boundary | enumerate every `Store`/`async_load` → one validated load layer; a fuzz property test per store (D1's round-8 ledger mutants are the seed) |
| P8 + unit half of P3 | currency/unit/scale resolved by divergent precedence (R8 D2-s2-02 öre/MWh) | enumerate every price/unit source → a unit-carrying price type and one resolution function; a lint refuses raw floats at those seams |
| P9 | card clipping, tokens, hit targets | the existing browser geometry sweep → a permanent gate assertion (`card_browser.mjs`) |
| P10 | GIL-holding solve starves the loop | the real-loop heartbeat harness → a perf check keyed on a ratio, not wall time |
| P4, P5 | seeds/tolerance don't bracket; sysid gate keyed on the wrong quantity | promote the race-grid and synthetic-bias sweeps to property tests |
| I1 | a mutation kill counted on exit status | require at least one failing assertion for a kill (already R7 D3-02 / #1453) |

`ISOLATED` gets D14, because it mutates production to prove each detector. Add it to `audit-find.js`, `prepare_baseline.sh` and the CLAUDE.md dimension table. The `check-wave-script.mjs` derivation will refuse a partial add.

**Relation to `root-cause.md`.** D14 is the audit-side producer of class barriers. The root-cause seat still owns why a process let a class reach a release. When D14 opens a class whose instance count is 3 or more, it cites the root-cause record if one exists and does not duplicate it.

**Stop rule** (replaces "0 findings"): the round's D14 finds no `open` class with a new instance, and the nightly replay (C) shows no new invariant break, for two consecutive rounds, AND 0 high/critical production findings. Rationale: rounds 6-7-8 sit flat at about 15-20 production findings, so a zero-findings stop never triggers.

---

## C. Real-day replay (move 2)

- **Why.** #1499 (Heat Pump Action always "off") was found by Tim in use, not by seven audit rounds. Synthetic matrices miss what a real install feeds the integration.
- **What.** A nightly lane, `tests/replay.py`, that feeds a recorded day through the real coordinator (`_honest_coordinator` shape), step by step:
  - price series, weather forecasts, every mapped sensor's state history, pump and valve states;
  - invariants on every published entity value and attribute: finite, unit matches `device_class`, no constructor default published as available, state/attribute agreement (the #1499 shape: action "off" while power > 0), no value unchanged across a changed input.
- **Data.** Tim exports N days from his Home Assistant recorder (the SQLite `states` table, or the History API) through a script `tools/replay/export.py` run on his install. It is sanitised by the same rules `tests/entities.py` a10 enforces: no tokens, coordinates at 2 dp or fewer. Fixtures are committed under `tests/replay/` only after sanitising. Start with 7 days, one per season as they accrue.
- **Gate.** Nightly (like `nightly_ha.py`), not per-PR, until its runtime is measured. A new invariant break opens a replay finding that goes to D14 as a new class if no class matches.

---

## D. Process diet (move 4)

- **Moratorium on new process.** Until a date Tim sets, no new policy file, lint class or `.claude/rules/*` rule. The exceptions are those a D14 barrier or a critical/high D11 finding requires. `policy_budgets.json` caps may go down, not up.
- **D11 and D13 every third round** (see the A.5 table). Their findings in rounds 6-7: 5 of 31 and 9 of 30.
- **One enforcement point.** Where a D14 barrier replaces a prose rule, the prose rule is deleted in the same PR. The detector is the rule.
- **Keep:** the identity model (decision 0011), the fix-review verdict, the scoped gate and the golden claims. These guard the product and cost little per merge.

---

## E. Fix by class (move 5)

- The fix plan groups every open audit issue by class id (from `bugclasses.json`), not by dimension.
- **One PR per class** carries:
  - the D14 barrier, or the detector promoted to `tests/`;
  - every instance the detector enumerates;
  - a regression test per instance where the barrier alone does not pin it.
- `fixer.md` step 8's enumeration rule already requires the seams. This makes the detector the enumerator.
- Instances in a class with no detector yet are fixed singly, and the class is queued for D14.
- **Ordering:**
  1. Classes with a live high/critical instance.
  2. Classes with a detector that exists as an audit harness today: P9, P10, P4, P5 and I1, which are promotions rather than new builds.
  3. The rest.

---

## F. Implementation order for the fixing orchestrator

Each item is one PR, authored by hpo-author via `app_push.sh`. Code-owned PRs need tvofi's approving review, available under the mandate until 2026-09-24T13:55Z.

1. **Round-driver repairs met in round 8** (instrument; not code-owned except where noted):
   - `tools/audit/prepare_baseline.sh` strips `tools/audit/round4/`, but `tests/entities.py` opens `round4/D11/governance_cost.py` (and via it `d11lib.py`) and `round4/D6/claims.json` unguarded. The script's own `finders_can_start` refusal therefore refuses its own output. Measured: the finders_can_start grep over the stripped export lists exactly those two paths as missing. Fix: keep those files, or move the instruments tests read out of `round4/`.
   - Stripping earlier rounds makes 8 further `entities.py` checks fail in a finder tree (measured: 9 of 1732 fail in a stripped git worktree vs 1 in the unstripped checkout). The instruments that read `tools/audit/round*/` need the same treatment.
   - Seat-scoped finding ids (`D1-s1-01`) fail `finding.schema.json`'s id pattern. Widen the pattern for multi-seat rounds.
2. **`audit-verify.js`:** 1 verifier per dimension, one common judge (A, panel paragraph); `verifier.md` one sentence (policy).
3. **Rotation:** step ids in the briefs, `rotation.json` seeded from round 8's seat focuses and reports, dispatch rule in `audit-find.js`, check in `check-wave-script.mjs` (policy for the brief numbering and the check).
4. **D14:** brief, `bugclasses.json` seeded from `classes.md`, ISOLATED/DIMS/WAVES, the CLAUDE.md table row (policy).
5. **Replay lane:** export script, sanitiser, `tests/replay.py`, nightly wiring. It needs Tim's first export.
6. **Process-diet record:** a decision record under `docs/decisions/` stating the moratorium, the D11/D13 cadence and the stop rule (policy).

Items 2-4 can share one PR if the gate's scope allows. Item 1 is independent and should go first, because round 9 depends on it.
