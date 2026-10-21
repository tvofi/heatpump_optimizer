Fix review: merge 6efcb1ac090e19522c95701db295908fb52990ab

bus-nonce: cf1e77012b3763d8ff861cead89fecbc

Round 3 (the batch-arm repair; round 2 blocked on a mutation survivor and on
`## Red checks`). Measured from a detached worktree at
`~/hpo-seats/r10s3/r10-train-hold-review2/wt`, head `6efcb1ac090e19522c95701db295908fb52990ab`, merge base
`f639f3b0d40c2cf528a7b781efebabf4afc2f140`. Instruments are mine and disclosed as mine (the finding is
issue-origin #2302 and has no committed finder harness): `hold_harness.py`
drives the production `hold_refresh`/`hold_release`/`wait_ci`/`recarry` with a
recording `run()`; `wf_harness.py` extracts the automerge step's `run:` from
the measured `tests.yml` and executes it over a stubbed API; round-3 variants
A/B/C are copies of the measured `merge_train.py` in the worktree's seat
directory, run with `--self-test`. Outputs are in
`~/hpo-seats/r10s3/r10-train-hold-review2/evidence`.

## Round 2's block 1 is cleared

At the measured head: `merge_train.py`, `tests.yml` and `tests/closures.json` are
blob-identical to the handoff `a8c8287`; `tests/entities.py` and `tests/closure.py`
differ only by main's `tools/plan/` additions, and both that entry and this
branch's `tools/audit/seat/merge_train.py` INERT_EXCEPT entry are present after
the merge. Baseline `198 checks, 0 failed`. Delete the batch start
`hold_refresh()` with the arming kept -> `rc=1, 198 checks, 1 failed`, naming
`a real-base batch publishes the record-beat hold before it merges anything
(the primary path is armed, not only the serial one)`. Delete both it and
`hold_armed = True` -> the same. Neither run printed a traceback, which matches
the fixer's disclosure that its first form passed a list to `check()` and
crashed; the final `bool(...)` makes the mutant red, not crash. The
`/git/commits` and `/git/refs` stub answers are the hold's own shape, and the
check reads the recorded call order, not a count.

## The arm's world is narrower than the name claims (carried, not blocking)

The check's world is `go({1: ...}, base="main", setup=...)` with `bot_prs`
left False, so its first `gh pr merge` is the D merge of #1. Every orchestrator
batch this round ran `--bot-prs` (b15, b16, b19), and in that mode `_batch`
calls `sweep_bots()` first, merging the open record PR before any wait, proof
or D merge. I moved the production arming+publish below `self.sweep_bots()`
and ran three variants of the same file: A, the shipped world with
`bot_prs=True`, production in place -> `198/0`; B, A with the publish moved ->
`198/1` on the named check; C, the SHIPPED world (no `bot_prs`) with the
publish moved -> `198/0`. C is a survivor of the same kind, smaller than round
2's: deletion reds, placement below the real first merge does not. The fix is
the variant-A keyword; the stub already models record PR #9. Not a block
because the production publishes above the sweep and the round-2 regression
(deletion) is now pinned. Carry: dismissed: written triage -- a `bot_prs=True`
arm is owed when the batch self-test is next touched; it passes at this head
and reds on the moved publish.

## Round 2's block 2 is answered, and its facts check out

The live body's `## Red checks` names four. `nightly-status`: the API reads
run 39387919507 as event `schedule`, head `0c298f6`, created
2026-10-20T07:39:11Z, with the `slow` job failed — main's run, before this
branch's first commit. `closures`: job 118884971127 printed `INERT READS
UNDER-APPROXIMATED ... tests/entities.py: tools/audit/seat/merge_train.py` at
21:24:53Z. `closures-autofix`: job 118895327353 printed `AUTOFIX:
skip-merge-failed` and `THE REPAIR DID NOT HAPPEN`. `pr-contract`: the
previous body's silence, now named. The repair adds
`tools/audit/seat/merge_train.py` to `INERT_EXCEPT` (the established route;
seven prior `tools/audit/` entries do the same) and adds it to
`tests/entities.py`'s recorded closure — the set moves by exactly that one
file (334 -> 335, nothing dropped), `rc: 0`. My local body check
(`policy_lint.mjs --pr-body <live body> --head <head> --red nightly-status
--red closures --red closures-autofix --red pr-contract`) prints
`PR-BODY: 0 error(s)`. At the measured head's tree: `closure.py selftest` ->
`ALL 124 closure shrink pins PASSED`; `closure.py no-copies` -> no copy;
`orphan_files()` -> 0; `tests/structure.py` -> `STRUCTURE RATCHET PASSED`.

## The closures `seconds` move (324.8 -> 670.4): disclosed, not earned, not scoping

The body discloses it as a loaded-Darwin re-derive and says "the closure set is
what the gate reads". True of `select`, not of every reader:
`gate_lock.needs_lease` classifies on `seconds` (`SLOT_MIN_SECONDS` 69) — both
324.8 and 670.4 are `slot`, so the heavy-slot classification is UNMOVED. The
derivation `lane_plan` is not unmoved: greedy LPT over the full recorded set
re-shards scripts at 3 and 4 lanes (per-lane recorded loads 866.7 -> 981.9 and
650.1 -> 738.5; the union is identical), and `mutation_table` seeds a driver's
initial estimate and timeout from the table until its baseline or last pool
cost replaces it. None of these changes which scripts run or what passes; the
move is mostly load (the new block spawns about eight short `bash`/`python3`
runs, not ~345 s). Disclosure is enough because every classification that
binds is unmoved; the post-merge re-record on main is where the number gets a
quiet re-take. Carry: dismissed: the number's binding consumer is unmoved; a
timing-only re-take belongs to the re-record, not this diff.

## The round-1 repairs still hold

`hold_harness.py` at the measured head: 12/12 (a PATCH before every one of 5
sleeps, the simulated refresh gap 240 s against `HOLD_MAX_AGE_S` 3600; a
recarry refresh only when main is not contained and before `remerge_main.sh`;
a refused commit writes no ref and logs `NOT held:`; a refused create falls
back to PATCH; a rehearsal and an unarmed run write nothing). At
`17197336f`, the same harness reds the wait-loop refresh, the recarry refresh
and the bare-`wait-ci` arming. `wf_harness.py`: 7/7 (fresh skips; at-bound,
ahead-of-clock, 422 and 404 proceed silently; 500 and unparseable warn and
proceed); the old step reds the 422 arm, as does the head step with the 422
arm dropped.

## Not established

The live `train-hold` create/refresh/delete cycle has still not run against
GitHub, and I did not run it: a write to the shared ref is the orchestrator's.
What I re-read: the payload shapes (400 for bad JSON, 422 naming the missing
keys), GitHub's create-commit default of the current date when `committer` is
omitted, the token's `repo` scope, the 422 absence code,
`GET /git/ref/heads/main`, and that both branch rulesets include only
`~DEFAULT_BRANCH` while every `push:` arm is `main` or `v*` tags.

## RESULT lines

```
RESULT baseline at the measured head=198 checks, 0 failed
RESULT M8 delete batch start hold_refresh=rc 1, 198 checks, 1 failed, named check, no traceback
RESULT M10 delete arming+start=rc 1, 198 checks, 1 failed, named check, no traceback
RESULT A bot_prs=True publish in place=198/0; B bot_prs=True publish moved=198/1; C shipped world publish moved=198/0 (survivor, carried)
RESULT round-1 F1 hold_harness head=12/12 old=9/12 (red: wait refresh, recarry refresh, bare wait-ci arm)
RESULT round-1 F2 wf_harness head=7/7 old-step=5/7 (422 warns); no-422-arm mutant=6/7
RESULT red checks named in body=4, every fact re-read at the API (scheduled run 39387919507; jobs 118884971127, 118895327353)
RESULT closures set delta=+tests/audit/seat/merge_train.py (334 -> 335, nothing dropped), rc 0
RESULT closure selftest=ALL 124 PASSED; no-copies=pass; orphans=0; structure=PASSED
RESULT needs_lease(tests/entities.py)=slot at 324.8 and 670.4 (SLOT_MIN_SECONDS 69) -- unmoved
RESULT lane_plan full set lanes=3 changes=True (866.7 -> 981.9, union identical); lanes=4 changes=True (650.1 -> 738.5)
RESULT body contract local=PR-BODY: 0 error(s) with the four --red names
RESULT live publish cycle=RAN BY NO ONE (disclosed)
RESULT head_measured=6efcb1ac090e19522c95701db295908fb52990ab body_head=names the measured head `6efcb1ac` (and the previous recarry `2b82f90` and the authored `a8c8287`), and the live body otherwise reads as pushed
RESULT ci at head=at this head every completed check is green or deliberately skipped, including `fast (3.14)`, `coverage`, `closures`, `pr-contract` (both its runs), `closure-scope`, `mutation`, `instrument-self-tests`, `arch-score`, `budget-raise-gate`, `briefs`, `hassfest` and the analysers; `nightly-status` alone is red and the body names it; `Analyze (python)` (the cancelled 30-minute run, being re-run) and `composed-proof` are still running
```
