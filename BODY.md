Triage batch 82 rules the orchestrator s8's slip proposal of 2026-10-31. The train's pre-flight refused #3004 with BAD-DEST `b42363f1`, "R10-FLY-CANCEL-SWEEP is not a group of the roster", though the group is open on the round's roster branch: round-10 roster changes reach main only at the stamp. It is the next rolling batch under V182, after batch 81. It holds one ruling and one held roster op.

- **P319: ACCEPT, a carry on R10-FLY-RELAY-REVIEW-FF** (it owns `carry_audit.py`'s disposition). It may be dispatched alone.
  - `carry_audit.load_dests` already reads the round roster (`roster_lib.round_ref`), but only on its no-ref path (lines 370-374).
  - `queue_pre_flight.py:197` passes `ref="origin/main"`, so it never reaches that path. The fix sets `round_roster` on the explicit-ref path too (lines 347-352), and pre-flight inherits it unchanged.
  - Train-log instances: `PARK #3004` `b42363f1` (R10-FLY-CANCEL-SWEEP: on the roster branch, absent from main) and `PARK #2925` `162aa32f` (R10-FLY-CIPREDICT-RESTORING, the same shape before its stamp). Both were waived by hand.
  - Nulls carried: a group on neither ref is still BAD-DEST, and a group done on the round ref is still refused.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`754999566c34adaf352e875386f18123ebf03fb1`; the file is the whole diff against `fbc731283`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P319 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch82.md#P319`: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same carry is refused: `dev/programme/triage/s6-batch82.md#P319 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main. The carry, appended to the live roster, gives `brief_lint.mjs` `TOTAL: 0 error(s)`.

## Figures

- `git show origin/main:tools/audit/carry_audit.py` at `fbc731283`: `def load_dests` at line 342, the explicit-ref branch at lines 347-352 setting no `round_roster`, and `rref = roster_lib.round_ref(git)` at line 372 inside the `else:` branch.
- `git show origin/main:tools/audit/seat/queue_pre_flight.py` at `fbc731283`, line 197: `ca.load_dests(self.checkout, "origin/main", issue_state=self.issue_state)`.
- `grep -c '"group": "R10-FLY-CANCEL-SWEEP"'` gives 0 on main's roster and 1 on the roster branch's.
- `grep 'is not a group of the roster'` over the orchestrator's live `merge_train/train.log` gives the two `PARK` lines named above.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
