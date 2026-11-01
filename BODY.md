Record PR for the v7.1.1 stamp batch: adds the #3048 pre-flight waiver note to its delivery row, records #3091's own row, and drops the answered #2674 carry file (`dev/programme/carries/carry-2674.json`), whose close comment answers it. The deletion is this PR's intended act, not a merge artefact: it is the subject of commit 806110c00 and of the title in `dev/programme/delivery/3091.md`. This round merges origin/main and the moved handoff ref (72c6eea, a delivery-row edit only) into the head (conflict in `dev/programme/delivery/3048.md`: main now records #3048 as merged, so the row keeps main's merged line and the waiver note beneath it).

## Head

d6c8c69b1a2119e9e41feaa63cfd4a9f0018d7f9

## Mutation proof

n/a: record-only diff, no production line or fix. Re-adding the pruned `carry-2674.json` entry to `tests/closures.json` while the file stays deleted is the PHANTOM the prune removes.

## Null control

n/a: no quantified claim. The unmodified tree (origin/main) carries the file and its closure entry, which stay consistent.

## Figures

none

## Red checks

Four failing check runs stand on b889290f (run 41311309577), the earlier head of this branch cut from base fb0a6d5a3; ba27089a has no CI beyond the skipped `arm` check. Each is answered the same way: the red was the branch lacking main's later commits (it deleted `dev/programme/carries/carry-2674.json` while the closure recordings and the policy fixtures it was cut beside predate main's 44aaa080a), and this head merges origin/main f04b25a00 (conflict only in `dev/programme/delivery/3048.md`, resolved to main's merged row plus the waiver note). The cheaper detector already exists in each case and costs nothing new: `tools/pr/prepr.sh` step 6d (`ci predict`) and `python3 tests/closure.py selftest`.

- `governance / instrument-self-tests`: PIN lines "FIXTURE VACUOUS" from the policy lint; at this head `node tools/policy/policy_lint.mjs --fixture` prints "FIXTURE ok: 93 error(s) hold 258 pins" and `prepr.sh` step `policy_lint` is ok.
- `tests / fast (3.14)`: `tests/closure.py selftest` and `tests/entities.py` failed; at this head `python3 tests/entities.py` prints ALL 2518 ENTITY CHECKS PASSED and `python3 tests/closure.py selftest` prints ALL 117 closure shrink pins PASSED.
- `tests / closures`: PHANTOM `tests/entities.py: dev/programme/carries/carry-2674.json`. The deletion is intended (this record PR drops the answered #2674 carry; only `dev/audit/rca/R10-RCA-ROSTER-SYNC-ORPHANS.md` and `dev/programme/triage/s6-batch1.md` still mention it as prose, and `tests/entities.py` does not name the file), so the closures entry is pruned with it; CI re-records every closure on this FULL diff.
- `tests / closures-autofix`: the autofix of the same PHANTOM; no standing cost beyond the above, and the prune leaves it nothing to repair.

main's own run at f04b25a00 was still in progress when this body was taken, so no red of main's is claimed or excused here.

## Forward-carry

none

## Friction

none
