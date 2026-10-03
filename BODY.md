R9-F10.13: the mutation lane's instrument findings of 2026-10-03. Part of #201.

_Requested by **tvofi**_

Three arms, no new job, no new driver run, no new runner minutes. The roster brief orders them A, B, C; the stamp arm (C) is the 2026-10-03 carry on the same roster entry.

**(A) A mutant can no longer kill the triage mark that names its own line.**
- `tests/entities.py` checks that "every mark still names a mutant this tree generates". It reads the tree it runs in. A mutant on a line a `survivor_triage` mark names changes that line, so in the mutated tree the mark is stale and the check fails. The driver then reports the mutant killed by a check that saw only its own mark go stale. #1867's review measured it on the `payload.py` mark: 1 of 2086 checks failing.
- Fix, in `tests/mutation_table.py` (the smaller diff of the two the brief allows; `tests/entities.py` has three open pull requests on it): `triaged_site(triage, mut)` is `disposition_matches` on the site's anchor, the same key and `old` pin every disposition uses. The sampled pool in `main()` leaves out such sites and prints how many (`N candidate site(s) hold a survivor_triage mark and are not driven`).
- The alternative, judging staleness against the unmutated tree inside the check, needs the unmutated text: `git show HEAD:` goes blind to an uncommitted edit of the marked line, and a stale-mark check that stops reading the working tree is a weaker check for the sake of the lane.
- `--drain` and `--pin-killed` pools are built from unpinned sites, so they never held a triaged one.

**(B) Pin re-verification, report only.**
- `mutation-nightly` draws its sample from every generatable mutant, `killed_by`-pinned sites included (595 pins of 5504 sites when measured, about one in nine), and until now discarded what the draw learned about them.
- For a pinned site the pool drew, `main()` now drives the pinned script first (so another driver's kill cannot leave the pin unread; a mutant is killed iff some driver kills it, so no verdict moves) and `drive()` records each (mutant, script) outcome. `pin_reverification` prints, per pinned site: reproduced (the script killed it); `PIN NOT REPRODUCED` (the script ran and did not kill, or the mutant LIVES); or `pin not re-verified` (the budget cut the mutant, the script timed out, or another driver killed it before the script ran). It is never a confirmation unless the pinned script itself ran and killed. A final `PIN RE-VERIFICATION:` line counts the three.
- It prints and exits as before. It never edits, deletes or rewrites a pin; the disposition (re-pin, triage, a new test) is a human's (`ci-autofix.md`).
- `mutation-nightly` gets a `--seed "$(date -u +%Y%m%d)"` as `mutation-ledger` already has, and a step that copies the three line kinds to the step summary and emits a `::warning::` per `PIN NOT REPRODUCED`. The draw stays at `--max 40`. The constant default seed (20260911) drew the same sample every night, so once F10.12's budget binds the same tail would stay unevaluated for good; the rotation is the mitigation the F10.12 review asked for and is measured against the ledger's: `ledger` rotates by `--seed "$(date -u +%Y%m%d)"` too (`tests.yml`, `mutation-ledger`).
- No pin share is reserved. About 1 in 9 sites is pinned, so a draw of 40 holds about 4 to 5 on average and the rotation walks the stock; reserving a share would also dilute the survivor fraction the nightly's cap judges.
- Carried from F10.12: a re-drive that ends `SKIP-BUDGET` is "not re-verified" and one that ends `SKIP-TIMED-OUT` is not a confirmation, both in `pin_reverification`. Arm A and B edit `drive_pool`'s neighbours but not `drive_pool`; its `SKIP-BUDGET` marking is untouched, and F10.12's checks still pass at this head and fail without it (mutation proof, M7).
- First case, the legionella pin. `LegionellaGuard.async_track` `GUARD_OFF` `43323b87` was pinned to `tests/harness_headers.py`, which does not kill it on Linux. The orchestrator's measurement branch `measure/legionella-pin` (main plus the mutant), Tests run 37133568644, slow job: `tests/dst_checks.py` ends `1 of 131 DST / QUARTER-GRID CHECKS FAILED` on `legionella: a credit a true 2 minutes after the last is refused across the spring gap`, and `tests/features.py` ends `1 of 3670 FEATURE CHECKS FAILED`. `dst_checks.py` is not in any recorded closure of `legionella.py`, so it cannot be the driver; `tests/features.py` is. The row is re-attributed to `tests/features.py` with that evidence in its `reason`; harness_headers ended `ALL 95 HARNESS HEADER CHECKS PASSED` in the same job. The failing `features.py` check's name did not print in the job log, so a runner re-drive is still owed (see Uncertainties in the hand-off); the nightly will name the pin `PIN NOT REPRODUCED` if `features.py` is wrong.

**(C) `stamp.py --dry-run` runs the register generator.**
- v6.7.15's dry run passed and the real stamp refused at `tools/audit/round4/D6/claims.py` (a 3.12 f-string under 3.11), because a dry run returned before any step that runs the generator. The cheaper detector now exists: `dry_run_register` copies the working tree (`git ls-files --cached --others --exclude-standard`) into a temporary directory, makes the stamp's own writes there (VERSION, manifest, card, both claim files), and runs `regenerate_register` in it under the same interpreter. Nothing in the checkout changes; a generator failure refuses with `rule register`, as the real stamp does.
- `--dry-run`'s help and the docstring (rules 7 and 8) say what it now does and still does not (no commit, so no rule 7 `env_drift --claims-only`).

## Head

059d435af73e6c042d47b00781441d8e90eba0ec

Merge base `9fed34071` (`origin/main` at 9fed34071, `date -u` 2026-10-03T22:20:42Z, unchanged since this branch was cut). All figures below are at this head unless a row names another tree. The scoped selection is `MODE: FULL` because `.github/workflows/tests.yml` is a gate file; CI runs everything, and the lines in `Mutation proof` are what a Mac can run.

## Mutation proof

Failing first. At the merge base with this head's `tests/entities.py` (the checks, without the fix): `PYTHONPATH=tests/hastub python3 tests/entities.py` gives rc=1, `3 of 2133 ENTITY CHECKS FAILED`, naming
- `a site holding a survivor_triage mark is triaged and not drawn ...` (`out=(None, None, None, None)`: no `triaged_site`)
- `the nightly reports a pin its script did not kill, and never reads a site the budget, a timeout or another driver left unrun as re-verified` (`lines=[]`)
- `main drives a pin's killer first, records and prints the re-verification, and mutation-nightly rotates its seed by date and surfaces the report`

The stamp arm's checks live in `stamp.py --self-test` and fail without their code by mutants S1 and S2 below.

Breaking the fix, each mutant in its own detached worktree of this head, `tests/entities.py` (rc, then the failing check):

| mutant | what it breaks | result |
|---|---|---|
| M1 | `triaged_site` returns False | rc=1, `1 of 2133`: the arm-A check (`out=(False, False, False, False)`) |
| M2 | `main()` draws `list(drawn)`, not the non-triaged | rc=1, `1 of 2133`: the arm-A check |
| M3 | `pin_reverification` no longer reports a LIVES verdict | rc=1, `1 of 2133`: the pin-report check (its first fixture let this mutant survive: its LIVES site had a recorded run; the fixture now gives it none, and M3 is killed) |
| M4 | a pin counts as reproduced unless its run came back False | rc=1, `1 of 2133`: the pin-report check |
| M5 | the pinned script is not moved to the front | rc=1, `1 of 2133`: `main drives a pin's killer first ...` |
| M6 | `--seed "$(date -u +%Y%m%d)"` removed from `mutation-nightly` | rc=1, `1 of 2133`: the same check |
| M7 | `verdict[j] = "SKIP-BUDGET"` removed from `drive_pool` (the F10.12 control) | rc=1, `3 of 2133`: `a budget too small for its pool ...`, `a budget cut falls on an anchor boundary ...`, `a twin granted with its anchor ...` |
| S1 | `--dry-run` no longer calls `dry_run_register` | `stamp.py --self-test` rc=1: `register dry run: main calls it before returning from --dry-run` |
| S2 | the copy never gets the stamped VERSION | rc=1: `register dry run: the copy carries the stamped version and claim files` |
| S3 | `regenerate_register(..., cwd=copy)` loses the `cwd` (the generator would re-record the real register) | rc=1: `register dry run: the default runner's working directory is the copy, not the checkout`; the first version of the self-test missed this, its `runner` seam being handed the copy regardless |

The F10.12 control the brief asked for: M7 is the "SKIP-BUDGET marking removed" arm, and at this head, unmutated, `ALL 2133 ENTITY CHECKS PASSED` includes the two `drive_pool` checks (`a budget too small ...` for a too-small budget and for an exclusive driver, `exclusive` in its `out`).

No production line is added (`custom_components/` is untouched), so `mutation_table.py --scope changed --base origin/main` has no site to pin; the brief's request to pin "the sites this change adds" is empty by construction.

## Null control

- Arm A's end-to-end claim, through `main()` on `payload.py`'s one marked site, `tests/entities.py` as the only driver (instrument: `$S/selfkill.py`, below):
  - at the merge base: `ok custom_components/heatpump_optimizer/payload.py:46 GUARD_OFF  -- killed by tests/entities.py`, the `if TYPE_CHECKING:` mark's own line, with `baseline tests/entities.py: rc=0 failed=0` and the null control surviving. (The run's `process_worker.py` survivor is the filler site that gives the pool a comment line for the null control, and its cap breach is that filler's; neither is the claim.)
  - at this head: `1 candidate site(s) hold a survivor_triage mark and are not driven`, `no mutant is both generatable and drivable`, `MUTATION TABLE PASSED (empty pool)`.
- The staleness check itself is unchanged and still fires, so the fix hides nothing the check judges: 
  - on an unmutated tree with the payload mark's `old` pin edited (a planted stale mark, in a scratch worktree of this head), `tests/entities.py` gives rc=1 and names `and every mark still names a mutant this tree generates, pin and all (#1217)` with `stale=['custom_components/heatpump_optimizer/payload.py:<module> GUARD_OFF e1433e05']`. The arm-A check also goes red there, as it must: the planted pin no longer matches the site.
  - on a tree whose `payload.py` line `if TYPE_CHECKING:` is mutated to `if False:` (the mutant itself, in a scratch worktree of this head), the same check fails with the same `stale=` list: the mutant would still kill its own mark if driven, which is why the pool must not drive it. The arm-A check is red there too, because the mutated tree no longer holds the site.
- A site with a pin that did reproduce: `$S/pinredrive.py tests/guard_pins.py,tests/doc_claims.py` on `topology.py:_tr` `RETURN_DEL`, pinned to `tests/guard_pins.py`, prints `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced, 0 not re-verified`.
- The same run with the pin planted wrong (`killed_by` edited to `tests/doc_claims.py`, in a scratch worktree, nothing committed) prints `PIN NOT REPRODUCED ... pinned to tests/doc_claims.py, killed by tests/guard_pins.py -- ... the pin is untouched` and `0 reproduced, 1 not reproduced`.
- `stamp.py`'s dry-run generator step, at this head, `python3 $S/dry.py` (`stamp.dry_run_register` for the next patch version on the real tree, `claims.py` run in the copy): `DRY RUN OK 3.14.7` on the venv interpreter; with a syntax error appended to `claims.py` in the checkout (restored after): `REFUSED stamp refused (rule register): tools/audit/round4/D6/claims.py failed with exit 1: SyntaxError: '(' was never closed`. Under the system 3.11.5 without the test dependencies it refuses on `ModuleNotFoundError: No module named 'voluptuous'`, which is the same detector firing on the environment.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head: `ALL 2133 ENTITY CHECKS PASSED` (rc=0); this PR adds 3 of those checks (the failing-first run above counts 3 failures at the merge base, the same 2133 checks).
- `PYTHONPATH=tests/hastub python3 tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 95 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/mutation_table.py --normalize` leaves the tree byte-identical (`git status --short` shows only this PR's files).
- Pinned share: 595 `killed_by` rows (`find tests/mutation_ledger/killed_by -name '*.json' | wc -l`) against 5504 candidate sites (the `candidate sites` figure `python3 tests/mutation_table.py --scope full` prints at its start).
- The measuring instruments are one-off probes kept in the seat's scratch (`selfkill.py`, `pinredrive.py`, `dry.py`); each is a few lines over `mutation_table.main()` / `stamp.dry_run_register` that replace `drawable` and `scope_files`, and names itself in its docstring.

## Red checks

`nightly-status` is the check this branch can turn red: it reads the scheduled lanes, and `.github/workflows/tests.yml` changes the `mutation-nightly` job it reports on. The new step is `if: always()` and exits 0 whatever the table prints, so it adds no failure path; a red `nightly-status` after this merge would be the nightly's own result, not the step's. The cheaper detector for a pin the nightly did not reproduce is the step summary and warning annotation this PR adds.

## Forward-carry

`none`

Nothing changes how a later stage must work. Two items are owed to the orchestrator rather than carried, and the hand-off message names them: a runner re-drive of the legionella pin against `tests/features.py`, and the `equivalent` branch of `survivor_gaps` in `tests/mutation_table.py`, which no sampled caller reaches now.

## Friction

`ci-autofix`: `unclear`: the brief names `tests/entities.py:28993` for arm A; the line has moved with every merge, and the stable anchor is the check's text ("every mark still names a mutant this tree generates").
