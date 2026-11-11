# D3 round 4 — verifier 0-2 report (panel D3-0)

- **Verifier**: 0-2 (verifier 2 of 3), refute-first.
- **Tree**: worktree `../audit-r4-verify-D3-2` at `0855277` (branch head of
  `claude/13-dimension-audit-920935`). The four production files carrying the
  mutants are **identical to the baseline `7dd68dd`** (verified:
  `git diff 7dd68dd HEAD --stat -- custom_components/` touches only
  `manifest.json` and the card JS), so the pool's line numbers are valid here.
- **Method**: targeted two-arm mutant runs in this worktree with my own driver
  (`tools/audit/round4/D3/verify_mutants_v2.py` — applies the pool's exact
  `new` line, runs the named scripts, restores, asserts SHA-256), plus an
  in-process equivalence probe
  (`tools/audit/round4/D3/verify_equiv_v2.py`). A mutant counts as killed by a
  script only if that script FAILS with the mutant and PASSES without it. I ran
  no `stress.py` and no `./tests/run.sh`; nothing here took the gate lock.
- **Contention**: nine-plus agents shared the box; `load1` quoted per run,
  3.3–18.4 over the window. Every number I rely on for a verdict is a count,
  an exit status, or a bit-identity boolean — contention-immune. Wall seconds
  are provisional and quoted, never load-bearing.
- **Harness contract notes**: threads pinned before numpy in both my scripts;
  runs from the repository root with `PYTHONPATH=tests/hastub`; no `cd`; my
  scripts write nothing outside their own directory and `/tmp`.

## Method attacks (before the per-finding votes)

1. **The finder's prescreen never executed S3/S4.** `prescreen.json` carries
   records for M01–M06 only; M22 and M32 were never run by the seat (its JSON
   was never returned). The S3/S4 "survivor" claims were unexecuted
   assertions. I executed both myself (below). This is recorded as a method
   defect in the finder's report, not as evidence against the findings.
2. **Pool determinism**: re-ran `mutant_pool_r4.py --n 36` at the default seed;
   the sampled 36 mutants (id/file/line/op/old/new) are identical to the
   committed `pool.json`; the only diff is a `"func"` annotation the committed
   file carries and the generator does not emit. `RESULT mutants=36`,
   `candidate_lines=9069`, 23 modules with candidates (pool says allocation
   drew from 12).
3. **Kill-rule oracle control**: recorded-killed mutant M02 (`inputs.py:438`
   GUARD_OFF, finder: killed by `entities.py`) through my own driver:
   `entities.py` rc=1, `5 of 1352 ENTITY CHECKS FAILED` with the mutant;
   rc=0 without (clean arm). The oracle fires; non-detections are meaningful.
4. **CI-mode attack**: for every finding mutant I ran
   `tests/env_drift.py --all 7dd68dd…` as the mutant's second arm (clean arm
   rc=0, 232.9 s at load1 6.96, provisional). `env_drift.py`'s branch capture
   is always recomputed (its own header, "The baseline cache"), so the
   working-tree mutant is visible to it; the baseline side comes from the
   shared warm cache. All four mutant arms returned rc=0 — CI's actual mode
   catches none of them. None of S1–S4 is an artefact of the "wrong gate
   mode" kind.
5. **FakeHass/reachability**: S1's mutant sits in pure config parsing
   (`config_flow.py:884` validates user input with the same function;
   `coordinator.py:7234` consumes it for `peak_tariff_months`); S2's state
   (feature disabled + `last_cycle` persisted) is restored across restarts by
   `LegionellaGuard.async_load`. Both reachable in real HA; neither depends on
   a stub artefact.

## D3-S1 — grid_fee.py:106 `parse_month_range` (M06, GUARD_OFF) — vote: verify

**Claim**: a non-wrapping range like Mar-Sep becomes year-round; the only
range assertion uses the wrapping case.

**My numbers** (both arms executed in this tree):

| arm | features.py | entities.py | config_flow_steps.py | env_drift --all |
|---|---|---|---|---|
| clean | rc=0 (99.1 s) | rc=0 (32.3 s) | rc=0 (0.7 s) | rc=0 (232.9 s) |
| M06 applied | rc=0 (95.3 s, load1 5.4) | rc=0 (24.4 s) | rc=0 (0.7 s) | rc=0 (79.0 s, load1 3.3) |

Survived everything I ran, matching the finder's prescreen record (all 11
fast drivers plus `env_drift --all`, rc=0).

**Killability (my probe, in-process mutant variant of the pool's exact line)**:
every non-wrapping range returns all 12 months — `Mar-Sep` {3..9} →
{1..12}, `Okt-Dec` {10..12} → {1..12}, `Jun-Aug` → {1..12}, `Jan-Feb` →
{1..12}; the wrapping case `Nov-Mar` {1,2,3,11,12} and single `Jul` are
unchanged. The mutant is **not equivalent**: one assertion
(`parse_month_range("Mar-Sep") == frozenset(range(3, 10))`) kills it.

**Why nothing catches it** (code reading, all greps over `tests/*.py`):
the only range assertions are `features.py:7991`
(`parse_rules("Nov-Mar Mon-Fri 06:00-22:00 = 0.25, Jul = 0.10")`) and
`features.py:8024` (`2 in parse_month_range("Nov-Mar") and 6 not in …`) —
both wrapping; `is_valid_spec("Okt-Dec Lör-Sön = 0.1")` (features.py:8020)
only checks parseability, which the mutant preserves; `entities.py:3863`'s DSO
catalog round-trip compares the spec **string**, not the parsed set, and the
catalog's only month range is the wrapping `Nov-Mar`
(grid_fee.py:391-392); golden/env_drift's `coord_grid_fee` fixture uses
`"Mon-Fri 06:00-22:00 = 0.25"` — no month token at all.

**Consequence**: non-wrapping ranges are valid user input, and the same parser
decides `peak_tariff_months` (coordinator.py:7234) — a seasonal fee or
capacity tariff silently applies year-round. Money, silently. Severity as
filed (bug, weight-5 module) is earned.

**Metric**: two-arm kill status of M06 over {features, entities,
config_flow_steps, env_drift --all} — killed iff some driver fails with the
mutant and passes without.

## D3-S2 — legionella.py:521 `due_in_hours` disabled guard (M01, GUARD_OFF) — vote: verify

**Claim**: the disabled-feature guard survives, with both existing assertions
running enabled.

**My numbers** (both arms executed):

| arm | features.py | entities.py | validate.py | manual_plan.py | env_drift --all |
|---|---|---|---|---|---|
| clean | rc=0 | rc=0 | rc=0 (23.8 s) | rc=0 (4.8 s) | rc=0 |
| M01 applied | rc=0 (98.7 s, load1 14.7) | rc=0 (36.2 s) | rc=0 (30.2 s) | rc=0 (6.8 s) | rc=0 (155.7 s, load1 10.6) |

Matches the finder's prescreen record exactly (survived everything).

**Killability (my probe, file mutant + restore, git-verified)**: in the state
(feature disabled + `last_cycle` 20 days ago) — built the way
`features.py:_lg_coord(enabled=False)` builds it — the clean tree returns
`None` and the mutant returns **-312.0**. Not equivalent; one assertion
(`due_in_hours() is None` in that state) kills it.

**Why nothing catches it**: the two direct assertions
(`features.py:20197/20198`, `:20250`) run with the feature enabled
(`_lg_coord` default `enabled=True`). The disabled coordinators that do exist
with a recorded history (`_lg_off`, features.py:~20225) feed only
`check_mode_block`, which carries its **own**
`bool(params.dhw_legionella_enabled)` condition (legionella.py:558-563) and so
cannot see the value change. `entities.py:6443/6456` reference
`dhw_legionella_due_in_hours` only as attribute-name presence in frozensets.
The golden/env_drift disabled scenario (`golden.py:405`) has no recorded
cycle, so `hours_since()` is None and the mutant changes nothing there —
confirmed by my env_drift arm.

**Consequence**: `coordinator.py:6426` publishes
`self._legionella.due_in_hours()` straight into the data dict → the sensor
attributes (`sensor.py:1183, 1230`). A user who disables disinfection after a
recorded cycle sees a live countdown/overdue number on a disabled feature.
The planner and the repair-notice path are unaffected (own guards). Bounded,
user-visible, wrong published value — I would keep the bug class but at the
minor end (published value only, no money/safety effect).

**Metric**: two-arm kill status of M01 over {features, entities, validate,
manual_plan, env_drift --all}, plus the clean-vs-mutant return value of
`due_in_hours()` in the disabled-with-history state.

## D3-S3 — tariff.py:507 top-k clamp (M22, STMT_DEL) — vote: refute

**Claim as filed**: bug, survivor — "a no-op on the one fixture that calls it;
equivalent through the only production caller".

**Method note first**: the finder never ran M22 (`prescreen.json` stops at
M06). I executed it:

| arm | features.py | optimality.py | env_drift --all |
|---|---|---|---|
| clean | rc=0 | rc=0 (59.8 s) | rc=0 |
| M22 applied | rc=0 (89.2 s) | rc=0 (43.7 s) | rc=0 (104.8 s, load1 6.1) |

It does survive. **But the survival is vacuous — the mutant is exactly
equivalent for every input any caller can produce:**

- **My equivalence probe** (`verify_equiv_v2.py`): original vs mutant
  `_smooth_topk_sum` over **1251 adversarial cases** (sizes 1,2,3,5,24,96 ×
  separated/tied/one-hot shapes × every integer k from 1 to 3·size):
  `m22_max_abs_diff_int_k = 0.000e+00` — **bit-identical**, not merely within
  tolerance. For k > size both versions bisect to the floor of the search
  interval and return the same float; for k ≤ size the clamp is the identity.
  The only divergent input is fractional 0 < k < 1
  (`m22_fractional_k_diff = 1.497` at k=0.5), which no caller can pass.
- **Through production**: `_smooth_topk_sum`'s only production caller is
  `peak_cost`, which clamps k itself at `tariff.py:593`
  (`k = max(1, min(int(peaks_averaged), excess.size))`) **before** the call at
  `:601` — line 507 is dead code on that path. Both optimizer call sites
  (`optimizer.py:2109`, `:3637`) pass `cfg.peak_count`, an int from config
  (`coordinator.py:7197` `peaks_averaged=int(…)`).
- **Through the tests**: the only direct call is `features.py:1277`
  (`_smooth_topk_sum(_tie_bill, 3, 0.05)`, 5 elements, k=3 — clamp is
  identity); every `peak_cost` call in features.py passes k=3 with 8/24/96
  elements.

So no black-box test through any reachable input — existing or writable —
can kill M22, except a direct fractional-k call to a private function. A
survivor that cannot be killed is not evidence of a suite gap. The finder's
own claim text concedes production equivalence; the "bug, survivor"
classification does not follow from it. This mutant belongs in the same class
as S4 (hygiene, judged equivalent) — if the register reclassifies it there,
the finding becomes true as stated; as a bug/survivor I refute it.

**Metric**: max |orig − mutant| of `_smooth_topk_sum` over 1251 integer-k
adversarial cases (0.000e+00), plus M22's two-arm kill status.

## D3-S4 — optimizer.py:1549 CLAMP_DROP (M32) — vote: verify

**Claim**: hygiene, judged equivalent — "numpy slices clamp, so no value
moves".

**My numbers**: fast arms features.py rc=0 (74.5 s), optimality.py rc=0
(37.3 s); env_drift --all rc=0 (168.2 s, load1 17.6) — survives, consistent
with equivalence (and required by it).

**Equivalence proof (my probe)**: `_anticipatory_weights` original vs mutant
(the pool's exact `new` line) — weights **bit-identical**
(`np.array_equal`, `m32_weights_identical = True`) across 7 shapes:
(n_steps, dt) ∈ {(10,0.25), (5,0.25), (96,0.25), (24,1.0), (8,2.0), (6,8.0),
(4,16.0)} — i.e. lookahead=32 far past a 10-step horizon, and the lookahead=0
edge. Reason: `end = (i + lookahead)` then `solar_gains[i:end]` /
`heat_loss_factors[i:end]` — Python/numpy slice bounds clamp to the array
length, and `if end <= i: continue` fires identically in both versions
(lookahead ≥ 0 ⇒ end ≥ i, with equality only at lookahead=0, same both ways).
No value moves; the finding's equivalence judgement is correct. Hygiene
severity as filed.

**Metric**: bit-identity of `_anticipatory_weights` output, original vs
mutant, across 7 (n_steps, dt) shapes including lookahead ≫ n_steps.

## D3-INST — closures.json `recorded` seconds; golden.py ≡ env_drift --all — vote: verify

**Sub-claim 1 — the recorded seconds are accounting, not behaviour.**
Verified by reading the writer and the design, and by executing the exact stub
invocations:

- `tests/derive_closures.sh` (header, lines 25-33) documents that the two
  differential guards are recorded with cheap arguments on purpose:
  `golden.py --only __no_such_scenario__`, `env_drift.py --cache-key <ref>
  --all` — "Running their full comparison here would take an hour and teach
  the closure nothing".
- My own timings of those exact stubs (safe, sub-second):
  `golden.py --only __no_such_scenario__` = **0.615 s** wall;
  `env_drift.py --cache-key 7dd68dd… --all` = **0.698 s** — reproducing the
  sub-second `recorded` values (my tree's `closures.json`: golden 0.4,
  env_drift 0.4; the finder's tree recorded 0.4/0.7 — same class).
- Against that, the real differential run on this box cost **232.9 s** in my
  own clean arm (load1 6.96, warm shared cache, provisional), consistent with
  the finder's 152.0 s warm / 193.2 s cold and ~3 orders of magnitude above
  the recorded number. I did **not** re-run the 201.2 s `golden.py`
  measurement — that re-measurement is for the judge on the quiet box.
- Consumers: `tests/closure.py` writes the block (:898, :930, :958); nothing
  reads `recorded[*].seconds` for a decision (run.sh's `seconds` is its own
  lane table; entities.py only constructs empty `recorded` dicts while testing
  closure.py). Accounting, exactly as the finding says.

**Sub-claim 2 — `python3 tests/golden.py` and `env_drift.py --all` are the
same measurement.** Verified by code: `golden.py:86-87`
(`DEFAULT_MODE = "drift"`, `DEFAULT_REF = "origin/main"`), `resolve_mode`
("Unset means `drift` — the CI comparison"), and `run_drift(ref)` which
subprocess-runs `[sys.executable, "tests/env_drift.py", "--all", ref]` —
"Not a reimplementation: the same script, the same arguments, the same exit
status, so a direct run and the gate lane answer the same question."
`tests/run.sh:382` skips golden.py whenever `GOLDEN_MODE=drift`, so CI never
pays twice; but `tests/README.md:352` lists `python tests/golden.py` in its
run-one-script guidance with the default drift mode, so a developer following
it pays the finder's 201.2 s + 152.0 s for one answer (finder's numbers,
provisional, judge to re-take).

**Severity**: hygiene/minor as an instrument finding (no decision consumes
the number; `derive_closures.sh`'s header and `tests/README.md:159` do
disclose the cheap-argument choice — but `closures.json`'s own `_comment`
does not, and it is the only per-script timing table in the tree).

**Metric**: wall seconds of the exact stub invocation `derive_closures.sh`
records vs the `recorded` seconds, plus code-read identity of golden.py's
default invocation to `env_drift.py --all`.

## Summary of executed RESULT lines

```
clean arms : features rc=0 99.1s | entities rc=0 32.3s | optimality rc=0 59.8s |
             validate rc=0 23.8s | config_flow_steps rc=0 0.7s | manual_plan rc=0 4.8s |
             env_drift --all 7dd68dd rc=0 232.9s (load1 6.96)
M06 arm    : features rc=0 | entities rc=0 | config_flow_steps rc=0 | env_drift rc=0 79.0s   -> SURVIVED
M01 arm    : features rc=0 | entities rc=0 | validate rc=0 | manual_plan rc=0 | env_drift rc=0 155.7s -> SURVIVED
M22 arm    : features rc=0 | optimality rc=0 | env_drift rc=0 104.8s                          -> SURVIVED (equivalent)
M32 arm    : features rc=0 | optimality rc=0 | env_drift rc=0 168.2s                          -> SURVIVED (equivalent)
M02 control: entities rc=1, 5 of 1352 FAILED with mutant; rc=0 clean                           -> ORACLE FIRES
probes     : m22_max_abs_diff_int_k=0.000e+00 (1251 cases) | m22_fractional_k_diff=1.497 |
             m32_weights_identical=True (7 shapes) |
             m06 every non-wrapping range -> 12 months; wrapping/single unchanged |
             m01 disabled+history: clean None, mutant -312.0
stubs      : golden --only __no_such_scenario__ 0.615s | env_drift --cache-key --all 0.698s
```

For the judge: the 201.2 s `golden.py` standalone measurement and the
cold-cache env_drift number remain to be re-taken on the quiet box; every
verdict above rests on counts, exit statuses and bit-identity probes, not on
wall time.
