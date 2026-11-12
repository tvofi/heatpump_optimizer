HOTFIX R10-HOTFIX-PLAN-OWNER-PRICE. The planner had no way to take an owner-stated price: `group_hours` read only size, class, resume stage and pending carries, so R10-CATALOG-PR (the owner's step that opens the hacs/default PR) was priced as a fresh small production fixer and closure sat past the owner's 2026-11-15 deadline. Owner ruling, tvofi 2026-11-12, verbatim: "Price it at 4h". The 240 minutes is the owner's value: the fixer did not choose, round or second-guess it.

What changed:
- Roster fields `owner_price_minutes` (positive minutes) and `owner_price_cite` (the owner's words, mandatory beside it). One definition, in `roster_lib.owner_price_why` / `roster_lib.owner_price`; a half-written pair is a `SchemaError`, never read as no price.
- `replan.group_hours` returns the price in hours before the size lookup, basis `owner-stated N min (not measured): <citation>`; a malformed price is a `PlanError` naming the group. The plan group row carries `owner_priced` (and, for a post-closure group, `duration_basis`) only when priced.
- Roster editor op `set-price <group> <minutes> --price-cite <text>` (`roster_edit.op_set_price`): refuses a missing or blank citation, non-positive, non-numeric or infinite minutes; the old price and citation go to `resume.note`; the price already held writes nothing. Not a queue-only op, like `set-size`.
- `plan_page.py` draws "owner-stated price, not measured" on the ETA cell of a priced row.
- Last step: R10-CATALOG-PR set to 240 min with citation `owner-stated price, tvofi 2026-11-12: "Price it at 4h"`, written through `op_set_price` and the editor's own `dump` (the diff is the two fields, the trailing comma and the `resume.note` record).

The durations model, the definition of closure and every other group's price are untouched.

Alternatives that lost: a per-size override in `durations.json` (changes every group of that size, which the brief forbids); a separate prices file (a second roster-shaped source to keep fresh).

## Head

9cb746c217bb0a1c303da765897612e562dc3b88 (merge base 19baca76181cb019d9b1cfd93ee6bc0a08e20047; `git merge-tree --write-tree origin/main HEAD` reports no conflict at origin/main 8c10361eb1fea539dc5acb8f7442eac2810faa47, 2026-11-12T15:42Z, so no re-merge).

## Mutation proof

Planner self-test (`python3 -I tools/plan/replan.py --self-test`), one mutant per new predicate, each reported `self-test fails when <name> is deleted`: `owner-price` (`if stated:` to `if False:`), `owner-price-hours` (drop `/ 60.0`), `owner-price-basis` (drop the citation from the basis), `owner-price-refusal` (no `roster_lib.owner_price` call), `owner-price-post-row` (post-closure row loses `owner_priced`).
Editor self-test (`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py roster_edit-1 roster_edit-2 roster_edit-3 roster_lib-1 roster_lib-2`): `roster_edit-1` no-op skip, `roster_edit-2` validation skip, `roster_lib-1` the `minutes > 0` predicate, `roster_lib-2` the citation predicate: KILLED. `roster_edit-3` (citation `.strip()` removed) first SURVIVED; a check that stores a padded citation and re-reads it equal was added, and it is now KILLED (`RESULT survivors=0` on the rerun of `roster_edit-3`).
Failing test first: the new self-test arms call `group_hours` with the price fields and `set-price`, neither of which existed at the merge base.

## Null control

The roster as it stands before the price is set, replanned at a fixed start (`python3 -I tools/plan/replan.py --roster-file <copy named wave-r10-groups.json> --start 2026-11-12T12:00:00 --out <plan>`), once on the merge-base code and once on this code: `cmp` of the two plans printed IDENTICAL. A second run on this code after the post-closure change printed IDENTICAL against the first. Self-test nulls: an unpriced group still plans 18 h beside a priced one; an unpriced post-closure row carries neither new key; an unpriced page draws no tag.

## Figures

- Plan before and after the price, same command and start, compared key by key (a Python walk over both plan.json files): only R10-CATALOG-PR `duration_minutes` 1589 to 240 (plus `duration_basis` and `owner_priced`, now present), its `finish`, `summary.closure`, `summary.post_closure_finish`, `summary.wall_hours` and `summary.expected_arrivals`, which closure feeds. Closure moved 2026-11-18T10:27:00Z to 2026-11-17T11:58:00Z at the 2026-11-12T12:00:00Z start; no other group's row differs. The null control for this claim is the IDENTICAL `cmp` above (a walk that printed differences elsewhere would have listed them).
- `python3 -I tools/audit/seat/roster_edit.py --self-test`, `python3 -I tools/audit/seat/plan_page.py --self-test`, `python3 -I tools/plan/replan.py --self-test`: all 0 failed.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL ENTITY CHECKS PASSED at this head and at the merge base.

## Red checks

`bash tools/pr/prepr.sh` at this head: every step printed ok or skip except `closures`, which printed `REFUSE failed while being recorded: tests/entities.py (exit 1) ... left to CI: tests/harness_headers.py`. `tests/entities.py` itself exits 0 at this head and at the merge base (above); the recording step runs it under strace in this container, so I read the refusal as the recorder's, not the script's, and did not re-run the closure derivation off its recorded platform (`gate-scoping.md`). The first prepr run was moved to a background task and stopped at its time limit after the `merged structure` step, so the body check below was run on its own. No check has gone red on a commit in the branch.

## Forward-carry

none

## Friction

none
