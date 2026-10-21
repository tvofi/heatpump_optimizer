Fix review: blocked 39f465739706edd44c7446a7cdebc0e0c5b30091 head-moved: measured 39f465739706edd44c7446a7cdebc0e0c5b30091, head is 13a798252c51e730f409d1648f1a39b3b0c1c997

Round 1. Group none: PR #2559 is the roster PR (topic audit-r10-roster); no group entry matched, so this review is against the PR body.

## Why blocked
The PR head moved while CI on the dispatched head was still running. 13a798252 is not a main-only carry (orchestrator.md section 11's predicate): it merges a new authored code head a6e0530d4, which adds two commits to the branch (5f52cb8ce `append-carry R10-CI-LAYOUT-P1` and a6e0530d4 `append-carry R10-CI-LAYOUT-P2`), and then merges origin/main dbea71db7 (#2525). A move that adds authored commits gets a fresh review, so this verdict does not carry (ev/head-move.txt). The gate jobs on 39f46573 (closures, closures-autofix, ci-ratchet, composed-proof) were cancelled at 13:12:37Z when the new head superseded them.

What still holds at 13a79825, and what does not:
- Still true at a6e0530d (ev/derive-a6e0530d.out): groups 91 to 108, 17 new and none removed, stage `done` 43 to 51, 18 stage changes, and 32 carries appended to 14 existing groups.
- Out of date: the body's "carries 201 to 254" and "the other 21 of the 53". The diff they describe is 31e162fd. At a6e0530d the counts are 201 to 256, with 23 carries on the new groups (55 in all). The body's Head section names a6e0530d, but its enumeration paragraph still says `at 31e162fd`.
- Not measured: the content of the two new carries, and CI on 13a79825.

## Checked at 39f465739706edd44c7446a7cdebc0e0c5b30091 (ev/HEAD.txt)
Each line gives the step from fix-review.md.
- 1 mutation proof: n/a. The diff adds no production or test code; it touches 4 files (ev/diffstat.txt).
- 2/3 harness, null control: n/a. The body makes no measured claim. The "finder harness" here is the JSON diff itself, and I re-derived it with my own script, ev/derive.py, which is mine and not the fixer's. The "stage" counts use `resume.stage`.
- 4 claim files: `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are untouched.
- 5 versions: `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- 7 body head: 39f46573 equals merge-tree(f58b14c19, 31e162fd) plus only `dev/programme/delivery/2559.md`, which matches the body.
- 8 figures, all re-derived at f58b14c19 vs 31e162fd (ev/derive-31e162fd.out). The roster files are identical at 03b49e152 and f58b14c19.
  - RESULT groups 91->108; new 17 with the stages the body lists; removed none.
  - RESULT resume.stage done 43->51; 18 stage changes, exactly the body's list (8 to done, 8 to in-progress, 2 done->in-progress).
  - RESULT carries 201->254; 14 existing groups take 32 carries and the new groups hold 21.
  - RESULT text-edits 16 groups (brief/issues/fixes/findings). R10-CI-LAYOUT `findings` names the four-PR split.
  - The per-group pairs "R10-BRIEFS-FOLD 19 to 20", "R10-ORCH-MACHINERY 8 to 10" and "REPLAY-LANE replaced" describe steps in the branch history, not counts against main. Against main, BRIEFS-FOLD goes 18 to 20 with nothing dropped, and REPLAY-LANE goes 3 to 5 with nothing dropped. R10-REGISTRY-LEAK is listed twice. These are wording issues and none of them is a wrong total.
- `critical-path.json` (new file): all 12 groups exist in the roster. Its shape matches `tools/pr/gate_priority.py`'s documented format. The file sits under the INERT prefix `dev/programme/` (tests/closure.py:273).
- 10 forward-carry: the body says none; that holds for a roster-only PR.
- 11 CI (ev/check-runs-39f46573.tsv): every job that concluded passed, except `nightly-status`, which was red. That check restores tests/nightly_status.py from the base and grades main's last scheduled run, and this diff does not reach it, so the red is not this PR's. pr-contract passed twice. The gate jobs were cancelled by the head move.
- 13 merge: `git merge-tree --write-tree origin/main(3688cf259) 39f46573` exits 0 with no conflict (ev/merge-tree.txt).
- 14 metrics: no budget, closure or golden file moves.
- Not run locally: tests/entities.py. This box has no venv with homeassistant, so I am relying on CI's `fast`, which passed.

## For a re-review at 13a79825
Re-take the carry counts. Review the two CI-LAYOUT-P1/P2 carries. Update the body's enumeration paragraph to a6e0530d (201 to 256, 23 of 55). Read the gate jobs on the new head.

bus-nonce: d63af2393eeaa21f6c75c7b3e356a3b6
