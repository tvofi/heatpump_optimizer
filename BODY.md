R11-HOTFIX-TRAIN-SKIP-READMIT (proposal P-train-timeout-skip-readmit; owner ruling 11-28, an exception to the tooling freeze). On train 2 (11-28) `already_held` re-admitted a same-verdict skip only for HOLDER, BRANCH-POLICY and PRE-FLIGHT, so five green PRs skipped on the train's own CI-wait TIMEOUT or a read at a moved head (#3897, #3845, #3870, #3872, #3883) answered `ALREADY #N: skipped by this train at this same verdict` until the train exited.

What changes, in `tools/audit/seat/merge_train.py`:
- `HeadRed` whose only red is `["TIMEOUT"]` (the value `wait_ci` returns when its polls run out) carries class `CI_TIMEOUT` (`TIMEOUT`); a real red, or a red beside TIMEOUT, carries none. The three approve-step stops at a head the branch moved off (`land`, the carried approval, the mandate approval) carry `HEAD_MOVED`. `MAIN_MOVED` already existed.
- `READMIT_ON_GREEN = (CI_TIMEOUT, MAIN_MOVED, HEAD_MOVED)` joins `READMIT_SAME_VERDICT`, so `already_held` (the one rule `add` and the drain `queue_take` share) admits them at the same verdict.
- `add` re-reads such a skip in `Train.readmit_refusal` before it spools: `classify`'s reading at the live head (`Train.live_classify` -> `classify_cmd`) must be GREEN, and `review_carry.py <verdict> <live head> --main origin/<base> --verdict-only` must exit 0 (CARRY); otherwise `ADD REFUSED #N readmit: ...` rc 1, nothing spooled. The existing pre-flight-park re-read (carries 3/18) moved into the same method, so `train_add` holds one re-read call, not two.
- `add --only` (`merge_train.py add` and `train.sh add`): a train the add starts runs the entry (and any spooled leftovers) alone; `ready_batch` is not read. On a live train it changes nothing, since `add` spools only the entry. The 11-28 incident: an add on an empty state dir started an 8-PR train when one was meant.

Alternatives not taken: re-admitting these classes in `already_held` with no live re-read (a timed-out head that then went red, or a verdict a bot push no longer carries, would rejoin); a second copy of the carry predicate inside the train (`review_carry.py` is the one predicate, asked rather than copied, and itself asks `app_approve.sh --carry`); a separate `readd_after_train.sh`, the orchestrator's local workaround, which this replaces.

## Head

5135ba5252a289e71197600e92cf1d419f57d7cb, measured on origin/main a59a1b0d9ac782fabbe01eb84f4d4ff5a17aee43 at 2026-11-28T17:03Z.

## Mutation proof

Test first: commit 54d94329148e7a68821e5960e6ac3df3c72a99ec, before the fix, names `CI_TIMEOUT`, `HEAD_MOVED` and an unused `only` keyword only. At that commit `_skip_readmit_self_test` held 6 checks and failed 5 (the sixth, the real-red and new-verdict null, passes, as a null should); two more were added at 5135ba52 for prepr's survivors (below).

Each fix line deleted or neutralised at the head, then `_skip_readmit_self_test` run alone (driver: import `merge_train`, call `_skip_readmit_self_test(check)`), file restored after each:
- `READMIT_SAME_VERDICT` without `+ READMIT_ON_GREEN` -> FAIL `skip readmit: a same-verdict re-add ... is ADDED`, FAIL `skip readmit null: the live head RED or WAIT ...`
- the `if cls not in READMIT_ON_GREEN: return None` arm made unconditional -> FAIL `skip readmit: ...`, FAIL `skip readmit null: the live head RED or WAIT ...`
- the GREEN test (`if code != 0` after `live_classify`) made `if False` -> FAIL `skip readmit null: the live head RED or WAIT ...`
- the carry test (`if code != 0` after `review_carry`) made `if False` -> FAIL `skip readmit null: the live head RED or WAIT ...`
- `HeadRed`'s `cls=CI_TIMEOUT if red == ["TIMEOUT"] else None` to `cls=None` -> FAIL `skip classes: a head wait that never completes is HeadRed [TIMEOUT] ...`
- `land`'s `cls=HEAD_MOVED` removed -> FAIL `skip classes: \`land\` at a head the branch moved off stops [HEAD-MOVED]`
- `others = [] if only else t.ready_batch(...)` to `others = t.ready_batch(...)` -> FAIL `add --only: a started train's queue is the entry alone ...`
- `readmit_refusal`'s `if not is_sha(h)` made `if False`, or its return deleted -> FAIL `skip readmit null: an unreadable live head is ADD REFUSED ...`
- its `git fetch -q origin <base> <verdict> <head>` deleted -> FAIL `skip readmit: a same-verdict re-add ...` (the fetch must precede the `review_carry.py` call)
- its final `return None if code == 0 else (...)` made a bare expression -> FAIL `skip readmit: a same-verdict re-add ...`
- `live_classify`'s `return classify_cmd(self, h, pr, False)` deleted, or `False` swapped to `True` -> FAIL `skip readmit: \`live_classify\` is \`classify\`'s pull-request reading ...`
- `train.sh`'s `${add_only:+"$add_only"}` removed -> `train.sh --self-test`: `REFUSE: self-test: add's argv shape wrong`

The two approval-step `HEAD_MOVED` stops (carried approval, mandate approval) are the same one-token class marker as `land`'s and are not separately driven by a check; a survivor there leaves that skip unre-admittable, today's behaviour.

## Null control

At origin/main ac9045c2 `merge_train.py --self-test` prints `841 checks, 0 failed`; at the head `850 checks, 0 failed` (the eight new checks plus the TOOLS row `the train's review_carry script is in the tree`); at c2e71e7c, before the last two checks, a sorted diff of the two outputs' check lines showed only the seven then added and none changed. Within the new checks, the nulls: a skip with no class (a real red) at the same verdict stays `ALREADY` with no live read and no `review_carry.py` call; a READMIT_ON_GREEN skip whose live head reads RED (1) or WAIT (3), or whose verdict answers FRESH-REVIEW (1) or cannot decide (2), is `ADD REFUSED #9 readmit:` naming the live head, nothing spooled; a TIMEOUT skip re-added at a new verdict is admitted as before, with no re-read; `HeadRed` over `[GATE]` and over `[GATE, "TIMEOUT"]` carries no class; `add` without `--only` still joins the ready set to the first batch (carry 14).

## Figures

- merge_train self-test at the head: `python3 tools/audit/seat/merge_train.py --self-test` -> 850 checks, 0 failed (at origin/main ac9045c2: 841, 0 failed).
- train.sh self-test: `bash tools/audit/seat/train.sh --self-test` -> ok.
- gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 2 script(s) run` (`tests/doc_claims.py`, `tests/entities.py`), both run green with `PYTHONPATH=tests/hastub`.
- structure ratchet: `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED.
- architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` -> `Architecture score: dS +0.0000 NULL`.
- the skip seams, enumerated by `grep -n 'Stop("approve", "head moved\|raise HeadRed(\|"TIMEOUT" in red' tools/audit/seat/merge_train.py` over production lines (before `def _self_test`): the three `Stop("approve", "head moved...")` sites -> closed here (`HEAD_MOVED`); the two `raise HeadRed(` sites (`at_head`, `admit`) -> closed here (the class is set in `HeadRed` itself); `settle`'s `"TIMEOUT" in red` -> a proof-level `Stop("proof", ...)` that stops the batch, not a per-entry skip, so no same-verdict record exists to re-admit, left alone. `MainMoved` already carried `MAIN_MOVED`.
- the finder's harness: none exists; the group is a proposal measured on train 2's log, not an audit finding. `_skip_readmit_self_test` drives the five PRs' shape (a TIMEOUT, MAIN-MOVED or HEAD-MOVED skip re-added at the same verdict) at both ends: refused at origin/main (the test-first commit's FAIL lines above), admitted at the head.

- diff mutants: `PREPR_SKIP_CLOSURES=1 MUTANT_IN_PLACE=1 MUTANT_CMD="python3 tools/audit/seat/merge_train.py --self-test" bash tools/pr/prepr.sh <body>` at c2e71e7c -> 14 SURVIVED of the first 40 mutants on added lines: 6 in `readmit_refusal`/`live_classify`, killed at 5135ba52 (each re-applied by hand above, each now FAILs a check); 8 in self-test code, dispositioned under `## Unpinned sites`. The same command at 5135ba52 -> `PRE-PR: 5135ba52... rc=0`, 8 SURVIVED, exactly those 8 (the registration and the seven fixture constants), none in production code.

## Unpinned sites

The 8 survivors in self-test code, read from prepr's log at c2e71e7c (line numbers at that commit): the `_skip_readmit_self_test(check)` registration in `_self_test` (CALL_DEL), and seven CONST_SWAPs inside `_skip_readmit_self_test`'s fixtures (`V7` length, the stub `run`'s return codes for `gh pr view` and other argv, the stub's CARRY text, `Train(..., min_runs)`, the drain fixture's `pr` and `next`). None is a production line: a mutant there changes what the self-test feeds the train, not what the train does, so no production check can kill it; the registration's deletion is caught by the check count (850 at the head against 842 without it), which no instrument reads. Disposition: self-test scaffolding, no killing check owed; no ledger triage written, since `tests/mutation_ledger/survivor_triage/` holds per-module files for `custom_components/` only.

## Red checks

none

## Forward-carry

none

## Friction

none
