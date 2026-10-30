Triage batch 76 rules two proposals from the orchestrator s8 (2026-10-30T21:40Z and 21:45Z). The first is the merge train's missing way to put a hotfix or critical-path entry first. The second is prepr's `brief_lint` trigger missing a line shift that breaks a cited anchor. This is the next rolling batch under V182, after batch 75. It holds two rulings and one held roster op.

- **P312: ACCEPT narrowed, a carry on R10-TRAIN-OVERLAP-GRADE, which may be dispatched alone.** That group owns the train's admission and drain.
  - `Train.queue_take` stable-sorts the batch it drains from the spool. A `train.sh add --priority N` entry goes first, then a critical-path entry (the train's own `_critical`), then arrival order.
  - REJECTED: a prioritise/move subcommand, which would be a second spool writer, and reading `gate_priority.py` at add, whose channels a spooled entry lacks.
  - Instances in `seat-ledger.md`: `:2718`, HOTFIX #3013 moved first by a hand edit under `queue.lock`, bypassing the instrument; and `:1770`, #2876 waiting behind #2888 for want of a verb. In the train log, 16 of 41 mid-train adds joined at batch 3 or later.
- **P313: DEFER.**
  - One confirmed instance: #3011's verdict `08765983a`, `tests / briefs` red on a shifted `tests/doc_claims.py:476` anchor. A second mention is in the `r10-roster-lint` body.
  - The full `brief_lint.mjs` run that the trigger would add costs 73 s of a core, measured here, detached, on every handoff touching a widely cited file.
  - CI's briefs job already caught #3011's shift. The lost round came from the body's "Red checks: none".
  - What would change the answer: a third line-shift block, or a measured `brief_lint.mjs --changed <files>` citation-only mode.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`b238bebd07611f24cd9bf68a1dbffd4ae43ac5b7`; the file is the whole diff against `437f1ba9b`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P312 as `ACCEPT` and P313 as `DEFER`. `triage_refusal` passes the P312 carry text, which cites `triage: dev/programme/triage/s6-batch76.md#P312`: it returns None.
- With P312's `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same carry is refused: `dev/programme/triage/s6-batch76.md#P312 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main. The carry, appended to the live roster and run through `brief_lint.mjs`, gives `TOTAL: 0 error(s)`.

## Figures

- `grep -oE 'batch [0-9]+ of this train'` over the orchestrator's live `merge_train/train.log` gives 25 at batch 2, 11 at batch 3, 4 at batch 4 and 1 at batch 5 (41 adds).
- `git log -1 08765983a` gives "verdict: #3011 Fix review: blocked 75b30a4e... gate-red: tests / briefs fails at this head ...".
- `node tools/policy/brief_lint.mjs` at `437f1ba9b`, run detached through `tools/audit/seat/daemonize.py`: rc 0 in 73 s.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
