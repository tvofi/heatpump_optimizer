Triage batch 92 rules one proposal: the orchestrator s9's triage-queue slip of 2026-10-31T14:50:00Z. The merge train SKIPs an approved pull request while the approval's review run is still settling. This is the next rolling batch after batch 91 (#3043), with one ruling and one held roster op.

- **P331: ACCEPT reframed**, as one carry on R10-FLY-TRAIN-DEFAULTS (`tools/audit/seat/merge_train.py`).
  - The proposed wait-after-approval already exists: `review_settle` (P86).
  - Its bound is 24 x 5 s, about 2 min, sized for P86's 70-s runs. The last 59 `CI review` runs took 91 s at p50, 2388 s at p90 and 5549 s at p95; 22 ran over 150 s. The train log holds 13 `(24/24)` lines.
  - `policy_refusal` then reads BLOCKED/APPROVED with every required context green as "the missing requirement is a review", and parks the entry at once.
  - Field SKIPs: #3031 and #3039, both merged later at an unchanged head. #3013 and #3000 have the same shape.
  - The carry has two parts:
    - bound `review_settle` by time, using `POLL_SECONDS` up to the existing CI-wait budget;
    - read a review run that is unfinished, or concluded under 120 s ago, with an approver APPROVED review at that head, as a wait and not a park.
  - The null parks are unchanged: #2968's missing owner review, and a red context.
  - REJECTED as filed: polling the `gate` check-run. The rollup already read every required context green when the policy refused.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`4c5df776be194a89ccd901380fe1dbb9b6e59234`; the file is the whole diff against `811112b78`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P331 as `ACCEPT`. `triage_refusal` passes the carry, which cites `triage: dev/programme/triage/s6-batch92.md#P331`, and returns None.
- With P331's verdict changed to `REJECT`, the carry is refused: `dev/programme/triage/s6-batch92.md#P331 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or on origin/main.

## Figures

- `merge_train.py` at `811112b78`:
  - line 601 `REVIEW_POLL_SECONDS = 5`;
  - line 1026 `polls: int = 24`;
  - `review_settle` at line 2095;
  - `policy_refusal` at line 2058, with its "missing requirement is a review" return at line 2091.
- Review runs:
  - 41211188623 (#3031) ran 2026-10-31T14:40:04Z to 14:46:10Z;
  - 41196240353 (#3039) ran 11:17:29Z to 11:18:48Z.
- `node tools/policy/policy_lint.mjs --budgets` names `merge_train.py` 0 times.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
