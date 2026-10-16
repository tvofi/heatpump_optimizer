Why this change, and what it measures.

`custom_components/heatpump_optimizer/early_cutoff.py`'s release/detach path is
the code `#2329` (`fix/r10-registry-leak`) added: `detach` drops the room
listener **and** the wiring that reaches the coordinator (`held.wiring = None`),
`_changed` guards on that wiring, and `allow_on` refuses to read a wiring that
was dropped at unload. `tests/features.py` reached that path only through the
`_ec_freed` gc/weakref pair, which pins the coordinator's release but asserts
nothing about *what* `detach` clears, and nothing fired the registered
listener's own callback after `detach`. This adds four direct assertions.

The coverage context that motivated it. `early_cutoff.py`'s behavioural
coverage is single-sourced to `tests/features.py`: the gate's `coverage` job
reuses a script's per-script data when no changed file is in its measured
closure, and a diff that changes no file under `custom_components/` does not
re-run `features.py`. When the reused data comes from a base that predates the
`#2329` code, the module's 29 features-only lines fall out of the union and the
Silver rule's 95 % per-module floor goes red — the `#2320` finding in
`## Figures`. This PR neither removes those lines' single source nor changes the
module's line set; it upgrades the release/detach path from incidentally covered
to explicitly asserted, so a mutant of that path is killed by a named check
rather than by the freeing side effect alone.

## Head

`ecaf178cbd4eef5e3b30425bd4693bef8ceb4b24`.

## Mutation proof

`PYTHONPATH=tests/hastub python3 tests/features.py` against three mutants of the
path, applied together (`held.wiring = None` -> `pass`; `if held.wiring is not
None:` -> `if True:`; `if not on or held.cut_at is None or held.wiring is None:`
-> drop the third disjunct). The message of the fix is deleted, the closure
(`tests/features.py`) run, the line restored. Result: **4 of 4142 FEATURE CHECKS
FAILED** (baseline: `ALL 4142 FEATURE CHECKS PASSED`). Three are the new checks:

- `detach drops the room listener and clears the wiring that reaches the coordinator`
- `a room event after detach is a no-op through the wiring guard, not a crash`
- `allow_on returns the plan's value when the record carries no wiring (unloaded)`

The fourth, `unloading the entry frees the coordinator the cut-off record was
keyed by`, is the pre-existing `_ec_freed` check the new pair sits beside.

## Null control

The unmodified tree returns `ALL 4142 FEATURE CHECKS PASSED` (4138 before this
PR, +4 new). Inside the added block, a record that is armed but **never**
detached still delivers the room event and cuts (`null control: a record never
detached still delivers the room event and cuts`), so the wiring guard is doing
work rather than passing vacuously.

## Figures

- `main@81ae048e8 early_cutoff.py 157/157 = 100.00 %, missing []` — rule: the
  `coverage.json` the `coverage` job uploads for the merge commit, read by
  `tests/coverage_ratchet.py`'s `read_module_percent`. Command:
  `gh run download 38922453927 --name coverage-json --dir <d>` then
  `python3 -c "import json;d=json.load(open('<d>/coverage.json'));print([ (s['covered_lines'],s['num_statements'],e.get('missing_lines')) for n,e in d['files'].items() if n.endswith('early_cutoff.py')])"`.
- `#2320@353f7f3c4d early_cutoff.py 128/157 = 81.53 %, missing 29` — same
  instrument over the `coverage` job's artifact for that run
  (`gh run download 38929983680 --name coverage-json`). The 29:
  `[178, 179, 181, 182, 197, 199, 206, 218, 219, 221, 224, 233, 234, 236, 243,
  248, 269, 270, 272, 276, 277, 279, 285, 286, 314, 316, 318, 319, 321]`.
- `#2320@353f7f3c4d: tests/features.py reused, not measured` — the `coverage`
  job's log names it: `SKIP tests/features.py (closure: 134 files, no changed
  file is in its measured closure)` and `reused tests/features.py's coverage
  from the base`. The three scripts that did re-run are `arch_score.py`,
  `arch_score_head.py` and `entities.py` (all structural), so the union carries
  no behavioural reading of `early_cutoff.py`, and the 29 features-only lines
  fall out.
- `scoped gate for this diff: MODE: SCOPED -- 2 script(s) run` — `RUN
  tests/features.py`, `RUN tests/entities.py` (`python3 tests/closure.py select
  --diff $(git merge-base origin/main HEAD) --workdir <d>`). `features.py` is in
  scope here, so the `coverage` job re-measures it and `early_cutoff.py` returns
  to its measured 100 % on this branch.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.

## Red checks

- `coverage-ratchet` on `#2320` (`early_cutoff.py 81.53 %`): the cheaper
  detector already exists and is the finding itself — the ratchet's per-module
  floor. The cause is not in this module's lines (main reads 100 %); it is the
  `coverage` job's per-script reuse handing the ratchet a base whose
  `features.py` data predates `#2329`. That mechanism is `#2320`'s to answer
  (a fresh coverage base / `update-branch`), not this PR's; this PR only makes
  the release/detach path explicitly asserted so a mutant of it cannot survive
  on the freeing side effect alone. Named here as `defect-root-cause.md`'s
  second trigger requires.

## Forward-carry

none.

## Friction

none.
