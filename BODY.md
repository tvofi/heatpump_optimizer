R11-PRE-HANDOFF-BOOKKEEPING part 1 of 4 (owner ruling 2026-11-13 on card P10): roster carries 0-4. Carries 5-20 are later parts, dispatched at this handoff, and none is answered here.

- **Carries 0 and 1 (the predictor owes the roster fetch).** `pr-contract` fetches `+refs/heads/handoff/audit-r*-roster:refs/remotes/origin/handoff/audit-r*-roster` before `carry_audit.py check`. `ci_predict.py` read whatever remote-tracking ref the seat's checkout last fetched. The tree clone's `fetch_round_rosters` copies that ref from the checkout, so it was just as stale. As a result, a carry to a group the round roster gained since that fetch was predicted `CARRY BAD ... is not a group of the roster`, though CI routes it. `predict` now runs `refresh_round_rosters(root)` whenever it is given a body. That is CI's fetch, into the checkout, so the carry arm and the graders arm's clone both read origin's roster. An unreachable origin leaves the refs alone and adds the note `ROSTER UNFETCHED: ...`.
- **Carry 2 (step replay keyed on what a step reads).** `step_replay_preds` replayed only the `instrument-self-tests` steps whose run text named a changed file, or named a tool whose text names it. It now also replays every step whose recorded closure in `tools/ci/selftest_closures.json` holds a changed path under `files` (`recorded_readers`). That is the enumerator the carry names. It is read through `selftest_scope.py`'s own `job_steps` and `covers`, so a `D/**` entry counts. The carry's instance (`queue_pre_flight.py --self-test` over `merge_train.py` at `23b943c987`) is already predicted by main's predictor through the one-level text rule (`## Figures`). What this part adds is the readers the text rule misses (counts in `## Figures`).
- **Carry 3 (the post-push `update-ref` in `write_roster`).** No arm can fail without it, so it is removed, as the carry directs for that case. The callers that reach `write_roster` are `roster_edit.main`, `roster_queue.py`'s batch and `roster_sync.sync`. Each runs `fetch_origin` (`+refs/heads/*:refs/remotes/origin/*`) first, which moves `origin/<branch>` to this run's own last push before the next op's `prepare_worktree`. A lost race re-fetches as well. The planted-defect audit's mutant (the line deleted) left the self-test green. With the line removed, the existing row `P409: two ops in one run both land after our own push` still passes, because the per-op fetch is what lands the second op.
- **Carry 4 (the queue-then-sync duplicate).** `already_carried` compared whole normalised texts. The queue's landing is `From <src>, body item <id>: <text> (items <id>)` and the sync's derived text is `<text> Carry: <G>`, so the two never matched. It now compares `finding_core`: `finding_words` with the queue's prefix, its `(items ...)` tag and a trailing `Carry: <G>` clause stripped. It also matches a carry tagged with the body item's own `carry_audit` id, which `carry_plan` passes. The existing duplicates on the roster are roster data for the orchestrator, not this carry.

Alternatives not taken, and why each lost:
- Carry 0: fetching inside the tree clone straight from the checkout's origin URL. The carry arm itself runs in the checkout (`carry_preds(root, ...)`), so it would still read the stale ref; one fetch into the checkout serves both readers.
- Carry 2: running `selftest_scope.select` (the prelude's selection). On a gate-file diff it returns FULL, every step, which is a replay of all 120 steps rather than the readers of the changed paths.
- Carry 3: a self-test arm with `_on_origin`'s fetch disabled. `main` fetches every head before `write_roster`, so such an arm stays green with or without the line; it would pin nothing.

## Head

`047ea3fddfdf4e90227010b4dacc2d38ec0b9f0a`, cut from `origin/main` `6d55bf6fd1cd3dd0677d98f6c2da33d259b35b18` (the merge base). It is `275faa2a43` plus one commit answering `prepr.sh`'s 17 survivors and its own self-test row (below). Figures were taken 2026-11-16 06:20Z to 08:40Z. Those the last commit touches are re-taken at this head: the two self-tests it edits, the carry-0 run and its mutants. `git merge-tree --write-tree origin/main HEAD` against `origin/main` `f1520e3539` reports no conflict.

One more change, outside the carries. `prepr.sh`'s own self-test failed one row whenever a fixer ran it with `MUTANT_IN_PLACE=1`, as `fixer.md` step 2 directs: `a check needing a git checkout measures nothing in the archive copy, and is refused (got 0, wanted 1)`. The archive-copy rows inherited the caller's variable and ran in place. Those three `mutants_line` calls now clear it (`MUTANT_IN_PLACE= mutants_line ...`).

## Mutation proof

Each mutant was applied in its own worktree at the head (`perl -0pi`), and the named self-test was run there. Failing rows:

- `mut:roundfetch` (`predict`'s `refresh_round_rosters` call deleted, at `275faa2a43`): FAIL `predict calls refresh_round_rosters on one `# mut:roundfetch` line`. At this head that pin is a behavioural row instead. `predict` is called with a body and without one, with the refresh stubbed. Its `if body:` made false, or its note append made false: FAIL `predict with a body refreshes the round rosters and notes a failed refresh`.
- `refresh_round_rosters` returning `None` before its fetch (at `275faa2a43`): FAIL `refresh_round_rosters moves it to origin's branch and returns no note`, and FAIL on the unreachable-origin row. At this head, its one `return` reduced to `return None`, or git's reason dropped from the note: FAIL `an unreachable origin leaves the ref, raises nothing and notes ROSTER UNFETCHED with git's reason (null control)`.
- `recorded_readers`' unreadable-table guard made false: the self-test raises (`no table: no recorded reader, nothing replayed, nothing raised` never prints), rc non-zero.
- `mut:readers` (`n in readers or` deleted from the step filter): FAIL `a step whose recorded closure reads the changed file, its run text naming none, is replayed and predicted red` and FAIL `a closure's `tools/lib/**` entry covers the changed file`.
- `mut:dupkey`, in place, `python3 -I tools/audit/seat/roster_sync.py --self-test`:
  - the base's key restored (`finding_words(c) == finding_words(text)`): `98 checks, 2 failed`. The failing rows are `the queue's landing of the same item is not appended again: ...` and `a reworded queue landing tagged with the item's own id is not appended again`. This is the failing test first.
  - the id arm deleted: `1 failed` (the reworded-landing row).
  - the core arm deleted: `3 failed` (the queued row and both markup rows).
  - at this head, the `R9-QID` fixture's landing deleted: FAIL `a reworded queue landing tagged with the item's own id is not appended again (got: ["the sync's words for the queued item. Carry: R9-QID"])`. The row now compares the carry whole, where it compared only a length at `275faa2a43`, which `prepr.sh` reported as the survivor `roster_sync.py:1149`.
- Carry 3 removes a line, so it has no mutant; the self-test at the head (`## Figures`) is the control.

## Unpinned sites

`prepr.sh` step 6d' ran with `MUTANT_IN_PLACE=1` and `MUTANT_CMD` set to `roster_sync.py --self-test` together with `ci_predict`'s `roundref_self_test` and `step_replay_self_test`, the rows this diff adds. At `275faa2a43` it left 17 survivors. The killed ones are in `## Mutation proof`. The rest, by key at that head:

- `tools/pr/ci_predict.py:916 CONST_SWAP` (the fetch timeout 60 to 61): an equivalent bound. A value check: the timeout path is `timed out` in the one `return`.
- `tools/pr/ci_predict.py:918 RETURN_DEL` and `:923 RETURN_DEL`: those returns no longer exist. `refresh_round_rosters` has one `return`, killed as above.
- `tools/pr/ci_predict.py:921 CONST_SWAP` (the stderr line index): the index no longer exists. The note quotes the whole stderr, and dropping it is killed.
- `tools/pr/ci_predict.py:558 CONST_SWAP`, `:562 CALL_DEL`, `:562 CONST_SWAP`: the `sys.path` insert position and its `pop` in `recorded_readers`. These are equivalent: `selftest_scope` imports the same either way. A value check.
- `tools/pr/ci_predict.py:565 GUARD_OFF` and `:566 RETURN_DEL`: killed at this head by the no-table row.
- `tools/pr/ci_predict.py:1242 GUARD_OFF`, `:1244 GUARD_OFF`, `:1245 CALL_DEL`: killed at this head by the `predict` with and without a body rows.
- `tools/pr/ci_predict.py:1762 CALL_DEL` and `:1762 CONST_SWAP`: the `sys.path` setup of `roundfetch_self_test`, the self-test's own scaffolding, not a production site.
- `tools/audit/seat/roster_sync.py:1149 STMT_DEL`: killed at this head, as above.
- `tools/audit/seat/roster_sync.py:1291 STMT_DEL` and `:1298 STMT_DEL`: each deletes one `check(...)` row of the self-test. That removes a pin, not production behaviour; each row was shown to fail on its production mutant (`mut:dupkey`).

## Null control

- Carry 0: an unreachable origin leaves the stale ref, raises nothing and returns the note (self-test row above). A body-less `predict` runs no fetch: the call sits under `if body:`.
- Carry 2: a closure entry that does not hold the changed path replays nothing (`null control: a closure not holding the changed file is not replayed`). The three existing null rows of `step_replay_self_test` still pass.
- Carry 4: a distinct item for the same group still appends. `R9-QUEUED` ends with `a distinct finding for the queued group. Carry: R9-QUEUED` beside the queued landing. The existing B1 rows (`R9-FROM-2`, `R9-FROM-3`, `R9-PROSE`) still append.

## Figures

- Carry 0, end to end on this checkout. `git update-ref refs/remotes/origin/handoff/audit-r10-roster f20f8b13a797c309719ddb00a853748697f1814f` sets the ref to a roster commit older than the group `R11-OUTSIDE-SELF-SETTING-PUMP`. Then `PYTHONPATH=tests/hastub python3 tools/pr/<copy>.py --base origin/main --body <body: one item, Carry: R11-OUTSIDE-SELF-SETTING-PUMP> --only orphans`:
  - with main's `ci_predict.py` (`6d55bf6fd1`): `PREDICT pr-contract / pr-contract CARRY BAD item 8d6b2d8e (R11-OUTSIDE-SELF-SETTING-PUMP: ... is not a group of the roster or of origin/handoff/audit-r10-roster)`, rc 1, ref left at `f20f8b13a7`.
  - with the head's: `no closures, fast, governance or instrument red predicted`, rc 0, ref moved to origin's tip (`0350a63e82` at `275faa2a43`, `3b6de29be6` at this head).
- Carry 2, `python3 -I -c "import sys; sys.path[:0]=['tools/pr']; import ci_predict as c; ..."` at this head, comparing `recorded_readers(root, {f})` with the steps `names_changed` selects for one changed file `f`. Each row is f: steps by recorded closure / by text / closure-only.
  - `merge_train.py`: 28 / 29 / 14
  - `roster_lib.py`: 42 / 9 / 36
  - `ci_predict.py`: 13 / 6 / 11
  - `roster_sync.py`: 19 / 8 / 16
  - `carry_audit.py`: 27 / 14 / 18
- Carry 2, the carry's instance replayed. In a detached worktree at `23b943c987`, an uncommitted predictor copy was run with `--base 23b943c987^ --only step-replay`.
  - main's copy: `PREDICT ... STEP REPLAY Show the carry check and the queue pre-flight refusing their own fixtures: rc 1 at the head, 0 at the base`, wall 674 s on this 4-core host under load. So the instance is already caught on main, by text.
  - the head's copy: the same line, wall 1226 s, the cost of the added closure-only steps for that diff. Each replay is bounded by `SELF_TEST_TIMEOUT` (180 s), and a step past it is `UNMEASURED`, never a red.
  - the head's copy also printed `STEP REPLAY Show the CI predictor ... rc 1 at the head`. That copy was taken before `275faa2a43` and still held the push-site fixture `ref_privacy` refuses. It is not a `23b943c987` red: at this head that step's command, `python3 -I tools/pr/ci_predict.py --self-test`, prints `ci_predict self-test: 0 failed`.
- Carry 4, census at roster tip `0350a63e82`, of the carries that repeat an earlier carry of the same group. Command: `python3 -I -c "import json,subprocess,sys;sys.path[:0]=['tools/audit/seat','tools/audit'];import roster_sync as rs;d=json.loads(subprocess.run(['git','show','origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r11-groups.json'],capture_output=True,text=True).stdout);cs=[[c for c in g.get('carry') or [] if isinstance(c,str)] for g in d['groups']];print(sum(map(len,cs)),sum(rs.finding_words(c) in map(rs.finding_words,l[:i]) for l in cs for i,c in enumerate(l)),sum(rs.already_carried(l[:i],c) is not None for l in cs for i,c in enumerate(l)))"`. It prints `429 0 8`: 429 carries, 0 repeats under the base's key, and 8 under the head's. Each of the 8 is a queued `From ..., body item <id>:` landing beside the sync's bare copy; one of them is this group's own carries 0 and 1. The same count over `wave-r10-groups.json` is 2466 carries, 0 under the base's key, 58 under the head's.
- `prepr.sh` step 6d on this diff replays 45 `instrument-self-tests` steps, in `step_replay_preds`' own order. Two of the four `prepr.sh` runs (at `275faa2a43` and at this head) predicted `STEP REPLAY Show the beat's job rows refusing their own fixtures: rc 1 at the head, 0 at the base`. The same step was green in every other replay at this head:
  - `python3 -I tools/audit/seat/beat_jobs.py --self-test` run alone, eight times: `263 checks, 0 failed` each time. The runs covered `PYTHONPATH=tests/hastub`, `MUTANT_IN_PLACE=1`, `MUTANT_CMD` set, `PREPR_SKIP_CLOSURES=1`, `HPO_SLOT_LABEL` set, and a heavy slot held through `tests/gate_lock.py slot-take`.
  - `replay_step` on that step, twice: rc 0 both times.
  - all 45 steps replayed in order outside `prepr.sh`: rc 0.
  - `ci_predict.py --base origin/main --body <this body> --record-self-tests` alone: `no ... instrument red predicted`.
  - the other `prepr.sh` runs.

  No cause was found, so it is recorded here and not carried (`finding-propagation.md`: an unverified observation is not carried).
- `python3 -I tools/pr/ci_predict.py --self-test`: `ci_predict self-test: 0 failed`.
- `python3 -I tools/audit/seat/roster_sync.py --self-test`: `roster_sync self-test: 98 checks, 0 failed`.
- `python3 -I tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 311 checks, 0 failed`.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `0 refused` at this head. At `e8aaab0fd3` it gave `1 refused`, for the push-site lines of the first fixture, before any push of a fix branch (`## Red checks`).
- `python3 tests/closure.py select --diff 6d55bf6fd1`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` Run with `PYTHONPATH=tests/hastub`:
  - `tests/entities.py`: `ALL 2723 ENTITY CHECKS PASSED`
  - `tests/doc_claims.py`: `ALL 410 checks PASSED`
  - the `run_always` set: `claims hygiene: origin/main ok`, `ALL 118 closure shrink pins PASSED`, `layout self-test: ok`, `ALL 115 HARNESS HEADER CHECKS PASSED`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 6d55bf6fd1`: `Architecture score: dS +0.0000 NULL`.

## Red checks

none

## Brief carries

Roster carries of R11-PRE-HANDOFF-BOOKKEEPING, by position. Carries 0-4 are built here; carries 5-20 are later parts.

- Carry 0: built here (`refresh_round_rosters`).
- Carry 1: built here, the same finding as carry 0 (carry 4's shape: the queue's landing and the sync's copy).
- Carry 2: built here (`recorded_readers`).
- Carry 3: built here, as the carry's removal branch (no arm can fail without the line).
- Carry 4: built here (`finding_core`, `item_ids`).
- Carry 5: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 6: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 7: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 8: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 9: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 10: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 11: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 12: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 13: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 14: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 15: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 16: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 17: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 18: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 19: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING
- Carry 20: not built here; a later part of this group. Carry: R11-PRE-HANDOFF-BOOKKEEPING

## Forward-carry

- Step replay now runs the closure-only readers too, so `prepr.sh` step 6d on a diff touching a widely read seat module costs more wall time: 674 s became 1226 s on `23b943c987`'s diff, on one loaded 4-core host. A later part that changes 6d's budget, or `HPO_STEP_REPLAY_TIMEOUT_S`, re-measures this with the same replay at its own merge base. Carry: R11-PRE-PARALLEL-PIPELINE

## Friction

none
