Triage batch 92 rules two of the orchestrator s9's triage-queue slips of 2026-10-31: the merge train's approval-race SKIPs (14:50Z), and the relay and the review-ref writer acting on closed pull requests (16:10Z). This is the next rolling batch after batch 91 (#3043), with two rulings and two held roster ops.

- **P331: ACCEPT reframed**, as one carry on R10-FLY-TRAIN-DEFAULTS (`tools/audit/seat/merge_train.py`).
  - The proposed wait-after-approval already exists: `review_settle` (P86).
  - Its bound is 24 x 5 s, about 2 min. The last 59 `CI review` runs took 91 s at p50, 2388 s at p90 and 5549 s at p95; 22 ran over 150 s. The train log holds 13 `(24/24)` lines.
  - `policy_refusal` then reads BLOCKED/APPROVED with every required context green as "the missing requirement is a review", and parks the entry at once.
  - Field SKIPs: #3031 and #3039, both merged later at an unchanged head. #3013 and #3000 have the same shape.
  - The carry has two parts:
    - bound `review_settle` by time;
    - read a review run that is unfinished, or concluded under 120 s ago, with an approver APPROVED review at that head, as a wait.
  - REJECTED as filed: polling the `gate` check-run. The rollup already read every required context green when the policy refused.
- **P332: ACCEPT narrowed**, as one carry on R10-FLY-RELAY-REVIEW-FF (`tools/audit/seat/cloud_relay.sh`).
  - `confirm_arm` owes `confirm-owed` on merged or closed PRs, which `app_comment.sh` line 67 can never post. There were 11 such lines, #2589 to #2741, `tries=3/3`.
  - The carry: skip a review whose PR is not in the same pass's open-PR list, which `handoff_arm` already fetches, so it costs no extra API call. A failed listing stays owed.
  - DEFERRED to a root-cause seat: a writer-side skip. 56 `review/<n>` tips were rewritten between 14:10Z and 14:56Z, 53 of them on closed PRs and 36 tree-identical to their parent, in `bus.sh` `append_commit` format. No log names the writer.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`f49926179f4e4c15d7f1d9702af91bbb4e65ac61`; the file is the whole diff against `811112b78`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P331 and P332 as `ACCEPT`. `triage_refusal` passes both carries, which cite `triage: dev/programme/triage/s6-batch92.md#P331` and `#P332`, and returns None.
- With P331's verdict changed to `REJECT`, its carry is refused: `dev/programme/triage/s6-batch92.md#P331 is not an ACCEPT ruling (REJECT)`. The same change on P332 refuses its carry the same way.

## Null control

- With the file absent, the citations do not resolve, and the gate refuses them as not on the roster branch or on origin/main.

## Figures

- `merge_train.py` at `811112b78`:
  - line 601 `REVIEW_POLL_SECONDS = 5`;
  - line 1026 `polls: int = 24`;
  - `review_settle` at line 2095;
  - `policy_refusal` at line 2058, with its "missing requirement is a review" return at line 2091.
- `cloud_relay.sh` at `811112b78`:
  - `confirm_arm` at lines 304-339;
  - `handoff_arm`'s open-PR listing at line 399.
- `app_comment.sh` line 67: "a verdict posts only on an open one".
- Review runs:
  - 41211188623 (#3031) ran 14:40:04Z to 14:46:10Z;
  - 41196240353 (#3039) ran 11:17:29Z to 11:18:48Z.
- `node tools/policy/policy_lint.mjs --budgets` names neither `merge_train.py` nor `cloud_relay.sh`.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
