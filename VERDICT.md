Fix review: merge c94061668cf61ee6bec00aaee7c5ab9942b0e37f

bus-nonce: b11d44a5cdaca59b185a502559fc7be7
pending-ci: gate

## Review

This is round 4, a later round over the reviewed head c9aed94c0e5ae5fe7cd99e538aaecdfdf07f85c7. Counted by verdicts it is the fifth review. The PR answers the fourth verdict with the re-cut `fixer.md` owes, and the body's `## Re-cut` section is present. `review_carry.py c9aed94c0 c94061668` prints FRESH-REVIEW, and the packet's `## Review scope` reads delta.

- The delta is c9aed94c → a merge of origin/main a7628041 → 76b902b9 → c94061668, which merges 76b902b9. Every hunk of `git diff c9aed94c0 c94061668 -- tools/audit/worktree_gc.sh` sits in the self-test, at old lines 214-490. `cwd_inside` (line 719) and `cwd_free` (line 747) are byte-identical to the reviewed head. The PR changes no production (`custom_components/`) code, so the scope is not widened.
- The round-3 block (flaky-harness) is resolved. The zero-pid helper now sends no signal (`sh -c 'case $$ in *0*) exec sleep 600 ;; esac' & ... wait "$ZPID"`). In 25 consecutive runs, the unmodified self-test at the head read `160 checks, 0 failed` every time (`25 of 25 green`). In the same loop, run concurrently on the same container, c9aed94c read `11 of 25 green`, with the other 14 runs at `100 failed`/`104 failed`.
- The Kept and Dropped claims hold. Each dropped fixture's mutants are still killed by the unmodified harness at the head:
  - `argvco`: `v3-argvterm-empty`, `v2-argvterm-empty` and `v1-argvterm` are KILLED.
  - `pidfuse`: `v1-pid`, `v1-killcheck` and the train.pid-loop drop (`r4-trainpid`, the body's `recut-trainpid`) are KILLED.
  - `nopsbin`: `v2-nopsbin` and `v1-psunread`/`v3-psunread` are KILLED.
- The check count 167 → 160 matches the seven `st` calls removed in the diff (2 + 2 + 3).

## Findings

- Residual: `[ -n "$out" ] || return 2` in `cwd_inside` survives its deletion mutant (`v3-lsofcwd-empty`, `v2-lsofcwd-empty` SURVIVED). The line is a pre-existing line on main, and the body dispositions it under `## Unpinned sites`. Carry: dismissed: pre-existing line on main, not added or changed by this PR, and out of its mutation scope

## Evidence

- Head reviewed: c94061668cf61ee6bec00aaee7c5ab9942b0e37f (ev/HEAD.txt). It is the PR head in the GitHub API, and the body's `## Head` names it (merging the authored head 76b902b9).
- FIRST STEP, the self-test loop at both ends (ev/loop25-head.txt, ev/loop25-c9aed94c.txt; the loop is in ev/loop.sh):
  - RESULT head c94061668: 25 of 25 green, every line `worktree_gc self-test: 160 checks, 0 failed`.
  - RESULT c9aed94c: 11 of 25 green, with 10 runs at `167 checks, 100 failed` and 4 at `167 checks, 104 failed`. The body's own figure at c9aed94c is 13 of 25. Mine is a different draw of the same race.
- Mutants, run with my own spec (ev/spec.json, built by ev/mkspec_r4.py). Its parts:
  - `v3-*`: probe/rev-3423-33f72110's ev/mkspec.py, unchanged.
  - `v2-*`: probe/rev-3423-23bb0265's ev/mutants.py `M` table.
  - `v1-*`: rebuilt from probe/rev-3423-468a0851's prose.
  - `r4-*`: my own four.
  
  The command was `mutant_run.py --spec ev/spec.json --cmd 'bash tools/audit/worktree_gc.sh --self-test'` with the unmodified harness and the default git-archive copy (ev/mutants.txt). RESULT: `SURVIVED NULL`, 39 KILLED, 5 SURVIVED besides NULL (44 entries; `grep -c ^KILLED` 39, `grep -c ^SURVIVED` 6 with NULL) (`v3-pidguard-restored`, `v3-pidempty-unquoted`, `v3-lsofcwd-empty`, `v3-trap-zpid-unguarded`, `v2-lsofcwd-empty`).
- Survivors versus the body: the survivors are exactly the body's survivors, and every mutant name the body quotes as KILLED is KILLED here. The body's `v1-heldway`, `v1-lsofall`, `v1-argvterm` and `v1-nopsbin-replacement` are spelled by my rebuild as `v1-heldway`, `v1-lsofall`, `v1-argvterm` and `v2-nopsbin`, the same `|| return 2` drop on the ps read.
- Dispositions of the survivors:
  - `pidguard-restored` and `pidempty-unquoted` are equivalent, as the round-3 verdict showed (`kill -0 ""` fails).
  - `trap-zpid-unguarded` is cleanup only.
  - `lsofcwd-empty` is carried above.
- Reviewer-added mutants, each KILLED:
  - `r4-trainpid` drops train.pid from the pidfile loop.
  - `r4-openfile-slash` drops the open-file `/`-prefix disjunct.
  - `r4-cwd-slash` drops the cwd `/`-prefix disjunct.
  - `r4-pidfile-head` makes the pidfile read empty.
- Minimal repro of the trap plus the helper loop (ev/zpid-repro-old.sh is the round-3 reviewer's script; ev/zpid-repro-new.sh changes only the loop line to the head's and adds a `/proc/$ZPID/comm` read). 30 runs each (ev/zpid-repro-summary.txt):
  - RESULT old: multi-iteration=20 fixture-NO=20 trap-runs>0=20.
  - RESULT new: multi-iteration=22 fixture-NO=0 trap-runs>0=0 zpid-comm=sleep 30/30.
  
  The body's 21/21 and 21/0/0 figures are another draw of the same shape.
- Body figures re-derived at the head:
  - `tests/closure.py select` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (ev/closure-select.txt).
  - `tests/structure.py` prints `STRUCTURE RATCHET PASSED`, rc 0 (ev/structure.txt).
  - The mutant count of 43 entries / 38 KILLED / 6 SURVIVED is the fixer's own spec, which is not committed. I re-derived it with my own 44-entry spec, and every name the two specs share agrees.
- `git merge-tree --write-tree origin/main c94061668` rc 0 at origin/main f24d107bd (ev/merge-tree.txt): merges cleanly.
- Role drift: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Harness (step 9): the finding has no separate finder's harness. The in-tree `--self-test` is the pin harness, as in earlier rounds.
- The three-dot diff touches only `tools/audit/worktree_gc.sh` and `dev/programme/delivery/3423.md`. VERSION, the manifest, the notes heading, the claim files and the budgets are untouched.
- Red checks: `merge_train.py owed-reds` is in ev/owed-reds.txt. The packet's `red-unanswered: gate` is an earlier gate run at this head. `classify` reads WAIT (pending: gate, red: none), so no red is owed. The `tests / nightly-status` failure is not in the owed set. The CI state is in ev/classify.txt: classify read WAIT (pending: gate, red: none) from 08:23 to 08:55 UTC, so the verdict carries `pending-ci: gate`.
