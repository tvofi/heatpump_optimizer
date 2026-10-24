Root-cause record for #2671's two reds on Governance run 39996377402 (`wave-script`, `instrument-self-tests`), on a head `prepr.sh` and `ci_predict.py` predicted green. It records only; no check, script or workflow changes. Part of #201. Part of #2505 (the issue #2671 was part of; its Root cause section is posted there).

- **Analysis.** `dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md`: reproduction (section 1), three causes (2), process state (3), reach (4), cost test (5), countermeasures (6). Every figure it states is measured there against `origin/main` `f046076ad` and is not restated here.
- **Process state (c), three times.** `prepr.sh` steps 3e-3g ran and passed but grade a pinned grader with the head's copy, which is the push-to-main direction, while the pull-request run grades with the base's copy. `ref_privacy.py --check` runs in CI and in no local path. Base-pinning the agreement lane, followed as designed, leaves a new `SHARED_GRAMMARS` entry with no tree the required check passes (#2423 merged red).
- **Class.** I3 ("a required governance/CI check is skipped, runs a stale ref, or has a bypassable boundary"), the class of `R9-RC1-pinned-local`, whose countermeasure was steps 3e-3g themselves. `dev/audit/config/bugclasses.json` gains `R10-RCA-2671-WAVE-SCRIPT` in I3's `rca` and its `_rca` entry (status `proposed`, `landed` null), as `defect-root-cause.md` "Where it is recorded" requires. I3 is barriered, so this instance owes a change to the unit the barrier missed: countermeasures A and B below, not a new arm count.
- **Cost test verdicts.** A (base-pinned arm under CI's restore, keyed on the lane's own reader closure): build. A' (the same arm keyed on any wave-script pin): refused, its standing cost exceeds the expected defect cost. B (`ref_privacy.py --check` in the local path): build. C (an admissible route for a new shared grammar): no bounded defect cost; an owner decision, not a seat's.
- **Classification.** Both touched paths are under `tests/closure.py`'s `INERT` prefix `dev/audit/` and in no `INERT_EXCEPT` entry, so no closure records them.

## Head

`3054a111360906639522a45eac993d7b996b7372`: the root-cause seat's `a148b3fa8` (the RCA document), a merge of origin/main `144fb4f90` with no conflict, and one commit citing the RCA in `bugclasses.json`.

## Mutation proof

n/a: this records a cause and proposes countermeasures; it adds no check. The RCA's countermeasure demonstrations (section 1 and section 6) are the proofs the receiving groups re-run: arm A fires on `338c9ba49` merged into `fd7e289d0` and passes on null control #2669; arm B fires at `338c9ba49` and passes at origin/main.

## Null control

`python3 -I tools/audit/seat/ref_privacy.py --check` at this head (origin/main `144fb4f90` merged) prints `0 refused`; at `338c9ba49` it prints `1 refused` on `tools/audit/seat/ledger.py:726`. `python3 tools/audit/fold_ledger.py check` at this head prints `0 violation(s)`.

## Figures

- 1 refused at `338c9ba49`, 0 refused at this head: `python3 -I tools/audit/seat/ref_privacy.py --check`
- 0 mentions of `ref_privacy` in the local pre-PR path: `grep -c ref_privacy tools/pr/prepr.sh`
- 0 register violations, 120 rca entries: `python3 tools/audit/fold_ledger.py check`

## Red checks

none

## Forward-carry

- Countermeasures A (base-pinned agreement arm under CI's restore, keyed on the lane's load closure, with the `refused=3` live-origin/main trap) and B (`ref_privacy.py --check` locally), with their controls and cost figures, correcting #2671's own carry at index 1 of the same group: landed as `carry[2]` of R10-FLY-CIPREDICT-LAYOUT on `handoff/audit-r10-roster` at `42e45f420`, present at its tip `6ae3061f9`. Carry: R10-FLY-CIPREDICT-LAYOUT
- Countermeasure C (the agreement lane's deadlock for a new `SHARED_GRAMMARS` entry: UNREGISTERED under the base copy, DEAD when registered first; candidates (i) a pending-second-writer marker DEAD does not refuse, (ii) the registry moved to a code-owned data file read from the head). Queued to the roster seat and HELD there at 2026-10-23T22:01Z pending the orchestrator's confirmation of the destination; not on `handoff/audit-r10-roster` at `6ae3061f9` (that group's `carry` has indices 0-1 only). This pull request does not merge until it lands or is re-routed. Carry: R10-MERGE-SUBJECT-HARDEN

## Friction

none
