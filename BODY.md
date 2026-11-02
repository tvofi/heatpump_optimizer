Record PR for the v7.1.1 stamp batch: adds the #3048 pre-flight waiver note to its delivery row, records #3091's own row, and drops the answered #2674 carry file (`dev/programme/carries/carry-2674.json`), whose close comment answers it. The deletion is this PR's intended act, not a merge artefact: it is the subject of commit 806110c00 and of the title in `dev/programme/delivery/3091.md`. This round starts from handoff cc46fbb8 (origin/main already merged in; main has not moved since, so no second merge) into the head (conflict in `dev/programme/delivery/3048.md`: main now records #3048 as merged, so the row keeps main's merged line and the waiver note beneath it).

## Head

cc46fbb8becea68ef86efdc235a9d96aa7983c77

## Mutation proof

n/a: record-only diff, no production line or fix. Re-adding the pruned `carry-2674.json` entry to `tests/closures.json` while the file stays deleted is the PHANTOM the prune removes.

## Null control

n/a: no quantified claim. The unmodified tree (origin/main) carries the file and its closure entry, which stay consistent.

## Figures

none

## Red checks

Check-runs read at PR head 645643590632a8895affebdb1d81fc9d0f42fe66 (all 68, runs 41352537181 and 41352537802). Each of the four named reds, one by one:
- `governance / instrument-self-tests`: success at 645643590 (job 125490654606); the red was on the older head b889290f, which lacked main's later commits. Stale; repaired by merging main. Detector: `tools/audit/prepr.sh --self-test`, which prepr skips when the diff touches no instrument.
- `tests / closures`: success at 645643590 (job 125490601143); red on b889290f because `tests/closures.json` still listed the deleted `carry-2674.json` (a PHANTOM). This diff prunes that entry. Stale. Detector: `python3 tests/closure.py selftest`, run by prepr's closures step (skipped here as MODE: FULL, where CI re-records).
- `tests / closures-autofix`: skipped at 645643590 (job 125490602090), the bot job that repairs `tests / closures`; it has nothing to repair at this head. Stale.
- `tests / fast (3.14)`: success at 645643590 (job 125490600436); red on b889290f for the same phantom closure entry, found by `python3 tests/entities.py`. Stale.

Reds at 645643590 that remain: `gate` (jobs 125491371211, 125491186582, 125490596797) and `pr-contract / pr-contract` (jobs 125490904965, 125490611081). `gate` fails only because it re-runs `pr-contract`; `pr-contract` refused because `## Head` named d6c8c69b, older than the pull request tip, the push-order window `prepr.sh` documents. The cheaper detector is `tools/pr/prepr.sh` step 7 (`--body-check`), run here against this head with rc=0.
- `governance / delivery-status` (job 125490596113): red because `python3 -I -S tests/delivery_status.py --check` reports #3065 OVERDUE with a longer list of merges on main owed a row; it grades main, not this diff, and is not a required context. This diff only adds the waiver note under main's merged line in `dev/programme/delivery/3048.md` and #3091's own row. The cheaper detector is that same command, run locally at no standing cost; the rows are the orchestrator's to write at each merge, so none are written here.

## Forward-carry

none

## Friction

none
