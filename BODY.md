Builds carries 16 (TRAIN-POLICY-REASON-STALE-CONTEXT) and 17 (TRAIN-UNDRAFT-EVERY-ROUTE) of R10-TRAIN-RESIDUE-P2 in `tools/audit/seat/merge_train.py`. `policy_refusal` read the last-listed rollup entry, so #3445 (gate FAILURE x4, SUCCESS listed last) parked as "missing requirement is a review" while GitHub blocked on a red gate; a `--queue` or `build_queue` entry never carried `item["draft"]`, so `undraft` never fired and `land` burned 8 attempts on "still a draft".

Fix: `rollup_states` reduces a rollup to one state per context by newest `completedAt`, else `startedAt`, any unfinished entry making it PENDING. `Train.record_drafts` sets `item["draft"]` from one `is_draft` read per entry lacking the key at batch start, before `preflight`. In `land`, "still a draft" is a state: an admitted draft is readied once and re-attempted, any other draft stops with `drafted after admission: left as a hold` (a plain Stop, so no recarry and no MAIN-MOVED). Alternative rejected: setting the key inside `preflight` only, since `preflight` returns early without `--pre-flight`.

- Carry 0: left for a later part; it stays on the roster.
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

## Head

0c55662763813cee343d86278f94f90bc3e193a6, measured on origin/main ee64358be7eeccaec5178a923cb3b83a18a924a0.

## Mutation proof

Mutants of `merge_train.py`, each run through `python3 tools/audit/seat/merge_train.py --self-test`:
- `if name not in best or (stamp, i) >= best[name][0]:` -> `if True:` (last-listed wins): FAIL "P608 #3445's five gate entries in list order".
- `if not item.get("draft") or undrafted:` -> `if False:`: FAIL "P609 a draft the train never admitted as one" and "P609 a draft again after the one ready".
- the `record_drafts` read replaced by `pass`: the P609 `record_drafts` case raises KeyError on `q[0]["draft"]` (a crash, not a named FAIL line).

## Null control

At the merge base `policy_refusal` has `last[name]=` overwrite and no "still a draft" arm. In the self-test, all-SUCCESS in either order reaches the review branch; a non-draft entry makes no `gh pr ready` call; a recorded `draft: False` is kept by `record_drafts`.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test` exits 0 at the head; its P608 and P609 lines print `ok` (9 lines).
- `tools/pr/prepr.sh` rc=0 with `PREPR_SKIP_CLOSURES` set in the environment: the closures step printed "skip ... PREPR_SKIP_CLOSURES is set"; the interpreter's missing homeassistant module was not separately confirmed.

## Red checks

none

## Forward-carry

none

## Friction

none

## Architecture score

n/a: no budget or gate rise.
