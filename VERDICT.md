Fix review: merge 838cff1468273b8615d303a433fc0f7ab936c6e6

bus-nonce: cd1350ce3678e9d57249fd36d669421c

## Scope

Round 1 review of #2791 (record lane, no group; autofix bot branch record/autofix), head 838cff1468273b8615d303a433fc0f7ab936c6e6, which is still the live head of record/autofix (ev/live_head.txt). dev/governance/roles/ is unchanged between the merge base and origin/main, so the contract read is current.

## Evidence

- Three-dot diff against origin/main (merge base 7138516b4b03764b4e76afbfdf183bab2cb1396b) touches exactly dev/programme/delivery/2787.md, dev/programme/delivery/2789.md and dev/programme/delivery/2791.md, three insertions and two deletions; no other file (ev/diff.txt).
- dev/programme/delivery/2787.md: open -> merged `1aa765f`. 1aa765fdd202647debaa7699f74bc15cf52ab674 is "Merge pull request #2787 from tvofi/fix/audit-r10-roster-pr9" and is an ancestor of origin/main (ev/merge_commits.txt). Row text otherwise unchanged apart from a trailing full stop.
- dev/programme/delivery/2789.md: open -> merged `7138516`. 7138516b4b03764b4e76afbfdf183bab2cb1396b is "Merge pull request #2789 from tvofi/record/autofix" and is an ancestor of origin/main. The new subject "delivery rows for #2765, #2788" matches that merge's diff (2765.md, 2788.md, 2789.md).
- dev/programme/delivery/2791.md: new, one line, anchors #2791, status **open**, matching the PR's real state (open, not merged).
- Merge with origin/main (ab3aade496371f1da01e96730188e2b0997e5536): `git merge-tree --write-tree` exits 0, tree 438dbbd0437de7912392e5951ad4af5f4ef95be3, no conflict, no claim file touched (ev/merge_tree.txt).
- RESULT delivery_status: `python3 tests/delivery_status.py` at the head prints DELIVERY STATUS OK, 141 rowed, 1 pending (#2790, merged on main after this PR's base, 0 commits since), 0 overdue (ev/delivery_status.txt). #2790 pending is the ordinary batch state and not this PR's subject.
- RESULT policy_lint --record --since 7138516~5 at the head: the one error names #2790 only, the same post-base merge; #2787 and #2789 are dispositioned (ev/policy_lint_record.txt).
- RESULT record_row.py --pr 2791 --automerge-check: AUTOMERGE OK, rc 0 (ev/automerge_check.txt).
- Mutation proof, null control, claim files (step 4), VERSION/manifest/notes (step 5), class enumeration (step 6), metric movement (step 14) and architecture (step 15): n/a, the diff is three delivery row files and moves no instrument, budget, fixture or version.
- CI on the head from the check-runs API: no run concluded failure; governance / instrument-self-tests and two prelude jobs were still in progress at read time (ev/check_runs.txt). With no red check there is no root-cause trigger to answer; the body's Red checks section answers record, nightly-status and delivery-status pre-emptively, and all three are green or skipped here.
- Body Head section names 838cff1468273b8615d303a433fc0f7ab936c6e6, the head measured. Forward-carry: none, consistent with a record-only diff.

## Findings

None.
