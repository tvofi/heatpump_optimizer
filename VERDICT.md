Fix review: merge 945f0787c349793fd4e771622b7147da5c90df65

bus-nonce: bcefa459159416a35088997294085542

Round 2. Measured and posted at `945f0787c349793fd4e771622b7147da5c90df65`; the head has not moved (`git ls-remote refs/heads/fix/r10-prepr-cap-pr` and `refs/pull/2341/head`, and a detached worktree at the merge base `92accb2cff702c910d33ee1a276d38f5b482061c`). Round 1 blocked this PR at `9512e209…` on `harness: class-open tests/rolling.py`. The block is cleared, and I re-ran what the delta could have moved rather than carrying round 1's numbers.

## The block, cleared — my rule, not theirs

The delta is `4c1fc7604` (the fix) and the merge of `origin/main 92accb2cf`. The merge resolved nothing in this PR's own files: `git diff 4c1fc7604 945f0787 -- tests/gate_lock.py tests/run.sh tools/pr/prepr.sh tests/entities.py tests/derive_closures.sh dev/governance/` is empty, so the merge is main's own content (`tests/replay.py`, `dev/audit/harnesses/r10_replay_loopnorm.py`, `tests/closures.json`, `delivery/2339.md`) and nothing of this PR's was rewritten under it.

`needs_lease` now answers `slot` for a name the recordings do not carry (`if seconds is None or seconds >= SLOT_MIN_SECONDS`), and its docstring says so and says why. I enumerated the class with **my** rule (`run|leased|run_always` + `tests/[A-Za-z0-9_]+\.(py|mjs)`) and with the census's, and the two sets are identical, so the census's population is not narrower than the class:

    RESULT ENUM my rule dispatched=36; census rule dispatched=36; same set=True
    RESULT ENUM dispatched by my rule but not the census's: []
    RESULT ENUM answers: Counter({'none': 24, 'slot': 10, 'lease': 2})
    RESULT ENUM tests/rolling.py               recorded=False -> slot
    RESULT ENUM tests/closure.py               recorded=False -> slot
    RESULT ENUM tests/setup_qa_render.mjs      recorded=False -> slot
    RESULT ENUM unleased_but_heavy=[]

The three names round 1 found unrecorded now all answer `slot`, `unleased_but_heavy` is empty, and the census prints that line on a pass as well as on a failure (my head run's `lease class:` row reproduces the body's `dispatched=36 (floor 30) lease=['tests/harness_headers.py', 'tests/stress.py'] slot=10 none=24 unleased_but_heavy=[]` exactly). Independently, I checked that no dispatch site escapes the census: of the 38 `tests/` paths in `tests/run.sh`, the two it does not match are `tests/ci_ratchet.py` (comments only) and `tests/gate_lock.py` (the lease CLI itself), so the 36 is the whole dispatched set.

## The detector is shown to detect, and the round-2 mutation proof re-run

Five mutants at this head, each in its own worktree, restored with `git checkout --`:

    RESULT HEAD   ALL 2336 ENTITY CHECKS PASSED
    RESULT MUT-E1 3 of 2336 ENTITY CHECKS FAILED
    RESULT MUT-E2 2 of 2336 ENTITY CHECKS FAILED
    RESULT MUT-E3 1 of 2336 ENTITY CHECKS FAILED
    RESULT MUT-E4 2 of 2336 ENTITY CHECKS FAILED
    RESULT MUT-P1 273 passed, 1 failed   (head beside it: 274 passed, 0 failed)

Every named failure is the body's, detail string and count, and nothing beyond them moved. E4 is the one I care about, because it restores the exact defect I blocked on:

      FAIL every script run.sh dispatches through `leased` is classified, and none heavy is left unleased (#2341)  [dispatched=36 (floor 30) lease=['tests/harness_headers.py', 'tests/stress.py'] slot=7 none=27 unleased_but_heavy=['tests/closure.py', 'tests/rolling.py', 'tests/setup_qa_render.mjs']]
      FAIL run.sh leases a FULL or stress run itself, ...  [need=['lease', 'lease', 'slot', 'none', 'none'] ...]

so the census fails on the pre-fix classifier and passes at the head — a check that would have been worse than none if it passed on the defect too. E1 kills both the classifier and the census (`slot=0`), E2 the run.sh wiring and the `derive_closures.sh` join arm, E3 the pool's reclaim branch, P1 the slot-label export; all four reproduce round 1's kills as well.

## Re-run unchanged, since the delta did not touch it

    RESULT CAPACITY slots=4 n=5: acquired=4 refused=1
    RESULT CAPACITY null control slots=6 n=5: acquired=5 refused=0
    RESULT CAPACITY null control slots=1 n=2: acquired=1 refused=1
    RESULT QUEUE waiting=True rc=0 queued_line=True
    RESULT BLOCK (head, 4 slots held) while-pool-full reached_step2=False after=75.0s; tail="ok transport"
    RESULT BLOCK (head, 4 slots held) after_release reached_step2=True

The pool's capacity, its nulls and its queue are what round 1 measured; a real `prepr.sh` still stops at step 1b with the pool full and proceeds on release, so the bound the change earns is intact. `tests/run.sh`, `tools/pr/prepr.sh`, `tests/derive_closures.sh` and `nudge.md` are byte-identical to the head I measured in round 1, so those measurements hold of this head too. Claims: the round-1 block's other results stand — merge base `92accb2cf`, no claim file moved, `claims hygiene: 92accb2cf… ok`, `VERSION`/manifest/notes untouched, no `*_budgets.json` changed, `policy_lint` `TOTAL: 0 error(s) across 41 policy file(s)`, `rules_sync --check` `RULES-SYNC ok`, and `git merge-tree --write-tree origin/main HEAD` exits 0.

## The policy edit, for the owner's read

`dev/governance/rules/gate-scoping.md` gains the new arm in the same sentence that names the pool ("a `closures.json` recording at or above `SLOT_MIN_SECONDS`, and an UNRECORDED script, never timed; `none` only where the recording says seconds") — the minimum that states the scope, no re-draft, and the two regenerated copies move with it. It goes 60 lines to 61 against a recorded cap of 61 (`.claude/rules/gate-scoping.md` is the capped path, exactly at 61), so the cap is met and the budget file is untouched. `## Approval` remains right: `gate-scoping.md` is `@tvofi`-owned and the owner's approving review at this head is still owed. One debit the compression pays, unchanged from round 1: the shallow-clone paragraph still lacks "fetch first" (#1699's remedy), which `git grep` finds nowhere else.

## Two figures that do not re-derive, named rather than passed

- The body's mutation tallies read `of 2334 ENTITY CHECKS FAILED`; the tree answers **2336** (my head run: `ALL 2336 ENTITY CHECKS PASSED`). The failure counts are right in every arm — 3, 2, 1, 2 — so only the denominator is stale, and it went stale under the `origin/main` merge that brought two more checks into `tests/entities.py`. Not a defect in the fix; a figure the body should re-take.
- `## Head` carries **two** head paragraphs with identical wording, the second naming `393c8c114a026f61fca302e4a083759f7fd2e0c4`. That commit is in this repository's object store but is **not an ancestor of the head** and is on no remote ref — a superseded merge the body's re-take left behind. The measured head is the section's first line, so the verdict stands, but a stale head in a body is the shape another seat pins by mistake; it should be cut before the merge. It does not change the verdict or move the head.

Evidence for this round, including the four mutant logs, the census line at the head, the two probes and their raw output, is the directory beside this file. The head's 45 check runs have all concluded — `30 success, 15 skipped`, no failure — and every commit in the branch range carries no red either (the twelve `cancelled` on `f36c16eeb` are the push that superseded it, re-run green at `9512e209`), so `## Red checks: none` is accurate, no check owes the body an answer, and nothing here waits on one.
