record: RCA for the orphaned-handoff class (N-orphaned-handoff)

Class `N-orphaned-handoff`, round 10. Document only: `dev/audit/rca/N-orphaned-handoff.md` (257 lines). No policy, code, roster or config change in this handoff.

What it establishes:

- Re-measured at 18:00Z: `bus.sh orphans --min-age-h 0` reports 12 stranded, five aged 41.9–96.6 h (earlycutoff 96.6, merge-pr-mandate 48.9, roster-ops 47.5, i5-docs 44.3, rca-harness-friction 41.9); `gh pr list --state all --head fix/<topic>` and `-pr` return nothing for all five. `earlycutoff` is content-covered by #2397 (`git cherry`: equivalent; 52 added lines all on main), so 11 of 12 are genuine.
- Corrections to the brief: the detector was not never-blind — 143 passes printed `bus.sh orphans unavailable (exit 1)` from 15:50Z Oct 18 to 06:06Z Oct 19 (14.25 h), reading a finding as instrument failure. The board is 4,073,591 B, 31,303 `OWED` lines over 236 refs, `DISPATCH LIST: 31343`; 179 refs already have a pull request and a merged, disposed ref still prints 144.
- Process state (c): `orchestrator.md` §5b's opener duty was followed — `SEATS.md` 20:02Z Oct 18 ("PARKED under soft cap"), 01:52Z and 07:10Z ("Owed openers remain … cap 6; 5 open now") show it read and queued — and did not produce the opening; two openers were dispatched at 11:33Z and ended `Terminated: 15` at 11:50Z with no retry.
- Cost test: 5 s/pass is 1.65 h per six-day round at the measured 8.25 passes/h (2.4 h at the nominal 300 s cadence), under 5.13 measured seat-hours × P=1.0 (`R9-ORPHAN-HANDOFF`'s r9-ux-10; class frequency 7 in R9, 11 in R10).
- Countermeasure as design: `handoff-no-pr` extends the machinery design's §6.3 (not a second ledger) with age ≥24 h `DISPATCH` and ≥48 h owner flag — the thresholds are tvofi's, not set here — an opener-attempt writer, a content-covered close, `design-build` as a new kind for state (a), and the availability contract (an unreadable store is `UNREADABLE`, never a clean board and never silently a finding).

## Head

5c500b7917145cb266762bf7a02836d2b2e50864

## Mutation proof

n/a: document only; no production check changed.

## Null control

The record's prototype (`fold_demo.py`, scratch, not carried) is silent on `r10-trust-relative` (merged #2435, disposed), `r10-tick-drivers` (merged) and `audit-r10-roster` (0.4 h), and its GREEN arm closes the four genuine refs when a `fix/<topic>` head is supplied. The bus's own null control is its `orphans: 0 stranded` summary.

## Figures

- `bash tools/audit/seat/bus.sh orphans --min-age-h 0`
- `gh pr list --state all --head fix/<topic> --json number,state`
- `wc -c -l ~/hpo-orch/r10s3/orch/tick/tick.txt`
- `grep -c '^-> OWED:' ~/hpo-orch/r10s3/orch/tick/tick.txt`
- `grep -c 'bus.sh orphans unavailable (exit 1)' ~/hpo-orch/r10s3/orch/tick/tick.log`
- `git cherry origin/main refs/hpo-orphans/handoff/r10-earlycutoff-coverage`
- `gh pr view 2397 --json number,state,files`

## Red checks

none.

## Forward-carry

- The machinery design (`dev/audit/design/orch-machinery/DESIGN.md` at `09174d94`, §6.3/§6.4) receives §5.1–5.3 and §5.6; §5.5 is a new kind and §5.4 a `bus.sh` content-arm defect. Carry: R10-ORCH-MACHINERY.
- §3's (d) observation (R10-ROSTER-OPS' brief gained the `state_docs.py beat` deliverable 41 h after its handoff at `541868d6f`) extends the §6.4 reconciler: pin the brief at handoff. Carry: R10-ROSTER-OPS.
- `dev/audit/config/bugclasses.json`'s `rca` citation for `N-orphaned-handoff` still names only `R9-ORPHAN-HANDOFF`; adding this record is a later config change. Carry: dismissed: config change, outside a document-only handoff.

## Friction

none.
