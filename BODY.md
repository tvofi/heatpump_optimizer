_Requested by **tvofi**_

Part of #201.

#1848 (F10.5, merged as 8fa06663) built `mutation-ledger-push` with a `stale_pins` rule that cannot land pins while a round is merging. In dispatch run 37050037132, `mutation-ledger` measured at aa7a8119 (18:49Z to 21:50Z) and printed `PIN KILLED: 39 pinned, 1 left unpinned`. `mutation-ledger-push` then checked out `main` at 03ba7f70. `stale_pins` dropped every pin whose killing script's recorded closure held any changed path. The two main killers' closures are broad (`tests/features.py` 123 entries, `tests/entities.py` 200), so all 39 were dropped, the job returned `skip-head-moved`, and `drain_report` reddened it (job 111044417786: `MUTATION LEDGER: skip-head-moved -- a measured slice did not reach main`).

**Choice: (a), plus a reach filter. (b) and (c) were weighed and not taken.**

- `stale_pins(pins, closures)` now drops a pin only when its killing script, in the **head's** recorded closures, no longer holds the mutated module, or the script has left the closures. This is the rule `drivers_for` used to choose that driver. A pin that fails it names a check the head cannot run against the site.
- Every remaining pin then goes through `apply_pins`'s existing re-key against the head's inventory: same anchor (file, scope, operator, digest, ordinal), same `old` text, not already disposed. A pin whose line changed or vanished is dropped there.
- An unreadable diff (`drain_changed` returns None: a measured head outside main's history) still applies nothing.

Against the risk of landing a pin that no longer kills: once a `killed_by` row is in the ledger, it is judged by anchor and `old` text alone (`completeness_problems`, `disposition_matches`). Nothing re-drives a standing row when its killer or any closure file changes. A pin that landed at aa7a8119, one merge before those edits, would have survived every one of them. The closure-wide rule therefore refused a pin for a hazard the ledger accepts for every row it already holds. It decided only *when* a pin may land, not whether the kill stays true.

The residual risk is the same as for any standing row: a merge between measurement and push that weakens the killing assertion without touching the site's line. (a) does not catch that, and neither does anything else in the tree for rows already landed. Closing it is (c)'s job.

(b), "module plus the killer's own file", keeps 7 of 39 on the real run (Figures). It is no sounder than (a): the killer's assertions also live in helpers and fixtures elsewhere in its closure. (c), re-driving the dropped pins at the new head, costs another drive of up to the 40-site slice. Under the reach-plus-re-key rule the real run has 0 pins left to re-drive. (c) is the instrument for the standing-row gap above, not for this defect.

The unfixed code also had a hole the new check exposes: a pin whose killer is absent from the closures read an empty closure, matched no changed path and **landed**. The second arm's null control `killer gone` is that case.

`.github/workflows/tests.yml`: the `mutation-ledger-push` comment stated the old rule. It is corrected; the comment is the only change there.

## Approval

Code-owned paths (`tests/mutation_table.py`, `.github/workflows/tests.yml`) need tvofi's approving review at the head, routed by the orchestrator under mandate 5951564627. No budget is raised.

## Head

98d9f1e16d8100664ed2ecce1c0084422946ea8d

It merges the code head 164f6575e02f107d1611137a7dde77ad4802a247 with `origin/main` 1655100779 (#1851, which touched `tests/entities.py` and `tests/closures.json`). The merge needed no hand resolution. The mutation arms below ran at 164f6575; `tests/entities.py` and `tests/structure.py` were re-run at this head.

## Root cause

**#1848**, process state **(c)**: the process was followed and did not produce the intended result. #1848 went through fixer, mutation proof and an adversarial review over two rounds. Its moved-head arm was tested, and mutants M4, M5 and M8 on `stale_pins`/`apply_drained` were killed. But the check's fixture gave each killer a one- or two-entry closure (`{"tests/x.py": ["f.py"], "tests/y.py": ["a.py", "tests/lib/"]}`), and the demonstration applied only on the measured head (`apply1 changed`, `apply2 skip-unchanged`).

The review missed the moving-head case because nothing in it drove the rule with the real `tests/closures.json` against a real stretch of `main`. In the real window, every one of the 7 first-parent merges aa7a8119..03ba7f70 touched `tests/entities.py`'s closure and 3 touched `tests/features.py`'s. The rule's precondition, "a killer's closure is usually untouched over a few hours", was never measured. The proof tested the predicate's logic, not its selectivity at production scale.

The countermeasure here is the new check. It drives 39 pins with both killers and every mutated module changed, the shape of the real run, and the real artifact was applied at 03ba7f70 with both codes (Figures). The cost test and any process countermeasure (e.g. "a filter's proof runs it once over the real table it filters") are `root-cause.md`'s seat, not this fix's.

## Mutation proof

Failing check first: at 164f6575 with `tests/mutation_table.py` restored from 03ba7f70 (the unfixed code; arm `red`), `tests/entities.py` printed `2 of 2082 ENTITY CHECKS FAILED`, rc=1:
- FAIL `mutation-ledger-push lands a drained slice on a main whose merges touched every killer's closure, and drops only the pins whose site or driver the head lost` -> `[('skip-head-moved', 0), ('changed', 1)]`
- FAIL `mutation-ledger-push applies a drained slice once, and on a moved main only the pins whose killer still reaches the mutated module` (the #1848 check, its moved-head arms rewritten to the new rule)

(At f4cca4dc the first check, run against the unfixed code in the worktree, also printed `1 of 2082` with the same value, before the fix existed.)

Mutants. Each was applied in a fresh clone of 164f6575 with origin set to GitHub, then `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/entities.py` was run. Runner: `/Users/timmalmstrom/hpo-seats/ledger-headmoved/scratch/runmut.sh`, out of tree, sha1 3182de26a344f550392a0f3f50a048fee6156232. Outputs are `r-<arm>.txt` beside it.
- M1, the `stale_pins` predicate replaced by `if False:` (drop nothing): `2 of 2082 ENTITY CHECKS FAILED`. Both checks above fail, the new one with `[('changed', 39), ('changed', 41)]` (killer gone and killer-no-longer-reaching both land).
- M2, the re-key's `entry.get("old") != site["old"]` removed in `apply_pins`: `2 of 2082 ENTITY CHECKS FAILED`. FAIL the new check (`[('changed', 39), ('changed', 40)]`: the edited line lands) and FAIL `mutation-autofix applies only a measured pin whose anchor, text and head this tree still has`.

Survivors on the sites touched: none. `tests/mutation_table.py` is not under the inventory's package (`custom_components/heatpump_optimizer/`), so the diff adds no candidate site.

## Null control

M0, a comment line added inside `stale_pins` (same runner, same clone form): `ALL 2082 ENTITY CHECKS PASSED`, rc=0. The unmutated head 164f6575 in the same form: `ALL 2082 ENTITY CHECKS PASSED`, rc=0. The real artifact with `main`'s code at 03ba7f70 returned `skip-head-moved` and wrote 0 paths (Figures).

Environment note: an earlier pass of the same arms in clones whose `origin` was the local worktree path failed 2 extra checks on every arm, null included: the #1471 window-reader pair, `no github remote on origin`. That is an artifact of the clone, so those runs were discarded and the arms re-run with a GitHub origin.

## Figures

At code head 164f6575, `origin/main` 03ba7f70, 2026-10-02 (re-checks at the merged head are named).

- Real run, fixed code: the artifact `mutation-ledger` from run 37050037132 (`gh run download 37050037132 -n mutation-ledger`; `pins.json` sha1 2f58628647ee6f8eed00abd66c3e3be7fe226dab, `head` aa7a81192325614999803e40e3cedc024e22ce2b), applied in a scratch clone at 03ba7f70 with this branch's `tests/mutation_table.py`, `changed` from `m.drain_changed(at, head)` (83 paths, equal to `git diff --name-only aa7a8119 03ba7f70f`): `stale_pins` -> `[]`, `apply_drained` -> `changed`. Then `git status --porcelain --untracked-files=all` showed 39 new files under `tests/mutation_ledger/killed_by/` and nothing else besides the copied module.
- Null control, same clone and inputs, `main`'s `tests/mutation_table.py`: `skip-head-moved`, 0 paths in `git status`.
- Filters compared on the real artifact at 03ba7f70, by rule (one script over `pins.json`, the head inventory and `closures.json`): closure-wide `stale_pins` (main) keeps 0 of 39. Re-key alone keeps 39. Re-key plus "killer's file unchanged" keeps 10. Plus "mutated module unchanged" keeps 7 (option (b)'s shape). Re-key plus reach (this PR) keeps 39.
- Closure sizes: `len(load_closures()[s])` at 03ba7f70: `tests/features.py` 123, `tests/entities.py` 200.
- Window: `git rev-list --first-parent aa7a8119..03ba7f70f` -> 7 commits. A commit counts as touching a killer when one of its first-parent diff paths is that killer or lies in its closure (file or directory prefix). Touching `tests/entities.py`'s: 7. Touching `tests/features.py`'s: 3.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` -> `MODE: FULL` (`.github/workflows/tests.yml changes the gate itself`). Run locally: `tests/entities.py` and `tests/structure.py` at the merged head (`ALL 2082 ENTITY CHECKS PASSED`, rc=0; `STRUCTURE RATCHET PASSED`), and `node .claude/workflows/policy_lint.mjs` -> `TOTAL: 0 error(s) across 40 policy file(s)`. Left to CI: the rest of FULL (`features.py` and the solver goldens need numpy here), `tests/stress.py`, and closures (`PREPR_SKIP_CLOSURES=1`).

## Red checks

`nightly-status`: this diff touches `tests.yml`, which it reads, so it owes an answer. The red it reports on `main` is `mutation-ledger-push` in run 37050037132, which is this defect. Cheaper detector: none ran it. The defect needed the real closure table against a real `main` window, and no PR check drives `stale_pins` with either. The new `tests/entities.py` check (seconds inside a ~4-minute script that every touching PR already runs) is that detector now, with no new standing cost. The finding that the old rule was never measured at production scale is in `## Root cause`. No check on this branch has gone red; CI has not run it.

## Forward-carry

none. The rule lives in `tests/mutation_table.py` and its pinning check. No later stage's brief depends on the closure-wide form. The standing-row gap named above (a killer weakened under a landed row) predates this PR and is not created by it.

## Friction

- environment: cost: a `git clone` of a seat worktree carries the worktree path as `origin`, so `tests/entities.py`'s #1471 pair fails in it and `origin/main` resolves to the worktree's stale `main`. One red-baseline arm read the wrong file before this was caught; mutant clones need `git remote set-url origin <github>` and a fetch.
