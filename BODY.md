ci: every main push run starts at once; main-cancel.yml alone cancels the superseded ones

The owner's ruling of 2026-11-25 ("superceded main runs should be canceled? That should obsolete ci-5") retires CI-5's `CI-main` concurrency group in `.github/workflows/ci.yml`. That group queued each main push run behind the one running: 27 min median wait, 65 min p90. `.github/workflows/main-cancel.yml` already cancels superseded main runs through `tools/pr/cancel_superseded.py main`, capped at three main runs with no concluded verdict. So ci.yml now gives every run its run-id group, push runs included. Pull-request runs keep the group they had.

Files:
- `.github/workflows/ci.yml`: `group: ${{ format('CI-{0}', github.run_id) }}` for every run, `cancel-in-progress: false` unchanged. The comment above the block now says main-cancel.yml cancels the older active main push runs when a push is graded in full, never past three main runs with no concluded verdict.
- `.github/workflows/main-cancel.yml`, `tools/ci/prelude.py` (`push_range` docstring), `.github/workflows/tests.yml` (coverage key comment): each said CI-5 replaced a pending run; each now says main-cancel.yml cancels it.
- `tests/entities.py`: the CI umbrella check now requires `CI-99` for every event and attempt, and `_CC_COALESCED` is empty. The three CI-5 plants are replaced by "push runs serialised in one main group (CI-5)", which re-adds the old expression, and "a run-id group cancelling in progress".

Nothing else reads the group. `tools/audit/seat/ci_pause.py`, `tools/audit/seat/scorecard.py` and the instrument pages never name `CI-main`, and a `git grep` of the tree outside the audit rounds and `RELEASE_NOTES.md` finds it in the five files above only.

This leaves #3885 open.

## Head

c4310fb28586c32f906cca5d002b578a4662bd1e (c4310fb2), one commit on origin/main d9100de781.

## Mutation proof

Failing first: with only `tests/entities.py` edited and ci.yml still carrying `CI-main`, a full local `PYTHONPATH=tests/hastub python3 tests/entities.py` run (130 min on a loaded host) failed both targeted checks:
- the CI umbrella: `concurrency group under push/None attempt 1 renders 'CI-main', want 'CI-99'`, and the new plant was not caught (the reader missed `push runs serialised in one main group (CI-5)`);
- "a superseded long-job pull-request run is cancelled": `ci.yml: two push runs by hpo-author[bot] get groups 'CI-main' and 'CI-main'`, and the same for `github-actions[bot]`.

The green run and the mutants use a local slice. It runs only these `tests/entities.py` blocks, with its imports: the `tools/ci/gate.py` pins through the CI umbrella check, `_RC_DOCS`, and `_cc_value` through the concurrency null control. Before the fix it reproduced the full run's red exactly. Each mutant edits ci.yml at the head, and the file is restored after each.

| mutant of ci.yml | CI umbrella check | superseded-run check |
|---|---|---|
| the `CI-main` expression restored | FAIL | FAIL |
| `cancel-in-progress: true` | FAIL | FAIL |
| `github.event_name == 'push' && 'CI-main'` (every push attempt shared) | FAIL | FAIL |

All three were killed.

## Null control

At the head, the slice passes all five of its checks: the two gate.py pins, the CI umbrella check, the superseded-run check, and "a group keyed on the ref, cancelling everything, is refused". The existing ref-keyed null control and the umbrella's other plants still fire. The new plants are checked as caught (`_CI_PLANT_MISSED` is empty).

## Figures

none

## Red checks

The full local `tests/entities.py` run had three failing checks besides the two this change targets. All three are host-local, and none reads the `concurrency` block:
- `RUN_PART=fast skips the arch pair by name and RUN_PART=arch runs only it; dropping the fast skip is refused (U5, null control)`: the nested `RUN_PART=arch` run of `tests/arch_score.py` and `tests/arch_score_head.py` reported `RESULT FAIL (1 failed)` on this macOS host. Its routing assertion (which scripts ran) held.
- `a measured script's late-writing descendant is waited for, not recorded as nodata`: the measured child scripts had written nothing by the bound, so twenty were recorded `nodata`. The host's load was far above normal (130 min wall clock against 17 min user CPU), and the run waited on gate leases held by other sessions.
- `hb:positive_control survives one hung py-spy sample`: the sampler needed try 3 of 3, and a 600 ms spin read as 607.4 ms with gaps over the bound, under the same load.

The diff reaches none of the files these checks exercise. CI runs them on Linux, and that run is the authority. No cheaper detector exists for timeouts caused by load on a shared local host.

## Forward-carry

none

## Friction

none
