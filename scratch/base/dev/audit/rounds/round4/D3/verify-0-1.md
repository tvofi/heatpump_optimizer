# D3-0 panel, verifier seat 1 — round 4 verification report

- **Seat**: verifier 1 of 3, panel D3-0.
- **Tree verified**: worktree `../audit-r4-verify-D3-1`, detached at `0855277`
  (branch head; findings were measured at baseline `7dd68dd` — every mutated
  line was re-checked byte-for-byte at `0855277` before mutating, and the
  committed `pool.json` regenerates identically at this HEAD, modulo a
  post-hoc `func` annotation: `RESULT mutants=36 modules=23
  candidate_lines=9069`, same 36 `(file,line,op,old,new)` tuples).
- **Scratch policy**: every mutation was applied in
  `../audit-r4-verify-D3-1-scratch`, a detached worktree at the same commit,
  restored in `finally` and verified by SHA-256. The verifier's own worktree
  and the main checkout were never mutated. `d3_own_common.py` recreates the
  scratch worktree automatically, so a judge can re-run any `d3_own_*.py`
  harness from this worktree's root with `PYTHONPATH=tests/hastub`.
- **Hard constraints honored**: `tests/stress.py` and `./tests/run.sh` were
  never run. `tests/golden.py` and `tests/env_drift.py` were never run
  (their 150–200 s measurements are cited from the finder's report and
  marked for the judge). `heavy_neighbours` (concurrent stress.py/run.sh
  processes) was 0 at every harness start; other verifiers' worktrees shared
  the box throughout (`load1` 4.3–9.4 during my runs — quoted, not gated).
- **Own harnesses** (all under `tools/audit/round4/D3/`, all printing their
  own `RESULT` lines): `d3_own_S1.py`, `d3_own_S2.py`, `d3_own_S3.py`,
  `d3_own_S4.py`, `d3_own_INST.py`, shared runner `d3_own_common.py`,
  baseline-arm cache `d3_own_base_cache.json`.

## Method (all findings)

Per the verifier contract §4, each test-gap claim is checked by naming the
single-line production mutation, applying it in the scratch copy, and running
**both arms** of every `tests/*.py` script that plausibly covers the symbol
(chosen by grep for the symbol; `stress.py`, `run.sh`, and the Node/card
lanes excluded). A mutant counts as killed only if a script FAILS with it
and PASSES without it. Kill rule per script: exit-status change or a rise in
the `N of M ... FAILED` count, mirroring the finder's `prescreen_r4.py`.
Scripts were driven from the scratch root with `PYTHONPATH=tests/hastub`, a
private `HPO_PLANDATA` under `/tmp/d3r4-verify-own/`, and the stress thread
pin. Every harness printed `RESULT thread_factor=1.0` (timing validity) and
quoted `load1`; kill/survive verdicts are exit-status counts and
contention-immune.

Baseline arms run by my own harnesses on this tree (all green):
`tests/features.py` rc=0 failed=0 (117.2 s), `tests/entities.py` rc=0 failed=0
(27.6 s), `tests/config_flow_steps.py` rc=0 failed=0 (0.9 s).

Provenance note on the finder's record: `prescreen.json` contains only six
mutants (M01–M06, two survivors); M22 and M32 were never pre-screened by the
finder's harness, and `FINDER.md` (116 lines) has no survivor section — the
seat's JSON was never returned. The four claims were therefore verified from
zero: my both-arms runs are the only both-arms evidence for S3 and S4.

## D3-S1 — grid_fee.py:106 `if start <= end:` → `if False:` — **verify**

- **Claim**: a non-wrapping month range (Mar-Sep) becomes year-round; the
  suite's only month-range assertion uses the wrapping case.
- **My numbers** (`d3_own_S1.py`):
  - `RESULT S1_killed_by=none` — features.py 0→0 (117.2 s base / 91.9 s
    mut), entities.py 0→0 (27.6 / 29.2 s), config_flow_steps.py 0→0 (0.9 /
    0.9 s). All baseline arms green; no mutant arm changed rc or FAILED.
  - `RESULT S1_mar_sep_months_base=7`, `S1_mar_sep_months_mut=12` —
    `parse_month_range("Mar-Sep")` returns {3..9} unmutated and all 12
    months mutated (year-round). `S1_nov_mar_unchanged=True`.
- **Code reading**: the only month-range *value* assertion in the suite is
  features.py:8024 (`"Nov-Mar"`, wrapping). The one non-wrapping range in
  the suite, features.py:8020 `is_valid_spec("Okt-Dec Lör-Sön = 0.1")`, is
  validity-only and passes under the mutant (the token still parses).
  entities.py's `_grid_verdict` fixtures use `"Nov-Mar"`; config_flow_steps'
  `"nov-feb"` is wrapping and tariff-side. No test anywhere evaluates a fee
  inside vs outside a non-wrapping month range.
- **Attacks run**:
  - *Reachability*: non-wrapping ranges are legal user config
    (`is_valid_spec` accepts "Okt-Dec …"), so the mutant is a real
    behaviour change reachable from Home Assistant config — a seasonal
    surcharge silently applying all year. Money moves silently (the pool
    weights grid_fee.py 5, its top class).
  - *Wrong-gate-mode*: irrelevant here — the named scripts are not golden or
    env_drift; the finder's prescreen additionally ran the full fast closure
    plus `env_drift.py --all` for M06 with no kill (rc=0), which I cite but
    did not repeat.
- **Vote: verify.** Severity high (weight-5 module, silent year-round fee
  for a whole class of legal specs; one assertion would close it).
- **Metric definition**: first of {features.py, entities.py,
  config_flow_steps.py} whose exit status or FAILED count rises against a
  passing baseline arm on the same tree, plus the direct month-set probe.

## D3-S2 — legionella.py:521 `if not params.dhw_legionella_enabled:` → `if False:` — **verify**

- **Claim**: the disabled-feature guard in `LegionellaGuard.due_in_hours`
  can be deleted with every existing legionella assertion running enabled.
- **My numbers** (`d3_own_S2.py`):
  - `RESULT S2_killed_by=none` — features.py 0→0 (117.2 / 118.2 s),
    entities.py 0→0 (27.6 / 27.1 s).
  - `RESULT S2_disabled_due_base=None`, `S2_disabled_due_mut=-312.0` hours
    (feature disabled, last cycle 20 d ago, interval 7 d): the method
    returns a countdown instead of None. `S2_behaviour_changed=True`.
- **Code reading**: `due_in_hours()` has exactly two production consumers —
  coordinator.py:6426 (publishes `dhw_legionella_due_in_hours`) and
  legionella.py:545 (`check_mode_block`, which carries its own
  `bool(params.dhw_legionella_enabled)` guard). So the mutant's only
  reachable effect is the published attribute lying when the user disabled
  the feature. The suite: features.py's `_lg_coord` fixtures assert
  `due_in_hours() < 0` (:20197, :20250) with `enabled=True`; the one
  disabled fixture (`_lg_off`, :20233) asserts only that `check_mode_block`
  raises nothing — which its own guard still ensures. entities.py checks the
  attribute *name* is in sensor key sets (:6443, :6456), never its value.
  No test asserts the attribute is None/unknown when the feature is off.
- **Attacks run**:
  - *First probe crashed productively*: with a SimpleNamespace self the
    mutant arm raised AttributeError at legionella.py:523
    (`since = self.hours_since()`) — direct proof the guard is skipped when
    disabled; fixed the probe to a real-method instance (`__new__`) and got
    the -312.0 h number above.
  - *Severity attack*: no control-path effect — the disinfection schedule
    and the mode-block notice each gate on `enabled` themselves; only the
    published value moves. This caps the consequence at a wrong
    user-visible attribute, not a health behaviour.
- **Vote: verify.** Severity low (published-value-only on a disabled
  feature; guard deletion changes no decision).
- **Metric definition**: same two-arm kill rule over {features.py,
  entities.py}, plus the disabled-feature probe `due_in_hours()` value.

## D3-S3 — tariff.py:507 `k = max(1, min(int(k), x.size))` → `pass` — **weaken** (equivalent mutant, not a gap)

- **Claim**: the top-k clamp inside `_smooth_topk_sum` is a no-op on the one
  fixture that calls it directly and equivalent through the only production
  caller.
- **My numbers** (`d3_own_S3.py`):
  - `RESULT S3_killed_by=none` — features.py 0→0, entities.py 0→0.
  - `RESULT S3_fixture_path_diff=0`, `S3_peakcost_path_diff=0`,
    **and** `S3_k_gt_size_diff=0`, `S3_clamp_is_live_code=False`.
- **The extra fact that changes the classification**: I attacked the claim
  from the untested side — direct calls with k > x.size (k=8 and k=7 over 5
  values, plateau and non-plateau), inputs no test makes. The deleted line
  makes **no difference there either**: with k ≥ n the logistic bisection
  can only converge to "all windows counted", which is the same full sum the
  clamp's `min(k, n) = n` produces. Grep confirms `_smooth_topk_sum` has
  exactly two callers in the tree: features.py:1277 (literal k=3 over 5
  values) and tariff.py:600 inside `peak_cost`, which applies the identical
  clamp itself at tariff.py:598 (`k = max(1, min(int(peaks_averaged),
  excess.size))`) on the same array before calling. `k <= 0` is already
  returned at line 505. The only inputs that distinguish the arms are
  fractional k (the `int()` truncation) — and no caller in the tree can pass
  a fractional k (the fixture passes a literal int; `peak_cost` ints it).
- **Vote: weaken** — the finding's factual content verifies exactly (0.0
  diffs everywhere I could measure), but a mutant that no test *could* kill
  at any reachable input is an equivalent mutant, the same class as D3-S4,
  not a suite gap: there is no behaviour to pin. Reclassify bug→hygiene;
  severity minimal.
- **Metric definition**: max |base − mutant| of `_smooth_topk_sum` (and of
  `peak_cost`) over the fixture input, k>n direct inputs, and the
  production path, plus the two-arm kill rule over {features.py,
  entities.py}.

## D3-S4 — optimizer.py:1549 `end = min(i + lookahead, n_steps)` → `end = (i + lookahead)` — **verify** (equivalent, hygiene)

- **Claim (judged equivalent)**: numpy slicing clamps, so no value moves.
- **My numbers** (`d3_own_S4.py`):
  - `RESULT S4_weights_max_absdiff=0` over a 36-cell grid (n_steps ∈ {1,2,3,
    5,24,96} × dt ∈ {0.25,0.5,1,4,8,16}, seeded arrays; `lookahead =
    int(8/dt)` spans 32→0 so `i+lookahead` runs past `n_steps` in most
    cells, and the `lookahead=0` edge exercises the `if end <= i: continue`
    guard identically in both arms), computed by importing the real
    `HeatPumpOptimizer._anticipatory_weights` from each arm's tree.
  - `RESULT S4_killed_by=none` — features.py 0→0 (117.2 / 87.6 s).
- **Code reading**: both `solar_gains[i:end]` and
  `heat_loss_factors[i:end]` are Python-sequence slices, which clamp an
  out-of-range upper bound by language rule; `guard_pins.py` pins other
  mutants (M04/M11 of round #805), not this clamp. The equivalence is
  semantic, not fixture-specific.
- **Vote: verify** — hygiene, exactly as the finder judged it.
- **Metric definition**: max |weights_base − weights_mutant| over the
  shape grid, plus the two-arm kill rule on features.py.

## D3-INST — closures.json recorded seconds are accounting; golden.py ≡ env_drift --all — **verify**

- **Claim**: `recorded[*].seconds` are the seconds of the cheap stub
  invocation `derive_closures.sh` records with (0.4 s recorded for a script
  measured at 201.2 s); nothing reads them for a decision; and a standalone
  `golden.py` run is the same measurement as `env_drift.py --all`.
- **My numbers and facts** (`d3_own_INST.py`; heavy runs NOT taken, cited
  from the finder and marked for the judge):
  - `INST_recorded_golden_s=0.4`, `INST_recorded_env_drift_s=0.4` (the
    committed values today; the finder's table said 0.7 for env_drift —
    sub-second either way, immaterial).
  - Sanity point (my own timing): `tests/config_flow_steps.py` recorded
    0.6 s, measured **0.7 s** here (`load1` 8.31, provisional) — i.e. the
    recorded table is accurate for ordinary scripts; the stub problem is
    specific to the two differential guards whose recorded arguments are
    cheap *by design* (tests/README.md:159: "golden.py and env_drift.py get
    their cheap recorded arguments automatically").
  - `INST_recorded_seconds_decision_readers=2`: closure.py (the writer) and
    entities.py (schema fixtures over temp-dir copies — it never loads the
    committed file's seconds). Zero decision readers, as claimed.
  - Structure, read not run: `golden.py` `DEFAULT_MODE = "drift"`
    ("Unset means `drift`"), `DEFAULT_REF = "origin/main"`, and `run_drift`
    `subprocess.run([sys.executable, "tests/env_drift.py", "--all", ref])`
    — a standalone `python tests/golden.py` IS an `env_drift.py --all
    origin/main` run. `run.sh` skips golden.py whenever
    `GOLDEN_MODE=drift` (:377–382), so CI never pays twice, but
    tests/README.md's "Running one script at a time" list (:352, :363)
    shows both commands, and a developer following it pays the finder's
    cited 201.2 s + 152.0 s for one answer. `env_drift.py --cache-key`
    prints the key and exits (:1846–1858), which is why derive records
    sub-second.
- **Attacks run**: is it behaviour? No consumer exists — accounting, as
  claimed. Is the 503× ratio trustworthy? The numerator is the finder's
  provisional wall time under load1 4.2–6.8; the denominator and the
  structural identity are contention-immune. My vote does not rest on the
  ratio.
- **Judge notes**: re-take `python tests/golden.py` and
  `tests/env_drift.py --all <ref>` (warm and cold cache) on the quiet box;
  expect ~200 s and ~150/190 s. Consider recording a `real_seconds` or a
  comment in closures.json, or having derive_closures.sh refuse to store
  seconds for the stubbed drivers.
- **Vote: verify.** Severity low (no behaviour; a misleading sizing table
  and a documented-but-duplicated 3.5-minute path for developers).
- **Metric definition**: committed recorded seconds vs measured wall for
  one cheap sanity script; repo grep for decision readers of
  `recorded[*].seconds`; structural equality of golden.py's standalone drift
  command and env_drift.py --all.

## Cross-cutting observations for the judge

1. `prescreen.json` records only 6 of 36 mutants and `FINDER.md` has no
   survivor section (`.wip` marker present) — the round's seat was cut
   short. Two of the four "survivor" claims (S3, S4) had no both-arms
   record at all until this report.
2. Re-running `mutant_pool_r4.py` with its default `--out` **overwrites the
   committed `pool.json`**, destroying the seat's post-hoc `func`
   annotations (I restored it with `git checkout --`). A harness whose
   re-run clobbers an artifact it is compared against is a small instrument
   wart worth fixing in place.
3. `mutant_pool_r4.py`'s header EXPECTED line ("36 mutants over 12 modules")
   is stale: the same seed at branch head yields 23 modules.
4. All my kill/survive verdicts are exit-status counts taken with
   `thread_factor=1.0` and are contention-immune; the only provisional
   numbers I quote are the INST sanity timing and the finder's cited
   heavy-run timings, both marked above.
