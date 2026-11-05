Fix review: merge 5e9a782b677a99dde28a147636986b82c17834bc

bus-nonce: 2293cc683db190b9760e674dae80ecb4

## Scope

Delta fix review of #3205 (R10-HOTFIX-GATE-STALE-JOBS), after verdict/3205 blocked 6e1e8023d body-stale. The body calls this "repair round 3", which is not the fourth, so `fixer.md`'s re-cut rule does not apply. Measured at head `5e9a782b677a99dde28a147636986b82c17834bc`, from a detached worktree at that SHA. The base is the PR's `af941ad4a`. `git diff <merge-base>...origin/main -- dev/governance/roles/` was empty when the review started. At the final read, main `c0b082bc4` changes only `nudge.md` under roles, which does not touch `fix-review.md`.

## Evidence

- Self-test at the head: `python3 -I tools/ci/gate.py --self-test` prints `gate self-test: 49 checks, 0 failed` (ev/selftest_head.txt). At bc806747b it prints `48 checks, 0 failed` (ev/selftest_bc806747.txt). Both match the body.
- Mutation proof, re-taken with my own one-line replacements and the tree restored after each (ev/mutants.txt). Each mutant's failed-check count matches the body: lag_bound made `if True:` (return 0), 8 failed. `all(` to `any(`, 1. `GATE_ABSENT_MAX_S = GATE_WAIT_MAX_S`, 1. `listed_unfinished = False`, 2. `listed_unfinished = True`, 2. `bound = 0` in judge(), 14. My own extra mutants were all killed too: lag_bound always returning GATE_WAIT_MAX_S, 2 failed; OWN_PENDING's text changed, 2; the cleared-lag note dropped (`lagged = lagged or why` made `pass`), 1. Null control: the unmutated tree, `49 checks, 0 failed`, and `git status` was clean after the run.
- Finder's harness: the RCA seat's `dev/audit/harnesses/r10_gate_stale_jobs/harness.py` from `9b0df6105c67a009bce09feea9f4dffe8079a86a` (handoff-wip/r10-rca-gate-stale). Its sha1 `7527a4832039d125950b8f07e1b2d931a6ef874c` equals the body's. I ran it with `python3 -I harness.py <tree>`, each tree from `git archive <sha> tools/ci .github/workflows`. RESULT: base af941ad4a `mismatches 4 of 9` rc 1; origin/main a45cf7f50 `mismatches 4 of 9` rc 1; head 5e9a782b6 `mismatches 0 of 9` rc 0 (ev/harness_*.txt). Per shape, the head's waits are 300, 180, 720, 180, 360, 60, 720, 0 and 0 s, the same as the body's table. Both fresh-listing nulls wait 0 s at every tree.
- Core harness at the head: `r10_ci_gate_core.py replay` prints `GATE-REPLAY2 rc 0`, output IDENTICAL to `1371a0a6:measure/rev/gate_replay2.txt`. `mutants` prints `RESULT mutants=16 survivors=0`. `sim` prints `GATE-SIM rc 0`, output IDENTICAL to `1371a0a6:measure/rev/gate_sim.txt`. My first `sim` run was killed by my own 220 s timeout; the re-run with no timeout gave this result (ev/core_*.txt).
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`. The diff moves no budget, golden fixture, claim file, `VERSION`, manifest version or notes heading (ev/version_untouched.txt is an empty stat).
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 against a45cf7f50 and against c0b082bc4. Since af941ad4a, main changes nothing under `tools/ci` or in `ci.yml` (ev/merge_tree*.txt).
- Head section: the head's parents are 0b66b88c2 and af941ad4a. 0b66b88c2 merges 5e1e16a64. 5e1e16a64 is d2bfb0738 (6e1e8023d merged with origin/main 2a9cd3476) plus the ABSENT-pin commit. 5e1e16a64 and the head have the same `tools/ci/gate.py` (ev/ancestry.txt). This matches the body.
- Body checks the brief named:
  - The body describes `lag_bound()` and 49 checks, which is what the head prints.
  - The mutation proof mutates lag_bound, `listed_unfinished` (OWN_PENDING's prelude path) and GATE_ABSENT_MAX_S, with a null control.
  - The alternatives section now states that the head adds `GATE_ABSENT_MAX_S`. That is true: see the diff and the self-test pin "the ABSENT bound is shorter than the pending bound, and pinned to two polls".
  - The three roster carries, e67341cc, e350d851 and d0916ca4, are on `handoff/audit-r10-roster` f772f5542 (group R10-HOTFIX-GATE-STALE-JOBS) and each is answered in the body. e67341cc is closed by the diff (harness 0 of 9 above). e350d851 and d0916ca4 are forwarded under `## Forward-carry` with `Carry: R10-FLY-GH-READ-RETRY`. That group is in stage `carries-open` on the roster, so it is a live destination. The packet's carry_audit at the head: `2 routed, 0 unrouted, 0 bad destination(s)`.
- Class (step 6): the class is gate.py's own-run reads of a lagging jobs listing. Both other readers of the same lag are dispositioned in the body (`codescan_wait.py` own-run path, `pr-contract.yml` red list), as forward-carries. No third reader was examined beyond those the RCA names.
- Not re-derived: the body's "At round 1's production code with round 2's checks: `47 checks, 4 failed`". That needs a hand-spliced tree, and I did not build one. Every other figure in the body was re-derived above.
- Not tested: the body's claim that the `src is not me` conditionals in `gate()` are equivalent. It is a code-reading claim and has no figure attached.
- CI on this head (step 11): `python3 tools/audit/seat/merge_train.py classify 5e9a782b677a99dde28a147636986b82c17834bc --pr 3205` exited 0: `GREEN 5e9a782b677a99dde28a147636986b82c17834bc pending: none red: none` (ev/classify.txt). The head was re-read on the remote right before this verdict and is unchanged.
- Red checks: `tests / nightly-status` concluded failure on run 41931941759. It is in no `REQUIRED` class and it reads main's nightly lane; this diff, which touches only `tools/ci/gate.py` and a delivery row, does not reach what it reads. The body's `## Red checks` answers it. No other check on this head concluded red at my last read.

## Findings

- Follow-up: `tools/ci/codescan_wait.py` `source()`, own-run path. A stale upload-step row can read as "stood down", leaving that leg unread (fail-open). It is read from the code and unmeasured; this PR forwards it, it does not settle it. Carry: R10-FLY-GH-READ-RETRY
- Follow-up: `.github/workflows/pr-contract.yml`, "List the red checks at this head". It keeps only completed failures, so a red that is still lagging can be left off what the body must answer. It is read from the code and unmeasured; forwarded, not settled. Carry: R10-FLY-GH-READ-RETRY
- Residual: the finder's harness `dev/audit/harnesses/r10_gate_stale_jobs/harness.py` is not in the tree at this head. It lives on handoff-wip/r10-rca-gate-stale `9b0df6105`, and the body discloses that the RCA seat lands it (step 9). Carry: dismissed: landing belongs to the RCA seat's own handoff, not this fix; disclosed in the body and hash-verified here

## Friction

- The frugal plugin's inline-search guard refused a Monitor wait and a background Bash wait as "search ops". The CI wait was moved to a background scout, and then to a plain background loop after a container restart. No refusal was worked around.
