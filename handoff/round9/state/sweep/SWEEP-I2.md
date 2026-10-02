# Sweep: I2 — "A measured closure or scope diverges from the real dependency graph"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Ledger class (`I2`,
`tools/audit/bugclasses.json`): rounds 2, 3, 5, 7; 6 prior instances (R2
D3-09, R3 D3-FLAKE, R5 D3-01, R5 D3-02, R5 R5-INST-01, R7 R7-INSTR-01);
status `open`, detector null, barrier null. This round's finding: D14-s5-01
(verified, medium).

## Enumerator

Reused verbatim from the D14-s5 finder seat (`handoff/audit-r9-evidence`,
`tools/audit/round9/D14/s5/closure_divergence.py`): re-records every listed
Python script under `strace -f -y`, normalises each read with the
production `closure._rel`/`_is_real_file`, and asks the production
`closure.select([F])` about every read file missing from the recorded
closure. No path fix needed (the script takes no directory-depth-relative
`HERE.parents[...]`).

```
$ python3 tools/audit/round9/D14/sweep/I2/closure_divergence.py
RESULT seams=31 count
RESULT seams_by_reader[python-child]=31 count
RESULT seams_on_measured_files=31 count
```

Reproduces the finding's own number (31) exactly, on the default script set
(`doc_claims.py`: 9 seams via its `plan_view.py` child; `deployment_shape.py`:
22 seams via its own `-P --driver` child).

## Positive control

31/31 re-found. Historical ledger instances (R2 D3-09, R3 D3-FLAKE, R5
D3-01/D3-02/R5-INST-01, R7 R7-INSTR-01) were not re-run at their pre-fix
commits by either the finder or this sweep (finder's own "Could not finish";
carried forward here per the brief's "historical instances only if the
ledger has the class" and the no-heavy-rerun rule — re-deriving 4 rounds of
pre-fix git-archive exports for a class already well past the N>=3 bar is
not worth the wall-clock).

## Null control

```
$ python3 tools/audit/round9/D14/sweep/I2/closure_divergence.py --scripts typing_ruler,structure,guard_pins
RESULT seams=0 count
```

## Perturbation

```
$ python3 tools/audit/round9/D14/sweep/I2/closure_divergence.py --perturb union
RESULT seams=0 count
$ python3 tools/audit/round9/D14/sweep/I2/closure_divergence.py --perturb drop
RESULT seams=32 count
```

`union` (the fix shape: fold every traced read into the recorded closure)
takes seams to 0; `drop` (remove one recorded file, a one-line
re-introduction) takes it up by one, to 32. Both directions match the
finder's report exactly.

## Baseline vs main

`git diff 1936d5ca..origin/main --stat` touches only
`custom_components/heatpump_optimizer/{button,coordinator,entity}.py` and
the card; none of `tests/closure.py`, `tests/closures.json`,
`tests/derive_closures.sh`, `tests/deployment_shape.py`, `tests/doc_claims.py`
changed. All 31 seams still exist on `origin/main`.

## Disposition — every returned seam

All 31 seams are on the two measured scripts named above (`doc_claims.py`: 9;
`deployment_shape.py`: 22), every one a `python-child` read the in-process
`sys.addaudithook` recorder cannot see (only the node lane records under
`strace -f`). All 31 are **instance** (the finder's own single finding
groups them as one mechanism, per COMMON.md's phenomenon-grouping rule); 0
`guarded`; 0 `not applicable`. The heavy set the finder also measured
(`entities`, `features`, `harness_headers`, `config_flow_steps`,
`finite_boundary`: 883 further seams) is a different, wider surface the
finder itself did not fold into D14-s5-01's own count — left as the
finder's own lead, not re-dispositioned here (D3/D9-style heavy re-measurement
avoided per the no-heavy-rerun rule).

## Count

N = 1 verified finding (D14-s5-01) + 0 additional sweep-confirmed instances
on the default set (re-finds exactly the finder's own 31, no more) = **1**.
Ledger class, status `open` (not `barriered`), so the "any instance of a
barriered class" trigger does not apply. Per-round count keeps **rca:
false**, matching the brief. As with P7 above: I2 has now recurred in 5 of
6 rounds (2, 3, 5, 7, 9) with no barrier ever built — flagged for whoever
owns the ledger's cross-round view, same caveat as P7's sweep.

## Barrier proposal

The finder's own: wrap `--exec-record` in `strace -f -y` on Linux, union
the result with the existing audit-hook set. Cost: 9.4s strace wall vs 5.9s
audit-hook seconds on the default set (provisional, finder's own number,
not re-measured here). Not built here (N < 3 this round).

## Gate seconds

~a few seconds per script under `strace`; the default-set run above
completed well under a minute.
