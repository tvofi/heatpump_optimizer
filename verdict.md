Fix review: merge 434213ade270b7debbd299681e2586416c6ec64f

bus-nonce: 0bd1d0b8358aeffbcc6dedba6dd1a445
pending-ci: gate

## Scope

Round 6. This is a delta review over c17c11af72a8af22fc19e5cd7360bf8adf0acabe, whose verdict blocked only on `merge-conflict` in `tools/audit/seat/tick_loop.sh`. `review_carry.py c17c11af72 434213ade2` printed `FRESH-REVIEW`, so this review covers the delta. The PR's own part of the delta is `tools/audit/seat/tick_loop.sh` (+11/-2) and `dev/audit/harnesses/r10_tick_selftest_checkout.sh` (+10/-5). Everything else is main's own commits. No `custom_components/` line is in the PR's three-dot diff, so the scope does not widen. `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched three-dot (`ev/structure_checks.txt`).

## Findings

none

## Evidence

- **Head.** I measured 434213ade270b7debbd299681e2586416c6ec64f (`ev/HEAD.txt`) from a detached worktree. At verdict time `git ls-remote` still prints it as the branch tip (`ev/head_live.txt`). It is the head the body names. bab56d8017, the commit the body measured, is an ancestor of it. Between bab56d8017 and the head the three PR files have no diff.
- **The previous block is resolved.** `git merge-tree --write-tree origin/main 434213ade2` exits 0 against origin/main e28a310d7d (`ev/merge_tree.txt`); the PR reports `mergeable_state: blocked`, not `dirty`.
  - The resolution follows the direction of the previous verdict: no `--self-test` arm runs rows. `grep -- '--self-test)'` matches only lines 66 (the `env -i` re-exec) and 67 (the refusal).
  - Main's bound from 38aee2235a now sits on the `--self-test-rows` entry at line 72. It runs after the `env -i` re-exec, so `PR_BOUND` is set by `pr_bounded` inside the cleaned process and does not depend on a caller variable that `env -i` would drop.
  - `pr_bounded` is `exec python3 -I ...` (pr_args.sh:384-386). If it returns, or the `.` of `pr_args.sh` fails, the entry prints its refusal and exits 1.
  - Main's line 372 clauses (guard, source, `pr_bounded tick_loop`) are all on line 72. Its `tick_loop_self_test; exit` arm moves to the branch's own line 503 `--self-test-rows)` arm. This is the union the body describes (`ev/structure_checks.txt`).
- **Harness arms at the head**, each a scratch copy that is not a checkout (`ev/harness_arms.txt`):
  - `whole: 42 checks, 0 failed rc=0`
  - `envi`: the line-67 refusal, rc=1
  - `bound: 1 failed` (the new bound row)
  - `failopen: 2 failed` (fail closed func and bashenv)
  - `carry: 1 failed` and `pathfirst: 1 failed` (the poison row)
  - `pipefail`: several nested FAILs, rc 1
  - Every row of the body's round-6 mutation table reproduces.
- **The channels arm at the head**:
  - fn-all, bashenv-all, env, ifs, opts, path and shellopts-posix each read `42 checks, 0 failed`, with fn-calls=0 and victim-refs=0.
  - fn-exec is refused at line 67 (rc 1).
  - posix exits rc 2 on the special-builtin error.
  - noexec reads rc 0 with fn-calls=0.
  - The null controls read fn 4, bashenv 4, env 1 and path 1, over a corpus of 85 names.
  - The round-4 attack class stays closed after the merge.
- **The five shape arms** (branch, detached, gitdir, shim, level) each read `31 checks, 0 failed HEAD-UNMOVED`.
- **My own mutants on the new bound line** (not the fixer's arms). I deleted the `exit 1` after the bound's refusal message:
  - With `pr_args.sh` absent, the rows ran unbounded, and the bound row plus the offline_spy row failed: `42 checks, 2 failed`, rc 1 (`ev/own_mutant_noexit.txt`). The bound fails closed through the row even when the explicit exit is gone.
  - With `pr_args.sh` present, the run read `42 checks, 0 failed`, rc 0 (`ev/own_mutant_noexit_withpr.txt`). That mutant is equivalent where the bound takes, because `pr_bounded` execs and never reaches the exit. It is not a survivor of the fix's own claim.
- **The poison row's label at this head counts 93 names.** The body's "90 at this head" sits under the section headed "Round 5's figures, at 12ead5feae", so it is a dated figure, and its round-6 sections state no count. I did not re-derive 90 at 12ead5feae.
- **bash -n**: rc 0 on both shell files (`ev/bash_n.txt`).
- **CI**: `merge_train.py classify 434213ade2 --pr 3520` read `WAIT 434213ade270b7debbd299681e2586416c6ec64f pending: gate red: none` on every run from 13:31 to 14:02 UTC, about 30 minutes (`ev/classify.log`). The `rc=0` on that log's last line is the `date` substitution's status, not classify's, because the line reads the same WAIT.
  - No red was read, so no `## Red checks` answer is owed at this head. The owed set is in `ev/owed_reds.txt`.
  - The body's answer for `tests / briefs` at c17c11af72 concerns an earlier head. I did not re-check it.
  - The review packet's `REFUSE introduced-red: unreadable` came from `instrument-self-tests` being in progress at render time. Classify decides.
- **Not re-derived**:
  - the body's `real 1m41.178s` (a host timing)
  - `ci_predict.py`, `structure.py`, `doc_claims.py` (348) and `entities.py` (2711), which the scoped gate runs in CI
  - the main-side `30 checks` at 5288db5dad
  - the reviewer-driver re-run at bab56d8017. The channels arm drives the same `exec` shadow, func and bashenv, at this head.
