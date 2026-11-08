R10-RCA-STAMP-FLUSH-COST is the root-cause seat for the owner's ruling of 2026-11-07: a stamp that dispatches a whole Nightly run is a defect. It ran beside R10-FLY-STAMP-FLUSH-COST (#3296, merged `341da0721`) and never inside it. It edits neither `stamp.py` nor `nightly.yml`.

**The RCA the brief asks for already exists on main.** It is `dev/audit/rca/r10-rca-flush-dispatch.md` (`R10-RCA-FLUSH-DISPATCH`, #3285, merged `b4ec2f332`), and it covers all four parts:
- the named cause: the flush rule's unit was a job, while the dispatch API runs a workflow (triage P88, carried into #2836 / `6b1aa629f`);
- process state (c), with why not (b) and why not (d);
- a class search over 7 code callers, 1 of which over-reaches;
- the cost test: a generic dispatch-scope check refused under the bound (a built candidate was withdrawn), and a `proposal-triage.md` cost line proposed to the owner.

Its class row is `N-dispatch-overreach` in `dev/audit/config/bugclasses.json`. Writing `R10-RCA-STAMP-FLUSH-COST.md` beside it would have given one defect two RCAs for a reader to reconcile, so this seat did not write one. It re-measured every figure at its merge base and adds a section 7 to the existing document with what changed:
- **#639 was missing.** Run 42382408131, 2026-11-07T14:36Z, ran every lane: 1007 runner-min. It is not attributable to the stamp, because no tag follows it. With it, 11-07 had 8 dispatches and 4564 runner-min, and the whole flush window had 27 dispatches and 16916 runner-min, against the 26 and 15909 recorded before.
- **No dispatch since #3296 merged.** The `lanes=beat` payload has not yet run in production, so the next stamp is its first exercise.
- **The class search, re-run at `73365699a`**, finds the same callers and no new ones.
- **Neither cost-test verdict moves:** about 28 runner-h per cycle, against 27.

The register's `non_round_instances` count, `26 dispatches, at most 15909`, is false over its own stated date range, so it is corrected to 27 and 16916.

Nothing new to carry forward. Section 5's `proposal-triage.md` line is policy and still awaits the owner's decision, which `_rca` `parts_missing` already records. The issue's **Root cause** section is left to the orchestrator, as section 6 says. The brief named a new `R10-RCA-STAMP-FLUSH-COST.md`, but #3285 had already landed the RCA for this defect, so this seat amended that document instead.

## Head

`1b8e1600aa53eca36eab63293483a43a7468f0c0`, measured on 2026-11-08 at merge base `73365699a` origin/main has since moved, to `2a3c05644`. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so by the owner's ruling of 2026-11-07 the branch is not merged and prepr is not re-run because main moved. The figures from the Actions API were read on the same date.

## Mutation proof

n/a: this diff adds no production line, test or check. It is a measurement record and a register text correction. `fold_ledger.py check` reads the register and printed 0 violations on it.

## Null control

`python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py since 2026-11-08T04:48:27Z` prints `runs=0`. The same instrument over `since 2026-10-26T02:31:17Z` prints `runs=27`, so 0 is a reading and not a blind instrument. At the fix's merge base `d2e4d2d10`, the dispatch posted `json.dumps({"ref": "main"})`; at the head it posts `RECORD_BEAT_PAYLOAD`, which carries `lanes=beat`.

## Figures

- #639: 1007 runner-min. `python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py runs 42382408131`
- since the flush shipped: 27 runs, 16916 runner-min, 7 cancelled, 916 lost ledger runner-min. `python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py since 2026-10-26T02:31:17Z`
- since #3296: 0 runs. `python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py since 2026-11-08T04:48:27Z`
- 11-07: 8 dispatches, 4564 runner-min. This is section 1's seven-run figure, 3557, plus 1007. Independently, the jobs API's job timestamps summed to 273836 s over the same 8 runs, about 4564 min.
- class search: the same code callers as section 4. `git grep -nE '/dispatches|gh workflow run|createWorkflowDispatch|repository_dispatch'` at `73365699a`
- register: 0 violations. `python3 tools/audit/fold_ledger.py check`
- scope: `MODE: SCOPED -- 0 script(s) run`. `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`
- mutants: `MUTANT_CMD='python3 tools/audit/fold_ledger.py check' tools/pr/prepr.sh` reports `diff mutants: no survivor`. The diff adds no `.py` lines, so there were 0 sites and 0 survivors, and the wall time is that of a zero-site run. `unpinned sites` is skipped: the diff adds no unpinned mutation site.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED

## Red checks

none on this branch. One local prepr step refuses, and it is not this diff's: `closures` reports "failed while being recorded: tests/entities.py (exit 1)". `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `3 of 2665 ENTITY CHECKS FAILED` both at this head and at the untouched base `73365699a`, and the FAIL lines are identical at both. The three checks are:
- the coverage job's cache-reuse probe;
- the release ZIP build step;
- the Pages workflow probe.

All three run workflow shell steps inside this cloud container. This diff changes only an `.md` and a `.json` that no closure measures (`MODE: SCOPED -- 0 script(s) run`). CI runs `entities.py` on its own runner. Every other prepr step is ok or skipped, including `ci predict` (no red predicted), `pr-body`, `figures` and `carry`. This seat does not work around the refusal, and it is outside the seat's scope to repair.

## Forward-carry

none

## Friction

none
