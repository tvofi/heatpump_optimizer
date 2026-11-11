Fix review: blocked cb30b77fbf14333a3f1a358548bb17771a2d8dc8 mutation-vacuous: X10 rollup_states `>=`->`>`, X14 stamps[0]->stamps[-1], X16 drop `c.get("context")` fallback, X17 drop `if not self.real: return` in record_drafts

bus-nonce: 971be45b7af9043015426981f1470cf6

## Block

Round 2, delta review of 0c55662763813cee343d86278f94f90bc3e193a6..cb30b77fbf14333a3f1a358548bb17771a2d8dc8 (tools/audit/seat/merge_train.py only; a test delta plus the `rollup_states` stamp tidy, no widening).

The four mutants the previous block named are killed now (M4, M7, M8, M9, each a distinct self-test FAIL). Four further mutants of the PR's own new lines survive the full `--self-test` (rc 0), so the added tests do not pin them:

- X10: `(stamp, i) >= best[name][0]` -> `>`. The docstring promises "an equal stamp keeps the later listed entry"; no case has two entries with an equal stamp.
- X14: `stamps[0]` -> `stamps[-1]`. Nothing has an entry with both a valid completedAt and a valid startedAt that differ, so completedAt-over-startedAt priority is unpinned.
- X16: drop the `c.get("context")` name fallback. No StatusContext-shaped entry (key `context`, no `name`) appears in any rollup case.
- X17: drop `if not self.real: return` in `record_drafts`. Nothing runs it with `real` false, so a dry run could make live `is_draft` reads.

Equivalent, not counted: X15 (`or state in ROLLUP_PENDING`) and X18 (`(c.get("status") or state).upper() in ROLLUP_PENDING`) survive, but each is redundant with the other clause for every entry shape GitHub produces.

## Findings

- Survivor X10 (see Block): add an equal-stamp pair in both list orders to P608. Carry: R10-TRAIN-RESIDUE-P2 | #0 | O0 | dismissed: own-group, repaired in this PR's next round
- Survivor X14: add an entry with both distinct stamps. Carry: R10-TRAIN-RESIDUE-P2 | #0 | O0 | dismissed: own-group, repaired in this PR's next round
- Survivor X16: add a `context`-keyed entry. Carry: R10-TRAIN-RESIDUE-P2 | #0 | O0 | dismissed: own-group, repaired in this PR's next round
- Survivor X17: run `record_drafts` with `real` false and assert no read. Carry: R10-TRAIN-RESIDUE-P2 | #0 | O0 | dismissed: own-group, repaired in this PR's next round

## Evidence

- Head reviewed: cb30b77fbf14333a3f1a358548bb17771a2d8dc8 (ev/HEAD.txt). No pull request, review packet or CI exists yet; none to wait on.
- RESULT baseline `merge_train.py --self-test` at the head: 623 checks, 0 failed, rc 0 (matches the body).
- RESULT mutants (ev/res_*.txt, driver ev/mut.py, one fresh worktree each): M4 KILLED, M7 KILLED, M8 KILLED, M9 KILLED, X11 (`"draft" not in item`->True) KILLED, X12 (drop `or undrafted`) KILLED, X13 (drop `undrafted = True`) KILLED, X19 (drop PENDING override) KILLED; X10, X14, X16, X17 SURVIVED; X15, X18 SURVIVED as equivalent.
- `git merge-tree --write-tree origin/main <head>` rc 0, no conflict.
- Body head SHA matches. Reds named in the body (`tests / fast (3.14)`, `governance / instrument-self-tests`) are main's per the brief; not answered here.
- Not run: `env_drift.py`, VERSION checks (the diff touches one tooling file only), `carry_audit.py check` (bus.sh/probe path not available to this seat).
