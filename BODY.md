Triage batch 154 rules queue line 248, which arrived after batch 153. It holds one ruling: P565, ACCEPT narrowed.

- **P565, ACCEPT narrowed, a repair of an observed wrong behaviour: S14-BEAT-CLASS-PHASE-LOCK.**
  - The beat's `orch-checkout` class jobs wait at most `class_wait_s` (60) for the class lock. Plan-beat runs a median 96 s, and every job loop stays on a grid anchored at the daemon's start, so the 1800 s jobs collide at every pass.
  - Over the journal, gantt was busy 57 of 84 passes, verdict-audit 39 of 84 and disk 86 of 161. Every one of the 232 busy passes had a class job running in its wait window.
  - After the local restart at 900, all four class jobs ran ok within 114 s.
  - The fix: `beatd.jobs.json` `class_wait_s` 900, at least the longest class `timeout_s`, pinned by `beat_jobs.py`'s self-test.
  - Remedy (b) is rejected: `beatd.py status` already counts a busy last outcome as an alarm (rc 1).
  - It is one PART 2 carry to R10-TICK-RESIDUE (handed off, PR 3425).

The diff is one file against the merge base: `dev/programme/triage/s6-batch154.md`, the ruling. No product behaviour changes.

## Head

`239bf793a9a6cd8e54fc3c892cf190bfd4432e0f`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P565 passes `triage_refusal`.
- With P565's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P566 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 63bcdcaad8...239bf793a9a6cd8e54fc3c892cf190bfd4432e0f`: 1 file.
- The busy counts come from `grep -c` on `S/beatd/journal.log` PASS lines.
- The lock holders come from overlapping each busy pass's window with the class jobs' run windows.
- The line numbers come from origin/main `63bcdcaad8`.

## Red checks

`none`. The merge base is main `63bcdcaad8`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
