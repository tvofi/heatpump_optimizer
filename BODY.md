Countermeasure for `RCA-1565-mutation-timeouts`, established by a root-cause seat:
the nightly mutation lanes bound each driver's first run below the pool factor the
lanes themselves measure. Six consecutive scheduled runs concluded `failure` from
2026-10-03 to 2026-10-08 (last green `36984959667`, 2026-10-02T08:36:04Z) on **five**
distinct causes -- counted by **mechanism** (the lane plus the rule that failed), not by
proximate fault, which is why `record-autofix`'s three nights are one cause here while
§2b of the doc records three different faults inside it (a credential, a request body, a
git exit). **This bound arm is the cause on two of the six** (10-07, 10-08).
10-03 and 10-04 reddened on its sibling -- the `EXCLUSIVE`-under-`--scope-full`
null-control arm, which is the owner's (item iv below) and is **not** fixed here --
and 10-05/10-06/10-07 on `record-autofix`. Per-night attribution, each from that
run's own failing-job list and job log, is the table in
`dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md` §1.

The bound was `max(--timeout floor 1200 s, TIMEOUT_SCALE 3 x the driver's *solo-gate*
recording)` while the lane drives the same script in a 3-worker pool whose cost the RCA
doc measures at **0.47x-3.27x** that recording (§2's enumerator: 51 driver rows over three
nightly job logs, excluding the `env_drift.py` stub and any solo recording under the log's
1-second resolution). `closure.SECONDS_BAND = 2.0` deliberately keeps a committed value up
to 2x below the cost CI last measured, so the worst-case headroom over the script's *true*
solo cost was `3 / 2 = 1.5x`, and the bound trips whenever a driver's pool factor exceeds
`3 x (committed / true)` -- `boost_drift_replay.py`'s was `>= 3.00` on both nights it died.
A factor below 1 (the range's low end) is no hazard; it is a recording that was stale
*high*. `closure.py`'s own `0.3x-3.4x` is a different quantity -- how much one script's
*recordings* vary run to run, which is why the band exists -- and is not the pool factor.

Derived from the committed table
with the tree's own `driver_timeout`, `tests/boost_drift_replay.py`'s bound was 1576 s on
10-07 (CI printed `timed out after 1576s`; the sibling lane completed the same script at
1573 s -- three seconds of margin) and 2401 s on 10-08 (CI printed `timed out after
2401s`). On 10-03/04/05 it had no recording and fell to the bare 1200 s floor: those
nights printed **no** timeout for this driver, so the exposure there is an *inference*
(the floor is below the 1573 s this script measured in the pool on 10-07), not a row CI
printed -- the doc's table marks those three cells inferred. When the bound did trip,
`baseline_refusal` voided every mutant verdict and printed "Fix the suite first" while the
same head's committed entry said `{"seconds": 800.2, "rc": 0}` -- the suite was green and
the lane was judging its own bound.

This lands RCA §5 items 1-3 and the record. It does **not** re-tune `SECONDS_BAND`
(tvofi set it 2026-10-08 for merge-text hygiene -- a different concern; `git diff
b2b6acd64...HEAD -- tests/closure.py` is 0 lines); it decouples the *bound* from the
*band*. The fourth arm -- honouring `EXCLUSIVE` under `--scope full`, the null-control
"kills" of 10-03/10-04 -- is an unpinned-count raise (`budget-raise-gate`, decision 0013)
and is routed to the owner, not built here. Note the streak has since ended on its own:
the 10-09 scheduled run `37909555545` concluded `success`, on the strength of a
re-recorded 1489.6 s (bound 4469) rather than of any mechanism -- which is why the fix is
still owed.

## Head

`c54beab894db7210c570cd67f7cfb61212ed301c`, one commit on top of the pull request's
round-2 head `96497ffc6` (= round-2 code head `7e8c5c8e4` plus this PR's own row
`dev/programme/delivery/2074.md`), not re-cut from it. Remote refs: this PR's branch
`fix/r9-nightly-bound`, this seat's handoff `handoff/r9-nightly-bound` and the body's
orphan `handoff-body/r9-nightly-bound`. Merge base against `origin/main` is still
`b2b6acd64`; **`origin/main` has moved past that base and this branch has not merged
it** -- that merge is the orchestrator's, so every three-dot figure below is against
`b2b6acd64` and none is a function of main's moving tip (which is therefore deliberately
not quoted here: `git rev-parse origin/main` answers it at read time, and a quoted tip
would be stale the moment it landed). The CI-evidence figures cite runs at the heads
named in each line.

Round 3, answering the review that measured `96497ffc6` (`record-stale`). **No executable
line moved**, and that is checked rather than asserted: with docstrings stripped, the ASTs
of `tests/mutation_table.py` and `tests/entities.py` at this head are **identical** to
`96497ffc6`'s (the only docstring that changed is `seed_pool_seconds`'), and of the
changed lines in `.github/workflows/tests.yml` **zero** are not comments. Round 3 is the
two blocked record defects and the three nits:

- `dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md` §7 -- the demonstration bullet, rewritten in
  round 2 and left on round 1's head ("the five checks", four `2239` tallies), now carries a
  seven-row table: one row per arm (clean, revert, A, B, C, D, E) with what it breaks, the
  check it reddens, the tally at this head and its log. Round 1's `2239` tallies stay,
  labelled as that head's by the doc's own disclosure convention. The C/D/E arms -- the
  proof the two wiring pins bite -- were absent from the landed record and are now in it,
  which is where `defect-root-cause.md` puts a demonstration.
- The four lines this PR adds that still asserted the superseded pool factor: the
  `TIMEOUT_SCALE` comment and `seed_pool_seconds`' docstring in `tests/mutation_table.py`,
  `tests.yml`'s restore-step comment, and `tests/entities.py`'s block comment (which also
  attributed `closure.py`'s `0.3x-3.4x` as a pool factor). All four now quote the measured
  `0.47x-3.27x` with the rule that produces it and cite §2; `entities.py` names `0.3x-3.4x`
  as what `closure.py` actually states -- how much one script's *recordings* vary run to
  run -- and says that conflating the two is how the superseded figure travelled.
- Nits: §1's bound table gains the **10-06** row it skipped (head `cff39dad6`,
  `{seconds: 765.6, rc: 0}` -> bound **2297**, both mutation lanes green, so neither
  evidence for the mechanism nor against it); §2b's header no longer claims every member was
  re-measured and names member 3 as the one that was not; the opening states its
  cause-grouping rule (a mechanism, not a proximate fault) so "five distinct causes" and
  §2b's "three different faults rather than one cause" are the same count.

Because round 3 changed only text, every mechanism figure the review re-derived at
`96497ffc6` -- bounds 1200/1576/2401/4469, seeded 4719/7200/7203, `SECONDS_BAND` unmoved,
the refusal-path drive, seed-never-lowers, fail-soft, round-trip,
carrier-fires-on-refusal-night -- stands unchanged. All seven arms were nevertheless
**re-taken at this head** rather than inherited, and their tallies are below.

`prepr.sh`'s `policy corpus` advisory fired and was answered rather than waved through:
`origin/main` moved six policy files past this branch's base, four of them contracts
(`dev/governance/roles/fixer.md`, `dev/governance/roles/fix-review.md`,
`.claude/rules/{ci-autofix,claim-files}.md`). `fixer.md`'s diff was read, and it changes
this seat's obligation: step 5 now says to run what `scope.run` **and `tests/run.sh`'s
`run_always` lines** name. `scope.run` is empty at `MODE: FULL`, so the four `run_always`
scripts are what a local run owes, and all four were run at this head -- results in
`## Figures`. The other three diffs were read for obligations on this PR and carry none:
`ci-autofix.md` and `claim-files.md` both add the new `merge-main.yml` bot as the one pusher
of a driver-file conflict resolution (`ci: merge main`, tvofi 2026-10-08) -- this branch has
no such conflict (`git merge-tree --write-tree` against the base exits clean) and touches no
claim file, so there is nothing for it to resolve here; `fix-review.md`'s change is to the
reviewer's step 7 (`--carry` heads), not the fixer's.

## Mutation proof

The seven checks are in `tests/entities.py`, named `RCA-1565 …`, driven as functions and
by reading the two wired artifacts (never a nightly run).
`PYTHONPATH=tests/hastub python tests/entities.py`.

**Failing arm -- the whole fix removed** (the merge-base `tests/mutation_table.py` restored
over the fix, my `entities.py` checks in place): the defect checks and the driver-wiring pin
go red, the two null controls and the YAML-wiring pin stay green (the YAML is still wired
when only the driver is reverted):

```
FAIL RCA-1565: the baseline bound covers the MEASURED pool cost with the scale's margin, not TIMEOUT_SCALE x a band-stale solo recording
ok   RCA-1565 null control: a healthy driver's bound still covers its pool cost, the seed never lowers a bound, and env_drift stays floor-bound (not scaled)
FAIL RCA-1565: the pool measurement round-trips through pool_seconds.json, and an absent/unreadable/malformed file seeds nothing (fail-soft, never a smaller bound)
FAIL RCA-1565: a baseline that TIMED OUT against a green committed recording names the stale recording and the bound, not 'fix the suite first'
ok   RCA-1565 null control: a real red baseline (a failing check, not a timeout) still says 'fix the suite first' and names the check
FAIL RCA-1565 wired in the driver: main() takes --pool-seconds, seeds the bound with it, records each pool baseline, and persists from the finally
ok   RCA-1565 wired in the workflow: both nightly lanes pass --pool-seconds, and mutation-ledger persists on an if: always() cache save in the measuring job, never in the success-gated push job
```

That arm's tally at this head: **`4 of 2241 ENTITY CHECKS FAILED`, exit 1** -- the three
defect checks plus the driver-wiring pin, with both null controls and the workflow-wiring
pin green.

**Passing arm -- the fix in place**: `ALL 2241 ENTITY CHECKS PASSED`, exit 0 (all seven green).

**Surgical mutations** (each isolates one production predicate or one wiring line; the check
that keys on it goes red and the others stay green -- so no check is vacuous, and no wiring
line is deletable). Each measured with `PYTHONPATH=tests/hastub python tests/entities.py`,
then restored with `git checkout HEAD -- <file>` and confirmed `tree == HEAD`:

| mutation | what is broken | red check(s) | count |
|---|---|---|---|
| A | `seed_pool_seconds`'s fold neutered (`out[s] = max(...)` -> `pass`) | the *bound covers pool* check (bound falls back to `3 x solo = 2401`, below the `3 x 2401 = 7203` it needs) | 1 of 2241 |
| B | `baseline_refusal`'s timeout arm neutered (`timeouts = []`) | the *timeout wording* check (verdict reverts to "Fix the suite first", omits "STALE") | 1 of 2241 |
| C | `--pool-seconds` deleted from **both** nightly lanes in `tests.yml` | the *wired in the workflow* pin | 1 of 2241 |
| D | the seed call site reverted to `own_s = recorded_seconds()` | the *wired in the driver* pin | 1 of 2241 |
| E | `if: always()` removed from the `actions/cache/save` step | the *wired in the workflow* pin (pinned as the adjacency, so a SHA bump does not break it) | 1 of 2241 |

C, D and E answer the review's reported-not-blocking item: before them, deleting
`--pool-seconds` from `tests.yml` or reverting the seed call site left every check green and
the nightly back on `TIMEOUT_SCALE x` a solo recording -- this PR's own defect, restorable
without tripping a check. They are written in the file's existing idiom (`_MUT_BODY` at its
"defined-but-never-called is the silent-green shape" comment, `_MUT_BW_MISSING` for the
YAML), and D is exactly the revert the review named.

**All seven arms were re-taken this round**, not inherited from round 2. Six of them ran at
`90ef590d8`; this head differs from that one **only in the RCA document's prose** --
`git diff 90ef590d8..HEAD --name-only` prints the RCA document alone -- and no check reads that
document's contents (`tests/entities.py` names the path only in comments, `tests/layout.py`'s
`GUARD_EXEMPT` exempts `dev/audit/rca/` by path prefix, `fold_ledger.py` stats
`in_tree_home` without opening it). The clean arm was nevertheless re-run at this exact
head, so one arm is measured at the SHA named above. Logs are in the seat scratch
`/Users/timmalmstrom/hpo-seats/fix-nightly-bound/logs/`, one per arm:
`entities_R3_HEAD_FINAL.txt` (clean at this head: `ALL 2241 ENTITY CHECKS PASSED`, exit 0;
the same arm at `90ef590d8` and `51ed9aee7` is `entities_R3_HEAD.txt` /
`entities_R3_HEAD_COMMITTED.txt`, same tally both times),
`entities_R3_REVERT.txt` (revert: `4 of 2241 ENTITY CHECKS FAILED`),
`entities_R3_MUTA.txt`, `entities_R3_MUTB.txt`, `entities_R3_MUTC.txt`,
`entities_R3_MUTD.txt`, `entities_R3_MUTE.txt` (`1 of 2241` each), and the run that drove
all seven with its per-arm red-check listing is `arms_r3_out.txt`. Every restore was
confirmed against `HEAD`, and afterwards all three code files were re-checked
`IDENTICAL to HEAD` -- no mutation residue. Round 1 measured five of these checks at
`2239` total, before the two wiring pins existed; the doc's §7 keeps those four tallies
labelled as that head's.

## Null control

The unmodified tree, and what the fix leaves alone:

- **The two null-control checks read flat at both ends** (green on the unfixed tree in the
  failing arm above, green with the fix): a healthy driver's bound already covered its pool
  cost, so the fix does not fire on it, and a real red baseline still says "Fix the suite
  first". Nothing is skipped to reach green.
- **Re-taken at this merge base** (`b2b6acd64`), committed solo seconds via the tree's own
  `recorded_seconds()`, pool costs from CI job `113233890923` (2026-10-08): `features.py`
  solo 730.5 / pool 772, `stress.py` 760.6 / 434, `entities.py` 259.6 / 142,
  `harness_headers.py` 199.0 / 211 -- each bound (floor 1200 or the scale) covers its pool
  cost before and after. `env_drift.py`'s solo recording is the declared 0.9 s stub
  (`closure.py` #934) against a 524 s pool cost: it is protected by the **floor** (1200),
  not the scale, and the fix reads flat on it -- the seeded bound rises to 1572 and still
  covers 524. The seed only ever raises a bound (`max(solo, pool) >= solo`, `driver_timeout`
  monotonic), so no driver's protection shrinks.
- **Fail-soft**: `pool_seconds(None)`, a missing file, and a malformed file each read as
  `{}`, so the bound falls back to the solo recording -- today's behaviour, never a smaller
  bound. A cache miss on the first nightly is therefore safe.

## Figures

- Six consecutive red scheduled runs; last green `36984959667`; the streak ended on
  `37909555545` (10-09, `success`) without this fix:
  `gh api "repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs?event=schedule&per_page=12" --jq '.workflow_runs[] | [.id,.head_sha[0:9],.created_at,.conclusion,.status] | @tsv'`.
- **The per-night arm attribution** (which night was the bound, which the `EXCLUSIVE`
  sibling, which `record-autofix`): `gh api "repos/tvofi/heatpump_optimizer/actions/runs/<run>/jobs?per_page=100" --jq '.jobs[] | select(.conclusion=="failure") | [.id,.name,.conclusion] | @tsv'`
  for runs `37108891698 37189092011 37288195257 37440269774 37595831734`, and without the
  `select` for `37753990323` -- which is also where `closures-autofix -> skipped` (job
  `113252338415`) is read.
- **CI's own refusal text per night**: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs --allow-escape-sequences`,
  ANSI-stripped, for `111162760555` (10-03 `harness_headers.py … rc=-24`), `111397325352`
  (10-04 `stress.py … 8.0x … budget 7.9x`), `111692063912` (`HTTP 401`), `112192034609`
  (`HTTP 422`), `112708108856` (`exit code 128`), `112708109605` / `113233890923`
  (`timed out after 1576s` / `2401s`), `112708109541` (the 1573 s completed run).
- **The pool/solo factor range 0.47-3.27 with its exclusion rule**: 51 driver rows over
  those three logs, factor = pool / the committed solo recording at that run's head
  (`git show <head>:tests/closures.json`), excluding `tests/env_drift.py` (declared stub,
  `closure.py` #934) and any solo recording under the log's 1-second resolution. Each end
  is named with its driver and both inputs in the doc's §2 table.
- **The cron-to-dispatch delay 5 h 54 m - 6 h 53 m over twelve runs**: each run's
  `created_at` from the query above minus the `02:17Z` that `tests.yml:119`'s
  `cron: "17 2 * * *"` declares, printed per run (min `37108891698`, max `37909555545`).
- The reproduced bounds 1200 / 1576 / 2401 / 4469 from the committed table with the tree's
  own function: `python -I -c 'import sys; sys.path.insert(0,"tests"); from mutation_table import driver_timeout; ...'` over `git show <head>:tests/closures.json` for heads `2e569748a fb11a0172 a1da8d381 be0cb8213 816547efe b2b6acd64`.
- Voided lane work 63.4 / 64.2 / 72.4 min: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id> --jq '[.started_at,.completed_at] | @tsv'` for `112708109605`, `112708109541`, `113233890923`.
- Failing arm, the five surgical mutations and the green arm, all
  `PYTHONPATH=tests/hastub python tests/entities.py` at this head: the revert arm, A, B, C,
  D and E logs named in the section above.
- `fold_ledger.py check` clean at both ends (`101 rca entries`, `0 violation(s)`): `python3 -I tools/audit/fold_ledger.py check`.
- Structural ratchet: `PYTHONPATH=tests/hastub python tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `tests/run.sh`'s four `run_always` scripts, which `fixer.md` step 5 (as `origin/main`
  now words it) puts beside `scope.run` -- and `scope.run` is empty at `MODE: FULL`, so
  these are what a local run owes: `PYTHONPATH=tests/hastub python tests/env_drift.py
  --claims-only $(git merge-base origin/main HEAD)` -> `claims hygiene: b2b6acd64… ok`;
  `python tests/closure.py selftest` -> `ALL 57 closure shrink pins PASSED`;
  `python tests/layout.py` -> `layout self-test: ok`; `python tests/harness_headers.py`
  -> `ALL 109 HARNESS HEADER CHECKS PASSED`. All four rc 0 at this head, in
  `run_always_R3.txt`.
- Scoped-gate selection: `python tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: FULL -- ... .github/workflows/tests.yml changes the gate itself`; `scope.run` names nothing to run locally, so the remainder is CI's.

## Red checks

- **`nightly-status` / `delivery-status` -- the non-exempt arm, answered.** This diff
  touches `.github/workflows/tests.yml`, which is what `nightly-status` reads, so
  `defect-root-cause.md`'s exemption for the main-grading reporters does **not** apply and
  the body owes them an answer whether or not they are red. **At the round-1 head they were
  both `success`** (the review's step-11 read: `nightly-status` `113815002358`,
  `delivery-status` green), because the 10-09 scheduled run `37909555545` concluded
  `success` and ended the six-night streak -- so no red had to be answered there. The
  answer is stated anyway, for the next time main strands a red: such a red is *main's*
  stranded nightly conclusion, not a regression this diff introduces -- a scheduled run's
  conclusion attaches to whatever commit was `main`'s head when the cron fired, and this
  branch is not that head. Cheaper detector: `nightly_status.py` **is** the detector (it
  grades `main` and fails closed); there is no cheaper one, and the remedy is the
  orchestrator's on `main` -- fix the lane (this PR) and dispatch Tests on the default
  branch once it merges. Standing cost: none added here.
- No check this diff turned red on its own head is expected: `entities.py` is green at this
  head (**all 2241**, the two new wiring pins included), `structure.py` passes,
  `fold_ledger.py check` is clean at both ends, the `mutation` lane's scope is empty (no
  production file is touched), and the four floor-override jobs and every
  `mutation-ledger`/`mutation-nightly` command pin in `entities.py` are unchanged -- the
  carrier is `actions/cache`, which needs no `permissions:` block, so the override count
  stays at four and no argument under that pin's "a fifth override should have to be argued
  for" is owed. Verified: `--scope full --drain "$out" --max 40`, `--seed`,
  `--budget-minutes 270` all present; no `secrets.` or `contents: write` added to the
  measuring job (decision 0011's invariant, now itself pinned).
- **Hygiene, and one base-moved subtlety.** No `*_budgets.json` is in this diff at all, and
  `VERSION`, `RELEASE_NOTES.md`, `hacs.json` and
  `custom_components/heatpump_optimizer/manifest.json` are untouched -- so no budget was
  raised and no version moved. Neither claim file is touched by this branch: both are
  byte-identical to the **merge base** `b2b6acd64`
  (`git diff --name-only b2b6acd64...HEAD -- tests/golden/` is empty). A diff against
  `origin/main`'s *tip* does show `tests/golden/claimed_drift.txt` differing, and that is
  **main's own content, not this branch's** -- R9-UX-9 added 13 lines to it after this
  branch's base (`git log b2b6acd64..origin/main -- tests/golden/claimed_drift.txt` names
  the commits; the tip is not quoted here because it moves). Because this side is unchanged,
  the orchestrator's main merge takes main's version cleanly; no `claimnotes` conflict and
  no `DIRTY` state arises from this branch. `prepr.sh`'s own `claim files` step compares
  against the merge base and reports `byte-identical`.

## Forward-carry

`none` owed to a later stage's brief; every finding this seat made that outlives the PR is
in the tree, at a named destination the reviewer can open:

- **The class search** -- where else this shape reaches -- is
  `dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md` **§2b**, six members, each re-measured at
  this head (`root-cause.md` §3/§6, `defect-root-cause.md`'s "Where it is recorded"). It
  carries `closures-autofix` being `pull_request`-only, so a `closures` red on a schedule
  run has no bot repair lane (measured: job `113252338415` `closures-autofix` -> `skipped`
  on the 10-08 schedule run while `closures` failed beside it); `record-autofix`; the
  bound's reach into the pull-request gate; `mutation-ledger-push`'s success gate; the two
  lanes that never call `driver_timeout`; and the reporter's costly remedy.
- **A correction to the record, not a carry.** The diagnosing seat's §3.2 reported that
  `record-autofix` "has **no `if:`**". It has one, at both the head that seat measured
  (`83f7ca558`) and this one: `!cancelled() && github.ref == 'refs/heads/main' && (push ||
  schedule || workflow_dispatch)`. The class member survives -- a lane that opens a pull
  request on events that have none, reddening three nights on `HTTP 401` / `HTTP 422` /
  `exit code 128`, each read off its own job log -- but the named defect does not exist, so
  §2b records the narrower true finding and says the seat's version was stale. Nothing in
  the tree carries it: `record-autofix`'s live rows (#1957/#1962/#1974) are about its
  identity and lookup. Left to the orchestrator per the dispatch's out-of-scope list.
- **The (iv) arm** -- honouring `EXCLUSIVE` under `--scope full`, an unpinned-count raise
  -- is the owner's (`budget-raise-gate`, decision 0013), already routed to tvofi per the
  dispatch, and recorded as refused-and-routed in the doc's §4 and §5 and in the
  `bugclasses.json` countermeasure with its price (211 s + 430 s, x2 lanes, ~21 min/night).

## Friction

defect-root-cause.md: contradiction: the dispatch scoped item 3's carrier as "an `if: always()` step" on `mutation-ledger-push`, but that job writes through the `hpo-ledger` App whose write-set decision 0011 pins to "new files under `tests/mutation_ledger/killed_by/` and nothing else" (enforced by `drain_write_set_problems` / `drain_push_problems` and an `entities.py` pin), so persisting `pool_seconds.json` to `main` through it would widen a policy grant a fixer does not own. Took the RCA's named alternative ("or the lane's artifact"): `actions/cache`, already pinned in this workflow for the drift baseline, which needs no write grant, no secret (so the measuring job keeps decision 0011's invariant) and adds no job to the four that override the read-only floor; the `if: always()` write rides `mutation-ledger` itself, which runs on the schedule whatever the drive concluded.
