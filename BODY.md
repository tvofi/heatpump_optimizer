The required `closures` check's re-record step is 98.9% of the push-to-main
job (53 m 35 s of 54 m 10 s, job 114258919874), lane 3 serialises 53 minutes
while lanes 1-2 idle after 15 and 21, the batch dispatch pays the full arm for
a diff whose entries were each already scope-checked, and the #2109 class --
a diff INERT by prefix but readable by a discovery glob a recording reaches --
took the 16-second skip lane and reddened only main, 54 minutes after the
merge. This lands (e), (a2) and (a1) of
`dev/audit/rounds/round9/prestudy/closures-scoping-prestudy.md` (at handoff
`177bb01c`): three independent changes, each with its own failing-first arm
and mutation proof. Rule 1 is untouched by all three: same recordings, same
checks, and detection moves EARLIER (a2: onto the pull request) or stays
identical (e: scheduling only; a1: the push-to-main and nightly full arms are
exactly as they were).

**(e)** `tests/derive_closures.sh`: `boost_drift_replay.py` (1489.6 s
recorded; 29 m 26 s on job 114258919874, 55% of that job's wall) gets a lane
of its own; the rest of the old lane 3 keeps its order as a fourth lane. LANE
LAYOUT ONLY: the recording set is byte-identical (34 `rec` lines, proven
below), the `plan_view.py` -> card order is preserved inside the one lane, and
that a script's lane changes WHEN it is recorded, never WHAT it opens, is the
in-tree R9-F10.15 result the lane-2 comment cites. No lock, queue or
serialisation is introduced: four unconstrained background shells, which is
exactly tvofi's 2026-10-10 direction that this box's lease budget is four
concurrent heavy scripts (stress.py's exclusive lease is untouched; nothing
here takes any lease).

**(a2)** `tests/closure.py affected()`: the skip rule now consults the
committed `inert_reads` table. A changed file that IS a recorded inert read of
a script, or lives under such an entry's own directory or that directory's
parent, selects that script. Both matches strictly over-select, fail toward
selection; the bound (entry's own directory + its parent, never the root) is
what keeps the docs-only skip alive outside the recorded reach. This
STRENGTHENS rule 1: the #2109 shape reddens on the pull request in ~4 minutes
(one harness_headers.py recording, 220.7 s) instead of on main one merge
later.

**(a1)** `.github/workflows/tests.yml closure-scope`: the job also answers
`workflow_dispatch` (the merge train's `batch/<tag>-<n>` proof dispatches,
`tools/audit/seat/merge_train.py launch()`), deriving the batch branch's
three-dot diff against `origin/main` and feeding it through the same
`closure.py affected`. FAIL-CLOSED, one mechanism: no origin/main, no merge
base, an unreadable or EMPTY diff, or a failed `affected` all land on an empty
file list, and `affected` answers `full` for exactly that. The choice is
job-side, not dispatcher-passed: a dispatcher-computed scope handed in as a
workflow input would narrow a required check on a bug the workflow cannot
see -- the same parroting the docs-only fast arm exists to refuse. The
nightly-ha decision stays a pull-request decision on dispatch (pinned).

Over-selection cost of (a2), stated: after this, a diff touching
`dev/audit/**` or `dev/programme/**` selects `tests/harness_headers.py`
(220.7 s recorded), `tools/**` selects `tests/entities.py` (259.6 s),
`docs/**` selects `tests/doc_claims.py` (8.6 s); `dev/governance/`,
`handoff/` and root-level INERT files still skip (pinned). Unbounded ancestor
matching was tried first and refused by measurement: the single
`round6/D11/fix/` entry shares `dev/` with all of `dev/programme/` and
`dev/governance/`, and every prose pull request in this repository lives
there -- the docs-only skip pin caught it.

Two instrument files ride along: `tools/audit/seat/a1_dispatch_arms.sh`
(the a1 arms' harness, under Forward-carry) and a `tools/pr/prepr.sh`
self-test fixture fix -- its "skip" arm diffed `docs/delivery/9999.md`,
which (a2) now correctly derives scoped, so the fixture branches a genuinely
unreached file instead; the arm's intent (a diff that reaches no selectable
script records nothing) is unchanged and still asserted.

Acceptance for (e) and (a1) is CI's own run, stated honestly: a full
`derive_closures.sh` is forbidden off Linux (`dev/governance/rules/
gate-scoping.md`), and this seat cannot trigger a batch dispatch. The wall
acceptance for (e) is the next push-to-main `closures` job green with all 33
recordings and re-record wall <= 35 min on at least two runs; for (a1) it is
the next `batch/<tag>` dispatch's `closures` run, scoped by its own diff. The
orchestrator observes both.

## Head

`1ec5ce9675aa712968b0d562c61340a573dcfcae` (merge base `origin/main` =
`6be88834e8`, the #2125 merge). Measured 2026-10-10 with the seat venv
interpreter (`tools/audit/seat/seat_venv.sh`, Python 3.14.7) on macOS; a
Darwin box cannot take the Linux-only figures, and none of the numbers below
claim it did.

## Mutation proof

(a2): the consultation loop deleted from `affected()` at the head, both arms
re-run, restored (`git checkout -- tests/closure.py`):

```
=== arm A (#2109 shape) under mutation:
  CASE: SKIP -- no recorded closure contains any changed file, no script's
=== arm B (LICENSE) under mutation:
  CASE: SKIP -- no recorded closure contains any changed file, no script's
restored
  CASE: SCOPED -- 2 closure(s) intersect the diff      <- arm B, back at head
```

(a1): the decide step's dispatch branch deleted in a mutant commit
(`5d154638331e`), harness re-run, branch reset to the WIP head. With the
branch gone no `case=` output is derived at all, so the `closures` job's
`SCOPE_CASE` is empty and every dispatch takes the FULL arm -- the base
behaviour, which is the point: the mutation removes exactly the production
lines that carry the fix.

```
decide step at HEAD (5d154638331e9afadbe957a1a163cad58476f5fd):
  inert-only               closure-scope case = <none derived>
  closure-touching         closure-scope case = <none derived>
  diff-underivable         closure-scope case = <none derived>
```

(e): the rebalance's mutation is the layout itself; locally that is the
structural proof, not a wall clock. Restore the old single lane-3 and the
critical path returns from 1489.6 s to 2728.8 s recorded (figure below); the
wall-clock acceptance is CI's, as stated above. Predicate, not tail: the
change IS the predicate, and the recording-set identity below is the control
that nothing else moved.

## Null control

The unmodified tree at the merge base `6be88834e8`:

- both (a2) arms answer `skip` (the defect, pasted under Figures);
- `affected(["SECURITY.md"])` and `affected(["NOTICE"])` answer `skip` at
  base AND at head -- the rule's two null controls, also pinned in
  `tests/entities.py`;
- this PR's new entities.py pins run against the BASE closure.py: 7 of 2260
  fail (the 7 are exactly the new a2/a1 pins; the run's other 46 FAIL lines
  are the fixture-output lines every run prints, byte-identical to the base
  run's set). At the head all 2260 pass;
- the a1 harness's BASE arm shows `closure-scope runs on workflow_dispatch:
  False` -- before the fix, every dispatch paid the full arm whatever its
  diff.

## Figures

Every figure's command, run at `1ec5ce96` unless stated; the seat venv
interpreter first on PATH. None of the commands re-derives closures.

- (a2) failing-first arm, BASE `6be88834e8` (the defect; both arms green
  there today):

```
python tests/closure.py affected --files dev/audit/rounds/round9/prestudy/nonesuch_probe.py --workdir <tmp>
  CASE: SKIP -- no recorded closure contains any changed file, and every one of them is INERT
python tests/closure.py affected --files LICENSE --workdir <tmp>
  CASE: SKIP -- no recorded closure contains any changed file, and every one of them is INERT
```

- (a2) same arms at HEAD (the file need not exist: `affected` decides from
  the table; `dev/audit/rounds/round9/prestudy/` holds a recorded entry, so
  the rule the table states is what fires):

```
python tests/closure.py affected --files dev/audit/rounds/round9/prestudy/nonesuch_probe.py --workdir <tmp>
  CASE: SCOPED -- 1 closure(s) intersect the diff
      REDERIVE  tests/harness_headers.py  <- dev/audit/rounds/round9/prestudy/nonesuch_probe.py
python tests/closure.py affected --files LICENSE --workdir <tmp>
  CASE: SCOPED -- 2 closure(s) intersect the diff
      REDERIVE  tests/entities.py  <- LICENSE
      REDERIVE  tests/harness_headers.py  <- LICENSE
```

- (a2) input-range edges (learner-range rule; both ends pinned in
  entities.py): a whole new round tree, probed as
  `affected(["dev/audit/rounds/round20/new_probe.py"])`, answers SCOPED for
  harness_headers (via `dev/audit/`, one level above the
  `dev/audit/harnesses/` entries' directory); probes on
  `dev/governance/roles/fixer.md` and `handoff/r9-x/note.md` answer SKIP
  (outside every recorded reach); a probe on `docs/new_page.md` answers
  SCOPED for doc_claims (8.6 s); a probe on `dev/programme/plan-x.md`
  answers SCOPED for harness_headers (the register entry's parent -- the
  stated cost, not a bug).

- (a2/a1) pins: `PYTHONPATH=tests/hastub python tests/entities.py` -- at HEAD
  `ALL 2260 ENTITY CHECKS PASSED`; against BASE closure.py `7 of 2260 ENTITY
  CHECKS FAILED` (the seven new pins, named under Null control); base without
  the pins `ALL 2250 PASSED`. The 46 `FAIL aN:...` lines inside every run are
  fixture outputs, set-identical base vs head (`diff` of the sorted FAIL
  lines: empty).

- (a1) three arms, HEAD and BASE, from the landed harness
  (`HPO_A1_PYTHON=<seat python> bash tools/audit/seat/a1_dispatch_arms.sh
  HEAD 6be88834e8c4658b3e4832cd24c00aa97b3da2d3`):

```
decide step at HEAD:
  inert-only               closure-scope case = skip
  closure-touching         closure-scope case = scoped
  diff-underivable         closure-scope case = full
BASE (6be88834e8):
  closure-scope runs on workflow_dispatch: False
  -> SCOPE_CASE empty -> the closures job takes the FULL arm, whatever the diff
```

  The harness extracts the decide step's `run:` verbatim from the workflow at
  each ref (PyYAML) and substitutes GitHub's `${{ }}` expressions as the
  runner does for a dispatch, so the arms drive the production shell, not a
  re-implementation of it. Rule for the empty-diff arm: an empty
  `--files-from` list makes `affected` answer
  `CASE: FULL -- no changed files could be determined` (verified directly:
  `: > <tmp>/empty.txt; python tests/closure.py affected --files-from
  <tmp>/empty.txt --workdir <tmp>`).

- (e) recording-set identity, old vs new (rule: the `rec tests/...` targets,
  sorted; identical means same recordings, scheduling only):

```
git show origin/main:tests/derive_closures.sh | grep -oE "rec tests/[A-Za-z_.]+( --smoke| --only __no_such_scenario__| --cache-key \"?\$GOLDEN_REF\"? --all)?" | sort
grep -oE "rec tests/[A-Za-z_.]+( --smoke| --only __no_such_scenario__| --cache-key \"?\$GOLDEN_REF\"? --all)?" tests/derive_closures.sh | sort
```

  -> `diff` empty; 34 rec lines both sides.

- (e) lane arithmetic (rule: sum of `recorded[*].seconds` in
  `tests/closures.json` at `6be88834e8`, per lane's member list; the table's
  own disclosure: golden/env_drift seconds time the cheap stub invocation):

```
lane1 stress        760.6 s     lane3 boost      1489.6 s
lane2 feat+ent      990.1 s     lane4 shard      1239.2 s
OLD lane3 (serial) 2728.8 s -> new critical path 1489.6 s
```

- (e) wall prediction, MARKED AS A PREDICTION because only CI measures it:
  ~29-33 min for the push-to-main `closures` job. Reasoning: the floor is the
  boost lane (1489.6 s recorded; 29 m 26 s wall measured inside the OLD
  three-lane contention, job 114258919874); every other lane now finishes at
  or under 1239.2 s recorded, and lanes 1-2 free their cores at 12-16 min.
  The one unmeasured term is 4-lane contention on the runner's cores -- the
  pre-study's own open item, converted to a measurement by the acceptance
  run. The faster same-shape run (run 38059574126, 30 m 22 s with lane 3 at
  53 min of work) says the floor sits near the boost lane's wall.

- gate scope for this diff (mode line, never the count):
  `python tests/closure.py select --diff $(git merge-base origin/main HEAD)
  --workdir <tmp>` -> `MODE: FULL -- reason: .github/workflows/tests.yml
  changes the gate itself` -- expected: three gate files. Run locally per
  `run.sh`'s run_always set: `env_drift.py --claims-only` (ok at
  `6be88834e8`), `closure.py selftest` (`ALL 57 closure shrink pins
  PASSED`), `harness_headers.py` (`ALL 109 ... PASSED`), `layout.py`
  (self-test ok), plus `entities.py`, `structure.py`
  (`STRUCTURE RATCHET PASSED`) and `arch_score.py --smoke` (`ALL 257 ... PASSED`).
  The rest of the FULL gate is CI's.

- pre-study figures carried forward unchanged (their provenance is the
  pre-study's §8, cited, not re-measured here): job 114258919874 timings,
  `boost_drift_replay.py` 29 m 26 s / 55%, lane idle times, ~8 full arms on
  2026-10-10, batch job 114247906174 54 m 45 s.

## Red checks

none at the head. Every locally runnable check named above is green at
`1ec5ce96`; the FULL gate this diff forces (three gate files:
`closure.py`, `derive_closures.sh`, `tests.yml`) runs in CI, and the
closures job itself is the acceptance instrument for (e)/(a1) as stated. No
`*_budgets.json` is touched (`python tests/structure.py` green at head).

## Unpinned sites

- `closure.py inert_read_owners()`: pinned by the six new entities.py checks
  (both arms, both bound edges, both null controls) plus the two `affected`
  CLI arms; the mutation proof kills the consultation.
- the a1 decide-step shell: pinned textually by the four new entities.py
  wiring checks (if-block, fail-closed derivation, nightly-ha boundary,
  DOCS_ONLY_FAST) and driven for real by the landed harness's three arms plus
  its BASE arm; the mutation proof removes the dispatch branch and the arms
  collapse to `<none derived>`.
- the lane layout: the recording-set identity and the lane arithmetic are the
  local pins; the wall acceptance is the next two main-push `closures` runs.
  The tree's own guard is the unchanged `check` the job runs after the lanes
  ("NO recording this run" for anything the lanes dropped) -- no new pin is
  needed for a pure re-grouping of the same 34 recordings.

## Forward-carry

- `tools/audit/seat/a1_dispatch_arms.sh` lands in this PR (fixer contract
  step 18): any seat can re-run the a1 arms at any pair of refs.
- Owed, the owner's not mine (tvofi's 2026-10-10 direction recorded in the
  programme): `dev/governance/rules/gate-scoping.md` may want to state the
  four-heavy-slot lease budget explicitly; the rule text is policy and this
  PR does not touch it. All three changes here preserve that concurrency by
  construction (no lock anywhere in the diff).
- Owed observations for the orchestrator, CI-side: the (e) wall acceptance
  (two green main-push `closures` runs <= 35 min) and the (a1) acceptance
  (the next batch dispatch's `closures` job scoped by its own diff). Both are
  recorded here as the acceptance tests; neither can be triggered from this
  seat.

## Friction

none
