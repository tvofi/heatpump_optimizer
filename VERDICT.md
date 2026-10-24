Fix review: merge f4458d2160d8f9f6b10d7fb3d657140201cd1d31

bus-nonce: cbde43b0474c8ce5f8ec6349dfcebdc8

## Summary

Round 1 (no earlier review/2692 or probe/rev-2692 ref on origin). Reviewed PR #2692 (R10-REPLAY-SCOPED, part of #2273) at head `f4458d2160d8f9f6b10d7fb3d657140201cd1d31`, merge base `e8a08cf9efefc96c36e79efa7459562e27007b54`; authored code head `799830bb54ecf6556f988e674150306968f471b9` over `50af6174f53c0f9bec3f705c3a4bb99615f71acc`. `git diff <merge-base>...origin/main -- dev/governance/roles/` was read before step 1. The head was re-read before returning and is unchanged on `fix/r10-replay-scoped`.

The change does what the owner asked ("Hard no, only when relevant"). A pull request runs `tests/replay.py` only when its diff reaches `COST_FILES`, `optimizer.py`, `tests/replay.py` or a `tests/replay/*.json` fixture. The reach is read from the lane's own `COST_FILES` literal and fails closed. Nightly stays the full run, and no blanket per-PR lane is offered.

## Findings

- The finding has no committed finder's harness: it is owner-reported (#2273, owner answer 3, 2026-10-15). The pins in `tests/entities.py` are the fixer's own instrument, and the PR discloses them as the fixer's. My reach measurement (`ev/reach-100.txt`) is mine: the PR's own rule replayed over 100 merges. No judge-designed harness is owed for an owner requirement with no on-device item. Carry: dismissed: owner requirement, no finder harness exists to run at both ends; disclosed here per fix-review.md step 9.
- The diagnostic text of the check `replay reach: a lane source naming no COST_FILES runs the lane, never skips it` always prints the `source='X = 1'` arm, whichever conjunct failed. Under my mutant M4 (optimizer.py dropped) it went red showing `(True, ...)`, which points away from the cause. The check still goes red correctly, so this costs only a little debugging time. Carry: dismissed: cosmetic message, the check's verdict is right under every mutant tried.
- `replay_cost_files` catches `OSError`, `SyntaxError` and `ValueError`. A non-iterable literal such as `COST_FILES = 5` raises `TypeError` from `tuple(...)`, which is not caught, so `closure-scope` would exit red rather than decide. That fails loud, not open. It also needs an edit to `tests/replay.py`, which `entities.py` already pins equal to the imported tuple. Carry: dismissed: far-fetched path, fails loud, and the existing pin catches it first.

## Evidence

- RESULT mutation M1 (`replay_reach` keeps fixtures only): entities 2 replay checks FAIL (missed coordinator.py, sensor.py, ...; fail-closed arm), rc=1. `ev/entities-m1.txt`
- RESULT mutation M2 (closure-scope `replay-reach ... >> "$GITHUB_OUTPUT"` line deleted): `the timed replay runs on a pull request whose diff reaches it...` FAIL, rc=1. `ev/entities-m2.txt`
- RESULT mutation M3 (fail-closed arm returns False): `replay reach: a lane source naming no COST_FILES runs the lane` FAIL, rc=1. `ev/entities-m3.txt`
- RESULT mutation M4 (mine, `optimizer.py` dropped from the reach): `missed ['custom_components/heatpump_optimizer/optimizer.py']` FAIL, rc=1. `ev/entities-m4.txt`. All four mutants are in `ev/mutants.diff`; none survived.
- RESULT entities at head: 2 of 2429 ENTITY CHECKS FAILED, the two named in the body as box-local (`gate-sweep.yml: on CI's completion...`, `graders-head-copy's delivery_status step...`), and all four replay checks ok. CI's `tests / fast (3.14)` at this head is green. `ev/entities-head.txt`
- RESULT reach over main's last 100 first-parent merges up to `50af6174f`: replay=true on 7 of 100 (#2675, #2620, #2632, #2647, #2612, #2563, #2572). That re-derives the body's figure and its PR list exactly. Each hit names a cost file, `optimizer.py` or `tests/replay.py`. Null control: a blanket per-PR lane fires 100 of 100. `ev/reach-100.txt`
- RESULT null control `HPO_JOB_GRADES: nothing` removed from the `replay` job: `codeowners_gap.py --check` gives `uncovered_files=3` with REFUSED. At head it gives `uncovered_files=0`. Re-derived. `ev/nullcontrol-grades.txt`
- RESULT CLI: `replay-reach` on `tests/replay.py` prints `replay=true`; on an empty list it prints `replay=false`, with the reason on stderr. `ev/cli.txt`
- Re-run at head: `closure.py selftest` ALL 117 PASSED; `structure.py` STRUCTURE RATCHET PASSED; `rules_sync.mjs --check` ok; `env_drift.py --claims-only` ok.
- Claims (step 4): the diff touches no golden or claim file, so there is no drift to claim. Step 5: `VERSION`, the manifest version and `RELEASE_NOTES.md` are untouched (three-dot diff empty; CI prepr "no version edit").
- Wiring end to end in CI: `closure-scope` printed `the diff reaches the timed replay lane: tests/replay.py` and set `replay`. The `replay` job ran and passed (93 checks, 45.3 s). Its install line, Python 3.13, `PYTHONPATH` and command are identical to nightly `slow`'s replay step. `ev/ci.txt`
- Class (step 6): the issue states one seam, the owner's reach list. The body names no enumeration rule because the class is that one list, plus fixtures, which widen the reach. Neither the diff nor the alternatives leave a seam of that list unhandled.
- Merge (step 13): `git merge-tree --write-tree origin/main <head>` against origin/main `2636ce9e9378addc393b749160be0bd928af4f90` gives rc=0 and no conflict. `ev/merge-tree.txt`
- Red checks (step 11): `tests / fast (3.14)` was red at the previous head (entities, 407 s). The body names it and answers it (a py-spy timing probe, not this diff), and it is green at this head with no code change since. I did not re-derive the `hb:positive_control` detail from that job's log because the log tail did not reach it. One pr-contract run on this head (edit run 40091420502) was red at `codescan_wait.py` before CodeQL concluded. A later pr-contract (code run, 12:23:44Z) started after that red and after the head's other workflows had concluded, checked the body, and passed. `ev/ci.txt`
- Not re-derived: the body's local `replay lane wall time 67.6 s` (CI shows 45.3 s at this head), archscore `dS +0.0000` (CI `arch-score` green), `doc_claims.py` 203 checks, and `policy_lint` 50 files. All are cited from CI or the body, not measured by me.
- Forward-carry (step 10): the body says `none`, and nothing in this change binds a later stage.
- Head (steps 7, 12): the body's `## Head` names `f4458d2160d8f9f6b10d7fb3d657140201cd1d31`, the head I measured. It is still the head of `fix/r10-replay-scoped` at return.
