_Requested by **tvofi**_

This is the countermeasure the v6.6.12 root-cause record proposed for bug 7,
built now that tvofi has captured a real `/api/history/period` answer from the
install (2026-09-25).

**Before.** The card's recorder stand-in (`tests/card_rig.mjs` `historyApi`)
served `last_updated` on every row and no `last_changed`. The real answer
differs. Under `minimal_response`, only a list's first row carries
`entity_id`, `attributes` and `last_updated`, and every later row carries
`state` and `last_changed` alone. A full row carries all five keys. So a card
that read only `last_updated` would have passed every card check and drawn
nothing on an install: the class that let bug 7 ship (P11).

**After.** The rig serves the rows with the real keys. `last_changed` holds at
the last state change under an attribute-only update, as HA's does. The keys are
pinned in `HA_HISTORY_ROW_KEYS`, taken from the capture (keys only, no values
from the install), and a card check compares the rig's answer to them. The card
needs no change: it already reads `last_updated || last_changed`.

The capture also confirms two semantics the rig already had. The action query
without `significant_changes_only=0` returned one row for 00:00–12:00 (RC2), and
lists came back in request order when none was empty.

## Head

3f9f7708c8ec17591a4369e28c585172df558a37. Merge base 1f032bd430921a1b4fc0bb0846351399d6d34745.

## Mutation proof

`PYTHONPATH=tests/hastub node tests/card.mjs`, file restored after each run:
- the card's two history-row time reads changed to `Date.parse(row.last_updated)`
  → 7 checks FAIL at the head, including "the measured indoor temperature renders
  left of now", "an unavailable stretch breaks the measured trace rather than
  zeroing it" and "the measured temperatures are drawn as held steps, not a
  fitted curve".
- the same card mutant against the merge base's rig → only the new shape check
  fails, and no other check notices the mutant. This is the gap the correction
  closes.
- the merge base's rig → FAIL "the history rig's rows carry the keys a real
  install's rows carry".

## Null control

At the head, `node tests/card.mjs` prints `ALL CARD CHECKS PASSED`.
`node tests/card_drift.mjs origin/main` prints "identical in all 40 states": the
rig change moves no drawn state.

## Figures

- `python3 tests/closure.py select --diff origin/main` prints `MODE: SCOPED --
  3 script(s) run, 23 scoped out`. plan_view.py, card.mjs and card_drift.mjs were
  each run directly and are ok.

## Red checks

none

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01XQkb2K7Xcpm4KxSZRQ6EDx
