Fix review: merge 154f99d0c9ab359aef75c7b676d075de21141363

bus-nonce: 63eacef35b801d269213154c4b12ccea

## Findings

- The nightly re-run 40835853528 on main (head 486e65c) and the head's `governance / instrument-self-tests` and `prelude` runs were still in progress when I read them, so I could not confirm their outcome; the verdict does not depend on them, since the rows touch no code. Carry: R10-FLY-NIGHTLY-HB | #0 | O0 | dismissed: the merge train re-reads the required checks at the head before merging; the nightly control is owned by R10-FLY-NIGHTLY-HB.

## Evidence

- Round 1. Fix-review contract read from the tree at the head; `git diff merge-base...origin/main -- dev/governance/roles/` is empty (current).
- `record_row.py --automerge-check --pr 2944 --head 154f99d0c9ab359aef75c7b676d075de21141363`: `AUTOMERGE OK #2944 at 154f99d...`, exit 0 (ev/automerge.txt).
- Diff scope (three-dot): 8 files, every path `dev/programme/delivery/<N>.md` (2887, 2914, 2915, 2916, 2919, 2936, 2937 rewritten; 2944 new). No other path.
- Merged state: each of #2887, #2914, #2915, #2916, #2919, #2936, #2937 has a merge commit on origin/main whose short SHA equals its row (bb48cf6, 9071062, 51cd666, 0b17333, 994b3df, 486e65c, 78c0ac5); #2937 read back as merged by GitHub (merged_by tvofi). The row for #2944 itself is "open", correct for a pull request still open.
- `git merge-tree --write-tree origin/main HEAD` is clean; origin/main is still the base 486e65cbd, so the branch is not behind.
- Mutation proof and null control: n/a, a record-only diff with no production, test or check code; body states this and the diff confirms it.
- `tests/delivery_status.py` ok in the review packet's figure_lint; `carry_audit` at the head: 0 findings; no refusals or advisories.
- CI on this head, from the check-runs API: all concluded gate checks succeed except `tests / nightly-status` (failure). The body's `## Red checks` names it, says it grades main (last night's `nightly-ha (stable)` lane, `hb:positive_control` and `run:exit_status`), names the re-dispatch 40835853528 and the owning group R10-FLY-NIGHTLY-HB, and states no cheaper detector exists. It also answers `record`, `nightly-status`, `delivery-status`; `delivery-status` is green and `record` skipped on this head. The answer is present, so no root-cause block.
- VERSION, manifest version and notes heading untouched (diff has only delivery rows). Forward-carry: none, matching the body.
- Figures I could not re-derive: the nightly lane's 600 ms vs 5308.8 ms spin reading is from a lane log I did not open.
