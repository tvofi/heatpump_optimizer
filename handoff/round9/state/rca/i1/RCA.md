# R9 RCA — class I1 (N=11): a mutation kill miscounted, or a guard whose deletion leaves the gate green

Seat: round-9 RCA, beside F9.1; barrier lands in F10.3 (tvofi-gated, `tests/mutation_table.py` is code-owned).
Baseline `1936d5ca` (v6.7.1); prototype cut from origin/main `db878b29`.
Prototype and evidence: branch `handoff/r9-rca-i1` @ `8eda51a2`, `tests/mutation_table.py` and `tools/audit/round9/rca/i1/`.
Every figure below comes from a script in that directory. Its `.out` file sits beside it, and it runs with
`PYTHONPATH=tests/hastub` from the tree named. CPU seconds were taken on a shared 4-core box at load1 of about 10–12, so they are provisional.

## Root cause

### Cause, reproduced at 1936d5ca

The round-9 findings attribute the class to two gaps: an inventory the ratchet cannot see (D14-s5-02) and a gate that runs on a
naive clock at `TZ=UTC`. The reproduction shows neither was the main cause of the round-9 instances.

**1. The ratchet already inventoried every round-9 production seam, and none of them was pinned.** `seam_status.py` (at baseline)
checks each production seam of the 10 D3 findings (13 seams) against `mutation_table.inventory()` and the ledger:

- 13 of 13 are inventoried. The operators are GUARD_OFF, CLAMP_DROP or BOOLOP.
- 12 of 13 are unpinned, and all 12 were born before the ratchet merged (#1426, `43dd4c34`, 2026-09-23).
- The 13th, `coordinator.py:1371` (D3-s1-01), is born after the ratchet and is "pinned". Its BOOLOP and RETURN_DEL sites carry
  `killed_by`, but the finding's mutant (`-5.0 <= value` → `<`) is a comparison bound, and no operator generates one. The ledger
  therefore marks the line accounted for while its bound is not.

So widening `candidates()` (S3's barrier 1) would have changed the outcome for **0 of the 10** D3 production findings.

**2. The unpinned stock is grandfathered, and nothing draws it down.** `backlog_age.py` at baseline: 3677 of 3951 inventory sites are
unpinned, and 3641 of those were born before the ratchet. The ratchet's docstring defers the draw-down to a job that was never built:
*"recording the sampled run's kills into the ledger (`killed_by`) is the nightly burn-in's follow-up, not this enforcement."*
`mutation-nightly` in `tests.yml` drives `--scope full --max 40` and records nothing. Each audit round's D3 seats sample this stock,
and 93% of it (3677/3951) is unpinned, so the class recurs by construction.

**3. The ratchet counts; it does not account.** `ratchet_refusal(base_count, unpinned)` refuses only when the total grows. A diff that
adds an unpinned guard and deletes, edits or pins any other unpinned site nets to zero and passes. `merge_trade.py` replays the 10
PR merges that carry the 36 post-ratchet unpinned lines, each merge with its own `mutation_table.py` and ledger:

- The merges admitted **28 content-new unpinned sites** (identity = file, operator, stripped line text).
- **0 were refused**, because every merge's net count fell or held. #1569 (`e0b83bbd`) brought 9 in and took 9 out, delta 0.

The docstring's claim, *"a diff that adds a site without one raises the count above the same count at the ratchet base … and is
refused"*, is false whenever the diff also removes one.

**4. The inventory shape gap, D14-s5-02, is real but secondary.** At origin/main, 528 of 2313 guard seams are invisible to the
ratchet. It accounts for 2 of the 6 ledger R5 instances (#1312 ternary, #1316 `np.clip`, per the finding's `--history`) and for
0 of round 9's production instances.

**Class search: what the same cause reaches beyond the sweep.**
- *Timezone guards.* There are 17 `tzinfo is None` guards in the package. All 17 are inventoried GUARD_OFF sites and all 17 are
  unpinned; round 9 found 3 of them. The sweep's naive-clock mechanism is one reason these guards are unkillable. The count ratchet
  is why that stays silent.
- *Unmutated comparisons.* The package has 860 ordering comparisons, and no operator mutates any of them. D3-s1-01 is one.
- *Shapes the prototype still misses.* It leaves 101 multi-line `if` tests and 99 multi-line clamp calls uninventoried, and
  conditional expressions (TERN) have no operator (228 of 299 uncovered).
- *Test-side verdict code (D7-s1-02).* This lies outside the inventory by design, since the inventory is production-only. It is
  F10.3's finding and not this barrier.

### Process state: (c) — followed, and it did not produce the intended result

The class's countermeasure is the deterministic inventory plus the unpinned-site ratchet (#1426, extended by #1561, #1577, #1594 and
#1599). The ledger's I1 row still says `"barrier": null`. The process was followed: every one of the 10 replayed merges ran the
mutation lane. It was obeyed and did not produce the result it states, *"The ratchet is what stops a guard from leaving the tree
unaccounted for"*:

- **(i)** It compares totals, so 28 new unpinned sites entered across 10 merges with 0 refusals.
- **(ii)** Its design assumed a burn-in that does not exist, so the 3641 pre-ratchet sites, where all 12 unpinned round-9 seams
  live, have no path to a disposition.

This is not (b): no seat skipped the lane. A firmer instruction ("pin your guards") would repeat the shape
`comment-readback.md` measured at 0 of 3. The countermeasure changes the rule the tool enforces.

### S3's two proposals, evaluated

- **(1) Widen `candidates()`.** Kept, as half of the barrier; it does not bite alone.
  - It would have caught 0 of 10 round-9 D3 production findings.
  - Under the count rule, a newly visible guard is still tradeable.
  - Measured on the prototype, which widens the single-line shapes (any one-line `if`/`elif` test with an `else` or a trailing
    comment, numpy/math clamps, and clamps with three or more arguments):
    - inventory grows 3951 → 4325 sites, and every site main lists stays byte-identical, so no ledger anchor moves;
    - uncovered seams fall 528 → 371 (EXIT 52→46, CLAMP 246→97, TERN 230→228);
    - 0 new mutants are unparseable (2 CONST mutants were already unparseable on main, and still are).
  - In the 10-merge replay, the widened inventory alone raised the count on 2 merges (`e0b83bbd` +1, `10bb8bb4` +4) that the old
    one passed.
- **(2) A closure-scoped non-UTC lane.** Refused as specified.
  - The `HASTUB_TZ=Europe/Stockholm` suite already runs inside every `tests/features.py` run (`tests/features.py:19331`,
    `dst_checks.py` subprocess), and `features.py` is in `coordinator.py`'s closure. A lane re-running it adds no coverage.
  - What is missing is checks that reach the seams:
    - `coordinator.py:8112`/`:8384` are live only when `dt_util.now()` is aware. Home Assistant's always is; the stub's default is
      naive, which is P11's instance `tests/hastub/homeassistant/util/dt.py` and P11's barrier.
    - `open_meteo.py:209` depends on the **process** zone, which `HASTUB_TZ` does not set. A pin in `tests/open_meteo.py` that
      switches `TZ` in-process kills it, at no lane cost (F1.1).
  - Under the per-site rule, a new timezone guard no driver can kill must be recorded as a `gap` or `equivalent` triage, so it can
    no longer go green silently.

### Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, per mutation-lane run and per release cycle.

**Standing cost.**
- Per-site rule: one extra `base_unpinned_sites` call plus the multiset difference, **+0.02 s CPU** per run.
- Widened inventory: the prototype also replaces `ast.get_source_segment` in the clamp operator with a line slice. That call
  re-split the whole file per clamp and took 94 of 98 profiled inventory seconds. `inventory()` goes **21.8 s → 1.2–1.3 s CPU**
  (two runs each) while listing 374 more sites. **Net standing CPU: about −20 s per run.**
- The real recurring cost is refusals. Replaying the 10 merges under the prototype:
  - 9 of 10 would have been refused, against 0 on main, with 45 added sites in total (4.5 per merge).
  - Each refusal goes to the existing `mutation-autofix` (`--pin-killed`, CI-only, the step's `timeout-minutes: 60`).
  - A seat is needed only for a survivor. Among the ledger's recorded dispositions, 30 of 273 are triage verdicts (13 `gap`,
    17 `equivalent`), so about 11% of driven sites need a human verdict. At 4.5 added sites per merge, that is roughly 0.5 per merge.

**Defect side.**
- `P(recurrence)`: I1 appears in every round the ledger covers (rounds 1–7, 49 instances, `tools/audit/bugclasses.json`) and again
  in round 9 (11). That is 8 of 8 recorded rounds, so P ≈ 1 per round.
- `cost(defect)`, lower bound: the D3 seat measured 660 s wall (provisional) to drive one coordinator mutant through its closure
  (`round9/D3/s1/REPORT.md` D3.M5). That is only the finding step, before three verifiers, a judge, a fixer and a reviewer, and
  round 9's I1 fix set is 4 PRs (F9.1, F9.2, F1.1 part, F10.3).
- 11 × 660 s = **≥ 7260 s** a round against about 0 standing seconds.

**Verdict.** Build it. The disposition then moves to the seat that wrote the guard, the cheapest point, instead of costing a finder
round later.

### The barrier

**Refuse any unpinned site the diff added, by content, not only a grown total; and widen the inventory to every single-line guard
and clamp shape.** Prototype on `handoff/r9-rca-i1`, `tests/mutation_table.py` (+66/−10):

- `added_unpinned(unpinned, base)` is a multiset difference on (file, operator, stripped `old`). A site that moved, was re-indented
  or had its def renamed is the base's. An edited or new guard is not.
- `main()` refuses when `ratchet_refusal(...) == 1 or added`. It prints `ADDED UNPINNED …` rows and keeps the
  `MUTATION TABLE REFUSED -- N unpinned site(s) against` line, so `mutation-autofix`'s trigger (`tests.yml`) and entities.py's
  string pins still match.
- GUARD_OFF replaces the test in place on any one-line `if`/`elif`, keeping the header's tail. CLAMP_DROP covers numpy/math clamps
  and clamps with three or more arguments. Segments are taken by line slice.

Evidence (`per_site_ratchet_demo.py`, `demo_seams.out` / `demo_history.out`). Each case is a synthetic diff that re-introduces one
round-9 seam and, in the same diff, removes another unpinned guard in that file: #1569's shape.

| | main (old tool, count rule) | prototype (per-site) |
|---|---|---|
| each of 12 seams (11 D3 + D14-s5-02's `np.clip`) re-introduced **with** a trade | 0 of 12 refused | **12 of 12 refused** |
| the same seams re-introduced **without** a trade | 11 of 12 refused (not the `np.clip`: invisible) | 12 of 12 |
| fixed: the added sites carry a `killed_by` pin | — | **0 of 12 refused** |
| null: the same file at both ends | — | **0 of 12 refused, 0 added** |
| 10 real post-ratchet merges | 0 of 10 refused (`merge_trade.out`) | 9 of 10 (45 added); `97dc04f2`, a pure move, 0 added |

It cannot go green by skipping. An unreadable base already refuses at `base_count is None` before the per-site check runs. Nothing
else in `main()` bypasses the check, except `--pin-killed`, which is the repair mode.

The structural ratchet passes on the prototype (`tests/structure.py`: `STRUCTURE RATCHET PASSED`, 3.0 s), and no structure metric
covers `tests/`. The prototype does not raise `mutation_budgets.json`: counts are derived at both ends and never committed, and the
widening adds the same 374 sites at base and head.

**Not eliminated, and tvofi's to decide:**
- **(a) The 3641-site pre-ratchet stock**, which is where every unpinned round-9 seam lives. The per-site rule draws it down only as
  code is touched. Eliminating it means recording the nightly's kills. That costs zero extra CI minutes, since it already drives 40
  a night and discards them, but it needs a writer that pushes ledger rows to `main`, which is an identity/permission decision
  under 0011. Survivors, about 11%, still need human verdicts. At 40 a night, the stock is ≥ 91 nights.
- **(b) A comparison-bound operator.** 860 comparisons. It needs its own cost measurement, because each new comparison in a PR
  would then owe a pin.
- **(c) Multi-line tests, clamps and TERN.** A `new` spanning several lines is a design change to the single-line mutant format.

## Plan fold

- **Landing PR:** F10.3, as planned. No change to the PR set or the `after` edges; F10.3 still waits on F9.2.
- **Files:**
  - `tests/mutation_table.py` is **code-owned** (@tvofi).
  - `tests/entities.py` is not code-owned. It owes a behavioural pin of `added_unpinned`: trade refused, move not refused, pinned
    passes. It also owes a pin that `main()` wires `added_unpinned(`, beside its existing string pins at `tests/entities.py:24520`.
  - No policy file.
- **Line estimate:** 0 production lines; about 76 changed test/tooling lines in `mutation_table.py` (prototype +66/−10); about
  40 test lines in `entities.py`.
- **Budgets:** no `*_budgets.json` raise needed.
- **Carries (finding-propagation.md), for the orchestrator to write into the briefs; this seat edits none:**
  - **F1.1:** the non-UTC lane is refused. `open_meteo.py:209` is killed by a `tests/open_meteo.py` pin that sets the process `TZ`
    in-process, since `HASTUB_TZ` does not reach it. `coordinator.py:8112`/`:8384` need a `dst_checks.py` arm with a naive
    stored stamp under the aware `HASTUB_TZ` clock.
  - **P11 RCA / F10.3:** an aware-by-default stub `dt_util.now()` is what makes the coordinator timezone guards live in every
    driver.
  - **F9.1/F9.2 fixers:** their pins must land as `killed_by` rows. Once F10.3 merges, a pin PR that edits a guard line without one
    is refused.
- **Ordering hazard:** after F10.3, every later round-9 PR that adds or edits a guard (F10.4, F11.x) is refused until
  `mutation-autofix` pins it or a seat triages it. Pure deletions add nothing.
