# Design note: R11-OUTSIDE-CI-3885-REST (#3885 items 2 and 3, after P1)

- Base: `origin/main` 98541868add741cd1967a82614d3b3b81b9178ef. No predecessor handoff: P1 merged as #3896. The table
  read here is `tests/case_closures.json` at that base, recorded at f184477ba8.
- Builds on the approved `design/R11-CI-CASE-SELECT` 25fa1f76 (verdict b7e7f57f) and `design/r11-ci-3885-queue`
  43ff5ae6 (verdict adbd80a4). Its selection rule (i)-(v), fail-safes and P3 stand, except where this note says otherwise.
- The earlier sampler, `tests/case_sample.py` at 9df0838b1d, was taken off main by d09793a86d. Its shape is reused
  below only where it is named.
- **No finder harness: owner report.** The evidence is the owner's two 11-25 items as the brief quotes them
  (#3394 comment 7157667401; this seat did not re-read the comment). The measurements below are the harness.

## 1. What the table says (this changes the brief's premise)

Every figure was taken over the base table with the table's own `needs` and `seconds`. A 30% draw keys
sha256(seed, NUL, span id) over 20 seeds sha1(k), and the median is reported. "back*" is the backward closure over
`needs`. The enumerator is `python3 tests/case_select.py stats <script>`, which P2b extends with these arms
(Notes, item stats-arms).

| script | spans (table / head) | 30% picked, s share | picked + back*, s share | one production file in diff: D ∪ fwd ∪ back*, s share |
|---|---|---|---|---|
| tests/entities.py | 65 / 65 | 0.14 | 0.96 | median 1.00 (121 of 121 files reach 2 or more spans) |
| tests/features.py | 248 / 252 | 0.36 | 0.93 | median 1.00, p10 0.00 (13 of 121 files reach no span) |

**Null control.** With `needs` dropped, picked + back* equals picked (0.14 and 0.36). The closure is what costs, not
the draw. On today's table, neither item saves more than 4-7% of either script's seconds. There are two causes, and
each is measured.

- **C1: one omnibus span.** In entities.py, `#558 D6 numeric schedule companion` (tests/entities.py:28946) runs to
  the next top-level `R.section` at :42466. That is 13.5k lines, 1094 of the table's 1388 s, and a read set of 560
  files (121 under `custom_components/`, 234 under `tools/`). Any diff meets it through rule (i), so it always runs.
- **C2: over-wide `needs`.** features.py holds 10241 table edges. `static_needs` gives 3046 of them, and the rest
  come from `dynamic_needs` module moves. The top static edge names are throwaway rebinds, read only after the span
  binds them itself: `i` 592, `d` 144, `_key` 55. Other top names are imports (`np`, `const`, `_asyncio`) and
  `@logging` 171. **A ceiling, unsound by construction and used only to bound the gain:** take free reads only, with
  import names and `@logging` dropped. Picked + back* then falls to 0.70 for features and stays at 0.92 for
  entities, because C1 holds it there.

## 2. Owning seam

`tests/case_select.py` owns every decision about which spans run: the split, the needs, the draw, the plan and the
`CASES:` line. Its callers do only this:
- `tests/run.sh` (lane units) passes a plan for the two scripts.
- `.github/workflows/tests.yml` exports the seed.
- `tests/closure.py` keeps case_select as a gate file (its FULL trigger).
- `tests/entities.py` pins the event/scope table.

`tests/seam_map.json` maps package seams only, and no concern needs two owners.

## 3. Shape

**Plan.** A new `plan` subcommand of `tests/case_select.py`. It takes a script, the merge base, the diff list, the
seed and the fraction, and returns either a plan file (span ids, each with the rule that chose it) or FULL with a
reason. `run <script> --plan FILE` is unchanged. The fraction is one module constant, 0.3. It engages only when
`HPO_CI_EVENT` is `pull_request` **and** `GATE_SCOPE` is `auto`. Every other pair returns FULL: a push to main,
full or light, schedule, workflow_dispatch, merge_group, and local. The approved fail-safe list also applies.

**Interaction (decided: union, as 25fa1f76 has it).**
`run = back*(ii ∪ i ∪ fwd(i ∪ ii) ∪ pick(rest))`, where `rest` is every span the diff cannot reach.
- A span the diff reaches, or an edited or new span, always runs, whatever the seed.
- The draw thins only what the diff cannot reach.
- Sampling alone (P2c, before rule i exists) is the same formula with (i) empty: `back*(ii ∪ pick(all − ii))`.

**Seed (chosen so a red reproduces).**
- The seed is the PR head SHA, `github.event.pull_request.head.sha`, which tests.yml already resolves into
  `CLAIM_HEAD` for its claim step (.github/workflows/tests.yml:335); P2c passes it to the units job. It is never `github.sha`. On `pull_request`, `github.sha` is the refs/pull/N/merge test merge, which
  moves every time main moves, so a re-run attempt would draw another set. It is never the run id or the attempt.
- The draw keys on the span **id**, never on the ordinal as 9df0838b's `keep()` did. With the ordinal, one inserted
  span reshuffles every later draw.
- Each script prints one line: `CASES: SCOPED <script> -- k of n spans (seed <40-hex>, fraction 0.3, base <sha>,
  d diff, s sample, b needed)`. The plan file goes into the job's artifact.
- The same head, base and table give the same plan on any machine, and a re-run attempt repeats it. Locally, the
  `plan` subcommand with the printed seed and base re-derives the plan, and `run --plan` replays it.
- A sampled red at a head whose FULL run (dispatch, or the main push) is green means the plan dropped a producer.
  That is a missing-`needs` defect in the recorder, never a flake.

**Null control: an unsampled run selects every case.** In FULL mode the runner counts the spans it executed against
`case_select.split`, and prints `CASES: FULL <script> -- n of n spans (<reason>)`. A count below n is a red, so no
path can skip a span silently.

```
PR (pull_request, auto): run.sh -> closure.select -> case_select plan(script, base, diff, CLAIM_HEAD, 0.3) -> run --plan
main push (full|light), schedule, dispatch, merge_group, local: run.sh -> case_select run (no plan) -> n of n
```

## 4. Alternatives, and why they lost

- **Sample over the diff-reached spans too** (item 2 read alone). This drops a span that reads the changed file
  with p = 0.7, so a production PR's verdict depends on the head SHA: a regression can pass at one head and fail at
  the next. Union keeps that verdict independent of the seed.
- **A separate sampling module** (the approved note's case_sample, or 9df0838b's in-script `engage()` hook). It
  makes two modules decide which spans run. The hook also sits in each script's header, so it is a header edit that
  forces FULL under the header-hash arm, and it re-enters the runner (the `_INNER` guard).
- **Ship sampling before C1/C2.** It buys 4-7% of seconds (§1), plus one more line to read in every log.

## 5. Parts, in order (each its own PR; harness and fix shape named)

| part | fix shape | harness, failing first | null / mutation |
|---|---|---|---|
| **P2a** C1 split | Insert top-level `R.section` titles at the omnibus span's existing case boundaries in tests/entities.py, with no check moved. Re-record entities with `derive_closures.sh --cases --single tests/entities.py` on Linux. | `stats`: the heaviest span's share of seconds drops from 0.79. Runner equivalence (approved evidence 2): the `ok`/`FAIL` lines match `python3 tests/entities.py` in order, ignoring section headings. | null: features.py is untouched and its stats lines are byte-identical; mutant: a check moved across a new boundary shows as an equivalence diff |
| **P2b** C2 needs | Reads become free reads: a name the span definitely binds before it reads it adds no edge. An import of an already-imported module binds nothing. `@logging` stays a binder only for setters (handlers, level), not for log calls. Dynamic module moves key on (module, attribute), and the reader needs them only when its static or started-code references name that attribute. | `stats` back* arms reach the ceiling's order (§1). The synthetic case_select self-test rows fail first: a loop target `i` gives no edge, and a re-import gives no edge. | null rows: a genuine read of A's `x` keeps A; a moved attribute the reader names keeps the edge. **Soundness replay** (approved evidence 5, at least 200 seeded mutation-ledger pins, fraction 0, both nulls) runs here, because tightening is where unsoundness enters. |
| **P2c** item 2 | The `plan` subcommand with rules (ii), (iv), (v), fail-safes, seed, `CASES:` lines and the n-of-n count. run.sh calls it, and tests.yml exports `CLAIM_HEAD` as the seed to the units job. | An entities.py pin drives run.sh's own function per (event, scope), as d09793a86d's lane_stress pin does: only (pull_request, auto) plans. Draw rows: the same seed draws the same ids; one inserted span moves no other draw. | mutants: plan engages on push; ordinal key; seed taken from `github.sha`; a FULL run that skips one span with the count check removed. Each must fail. |
| **P2d** item 3 | Rules (i) and (iii) join the plan. | Approved evidence 4, plus the measurement table rows (#3875, #3887, #3596) re-measured against a same-runner FULL. | approved mutation targets for (i) and (iii); soundness replay re-run |
| **P3** | As approved: `closures-autofix` and `CASE UNDER-SCOPED`. | — | — |

**Stop rule.** If P2a and P2b together leave picked + back* above 0.85 for both scripts, the fixer reports the figures
and P2c does not ship. A 30% knob that saves under 15% is a log line paid for on every PR. This goes to the
orchestrator as a decision.

## 6. Sibling sites, hot files, serial position

- **Sibling sites.** Scripts with top-level sections: `for f in tests/*.py; do grep -cE '^R\.section' $f; done`. Those
  with sections beyond the two are dst_checks, optimality, rolling and wood_advisor. All are under the approved
  300 s floor by `tests/closures.json` `recorded`, so they are out of scope. `case_select.py` itself counts only as
  self-test fixtures.
- **Hot files.** These go serially, in the order P2a → P2b → P2c → P2d → P3:
  - tests/entities.py: P2a, P2c's pin.
  - tests/case_select.py: P2b, P2c, P2d.
  - tests/case_closures.json: P2a and P2b re-record.
  - tests/run.sh and .github/workflows/tests.yml: P2c only.
- **tests.yml.** Before P2c starts, the fixer checks `git log origin/main -- .github/workflows/tests.yml` and the open
  PRs for a tests.yml edit in flight.

## Notes for the fixer

- Carry: R11-OUTSIDE-CI-3885-REST (item stats-arms) -- add `stats` arms that print the picked and picked+back*
  seconds shares over a printed seed list, and the per-production-file D∪fwd∪back* share, so §1's figures have an
  enumerator in the tree. Derive every figure at your merge base; never carry §1's numbers.
- Carry: R11-OUTSIDE-CI-3885-REST (item stale-table) -- the base table lags features.py by 4 spans (248 against
  252). Rule (ii) runs them, but P2a's Linux re-record must cover both scripts, or features' stats compare against a
  stale entry.
- Carry: R11-OUTSIDE-CI-3885-REST (item dispatch-full) -- a STALE-PIN `workflow_dispatch` at a PR head runs FULL by
  design, so it is the reproduction check of §3. Do not let it take the pull_request plan path.
- Carry: R11-OUTSIDE-CI-3885-REST (item policy-tests-yml) -- P2c's tests.yml line and P3's `ci-autofix.md`
  sentence follow the approved note: owner approval before merging.
