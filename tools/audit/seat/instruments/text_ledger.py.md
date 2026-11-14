# `text_ledger.py`

- `text_ledger.py` — enumerates every text unit a D5 or D6 seat judges (D6:
  each sentence, fenced block, JSON string sentence and user-visible literal;
  D5: each comment block and docstring), with ids stable across line moves.
  When: a D5 or D6 finder rows its cells (`units --seat`), and closes its
  ledger (`check --plant`). Refusal: a unit with no row, an orphan or
  malformed row, or a planted sentence the ledger does not see — the planted
  unit is the null control that an omission is visible; `--self-test` also
  pins round 10's unrowed `strings.json` sentence as a unit.
