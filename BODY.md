Triage batch 115 records five rulings, P373 to P377, from the orchestrator s10's messages of 2026-11-02 between about 12:15Z and 16:55Z. It is the first batch held to the owner's 8-to-10-entry record size (P373), and it is pushed early because the orchestrator planned the v7.1.2 stamp.

- **P373: DEFER (LOG).** Rolling record and roster branches. The friction holds no `custom_components/` pull request, and the whole triage lane is 7.6% of measured CI run time, under the 10% exemption. The same saving comes from batching rulings, which this seat now does; the roster branch already rolls.
- **P374: ACCEPT (defect).** `append_commit` in `tools/audit/seat/bus.sh` appends a second commit with the same tree to a verdict ref, which deadlocked #3173 at the merge train's verdict-identity guard. Carry b115-P374 goes to R10-FLY-RAISE-REVIEWABLE. Option (b), loosening the train's guard, is refused.
- **P375: ACCEPT (propagation).** RED-UNOWNED must count a payload-named fire and a `handoff-wip/<topic>` move as "a seat is on it". Carry b115-P375 goes to R10-TICK-PR-BUCKETS, whose carry 6 leaves "dispatched" undefined.
- **P376: DEFER (LOG).** The seat-no-return false positive on a split-part topic. The class went to a root-cause seat as the third instrument keying on an exact topic.
- **P377: ACCEPT (root-cause barrier).** One shared topic grammar for the split-part class. Carry b115-P377 goes to R10-TICK-PR-BUCKETS, with R10-OPENER-REUSE as the fallback. The root-cause document rides in this batch as `s6-batch115-rca-topic-family.md`, with host paths scrubbed.

No product behaviour changes: the diff is two markdown files under `dev/programme/triage/`. The three ACCEPT carries and one set-files op are held in the roster queue until this batch is on main.

## Head

`1d35b423ce237efda5eb353d489b387ad630751c`; the two files are the whole diff against `3905069f3`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P373 `DEFER`, P374 `ACCEPT`, P375 `ACCEPT`, P376 `DEFER` and P377 `ACCEPT`. A text citing `s6-batch115.md#P374`, `#P375` or `#P377` gets refusal `None`. A text citing `#P373` or `#P376` is refused: `is not an ACCEPT ruling (DEFER)`.
- With P373's verdict flipped to ACCEPT, it reads `ACCEPT` and the refusal is `None`.
- With P374's verdict flipped to REJECT, it reads `REJECT` and the citing text is refused: `is not an ACCEPT ruling (REJECT)`.
- P378 reads `None`: no such entry.

## Null control

- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch115.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat 3905069f3...1d35b423c`: 2 files, 515 insertions.
- The per-ruling figures are cited beside their commands in each entry's `Instances:`.
- No capped file is touched; the diff is two markdown files.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
