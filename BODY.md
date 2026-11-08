Root-cause record for the third instance of the relay handoff-starvation class (2026-11-08): `dev/audit/rca/r10-relay-handoff-starvation.md`, the class entry `N-relay-handoff-starvation` plus its `_rca` row in `dev/audit/config/bugclasses.json`, and a read-only detector, `dev/audit/rca/relay_handoff_lag.py`. No tool under `tools/` is edited; the countermeasures to the relay and tick are proposals, not landed. Process state (d). Not read: the orchestrator's tick-loop and relay logs are outside the tree, so `relay=running` and `TICK-STALE behind=13` are the orchestrator's record, not re-read. Only #3308's delay (61 min) is measurable from refs; #3299 and #3310 read `uncarried` today and their 20 to 60 min is the orchestrator's figure.

## Head

3f1ec2907e1ff0c5eaabf2144144a36e3e214ca9

Main (origin/main 28596c569) had not moved relevantly since the cut; no second prepr run, per the owner's ruling.

## Mutation proof

n/a: no production code changes; the one new script is a detector whose null control is below.

## Null control

`python3 -I dev/audit/rca/relay_handoff_lag.py --self-test` builds a synthetic origin: a handoff carried after 2 min reads green, one after 40 min reads LATE at the 15 min limit, one never carried is `uncarried` and not scored. It prints `self-test ok: fast=2m (green), slow=40m (LATE at 15m), never=uncarried (not scored)`. On the real refs the same script scores #3308's handoff (r10-min-power-floor) late at 61 min and exits 1.

## Figures

- Lag table: `python3 -I dev/audit/rca/relay_handoff_lag.py --repo . --since $(date -u -d 2026-11-04 +%s)` at 2026-11-08T10:24Z printed 9 LATE of 10 carried and 4 uncarried; lags 717, 421, 394, 334, 158, 129, 61, 45, 35, 9 min. Rule: committer time of the first commit on the ancestry path from the handoff tip to the PR head, less the tip's committer time; an upper bound, not a measure of starvation. A sliding window: re-run, do not carry the number.
- #3297 freeze: `git merge-tree --write-tree origin/main origin/fix/r10-hotfix-cop-unmeasured` exits 1 (conflict) with main 367 commits ahead (`git log --oneline $H..origin/main | wc -l`); the head equals the verdicted head 2d010b09.
- Also registered the class id in finding.schema.json and audit-find.js (agreement lane: it refused the id missing from both enums; `node tools/policy/agreement.mjs` now prints `divergent=0`).
- Ledger: `python3 tools/audit/fold_ledger.py check` prints `fold_ledger: 0 violation(s)` (two violations before the `_rca` row and the trigger flag were added).
- `python3 tests/entities.py` at this head: 3 of 2665 checks failed (release ZIP, Pages workflow, coverage-job cache); `every tracked file is either measured or deliberately classified` is ok. These three are the failing set documented for this container's BASH_ENV/RUNNER_TEMP profile (same three at base in another seat's body); I did not re-run with `env -u BASH_ENV`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`.

## Unpinned sites

none: no line under custom_components/ is added.

## Red checks

none

## Forward-carry

none

## Friction

none
