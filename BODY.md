<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
Rework onto R1: this PR originally landed three changes of
`dev/audit/rounds/round9/prestudy/closures-scoping-prestudy.md` -- (a2), the
`inert_reads` consultation in `affected()`'s skip rule; (a1), the batch
dispatch arm of `closure-scope`; and (e), a lane rebalance of the full derive.
**R1 (#2131, main `5c02e2bab`) landed a `--scripts-from` lane runner in
`tests/derive_closures.sh` that owns lane layout for the scoped arm and
reworked the same files, so (e) is DROPPED from this PR entirely: it
superseded it, its branch conflicted with R1's structures, and merging two
lane layouts would be neither reviewed tree.** `tests/derive_closures.sh` at
this head resolves byte-identical to `origin/main`'s (the conflict was taken
wholly in R1's favour). What remains is (a2) exactly as round-1 reviewed it
and (a1) re-coupled to R1's runner -- the merge-path pre-study's explicit
condition: "couple (a1) to that runner or scoped proofs pay serial sums".

**(a2)** `tests/closure.py affected()`: the skip rule now consults the
committed `inert_reads` table. A changed file that IS a recorded inert read of
a script, or lives under such an entry's own directory or that directory's
parent, selects that script. Both matches strictly over-select, fail toward
selection; the bound (entry's own directory + its parent, never the root) is
what keeps the docs-only skip alive outside the recorded reach. This
STRENGTHENS rule 1: the #2109 shape (PR #2109 added
`dev/audit/rounds/round9/prestudy/boost_drift_refit.py` under a tree
`tests/harness_headers.py`'s discovery demonstrably rglobs; `affected` said
skip, the fast arm passed in 16 s, and main reddened 54 minutes after the
merge) reddens on the pull request in ~4 minutes (one harness_headers.py
recording, 220.7 s recorded) instead of on main one merge later.

**(a1)** `.github/workflows/tests.yml closure-scope`: the job also answers
`workflow_dispatch` (the merge train's `batch/<tag>-<n>` proof dispatches,
`tools/audit/seat/merge_train.py launch()`), deriving the batch branch's
three-dot diff against `origin/main` and feeding it through the same
`closure.py affected`. FAIL-CLOSED, one mechanism: no origin/main, no merge
base, an unreadable or EMPTY diff, or a failed `affected` all land on an empty
file list, and `affected` answers `full` for exactly that. The nightly-ha
decision stays a pull-request decision on dispatch (pinned). **The coupling to
R1:** a dispatch-derived `scoped` case is consumed by the closures job's
shared "Re-record the closures" step, which R1 wired to ONE
`--scripts-from` lane run (`closure.py lane-plan` shards it, bounded to three
lanes on a CI runner) instead of a serial `--single` loop -- so a scoped
batch pays the lane MAX, never the serial SUM. A new entities.py pin holds
that coupling: the step must carry `--scripts-from`, no per-script `--single`
invocation, and no event gate of its own.

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
unreached file (`dev/governance/rules/9999.md`) instead; the arm's intent (a
diff that reaches no selectable script records nothing) is unchanged and
still asserted.

Acceptance for (a1) is CI's own run, stated honestly: this seat cannot
trigger a batch dispatch. It is the next `batch/<tag>` dispatch's `closures`
run, scoped by its own diff through the R1 lane runner; the orchestrator
observes it. (e)'s wall acceptance moved to R1's PR with the change itself.

## Head

`4bbfd009a67c4c83b131d6c20d3d3f1c6d63debd` (`origin/main` tip
`5c02e2babd6ace27cdab9c0eba557431417d1076`, which is also the merge base;
`date -u` 2026-10-11T12:23:31Z): one commit -- the a1 x R1 coupling pin --
atop the merge commit that took R1 into this branch (`83ff5d158`, which also
dropped (e) by resolving `tests/derive_closures.sh` wholly to R1's tree and
combined the prepr.sh self-test arms) atop the previously reviewed head
`156fe40a1` (the harness-construction repair) and the authored code head
`1ec5ce967`. Measured with the seat venv interpreter
(`tools/audit/seat/seat_venv.sh`, Python 3.14.7) on macOS; a Darwin box
cannot take the Linux-only figures, and none of the numbers below claim it
did. This re-take re-executed the contract's post-merge steps: all three
(a2) mutants re-killed, the (a1) arms re-driven, the bound probes
re-measured, entities/structure/policy re-run at this tree.

## Mutation proof

(a2), three mutants at the head, each a production-line deletion or bound
mutation in `tests/closure.py`, restored with `git checkout -- tests/closure.py`
after each:

- **A -- the consultation loop deleted from `affected()`**: the #2109 probe
  and the LICENSE probe both answer
  `CASE: SKIP -- no recorded closure contains any changed file, no script's
  recorded inert_reads reach them, and every one of them is INERT` (not
  vacuous: the skip reason itself names the rule the mutant removed);
  restored, LICENSE answers `CASE: SCOPED -- 2 closure(s) intersect the diff`.
- **B -- the bound narrowed to own-dir only** (the parent level,
  `allowed.add(dirs[-2])`, removed): the round20 new-tree probe
  `dev/audit/rounds/round20/new_probe.py` answers `SKIP` -- the exact
  hole the `_A_IR_NEWDIR` entities pin catches -- while the #2109 probe
  stays `SCOPED` via its own directory, distinguishing B from A.
- **C -- unbounded ancestors** (every proper ancestor of a recorded entry
  allowed): `dev/governance/roles/fixer.md` answers `SCOPED` for
  entities+harness_headers -- the over-trigger the pre-study refused and the
  `_A_IR_BOUND` entities pin catches; restored, the probe skips again.

(a1): the decide step's dispatch branch deleted in a mutant commit
(`5d154638331e`, the round-1 proof; the branch text is unchanged at this
head), harness re-run: with the branch gone no `case=` output is derived at
all, so the `closures` job's `SCOPE_CASE` is empty and every dispatch takes
the FULL arm -- the base behaviour, which is the point. The new a1 x R1
coupling pin's own kill arm, run through the same extraction rule the pin
uses: against the PRE-R1 serial-loop step (workflow at `a74520020`) the pin
FAILS, at this head and at `origin/main` it PASSES.

## Null control

- The unmodified tree at `origin/main` (`5c02e2bab`): both (a2) arms answered
  `skip` before this branch's change (the defect), and
  `affected(["SECURITY.md"])` / `affected(["NOTICE"])` answer `skip` at base
  AND at head -- the rule's two null controls, also pinned in
  `tests/entities.py`.
- `custom_components/heatpump_optimizer/const.py` answers `SCOPED -- 30
  closure(s)` at head -- identical to base, no over-trigger toward full.
- the a1 harness's BASE arm (at `origin/main`) shows `closure-scope runs on
  workflow_dispatch: False` -- before the fix, every dispatch paid the full
  arm whatever its diff.
- an empty `--files-from` list makes `affected` answer `CASE: FULL -- no
  changed files could be determined` (re-verified at the head), which is the
  rule every fail-closed path in the decide shell lands on.

## Figures

Every figure's command, run at `4bbfd009a` unless stated; the seat venv
interpreter first on PATH. None of the commands re-derives closures.

- (a2) arms at HEAD (re-taken after the merge onto R1; the merged
  `tests/closures.json` carries R1's new `inert_reads` entries, and the
  probes hold unchanged):

```
python tests/closure.py affected --files dev/audit/rounds/round9/prestudy/nonesuch_probe.py --workdir <tmp>
  CASE: SCOPED -- 1 closure(s) intersect the diff
      REDERIVE  tests/harness_headers.py  <- dev/audit/rounds/round9/prestudy/nonesuch_probe.py
python tests/closure.py affected --files LICENSE --workdir <tmp>
  CASE: SCOPED -- 2 closure(s) intersect the diff
      REDERIVE  tests/entities.py  <- LICENSE
      REDERIVE  tests/harness_headers.py  <- LICENSE
```

- (a2) bound and null probes at HEAD (both edges of the bound, both null
  controls, and the stated costs; each the same instrument as the arms
  above, `python tests/closure.py affected --files <path> --workdir <tmp>`):
  a whole new round tree, probed as
  `affected(["dev/audit/rounds/round20/new_probe.py"])`, answers SCOPED for
  harness_headers (new tree inside the discovery breadth); probes on
  `dev/governance/roles/fixer.md` and `handoff/r9-x/note.md` answer SKIP
  (outside every recorded reach); `SECURITY.md` answers SKIP (inert, no
  recorded read reaches it) and `NOTICE` answers SKIP (a root-level entry
  drags in nothing); `docs/new_page.md` answers SCOPED for doc_claims
  (8.6 s; the stated cost) and `dev/programme/plan-x.md` answers SCOPED for
  harness_headers (the register entry's parent; the stated cost); and
  `custom_components/heatpump_optimizer/const.py` answers SCOPED 30 --
  identical to base, no over-trigger.

- (a2/a1) pins: `PYTHONPATH=tests/hastub python tests/entities.py` -- at HEAD
  `ALL 2262 ENTITY CHECKS PASSED`; the same run at `origin/main` prints
  `ALL 2251 ENTITY CHECKS PASSED` (rule: the runs' own count lines; the
  delta of 11 is this PR's ten a2/a1 wiring pins plus the a1 x R1 coupling
  pin added by this rework). The in-run `FAIL aN:`/`hb:` fixture-output
  lines are the same set every run prints.

- (a1) three arms at HEAD and the BASE arm, from the landed harness
  (`HPO_A1_PYTHON=<seat python> bash tools/audit/seat/a1_dispatch_arms.sh
  HEAD origin/main`, re-taken at `4bbfd009a`):

```
decide step at HEAD:
  inert-only               closure-scope case = skip
  closure-touching         closure-scope case = scoped
  diff-underivable         closure-scope case = full
BASE (origin/main):
  closure-scope runs on workflow_dispatch: False
  -> SCOPE_CASE empty -> the closures job takes the FULL arm, whatever the diff
```

- (e) dropped, verified rather than asserted:
  `git diff origin/main -- tests/derive_closures.sh` at this head is EMPTY --
  the file is R1's, byte for byte; this PR no longer touches it.

- (a1 x R1) coupling: the pin's own null control, extraction rule identical
  to the check's (`_workflow_job(text, "closures")`, split on the step
  separator, `name: Re-record the closures`): pre-R1 `a74520020` FAILS
  (serial `--single "$s"` loop), `origin/main` and HEAD PASS (one
  `--scripts-from`).

- gate scope for this diff (mode line, never the count):
  `python tests/closure.py select --diff $(git merge-base origin/main HEAD)
  --workdir <tmp>` -> `MODE: FULL -- every test script runs, nothing is
  scoped out` -- expected: the gate files `.github/workflows/tests.yml`,
  `tests/closure.py`, `tools/pr/prepr.sh`. Run locally per `run.sh`'s
  run_always set: `env_drift.py --claims-only origin/main` (ok),
  `closure.py selftest` (`ALL 76 closure shrink pins PASSED`; 76 = 57 at the
  last body + R1's new runner pins), `harness_headers.py` (`ALL 109 ... PASSED`),
  `layout.py` (self-test ok), plus `entities.py`, `structure.py`
  (`STRUCTURE RATCHET PASSED`) and `arch_score.py --smoke` (`ALL 257 ... PASSED`).
  The rest of the FULL gate is CI's.

- `python3 -I tests/throwaway_git.py --check` at the head:
  `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow
  entries at HEAD` -- the round-2 red stays answered by `156fe40a1`, which
  this head contains.

- pre-study figures carried forward unchanged (their provenance is the
  pre-study's §8, cited, not re-measured here): job 114258919874 timings,
  `boost_drift_replay.py` 29 m 26 s / 55%, the #2109 16-second skip and
  54-minute-late main red, batch job 114247906174 54 m 45 s, R1's 51m18s
  serial SUM vs 27m57s lane MAX on #2071's closures job.

## Red checks

none at the head. The two round-2 reds are answered by commits this head
contains, not re-opened: `instrument-self-tests` by `156fe40a1` (both raw
git sites routed through `tests/throwaway_git.sh`; the check prints 0
refused above) and `pr-contract` by this section and the round-3 body naming
them. The merge onto R1 (`83ff5d158`) resolved textual conflicts in
`tests/derive_closures.sh`, `tools/pr/prepr.sh` and `tests/entities.py`; the
resolution is R1's structures plus this PR's (a2)/(a1), and every locally
runnable check above is green at `4bbfd009a`. The FULL gate this diff forces
runs in CI. No `*_budgets.json` is touched (`python3 tests/structure.py`:
`STRUCTURE RATCHET PASSED`).

## Unpinned sites

- `closure.py inert_read_owners()`: pinned by the six entities.py checks
  (both arms, both bound edges, both null controls) plus the `affected` CLI
  probes above; all three mutants kill against those pins.
- the a1 decide-step shell: pinned textually by the entities.py wiring checks
  (if-block, fail-closed derivation, nightly-ha boundary, DOCS_ONLY_FAST,
  and the new a1 x R1 coupling pin) and driven for real by the landed
  harness's three arms plus its BASE arm; the mutation proof removes the
  dispatch branch and the arms collapse to `<none derived>`.
- `tools/audit/seat/a1_dispatch_arms.sh`: pinned by
  `tests/throwaway_git.py --check` (0 raw git sites) and by the arms
  themselves, which CI re-runs through the `instrument-self-tests` job.

## Forward-carry

- `tools/audit/seat/a1_dispatch_arms.sh` lands in this PR (fixer contract
  step 18): any seat can re-run the a1 arms at any pair of refs.
- Owed, the owner's not mine (tvofi's 2026-10-10 direction recorded in the
  programme): `dev/governance/rules/gate-scoping.md` may want to state the
  four-heavy-slot lease budget explicitly; the rule text is policy and this
  PR does not touch it.
- Owed observation for the orchestrator, CI-side: the (a1) acceptance -- the
  next batch dispatch's `closures` job scoped by its own diff through the R1
  lane runner. Recorded here as the acceptance test; it cannot be triggered
  from this seat.

## Friction

none
