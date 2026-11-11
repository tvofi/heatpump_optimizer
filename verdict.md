Fix review: blocked 95c04821e5ba3d6672e911f45292e1a2a4e463a9 mutation-vacuous: note-run run-via replan-via, the REST read's wiring into the measurement is unpinned

bus-nonce: 9ebd4ea7050de3c52e1caaeaa684d491

Round 3 (delta re-review of 9774026d05..95c04821e5). The measured head is 95c04821e5ba3d6672e911f45292e1a2a4e463a9, still the PR head when this verdict was written (ev/head-at-verdict.txt). From the fourth round, fixer.md owes a re-cut.

## Block

Round 2 blocked on two items, and this delta settles the first. The hotfix mark is now pinned on the rendered page. The second item asked for the REST read to land and for `sizes_provenance` to state that input. The read and `input_note` both landed and both are pinned. The wiring that connects them to the measurement is not pinned. No self-test calls `size_durations.run` or `replan.main --measure-sizes` (located: `replan.py:3290` is the only caller, and neither self-test reaches it). My driver (ev/my-mutants-sd-driver.py, ev/my-mutants-sd.txt) found three production survivors. Each had `--self-test` rc=0 and no FAIL line:

- `note-run`: `size_durations.run`'s `out["sizes_provenance"] += input_note(...)` deleted. The provenance goes back to not naming its input, which is round 2's defect, and nothing fails.
- `run-via`: `run` passes `"graphql"` to `read_prs` instead of `via`. A `--via rest` run then reads GraphQL. Its provenance still says `fetch_rest (--via rest)`, so the provenance is false and nothing fails.
- `replan-via`: `replan.main` drops `args.sizes_via` from the `size_durations.run` call. The body's own figure command (`--sizes-via rest`) silently uses GraphQL. The provenance stays honest, but the flag does nothing.

None of the three is equivalent, because each changes the measured output or its provenance. The body's `## Unpinned sites` does not list them. `mutant_run.py --diff` did not generate them, since they delete a statement or drop an argument.

Fix: make `run` injectable, as `fetch_rest`'s `get` already is. For example, `run(..., reads=READS, roster=None)` or something similar. Then add an arm that drives `run` with a fake `rest` read and a fixture roster. It must assert that the `rest` read was the one called, and that `sizes_provenance` ends with `input_note("rest", ...)`. Its null control is a `graphql` run, which names `fetch`. In replan, add an arm showing that `--measure-sizes --sizes-via rest` reaches `size_durations.run` with `via="rest"`, using a stubbed `run`.

## Findings

- Follow-up: the test-side mutant `replan-cap` (`unset = ()`) survives, because the fixture records `live_remaining_fraction` 0.5 and review prices equal to progress either way. The arm's production pin holds regardless. Both 0.7 defaults changed to 0.9 are killed by `live stage (cap)` (ev/my-mutants-cap.txt). Carry: dismissed: test-side only, and the production defaults are pinned

## Evidence

- RESULT round-2 survivors at this head, with my driver (ev/my-mutants-driver.py, ev/my-mutants.txt), `plan_page.py --self-test`: `hot-render`, `hot-gates`, `hot-notdone` were each KILLED by a named FAIL. So were my added mutants: `hot-dis` (discharged excluded from `done` for `hot`), `hot-crit`, `hot-title`, `hot-allrows` and `hot-nothotfix`. `hot-notdone` dies on the `deferred` arm, so it is not equivalent, which matches the body.
- `hot-discharged`: the term is deleted. `done = {...} | discharged` (plan_page.py:212), and `hot` requires `g not in done`, so the deletion is behaviour-preserving. `hot-dis` shows that the discharged null arm pins it. The PR body records it as answered by deletion, not as KILLED, and I accept that.
- RESULT harness `r10_plan_page_mutants.py M0 hot-render hot-gates hot-notdone hot-crit`: M0 null, four killed, `survived=0`. This matches the body (ev/harness-new-mutants.txt). The body quotes each of these as killed.
- RESULT REST-read mutants killed: `rest-short`, `rest-since`, `rest-merged`, `rest-first` and `read-replay` (ev/my-mutants-sd.txt).
- Durations input driver (fixer.md 18): landed as `size_durations.fetch_rest`, `--via rest` and `replan.py --sizes-via rest`. The committed `sizes_provenance` names the input: "1021 merged PRs created since 2026-10-12, read by size_durations.fetch_rest (--via rest)". I did not re-run the REST read. The corpus window is still open, because PRs have merged since 04:56Z, so a re-run would not reproduce the figures exactly. I did not re-derive `sizes_hours` S 21.6, M 32.4, L 35.6, XL 35.6 or `round_hours` 5.65. Carry: dismissed: evidence, not a finding
- RESULT self-tests at head: `plan_page.py` "93 checks, 0 failed"; `replan.py` "model self-test: 0 failed", "self-test: 0 failed"; `size_durations.py` "0 failed". All match the body's Figures.
- Step 13: `git merge-tree --write-tree origin/main 95c04821e5ba3d6672e911f45292e1a2a4e463a9` rc=0, no conflict, against origin/main a7628041dc (ev/merge-tree.txt).
- Step 5 and step 14: the delta touches no VERSION, manifest, budget, claim, golden or closures file.
- Step 11: the only red is `tests / nightly-status`, which is not in the `owed-reds` set (ev/owed-reds.txt), so it blocks nothing. `merge_train.py classify` printed `WAIT ... pending: gate red: none` from 07:31Z on (ev/classify-poll.txt). This block does not depend on CI.
- Finder's harness: none. This is an instrument group fed by roster carries and closes no issue. Carry: dismissed: evidence, not a finding
