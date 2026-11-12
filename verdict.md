Fix review: merge f43d1a539910824725a6d13ed12095076d6ec235

bus-nonce: b580d47598f1657aefa71d3945106612
pending-ci: pending: gate red: none

## Round

Round 3. This is a later-round review over the reviewed head `7ee0461a30e2c58d7e5f78c1fdaa13232325f88b` (verdict merge). Scope is `delta`. The delta is a delivery row plus four merges, and one of them carries a hand-resolved conflict in tools/audit/seat/merge_train.py. It touches no production code (custom_components/), so the scope is not widened (fix-review.md step 12).

## Previous verdict's findings

- R6 (`.match` to `.search`) still survives at this head (`ev/mutants.txt`, 700 checks, 0 failed). It was carried to R10-TRAIN-RESIDUE-P2, and the PR's own lines are unchanged, so that carry still stands.
- R2, R7 and the update_pr.sh/open_pr.sh note were dismissed last round. The code they read is unchanged.

## Findings

none

## Evidence

- The PR's own +/- lines are byte-identical to the reviewed head except one added line, `dev/programme/delivery/3490.md` (`ev/pr-lines-old-vs-new.txt`). Old is `git diff ba544faa 7ee0461a`; new is `git diff e59e21fe f43d1a53`. Both are 13 code files, +161/-9.
- The four first-parent merges (84d439af, 040b7d95, 6d6432bc, f43d1a53) each equal git's automatic merge tree (`ev/first-parent-merges-auto.txt`).
- `review_carry.py` prints FRESH-REVIEW because d3e955485a is not an automatic merge (`ev/review-carry.txt`). I reviewed that resolution directly. `git merge-tree 040b7d95 0b276e8c` conflicts only in merge_train.py (`ev/d3e-mergetree.txt`). The committed resolution differs from the conflicted tree only by dropping the three markers and adding two blank lines (`ev/d3e-resolution.diff`). That keeps both whole: the branch's QUIET_CHATTER/quiet_log/wire_quiet block and main's BASELINE_JOBS/one_job_pulse. It is the union the body describes.
- Main's only new log call under the quiet filter is wait_ci's one-job pulse (merge_train.py:2247-2249). No chatter member matches it, so it prints in quiet mode, which is what it was added for (`ev/pulse-note.txt`).
- `merge_train.py --self-test` at the head: 700 checks, 0 failed (`ev/selftest-tail.txt`). This matches the body.
- Mutants re-run against the merged file (`ev/mutants.txt`): wire_quiet call to `pass` gives 1 failed; predicate `if False:` gives 13; predicate `if True:` gives 29; stop flush `if True:` gives 2. Each matches the body's count.
- `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py`: ALL 2709 ENTITY CHECKS PASSED, rc 0 (`ev/entities-tail.txt`). The indented FAIL lines in its log are its seeded negative controls.
- `git merge-tree --write-tree origin/main f43d1a53` reports no conflict (`ev/merge-tree-main.txt`).
- I did not re-run the body's `prepr.sh rc=0` claim (heavy); CI runs it.
- CI: `merge_train.py classify f43d1a53 --pr 3490` printed `WAIT f43d1a539910824725a6d13ed12095076d6ec235 pending: gate red: none` (rc 3) on all 17 polls from 23:20 to 23:50 UTC; it names no pending context (`ev/classify-polls.txt`). The body's red-checks section names only reds outside the owed-reds set (`tests / mutation`, `tests / typing`, `validate / validate-hacs`), so it owes no answer.
