# Round-9 pre-dedup pass

Input: 154 findings (122 batch1 + 25 leads + 2 D3-s2 + 5 D3-s3 catch-up), from
`origin/handoff/audit-r9-evidence`. This is a records-only pass — no harness
was run. It produces CANDIDATE clusters for the judge; nothing here is a
verdict, and no finding is discarded or merged by this pass.

## Clusters (6 total: 2 high, 2 medium, 2 low)

**High confidence (both would very likely collapse under judge.md step: canonical's perturbation moves the other's harness too)**

- **PD-01**: D11-s1-04 + D11-s2-03 — both key on
  `budget_raise_gate.py:approval`'s inability to tell tvofi's own GitHub review
  from a seat's on his behalf. Overlapping ranges, same reattribution
  perturbation on both harnesses. Canonical: D11-s1-04 (wider sample, 90
  reviews). Checked but NOT included: D11-s1-01, same file, different bug
  (stale approval survives a code-owned repush, not identity).
- **PD-02**: D5-s1-06 + D6-s2-05 — both say docs/configuration.md's
  simulate_plan field list names 11 fields against the registered schema's 16,
  and name the identical 5 missing wood_* fields. Canonical: D6-s2-05 (tighter
  claim); D5-s1-06's broader "no doc names them at all" framing folds in.

**Medium confidence (plausible shared root cause, needs one cross-harness run)**

- **PD-03**: D8-s1-03 + D12-s2-01 — the idle-action/power group the leads
  flagged (D8-s1-03, D12-s2-01..03, D8-s2-02). Only two of the five actually
  share a mechanism: get_current_action's on/off threshold disagreeing with
  the solver's continuous plan on a modulation-floor step, observed as a
  physical switch-OFF (D12-s2-01) and as a stale power reading on the "off"
  step (D8-s1-03). D12-s2-02 (wrong write domain), D12-s2-03 (p_norm
  divide-by-floor mislabelling), and D8-s2-02 (hvac_action vs boost) were
  checked and are distinct mechanisms — left as singletons.
- **PD-04**: D12-s1-01 + D12-s1-02 — the DHW-default group. Config-flow
  default leaves DHW planning on for a tankless install (s1-02); the solver
  then runs that DHW path off a never-advanced 55C default (s1-01). Plausible
  one root cause at two seams. No D4-s2 finding matches this theme after a
  keyword sweep of all 10 D4-s2 findings (tank/DHW/hot-water) — the verifier's
  "D4-s2" arm looks like a mis-tag, noted rather than forced into a cluster.

**Low confidence (same symbol only; likely distinct, given as a check not a merge)**

- **PD-05**: D1-s5-01 + D1-s5-51 — the pair the leads seat already called
  "different mechanisms" (age_of precedence bug vs. _age_gate's 60-min
  availability threshold on a report-on-change device). This pass agrees they
  are different functions on the same module and cannot rule out a shared
  cause without a harness run — carried forward as a candidate to confirm or
  refute, per the task, not asserted as a merge.
- **PD-06**: D8-s2-02 + D8-s2-03 — both are hvac_action state-consistency
  findings on climate.py, but one looks like a steady-state derivation bug
  (label from mode, not action) and the other a transient torn-write during a
  30-70s refresh window. Found during the general symbol sweep, not in the
  task's named list.

## Groups checked and NOT clustered (recurring theme, distinct mechanisms)

- **Stub-divergence (P11)**: D1-s1-51, D1-s1-52, D1-s2-71 (all class_guess
  P11) plus D14-s4-02 (P7) — each hits a different hastub component (Store
  codec, dt_util.now(), DataUpdateCoordinator, the replay lane's own frozen
  clock). Four independent instances of the same recurring class, not
  duplicates of one finding; this is root-cause.md territory (third-instance
  rule), not a dedup merge.
- **Currency/SEK**: D12-s3-81 (grid-fee validation bounds sized in SEK),
  D6-s1-81 (README's SEK-fallback doc claim is unreachable under HA core),
  D4-s2-02 (wood-price field's unit label ignores instance currency) — three
  different symbols, three different failure modes (validation range vs. doc
  claim vs. display label). Same theme, not the same finding.
- **D0 seed/optimality cluster**: D0-s1-01, D0-s2-01, D0-s2-02, D9-s1-02,
  D6-s2-04 all touch `_multi_start_minimize`/the seed apparatus but each
  states a distinct, separately-fixable claim (missing DHW anchor; loose
  ftol; seed set misses shoulder-price basins; excessive objective-eval
  count; a doc's "two starting points" undercount). Not merged.
- Also checked, distinct: D1-s4-01/D1-s4-03 (defrost store: bad-value
  acceptance vs. one-cell-voids-everything), D1-s5-04/D3-s3-01
  (`_parse_block`: off-grid-timestamp resolution collapse vs. a
  mutation-testing coverage gap), D4-s2-03/D4-s2-09 (different string-escaping
  bugs in the same flow), D7-s1-01/D7-s3-02 (different ways structure.py
  undercounts), D1-s2-04/D9-s2-02 (`_async_update_data`: swallowed failures
  vs. an uninstrumented perf blind spot).

## Conflict for the judge (not a merge)

- **D6-s1's non-finding** on the "0.5 K/week" curve-bias figure checked it as
  a config-DEFAULT equality (claims.py C27-C48: shipped default matches the
  docs, "22 equal" — a non-finding). **D6-s2-03** checked the same figure as a
  runtime BOUND on `CurveLearner.record_day` and measured 0.6 K actually
  accruing in 7 days. Different metric definitions (default-matches-doc vs.
  bound-is-respected-at-runtime) on the same documented number — per
  judge.md step 3, mark "not comparable" and re-measure `record_day`
  independently; do not average or drop either verdict.

## Counts

154 findings in, 6 candidate clusters (12 findings), 1 conflict pair, 142
singletons untouched.
