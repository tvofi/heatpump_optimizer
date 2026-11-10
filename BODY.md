Fix review: blocked 81ef6d1901f92cac95d49f9f886c58f0041ee425 mutation-vacuous: delete the update-ref after our own push (roster_edit.py:1158-1162)

## Block
Deleting the three-line `git update-ref refs/remotes/origin/<branch> <head>` after a successful push in `write_roster` leaves the whole roster_edit self-test green (256 checks, 0 failed). The check meant to pin it, "P409: two ops in one run both land after our own push", still passes because `_on_origin`'s fetch-on-miss (and prepare_worktree's own refresh) re-reads the ref from origin. So the update-ref is either redundant, in which case it should go, or load-bearing in a case the test does not reach. The comment above it says the next op "finds HEAD on no origin ref" without it, and no check shows that. A detector must be shown to detect: fails without the line, passes with it.

## Findings
- tools/audit/seat/roster_edit.py:1158 — update-ref after push is a surviving mutant (see Block). Either add a check that fails without it (for example, stop the fetch from running, or make the fetch fail, and assert the second op still lands), or delete the line.
- tools/audit/seat/roster_edit.py:1066 — `new = [e for e in errs if e not in base_errs]` compares ERROR lines as text sets. A write that adds a second, identical ERROR line (same group and cite) already present in the base passes unflagged. Low severity, not blocking; the owner is told by the WARN output.
- No defect found in postmerge.py or roster_queue.py; the mutants for those are killed (below).

## Evidence
- Tree at 81ef6d1901f9, base 51cd5ec8a42a; `git diff --stat` three-dot: 4 files, +282/-32. CI classification skipped as briefed.
- `python3 tools/audit/seat/postmerge.py --self-test` → `postmerge self-test: 19 checks, 0 failed`
- `python3 -I tools/audit/seat/roster_queue.py --self-test` → `roster_queue self-test: 58 checks, 0 failed`
- `python3 tools/audit/seat/roster_edit.py --self-test` → `roster_edit self-test: 256 checks, 0 failed`
- Mutant: postmerge `errs = []` → 2 failed (refusal_detail leads with the lint ERROR line; stage refused by lint gate owes its ERROR line). Killed.
- Mutant: roster_queue `if False:` in refusal_tail → 2 failed (refusal_tail; lint-gate refusal report line). Killed.
- Mutant: roster_queue except narrowed to `re_.Refuse` only → 1 failed (malformed line named and refused, rest still batch). Killed.
- Mutant: roster_edit `new = list(errs)` → 4 failed (lint gate and P435 op checks). Killed.
- Mutant: roster_edit `action="extend"` removed → 2 failed (set-files --add parse). Killed.
- Mutant: roster_edit update-ref block deleted → `256 checks, 0 failed`. SURVIVED.
- Not run: the claim-files, closure and structure ratchet checks (`tests/structure.py`, closure derivation). Only the three self-tests and the mutants were run. VERSION, manifest and notes heading are untouched by the diff (no such files in it).
