# D3 round 4 — verifier 3 report (panel D3-0, verifier 3 of 3)

- **Verifier worktree**: `../audit-r4-verify-D3-3`, detached at `0855277`
  (branch head). The findings were measured at baseline `7dd68dd`; the branch
  has ~30 commits past it, so an `env_drift.py --all 7dd68dd` run *here* would
  show the branch's own drift, not the mutant's — the executed CI-mode check
  below is the finder's recorded run (M01/M06, rc=0 with the mutant applied)
  plus my enumeration of every fixture the differential compares. Where that
  matters I say so per finding.
- **Machine**: same box, shared — `load1` 4.6–6.9 during my runs. Every number
  I rest a vote on is a count, an rc, or a set/array equality
  (contention-immune). I ran no timing measurement this round.
- **Constraints honored**: no `tests/stress.py`, no `./tests/run.sh`, no
  200 s `golden.py`/`env_drift.py` measurements (marked for the judge below).
  All mutants were applied in this scratch worktree by **line number**
  (exactly as `prescreen_r4.py` does — note `grid_fee.py`'s line 106 text is
  NOT unique in the file; `parse_day_range` has the identical line at :125,
  so string-replacement would mutate the wrong function), each restored and
  verified with `git status --porcelain` (empty after every restoration).
- `python3` = 3.11 (framework build), `PYTHONPATH=tests/hastub` from the
  worktree root, thread pins exported on every test run.

## Harness re-runs

- **`mutant_pool_r4.py`** re-run with `--out /tmp/verify33_pool.json`:
  `RESULT mutants=36`, `modules=23`, `candidate_lines=9069` — reproduces the
  committed `pool.json` exactly (all 36 mutants byte-identical: id, file,
  line, old, new, op, weight). The only delta is a `func` annotation key the
  finder added to the recorded copy; the sampler itself does not emit it.
  The pool is deterministic at seed 20260912.
- **`prescreen_r4.py`**: not re-runnable to completion here — its state file
  records only **M01–M06** (the seat's JSON was never returned; the run was
  interrupted). In particular **M22 and M32 have no finder record at all**;
  their survivor status below rests on my own targeted runs, not the
  finder's. The baseline block is intact and green (15 drivers rc=0,
  `tests/golden.py` measured 201.2 s there — that is where the finder's
  golden number comes from — and `tests/env_drift.py --all` 152.0 s, warm).

## The CI-mode attack (applies to S1 and S2)

`tests/env_drift.py --all` captures the **branch** side from the working
directory (`env_drift.py:2021-2034`: `--capture repo`), so an uncommitted
mutant IS visible to CI's mode; the finder's pre-screen used the right gate
(`prescreen_r4.py:run_env_drift`), and excluding `tests/golden.py` from the
drivers is sound because `run.sh:382` skips it outright under
`GOLDEN_MODE=drift` (CI: `.github/workflows/tests.yml:286,719`) — standalone
it is the same differential (`golden.py:156-176` execs
`env_drift.py --all <ref>`; `DEFAULT_REF="origin/main"`). So no survivor here
is a false gap born of the 5-fixture default mode. I then enumerated the
fixture set `--all` compares, per mutant, to confirm CI genuinely cannot see
these lines (details below).

---

## D3-S1 — grid_fee.py:106 `parse_month_range` non-wrapping branch

**Claim**: deleting `if start <= end:` (M06) turns a non-wrapping range like
Mar-Sep into year-round; the only range assertion uses the wrapping case.

**My numbers (all executed here)**:

| arm | `parse_month_range` result |
|---|---|
| clean | `Mar-Sep → {3..9}` (7), `Okt-Dec → {10,11,12}`, `Nov-Mar → {1,2,3,11,12}`, `Jul → {7}` |
| M06 applied | `Mar-Sep → {1..12}` (12), `Okt-Dec → {1..12}` (12); `Nov-Mar` and `Jul` unchanged |

| script (with M06 applied) | rc | verdict line |
|---|---|---|
| `tests/features.py` | 0 | `ALL 2540 FEATURE CHECKS PASSED` |
| `tests/config_flow_steps.py` | 0 | pass |

Clean arm of `tests/features.py`: rc 0, `ALL 2540 FEATURE CHECKS PASSED`.
Both arms green while my own harness shows a real behaviour change → the
mutant is not killed by the suite.

**Attacks and outcomes**:

- *Mutant equivalent?* No — month set provably changes (table above).
- *Reachable in production?* Yes, executed:
  `spec_problem("Mar-Sep Mon-Fri 06:00-22:00 = 0.25") = None` and
  `is_valid_spec("Mar-Sep = 0.25") = True` — the config flow accepts and
  stores a non-wrapping range; on the clean tree the January fee is the
  0.05 fixed component only, July 0.30. Under M06 the same stored spec
  surcharges January too. A seasonal grid-fee rule silently applies
  year-round — money-adjacent, weight-5 module by the finder's own ladder.
- *Would CI's `env_drift.py --all` catch it?* No, and I verified why by
  enumerating what `--all` compares: the only coordinator fixture with
  `grid_fee_mode` rules is `coord_grid_fee`, whose rules are
  `"Mon-Fri 06:00-22:00 = 0.25"` — **no month token at all**
  (`tests/golden.py:894`); `peak_masked` sets `peak_months` as a literal
  `frozenset`, bypassing the parser; `tests/entities.py`'s grid verdicts use
  `Nov-Mar` (wrapping). The finder's recorded `env_drift.py --all` run with
  M06 applied is rc=0, consistent with this. Not a wrong-gate artefact.
- *Is the assertion really only wrapping?* Yes: `tests/features.py:8023`
  ("a wrapping month range covers the wrap and not the middle", `Nov-Mar`)
  and `:8139` (`"Jul"` single token). `is_valid_spec("Okt-Dec …")` at :8018
  checks parseability only — under the mutant it still parses, so it stays
  green (observed).

**Vote: verify.** Severity high — a wrong fee schedule for every month
outside the configured season, silently, in the module the finder weights 5
(money); not critical because it requires a non-wrapping seasonal rule, which
the corpus suggests is the rarer form in this locale (höglasttid wraps).
Class: bug (a test gap a real seasonal-pricing bug could hide in).

---

## D3-S2 — legionella.py:521 the disabled-feature guard in `due_in_hours`

**Claim**: deleting `if not params.dhw_legionella_enabled: return None` (M01)
survives because both existing assertions run enabled.

**My numbers (executed)** — my own probe on a real `LegionellaGuard`
(interval 7 d, `last_cycle` set, `attempt=None`):

| arm | enabled=True, 20 d since | enabled=False, 20 d | enabled=False, 1 d |
|---|---|---|---|
| clean | -312.0 | `None` | `None` |
| M01 applied | -312.0 | **-312.0** | **144.0** |

| script (with M01 applied) | rc | verdict line |
|---|---|---|
| `tests/features.py` | 0 | `ALL 2540 FEATURE CHECKS PASSED` |
| `tests/entities.py` | 0 | `ALL 1352 ENTITY CHECKS PASSED` |

Clean arms: features.py green (above); entities.py rc=0 in the finder's
baseline and the attribute-key checks are name-presence only.

**Attacks and outcomes**:

- *Mutant equivalent?* No — disabled-with-history returns a countdown
  instead of `None` (table).
- *Consequence bounded?* Yes, and I verified each consumer:
  `due_in_hours` is read at `coordinator.py:6426` (data-dict attribute),
  `sensor.py:1183,1230` (republished), and `legionella.py:545`
  (`check_mode_block`, which **re-guards** on
  `bool(params.dhw_legionella_enabled)` at :550, so repair notices are
  unaffected). The optimizer's legionella placement does not call it. So the
  defect is exactly one wrong published attribute
  (`dhw_legionella_due_in_hours`) in the disabled-with-history state.
- *Would CI's `env_drift.py --all` catch it?* No: plan-scenario captures
  (`golden.py:capture`, :747-830) record the optimizer result only — no data
  dict, no `due_in_hours`; the coordinator fixtures that DO record the data
  dict (`coord_*`) all have `dhw_legionella_enabled: true` (enumerated;
  `coord_grid_fee.json` shows the attribute `null` only because history is
  `None`). `legionella_off` is a plan scenario. The finder's recorded
  `env_drift.py --all` with M01 applied is rc=0, consistent.
- *"Both assertions running enabled"*: confirmed — `features.py:20197`
  (`_lg_blocked`) and `:20250` (`_lg_recent`) default `enabled=True`; the one
  disabled case (`_lg_off`, :20233) asserts only that no repair issue is
  raised, a path that re-guards itself.

**Vote: verify.** Severity medium — a wrong published value, but only when
the user has turned the feature off after history existed, and nothing
downstream acts on it (notices and planning both re-guard). The ladder's
"high = wrong published value" is arguable; I weaken to medium because the
wrong value is published for a feature the user explicitly disabled and no
money, comfort, or control path reads it. Class: bug.

---

## D3-S3 — tariff.py:507 the top-k clamp in `_smooth_topk_sum`

**Claim**: deleting `k = max(1, min(int(k), x.size))` (M22) is a no-op on the
one fixture that calls the function and equivalent through the only
production caller — yet was returned as a *bug* survivor.

**My numbers (executed, in-process A/B: the module exec'd twice from source,
clean vs mutant, identical inputs)**:

| path | cases | differ |
|---|---|---|
| `peak_cost(...)` randomized (n=4..40, k=1..11 incl. k > n_windows, dt ∈ {0.25,0.5,1,2}) | 300 | **0** |
| `_smooth_topk_sum` direct, the one fixture call (size 5, k=3) | 1 | 0 (59.985428470471184 both) |
| `_smooth_topk_sum` direct, k=0.5 (no reachable caller sends this) | 1 | differs (19.99997… vs 16.13648…) |

`tests/features.py` with M22 applied: rc 0, `ALL 2540 FEATURE CHECKS PASSED`.

**Why it is equivalent on every reachable path (reading + execution)**: the
only production caller pre-clamps the identical expression on the identical
array — `peak_cost` at `tariff.py:593` computes
`k = max(1, min(int(peaks_averaged), excess.size))` and passes that `k` with
`excess` as `values`; the deleted line inside `_smooth_topk_sum` would
recompute the same value on `x = np.asarray(excess)`. The one direct test
call (`features.py`, "smooth top-k on a k-wide tie recovers the billed sum")
passes k=3 on a 5-element array — in range. The line is live only for k no
reachable caller sends (fractional k; the k > size case converges to the
same bisection limit anyway).

**Attacks and outcomes**: equivalence attack *succeeds* — this is the
decisive one. Gate-mode attack moot (an equivalent mutant is invisible to
every mode). Reachability attack: `_smooth_topk_sum` is module-private with
exactly one call site (`tariff.py:600`). Provenance note: M22 has **no record
in `prescreen.json`** (the finder's run stopped at M06), so its "survivor"
label was never backed by the finder's harness; my runs supply both arms.

**Vote: weaken.** The survivor observation is true (features.py passes with
the mutant; nothing can kill an input-unreachable line), but the *bug*
classification is refuted: through the only caller and the only fixture the
mutant is bit-identical. This is redundant defensive hardening — hygiene
(dead code per COMMON.md's class list), severity low. The fix-side note a
judge may care about: if the line is kept as hardening, a one-line direct
test with k out of range would pin it; if not, the caller's identical clamp
at :593 already covers every reachable path.

---

## D3-S4 — optimizer.py:1549 CLAMP_DROP in `_anticipatory_weights`

**Claim (as judged by the finder)**: `end = min(i + lookahead, n_steps)` →
`end = (i + lookahead)` is equivalent because numpy slices clamp.

**My numbers (executed, in-process A/B as above)**: 200 randomized shapes
(n_steps 1..23, dt ∈ {0.25,0.5,1,2} so lookahead 32..4 — **every** case has
`i + lookahead > n_steps` for late i): **0/200 output arrays differ**.
`tests/features.py` with M32 applied: rc 0, `ALL 2540 FEATURE CHECKS PASSED`.

**Reading confirms the mechanism**: inside the loop, `end` is used only in
`if end <= i: continue` and as the upper bound of `solar_gains[i:end]` /
`heat_loss_factors[i:end]` (`optimizer.py:1550-1555`). Python slicing clamps
an over-long upper bound to `n_steps`, and the `end <= i` comparison is
unchanged whenever `lookahead >= 1` (both arms False) and identical whenever
`lookahead <= 0` (both arms equal). No test references
`_anticipatory_weights` by name (grep: only `optimizer.py` itself).

**Vote: verify** the equivalence claim as stated — hygiene, severity low,
class hygiene (the clamp is harmless self-documentation; the suite's
inability to kill it is not a gap because there is no behaviour to lose).

---

## D3-INST — closures.json's recorded seconds are accounting; golden.py and env_drift --all are one measurement

**Claims**: (a) `tests/closures.json` records 0.4 s for `tests/golden.py`,
which really costs ~201 s; (b) standalone `golden.py` *is*
`env_drift.py --all` (same two trees, same fixtures), so the README's
one-script list pays ~201 s + ~152 s for one answer.

**Verified by reading this round (no 200 s run taken, per instructions)**:

- `tests/derive_closures.sh:151-152` records the two differential guards
  with deliberately cheap arguments — `golden.py --only __no_such_scenario__`
  and `env_drift.py --cache-key <ref> --all` — and `tests/closure.py`'s
  merge (`:931`, `:958`) stores that invocation's wall time in the
  `recorded` block. The tree's `closures.json` says `golden.py 0.4 s`,
  `env_drift.py 0.4 s` (the FINDER table quotes 0.7 s for env_drift —
  trivially stale either way; the conclusion is identical).
- Nothing reads `recorded[*].seconds` for a decision: `closure.py` writes
  it; `entities.py` only builds `"recorded": {}` fixtures for closure.py's
  own unit tests; `run.sh` prints seconds it measures itself. Grep-verified
  across `tests/`, `tools/`, `.github/`.
- `golden.py` standalone: `resolve_mode` defaults to `drift`
  (`DEFAULT_MODE`, "Unset means drift"), `DEFAULT_REF="origin/main"`,
  `main()` → `run_drift(ref)` → `drift_command` =
  `[python, tests/env_drift.py, --all, ref]` — the same script, arguments
  and exit status the gate's drift lane uses. `run.sh:382` **skips**
  golden.py under `GOLDEN_MODE=drift`, and CI sets exactly that
  (`tests.yml:286,719`), so CI never pays twice; but
  `tests/README.md`'s "Running one script at a time" list includes both
  `python tests/golden.py` and `python tests/env_drift.py`, so a developer
  following it runs the ~200 s differential twice (and each adds a
  `git worktree add` inside the checkout — `env_drift.py:2006`).
- The wall numbers are the finder's, quoted from `prescreen.json`'s baseline
  block (golden.py 201.2 s; env_drift --all 152.0 s warm / 193.2 cold,
  taken at load1 4.2–6.8 on a shared box). **Marked for the judge**: the
  201.2 s / 152.0 s / 193.2 s re-measurement belongs in the quiet window; I
  did not run it. The 0.4 s recorded values and the control-flow facts above
  are mine, executed or grep-verified, and are load-independent.

**Vote: verify.** Severity low — an instrument/accounting defect (the only
per-script timing table in the tree understates the dearest script by ~500x
and double-charges a documented workflow), no gate behaviour changes. Class:
instrument finding per `tools/audit/README.md`'s rule; filing waits for the
judge.

---

## Method notes for the judge

1. `prescreen.json` is incomplete (M01–M06 of 36); the FINDER.md report
   carries no per-survivor section for S3/S4 at all. My targeted runs above
   are the only both-arms record for M22 and M32.
2. The D3 brief's step 3 ("the quiet window runs the full
   `GATE_SCOPE=full GOLDEN_MODE=drift` gate for the top six survivors") was
   never executed by the finder and could not be by me (gate lock belongs to
   the judge phase). If the judge runs it, S1 and S2 should still survive it:
   the full gate adds `stress.py`, `edge.py`, `backtest.py` and the strict
   golden compare; `edge.py`/`backtest.py` drive plans (no `due_in_hours`
   attribute, no dashed month range found by grep), and the committed golden
   fixtures contain no non-wrapping month range and no
   legionella-disabled-with-history coordinator capture. Predicted, not
   measured — the judge's run decides.
3. All four mutations were line-numbered edits matching `pool.json`'s
   `old` text exactly (asserted before writing); restoration verified by
   `git status --porcelain` after each (empty every time).
