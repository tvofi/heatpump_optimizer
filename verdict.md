Design review: approve 32892dc67863bcfd92a6f0d7ad6f5583d83ed229

Reviewed: `dev/programme/designs/R10-CONFIGFLOW-PAGES.md` at `design/R10-CONFIGFLOW-PAGES` 32892dc67, round 2 of 3, from a detached worktree at that SHA. Round-1 verdict: `d2d710ad8`. Round 2 changes only the note: 32 lines added, 4 removed, against c9aa22947. `config_flow.py` and `tests/config_flow_steps.py` are unchanged from `aaf8af512` to current main `6d86acc90`, so every line cited still holds. No open `design/*` ref touches `config_flow.py`. Evidence: `evidence/round2_checks.txt`. Token count: not reported by this harness.

## Round-1 point 1 (Arm A3'), answered point for point

- **Fix:** answered. `_entities_errors(cleaned, current)` judges the source and the entity over `{**current, **cleaned}`. The tibber branch is unchanged, because its row default is `''` and not `_STORED`.
  - The rule is grounded in `_clear_absent` (2264-2267), and it matches `async_step_hot_water_tank`.
- **Failing test:** answered, with the setup, the asserts (`form`, the error, options unchanged) and the main failure as specified.
  - The null control (`sensor.other` saves) is as specified.
  - The second control corrects my round-1 wording, and the correction is right. Under the tibber switch the absent `_STORED` entity is still nulled by `_clear_absent`, so that control's claim is "no error, token saved, nulling as at main", not "clears nothing".
- **Mutants:** answered. Both are killed by the failing test:
  - the pre-clear `{**current, **flat}` view still sees `sensor.price` and returns `menu`;
  - the restored `or current.get` does the same.
- **Harness:** answered. `--clear-required` is added to `dev/audit/harnesses/r10_configflow_pages.py`, with its base and head readings and a `--null` arm.
- **Invariants:** answered.
  - The one exception is named (`A3-exception: price_entity_cleared_under_entity_source`).
  - The predicate must match exactly one fixture case, which goes beyond the request and closes silent growth of the exception.
- **User-visible change:** answered. It is named for the PR body's behaviour section, and the existing `price_entity_required` key means no string moves.
- **Placement:** sound. A3' lands in arm A's PR, after A's template, because A is the change that introduces `_entities_errors`.

## Round-1 carries

- **patch04/C2 conflict:** resolved in Arm C2. The note keeps both sides on each wood probe: `_suggested_optional(current, K): _registry_widget(K)`.
  - This is the tree I measured at dS +3.3700. The note cites it as the reviewer's figure, not its own.
  - It re-runs `wizard_widgets.py --all` and the marker and quick-setup tests after the merge.
- **#2238:** the disposition section is adequate. The rule for the fix reviewer is:
  - no closing keyword until every other #2238 finding is dispositioned in the body, as fixed by a named PR, fixed here, or carried;
  - `blocked` on a keyword that precedes a complete list;
  - no keyword in a code span.

  `close-2238` and `dr1-close-2238-disposition` carry it to the fixer.

Nothing in the re-cut breaks a measured figure. A3' is one predicate inside `_entities_errors`, and the note leaves the fixer's `score.py --diff` at head to confirm that dS does not move.

## Notes for the fixer

None new. The note's carries (`a3p-test`, `dr1-b-c2-conflict`, `dr1-close-2238-disposition`, and the round-1 set) stand as written.
