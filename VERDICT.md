Fix review: blocked 96497ffc694302b814eecaeea2710bfdbebf6678 record-stale: RCA §7's arm bullet, rewritten this round, still quotes round 1's five-check/2239 tallies (this head answers seven/2241) and omits the C/D/E arms it added, and four lines this PR adds still state the 1.3-3.3x pool factor that §2 of the same document measures at 0.47-3.27

Round 2.
`record-stale` is outside `web-fix-wave.js`'s `VERDICT_CLASSES`, so the parser routes it
as `other` with the word kept at the front of the why (#1475's documented degradation);
no taught word names "the landed record contradicts the measurement this PR corrected",
and inventing one silently is worse than naming it here.
seat: review-2074b
bus-nonce: f4a2f01860c4a11d6dce10da0f6af16a
Measured at `96497ffc694302b814eecaeea2710bfdbebf6678` in a detached worktree at
`/Users/timmalmstrom/hpo-seats/review-2074b/wt`; merge base `b2b6acd64` = live
`origin/main` (confirmed by `git ls-remote`, unmoved since round 1, so three-dot and
two-dot coincide). Contract read at this head:
`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is
empty. Python 3.14.7 (`$HOME/.local/state/hpo/venv-ci/bin/python3`).
Evidence: /Users/timmalmstrom/hpo-seats/review-2074b/evidence

## The mechanism is untouched, and I confirmed that rather than accepting it

- `git diff 7e8c5c8e4 96497ffc6 -- tests/mutation_table.py .github/workflows/tests.yml`
  is **empty**; `git diff --name-only 7e8c5c8e4 96497ffc6` is
  `dev/programme/delivery/2074.md` **only**; the RCA doc `+333/−68` and
  `tests/entities.py` `+64` (one hunk, `@@ -31725,6 +31725,70 @@`) are the whole round-2
  delta. The head is round-2 content plus this PR's row — nothing reviewed moved.
- Because the mechanism files are byte-identical, round 1's mechanism verdicts are not
  re-argued here; the two numbers I was told I could rely on I re-derived anyway, at
  seconds scale: **bounds 1200 / 1576 / 2401 / 4469** with the tree's own
  `driver_timeout` over `git show <head>:tests/closures.json` (seven heads,
  `evidence/bounds_rederive_mine.txt`), and **seeded 4719 / 7200 / 7203**
  (solo 800.2 with pool 1573 / 2400 / 2401). `SECONDS_BAND = 2.0`,
  `TIMEOUT_SCALE = 3`, `git diff b2b6acd64 HEAD -- tests/closure.py` = 0 lines.
- The one CI number I did **not** re-take: the `mutation` lane's *empty scope* (green at
  this head, suite `102813714594` — see step 11). It is empty because the diff writes no
  source line; that is round 1's read of the lane log (`113815002602` at its head), and it
  survives because the mechanism files this head holds are the byte-identical ones round 1
  read. **I relied on round 1 there.**

## Round 1's four items, each checked with my own instrument

**1. The class search: landed, and its claims resolve.** The grep round 1 ran
(`grep -n -i "record-autofix\|closures-autofix\|class" dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md`)
now exits 0: §2b, "Class search: where else this shape reaches", six members. Every
checkable claim in it I verified myself:
- `closures-autofix` **is** pull_request-only: its `if:` at this head is
  `!cancelled() && github.event_name == 'pull_request' && needs.closures.result ==
  'failure' && …head.repo.full_name == github.repository`, and on the 10-08 schedule run
  `37753990323` job `113252338415` `closures-autofix` concluded **`skipped`** while
  `113233890832` `closures` concluded **`failure`** — both from my own jobs fetch
  (`evidence/my_1008_closures.txt`). `dev/governance/rules/ci-autofix.md`'s summary table
  really does name `closures-autofix` as the repair for `UNDER-SCOPED, INERT READS` (its
  "Same-repo PRs" line scopes all three repair jobs to PRs), so the member is the shape it
  claims.
- The two hand-edit repairs exist and are what the doc says: `b416093e9` "fix:
  inert_reads entry for git_auto_maintenance_race.sh (main closures red after #2051)" and
  `387128bb3` "closures: list the new harness among harness_headers.py's inert reads" —
  ancestors of main, both 2026-10-08, and each touches `tests/closures.json` and nothing
  else ("two hand edits to the committed table" ✓).
- **The correction to the diagnosing seat is TRUE, and it also corrects round 1.**
  `record-autofix` has an `if:`, character-for-character what §2b quotes, at this head,
  at the diagnosing seat's `83f7ca558` and at round 1's `d7c830c2f`. Round 1's own verdict
  text repeated the stale "missing job-level `if:`" claim; the class member the fixer kept
  is the narrower one, and its three faults are real — from logs I fetched myself:
  10-05 `returned HTTP 401`, 10-06 `returned HTTP 422`, 10-07 `Process completed with
  exit code 128` plus `the record step did not run; a beat owed cannot be distinguished
  from one skipped`. The three live rows' titles (#1957/#1962/#1974) being about other
  properties I did not re-read; the body's out-of-scope routing of the lane itself is the
  orchestrator's.
- Members 3/5/6: `driver_timeout(1200, 0.0) = 1200` and all three call sites
  (`3457`/`3470`/`3552`) take the same seeded basis in every scope ✓ (member 3's reach
  claim); `slow` = `timeout-minutes: 150`, `nightly-ha` = 45, neither job's YAML mentions
  `driver_timeout` or `mutation_table` ✓; `governance.yml` contains zero `actions/runs`
  and zero `workflow_runs` ✓; `tests/nightly_status.py` `OWED_WHEN_RED` at line 206 (the
  owed text names `gh workflow run tests.yml` at 209) and line 547
  `run.get("head_branch") != default_branch` ✓; the `_gh_if` §7 cites exists at
  `entities.py:30485` ✓.

**2. The count is corrected, and the correction is what CI shows.** I read the failing
jobs of all six runs myself: 10-03 `mutation-ledger`; 10-04 `mutation-ledger`; 10-05
`record-autofix`; 10-06 `record-autofix`; 10-07 `record-autofix` + `mutation-ledger` +
`mutation-nightly`; 10-08 `nightly-ha` ×2 + `closures` + `mutation-nightly`. In the logs I
fetched, 10-03 prints `MUTATION TABLE REFUSED -- the null control … NULL_COMMENT was
killed by tests/harness_headers.py` and **no** bound timeout, while 10-07 prints
`timed out after 1576s` and 10-08 `timed out after 2401s` — the bound arm is **two**
nights. §1's table now marks the three floor nights "*Inferred* exposure" and the two
tripping nights "**printed**", and that marking matches the logs. §4's split — 0.33/night
(2/6) for the arm this PR fixes, 0.67/night (4/6) for the family including the `EXCLUSIVE`
sibling — is the arithmetic of that table, and the cost test clears on the arm alone
(200 min of voided lane work over the two nights against 0 s standing cost).

**3. Both enumerators reproduce their figures.** The factor range: I fetched the three
job logs myself (`112708109605`, `112708109541`, `113233890923`) and applied §2's stated
rule (factor = pool / the committed solo recording at *that run's* head, excluding the
`env_drift.py` stub and any solo < 1 s). **Kept 16 + 16 + 19 = 51 rows**; min **0.4653**
(`harness_headers.py` 449.2 → 209) and max **3.2692** (`structure.py` 5.2 → 17) — exactly
the doc's ends, drivers and inputs; the two `rc=124` boost rows land at 3.0002 / 3.0005,
which is the doc's "censored, ≥ 3.00"; 10-08's min `block_duty.py` 1.6 → 1 = 0.625.
`evidence/factor_range_mine.txt`. The delay: over the twelve schedule runs I fetched,
`created_at` − `02:17Z` (`tests.yml:119` = `- cron: "17 2 * * *"`, line checked) gives
**5 h 54 m** (`37108891698`, 08:11:57Z) to **6 h 53 m** (`37909555545`, 09:10:23Z) — the
doc's two ends, both re-taken.

**4. The wiring is pinned, and each pin bites.** `tests/entities.py` at this head answers
**2241** (round 1: 2239): my own whole-file run prints `ALL 2241 ENTITY CHECKS PASSED`,
exit 0, with seven checks named `RCA-1565 …` (`evidence/entities_HEAD_green.txt`). I
re-ran the arms with a targeted block harness (`evidence/review_block2.py`, execs the
tree's own lines 31585..31792 verbatim, with `_workflow_job` and `_TESTS_YML` lifted from
`entities.py` by line marker rather than re-implemented): CLEAN **0 of 7**; the merge-base
`mutation_table.py` **4 of 7** (three defect checks + the driver pin, both null controls
and the workflow pin green — the body's "4 of 2241" arm); **A** 1 of 7, **B** 1 of 7,
**C** (`--pool-seconds` out of both lanes) 1 of 7, **D** (seed call site reverted to
`recorded_seconds()`, round 1's own example) 1 of 7, **E** (`if: always()` off the cache
save) 1 of 7 — each red check exactly the one the body names, every restore confirmed
`git diff --quiet HEAD` clean. **E** is the arm the brief asked me to run and it fires
through the adjacency regex, not the step name.

**5. Nothing regressed.** Hygiene all clean at the head: both claim files 0 diff lines vs
live `origin/main`; **no** `*_budgets.json` in the diff at all; `VERSION`,
`RELEASE_NOTES.md`, `manifest.json` untouched; `tests/structure.py` → STRUCTURE RATCHET
PASSED (`seam_cut_total 760 <= 760`, so the +64 lines paid for themselves);
`fold_ledger.py check` → 28 classes, 549 instances, 39 in-tree judge survivors, **101 rca
entries / 0 violation(s)**; `bugclasses.json`'s `RCA-1565-mutation-timeouts` → `status:
done`, `parts_missing: []`, `process_state` "(c) … (d) … arm", countermeasure naming the
(iv) refusal, `doc` and `in_tree_home` both citing the RCA file (which fold_ledger is what
validates, and it passes) — and the doc really contains those sections: §3 "(c), with a
(d) arm", §4 "Cost test (wall-clock, per occurrence, over this release cycle)" with both
sides in minutes and the P(recurrence) split, §5 the countermeasure.
`git merge-tree --write-tree b2b6acd64 HEAD` exits 0 with **no** `MERGE-CLAIM` line on
stderr; `mergeable_state: blocked` is the draft + code-owner review, not a conflict
(step 13).

## What blocks: the record this PR lands still contradicts the record this PR corrects

Both items are edits to files the PR already touches. No production or pin line is in
question, and every number above survives.

**a) §7's figure index was rewritten this round and left on round 1's head**
(`dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md:403-410`). The new bullet — "Failing arm,
surgical mutations, green arm" — still reads "**the five checks** named 'RCA-1565 …'" and
quotes **four `2239` tallies** (`entities_FAILINGARM.txt` = "3 of 2239",
`entities_MUTA/MUTB` = "1 of 2239", `entities_FINAL.txt` = "ALL 2239 ENTITY CHECKS
PASSED"). At the head the doc claims to be measured at (lines 9-12: "Base measured:
`origin/main` at `b2b6acd64` … Where a figure IS that seat's and was not re-taken, the
line says so") the file answers **seven** checks and **2241**, and the PR's own body says
so ("4 of 2241", `entities_R2_*`) — so the doc and the body now state two different
failing-arm tallies for the same described arm, and §7's command,
`PYTHONPATH=tests/hastub python tests/entities.py`, no longer prints the numbers beside
it. Two of §7's neighbours were updated in the same edit (the streak-end and the
per-night attribution bullets), which is what makes this a slip rather than a choice.
And the **C/D/E arms this round added — the proof that the two new pins bite — are absent
from the landed record entirely**: `defect-root-cause.md`'s "A detector must be shown to
detect … Both runs go in the report" lands in the doc, not the body, precisely because
"the analysis is `dev/audit/rca/<id>.md`" while "a pull-request body or comment can be
deleted or its author retired". The demonstration exists (I re-ran it: 1 of 7 each, 4 of
7 on the revert) — the record just does not carry it. Fix: restate the bullet at this head
(seven checks, `entities_R2_REVERT.txt` 4 of 2241, `entities_MUTC/D/E` 1 of 2241 each,
`entities_R2_HEAD.txt` ALL 2241), and keep round 1's `2239` lines only if labelled as the
round-1 head's, by the doc's own disclosure convention.

**b) the pool-factor correction reached the document but not the lines this PR adds**
— so the tree contradicts §2 of its own RCA. Three new comment lines still assert the
superseded figure *as the measurement*: `tests/mutation_table.py:136` ("the same script
costs 1.3-3.3x its solo recording there"), `tests/mutation_table.py:2883` — inside
`seed_pool_seconds`'s docstring, the function this PR installs — "the pool/solo factor
the lane itself measured **(1.3-3.3x across drivers on 2026-10-07/08)**", and
`.github/workflows/tests.yml:1085` ("the 3-worker pool exceeds by 1.3-3.3x"). §2 of the
same document, and my own re-derivation over exactly those drivers, nights and rule,
measure **0.47–3.27** (51 rows; the low end is `harness_headers.py` on 10-07). "Across
drivers on 2026-10-07/08" is the same population and the same window, so one of the two
is false, and the code is the false one. The fourth line is the same mis-attribution the
round-2 message says was corrected: the new `tests/entities.py:31575-31576` comment calls
closure.py's `0.3x-3.4x` "a pool factor the tree's own comment states reaches 3.4x", where
§2/§3 now say that figure is *how much one script's recordings vary run to run* "and is
not the pool factor". This is the class the RCA is the countermeasure for — a lane that
does not consult its own instrument — reproducing in the PR that lands the instrument:
the next seat to touch the bound will read `1.3-3.3x` out of the function's own docstring,
which is exactly how the inherited figure travelled this far. Fix: the four lines take
`0.47-3.27 (§2)` (and entities.py names 3.4x as recording variation, not pool factor); or,
if the correction is deliberately not going into the code this round, §2b says so in one
line, because nothing at head currently does.

## Reported, not blocking (three nits, all in the same file)

- §1's per-night bound table covers five of the six-night streak and silently skips
  **10-06** (head `cff39dad6`), whose recording I read as `{seconds: 765.6, rc: 0}` →
  bound **2297 s** — the one night of the streak with a *seeded-looking* number that is
  neither floor nor printed. A row (or a half-line saying why 10-06 is not in it) closes
  the gap; no figure depends on it, since 10-06's mutation lanes passed.
- §2b's header ("Each member below was re-measured at this head") and member 3's
  "Sampled rather than enumerated … not re-sampled here" pull opposite ways; the member's
  own disclosure is the honest one, so the header is the line to soften.
- The body's `## Head` names branch `fix/r9-nightly-mutation-bound`; the remote has only
  `fix/r9-nightly-bound` (`git ls-remote`), and it calls the row commit "an automatic
  merge of `origin/main`" when `955dd09a3`'s only parent *is* main — the operative claim,
  that no reviewed line moved, I verified. The opening "five distinct causes" and §2b's
  "three refusals are three different faults … rather than one cause" cannot both be the
  count; state which grouping.

## Step 11, the checks at this head

CI settled at this head, polled every 300 s from 14:58:59Z to **15:44:21Z** (`evidence/ci_poll.log`).
From the check-runs API at `96497ffc6` (`evidence/checkruns_final.tsv`, 40 runs / 38
names) against the required list read from ruleset 23698884 `main-protect-checks`
(enforcement active, `evidence/ruleset_raw.json`), compared in
`evidence/ci_required_at_head.txt`: **all 17 required contexts ran and concluded
`success`** — `fast (3.14)`, `browser`, `briefs`, `closure-scope`, `closures`, `typing`,
`hassfest`, `validate-hacs`, `policy-docs`, `wave-script`, `pr-contract` (two arms),
`env-matrix`, `Analyze (actions)`, `Analyze (javascript-typescript)`, `Analyze (python)`,
`mutation`, `budget-raise-gate` (two arms). **ABSENT: none. NOT-success: none.** The two
the brief named are green — `instrument-self-tests` (the lane that owns workflow-edit pins)
and `fast (3.14)` (the whole-file run) — and `nightly-status`, which round 1 verified at
the pre-merge head, is **success** here too, as are `delivery-status`, `coverage`,
`coverage-ratchet`, `graders-head-copy` and `CodeQL`; the remaining 14 names are the
expected `skipped` PR-only arms (`closures-autofix`, `claims-autofix`, `mutation-autofix`,
`record-autofix`, `record`, `recheck-gate`, `slow`, `nightly-ha`, `mutation-nightly`,
`mutation-ledger`, `mutation-ledger-push`, `mutation-pins`, `mutation-pin-plan`,
`delivery-status-publish`). Suite ids: `102813714594` (tests.yml: closures, coverage,
fast (3.14), mutation, nightly-status), `102813714569` (instrument-self-tests),
`102813715254`/`102813715225` (pr-contract).
`fast (3.14)` is the whole-file run; rather than repeat it I ran the file myself at this
head — `ALL 2241 ENTITY CHECKS PASSED` (above) — so the seven `RCA-1565` checks including
the two new pins are green both in CI's lane and in my own run.
No red check needs a root-cause answer at this head, and the non-exempt arm of
`defect-root-cause.md` was already answered by the body in round 1 and unchanged since
(the diff still touches `.github/workflows/tests.yml`, which `nightly-status` reads, and
the body names the cheaper detector and its standing cost). `mutation` is green; step 11's
separation was read at round 1's head as `empty scope`, and I relied on it there rather
than re-fetching the lane log — see the mechanism-identity argument above.


## Step 12, head discipline

I measured `96497ffc694302b814eecaeea2710bfdbebf6678` — the SHA the PR reports as its head
and the SHA the body names under `## Head` as the reviewed-and-merged result. Re-read
before posting: the API still answers `head.sha = 96497ffc694302b814eecaeea2710bfdbebf6678`,
`state: open`, `draft: true` (`evidence/head_recheck.tsv`), so the head did not move under
this verdict. If it moves after posting, the mechanism files survive only their byte-
identity with `7e8c5c8e4`, and the CI paragraph is this head's own.

## What this round owes

Round 2, so `fixer.md` still owes a repair, not a re-cut. Both blocking items are text
edits to files this PR already touches — one bullet in
`dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md` (§7's arm tally, plus the C/D/E arms and the
`entities_R2_*` log names), and four comment lines (`tests/mutation_table.py:136` and
`:2883`, `.github/workflows/tests.yml:1085`, `tests/entities.py:31575-31576`) — with the
three nits optional in the same round. **No production predicate, no pin, no bound number
is in question**: the mechanism, the seven checks, the class search, the corrected count
and both enumerators verify, and every figure in this verdict is mine, taken at this head.
Route it back to the fixer that authored `7e8c5c8e4`, as round 1 said: the same seat owns
the file, and the correction to be finished is its own.

## RESULT lines (round 2)

Full list with instruments in `evidence/RESULT2.txt`; the load-bearing ones:

- `RESULT scope-unchanged: PASS` — the round-2 delta is the RCA doc `+333/−68` and
  `tests/entities.py` `+64` (one hunk); `git diff 7e8c5c8e4 96497ffc6` for
  `tests/mutation_table.py` and `.github/workflows/tests.yml` is empty, and the head adds
  only `dev/programme/delivery/2074.md` over `7e8c5c8e4`.
- `RESULT green-arm-mine: ALL 2241 ENTITY CHECKS PASSED`, exit 0, seven `RCA-1565` checks
  `ok` (my own whole-file run at the head).
- `RESULT targeted-block: CLEAN 0 of 7 | REVERT 4 of 7 | A 1 | B 1 | C 1 | D 1 | E 1` —
  each red check exactly the one the body names; restores confirmed `git diff --quiet HEAD`.
- `RESULT class-search-carry: LANDED` — round 1's grep now exits 0; §2b has six members;
  `closures-autofix` is pull_request-only and job `113252338415` was `skipped` beside a
  `failure` `closures` on run `37753990323`; `b416093e9`/`387128bb3` are ancestors of main
  with the quoted subjects and touch `tests/closures.json` only.
- `RESULT record-autofix-correction: TRUE` — the `if:` exists verbatim at this head, at
  `83f7ca558` and at `d7c830c2f`; the three faults read out of logs I fetched (`HTTP 401`,
  `HTTP 422`, `exit code 128` + the beat-owed line). Round 1's verdict text carried the
  stale claim; the record here corrects it.
- `RESULT per-night-attribution: CORRECT` — bound arm on TWO nights; 10-03/10-04 print the
  `EXCLUSIVE` null-control refusal and no bound timeout; the Inferred/printed marking
  matches CI's logs; §4's 0.33 and 0.67 are that table's arithmetic.
- `RESULT factor-range-mine: 51 rows, 0.4653-3.2692` (`harness_headers.py` 449.2→209,
  `structure.py` 5.2→17) from three logs I fetched under §2's stated rule; the rule
  reproduces the doc's number. `RESULT delay-mine: 5h54m–6h53m` over twelve runs.
- `RESULT bound-arithmetic-mine: 1200/1576/2401/4469, seeded 4719/7200/7203` with the
  tree's own `driver_timeout` over seven heads — round 1's numbers, re-derived not relied
  on (except the `mutation` lane's empty-scope reading, above).
- `RESULT hygiene: PASS` — claims files 0 lines vs live `origin/main`, no budgets file in
  the diff, VERSION/notes/manifest untouched, STRUCTURE RATCHET PASSED, `fold_ledger` 101
  rca entries / 0 violations, RCA-1565 `done` with `parts_missing: []` and the (c)+(d)
  process state, `merge-tree` exit 0 with no `MERGE-CLAIM`.
- `RESULT FINDING-record-7` and `RESULT FINDING-record-factors` — the two blocks.
- `RESULT ci-at-head: 17 of 17 required success`, `nightly-status`/`instrument-self-tests`/
  `fast (3.14)`/`coverage`/`coverage-ratchet`/`delivery-status` success, nothing red.
