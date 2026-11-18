# D3 round 8 — single-verifier report (v1)

Tree: /home/claude/audit-r8/seats/D3-v1 (detached git worktree at cdf82daabcfe3777d98b31489f36df5555ec9d82).
The finders' evidence was copied in with `cp -rn`. `s1_claimkill.py`, `s1_prescreen.py`, `s1_envdrift.py` and `s1_cachekey.py` hard-code `/home/claude/audit-r8/tmp/D3-s1`. My copies were rewritten (sed) to `/home/claude/audit-r8/tmp/D3-v1`, so s1_cachekey's plandata arm uses the D3-v1 path. That changes nothing about the number, because the arms only need the paths to differ.
Environment: PYTHONPATH=tests/hastub, five BLAS variables = 1, TMPDIR/HPO_PLANDATA under /home/claude/audit-r8/tmp/D3-v1. load1 ranged 0.95–4.96 during the session. thread_factor was 1.000 on every in-process harness except one noted below. Every number here is a count. The two wall times are provisional.
Production files are byte-identical to the baseline at the end: `git diff --stat -- custom_components tests` is empty. The panel has one verifier (the owner's call), so this seat did both halves of verifier.md: it re-ran each finder harness and wrote its own harness per finding.

## D3-s1-01: env_drift INHERITED CLAIMS refusal "kills" every production mutant

**Finder's harness re-run.** `s1_claimkill.py --ref <BASE>` gave refused_mutants=17 of 17 with unmutated_rc=0. Under `--perturb`: refused=0 and unmutated_rc=1. The null (ref HEAD^1) gave 0 of 17 with unmutated_rc=0. All three match the finding.

**Own harness.** `v1_claimgate.py`.
- Metric: the count of mutants for which `env_drift.check_claims_hygiene(repo, BASE)`, called in-process, returns INHERITED CLAIMS on a test-only working-tree diff, while the same diff without the mutant returns None.
- Mutants: 15 fresh ones from `mutation_table.candidates` (legionella, services, config_flow, sensor, tariff; none are in the finder's pool) plus 1 comment-only edit.
- Result: **16/16 refused**, and the null (test-only diff alone) returns None.
- Perturbation: both claim lists read as empty, i.e. a fork point that claims nothing. Refused falls to 0 and the null stays None. This perturbation is cleaner than the finder's: the finder's empties only the tree's list, which also turns the unmutated arm red.

**Attacks.**
- (a) Is the finder's exact configuration (HEAD == BASE) one the instrument runs? No, measured two ways:
  - `mutation_table.ref_skip_reason(BASE)` returns "is this commit", so mutation_table drops env_drift from the driver net.
  - The literal `env_drift.py --all BASE` exits rc=1 with SELF-COMPARISON for mutated and unmutated trees alike, so there is no rc change and no kill.

  So the D3-brief pre-screen and the quiet-window drift gate at HEAD == baseline do not false-kill. The first cannot run at all; the second skips. The false kill appears only through the finder's `_rev("HEAD")` sentinel wrapper. That part of the claim is overstated.
- (b) Where is it reachable? mutation_table `--scope changed` on a **test-only PR** whose merge base carries claims. This is `scope_files`' documented fallback, and it is exactly what my harness models. On that path the unmutated env_drift arm is green (record-PR rule, file unchanged), and any production mutant makes the diff claimable, so it gets INHERITED CLAIMS. `run_script`'s rc rule then scores "killed by tests/env_drift.py".
  - Drivers run cheapest-first and stop at the first kill. Every mutant that reaches env_drift unkilled, which means every would-be survivor, is converted to a kill.
  - On a production-touching PR the unmutated arm is already red, and `baseline_refusal` stops the table instead.
  - The nightly (HEAD^1) is not affected at this baseline (0/17).
- (c) Null present and passing. It is a count, so contention is irrelevant. It is not a grid artefact: 16/16 and 17/17 over two disjoint pools.
- (d) Consequence: on the one PR shape the fallback exists for, the mutation lane cannot report a survivor. The lane is advisory rather than a required context. Medium stands, with the scope narrowed to (b).

**Same mechanism as.** This same refusal would "kill" the three D3-s2 mutants below if env_drift were driven on such a tree. That is why my suite run for D3-s2 excludes env_drift.

## D3-s1-02: env_drift cache key hashes HPO_* variables no capture reads

**Finder's harness re-run.** `s1_cachekey.py` gave distinct_keys=4, null_equal=1 and capture_reads=0. `--perturb` gave distinct_keys=1. This matches.

**Own harness.** `v1_cachekey.py`. The keys come from the production CLI, `env_drift.py --cache-key BASE --all`, run as a subprocess per arm.
- Metric: the number of HPO-only environments whose key differs from the clean key. Result: **4 of 4** (plandata ×2 paths, lock label ×2). The four keys are all distinct.
- Null: clean_again equals clean.
- Positive control: OMP_NUM_THREADS=2 splits the key.
- Perturbation (in-process, HPO_ removed from `CACHE_ENV_PREFIXES`): 0 of 4 differ. thread_factor printed 2.97 on that in-process arm. That arm holds counts only, and I did not re-take it.
- Empirical arm: the shared cache holds **1 pair** of entries whose key_inputs differ only in HPO_PLANDATA (the D3-s1 path), and **both entries have an identical capture_sha256**. That is a re-capture that was paid for and produced the same bytes.
- Dynamic read arm (`--reads`): a full `env_drift.py --capture <tree> --all` (56 payloads) ran with `os._Environ.__getitem__` and `__iter__` wrapped, and HPO_PLANDATA plus the lock variables set.
  - 0 HPO_* reads and 0 whole-environment iterations.
  - Wall 169 s at load1 ≈ 2 (provisional).

**Attacks.**
- CI never sets HPO_GATE_LOCK_LABEL. `tests.yml` names only HPO_RUNS_*, which are not in the capture step's environment as far as grep shows. So CI hit rates are unaffected, and the cost lands on locked local and audit-box runs and on HPO_PLANDATA-setting harnesses.
- Each lock label gets its own key, so each seat pays its own cold capture.
- There is no correctness impact. A miss costs a capture: 169 s at load 2 here, and the finder's 23 min at load 23 is provisional.
- Side note (not a finding): at this moment even the clean key misses the warmed entry, because the `packages` component changed after warming (ast_serialize appears in the inventory). That is a shared-box artefact.
- Severity: resource-only and local-only. **Weaken to low.**

## D3-s2-01: `LegionellaGuard.hours_since` clamp untested

**Finder's harness re-run.**
- future: 0.0 → −2.0; past: 2.0 → 2.0.
- entities.py with the mutant: 9 of 1732 failed, the same count as the baseline, so the mutant survives. This matches.
- The finder's pre-screen ran only structure.py and entities.py, which is not the closure.

**Own suite run.** `v1_suite_mutants.py` ran every script in the measured closure of legionella.py: 16 scripts, i.e. tests/closures.json less env_drift.
- Kill rule: rc or failed-count changes against the unmutated run in the same tree.
- m05 (clamp removed): **0 killers**, including features.py (which drives dst_checks) and entities.py. The gap is real.
- Positive control (services `>`→`<`): killed by features.py.

**Own consequence harness.** `v1_legionella_due.py`, with interval 1 day, last_cycle 2 h in the future, and the clock stepped via `dt_util.freeze`:
- Published due_in_hours at t0 moves 24.0 → 26.0.
- The **instant the timer first reads overdue is unchanged (delta 0.0 h)**: 26 h after t0 in both arms.
- The optimizer's deadline derived from the state moves +2.0 h, but only while now < last_cycle. Without the clamp it matches the overdue instant. With the clamp it is 2 h earlier than the timer's own overdue instant.
- Null (skew −2 h): all identical.

**Attacks.**
- The finding's consequence, "silently push the anti-legionella due time later", is false for the due instant. The clamp does not move when disinfection becomes due. Clamped, the age sits at 0 until the clock passes last_cycle.
- What the mutant changes is a published attribute and a per-plan deadline, and only during the skew window. The reachable trigger is a backward clock step or a restored store with a future timestamp; there is no load-time sanitiser.
- The test gap stands. Severity: **weaken to low**.

## D3-s2-02: dhw-min deadband boundary untested at both service sites

**Finder's harness re-run.** At the boundary, the baseline accepts and the mutant raises `*_no_deadband`. The null at −0.01 is accepted. Both sites match.

**Own harness.** `v1_deadband.py` goes through the real `ha_setup_component` + `ha_setup_entry` and `hass.services.async_call`, with the mutant applied in memory only.
- dhw_min 50.0 with the default setpoint 55 (ceiling 50) is accepted by both services on the baseline.
- The `>=` mutant at each site separately rejects only at its own site: **boundary_flips=2 of 2**.
- Null (49.99): accepted everywhere. Positive control (51, the value features.py uses): rejected everywhere.

**Suite run.** `v1_suite_mutants.py`: m11 (services.py:486) and m12 (services.py:823) each had **0 killers** across the services.py closure of 11 scripts less env_drift, including features.py and entities.py.

**Attacks.**
- The path is reachable in real HA: a user sets minimum = setpoint − 5.
- The consequence is a legal value being refused with a translated error. It is minor, and the error text says "at most", which the mutant would contradict.
- config_flow.py:895 enforces the same boundary separately and was not measured here.

Low stands. **Verify.**

## Harnesses (all under tools/audit/round8/D3/)

| harness | what it measures |
|---|---|
| v1_claimgate.py | D3-s1-01 |
| v1_cachekey.py | D3-s1-02; `--perturb`, `--reads` |
| v1_legionella_due.py | D3-s2-01, consequence |
| v1_deadband.py | D3-s2-02 |
| v1_suite_mutants.py | D3-s2-01/02 closure survival; `--posctl` |

Logs: /home/claude/audit-r8/tmp/D3-v1/{reads,suite,posctl}.log.
