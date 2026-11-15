Fix review: merge e4edcd794d22dfe996322a63e7d115f262e12042

bus-nonce: e9c1f05f3eef1b2ef1abf3a56e8dc53b

## Scope

This is a later round on PR #3598, over the reviewed head a945275dd01d5a7ee100598315bd94e20652cb25. The packet's `## Review scope` reads `delta`. The delta (`git diff a945275dd0 e4edcd794d`) is three commits: d9e3d1550f (one features.py check plus the `tick-before-note` mutant in `dev/audit/harnesses/start_counter_edges_mutants.py`), 7c2370fbb0 (`mutation-autofix`'s 14 ledger rows) and the merge e4edcd794d that brings d9e3d1550f in. It is 16 files, 115 insertions, and touches no `custom_components/` path, so nothing widens the review. The role contract is current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. This is the third reviewer round on this group's code since its last block. A fourth round would owe a re-cut (`fixer.md`).

## Prior findings

- The previous verdict's only block was the survivor `own-tick-before-note` (`running_signal.refresh` with `note(sig, when)` and the re-read swapped). It is resolved.
  - The new features.py check, "a refresh whose own re-read moves the class off running ...", kills it. In the tracked harness at this head it reads `KILLED tick-before-note: 1 fail, 0 fail`.
  - The previous round's order probe (ev/probe_order.py, sha1 28473aac79655ac54d647a5ab5bb8c6ac5f82f5e) prints `RESULT starts=0` at this head and `RESULT starts=1` with the two lines swapped.
  - The check carries its own null control: the row with nothing moving counts the rise once.

## Evidence

- RESULT tracked mutation harness at this head: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/start_counter_edges_mutants.py` prints `BASELINE [(0, False), (0, False)]`, 43 `KILLED`, `RESULT survived=0`, rc=0 (ev/mutants-head.txt). This matches the body's `## Figures` (43 mutants, 43 killed).
- RESULT order probe: `starts=0` at the head (ev/probe-order-wt.txt) and `starts=1` under the swap (ev/probe-order-wtm.txt), as the body states.
- RESULT whole features.py, applied in place in a separate worktree: at this head `ALL 5710 FEATURE CHECKS PASSED`, rc=0 (ev/features-head.txt). With `running_signal.refresh`'s two lines swapped: `1 of 5710 FEATURE CHECKS FAILED`, rc=1. The only failure is the new check, rows `{'commanded': 1, 'latch': 1, None: 1}`, and the null row is unmoved (ev/features-mutant-tick-before-note.txt). This matches the body's 5710 and its mutated rows, and the survivor the previous round found against the whole script is now killed there.
- Mutation ledger delta: all 14 rows from 7c2370fbb0 name an `old` line that is present verbatim in its module at this head (ev/ledger-delta.txt). Each is a `killed_by` pin from CI's `--pin-killed`, which I cite rather than re-run (fix-review.md step 11).
- Structure: `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED` (ev/structure-head.txt). No budget file is in the delta.
- Version and claims: the three-dot diff touches neither `VERSION`, `manifest.json`, `RELEASE_NOTES.md` nor either claim file (ev/version-claims.txt, empty).
- Merge: `git merge-tree --write-tree origin/main e4edcd794d` exits 0 (ev/merge-tree.txt).
- CI: `merge_train.py classify e4edcd794d22dfe996322a63e7d115f262e12042 --pr 3598` printed `GREEN e4edcd794d22dfe996322a63e7d115f262e12042 pending: none red: none`, rc 0 (ev/classify.log). There is no red at this head, so no `## Red checks` answer is owed for it. The body's `## Red checks` names the `tests / mutation` red at a945275dd0 and its repair by 7c2370fbb0. The owed-reds set is in ev/owed-reds.txt.
- Body: the `## Head` section names e4edcd794d22dfe996322a63e7d115f262e12042, the head I measured. The fixer's harness `dev/audit/harnesses/start_counter_edges.py` is flat by design this round (no production line changed), and I did not re-take its rows. The previous round measured them at a945275dd0, whose production tree this head shares.
