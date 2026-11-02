Record PR for the v7.1.1 stamp batch: adds the #3048 pre-flight waiver note to its delivery row, records #3091's own row, and drops the answered #2674 carry file (`dev/programme/carries/carry-2674.json`), whose close comment answers it. The deletion is this PR's intended act, not a merge artefact: it is the subject of commit 806110c00 and of the title in `dev/programme/delivery/3091.md`. This round merges origin/main and the moved handoff ref (72c6eea, a delivery-row edit only) into the head (conflict in `dev/programme/delivery/3048.md`: main now records #3048 as merged, so the row keeps main's merged line and the waiver note beneath it).

## Head

cc46fbb8becea68ef86efdc235a9d96aa7983c77

## Mutation proof

n/a: record-only diff, no production line or fix. Re-adding the pruned `carry-2674.json` entry to `tests/closures.json` while the file stays deleted is the PHANTOM the prune removes.

## Null control

n/a: no quantified claim. The unmodified tree (origin/main) carries the file and its closure entry, which stay consistent.

## Figures

none

## Red checks

Concluded red at PR head 645643590632a8895affebdb1d81fc9d0f42fe66 (runs 41352537181 and 41352537802): `gate` (two runs) and `pr-contract / pr-contract`. Answer: `gate` fails only because it re-runs `pr-contract`; `pr-contract` refused because the body's `## Head` named an older head (d6c8c69b) than the pull request's tip, the push-order window `prepr.sh` documents. The cheaper detector is `tools/pr/prepr.sh` step 7 (`--body-check`), run here against the new head and standing at no new cost. The earlier reds on b889290f (`governance / instrument-self-tests`, `tests / fast (3.14)`, `tests / closures`, `tests / closures-autofix`) were the branch lacking main's later commits and the pruned PHANTOM `carry-2674.json` closure entry; both are repaired by merging main and the prune, with `python3 tests/entities.py` and `python3 tests/closure.py selftest` as their detectors.
- `governance / delivery-status`: red because `python3 -I -S tests/delivery_status.py --check` reports #3065 OVERDUE (12 commits since) with a longer pending list of merges on main still owed a row; it grades main, not this diff, and the check is not a required context. This diff touches `dev/programme/delivery/3048.md` only to add the waiver note beneath main's merged line and adds #3091's own row, neither of which can clear another PR's overdue row. The cheaper detector is that same command, run locally at no standing cost; the rows are the orchestrator's to write at each merge (`delivery-status-tracking.md`), so none are written here.

## Forward-carry

none

## Friction

none
