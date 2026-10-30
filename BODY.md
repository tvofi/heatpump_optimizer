Triage batch 73 rules lever L7 of the orchestrator s8's regain-24h investigation (message of 2026-10-30): run the record beat outside the merge train's critical section, so a pending record row never holds a code merge. It is the next rolling batch under V182, after batch 72 (#2993). It holds one ruling and no roster op.

- **P307: DEFER.**
  - "The record beat held the train 7.06 h on 30 SHAs" has no command behind it in the cited evidence. `phases.txt` and `durs.txt` hold no hold duration, count or SHA list.
  - The train log shows the hold the other way round: `refs/heads/train-hold` is the train holding the record beat (`hold_refresh`, "the record beat waits"), so nightly's record auto-merge cannot move main mid-train (#2291, #2295, #2299, #2302).
  - In-train record merges happen at the batch start, before the base read. The log has 8 `BOT #N MERGED` lines, each followed by the batch's `OVERLAP` base read, 15 pending skips, and 0 mid-batch or critical-path record waits.
  - Host if the answer changes: R10-TRAIN-OVERLAP-GRADE, beside P289, not R10-FLY-TRAIN-DEFAULTS. The host's three-round risk is noted (20 carries, six stage flips since 2026-10-28).
  - The control to keep is `merge_train.py`'s hold self-test.
  - What would change the answer: a per-SHA attribution from a timestamped source showing a code merge that waited on the record beat.
  - L7's queue-order actions (FLY-CANCEL-SWEEP, FLY-TRAIN-DEFAULTS forward) are the orchestrator's and need no ruling.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`b05e4b7ce7fce109bf4f2a8cb960d8ef8e319b23`; the file is the whole diff against `cf4f6b7a6`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P307 as `DEFER`. A carry citing `triage: dev/programme/triage/s6-batch73.md#P307` is refused: `dev/programme/triage/s6-batch73.md#P307 is not an ACCEPT ruling (DEFER)`. No roster op cites it.

## Null control

- With the file absent, a citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- Over the orchestrator's live `merge_train/train.log` (3732 lines): `grep -c '^TRAIN HOLD refs'` = 601, `grep -c '^TRAIN HOLD released'` = 62, `grep -c '^BATCH '` = 110, `grep -c '^BOT #[0-9]* MERGED'` = 8, `grep -cE '^BOT #[0-9]+ pending'` = 15, `grep -cE 'merged under the batch'` = 0, `grep -cE 'critical path: the record sweep waits'` = 0.
- The evidence (out of tree, the orchestrator's regain-24h scratch, which these lines rest on) holds "last merge verdict->merged (train/CI): median 1.78 mean 2.25 sum 144.2 p90 3.81" and no record-hold figure.
- `tools/audit/seat/merge_train.py` at `cf4f6b7a6`: 6703 lines; `sweep_bots` at line 1229; `hold_refresh` at line 2125; the `TRAIN HOLD` log at line 2169; `hold_idx` at line 4393; the `TRAIN HOLD released` assertion at line 4414.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
