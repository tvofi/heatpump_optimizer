Triage batch 99 rules one merge-blocking false refusal, sent by the orchestrator s9 by message on 2026-11-01. `merge_train.py add` refuses #3068 because the newest posted verdict names `3c0b62eaa`, while `verdict/3068`'s tip is `948d1ee60`, a same-tree copy pushed 9 s later. This is the rolling batch after batch 98, which was pushed first and left at its head.

- **P354: ACCEPT, as two carries.**
  - **(a) R10-FLY-TRAIN-DEFAULTS.** `posted_verdict` treats the commented commit as the tip's posting iff it is an ancestor of the tip with an equal tree. That is the bus's own signed identity, `<pr> <tree>` (`bus.sh` `post_verdict`), and it releases #3068 without touching a ref.
  - **(b) R10-FLY-RELAY-REVIEW-FF, held until #3065 merges.** `bus.sh confirm` takes a per-PR `mkdir` lock across its pre-check, append and post, and appends nothing when the tip already has the tree.
  - **What made the copy.** Two confirms of one review commit, 9 s apart in one state directory. The second passed the replay pre-check before the first's post wrote `posted-signed`.
  - **The class.** 170 same-tree parent/child pairs on 79 of 515 `verdict/*` refs. 54 are 60 s apart or less, 53 refs have a copy at the tip, and 13 pairs date from 2026-10-30 on.
  - **The interim for #3068.** Rewind `verdict/3068` to the posted commit with `--force-with-lease`. That loses nothing: same tree, message and signature. A by-id waiver is not legitimate, because the train has no waiver and a hand merge leaves no record that its check held.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`8d788ff12d6c50399c3bb3e2578bfc9320adced6`; the file is the whole diff against `c89de2f62`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`. The gate was run against the roster at `c28fbf12d`.
- On the committed file, `ruling_verdict` reads P354 as `ACCEPT`.
- `op_append_carry` accepts carry (a) on R10-FLY-TRAIN-DEFAULTS and carry (b) on R10-FLY-RELAY-REVIEW-FF.
- `triage_refusal` returns None for both.
- With P354's verdict changed to `REJECT`, both carries are refused: `dev/programme/triage/s6-batch99.md#P354 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it: `the triage ruling dev/programme/triage/s6-batch99.md is not on the roster branch or origin/main`.
- `brief_lint.mjs` reports 0 error lines on the roster both before and after the two ops.

## Figures

- `git log origin/verdict/3068`: `3c0b62eaa` (04:57:25 +01:00) and `948d1ee60` (04:57:34), both with tree `03483ecd5`.
- Comment 6553126385 (03:57:35Z): `bus: verdict/3068 at 3c0b62eaa...`.
- `git ls-remote origin 'refs/heads/verdict/*'`: 515 refs.
- The two branch rulesets include only `~DEFAULT_BRANCH`.
- No capped file is touched.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
