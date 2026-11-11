Builds carries 17 (TRAIN-POLICY-REASON-STALE-CONTEXT) and 18 (TRAIN-UNDRAFT-EVERY-ROUTE) of R10-TRAIN-RESIDUE-P2 in `tools/audit/seat/merge_train.py`. `policy_refusal` read the last-listed rollup entry, so #3445 (gate FAILURE x4, SUCCESS listed last) parked as "missing requirement is a review" while GitHub blocked on a red gate; a `--queue` or `build_queue` entry never carried `item["draft"]`, so `undraft` never fired and `land` burned 8 attempts on "still a draft".

Fix: `rollup_states` reduces a rollup to one state per context by newest `completedAt`, else `startedAt`, any unfinished entry making it PENDING. `Train.record_drafts` sets `item["draft"]` from one `is_draft` read per entry lacking the key at batch start, before `preflight`. In `land`, "still a draft" is a state: an admitted draft is readied once and re-attempted, any other draft stops with `drafted after admission: left as a hold` (a plain Stop, so no recarry and no MAIN-MOVED). Alternative rejected: setting the key inside `preflight` only, since `preflight` returns early without `--pre-flight`.

- Carry 1: left for a later part; it stays on the roster.
- Carry 2: left for a later part; it stays on the roster.
- Carry 3: left for a later part; it stays on the roster.
- Carry 4: left for a later part; it stays on the roster.
- Carry 5: left for a later part; it stays on the roster.
- Carry 6: left for a later part; it stays on the roster.
- Carry 7: left for a later part; it stays on the roster.
- Carry 8: left for a later part; it stays on the roster.
- Carry 9: left for a later part; it stays on the roster.
- Carry 10: left for a later part; it stays on the roster.
- Carry 11: left for a later part; it stays on the roster.
- Carry 12: left for a later part; it stays on the roster.
- Carry 13: left for a later part; it stays on the roster.
- Carry 14: left for a later part; it stays on the roster.
- Carry 15: left for a later part; it stays on the roster.
- Carry 16: left for a later part; it stays on the roster.
- Carry 17: built here (TRAIN-POLICY-REASON-STALE-CONTEXT, `rollup_states`).
- Carry 18: built here (TRAIN-UNDRAFT-EVERY-ROUTE, `record_drafts` and the `land` draft arm).

## Head

cb30b77fbf14333a3f1a358548bb17771a2d8dc8, measured on origin/main ee64358be7eeccaec5178a923cb3b83a18a924a0. Repair round 1 after `Fix review: blocked 0c55662763813cee343d86278f94f90bc3e193a6 mutation-vacuous`; the added commit is test-only plus one production tidy: `rollup_states` drops a zero-time stamp per field before the `or`, so a zero `completedAt` now falls back to `startedAt`.

## Mutation proof

Mutants of `merge_train.py`, each run through `python3 tools/audit/seat/merge_train.py --self-test` (623 checks, 0 failed unplanted):
- `if name not in best or (stamp, i) >= best[name][0]:` -> `if True:` (last-listed wins): FAIL "P608 #3445's five gate entries in list order".
- `if not item.get("draft") or undrafted:` -> `if False:`: FAIL "P609 a draft the train never admitted as one" and "P609 a draft again after the one ready".
- M4 `self.record_drafts(queue)` in `_batch` -> `pass`: FAIL "P609 a batch records the draft key on a key-less entry before admission" (drives `_batch` with `preflight` stubbed to capture the queue).
- M5 the read inside `record_drafts` -> `pass`: the `record_drafts` case crashes on KeyError.
- M7 `pending.add(name)` -> `pass`: FAIL "P608 an unfinished entry older than a SUCCESS still makes the context pending".
- M8 the zero-time filter `if x and not x.startswith("0001")` -> `if x`: FAIL "P608 a zero-time completedAt falls back to startedAt".
- M9 the `startedAt` fallback dropped from the stamp tuple: FAIL "P608 a zero-time completedAt falls back to startedAt" and "P608 an entry with only startedAt is ordered by it".
Survivors found by my own drive among these seven: none. Not driven: the reviewer's M10 (inconclusive, malformed in the review).

## Null control

At the merge base `policy_refusal` has `last[name]=` overwrite and no "still a draft" arm. In the self-test, all-SUCCESS in either order reaches the review branch; a non-draft entry makes no `gh pr ready` call; a recorded `draft: False` is kept by `record_drafts`; the unplanted tree passes every new case.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test` exits 0 at the head, 623 checks, 0 failed; the P608 and P609 lines print `ok`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` rc=0 at the head, body check included; merge-tree against origin/main reports no conflict.

## Red checks

- `tests / fast (3.14)`: main's red (combi census), cleared by PR #3466; not this diff.
- `governance / instrument-self-tests`: main's red (pusher census), roster group R10-HOTFIX-PUSHER-CENSUS; not this diff.

## Forward-carry

none

## Friction

none

## Architecture score

n/a: no budget or gate rise.
