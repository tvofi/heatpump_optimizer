Fix review: merge f0f6b47f2c8f402e6d35b461c06760318576b01a

bus-nonce: b241498ea563008dae5e793dea2ce091
pending-ci: gate

Round: a delta round over the reviewed head dd5faa50c0a87aec310975128c18b172e052af3a, which merge verdict 32592495c782 named. That verdict settled the rest and is not redone here. review_carry prints FRESH-REVIEW only because d9ab65e9c97b is a hand resolution and not the automatic merge (`ev/review_carry.txt`). The scope is therefore the delta named in the packet's `## Review scope: delta` line.

## Findings

(none. The previous verdict left no open finding: its carry-missing items were cured at dd5faa50 and the earlier findings were carried there.)

## Evidence

- Separation: `git rev-list dd5faa50..f0f6b47f --not origin/main` returns three merges and no other commit. d9ab65e9c97b merges dd5faa50 with main c71d3f6e8983, 20c79e83a2bc brings d9ab65e9 into the branch, and f0f6b47f2c8f merges main 61afd4f2db10. The PR adds no change of its own beyond these resolutions.
- Clean merges: 20c79e83a2bc and f0f6b47f2c8f are byte-identical to `git merge-tree --write-tree` of their parents (0 diff lines, `ev/clean_merges.txt`).
- Hand resolution d9ab65e9c97b: the only conflict was `tools/audit/seat/cloud_dispatch.py`, one hunk in `dispatch_group`'s `args = dict(...)` (`ev/resolution_conflict.txt`). The diff from the conflicted tree to the resolution (`ev/resolution_vs_conflicted.diff`) only removes the markers and keeps both sides: the branch's `verdict = ()` designer block with `verdict=verdict`, and main's `brief=... + (f"\n{pline}\n" if pline else "")`. `pline` is assigned to "" before the call on every path. No logic changed beyond the union; the auto-merged `tests/entities.py` and `instruments/cloud_dispatch.py.md` match their automatic merge.
- Mutants at the head on the resolved hunk (`ev/mutants.txt`): baseline `cloud_dispatch self-test: 169 checks, 0 failed`, which matches the body's NULL-cloud line. M1 drops `verdict=verdict` and is KILLED with `FAIL a designer's text pins the revise verdict's own commit and first line`. M2 drops main's pline append and is KILLED with `FAIL --part 2 renders the topic <topic>-p2 ...` and `FAIL --part 1 keeps the group's own topic ...`. Both sides of the union are therefore pinned.
- Production code: the three-dot diff touches nothing under `custom_components/`, and VERSION, RELEASE_NOTES.md and tests/golden are also untouched. Nothing widens the scope.
- Finder's harness: none named (packet). The policy group's harnesses are the self-tests and the entities check, as accepted by the previous verdicts.
- Merge with main: `git merge-tree --write-tree origin/main f0f6b47f` at origin/main 61afd4f2db10 exits rc=0 (`ev/merge_tree.txt`).
- PR body head line names f0f6b47f2c8f402e6d35b461c06760318576b01a. The body's Red checks section answers budget-raise-gate and instrument-self-tests, and neither is in the owed set.
- Roles: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Owed reds set (`ev/owed_reds.txt`); CI at this head: after about 30 minutes of polling, classify still prints `WAIT f0f6b47f2c8f402e6d35b461c06760318576b01a pending: gate red: none` (`ev/classify.txt`). No required check is red, and the only pending context is `gate`. Head re-read at publish: origin/fix/r10-standing-contracts-p2 is still f0f6b47f2c8f402e6d35b461c06760318576b01a.
