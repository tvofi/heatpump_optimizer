Triage batch 91 rules two of the orchestrator s9's triage-queue slips of 2026-10-31. This is the next rolling batch after batch 90, with two rulings and two held roster ops.

- **P329: ACCEPT narrowed**, as one carry on R10-FLY-RELAY-REVIEW-FF. That group holds P308's `## Evidence` carry on the same `items()` in `tools/audit/carry_audit.py`.
  - The new rule is an owner-approval carve-out, read in every verdict section. It covers a sentence stating that the owner's approving review is required at the merge, and the one bare "does not block" sentence after it. NONBLOCK and DEFERRED are not read in either.
  - Prototyped over all 484 `verdict/<pr>` refs, it clears exactly four items: #2997 `a7dc6fe0`, #3004 `fdeb7c52`, #3005 `e963066e` and #3013 `fccf8846`. #3005 and #3013 sit outside `## Evidence`, where P308 does not reach, and each parked the train.
  - The null rows stay findings: #2281 `e9ead054` and #2867 `fe436106`/`9132bbad`, which name code-owned paths but have no approval sentence.
  - REJECTED (a): skipping `## Summary` or non-bulleted prose. 69 items are flagged in such prose across the 484 refs, 19 of them routed with `Carry:`. Unheaded prose holds real findings, for example #2549 `01ce8b81` and #2386 `97a3b64e`. Only 2 items are flagged under a `Summary` heading at all.
  - REJECTED (b): a reviewer-contract `Carry: dismissed`. It is a `fix-review.md` policy edit that makes every reviewer pay for a classifier defect.
  - DEFERRED: #3038 `7dba2920`'s "the score does not block" shape, a single instance. It re-opens at three instances once P308 and this carry have landed.

- **P330: ACCEPT narrowed**, as one carry on R10-FLY-TRAIN-DEFAULTS, which owns `dev/governance/roles/standing-merge.md`. The merge seat serialised default-flag pull requests into solo trains.
  - The carry is one contract sentence: a verdicted pull request on the recommended flags joins the live train with `train.sh add` as its next batch. Only a pull request whose flags differ (a `--no-pre-flight` waiver) waits for its own train.
  - The sentence must be paid within the file's cap, 36 of 37 lines and 501 of 507 tokens. It is policy, approved at merge.
  - Instance: the s9 merge seat's sequencers ran `add` only after each `TRAIN_RC`, which planned #3037, #3030 and #3039 as three solo trains. A solo train ran 48 to 67 min (#3022, #3038).
  - REJECTED: an `add` refusal. The pidfile and flock already allow one train per state dir, and a sequencer that waits for `TRAIN_RC` never runs two trains at once, so the refusal would see nothing.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`ccc4e5435a6f03fcf80cdeb8f89ab94650093aa9`; the file is the whole diff against `0cae227c3`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P329 and P330 as `ACCEPT`. `triage_refusal` passes both carries, which cite `triage: dev/programme/triage/s6-batch91.md#P329` and `#P330`, and returns None.
- With P329's verdict changed to `REJECT`, its carry is refused: `dev/programme/triage/s6-batch91.md#P329 is not an ACCEPT ruling (REJECT)`. The same change on P330 refuses its carry the same way.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or on origin/main.
- The prototype's null rows stay flagged:
  - the approval sentence followed by "A defect in y is left in place, not blocking.";
  - "- x.py is code-owned and a defect in it does not block.".

## Figures

- Every figure is `carry_audit.items(text, True)` at `0cae227c3`.
- `train/current.log` (orchestration dir) holds 7 PARK lines whose first item is a review comment, and all 7 are over-fires. Four of them fall in `## Evidence`, where P308 clears them: #3011, #2997, #3019 and #3031. The other three are #3005, #3013 and #3038.
- Over the last 30 merge verdicts, #3007 to #3039, 11 items are flagged, and 5 of them have no `Carry:` marker.
- `node tools/policy/policy_lint.mjs --budgets` names `carry_audit.py` 0 times. `fix-review.md` is at 137 of 140 lines.
- `standing-merge.md` in `--budgets`: 36 of 37 lines, 501 of 507 tokens. `train.sh` lines 12-16 document `add`, and line 25 documents the pidfile.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
