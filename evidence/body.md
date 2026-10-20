Part of #2272.

The replay lane is already gated nightly: `.github/workflows/tests.yml`'s `slow` job runs `tests/replay.py` on the `17 2 * * *` schedule (step "Replay recorded days through the real coordinator", landed 027979753). This pull request lands what this group's carry can land without decisions this seat cannot take: it corrects the lane's series instrument so it reads the series #2339 created (two ruler eras, not one mixed one), records the cross-runner comparison the carry asks for, and corrects the `loop_cpu_ratio` note's invariance claim, which the 2026-10-20 nightly falsified.

It deliberately does **not** change `COST_BUDGETS` and does **not** add the real recorded day. The cap's re-record is a raise, which is the owner's under CLAUDE.md rule 2, and the real day needs an export from the owner's Home Assistant box that is neither in the tree nor on this box. Both are carried under `## Forward-carry`.

**Owner review and rollback.** The group is code-owned on `.github/workflows/`; this diff touches no `.github/workflows/` file (the lane is gated in `tests.yml`'s `slow` job, unchanged), so the code-owner rule does not bind it, and the decision it leaves to the owner is the cap's re-record under rule 2 (mandate 6175172275), not a workflow change. **Rollback:** revert the branch's two commits over `4e5801eb5` (`cdec077ac`, `f0b1844ba`) — they change one audit instrument and one comment; no runtime path, budget or workflow reads either.

## Head

`aea79fa6b388ca546f69fdcac5ec0a006aac05dd` merges origin/main `e2a47458f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2514.md`.

`af03a14e038776d751034ee8b74c7965719cbb1b`. The review-blocked class (`tests/replay.py:377` still said the ratio was "invariant across runners", 25 lines below this diff's corrected note) is closed in this head: the ruler's docstring now says most of the interpreter factor cancels and the residual runner-class spread remains, so the ratio is bounded, not invariant.

## Mutation proof

`dev/audit/harnesses/r10_replay_loopnorm.py --self-test` pins the derivation. Mutating the post-era branch of `figures()` from `loop_cpu_ms / row["ref_ms"]` to `loop_cpu_ms / row["loop_ref_ms"]`:

- base copy: `RESULT self_test checks=7 failed=0`
- mutated copy: `FAIL: post: the old figure is derived`, `RESULT self_test checks=7 failed=1`

The instrument's own defect has the same shape on the same nightly rows: the baseline harness printed one "old" series spanning both rulers, `old_spread=min0.0868_max0.4050_factor4.666`, where the two real spreads are 1.659x (pre) and 1.283x (post). Both are `--series` output at the same rows; see Figures.

## Null control

Two arms.

1. **The cap red is not a loop-work regression.** Same fixture, same box, `git archive` exports of the two nightly heads (`c3530277`, the 2026-10-19 run's head, and `0c298f6b`, the 2026-10-20 run's), `tests/replay.py --one tests/replay/synthetic-dhw-only.json` interleaved six times each: median `loop_cpu_ratio` 0.0711 at `c3530277` and 0.0701 at `0c298f6b`, maxima 0.081 and 0.0719. Had the later head added the loop work the CI jump implies (+27 %), its readings would sit near 0.090; none of the six reached 0.072. The jump is the runner: the 2026-10-20 runner ran the ruler at `loop_ref_ms` 84.05 against 128-161 on the other four post-#2339 rows, while the loop CPU in absolute time fell to 9.36 ms. The design is R10-RCA-2205's interleaved per-SHA comparison.
2. **The `--series` change does not move the local figure.** The harness's default (local) mode is untouched, so both ends run the same `tests/replay.py --one` measurement and a re-run is flat by construction; the mutation above is the arm that moves.

## Figures

- Cross-runner series, by ruler era: `python3 dev/audit/harnesses/r10_replay_loopnorm.py --series` — 22 main rows (17 pre, 5 post), 0 API failures, 58 fix-branch dispatches filtered; pre-era BLAS figure 0.2441-0.4050 (1.659x); post-era pure-Python figure 0.0868-0.1114 (1.283x, median 0.0877); the same five post rows under the BLAS figure 0.2599-0.4190 (1.612x); corr(post figure, `ref_ms`) -0.616, n=5.
- The 2026-10-20 red: `gh run view 39387919507 --job 118512165515 --log` — clean `loop_cpu_ratio` 0.1114 against its cap 0.111, `loop_cpu_ratio` 0.1114 with `loop_ref_ms` 84.05 and `ref_ms` 22.35; the doubled-loop arm read 0.2616 with `injected_ratio` 1.0001, so a cap up to 0.2616 still sees it.
- The five post-#2339 rows, clean cost line each: `gh run view <run> --job <job> --log` — `loop_cpu_ratio` / `loop_ref_ms` / loop CPU: 2026-10-17 `39011974246` 0.0868 / 161.10 / 13.98 ms; 2026-10-18 `39106988523` 0.0875 / 127.94 / 11.19 ms; 2026-10-19 `39218718759` 0.0877 / 161.39 / 14.15 ms; 2026-10-19 dispatch `39256093598` 0.0982 / 157.17 / 15.43 ms; 2026-10-20 `39387919507` 0.1114 / 84.05 / 9.36 ms. The fastest ruler carries the lowest absolute loop CPU.
- The re-record arithmetic: `python3 -c 'import math; print(round(math.sqrt(2) * 0.0877, 4), round(math.sqrt(2) * 0.1114, 4))'` — 0.124 (sqrt(2) x the post-era median, the smallest cap covering every post row) and 0.1575 (sqrt(2) x the largest reading, the file's "largest record" rule).
- Local paired runs: two `git archive` exports of `c3530277` and `0c298f6b`, `PYTHONPATH=tests/hastub python3 tests/replay.py --one tests/replay/synthetic-dhw-only.json` six times each, interleaved — the medians and maxima above.
- Structure: `python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`, no metric moved.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` — `MODE: SCOPED -- 3 script(s) run`; `tests/debug_collect.py` (122 checks), `tests/entities.py` (2359 checks) and `tests/features.py` (4258 checks) pass. `tools/pr/prepr.sh <body>` passes; its closures step is skipped locally with `PREPR_SKIP_CLOSURES=1`, because that re-recording is a trace the Linux recorder owns and CI's `closures-autofix` re-derives, and this diff adds no read.

## Red checks

This branch turns no check red. The standing red on main at the base is the lane's own cap, not a check this diff touches:

- `FAIL synthetic-dhw-only.json: cycle_cost [loop_cpu_ratio 0.1114 over its budget 0.111]` (Tests `slow`, run 39387919507, job 118512165515, 2026-10-20T07:39Z). The Figures establish it as residual runner sensitivity, not loop work; the only fix is a cap raise, which is the owner's under CLAUDE.md rule 2, so this branch leaves `COST_BUDGETS` byte-identical. `nightly-status` reports the last scheduled run and blocks no merge, so the cost is a red board row, not a blocked pull request.

## Forward-carry

- The group's headline item, a real recorded day, is not in this pull request. No `hpo-replay/1` document exists in the tree (`tests/replay/` holds only `synthetic-dhw-only.json`), and none is on this box: `dev/audit/rounds/round10/D15/s2/REPORT.md` records that no `export.py` document was supplied, and no recorder database is present. It must be produced on the owner's Home Assistant box with `python3 tools/replay/export.py --config-dir /config --days 1 --out /config/hpo-replay-<day>.json`, checked with `export.py --check`, then committed as `tests/replay/<day>.json`. Carry: #2272
- The new fixture is a new tracked file and owes a deliberate classification: add it to the `tests/closures.json` sets that list `synthetic-dhw-only.json` (`tests/entities.py` and `tests/features.py`) and to `COST_BUDGETS` in `tests/replay.py`, or `tests/entities.py` refuses it. Carry: #2272
- D14-s3 (the nightly-replay seat) re-runs on the real day once it has landed. Carry: #2272
- The cap's re-record is measured and owed: 0.124 covers every post-#2339 row with the recorded band construction, 0.1575 follows the file's largest-record rule; both are above the measured median and therefore a raise the owner confirms before a branch is pushed. 0.124 puts the floor at 0.062, 0.3 % under the twelve-run local minimum 0.0618, so a local run can red on "cannot see a 2x"; 0.1575's floor is 0.0788 and would red more local runs. Carry: #2272
- The owner's own diagnostics download (integration 7.0.1, 2026-10-19) refuses the replay half: `manifest.replay` reads "refusing to write: 2 dropped credential value(s) survive elsewhere in the payload", raised by `replay_doc.seal`'s dropped-value post-check. That is #2271's file, not this group's, and #2271's group is done; it lands here because it blocks this group's own route to a real fixture, and the repair is to drop a credential value wherever the payload repeats it (and name the two values if the owner wants to judge them). Carry: #2272

## Friction

- `roster: stale: this group's files list names .github/workflows/nightly.yml, which the tree does not have; the lane is gated in .github/workflows/tests.yml's slow job (027979753).` Carry: dismissed: plan artifact, named here so the next seat does not search for it.
- `budget: stale: the carry's doubled-loop arm figure (~0.156) is the slow-runner estimate; on the 2026-10-20 runner the arm reads 0.2616, so the control has more headroom than the carry's number suggests.` Carry: dismissed: it changes no disposition, and the cap is still the owner's.

