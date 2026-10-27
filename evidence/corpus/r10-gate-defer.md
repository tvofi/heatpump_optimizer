R10-GATE-DEFER: the required check `gate` (job `gate` in `.github/workflows/ci.yml`, program `tools/ci/gate.py`) went red early at every PR head with more than one `ci.yml` run. Each run's gate listed the others, and if any of them was still adding a source it FAILed with "run(s) [...] at this head are still being judged; their gate decides". An undecided head therefore showed a red that a later gate had to overturn. When two gates each read the other before the other was listed, both went red and nothing decided, because `gate-sweep.yml` acts only on a green gate.

Code-owned paths (`@tvofi`, `.github/CODEOWNERS` `/tools/ci/`): `tools/ci/gate.py`, `tools/ci/prelude.py`, `tools/ci/sweep.py` and `tools/ci/sweep_selftest.py`. Other paths: `.github/workflows/gate-sweep.yml` (header comment only), `dev/audit/harnesses/r10_gate_defer_race.py` (new, classified in `tests/closures.json` under `tests/harness_headers.py`'s inert reads), `dev/audit/harnesses/r10_ci_gate_core.py`, `tests/closures.json` and `dev/programme/delivery/2770.md`.

**Who built the harness.** No finder's harness for this defect predates the fix. `dev/audit/harnesses/r10_gate_defer_race.py` was written by the fixer seat, in this PR's first commit (409bbe929). It replays the finder's shape (#2754's runs, from the jobs API), but the instrument is the fixer's (fixer.md 18). Round 2 extends it with the reviewer's `editcode` shape and drives each tree's own `sweep.py`.

## Design

The rule: a deferral publishes nothing until the head is decided. The only sound state an Actions job can hold that is neither red nor green is "still running", so the deferring gate keeps running.

- **The gate waits, bounded.** While its only reason to fail is the deferral, `gate.judge` re-reads every `POLL_S` (60 s, tvofi's floor), for up to `GATE_WAIT_MAX_S` (720 s). Then it judges with the predicate unchanged. The bound sits inside the job's `timeout-minutes: 15`: the self-test parses `ci.yml` and pins bound + one poll + 120 s under that limit. A decided red never waits, so a prelude cross-check beside a busy run returns at once.
- **Nothing waits on a waiting gate.** `prelude.wait_sources` (formerly `wait_earlier`) releases a run once it is `judging` (every unit has ended and its gate is listed), not once it has finished. So a gate that is waiting is never what a prelude waits for, and the waits cannot form a cycle. `judging`, `UNITS` and the jobs read move into `prelude.py`, which both programs import, so the gate's defer test and the prelude's wait read one predicate. `gate.py` re-exports `UNITS` for `codescan_wait.py`, `ruleset_cutover.py` and `ci_predict.py`.
- **A non-code run's prelude waits for every code run, whatever its id.** This is R10-RCA-CODESCAN-WAIT's M1. GitHub numbers a same-second push and body edit out of order (#2754: edit 40119473491 < code 40119473870). With the code run first, the long wait (its tests and codeql) is spent in the prelude, which has a 150-minute budget, and the gate's 15 minutes only has to cover the edit run's body units. A code run never waits in its prelude, so no cycle forms.
- **The sweep re-judges a red gate at the head whatever its run's id (round 2).** M1 has a consequence. The gate that waits, and can expire at the bound, is the higher-id code run's, while the decider is often the lower-id edit run. `sweep.py` used to walk only runs with `id < V`, so the decider's sweep never reached the expired gate. The code run's own sweep skips, because its gate is red. The red stayed. The sweep now walks every other `ci.yml` run at the head (`r["id"] != v["id"]`). Everything else is unchanged: it acts only when V's gate is green at the live head and covers the newest event, it never re-runs V or a green gate, the attempt cap is 45, each run is re-run at most once, and the poll is bounded.
- **A real red stays red.** After waiting, every gate at the head computes the same predicate over the same finished sources, so a red source is red in every published verdict. No wait can publish a PASS over a decider's red: fixture "a deferring gate published after the decider's red", and harness `2754-red`. A sweep re-run is a re-judge, so it reads the same red.
- **The residual.** Past the bound, a gate still FAILs deferring. That happens when a run at the head keeps adding sources for 12 minutes after this gate's units ended: an edit run's body units stalled several minutes in the runner queue, a code event at an already-judged head (a reopen, or a same-SHA dispatch), or a stuck runner. The red now converges, whichever id holds it. Once the decider's gate is green, the decider's sweep re-runs the expired gate, which then reads the head decided (harness `editcode` and `2754` with `--edit-s` 760 or 900: `RESIDUAL-RED 0`, against `RESIDUAL-RED 1` on `editcode` at the round-1 head). One red stays visible between the expiry and the decider's verdict.

Alternatives and why each fails:

- **Option 2: publish the deferral as a non-failing conclusion.** An Actions job can conclude `success`, `failure`, `cancelled` or `skipped`. `success` and `skipped` both satisfy a required check, so a merge could pass while the decider is undecided, which is a mask. Mutant M4 below plants this and is killed. `cancelled` needs `actions: write` on `gate`, a permission change on the required job, and `merge_pr.sh` and the tick would still read it as red.
- **Option 1 without M1.** The harness's `2754` replay with `waits_on` reverted to id order makes the edit gate wait 660 of its 720 s for the code run's tail. That tail is unbounded relative to 15 minutes (R10-RCA-CODESCAN-WAIT measured a 28.1 min median codeql tail), so the bound would routinely expire red.
- **Option 1 with the prelude still waiting until runs are finished.** A later verdict run's prelude waits on the earlier run's gate, and that gate waits on it. Both burn to the bound and the gate goes red (mutant M6).
- **A separate long-timeout `settle` job before `gate`.** It adds a job to `ci.yml`'s pinned graph (`tests/entities.py`'s caller set), and `gate` would still need the same wait for a run created after `settle` passed. It duplicates the mechanism.
- **For the round-2 seam, extending `GATE_WAIT_MAX_S` instead of the sweep.** The bound is already pinned 60 s under `timeout-minutes: 15` with one poll and 120 s of steps. Raising it moves the stranding threshold but leaves an id-ordered sweep that strands whatever crosses it.

Cost, disclosed: on the #2754 shape, the head's first PASS lands later than the base's. The edit run's body units now run after the code run's units instead of beside them; the harness gives the numbers under Figures. Against that, the base publishes two undecided reds first, and `gate-sweep.yml`'s re-runs follow them. The replay uses the measured edit `pr-contract` span, 5.5 min. That span included `codescan_wait.py` waiting for the code run's codeql, which M1 removes, so the replay is pessimistic for the head. Round 2 has one more cost: a sweep may now poll, for up to its 600 s, a higher-id run's gate that is still in progress. Each poll is one runs listing, as before.

The coordinator added a rerun cascade (#2748 029d6ccc): three completed red deferring gates, a queued review decider, and a re-run of an older gate. The re-run waits for the decider instead of deferring red again. The decider never waits on the re-run, because a run whose only open job is its gate is `judging`. This is pinned by two self-test fixtures and the harness's `cascade` scenario.

## Head

b2ff00056ad3cee05279d1a6c72f12f47079c650. Merge base 5c0ee109305fc4f377c9326c712156b9ceb0e638 (origin/main at 2026-10-25T00:48Z; `origin/main` merged into the branch at 5a33c766e). The round-1 head this repairs is ce6f6511e693a6c175282796281c304e22cfb52a.

## Mutation proof

For each mutant, a scratch driver replaced one production line (old text to new, as listed), ran `python3 -I tools/ci/{gate,prelude,sweep}.py --self-test`, and restored the file. After the last restore, `git status --short` printed nothing.

- M1, `judge` never waits (`if ok or why != [deferral(waiting)] or now() - t0 + POLL_S > GATE_WAIT_MAX_S:` to `if True:`). The gate self-test fails 6: "#2754 shape", "simultaneous completion, side A", "side B", "a deferring gate published after the decider's red is that red, never a PASS", "past the bound ...", and "rerun cascade ...".
- M2, the wait without its bound (drop `or now() - t0 + POLL_S > GATE_WAIT_MAX_S`). The gate self-test fails "past the bound, the deferral FAILs (for gate-sweep.yml), and the wait stays inside the bound".
- M3, it waits on a decided red too (`why != [deferral(waiting)]` to `not waiting`). The gate self-test fails "a decided red never waits: the prelude cross-check beside a busy run".
- M4, the deferral publishes PASS (`"PASS" if ok` to `"PASS" if ok or why == [deferral(waiting)]`). The gate self-test fails "past the bound ...".
- M5, the prelude orders by id only, pre-M1 (`(run["id"] < run_id or t is None or t[0] == "code")` to `(run["id"] < run_id)`). The prelude self-test fails "M1: waits for a LATER code run (a same-second pair numbered out of order) until it is judging".
- M6, the prelude waits until finished, not judging (`if not judging(run):` to `if True:`). The prelude self-test fails "M1: ..." and "a run whose gate is listed and units ended adds no source: not waited on (its gate may wait on us)".
- M7 (round 2), the sweep reverted to lower ids (`runs if r["id"] != v["id"]` to `runs if r["id"] < v["id"]`). The sweep self-test fails "a red gate on a HIGHER-id run is re-run (an id orders nothing)" and "a HIGHER-id gate still waiting is polled, and re-run once it expires red". The harness `--edit-s 760 editcode` prints `RESIDUAL-RED 1`.

Failing test first: those two sweep fixtures were added before the `sweep.py` line changed. Run against the unchanged `sweep.py`, the self-test printed `23 checks, 2 failed` with those two names; after the change it printed `23 checks, 0 failed`.

The design's own predicate mutants (`dev/audit/harnesses/r10_ci_gate_core.py mutants`; M7 to M9 now plant where `judging` lives) print `RESULT mutants=16 survivors=0` at this head.

## Null control

- The race harness `dev/audit/harnesses/r10_gate_defer_race.py`, run over an export of the merge base 5c0ee1093's `tools/ci` and `tools/pr`, prints `2754: ... UNDECIDED-RED 2`, `pair: ... UNDECIDED-RED 2 ... DEADLOCK yes` (and `RESIDUAL-RED 2`), `cascade: ... UNDECIDED-RED 1` and `editcode: ... UNDECIDED-RED 1`. At this head with the default `--edit-s 518`, every scenario prints `UNDECIDED-RED 0 ... DEADLOCK no` and `RESIDUAL-RED 0`.
- The round-2 null is the round-1 head ce6f6511e (export of its `tools/ci`, `tools/pr`) with `--edit-s 760` and `--edit-s 900`: `editcode: ... sweep present re-runs 0 RESIDUAL-RED 1`. That is the stranding the review reported. This head, with the same arguments, prints `editcode: ... re-runs 1 RESIDUAL-RED 0`. The merge base also prints `RESIDUAL-RED 0` on `editcode`, because there the red sits on the lower id. Had the repair not closed the seam, this head would print the round-1 line.
- The no-defect null is `single` (one run at the head): `UNDECIDED-RED 0 ... gate-wait 0 s ... RESIDUAL-RED 0` at all three trees.
- The masking null is `2754-red` (the code run's `tests / closures` red): `MASKED 0` at all three trees and every `--edit-s`. Every head verdict is `FAIL tests / closures: failure`. RESIDUAL-RED is defined only on a head with no real red, so it is 0 there by construction.
- The design oracle's replay, `python3 dev/audit/harnesses/r10_ci_gate_core.py replay`, prints `output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt` at this head. The judging inputs are unchanged.

## Figures

- `python3 dev/audit/harnesses/r10_gate_defer_race.py [--edit-s S]` at the head, and the same with `--ci "$D/tools/ci"` after `git archive <sha> tools/ci tools/pr | tar -x -C "$D"` for 5c0ee1093 (merge base) and ce6f6511e (round-1 head), with S in 518, 760 and 900. These print the per-scenario `UNDECIDED-RED`, `MASKED`, `DEADLOCK`, `gate-wait`, sweep `re-runs` and `RESIDUAL-RED` lines stated under Null control. At the head on `2754`, the first PASS is at t=1847 s, and the longest single wait is 600 s against `GATE_WAIT_MAX_S` 720. On `2754` and `editcode` with S of 760 or 900, the head prints `UNDECIDED-RED 1` (the bound's residual) and `RESIDUAL-RED 0`.
- The `2754` replay over an export of this head with `prelude.waits_on` reverted to id order (Option 1 without M1): the edit gate waits 660 s. Taken at round 1; `prelude.py` is unchanged since then.
- `python3 -I tools/ci/gate.py --self-test`: `37 checks, 0 failed`. `python3 -I tools/ci/prelude.py --self-test`: `29 checks, 0 failed`. `python3 -I tools/ci/sweep.py --self-test`: `23 checks, 0 failed`. `codescan_wait.py`, `ruleset_cutover.py` and `ghapi.py` `--self-test`: 0 failed each.
- `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants`: `RESULT mutants=16 survivors=0`.
- Class enumeration (fixer.md 8). Rule: `grep -nE '(\[.id.\]|run_id|\bid\b)\s*[<>]=?\s|(max|min)\(.*\[.id.\]|key=lambda \w+: \w+\[.id.\]' tools/ci/*.py tools/pr/*.py tools/audit/seat/*.py | grep -v selftest`, which is a superset of the reviewer's `grep '\["id"\] *[<>]'`. Every code seam it returns:
  - `tools/ci/prelude.py` `waits_on`: closed in this diff (M1).
  - `tools/ci/sweep.py` `Sweep.run`'s walk: closed in this diff (round 2).
  - `tools/ci/gate.py` `gate()`'s source loop (`sorted(others + [me], key=id, reverse=True)`): already guarded. It is a preference among completed sources for one unit at one head and base, and any of them judges the same SHA. It orders no waiting or re-judging.
  - `tools/ci/codescan_wait.py` `source` (`sorted(runs, key=id, reverse=True)`): already guarded, the same way. It returns the first run owning a finished codeql unit for the head and base, and any such run is equivalent.
  - `tools/ci/ruleset_cutover.py` `gate_green` (`max(rs, key=id)` per suite) and `reds_at_head` (`r["id"] > newest[key]["id"]`): already guarded. The newest check run per (name, suite) is an attempt order inside one suite, not a cross-run order.
  - `tools/ci/ruleset_cutover.py` `attempts` (`id=max(...) + 1`): a self-test fixture that builds an id, not an ordering.

  The rule's other hits are usage strings (`sweep.py` `main`, `alert_list.py`, `ci_probe.py`, `proof_watch.py`).
- The scope came from `python3 tests/closure.py select --diff 5c0ee1093 ...` and reads `MODE: FULL` (reason: `.github/workflows/gate-sweep.yml changes the gate itself`). The full suite is CI's. Locally, with `PYTHONPATH=tests/hastub`:
  - `tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
  - `tests/env_drift.py --claims-only` printed `claims hygiene: origin/main ok`.
  - `tests/closure.py selftest` printed `ALL 117 closure shrink pins PASSED`.
  - `tests/layout.py` printed `layout self-test: ok`.
  - `tools/pr/ci_predict.py --base origin/main` printed `no closures, fast, wave-script or instrument red predicted`.
  - `tests/entities.py`: see the next figure.
- `tests/entities.py` with `BASH_ENV` set by this Linux seat's environment printed `2 of 2429 ENTITY CHECKS FAILED`: the `gate-sweep.yml ... (U0c)` step-reader check and `graders-head-copy's delivery_status step`. Both run a workflow step under `bash -c` with a stand-in `python3` on `PATH`, and `BASH_ENV` re-prepends the real toolchain ahead of it. With `env -u BASH_ENV`, the same command printed `ALL 2429 ENTITY CHECKS PASSED`. That run began at 85b72e824; the harness-only commit b2ff00056 was re-checked by `tests/harness_headers.py`, which printed `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `git diff 5c0ee1093...HEAD --quiet -- VERSION RELEASE_NOTES.md tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt custom_components/*/manifest.json` exits 0: no version or claim file is touched.

## Red checks

- No check on round-1 head ce6f6511e concluded red when the review read the check-runs API (review/2770 `evidence/ci_checkruns.tsv`). This head has no CI yet. The two local `tests/entities.py` reds above are the seat's `BASH_ENV`, not this diff. They are answered there, and they are not CI checks.
- `gate` (the required check) is this PR's subject. It went red on #2743, #2744, #2747, #2748, #2752, #2714, #2709, #2711, #2735, #2736, #2738, #2749 and #2754 on 2026-10-24 (the orchestrator's list, not re-counted here).
  - **Cause.** `gate.py`'s defer rule FAILed at once. It published a red for a head whose verdict was not yet decided, and it had no decider at all when two gates read each other before either was listed.
  - **The cheaper detector.** The self-test fixtures added here: a timeline `get` with a simulated clock, run in `governance`'s existing self-test steps. They take under a second, and their standing cost is those steps'. The design's replay scored timing perturbations but never an undecided head, which is why none of them caught this.
  - **Round 2.** No check went red. The stranding was found by review, with a harness shape (an edit span past the bound) that round 1's fixtures did not drive. The cheaper detector is the two sweep fixtures, plus the harness's `editcode` scenario and `RESIDUAL-RED` count, which now drive each tree's own `sweep.py`.
- **Same class.** R10-RCA-CODESCAN-WAIT (handoff `r10-rca-codescan-wait`, unmerged) named the same id-order premise for `pr-contract`'s codescan red. Its M1 and its prelude self-test case (M4) land here. P62's bounded codescan poll (#2737) is untouched.

## Forward-carry

- P82 (triage batch 13, unmerged ref `triage/s6-batch13`) has a tick branch that reads a red `gate` with siblings in flight as a race. After this lands, such a red appears only past `GATE_WAIT_MAX_S`, and `gate-sweep.yml` re-judges it whichever run's id it sits on. The tick's line should name that bound, and its removal should key on this PR. Carry: R10-ORCH-LEDGER (roster 61446b002)
- R10-RCA-CODESCAN-WAIT section 5 carries M1, M3 and M4 to R10-CI-LAYOUT-P2. M1 and M4's prelude case land here; M3 (echo `codescan_wait.py`'s FAIL line to the log) does not. Carry: R10-RCA-CODESCAN-WAIT (roster 216e090fe)
- Round-1 review findings 1 and 2 (the fixer-built harness was not disclosed plainly, and there was no UNCERTAINTIES section) were carried by the reviewer. The disclosure is now in this body's opening. The uncertainty is that `.github/workflows/gate-sweep.yml`'s step is still named "Re-judge the older gates at this head". It was left unrenamed because `dev/audit/harnesses/r10_ci_layout_u0c/sweep_map.json` records that name as a measurement, so only the header comment changed. Carry: R10-ORCH-LEDGER

## Friction

none
