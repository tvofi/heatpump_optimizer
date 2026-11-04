# Proposal triage, session s8, batch 82 (P319)

The rolling batch (V182) after batch 81 (handoff `triage-s8-batch81`). Facts were read at
origin/main `fbc731283`, on the roster branch `origin/handoff/audit-r10-roster`, and in the
orchestrator's live merge-train log (`merge_train/train.log`).

## P319: the train's pre-flight refuses a carry to a group that exists only on the round's roster branch

Verdict: ACCEPT, a carry on **R10-FLY-RELAY-REVIEW-FF** (`carries-open`). It owns `carry_audit.py`'s
disposition, where the fix lives (`load_dests`). The carry may be dispatched alone, ahead of the
group's other carries.
- **The rule.** `carry_audit.load_dests` adds the round roster (`roster_lib.round_ref`) as a second
  destination source whenever it reads a roster, including when a caller names `ref`. Today it does
  that only on the no-ref path.
- **Pre-flight changes nothing itself.** `queue_pre_flight.py:197` keeps calling
  `load_dests(self.checkout, "origin/main", ...)` and inherits the fix.
- **The premise the orchestrator asked to check holds.** carry_audit already has the round-branch
  path (`Dests.round_ref`/`round_groups`, and `load_dests` lines 370-374, "The tree's roster lags the
  round's branch (finding-propagation.md)"). Pre-flight never reaches it, because that branch sits
  under `else:`: the explicit-ref path at lines 347-352 sets no `round_roster`.

Source: the orchestrator s8's message of 2026-10-31 (a slip; a third pre-flight false-park class,
beside P308 and P314's verdict-prose class).

Instances (train log, `grep 'is not a group of the roster'`):
- `PARK #3004` item `b42363f1`: "R10-FLY-CANCEL-SWEEP is not a group of the roster". The group is on
  the roster branch (in-progress) and absent from main's roster at this read (count 1 on the
  branch, 0 on main). Waived by hand under the mandate.
- `PARK #2925` body item `162aa32f`: "R10-FLY-CIPREDICT-RESTORING is not a group of the roster". It
  is the same shape. The group has since reached main at a stamp, so it reads on both now.
- **Why it recurs.** Round-10 roster changes reach main only at the stamp (finding-propagation.md,
  tvofi 2026-10-18). Any carry to a group appended this round reads as a bad destination at
  pre-flight until the next stamp, while `carry_audit check` with no ref (prepr, body_push) accepts
  it.
  - `body_patch.sh` printed the matching `NOTE stale tree ... roster read at origin/main` (the
    orchestrator's account).
  - Two parks so far. Every fly-in appended this round is exposed.

Cost:
- About 3 lines in `load_dests`: compute `round_roster` on the explicit-ref path too, from the
  same `roster_lib.round_ref` read. Add two fixture rows.
- No new file, check or API call. `carry_audit.py` is not a capped file.

Binding: two train parks, each needing a by-name waiver, from the one destination source the rest of
carry_audit already honours. A two-path disagreement inside one function, against about 3 lines,
is clearly positive. It removes the third pre-flight false-park class at its source, not per
instance.

Carry text (for `roster_edit.py append-carry R10-FLY-RELAY-REVIEW-FF`, citing
`triage: dev/programme/triage/s6-batch82.md#P319`): "P319 (orchestrator 2026-10-31, slip:
pre-flight roster source). May be dispatched alone, ahead of this group's other carries.
- `tools/audit/carry_audit.py` `load_dests` (line 342 at fbc731283) sets `round_roster` from
  `roster_lib.round_ref` on the explicit-`ref` path too (lines 347-352). Today only the no-ref
  `else:` branch does (lines 370-374).
- A carry to a group that is open on the round's roster branch is then valid at every caller,
  including `queue_pre_flight.py:197`'s `load_dests(self.checkout, "origin/main", ...)`, as
  finding-propagation.md counts it.
- Observed: train `PARK #3004` item b42363f1 ("R10-FLY-CANCEL-SWEEP is not a group of the roster";
  on the roster branch, not on main) and `PARK #2925` item 162aa32f (R10-FLY-CIPREDICT-RESTORING,
  same shape before its stamp). Both were waived by hand.
- Fixture rows:
  - `load_dests(repo, 'origin/main')` with a group present only on the round ref routes a `Carry:`
    to it.
  - Null: a group on neither is still BAD-DEST.
  - Null: a group `done` on the round ref is still refused.
- One mutant: skip `round_roster` on the ref path, and the first row is BAD-DEST again."
