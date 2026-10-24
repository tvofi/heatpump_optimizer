R10-GATE-DEFER: the required check `gate` (job `gate` in `.github/workflows/ci.yml`, program `tools/ci/gate.py`) went red early at every PR head that had more than one `ci.yml` run. Each run's gate listed the others. When any of them was still adding a source, it FAILed with "run(s) [...] at this head are still being judged; their gate decides". So an undecided head showed a red that a later gate had to overturn. When two gates each read the other before the other was listed, both went red and nothing decided (`gate-sweep.yml` acts only on a green gate).

Code-owned paths (`@tvofi`, `.github/CODEOWNERS` `/tools/ci/`): `tools/ci/gate.py` and `tools/ci/prelude.py`. Other paths: `dev/audit/harnesses/r10_gate_defer_race.py` (new, classified in `tests/closures.json` under `tests/harness_headers.py`'s inert reads), `dev/audit/harnesses/r10_ci_gate_core.py`, and `tests/closures.json`.

## Design

The rule is that a deferral publishes nothing until the head is decided. The one sound non-red, non-green state an Actions job can hold is "still running", so the deferring gate keeps running.

- **The gate waits, bounded.** `gate.judge` re-reads every `POLL_S` (60 s, tvofi's floor) while its only reason to fail is the deferral, up to `GATE_WAIT_MAX_S` (720 s). Then it judges with the predicate unchanged. The bound sits inside the job's `timeout-minutes: 15`. The self-test parses `ci.yml` and pins bound + one poll + 120 s under it. A decided red never waits: a prelude cross-check beside a busy run returns at once.
- **Nothing waits on a waiting gate.** `prelude.wait_sources` (formerly `wait_earlier`) releases once a run is `judging`, meaning every unit has ended and its gate is listed, rather than finished. A gate that is waiting is therefore never the thing a prelude waits for, and the waits form no cycle. `judging`, `UNITS` and the jobs read move into `prelude.py`, which both programs import, so the gate's defer test and the prelude's wait read one predicate. `gate.py` re-exports `UNITS` for `codescan_wait.py`, `ruleset_cutover.py` and `ci_predict.py`.
- **A non-code run's prelude waits for every code run, whatever its id.** This is R10-RCA-CODESCAN-WAIT's M1. GitHub numbers a same-second push and body edit out of order, which is exactly #2754's edit 40119473491 < code 40119473870. If the code run comes first, the long wait (the code run's tests and codeql) is spent in the prelude, which has a 150-minute budget. The gate's 15 minutes then only has to cover the edit run's body units. A code run never waits in its prelude, so no cycle forms.
- **A real red stays red.** After waiting, every gate at the head computes the same predicate over the same finished sources. A red source is therefore red in every published verdict. No wait can publish a PASS over a decider's red: fixture "a deferring gate published after the decider's red", and harness `2754-red`.
- **The residual.** Past the bound, the gate still FAILs deferring and `gate-sweep.yml` re-judges it. This happens only when a run at the head keeps adding sources for 12 minutes after this gate's units ended. Given M1, that means a code event arriving at an already-judged head (a reopen or same-SHA dispatch), or a stuck runner.

Alternatives and why each fails:

- **Option 2: deferral as a non-failing conclusion.** An Actions job can conclude `success`, `failure`, `cancelled` or `skipped`. `success` and `skipped` both satisfy a required check, so a deferral published as either lets a merge through while the decider is still undecided, which is a mask. Mutant M4 below plants this and it fails "#2754 shape", "decider's red" and "rerun cascade". `cancelled` needs `actions: write` on `gate`. That is a permission change on the required job, and the reads would still be red to `merge_pr.sh` and the tick.
- **Option 1 without M1.** The harness's `2754` replay over this head with `waits_on` reverted to id order makes the edit gate wait 660 of its 720 s for the code run's tail. In general that tail is unbounded relative to 15 minutes: R10-RCA-CODESCAN-WAIT measured a 28.1 min median codeql tail. So the bound would routinely expire red.
- **Option 1 with the prelude still waiting until runs are finished.** A later verdict run's prelude waits on the earlier run's gate, which waits on it. Both burn to the bound, and the gate goes red. Mutant M6 below.
- **A separate long-timeout `settle` job before `gate`.** This adds a job to `ci.yml`'s pinned graph (`tests/entities.py`'s caller set). It still needs the same wait inside `gate` for a run created after `settle` passed, so it duplicates the mechanism.

Cost, disclosed: on the #2754 shape the head's first PASS lands later than the baseline's first PASS. The edit run's body units now run after the code run's units instead of beside them; see the Figures for the harness's numbers. Against that, the baseline publishes two undecided reds first, and `gate-sweep.yml`'s re-runs follow. The replay uses the measured edit `pr-contract` span, 5.5 min. That span included `codescan_wait.py` waiting for the code run's codeql, which M1 removes, so the replay is pessimistic for the head.

The coordinator added a rerun cascade (#2748 029d6ccc). Three completed red deferring gates, a queued review decider, and a re-run of an older gate: the re-run waits for the decider rather than deferring red again, and the decider never waits on the re-run, because a run whose only open job is its gate is `judging`. This is pinned by two self-test fixtures and the harness's `cascade` scenario.

## Head

5150d17238edfd98a757687a10eeb5fd8573fbda (merge base 343fb2a2c23dbb1a78142ce869be495187b8d481).

## Mutation proof

Each production line was replaced, then `python3 -I tools/ci/gate.py --self-test` and `python3 -I tools/ci/prelude.py --self-test` were run, then the file was restored. A one-off scratch driver applied each replacement named here (old text to new, in the file named) and restored it; `git status` read clean after it.

- M1, `judge` never waits (the baseline's behaviour): gate FAILs "#2754 shape", "simultaneous completion, side A", "side B", "a deferring gate published after the decider's red", "past the bound", and "rerun cascade".
- M2, the wait without its bound: gate FAILs "past the bound, the deferral FAILs (for gate-sweep.yml), and the wait stays inside the bound" (UNBOUNDED).
- M3, waits on a decided red too: gate FAILs "a decided red never waits: the prelude cross-check beside a busy run".
- M4, the deferral publishes PASS (Option 2 as success): gate FAILs "#2754 shape", "a deferring gate published after the decider's red is that red, never a PASS", "past the bound", and "rerun cascade".
- M5, the prelude orders by id only (pre-M1): prelude FAILs "M1: waits for a LATER code run (a same-second pair numbered out of order) until it is judging".
- M6, the prelude waits until finished, not judging: prelude FAILs "M1: ..." and "a run whose gate is listed and units ended adds no source: not waited on (its gate may wait on us)".

The design's own predicate mutants (`dev/audit/harnesses/r10_ci_gate_core.py mutants`; M7 to M9 now plant where `judging` lives) give `RESULT mutants=16 survivors=0` at this head. At the merge base they also give `RESULT mutants=16 survivors=0`. M9 survived the head once, before the R3-2 fixture (a listed gate with an owed job unlisted is still busy) was restored to the gate self-test.

## Null control

- At the merge base, the finder-shape harness `dev/audit/harnesses/r10_gate_defer_race.py`, run over an export of 343fb2a2c's `tools/ci` and `tools/pr`, prints `2754: ... UNDECIDED-RED 2`, `pair: ... UNDECIDED-RED 2 ... DEADLOCK yes` and `cascade: ... UNDECIDED-RED 1`. At this head, every scenario prints `UNDECIDED-RED 0 ... DEADLOCK no`.
- The no-defect null is `single` (one run at the head): `UNDECIDED-RED 0 ... gate-wait 0 s` at both ends.
- The masking null is `2754-red` (the code run's `tests / closures` red): `MASKED 0` at both ends, and every head verdict is `FAIL tests / closures: failure`.
- The design oracle's replay is `python3 dev/audit/harnesses/r10_ci_gate_core.py replay`: `output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt` at this head. The judging inputs are unchanged.

## Figures

- `python3 dev/audit/harnesses/r10_gate_defer_race.py` at the head, and with `--ci "$D/tools/ci"` after `git archive 343fb2a2c tools/ci tools/pr | tar -x -C "$D"` at the base: per-scenario `UNDECIDED-RED`, `MASKED`, `DEADLOCK` and `gate-wait` lines as stated under Null control. On `2754` the first PASS comes at t=1847 s at the head and t=1367 s at the base (the base's 1367 s verdict follows its two undecided reds). The longest single wait at the head is 600 s, against `GATE_WAIT_MAX_S` 720.
- The same `2754` replay over an export of this head with `prelude.waits_on` reverted to id order (Option 1 without M1): the edit gate waits 660 s.
- `python3 -I tools/ci/gate.py --self-test`: `37 checks, 0 failed`. `python3 -I tools/ci/prelude.py --self-test`: `29 checks, 0 failed`. The sibling self-tests in `governance.yml` (`sweep.py`, `codescan_wait.py`, `ruleset_cutover.py`, `ghapi.py`, `alert_list.py` and `alert_list_mutants.sh`) all print 0 failed or "every mutant refused".
- `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants`: `RESULT mutants=16 survivors=0`, at both the head and the merge base.
- The scope came from `python3 tests/closure.py select --diff 343fb2a2c ...` and reads `MODE: FULL` (reason: `tools/ci/gate.py changes the gate itself`). The full suite is CI's. Locally, `tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `tests/env_drift.py --claims-only` printed `ok`, `tests/closure.py selftest` printed `ALL 117 closure shrink pins PASSED`, and `tests/layout.py` printed ok. `tests/entities.py` under the gate lease printed `4 of 2425 ENTITY CHECKS FAILED` at both the head and the merge base, and the sets of failing check names compare identical (`diff` of the sorted `FAIL` names). All four are `hb:positive_control` py-spy arms on this macOS seat, and this diff touches none of their inputs.

## Red checks

`gate` (the required check) is this PR's subject. It went red on #2743, #2744, #2747, #2748, #2752, #2714, #2709, #2711, #2735, #2736, #2738, #2749 and #2754 on 2026-10-24 (the orchestrator's list, not re-counted here; #2754 and #2752 were read from the runs and check-runs APIs).

- **Cause.** `gate.py`'s defer rule FAILed at once. It published a red for a head whose verdict was not yet decided, and it had no decider at all when two gates read each other before either was listed.
- **The cheaper detector.** The self-test fixtures added here: a timeline `get` with a simulated clock (`#2754 shape`, the simultaneous-completion pair, the rerun cascade, the decider's red and the bound). They cost under a second in `governance`'s existing gate self-test step, and their standing cost is that step's. The design's replay scored timing perturbations but never an undecided head, which is why none of them caught this.
- **Same class.** R10-RCA-CODESCAN-WAIT (handoff `r10-rca-codescan-wait`, unmerged) named the same id-order premise for `pr-contract`'s codescan red. Its M1 and its prelude self-test case (M4) land here. P62's bounded codescan poll (#2737) is untouched. P82's tick branch for "gate race" reds stays useful only past this bound; see Forward-carry.

## Forward-carry

- P82 (triage batch 13, on the unmerged ref `triage/s6-batch13`) carries a tick branch that reads a red `gate` with siblings in flight as a race. After this lands, such a red appears only past `GATE_WAIT_MAX_S`. The tick's line should name that bound, and the carry's "remove when R10-CI-LAYOUT-P2's codescan poll lands" should instead key on this PR. Carry: R10-ORCH-LEDGER (roster 61446b002)
- R10-RCA-CODESCAN-WAIT section 5 carries M1, M3 and M4 to R10-CI-LAYOUT-P2. M1 and M4's prelude case land here. M3 (echo `codescan_wait.py`'s FAIL line to the log) does not. Carry: R10-RCA-CODESCAN-WAIT (roster 216e090fe)

## Friction

none
