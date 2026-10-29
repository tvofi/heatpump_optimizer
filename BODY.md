Triage batch 63 rules two of the orchestrator's triage-queue lines. The line of 2026-10-29T23:39:17Z (a re-add of a skipped pull request is dropped as ALREADY) is P291. The line of 2026-10-29T23:45Z (the record body names its reporter reds in a form the review packet does not match) is P292. It is the next rolling batch under V182, after batch 62 (#2972). P292's group cannot be appended to the roster until this file is on main, and the record pull request (#2966) is refused at review until the group's fix lands.
- **P291 (merge_train drops re-adds of skipped entries): ACCEPT as already ruled. The fix is P129 (`s6-batch26.md`) as amended by P189 (`s6-batch32.md`), accepted carries on R10-TRAIN-OVERLAP-GRADE that have not been built. One carry adds the field instances.**
  - Live train log, train pid 34197: batch `20261029-193537-b4` formed right after `SKIP REPORT: 5 skipped of 10` with `ALREADY #2917`, `#2872` and `#2961` ("in this train already"). #2970, skipped at merge, was refused twice from the pending layer ("queued in the live train ... nothing added").
  - P129's shared admission predicate for `train_add` and `queue_take`, and P189's pending-layer removal on skip, are exactly that fix. `merge_train.py` still has the two separate checks.
  - New in the carry: a `merge` skip whose last refusal is GitHub's branch policy re-admits at the same verdict head, as P189's HOLDER exception does. That covers #2970's shape.
  - Dispatch of R10-TRAIN-OVERLAP-GRADE does not wait on this batch. Meanwhile a new train re-admits every entry, because `seen` is per train.
  - One held roster op (`append-carry R10-TRAIN-OVERLAP-GRADE`), released once this file is on main.
- **P292 (record body red-check names): ACCEPT as a new S fly-in, R10-FLY-RECORD-RED-NAMES (`tools/audit/seat/record_row.py` and its instrument note).**
  - `record_row.py` writes `## Red checks` with `record`, `nightly-status` and `delivery-status`. `review_packet.py` `gate_digest` passes the check-run's full name, `<caller job> / <job>`, as `--red` to `policy_lint.mjs --pr-body`. `ci.yml` calls `tests.yml` from job `tests` and `governance.yml` from job `governance`, and no called job sets `name:`. #2966 at `850c81c3` was refused as red-unanswered.
  - The writer's self-test pins the writer's own form. The self-test is rc 0 with the short names and rc 1 with `tests / nightly-status` and `tests / delivery-status`.
  - The fix: name the full check-run names and keep the short names beside them, from one definition the self-test also reads. Mutation and null control are specified in the ruling.
  - One held roster op (`append-group R10-FLY-RECORD-RED-NAMES`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`3178d6a56069e3032941a4680e5edcf4f536878d`; the file is the whole diff against `2ab53fe90590dee8376e800af2f09fd94bc75703`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P291 and P292 as `ACCEPT`. `triage_refusal` passes the R10-TRAIN-OVERLAP-GRADE carry text and the R10-FLY-RECORD-RED-NAMES group brief (both return None).
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same texts are refused: `dev/programme/triage/s6-batch63.md#P291 is not an ACCEPT ruling (REJECT)`, and the same message for `#P292`.

## Null control

- With the file absent, the carry's citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- `grep -n ALREADY` over the live `merge_train/train.log` gives 13 lines. Of these, `ALREADY #2917`, `#2872` and `#2961` immediately follow `SKIP REPORT: 5 skipped of 10` at the batch-4 formation, and `ALREADY #2970: queued in the live train (pid 34197); nothing added` appears twice.
- `grep -n '^SKIP #'` gives #2917 at carry (4 times), #2872 at ci (`TIMEOUT`) and #2970 at merge (`not merged after 8 attempts`).
- `git cat-file -e origin/main:dev/programme/triage/s6-batch26.md` and `s6-batch32.md` both succeed, so P129 and P189 are on main.
- The carry was linted on a copy of the roster at the `handoff/audit-r10-roster` tip: `TOTAL: 0 error(s)`.
- The R10-FLY-RECORD-RED-NAMES group, appended to a copy of the roster at that tip, lints to `TOTAL: 1 error(s)`. The error is the expected one: the cited `dev/programme/triage/s6-batch63.md` is "not in the tree" until this pull request merges.
- `grep -n 'uses: ./.github/workflows/'` in `ci.yml` puts `tests:` at line 175 and `governance:` at line 204.
- The P292 self-test mutation was run in a scratch worktree at origin/main `2ab53fe90`, by editing the reds `_body_check` is given. The result was rc 0 before and rc 1 after: `body check passes the generated body over the reporter reds (rc 1: PR-BODY: 2 error(s)...)`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
