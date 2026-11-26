# ADR-011: a surviving mutant is closed by one pin in its seam's suite, proven under its own patch

Groups: `R11-D3-PINS-solver`, `R11-D3-PINS-sysid`, `R11-D3-PINS-fabric`,
`R11-D3-PINS-plant`, `R11-D3-PINS-money`, `R11-D3-PINS-actuation`,
`R11-D3-PINS-inputs`, and the D3 carries of `R11-SEAM-cycle-reporting-p2` and
`R11-SEAM-store-p2`. This ADR fixes their shape, so no designer is dispatched
for the L and XL ones (`architect-planner.md` step 5).

## Context

The D3 wave judge (`handoff/audit-r11-judge-D3` at `a826f55f8c`) upheld
production mutants in ten modules that the full gate did not kill, all class
I1 (#3755). Each has a probe whose number moves under a one-line patch with
its null held. None is a production defect as judged: the production line is
right and no check would notice it going wrong.

Three facts constrain the fix.

1. `tests/mutation_table.py --scope changed` draws mutants only from
   production lines a diff touches, so a tests-only pull request draws none.
   The gate cannot prove these kills; the fixer must.
2. The wave's lines are at its baseline `92d38ecb64`. `d3_fnstate.py` reads
   which enclosing functions differ at a later ref (`## Figures` of
   `CHANGES-R5.md` for main and the open pull requests).
3. The survivor claim compares each gate log with a null that was red on its
   box (the judge's carry R11-D3-JUDGE-GATE). A mutant killed only by an
   already-red check reads as a survivor.

## Decision

1. **Tests only.** A D3 pin group edits no file under
   `custom_components/`. A pin that cannot pass on the unpatched tree has
   found a production defect; the fixer stops and carries it to the seam's
   owning group.
2. **Pin home.** A pin goes into an existing script whose recorded closure in
   `tests/closures.json` already reaches the mutated module, beside the checks
   of the same behaviour where there are any, else `tests/guard_pins.py`. No
   new test script: one would add a `tests/closures.json` row, a `tests/run.sh`
   line and a Linux-only closure derivation to each of seven pull requests.
3. **Ledger.** Each closed key gets its row under
   `tests/mutation_ledger/killed_by/`, named by module, function, mutant kind
   and key, as the existing rows are.
4. **Proof per finding, by the fixer.** Re-locate the patch by its text at the
   merge base; run the judge's probe under it; write the pin failing under
   the patch and passing without it; both runs in the body. A patch an
   existing check already kills at the merge base, or a probe whose number no
   longer moves, is a non-finding returned to the judge, not a pin.
5. **A pin asserts behaviour through the production entry point.** It never
   re-states the production expression (`tests/README.md`): a boundary pin
   feeds the tie value and asserts the outcome the probe measured.
6. **Order inside a group.** High and medium survivors first; a group that
   runs out of its window hands off what is built and carries the rest to a
   part 2, as `R11-SEAM-store-p2` was cut.
7. **The red-null question is not each group's.** R11-D3-JUDGE-GATE is a carry
   of `R11-SEAM-tests`, the owner of #3755: a stratified re-take on a quiet
   Linux box. A pin group claims its kill from its own pin under the patch,
   which holds whatever the re-take reads.

## Alternatives

- **One issue per production file, as the judge drafted.** Ten issues cut by
  file put `coordinator.py`'s survivors, which belong to five seams, under
  one owner, and each issue would need a disposition and a group anyway.
- **One group for all of them.** One pull request appending several hundred
  pins conflicts with every open pull request that touches the pin scripts
  and has no reviewable unit.
- **A new script per seam.** Refused in part 2.
- **Raise the mutation gate to full scope on pull requests.** An instrument
  change under the freeze, and `tests/mutation_table.py` states its cost; it
  is the class barrier's question, owed to the root-cause seat under #3755.

## Consequences

- `tests/guard_pins.py` is a hot file shared with the open pull requests that
  touch it; they land first and a D3 group rebases (`CHANGES-R5.md`, hot-file
  order). `fixer.md` steps 2 to 8 re-execute after that rebase.
- The kill rate of the mutation ledger is one of the round's holdouts
  (`plan_audit.py snapshot`): these groups can only raise it.
- No scored metric is predicted to move: dS 0 for every D3 group. A structure
  budget on a test script's size, if one is at zero headroom, is paid by
  placing pins beside the seam's checks in another reaching script, never by
  a raise.

## Scenarios served

`SCENARIOS.md`, "Test-suite reach (D3)": a changed production line is noticed
by a check.
