Fix review: merge a2e33e46c09fba23edaed5897351868525049da2

bus-nonce: 839b82603c7655af2c6a5663fcf86daa
pending-ci: gate

Round 1 (first review of this PR; review scope full).

## Evidence

- Head reviewed: a2e33e46c09fba23edaed5897351868525049da2, the PR body's stated head; merge base 921214bf42. Worktree detached at the head. Role files: `git diff <base>...origin/main -- dev/governance/roles/` is non-empty, so the contract was read from main (6aa7ddc712) via `role_pack.py render fix-review`.
- Merge with main: `git merge-tree --write-tree origin/main a2e33e46c0` at origin/main 6aa7ddc712 exits 0, tree 60147e8728, stderr `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt). No conflict.
- Step 1, mutation proof, re-run at the head (ev/head-runs.txt): `python3 dev/audit/harnesses/r10_open_driver_mutants.py` prints `RESULT mutants=33`, `RESULT survived=0`, the nine new plants (M-stale-env, M-stale-key, M-stale-count, M-stale-unread, M-stale-notice, M-retry-nowrite, M-retry-refuse, M-retry-namesake, M-unlisted) each `verdict=killed`; `python3 dev/audit/harnesses/r11_main_cancel_mutants.py` prints M0 `failed=0 verdict=null-ok`, all eleven plants killed, `RESULT mutants=11`, `RESULT survived=0`. Both match the body.
- Own targeted mutants, outside the PR's harnesses (ev/own-mutants.txt), each one exact replacement restored afterwards, worktree clean: killed — open_driver `tools = ""` (3 rows red: stale (i), (ii), (v) replay), stale entry `"next": 0` (count-and-backoff row), retry `startswith` -> `True` (2 rows), read-back check disabled (1 row), STALE_RE without the `behind ` anchor (480-spelling row), cancel_superseded VERDICTS minus `timed_out` (1 row). Survived — two in `main_arm`, carried under Findings.
- Figures re-derived at the head: `open_driver self-test: 114 checks, 0 failed`; `cancel_superseded self-test: 76 checks, 0 failed`; `ALL 115 HARNESS HEADER CHECKS PASSED` and `STRUCTURE RATCHET PASSED` (ev/head-runs.txt). Figures at 31117b1029 (carry 0, carry 4, ci_ratchet, gate.py self-tests) and the 175e8bb579 red were not re-taken here: they are the base's and an earlier head's, and the head's own runs above supersede what this verdict rests on.
- Step 2/9, finder's harness: the review packet names none. The group's items are process carries (P627, P678, P658) with acceptance rows (i)-(v) in the self-tests and the fixer-built mutant harnesses; disclosed by the body as the fixer's. The design note a37706d599's acceptance table covers its own p1 seams (R3 mirror etc.), not carries 1-3, so there is no design-trace item this cut owes.
- Step 4, claims: the diff touches no golden fixture and neither claim file. Step 5: `VERSION`, the manifest and `RELEASE_NOTES.md` are not in the diff.
- Step 14: `tests/closures.json` moves by one `inert_reads` entry, the new harness `dev/audit/harnesses/r11_main_cancel_mutants.py`; earned by the new file. No budget file moves.
- Step 6, the class: carry 2's classifier is the one seam (`pr_refuse`'s line for `pr_tools_fresh`); carry 3's `run`/`sweep` null row pins that no other arm selects a main run. No enumeration rule is named and none is owed for these single-seam carries.
- Step 16: no actuator path; no `custom_components/` change.
- Step 11: the reds at 175e8bb579 (`tests / fast (3.14)`, `pr-contract`, `gate`) are answered in the body's `## Red checks`, naming the cheaper detector. CI at this head: see the CI line below.
- CI at this head: `merge_train.py classify a2e33e46c09fba23edaed5897351868525049da2 --pr 3645` printed `WAIT a2e33e46c09fba23edaed5897351868525049da2 pending: gate red: none` (rc 3) on every run from 03:53Z to 04:23Z (ev/classify-log.txt); no red at this head, so no owed red is answered here. The packet's digest read `gate` as failure at render; classify decides and reads it pending.
- Step 12, head re-read before return: the PR head moved to ffe0323ab113bd950886aea190bed6289dd06100 (`ci: merge main`, parents a2e33e46c0 and main's 56ce2f695b). `tools/audit/seat/review_carry.py a2e33e46c0 ffe0323ab1` at origin/main 5aaf9c112f prints `review_carry: CARRY` (0 of 1 branch-only commits non-merge; ev/review-carry.txt). The three-dot own diff at the new head equals the reviewed one except `tests/closures.json`'s ledger-merged context (main's `r11_plan_page_inventory.py` entry); the same nine files (ev/own-diff-at-ffe0323ab1.txt). Every number above was taken at a2e33e46c0 and carries; none was re-taken at ffe0323ab1. CI must be read at whichever head the relay posts to.

## Findings

- Follow-up (non-blocking test gap): `cancel_superseded.py main_arm` derives `full=len(runs) >= PAGE`, but no self-test row drives a full-page listing end to end; mutants `full=len(runs) > PAGE` and `full=False` both survive (`cancel_superseded self-test: 76 checks, 0 failed`). `main_plan`'s `full` branch is pinned (M-full), only its wiring is not. Practical reach is small: the refusal can bite only when an active run sits among the three oldest of a 100-run page, but the docstring's "a row that reaches the old end of a full listing ... is refused" is unpinned at the arm. A row with a 100-run stub listing closes it. Carry: R11-PRE-TOOLCHAIN-PIN
- Follow-up (non-blocking test gap): `main_arm`'s unreadable-listing branch `continue` can become `return 0` and survive, because the only unreadable workflow in the fixture (`tests.yml`) is the last one listed; an unreadable first workflow would silently skip the rest. The failure direction is safe (cancels nothing), so not a block; putting the unreadable workflow first in the dry-run row pins it. Carry: R11-PRE-TOOLCHAIN-PIN

## Notes

- Note: design-cut: the PR builds the dispatch's cut (carries 0-4) instead of the approved design's p1 seam cut; disclosed in the body, the unbuilt p1 items carried to R11-PRE-TOOLCHAIN-PIN (item tp1). The code built does not depart from the design's carry-2 rule (driver's own checkout HEAD), so this is not an architecture block.
