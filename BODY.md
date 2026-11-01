Triage batch 107 records one ruling, P365, from the orchestrator s10's queue line of 2026-11-01T20:40Z: the carry-verdict deadlock between `tools/pr/app_comment.sh`, `bus.sh` and `app_approve.sh` that held #3047, the v7.1.1 production fix. It is the rolling batch after batch 106. P364 was never assigned.

- **P365: ACCEPT, by owner ruling (tvofi, 2026-11-01T20:34:40Z).** No new carry is queued.
  - **The destination.** It is R10-FLY-CARRY-DOC-CONTEXT carry 3, which is P264 (`s6-batch53.md#P264`, ruled 2026-10-28 on four instances). That carry specifies exactly this change: `app_comment.sh check_pr` runs `app_approve.sh --carry` on a moved merge head and posts on `CARRY: yes` with a carry line.
  - **It is built.** #3077 (head `aa6148d4f`, in stamp-batch train 54386) implements it in `tools/pr/app_comment.sh` (56 lines added, 8 removed). Its self-test arms are: a pin-only head posts with the carry line; a branch's own code commit is refused "head moved"; the carried body reads back identical.
  - **Why no new carry.** A second carry would duplicate P264, and `brief-carries` would refuse #3077's in-flight packet.
  - **#3047's merge-shaped move is covered.** `review_carry.py` prints CARRY only where `app_approve.sh --carry` carries ("One predicate, asked rather than copied"), and #3047 printed CARRY.
  - **Delivery is #3077's merge.** Until then a carried head needs the manual path used on #3047.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. No roster op is queued.

## Head

`bea0c09f1ee68c20dcd183a69307c4cc1ea5128d`; the file is the whole diff against `7f849a249`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P365 as `ACCEPT`, and a text citing `s6-batch107.md#P365` passes `triage_refusal`.
- With the verdict flipped, it reads `REJECT`.
- P364 reads `None`: no such entry.

## Null control

- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch107.md is not on the roster branch or origin/main`.

## Figures

- `git diff --numstat origin/main...aa6148d4f -- tools/pr/app_comment.sh`: `56 8`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
