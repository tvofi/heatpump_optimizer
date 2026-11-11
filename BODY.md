Triage batch 159 rules queue line 254. It holds one ruling: P571, ACCEPT, at a corrected cause.

- **P571, ACCEPT, a repair of an observed wrong behaviour: S14-FAILURE-LOGS-HIDES-OLDER-GATE.**
  - `failure_logs.sh` keeps only failures before it groups by name, so a newer green never hides an older red. Its real defect is that it reads one page of 100 check-runs (line 125).
  - PR 3355's head holds 144 check-runs, listed by id descending. Both missed red `gate` runs (130305517989, 130305543232) sit below page 1's last id.
  - The fix: read every check-run through `merge_train.py`'s one paginated reader, and list every red of a required context, with deferrals tagged.
  - The ruling also corrects carry 18 (P567). The deferral `output.title` it tests is null on these runs, and `sha=` in the run name is `github.sha`, the PR's merge commit. So one arm never matches and the other always does.
  - Two carries go to R10-TRAIN-RESIDUE, both PART 2.

The diff is one file against the merge base: `dev/programme/triage/s6-batch159.md`, the ruling. No product behaviour changes.

## Head

`cbf1893c7f5ee3d028d16df85f61a42e4d09a287`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P571 passes `triage_refusal`.
- With P571's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P572 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat dbd1ab5b07...cbf1893c7f5ee3d028d16df85f61a42e4d09a287`: 1 file, 1 commit.
- The check-run pages, ids and titles come from the GitHub API at about 04:05Z.
- The line numbers come from origin/main `dbd1ab5b07`.

## Red checks

`none`. The merge base is main `dbd1ab5b07`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
