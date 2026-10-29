Fix review: merge cf326bb3440f2d9bb49d0394ee7e75cd9e60b304

bus-nonce: d6a90ec015330dc3386ce996a3f92e4b

## Scope

Resolution-delta review (fix-review.md step 12, #1667): the prior merge verdict was at ceb41a60; the head since moved only by two first-parent merges of origin/main (8410878f merging ddc4f1fe = ceb41a60 + main 9071062b, then cf326bb merging main 51cd66673). No authored commit beyond those merges. Round: re-review of the resolution delta, not a new round. Roles diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read is current.

## Evidence

- RESULT main-delta: main changed `tools/audit/seat/INSTRUMENTS.md` between the old base b0b2d769 and the new base 51cd66673 in four hunks (ev/main-delta-INSTRUMENTS.diff): the `cloud_dispatch.py` `--publish`/pointer-event text, the `cloud_relay.sh` `ledger.py landed` text, and new entries `owed_unactioned.py`, `beatd.py`, `beatd_shims/git`. Main has not touched `tools/audit/seat/` since 51cd66673 (origin/main now 7685a4d9).
- RESULT placement: each of the three new entries is main's bullet verbatim in its own `instruments/` file under a `# name` title; their index lines sit in main's order (`owed_unactioned.py` between `orchestrator_tick.py` and `plan_audit.py`; `beatd.py`, `beatd_shims/git` after `heartbeat.sh`, before `train.sh`). The two changed entries carry main's text inside `cloud_dispatch.py.md` and `cloud_relay.sh.md` (ev/resolution-delta.diff).
- RESULT nothing lost or duplicated: for every file of the PR, the PR's own +/- lines against its merge base are identical at ceb41a60 and at the head except the six files above; INSTRUMENTS.md's added lines differ only by the three new index lines. A line census of main's INSTRUMENTS.md against head's index plus all 79 entry files: 1197 non-blank lines, 0 over-represented, 1 absent (`runs offline.`, the intro line the split itself reflowed, unchanged since ceb41a60). This census and the rebuild below are my own instruments, not a finder's harness; this PR's finding has no finder harness (packet: "Finder's harness: none named"), as at the prior verdict.
- RESULT read-back: rebuilding the flat guide from the head's index (each linked line replaced by its entry body minus the title) and diffing against main 51cd66673's INSTRUMENTS.md shows exactly the split's two intended additions, the index sentence and the `selftest_wiring.py` paragraph (ev/rebuild-vs-main.diff), matching the body's Head section.
- RESULT check: `selftest_wiring.py --check` at head exits 0, `101 self-testing, 101 wired, 0 unwired`, `0 index gap(s)`; `--self-test` `26 checks, 0 failed`. Mutants on the merged-in entries: dropping the `beatd.py` index line gives `UNINDEXED ... beatd.py.md`, rc 1; deleting `owed_unactioned.py.md` gives `MISSING ...`, rc 1; restored clean (ev/selftest_wiring.txt).
- RESULT figures: INSTRUMENTS.md `wc -c` 87231 at 9071062b0 and at 51cd66673, 12425 at ddc4f1fe7 and at the head; `grep -c '^- \`'` 79 at the base; 79 entry files and 79 index links at head. The seat tree is identical between ddc4f1fe7 and the head, so the body's figures taken at ddc4f1fe7 hold at cf326bb.
- RESULT merge: `git merge-tree --write-tree origin/main cf326bb` exits 0 against origin/main 7685a4d9 (ev/merge-tree.txt); no claim file or other conflict.
- RESULT untouched: VERSION, manifest, RELEASE_NOTES.md and tests/golden/ are not in the three-dot diff; no claim file changed, so step 4 has nothing to compare.
- RESULT head: the PR body's Head section names cf326bb3440f2d9bb49d0394ee7e75cd9e60b304, the head measured; the live PR head was still cf326bb at verdict time.
- RESULT CI on the head (ev/checks.txt): no run concluded failure; five runs were still in progress at read time (closures, coverage, instrument-self-tests, codeql python, one prelude). With no red check, step 11 owes no answer; the body's `## Red checks: none` agrees. The heavy runs are CI's to finish; the merge train gates on their conclusion.
- RESULT packet: rendered rc 0, `## Refusals none`, carry_audit and figure_lint clean at the head (ev/review-packet.md).

## Findings

none
