R10-HOTFIX-GATE-BUSY-DEFER, the carries part (topic r10-hotfix-gate-busy-defer-p5). Every one of the 12 carries ends below in a fix with its controls, a `covered by <sha>` line naming the code and test that prove it, or the owner's recorded dismissal.

**Carry numbering.** Each carry line names the roster's 1-based number and the brief's 0-based one. Everywhere else in this body, "carry N" is the brief's number.

**What the tree already did, and what was left.** The deadlock this group was cut for is closed on main:
- #3246 (355d9965a) added `busy()`'s id tie-break.
- #3276 (812bb8747) made `judging()` read a deferring run's skipped caller as judging.
- #3287 (5c1fa41fb) publishes a deferral at once and lets `gate-sweep.yml`'s `settle` re-judge it.
- #3290 (48af0864a) made the train and `ci-watch` read a deferral red as a deferral, not as RED.

Three defects were left, and this diff fixes them:
1. **A stale pin (carries 3 and 5).** A gate re-run executes the programs of its event's original `base.sha`, so the sweep's job re-runs kept replaying a pre-fix `busy()`. The recorded #3244 triple deadlocks under its live pin 9cbd7dd0 and decides under main (`## Figures`). The fix is `sweep.py`'s `stale_pin`/`fresh`: where the base changed `tools/ci/*.py` after the pull request's `base.sha`, the sweep dispatches ONE fresh `ci.yml` run (`pr`, `base`) instead of re-running. That run rev-parses `origin/<base>` when its job starts, and its gate is the newest check run at the head. A dispatched run created at or after the stale gate's conclusion is that fresh judge already, so nothing is dispatched twice and the branch cannot loop. It lives in the sweep because the sweep runs main's copy (`gate-sweep.yml`, `ref: github.sha`), so it reaches every PR at once. `gate.py --refresh` runs the pinned copy itself, so a change there could not reach the PRs it is for.
2. **A source shadowed by run id (carries 11 and 10).** `gate.gate` took each unit's source from the highest-id run, so a body run that GitHub numbered below its code run had its read of the latest body shadowed. The source is now the run whose jobs for the unit started LAST, then the higher id. `arch-score` reads the PR live at its start (`arch-score.yml`, `gh api .../pulls/$NUMBER`), so a later start is the fresher read. This run's own unit, while its listing lags, is never displaced: that is fail-closed, and it is a design choice. Before, a higher-id sibling's green could cover a lagging own unit; now the gate re-reads its own listing inside `lag_bound`. `prelude.run_jobs` fills an optional `starts` map from the listing it already reads, so no request is added.
3. **No pin for the three-gate shape (carry 1).** A self-test case and a recorded replay scene now pin #3244's three-gate mutual deferral. Two stale parts of the proof instruments were retired as #3287's design: the RCA replay's `C3-AT-ONCE` defect class, which failed every replay at main, and `r10_ci_gate_core.py`'s M26, whose anchor no longer exists.

**Alternatives.**
- **Stale pin:**
  - Change `ci.yml` to restore from the live base on a re-run. `ci.yml` is outside this group, and the pin is deliberate (a PR judges with its base's programs).
  - Read each gate's `programs restored from` log line. The logs endpoint redirects to a blob, which `ghapi` does not follow as JSON. The PR's live `base.sha` equals that line on every pull_request-event gate measured (`## Null control`).
  - Re-run and accept the old program. That is the #3261 attempt-10 loop the carry records.
- **Source order:** order by run `created_at`. A same-second push and edit tie on it, and a re-run executes a unit afresh without moving it, so a job start is the only stamp that orders the reads.

**Order against #3243 (R10-GATE-LEASE-TOCTOU).** #3243 merged first (5421413b). It touches `tests/gate_lock.py` alone, and this diff does not touch that file, so neither order conflicts.

Carry 1 (the brief's carry 0): covered by 355d9965a (#3246). `busy()`'s clause `and not (r["id"] > ctx["run_id"] and started(r))`, tools/ci/gate.py. The self-test `busy-defer: of two started gates at one head the lower id defers to none, the higher to the lower` drives runs 42192623509 and 42193153511 and reads `([], [lo])`. Mutant M17 (r10_ci_gate_core.py) is killed by it.

Carry 2 (the brief's carry 1): partly covered, remainder fixed here.
- Covered by 355d9965a (the tie-break) and 812bb8747 (`judging()`). At main the recorded #3244 triple replays `DECIDED`, all three PASS (`## Figures`).
- Covered by 5c1fa41fb (`sweep.settle`), so a deferral resolves without a hand re-run. Self-test `#3282: the sweep for the code run's completion re-runs that deferring gate, no human`.
- Covered by 48af0864a: the readers take that transient red as a deferral (`merge_train.classify_at`).
- The red itself stays, #3287's design: a job that holds no runner can only conclude, and a skipped required check reads as passing.
- Fixed here:
  - The three-gate shape is pinned: `busy-defer, three gates (#3244)`, red under M17 and M18.
  - The scene `3244-triple` replays DEADLOCK at the live pin and DECIDED at main and at this head.
  - The stale-pin dispatch, the reason #3244's and #3261's reds outlived the fix.
- The scratch `rerun-gate.sh` is in no tree path (grep below). With the sweep re-judging deferrals and dispatching stale pins, nothing is left for it.

Carry 3 (the brief's carry 2): covered by 5c1fa41fb. `judge()` re-reads only for `lag_bound(why)`, which is 0 for a deferral, so no deferral waits 720 s. Self-tests `#3282: the deferring edit gate publishes CI's deferral at once and holds no runner` and `C3: a deferring edit gate beside a busy code run defers at once, no nap; re-run once the code run ends, it judges its sources`. A code run longer than any bound is re-judged by the sweep when it completes, so the bound question is moot.

Carry 4 (the brief's carry 3): fixed here (stale pin, above). The orchestrator step it proposed ("re-judge only after a fresh event") is now the sweep's own dispatch, so no policy text is owed.

Carry 5 (the brief's carry 4): covered by afc1586a, the merge base: no defect. `governance / instrument-self-tests` is not a required context. The gate's governance names are `UNITS["governance"] = ("policy-docs", "wave-script", "env-matrix")` (tools/ci/prelude.py), and `REQUIRED` is built from `UNITS` alone. The gate job 128321406871 read `WORKSET: ... governance ...` and printed `PASS` under pinned 294a880d with the same names. The cancelled job is reported under "Not gating" by design. Making it required is the gate owner's call, not raised here.

Carry 6 (the brief's carry 5): fixed here. The first item (re-prove with `replay --ci <export>`) is under `## Figures`. The second item, RCA 5.2's countermeasure, is built in `sweep.py`, so the manual 5.3 dispatch is retired once this merges.

Carry 7 (the brief's carry 6): dismissed by the owner (bar 2026-11-08, triage batch 136 entry 425); no work.

Carry 8 (the brief's carry 7): covered by 5c1fa41fb. "Nothing re-judges it" is false by construction: `Sweep.settle` and the green branch re-run a deferring gate with no human. The self-test #3282 replay posts the re-run with tvofi's human re-run removed.

Carry 9 (the brief's carry 8): dismissed by the owner (the same ruling as carry 6, which it repeats); no work.

Carry 10 (the brief's carry 9): covered by 5c1fa41fb, the same as carry 7, which it repeats.

Carry 11 (the brief's carry 10): measured first, then fixed here through carry 11's source order, not the re-run the carry proposed.
- **The measurement.** `dev/audit/harnesses/r10_codescan_wait_race.py --since 2026-11-01T06:21:44Z --until 2026-11-08T06:21:44Z --rows`, over the 7 days before the merge base, reads 1821 runs and 5 ORDERED red edit runs. That count is a superset: it counts any failure of the codescan step.
- **Narrowed to the carry's rule** (an ordered pair; the job log carries `no run at this head owns a finished codeql unit`; a codeql leg of the code run succeeded after that red) by a probe over those runs (scratch `probe10.sh`; its rule is the three conditions just named). It reads **3** edit runs on 2 heads: 42373556850 (head 97786d25), and 42385417686 and 42387066581 (#3252, head 31347980).
- **The other two** (41952981275, 42246412814) carry the line, but the code run's codeql legs had succeeded before the red, so no source finished later.
- **3 meets the build threshold.**
- **What was built.** Only `gate` is a required context (tools/policy/fixtures/required-contexts.json), so the stale red mattered only as the gate's source. Under id order, the higher-id edit run's red outranked the code run's later green. #3252's code-run gate at 17:14:38Z (attempt 2) failed on `pr-contract / pr-contract: failure (run 42387066581)` while its own `pr-contract`, started 17:13:48Z, was green. `pr-contract` reads the body live at its start (pr-contract.yml, "THE BODY IS READ FROM THE API AT RUN TIME"), so the later start is the fresher read, and carry 11's source order takes it.
- **The replay of that recorded gate** (scene `3252-nosource`): `FAIL pr-contract / pr-contract: failure (run 42387066581)` at main, the live verdict, and PASS at this head. The sweep then re-runs the edit runs' red gates through its green branch, and they read the same fresher source.
- **Why not the proposed log-keyed re-run.** It would need the sweep to read job logs (a raw, redirect-following mode in `ghapi`) and re-run whole `pr-contract` jobs. It would still leave the gate taking the higher id's red until that re-run finished.
- **Arms:**
  - The #3252 shape passes once the code run's pr-contract is green: the replay.
  - The null, a fresher red is still the source, never passed over: self-tests `C3: a body edited after the code run's gate passed is still judged (this run's own pr-contract)` and `source order: ... null`.
  - M27 (id order) reads `MISREAD` on the scene, replay exit 1.
- **The residual, stated.** The red stands until the code run's own `pr-contract` runs. At #3252 that was the code run's re-run, about 1.5 h after the first red, against 3 h 10 min live.
- **Two harness defects fixed on the way**, both now in its selftest (12 checks):
  - The run listing truncated silently at GitHub's 1000-run cap, and the 7-day window holds 1821. It now reads day windows and refuses a window at the cap.
  - Run 42425147012's `filter=all` jobs listing answers HTTP 502 on pages 2-6 every time. It is now read per attempt after a 5xx.

Carry 12 (the brief's carry 11): fixed here (source order, above).

## Head

1202efb64f6bf776c32fc8131c82a8220ec89fe5, cut from origin/main afc1586a4424f997ce70ed2003add9d7de93d6f6. origin/main moved to 2a3c05644d85b7ee5c2c314fde5aca950e4aba91 (v7.1.6's stamp, #3307, #3309) before the handoff. `git merge-tree --write-tree origin/main HEAD` reports no conflict, and `git diff --stat afc1586a 2a3c0564` touches no `tools/ci/`, `.github/workflows/` or harness path this diff changes. Under the owner's ruling of 2026-11-07 the branch is not merged and prepr is not re-run for it; the merge train re-proves this head on current main.

## Mutation proof

Failing tests first, each committed red before its fix:
- a23110b7c, over main's `sweep.py`: `sweep self-test: 59 checks, 5 failed`:
  - `stale pin: a red gate pinned before a tools/ci change on its base is re-judged by ONE dispatched run (pr, base), never re-run`
  - `... two stale reds at one head take one dispatch, one compare`
  - `stale pin, settle: the #3261 pair ...`
  - `stale pin, no loop: ...`
  - `stale pin null: a dispatched run created before the stale gate concluded is no fresh judge: dispatch`
- b020e96f0, over 5fa576c6f's `gate.py`: `gate self-test: 81 checks, 2 failed`:
  - `source order: a LOWER-id edit run's red arch-score started after the code run's own -> the code gate reads the later start`
  - `source order null: this run's own unit, listed lagging, is never displaced by a later sibling's green`

Sweep mutants, each applied to a `tools/ci` copy and run with `python3 -I <copy>/sweep.py --self-test`:
- **S1, the stale branch in `judge()` deleted.** 5 failed, the five above.
- **S2, the `tools/ci/*.py` filter replaced by True.** 1 failed: `stale pin null: a base that moved without touching tools/ci/*.py re-runs the gate as before`.
- **S3, the fresh-run guard off.** 1 failed: `stale pin, no loop: a dispatched run created after the stale gate concluded re-judges the head; nothing posted`.
- **S4, one dispatch per sweep off.** 2 failed: `two stale reds ...` and `stale pin, settle: the #3261 pair ...`.
- **S5, the event key dropped.** 1 failed: `stale pin null: a dispatched run's gate (it rev-parses origin/<base> at its re-run) is re-run, the base never compared`.
- **S6, the guard's created-vs-concluded comparison replaced by True.** 1 failed: `stale pin null: a dispatched run created before the stale gate concluded is no fresh judge: dispatch`.
- **S7, the 300-file cap dropped.** 1 failed: `stale pin: a compare listing at GitHub's 300-file cap may hide a tools/ci change: a fresh run`.
- **S8, the fork guard off.** 1 failed: `stale pin null: a fork head (no branch here to dispatch on) is re-run as before, the base never compared`.

Gate mutants, `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants`, which runs the gate self-test and its replay per row:
- `RESULT mutants=22 survivors=0`.
- **M17 (tie-break deleted)** reds `busy-defer, three gates (#3244): the lowest defers to none, each other only to the gates below it`, beside the pair case.
- **M27 (source order by id alone)** reds both `source order` cases.
- **M28 (a lagging own unit displaced)** reds the `source order null`.

The diff's added lines (owner ruling: MUTANT_CMD). The command is `MUTANT_CMD="bash -c 'python3 -I -B tools/ci/gate.py --self-test && python3 -I -B tools/ci/sweep.py --self-test && python3 -I -B tools/ci/prelude.py --self-test'" MUTANT_MAX=0`, through prepr.sh's diff-mutant step. The same run standalone: `python3 -I tools/audit/seat/mutant_run.py --diff afc1586a...HEAD --max-mutants 0 --report-only --cmd "<that>"`.
- 73 mutants, every site `mutant_run.py --list` derives from the diff (gate.py 11, prelude.py 3, sweep.py 25, sweep_selftest.py 34). Wall time 15.8 s, 6 SURVIVED, each under `## Unpinned sites`.
- `-B` is load-bearing. Without it the imported `sweep_selftest.py` is served from a `.pyc` its same-size, same-second mutant does not invalidate. Two sites (a `w.runs[5]`->`[6]` that raises KeyError when applied by hand) read SURVIVED that way, and both are killed under `-B`.
- Four real survivors were killed by checks added before this run:
  - `sweep.py`'s guard `>=`->`>`, and its deleted `left to this sweep's dispatched run` line (0c215489e).
  - The fake dispatch's 204->205, and the deleted `w.sweep()` under the same-second check (3105bbd06).

## Unpinned sites

Every survivor is a constant in a test fixture that no assertion reads, so each is an equivalent mutant:
- `tools/ci/gate.py`, self-test `trio` line, `pair[0]`->`pair[1]`: `pair`'s two rows carry identical jobs and differ only in `id`, which the line overwrites.
- `tools/ci/gate.py`, self-test `source order null`, id 101->102: any id above 100 is the later sibling the null names. The start stamp, not the id, is what it varies.
- `tools/ci/sweep_selftest.py`, the stale-pin cases `pinned(run(1, ...` at four sites, 1->2: they rename the stale red run. Each assertion reads the posts, the dispatch body and the named fresh run 5, never the stale run's id.

## Null control

- **Pin equals base.sha.** For every pull_request-event run at the open PRs' live heads, the gate job log's `programs restored from <sha>` was compared with the PR's live `base.sha`: 19 of 19 SAME. The workflow_dispatch run 42446409559 (PR #3308) read DIFF, pinned 5bc009bc against base d2e4d2d1, because a dispatch rev-parses `origin/<base>` at its start. That is why `stale_pin` keys on the event. Command: `scratchpad pincheck.sh`, whose output is the per-run SAME/DIFF line. A wrong assumption would have printed DIFF on a pull_request row.
- **`stale_pin` against git, live and read-only** (no post). It returned the pin for #3305 (17e11579), #3291 and #3245 (4b5d771b), and None for #3307 (afc1586a) and #3308 (d2e4d2d1). `git log --oneline <pin>..origin/main -- 'tools/ci/*.py' | wc -l` reads 6 for 4b5d771b and 0 for d2e4d2d1 and afc1586a. Each stale call matches a non-zero count, each None a zero.
- **The base moved without touching tools/ci** (`custom_components/...`, `tools/ci/fixtures/f.json`, `tools/pr/prepr.sh`): the gate is re-run as before. A dispatched run's gate is re-run, the base never compared. So is a fork head. Every pre-existing sweep check passes unchanged (`sweep self-test: 62 checks, 0 failed`).
- **Source order.** A lower-id edit run whose red started BEFORE the code run's own green leaves the code gate PASS (`source order: ... null: started before it`). Every pre-existing gate case passes, the #3263, #3261 and #3282 recorded replays included (`gate self-test: 81 checks, 0 failed`).
- **The three-gate scene.** At main, unmutated, all three gates PASS. Its live verdicts are the recording's own `verdict` fields.

## Figures

- Self-tests at this head:
  - `python3 -I tools/ci/gate.py --self-test`: 81 checks, 0 failed.
  - `python3 -I tools/ci/sweep.py --self-test`: 62 checks, 0 failed.
  - `python3 -I tools/ci/prelude.py --self-test`: 76 checks, 0 failed.
- RCA replay (dev/audit/harnesses/r10_rca_gate_busy_defer_2.py, sha1 556b35c217d462db2fc89f669f790ada1a7699ee). Fixture scenes `3244-triple` and `3252-nosource` were added by `record --scene <name>`, additions only. Each `--ci` copy is `git archive <sha> tools/ci tools/pr | tar -x -C $D`, run as `python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci $D/tools/ci`:
  - at 9cbd7dd0 (the triple's live pin, lacking 355d9965a): `3244-triple: DEADLOCK`, each gate `FAIL run(s) [<the other two>] ...`, as live.
  - at afc1586a (main): `3244-triple: DECIDED`, all PASS naps=0; `RESULT ... defects=no`.
  - at this head (`replay`, no `--ci`): `3244-triple` the same as main; `3252-nosource: DECIDED`, PASS; `defects=no`, exit 0.
  - `3252-nosource` at main: `MISREAD`, `FAIL pr-contract / pr-contract: failure (run 42387066581)`, the recorded live verdict; exit 1. Under M27 on this head: the same `MISREAD`, exit 1.
  - M17 on main: still `DECIDED`. The honest listing is ordered by `judging()`, so the self-test's lagging trio is the case that kills M17.
- Gate mutants: `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants` (sha1 fcee81f4174409a55f1e57f7bbd4e83904aadbd2): `RESULT mutants=22 survivors=0`. At main it read `mutants=21 survivors=1`, M26 NOT RUN.
- Diff mutants: 73 mutants, 6 SURVIVED (equivalent, `## Unpinned sites`), wall time 15.8 s (`## Mutation proof`).
- Codescan harness (dev/audit/harnesses/r10_codescan_wait_race.py, sha1 b25381629a7f71ee8826435b9d5553a879a4be53): `--selftest` 12 checks, 0 failed. The 7-day reading is under carry 10.
- `rerun-gate.sh`: `git grep -n rerun-gate` over the tree: no hit.
- Live gate census since #3287 (`r10_rca_gate_busy_defer_2.py census --since 2026-11-07T19:14:31Z`): not taken. The run reads every attempt and gate log in the window and was stopped at this session's 30-minute background limit before printing. No figure in this body rests on it.
- Class census, the seams where a program orders runs at a head by id (fixer step 8). Rule: `grep -nE "sorted\(.*\"id\"|r\[\"id\"\] [<>]|i [<>] run_id|\"id\"\] [<>]" tools/ci/gate.py tools/ci/sweep.py tools/ci/prelude.py`, self-test lines aside. At the merge base it also returns `gate.gate`'s source loop (`sorted(others + [me], key=lambda r: r["id"], reverse=True)`); at this head it returns 8 lines:
  - `gate.gate`'s source loop: closed in this diff (`fresh`), so the rule no longer returns it.
  - `gate.busy` (two lines, the id tie-break): kept. It orders two started gates' deferrals, not sources, and M17/M18 pin it.
  - `sweep.undecided` (two lines, `i > run_id`, `i < run_id`): kept. It mirrors `busy()`'s tie-break (#3287).
  - `sweep.run` and `sweep.settle`'s `sorted(..., key=id)`: these set the order of re-runs only and decide no verdict. Already guarded by the once-per-run `rerun_ids`.
  - `prelude.waits_on` (`run["id"] < run_id`): a distinct finding, R10-RCA-CODESCAN-WAIT's inverted-pair wait. Not this group's; untouched.
  - `prelude.defer_to`'s `sorted(..., key=id)`: it returns the first unfinished code run whose pr-contract has not started. Any one qualifies, so the order decides nothing.
- Ratchet and scope:
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `python3 tools/audit/archscore/score.py --diff afc1586a`: `Architecture score: dS +0.0000 NULL`.
  - `tests/closure.py select --diff $(git merge-base origin/main HEAD)` reads `MODE: FULL`, with the reason `tools/ci/gate.py changes the gate itself`. The full suite is CI's.
  - `VERSION`, the manifest, the `RELEASE_NOTES.md` heading, both claim files and every `*_budgets.json` are byte-identical to the merge base.
- prepr: `tools/pr/prepr.sh` with this body and `MUTANT_CMD`/`MUTANT_MAX=0` as under `## Mutation proof`, on the committed head 1202efb6, printed `PRE-PR: 1202efb64f6bf776c32fc8131c82a8220ec89fe5 ... rc=0`.
  - Its `ci predict` step: `no closures, fast, governance or instrument red predicted against afc1586a4424`.
  - Its `merged structure` step (HEAD merged with origin/main): `STRUCTURE RATCHET PASSED`.
  - Its diff-mutant step: `6 survivor(s)`, the six under `## Unpinned sites`.

## Red checks

none. No pull request exists yet for this head; `tools/pr/prepr.sh`'s `ci predict` step is the prediction (`## Figures`).

## Forward-carry

none

## Friction

- frugal-inline-budget: cost: a session guard caps inline searches per prompt, so the carry survey went through one subagent. Carry: dismissed: a session plugin's guard, not this repository's policy
