# Round 9 fix plan (step E2)

Final plan for tvofi, 2026-09-26. Drafted by the E2 fix-plan designer seat (strongest model) and
finished once the seven Phase D sweeps (S1–S7) had landed; section 9 lists what the sweeps changed. It
is built from the judge's final class list (CLASSES-DRAFT.json at `bad458a3`, verdicts at `2f97b0a`), DEDUP.md, JUDGE.md/json,
RESUME.md ("PHASE F SHAPE", "FIX-PLAN CARRY-INS", "PR COUNT TARGET", "MODEL ROUTING", "NO HEAVY D3 RE-RUNS")
PLAN.md sections 7 and 8, and the sweep outputs `S1.json`–`S7.json` with their `SWEEP.md` files. Main at plan time: `db878b29` (after #1643). Baseline of every finding:
`1936d5ca` (v6.7.1).

Companion files, all generated from one data file so they cannot disagree:

- `handoff/round9/fix/F1.md` … `F11.md` — one fixer brief per lane (one cloud thread each).
- `.claude/workflows/wave-r9-groups.json` — the roster draft, one entry per PR, each with a `resume`
  field. `brief_lint.mjs` on it, run against an origin/main tree: exit 0, `TOTAL: 0 error(s)`.
- The tables at the end of this file (PR table, finding→PR, class→PR, owned files, merge queue).

## 1. The numbers

- **41 PRs in 11 lanes**, covering all 145 surviving findings (148 canonical less 3 refuted; the 7 merged
  ids travel with their canonical) and all 9 sweep-confirmed instances beyond them (section 9).
  One over tvofi's 15–40 range; the reason is the next bullet but one.
- **Why not fewer.** `fixer.md` caps a PR at five findings and about 400 production lines, and PLAN
  §8.2 keeps that cap; a sweep instance counts toward it like a finding. So 145 findings need at least
  29 PRs. The rest come from three constraints: lanes own disjoint files, so a PR packs findings from
  one lane's files only and a lane's last PR is often part-full; 9 PRs need tvofi and are kept apart so
  nothing else waits on them; and one PR (F6.3) is a class barrier alone, because P9's barrier lives in
  `tests/card_browser.mjs`, which is code-owned.
- **Why 41 and not 40.** S7 raised "persisted future instant trusted without bound" from 2 to 7, so it
  owes an RCA seat and a barrier. Four of its five new instances are in `coordinator.py`, which only F1
  owns, and the instruction is that a class's sweep instances travel with its barrier PR where the lane
  allows. No F1 PR has more than two free slots, and one of the two
  roomiest, F1.10, is tvofi-gated, which would make the instances wait on tvofi. So the four
  instances and the barrier are a new PR, **F1.9** (the old F1.9 is now F1.10). Keeping 40 would mean
  merging two unrelated card PRs (F6.2 with F6.4), which delays the keyboard fix and the #1643 mutant pins
  behind F1.8 for no gain; I did not.
- **Why not more.** Classes are merged into one PR wherever they share a file set and fit the cap; a
  class over the cap (P2 with 27, I5 with 19, I1 with 11, P1 with 11) is split into instance PRs by
  subsystem with its barrier in the last one (PLAN §8.2). The other four sweep instances fit PRs that
  already held their class: P1's two ride the P1 barrier PR F1.6 (borrowing `comfort_learning.py`), P9's
  joins F6.1, the recompute class's joins F2.2, and the future-instant class's pump-arbiter seam joins
  F3.2; each of those PRs is now exactly at five.

## 2. How the PRs were clustered

tvofi's order (13:04Z): class first, then shared file set, then fixer skill; owner-gated work in its
own PRs.

1. **Class first.** A class that fits one PR is one PR with its barrier (P5 in F4.2; the CPU-gate
   class in F10.2; the restart class in F1.4). A class whose instances sit in several lanes takes its
   barrier in a PR that waits on all of them (I5 in F10.4, P11 in F10.3, I3 in F11.3, I4 in F11.4).
2. **Then file set.** The package has hub files that many classes touch: `coordinator.py`,
   `optimizer.py`, `config_flow.py` with the three translation files, the card, `sensor.py`. A class
   like P2 spans all of them, so one class PR would collide with every other lane. Instead **each file
   is owned by exactly one lane**, and each lane's PRs group that lane's findings by class where they
   can. This is what makes Phase F's "parallel groups have disjoint file sets" true.
3. **Borrowing, not sharing.** 12 PRs must edit a file another lane owns (a fix-together sibling
   pair across hubs, a cross-cutting finding, a barrier that reads every instance). Each lists the file
   under **Borrows** and carries an `after` edge on the owning lane's last PR on that file. The generator
   checks every pair of PRs that could be open at the same time and refuses the plan if any two touch the
   same file; it reports none. So, as declared, no two open branches ever edit one file, which is the property the
   disjointness rule protects, and conflicts are left only in the shared ledgers PLAN §9.4 already
   handles (`tests/features.py`, `tests/entities.py` by class-named sorted blocks; `closures.json` and
   `structure_budgets.json` re-recorded once at the hand-off; delivery rows one file per PR).
4. **Then skill.** Lanes F5 (config flow and translated text), F8 (docs) and F9 (test pins) run on
   sonnet; everything else on the strongest model (tvofi 12:21Z).

The four fix-together sibling pairs DEDUP.md names each land in one PR: D12-s2-01 with D8-s1-03 in
**F2.4** (D12-s2-01 first, at both seams; D8-s1-03 then re-measures); D12-s1-01 with D12-s1-02 (merged
into D12-s3-01) in **F1.2**; D1-s5-01 with D1-s5-51 in **F4.1**; D8-s2-02 with D8-s2-03 in **F7.1**.
DEDUP's other "fix together" notes are honoured too (D1-s2-51/D1-s2-91 in F1.3; D7-s1-71/D5-s2-03 in
F2.3; D5-s1-01/D6-s2-01/D6-s2-02 in F8.1; D5-s1-05/D6-s1-02 in F8.2; the plausibility trio D1-s5-52 →
D1-s2-02, D1-s1-03 share F4.1's window and land in F1.6).

**Three findings are split across two PRs**, because their seams sit in two lanes' files; each closes
when its last PR merges, and the first PR's body says "leaves #N open":

- D14-s4-01 (high, P7): its `get_current_action` seam in F2.1 (first, and short), everything else plus
  the DST tracer barrier in F1.1, which waits on F2.1.
- D5-s1-02: the quick-setup text in `en.json`/`sv.json` (an L2 extra seam) in F5.1, `docs/setup.md` in F8.3.
- D6-s2-03: the figure in `strings.json` (an L2 extra seam) in F5.1, the docs in F8.3.

## 3. Phase F shape (tvofi "Yes", 12:11Z)

- **Mac fix orchestrator** keeps PR authoring (`hpo-author` via `app_push.sh`), approvals
  (`hpo-approver`; tvofi's own review for code-owned and policy paths), merges one at a time with
  `--match-head-commit`, and the stamp.
- **One cloud fixer thread per lane (F1–F11)**, started from `fix/F<n>.md`, pushing each PR to
  `handoff/<lane topic>-<k>` (for example `handoff/r9-f1-coordinator-3` for F1.3). A thread works its
  lane's PRs in order and may prepare the next while the previous is in review; it merges `origin/main`
  (never rebases) before each hand-off and re-executes `fixer.md` steps 2–8.
- **Reviews** by the cloud helpers (Cloud compute helper, Cloud reviewer 2) on the strongest model,
  never the session that wrote the fix and never both reviewers on one PR. **Add a third reviewer when
  more than two hand-offs are waiting** — with ten lanes starting together that is likely within the
  first few hours.
- **RCA seats**: 15, one per `rca: true` class (the fifteenth, for the future-instant class, is new at Phase D), each on the strongest model in its own thread, started
  beside the PR named in section 5 (not inside it). They name each barrier's form; the fixer of the PR
  that lands the barrier builds it.
- **Startable at once (wave 1):** F2.1, F3.1, F4.1, F5.1, F6.1, F7.1, F8.1, F9.1, F10.1, F11.1 — ten
  threads, one per lane, which fills the ~10 cloud containers. F1's thread starts with F1.1 as soon as
  F2.1 merges (F2.1 is deliberately small), so the eleventh thread is not needed until then.

## 4. What needs tvofi, and why (answerable in one pass)

**Owner-gated PRs (9)** — each is its own PR so nothing else waits on it:

| PR | why tvofi |
|---|---|
| F1.10 | `tests/harness.py` is code-owned (D14-s1-02 moves the boost test double's persist patch there); last PR of F1, holds nothing. |
| F6.3 | `tests/card_browser.mjs` is code-owned (the P9 class barrier). |
| F7.3 | **Ruling first:** D8-s2-01's fix overturns tvofi's recorded A3(e) decision (climate unavailable without an indoor thermometer). If tvofi keeps A3(e), no PR: the finding is dispositioned refused. |
| F10.2 | `tests/stress.py` is code-owned; new `stress_budgets.json` entries go through `budget-raise-gate`. |
| F10.3 | `env_drift.py`, `stress.py`, `mutation_table.py`, `closure.py`, `derive_closures.sh` are code-owned; `mutation_budgets.json` may rise as the inventory widens. Lands the I1 and P11 barriers. |
| F10.4 | D7-s1-01 prices coordinator state reached through module-level helpers; an honest re-record likely **raises** coordinator structure budgets — asked before the push (CLAUDE.md rule 2). Also lands the I5 barrier. |
| F11.2 | Workflows, `CODEOWNERS`, `budget_raise_gate.py`, `docs/decisions/` are code-owned. **Two decisions first:** D11-s1-01 is a ruleset setting only tvofi can change (dismiss stale reviews on push, or require last-push approval); D11-s1-04 (with merged D11-s2-03) is tvofi's choice between a distinct delegated identity and a refusal in `budget_raise_gate.py`. |
| F11.3 | Policy: `CLAUDE.md` (D11-s2-04), `.claude/rules/ratchet-budgets.md` and `policy_budgets.json` units (D11-s2-01), `fix-review.md` and `web-fix-wave.js` (D13-s1-02, where tvofi also decides whether a merges-only verdict carry is worth building: the judge measured it saves a few rounds, not most). Also lands the I3 barrier. |
| F11.4 | `.claude/workflows/audit-find.js` is code-owned (D14-s2-03, and the I4 barrier); the round's last PR; optionally folds the owed round-9 driver fixes, which touch the same file. |

**Other asks that may arrive during the wave:**
- Any budget raise a fixer hits (most likely in F1, whose coordinator class sits at zero headroom on several
  metrics; each F1 PR pays for its lines first).
- Any RCA seat that finds no barrier within "The bound" asks tvofi for a ruling rather than recording a
  refusal (PLAN §8.3).
- D0-s2-02 (F2.4) may end as a recorded refusal priced in money and CPU, standing on the #1294 refusal;
  that is the fixer's to record, reported to tvofi.

## 5. RCA seats (15, all on the strongest model)

| class | N judge | N final | starts beside | barrier lands in | barrier proposal (the sweep's; the seat names the form) |
|---|---|---|---|---|---|
| P2 | 27 | 27 | F3.1 | F1.10 | S1 proposes one lint generalising the P2 enumerator: a registry of canonical predicates, and every other decision context reading the same key or threshold refused; sub-shape checks may ride instance PRs (F1.2's proxy-key check), the class-level check lands last |
| I5 | 19 | 19 | F8.1 | F10.4 | S2 finds no single production seam (8 claim shapes); proposes a nightly lane running the shape-checkers, failing on any false/mismatch count; the seat sizes it and chooses nightly or per-PR |
| I1 | 11 | 11 | F9.1 | F10.3 | S3 proposes two: widen the mutation inventory's candidates (D14-s5-02) and a closure-scoped non-UTC lane for tzinfo and timestamp seams (D3-s1-91, D3-s3-01, D7-s1-02) |
| P1 | 9 | 11 | F3.1 | F1.6 | S3 proposes one validated-load helper (convert, isfinite, clamp) used by every loader, about 15 call sites; the store-fuzz check goes in tests/finite_boundary.py |
| I3 | 7 | 7 | F11.1 | F11.3 | S4 proposes the hooks check reading each hook's matcher, and a per-file byte or token cap beside the line cap (or a zero band on the pooled aggregates); owner-gated |
| P11 | 6 | 6 | F10.1 | F10.3 | S4 proposes tests/ha_contract.py contracts for each divergent stub, run nightly against the real package, including the currency and Tibber-reauth probes |
| I4 | 5 | 5 | F11.1 | F11.4 | S4 proposes one shared frontmatter-paths parser, the GOV pin deriving its watched workflows from governance.yml, and one class-id module for the 31 readers |
| P6 | 5 | 5 | F1.2 | F1.10 | S4 proposes one generated producer/consumer key manifest in tests/entities.py, promoting the p6_keys census |
| P9 | 4 | 5 | F6.1 | F6.3 | S5 proposes the enumerate.mjs canonical grid as a browser lane asserting zero contrast, popup-out, indistinct-option, now-marker and label-overlap instances |
| N-solve-recompute | 4 | 5 | F2.2 | F10.2 | S5 proposes a nightly call-count ratchet (recompute instances may only fall); the seat may prefer a structural form or a CPU budget the stress gate sees |
| P3 | 3 | 3 | F2.1 | F1.10 | S5 proposes the p3_floors enumerator as a lint refusing a new floor group or a floor above the schema minimum |
| P5 | 3 | 3 | F4.2 | F4.2 | S5 proposes the p5_gate sweep as a tests/ script asserting zero admitted-over-bar cells |
| N-cpu-gate-blind | 3 | 3 | F10.2 | F10.2 | S5 proposes three additive stress/replay channels: non-kernel solve CPU, a loop-thread cost channel, a throttling-valve scenario |
| N-restart | 2 | 2 | F1.4 | F1.4 | barriered class (RC2): S5 proposes the two enumerators (store race, params restart) as regressions asserting lost == 0, extending the RC2 barrier |
| N-future-instant | 2 | 7 | F3.1 | F1.9 | new at Phase D (S7 raised N past 3): an AST lint over every fromisoformat reachable from a persisted-store load that reaches a now comparison with no clamp at the restore site |

N final is judged findings plus sweep-confirmed instances (PLAN §7). Each barrier PR comes after every
PR holding an instance of its class; the generator refuses the plan otherwise. A seat that finds no
barrier within "The bound" asks tvofi rather than recording a refusal.

## 6. Carry-ins from RESUME, placed

| carry-in | PR |
|---|---|
| #1643 card tests: pin its surviving mutants (ghi as a step mean; `overlays()` iterating covered; the null-stretch denominator in the step mean; askedThrough) | **F6.2** |
| Merged since baseline (#1641, #1642, #1643): findings measured at `1936d5ca` are re-checked before fixing | every brief (standing rule); named specifically in **F1.3** (button.py), **F1.4** (RC2 restart class, #1641), **F6.1** (card, #1643), **F8.3** (`docs/dashboard-card.md`, #1643) |
| L1 indoor-sensor lead, D4 side: a source-id attribute so the card draws the raw thermometer through a staleness gap | **F6.4** (after D1-s5-51's fix in F4.1) |
| Verifier: D9-s1-01's vectorised fix loses parity on Fortran-order batches | **F2.2** |
| Verifier: D14-s4-02's fix must also step `run_fixture` in UTC | **F1.1** |
| Verifier: D10-s1-01's seam misses services.py (`handle_assign_entity`, `services.py:629` at baseline) | **F1.8** |
| Judge/verifier notes carried to the fixer: D2-s2-01's missed coordinator seams (F1.7); D2-s2-03's baseline_end sibling (F2.3); refuted D0-s1-01's two-zone deep-anchor asymmetry as hygiene for the P4 fixer (F2.4); D8-s2-03's finder fix would reintroduce D8-s2-02 (F7.1); G1-V2's `boost.restore` naive-until observation (F3.1); every weakened or narrowed claim (in the finding's fix notes) | as listed |
| L2 extra seams for existing findings (en.json → D5-s1-02; strings.json and README → D6-s2-03; README → D8-s3-03; climate.py → D8-s1-03; config_flow `async_step_dhw` → D12-s1-02; the card's datetime-local handler → D1-s3-01; the price-unit fields → D4-s2-02) | F5.1, F8.3, F7.2, F2.4, F1.2, F3.1, F1.8 respectively |
| Owed round-9 driver fixes (Prepare rounds interpolation, earlier-rounds strip, env_drift warm step, Chromium path, the batch patch's defer and judge-flag arguments) and `tools/audit/README.md` naming `scopes.json`/`check_scopes.py` | optional fold into **F11.4**, tvofi's call |

## 7. Findings I could not place

None. Every one of the 145 survivors and every one of the 9 sweep instances maps to a PR (tables below). Five may end without a code change,
by design: D8-s2-01 (tvofi's A3(e) ruling), D11-s1-01 (a ruleset setting tvofi changes; the PR records it),
D11-s1-04 (tvofi's identity decision), D13-s1-02 (tvofi decides whether to build the carry), and D0-s2-02
(a recorded refusal is a legitimate outcome).

## 8. Merge order, stamps and throughput

- **One merge at a time**, in the proposed queue below, which respects every `after` edge. When two PRs
  are ready together, the one on the longer remaining chain goes first: **F1 is the critical path**
  (ten PRs, the coordinator), then F2.
- **Critical path (inferred, not measured):** F2.1 -> F1.1 -> F1.2 -> F1.3 -> F1.4 -> F1.5 -> F1.6 -> F2.4 -> F1.7 -> F1.8 -> F1.9 -> F1.10 -> F10.4 -> F11.4, 14 PRs deep (the longest chain of
  `after` edges, derived by the generator). The high findings all sit in the first waves: D14-s4-01
  (F2.1, F1.1), D1-s3-01 (F3.1), D1-s5-52 (F4.1), D8-s2-02 (F7.1), D12-s1-01 (F1.2), D2-s3-01 (F1.3).
- **Stamps.** The plan's standing rule holds: no new branch is cut between a fixture-mover's merge and
  its stamp. PRs marked fixture (drift plausible): F1.3, F1.7, F2.1, F2.3, F2.4, F10.1. If one of them
  merges with claimed drift, the orchestrator stamps before the next branch is cut; otherwise, proposed
  stamp points are (a) after the high-severity set above has merged, (b) after F1.6 (P1 barrier), and
  (c) after F11.4, the last PR.
- **Capacity:** ten fixer threads in wave 1, then as lanes finish their threads end; lanes F5, F8, F9 finish
  early (two or three PRs), F11 is mostly waiting on tvofi, F1/F2 run longest. Reviewers: two, plus a third
  when the queue passes two hand-offs.

## 9. Phase D: what the sweeps changed

All seven sweeps landed (commits in the class table). Every class's final N matches judged findings
plus the instances below, and every seam each sweep returned is listed, with its disposition, in the
lane brief of each lane holding the class.

- **P1** (S3): 9 → 11. Two new `ComfortLearner.from_dict` leaves (P1-sw1, P1-sw2), carried by F1.6
  with the P1 barrier.
- **P9** (S5): 4 → 5. The new instance is the chart's SVG axis number/unit label overlap (P9-sw1, F6.1).
  The keyboard route is **not** a counted instance: S5 ran with the keyboard cells off and records it as
  exposure, so it is a check for F6.2 (below), not an instance.
- **avoidable interpreter-bound recomputation** (S5): 4 → 5. `cycling_penalty_batch` (RC-sw1, F2.2); the
  other ThermalParameters properties S5 found are folded into D9-s1-71.
- **persisted future instant trusted without bound** (S7): 2 → 7, now `rca: true` with its own RCA seat
  and barrier. The five instances: four in `coordinator.py` (fuse-advisor cooldown, heavy-snow damping,
  `_detect_outage`, and the lower-confidence immersion recency) in the new F1.9 with the barrier;
  `pump_arbiter.py`'s `hold()` echo grace in F3.2.
- **P5** (S5): stays 3. `async_update_thermal_params` writing two gated parameters with no gate is a
  lead, not an instance: S5 disposed it not applicable, since there is no gate to key wrong.
- Every other class kept its N; a few PRs gained a borrow to reach a seam their finding already owned
  (F1.8 borrows `price_model.py` for P8's money-code seam).

**Barrier order corrected.** The draft stated that a barrier lands after every instance PR of its
class but did not check it. The generator now does, and it refused five barriers in the draft; each
moved to a PR that waits on all its class's instance PRs:

- I5: F8.3 → **F10.4** (instances in F2.1, F2.3, F6.2, F1.10 and F11.3 as well as F8); F10.4 now waits on F11.3,
  and F8.3 no longer borrows `tests/doc_claims.py`.
- P11: F10.1 → **F10.3** (instances in F1.1, F1.7 and F8.3); F10.3 now waits on F1.7 and edits `tests/ha_contract.py`.
- I1: F10.3 stays, and now waits on F9.2 (the last I1 pin PR).
- I3: F11.2 → **F11.3** (D11-s2-01 is an I3 instance in F11.3, and the barrier's shape lives in its files).
- I4: F11.4 stays, and now waits on F10.4 (D7-s3-02, the dead_methods census), so F11.4 is the round's last PR.

The draft's critical path was 13 PRs deep and is now 14: F11.4 now follows F10.4. The new F1.9
sits between F1.8 and F1.10 at the depth F6.4 already had there, so it adds none.

Leads placed as instructions, not instances:

- **P9 keyboard route (S5, exposure, not counted)** -> F6.2: S5 ran its grid with the keyboard cells off, so the 204 pointer-only hits across 8 selectors (both chart pan surfaces, the six setup-picker entity rows) are unverified for a keyboard route. S7's pointer-only sweep disposed the chart pan as guarded (zoom buttons) and the picker surface as guarded (its own keydown handler); D4-s1-04's fixer re-checks the six setup-hit rows with the keyboard cells on and dispositions each.
- **P5 lead: async_update_thermal_params has no gate (S5)** -> F1.4: The set_thermal_parameters service writes house_heat_loss_scale and buffer_cooling_rate with no admission gate. S5 disposed it not applicable to P5 (no gate to key wrong), so it is not a P5 instance and not counted; it is D1-s2-53's seam. D1-s2-53's fixer decides, with the measurement, whether the service write is bounded like the sysid adoption, and says so; F4.2's P5 barrier does not cover this writer.

Ledger notes (not RCA triggers this round; no PR unless a finding already covers them):

- P4 (S6): the ledger's most recurring class, 14 historical instances in rounds 1-7, never barriered or given a detector; N=1 this round (D0-s2-02, F2.4), so no RCA seat. Flagged for whoever owns the ledger's cross-round view.
- P7 (S7): recurred in 4 of 6 swept rounds (2, 3, 5, 9) with no barrier; N=1 this round (D14-s4-01). F1.1's DST tracer barrier is D14-s4-01's own fix, not a class barrier.
- I2 (S7): recurred in 5 of 6 swept rounds (2, 3, 5, 7, 9) with no barrier; N=1 this round (D14-s5-01, F10.3).
- S4: the per-file policy-doc cap counts lines, with no byte or token guard. That is D11-s2-01 (F11.3), whose seams S4 widened to every capped file; no new PR.

---

## PR table (merge order within each lane; `after` gives the cross-lane edges)

| PR | lane | wave | findings | classes | sev | model | tvofi | RCA seat beside | barrier here | after |
|---|---|---|---|---|---|---|---|---|---|---|
| F1.1 | F1 | 2 | D14-s4-01*, D14-s4-02, D3-s1-91, D3-s3-01 | P7, P11, I1 | high | opus | - | - | - | F2.1 |
| F1.2 | F1 | 3 | D12-s1-01, D12-s3-01, D14-s2-01 | P6, P2 | high | opus | - | P6 | - | F1.1 |
| F1.3 | F1 | 4 | D2-s3-01, D1-s2-51, D1-s2-91, D1-s4-02, D10-s1-02 | P2 | high | opus | - | - | - | F1.2 |
| F1.4 | F1 | 5 | D1-s2-52, D1-s2-53, D1-s2-54, D1-s2-03 | N-restart, N-service-clamp, P1 | medium | opus | - | N-restart | N-restart | F1.3 |
| F1.5 | F1 | 6 | D1-s2-04, D1-s2-55, D1-s2-05, D2-s1-51, D7-s2-02 | N-debug-swallow, N-late-try, N-reap-lock, P6, P2 | medium | opus | - | - | - | F1.4 |
| F1.6 | F1 | 7 | D1-s2-02, D1-s1-03, D14-s1-01, +P1-sw1, +P1-sw2 | N-plausibility, P1 | medium | opus | - | - | P1 | F1.5, F3.3, F4.1, F9.1 |
| F1.7 | F1 | 9 | D9-s1-03, D9-s2-01, D10-s1-03, D2-s2-01 | N-loop-cpu, P11, P2 | medium | opus | - | - | - | F1.6, F2.4, F4.2, F5.2, F10.1 |
| F1.8 | F1 | 10 | D14-s2-02, D12-s3-81, D10-s1-01 | P8, P2 | medium | opus | - | - | - | F1.7, F5.2, F6.2, F3.3 |
| F1.9 | F1 | 11 | +FI-sw1, +FI-sw2, +FI-sw3, +FI-sw4 | N-future-instant | barrier | opus | - | - | N-future-instant | F1.8, F3.2 |
| F1.10 | F1 | 12 | D14-s3-01, D14-s1-02, D5-s2-02 | P3, P6, I5 | low | opus | **yes** | - | P2, P6, P3 | F1.9, F1.8, F2.4, F6.4 |
| F2.1 | F2 | 1 | D14-s4-01*, D12-s2-03, D2-s2-81, D2-s3-02, D5-s2-51 | P7, P3, N-sign-floor, I5 | high | opus | - | P3 | - | - |
| F2.2 | F2 | 2 | D9-s1-01, D9-s1-02, D9-s1-04, D9-s1-71, +RC-sw1 | N-solve-recompute | medium | opus | - | N-solve-recompute | - | F2.1 |
| F2.3 | F2 | 3 | D2-s1-01, D2-s1-02, D2-s2-03, D7-s1-71, D5-s2-03 | N-euler-coupled, P2, I5 | medium | opus | - | - | - | F2.2, F4.1 |
| F2.4 | F2 | 8 | D12-s2-01, D8-s1-03, D0-s2-02 | P2, P4 | medium | opus | - | - | - | F2.3, F1.6, F7.2, F5.2 |
| F3.1 | F3 | 1 | D1-s3-01, D1-s1-01, D1-s1-04, D1-s3-05, D1-s1-02 | P2, P1, N-future-instant | high | opus | - | P2, P1, N-future-instant | - | - |
| F3.2 | F3 | 2 | D1-s3-02, D1-s3-03, D12-s2-02, D1-s3-06, +FI-sw5 | P2, P1, N-future-instant | medium | opus | - | - | - | F3.1 |
| F3.3 | F3 | 3 | D1-s4-01, D1-s4-03, D1-s5-02, D1-s5-03, D1-s5-04 | P1, P2, N-min-gap | medium | opus | - | - | - | F3.2 |
| F4.1 | F4 | 1 | D1-s5-52, D1-s5-01, D1-s5-51, D2-s2-02 | P2, N-staleness, N-clamp-range | high | opus | - | - | - | - |
| F4.2 | F4 | 2 | D2-s4-01, D2-s4-81, D14-s3-03, D7-s2-01, D2-s4-02 | P5, N-fit-integrator, P2 | medium | opus | - | P5 | P5 | F4.1 |
| F5.1 | F5 | 1 | D4-s2-03, D4-s2-08, D4-s2-09, D8-s3-02, D8-s3-01, D5-s1-02*, D6-s2-03* | N-escape, N-service-icons, I5, N-name-sort | medium | sonnet | - | - | - | - |
| F5.2 | F5 | 4 | D4-s2-01, D4-s2-05, D4-s2-06, D4-s2-07, D10-s2-01 | P6, N-step-grid, P2, N-menu | medium | sonnet | - | - | - | F5.1, F1.2, F7.1 |
| F6.1 | F6 | 1 | D4-s1-01, D4-s1-02, D4-s1-03, D4-s1-05, +P9-sw1 | P9 | medium | opus | - | P9 | - | - |
| F6.2 | F6 | 2 | D4-s1-04, D5-s2-01 | N-keyboard, I5 | medium | opus | - | - | - | F6.1 |
| F6.3 | F6 | 3 | (class barrier) | - | barrier | opus | **yes** | - | P9 | F6.2 |
| F6.4 | F6 | 11 | D4-s2-81 | N-language | medium | sonnet | - | - | - | F6.3, F1.8 |
| F7.1 | F7 | 1 | D8-s2-02, D8-s2-03, D1-s3-04 | P2, N-shared-config | high | opus | - | - | - | - |
| F7.2 | F7 | 4 | D8-s1-02, D8-s3-03, D8-s3-61 | P2, N-dup-entity | low | opus | - | - | - | F7.1, F8.3 |
| F7.3 | F7 | 9 | D8-s2-01 | N-availability | medium | opus | **yes** | - | - | F7.2, F2.4 |
| F8.1 | F8 | 1 | D5-s1-01, D6-s2-01, D6-s2-02, D5-s1-04, D6-s2-05 | I5, N-markdown | medium | sonnet | - | I5 | - | - |
| F8.2 | F8 | 2 | D5-s1-05, D6-s1-02, D6-s2-04, D6-s1-01, D6-s1-03 | I5 | low | sonnet | - | - | - | F8.1 |
| F8.3 | F8 | 3 | D5-s1-02*, D6-s2-03*, D6-s1-81, D5-s1-03 | I5, P11 | medium | sonnet | - | - | - | F8.2, F5.1 |
| F9.1 | F9 | 1 | D3-s1-01, D3-s2-01, D3-s2-02, D3-s3-02, D3-s3-03 | I1 | medium | sonnet | - | I1 | - | - |
| F9.2 | F9 | 2 | D3-s3-04, D3-s3-05, D7-s3-51 | I1, N-finally-return | medium | sonnet | - | - | - | F9.1 |
| F10.1 | F10 | 1 | D1-s1-51, D1-s1-52, D1-s2-71 | P11 | low | opus | - | P11 | - | - |
| F10.2 | F10 | 3 | D9-s2-02, D9-s2-03, D9-s2-71 | N-cpu-gate-blind | medium | opus | **yes** | N-cpu-gate-blind | N-solve-recompute, N-cpu-gate-blind | F10.1, F1.1, F2.2 |
| F10.3 | F10 | 10 | D7-s1-02, D14-s5-02, D14-s5-01 | I1, I2 | medium | opus | **yes** | - | I1, P11 | F10.2, F8.3, F9.2, F1.7 |
| F10.4 | F10 | 13 | D7-s3-01, D7-s3-72, D7-s3-02, D7-s1-01 | N-dead-member, I4, N-structure-blind | low | opus | **yes** | - | I5 | F10.3, F1.10, F7.3, F11.3 |
| F11.1 | F11 | 1 | D11-s1-71, D13-s1-01, D11-s2-02, D11-s1-02, D11-s1-72 | I4, I3 | medium | opus | - | I3, I4 | - | - |
| F11.2 | F11 | 2 | D11-s1-01, D11-s1-04, D11-s1-03, D13-s1-03 | I3 | medium | opus | **yes** | - | - | F11.1 |
| F11.3 | F11 | 3 | D11-s2-01, D11-s2-04, D13-s1-02 | I3, I5, N-approval-rebuy | medium | opus | **yes** | - | I3 | F11.2 |
| F11.4 | F11 | 14 | D14-s2-03 | I4 | low | opus | **yes** | - | I4 | F11.3, F10.4 |

`*` = part of a finding; the finding closes when every PR listing it has merged (see the split list). `+` = a Phase D sweep instance (table below).

## Files per PR (package paths relative to custom_components/heatpump_optimizer/)

| PR | edits (owned by its lane) | borrows (file from lane) | tvofi because |
|---|---|---|---|
| F1.1 | coordinator.py, accuracy.py, dhw_learning.py, external_heat.py, tests/dst_checks.py, tests/open_meteo.py | tests/replay.py from F10 | - |
| F1.2 | coordinator.py | config_flow.py from F5, modbus_prefill.py from F5, topology.py from F5 | - |
| F1.3 | coordinator.py, button.py | - | - |
| F1.4 | coordinator.py, store.py, services.py, manual_plan.py | - | - |
| F1.5 | coordinator.py | - | - |
| F1.6 | coordinator.py, dhw_learning.py, manual_plan.py | legionella.py from F3, boost.py from F3, pump_arbiter.py from F3, snapshots.py from F3, away.py from F3, comfort_learning.py from F3, inputs.py from F4, tests/finite_boundary.py from F9 | - |
| F1.7 | coordinator.py | sysid.py from F4, sensor.py from F7, topology.py from F5, optimizer.py from F2, tests/hastub/homeassistant/exceptions.py from F10, tests/hastub/homeassistant/helpers/update_coordinator.py from F10 | - |
| F1.8 | coordinator.py, services.py | inputs.py from F4, currency.py from F4, config_flow.py from F5, strings.json from F5, translations/en.json from F5, translations/sv.json from F5, tests/config_flow_steps.py from F5, www/heatpump-optimizer-card.js from F6, grid_fee.py from F3, price_model.py from F3 | - |
| F1.9 | coordinator.py | - | - |
| F1.10 | coordinator.py | sensor.py from F7, boost.py from F3, defrost.py from F3, tariff.py from F3, away.py from F3, const.py from F4, sysid.py from F4, optimizer.py from F2, thermal_model.py from F2, tests/harness.py from F10 | tests/harness.py is code-owned (D14-s1-02 moves the test double's persist patch there) |
| F2.1 | optimizer.py, pv.py | - | - |
| F2.2 | optimizer.py, thermal_model.py | - | - |
| F2.3 | thermal_model.py, optimizer.py | const.py from F4 | - |
| F2.4 | optimizer.py | pump_arbiter.py from F3, entity.py from F7, sensor.py from F7, climate.py from F7 | - |
| F3.1 | away.py, boost.py, legionella.py, pump_arbiter.py, snapshots.py, curve_learning.py, comfort_learning.py, drift.py | - | - |
| F3.2 | pump_arbiter.py, freq_control.py | - | - |
| F3.3 | defrost.py, price_model.py, tariff.py, open_meteo.py | - | - |
| F4.1 | inputs.py, const.py, flow_lift.py | - | - |
| F4.2 | sysid.py | - | - |
| F5.1 | strings.json, translations/en.json, translations/sv.json, icons.json | - | - |
| F5.2 | config_flow.py, strings.json, translations/en.json, translations/sv.json, icons.json, quality_scale.yaml, tests/config_flow_steps.py | climate.py from F7 | - |
| F6.1 | www/heatpump-optimizer-card.js, tests/card.mjs, tests/card_drift.mjs | - | - |
| F6.2 | www/heatpump-optimizer-card.js, tests/card.mjs | - | - |
| F6.3 | tests/card_browser.mjs | - | tests/card_browser.mjs is code-owned |
| F6.4 | www/heatpump-optimizer-card.js | topology.py from F5, config_flow.py from F5, sensor.py from F7, strings.json from F5, translations/en.json from F5, translations/sv.json from F5 | - |
| F7.1 | climate.py, switch.py | - | - |
| F7.2 | sensor.py, binary_sensor.py | README.md from F8 | - |
| F7.3 | climate.py | - | the fix overturns the owner's recorded A3(e) decision pinned in tests/entities.py; tvofi rules first |
| F8.1 | docs/configuration.md | - | - |
| F8.2 | docs/configuration.md, docs/how-it-works.md, README.md | - | - |
| F8.3 | docs/setup.md, docs/ecl110.md, docs/configuration.md, docs/how-it-works.md, README.md, docs/dashboard-card.md | - | - |
| F9.1 | tests/finite_boundary.py | - | - |
| F9.2 | tests/nightly_ha.py | - | - |
| F10.1 | tests/hastub/homeassistant/helpers/storage.py, tests/hastub/homeassistant/util/dt.py, tests/hastub/homeassistant/helpers/update_coordinator.py, tests/ha_contract.py | - | - |
| F10.2 | tests/stress.py, tests/stress_budgets.json, tests/replay.py | - | tests/stress.py is code-owned; new stress_budgets.json entries go through budget-raise-gate |
| F10.3 | tests/env_drift.py, tests/stress.py, tests/mutation_table.py, tests/mutation_budgets.json, tests/closure.py, tests/derive_closures.sh, tests/deployment_shape.py, tests/doc_claims.py, tests/ha_contract.py | - | tests/env_drift.py, tests/stress.py, tests/mutation_table.py, tests/closure.py and tests/derive_closures.sh are code-owned; mutation_budgets.json may rise |
| F10.4 | tests/structure.py, tests/doc_claims.py | coordinator.py from F1, defrost.py from F3, open_meteo.py from F3, inputs.py from F4, optimizer.py from F2, thermal_model.py from F2, tests/open_meteo.py from F1 | D7-s1-01 prices coordinator state reached through module-level helpers, which likely raises coordinator budgets: ask before the push |
| F11.1 | .claude/workflows/policy_lint.mjs, .claude/workflows/rules_sync.mjs, tools/release/stamp.py | - | - |
| F11.2 | .github/workflows/tests.yml, .github/workflows/pr-contract.yml, .github/CODEOWNERS, .claude/workflows/budget_raise_gate.py, docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md | - | workflows, CODEOWNERS, budget_raise_gate.py and docs/decisions are code-owned; D11-s1-01 and D11-s1-04 are owner decisions |
| F11.3 | .claude/workflows/policy_lint.mjs, .claude/workflows/policy_budgets.json, .claude/rules/ratchet-budgets.md, .cursor/rules/ratchet-budgets.mdc, CLAUDE.md, tools/audit/briefs/fix-review.md, .claude/workflows/web-fix-wave.js, tools/audit/app_approve.sh | - | policy (CLAUDE.md, .claude/rules, tools/audit/briefs) and web-fix-wave.js are code-owned |
| F11.4 | tools/audit/scopes.json, tools/audit/check_scopes.py, .claude/workflows/audit-find.js, .claude/workflows/check-wave-script.mjs | - | audit-find.js is code-owned |

## Finding to PR (all 145 survivors)

| finding | sev | class | PR | title |
|---|---|---|---|---|
| D0-s2-02 | low | P4 | F2.4 | Multi-start seed set misses lower basins on shoulder prices, above the flat-price null |
| D1-s1-01 | medium | P1 | F3.1 | A tz-naive persisted timestamp raises on every cycle at three sibling loader seams (snapshots, curve, comfort) |
| D1-s1-02 | medium | P1 | F3.1 | A non-numeric snapshot temperature_bias makes best_restore raise and suppresses the accuracy_drift issue for good |
| D1-s1-03 | medium | N-plausibility | F1.6 | One out-of-range DHW thermometer sample is booked as a physically impossible draw and inflates the published p90 |
| D1-s1-04 | low | N-future-instant | F3.1 | A timestamp stored while the clock ran ahead is trusted verbatim and stretches stale timeouts by the clock error |
| D1-s1-51 | low | P11 | F10.1 | hastub Store decodes with stdlib json: 6 of 6 hostile number tokens load where HA's orjson Store drops the file |
| D1-s1-52 | low | P11 | F10.1 | hastub dt_util.now() is naive by default: the naive-vs-aware verdict of 6 of 6 stored-timestamp cells is inverted |
| D1-s2-02 | medium | N-plausibility | F1.6 | Finite-but-absurd weather forecast values reach the solve unbounded: failed plans and a runaway solve |
| D1-s2-03 | medium | P1 | F1.4 | A sample count past 2**64 in the thermal-learning store fails every cycle, across restarts |
| D1-s2-04 | medium | N-debug-swallow | F1.5 | Five cycle-path guards swallow a persistent failure at DEBUG, including pump and frequency actuation |
| D1-s2-05 | medium | N-reap-lock | F1.5 | Home Assistant stop waits out an in-flight solve before reaping the solve worker |
| D1-s2-51 | medium | P2 | F1.3 | A learner or arbiter raise on the cycle path fails the solve or the whole cycle and skips actuation and saves |
| D1-s2-52 | medium | N-restart | F1.4 | Five store writers do not wait for the startup read: a save in that window replaces persisted learned state |
| D1-s2-53 | medium | N-restart | F1.4 | set_thermal_parameters changes are silently lost at the next restart (24 of 26 fields) |
| D1-s2-54 (merged: D6-s1-04) | low | N-service-clamp | F1.4 | apply_manual_plan accepts expires_at past the horizon: the override owns all 96 steps unenforced |
| D1-s2-55 | medium | N-late-try | F1.5 | A solve worker that cannot start (Popen OSError) skips the in-process fallback: no plan, no fallback notice |
| D1-s2-71 | low | P11 | F10.1 | hastub DataUpdateCoordinator drops update_interval: the coordinator's cadence is unreadable in 4 of 4 cells |
| D1-s2-91 | medium | P2 | F1.3 | FlowCurveBias.observe raise aborts the cycle's accuracy pipeline and fails the whole update |
| D1-s3-01 | high | P2 | F3.1 | A tz-less return_time (card datetime-local) or a naive stored datetime wedges every cycle with TypeError |
| D1-s3-02 | medium | P2 | F3.2 | Pump-duty arbiter re-registers its timer and state listener on an unloaded coordinator and keeps writing the pump |
| D1-s3-03 | medium | P1 | F3.2 | pump_arbiter._load installs non-numeric set-point values that raise TypeError on every apply |
| D1-s3-04 | low | N-shared-config | F7.1 | Climate entity publishes the away setback as the user's target while the solve is in the executor |
| D1-s3-05 | low | N-future-instant | F3.1 | Boost 'two-hour maximum' is an absolute instant: a clock step back or a far-future store extends it without bound |
| D1-s3-06 | medium | P1 | F3.2 | FrequencyMap.from_dict admits an unbounded ratio or out-of-range decile that pins recommend() at hz_min for days |
| D1-s4-01 | low | P1 | F3.3 | DefrostDerate.from_dict admits non-finite/out-of-range duty; the bucket pins at DERATE_MIN and never recovers |
| D1-s4-02 | medium | P2 | F1.3 | A failed solve is returned as a plan with status 'failed (...)', so the coordinator counts it a success |
| D1-s4-03 | low | P1 | F3.3 | One unreadable cell in a v2 defrost store voids all 12 measured buckets and is labelled a pre-v5.3.0 upgrade |
| D1-s5-01 | medium | P2 | F4.1 | inputs.age_of ignores last_reported and accepts future stamps, diverging from InputReader's freshness rule |
| D1-s5-02 | medium | P1 | F3.3 | Learner-store loaders check finiteness but not the domain their own update path enforces (price shape, peak tracker) |
| D1-s5-03 | low | P2 | F3.3 | One huge JSON integer drops a whole price fetch (entity and Tibber) or Open-Meteo refresh instead of one row |
| D1-s5-04 | low | N-min-gap | F3.3 | One off-grid timestamp collapses Open-Meteo's inferred resolution and erases the whole solar horizon |
| D1-s5-51 | medium | N-staleness | F4.1 | A report-on-change indoor thermometer silent over 60 min turns Indoor Temperature unavailable |
| D1-s5-52 | high | P2 | F4.1 | InputReader has no plausibility window: -127 and 85 degC sentinels deliver as ok readings |
| D2-s1-01 | medium | N-euler-coupled | F2.3 | Euler sub-step guard judges each store's diagonal ratio only, so coupled stores in accepted configs diverge |
| D2-s1-02 | low | P2 | F2.3 | DHW refill coil debits the wood tank the full coil heat but spares the DHW tank only its scaled share |
| D2-s1-51 | low | P6 | F1.5 | DHW setpoint advisor prices candidates at the 5.0 degC ThermalState default when no outdoor thermometer is mapped |
| D2-s2-01 | medium | P2 | F1.7 | Settlement caps (slab_settlement_cap, hold_demand_kw) ignore the learned house_heat_loss_scale the dynamics apply |
| D2-s2-02 | medium | N-clamp-range | F4.1 | #1067 flow-lift bias clamp (15 K) cannot reach real supply: model curve tops out at 27.9 C, COP overstated up to 37% |
| D2-s2-03 | low | P2 | F2.3 | DHW-path savings settle-up replays space schedule without the DHW coil: end state differs from published trajectory |
| D2-s2-81 | medium | P3 | F2.1 | Two-zone comfort penalty halves each zone's floor price; shipped plans sit up to 0.46 K below min_temp |
| D2-s3-01 (merged: D8-s1-01) | high | P2 | F1.3 | _current_spot_price reads a quarter up to 45 min stale under 15-minute price entries |
| D2-s3-02 | low | N-sign-floor | F2.1 | PV piecewise cost clipped by import_margin's zero floor wherever import price < export price |
| D2-s4-01 | low | P5 | F4.2 | sysid adoption interval misses the true UA on 14 of 22 fits it admits; admitted fits biased high |
| D2-s4-02 | medium | P2 | F4.2 | sysid step sized to exactly the abort bound: sensor noise aborts 100 of 294 experiments, light_new 81 of 96 |
| D2-s4-81 | medium | P5 | F4.2 | sysid cannot adopt its own exact noise-free fit on 43 of 80 preset houses, yet arms on all 80 |
| D3-s1-01 | low | I1 | F9.1 | No closure script fails when _dhw_inlet_c's lower plausibility bound moves (-5.0 <= value -> -5.0 < value) |
| D3-s1-91 | medium | I1 | F1.1 | coordinator.py tzinfo guards (:8112, :8384) are dead under the gate's naive clock; unblinded they crash |
| D3-s2-01 | low | I1 | F9.1 | Store-parser non-finite guards in flow_lift, tariff, price_model survive deletion: no gate driver notices |
| D3-s2-02 | low | I1 | F9.1 | PriceShapeModel residual_var restore can discard every stored variance with the gate green |
| D3-s3-01 | medium | I1 | F1.1 | Every gate driver runs with process local time = UTC, so open_meteo's naive-stamp UTC guard is deletable |
| D3-s3-02 | medium | I1 | F9.1 | DrawStats.from_dict can zero the open draw occurrence and no gate check notices |
| D3-s3-03 | medium | I1 | F9.1 | MonthlyLedger.add's non-finite guard is unpinned; one NaN amount loses the month on reload |
| D3-s3-04 | medium | I1 | F9.2 | No gate check observes a positive draw folded by DhwProfileLearner.async_fold_draw_stats |
| D3-s3-05 | low | I1 | F9.2 | The disinfection write-failed notice memo is unpinned |
| D4-s1-01 | medium | P9 | F6.1 | Status text coloured by HA's --success/--error/--warning-color fails WCAG AA on the default themes |
| D4-s1-02 | low | P9 | F6.1 | Lane slot menu is placed at the tap point unclamped; near the right edge it spills past its chart and the viewport |
| D4-s1-03 | medium | P9 | F6.1 | Setup picker: two identically named sensors render as identical options at 375 and 768 px |
| D4-s1-04 | medium | N-keyboard | F6.2 | Setup layout editor: removing a pipe, drawing a pipe and moving a box have no keyboard route |
| D4-s1-05 | medium | P9 | F6.1 | Now-marker label prints over the measured-now reading on the live default view |
| D4-s2-01 | medium | P6 | F5.2 | Setup wizard's device pre-fill page shows raw keys: 3 unlabelled fields and 1 untranslated error |
| D4-s2-03 | medium | N-escape | F5.1 | The hot-water minimum error text shows literal '\u00b0C' (en) and 9 escaped letters (sv) |
| D4-s2-05 | low | N-step-grid | F5.2 | 12 number fields start off their own step grid: native validity flags them, one spinner click gives 5.1 not 5.5 |
| D4-s2-06 | low | P2 | F5.2 | The zones page computes the derivation-overwrite warning but never shows it for its 6 derived fields |
| D4-s2-07 | low | N-menu | F5.2 | After 'Quick setup (recommended)' the wizard returns to the identical menu, offering quick setup again |
| D4-s2-08 | low | N-service-icons | F5.1 | None of the 12 registered services has an icon in icons.json |
| D4-s2-09 | low | I5 | F5.1 | 8 help texts per language write '45 C' / 'W/m2' beside selectors that say °C and m² |
| D4-s2-81 | medium | N-language | F6.4 | Setup overview page and setup diagram publish English slot text on a Swedish install |
| D5-s1-01 | medium | I5 | F8.1 | configuration.md 'Initial setup' documents the pre-v6.6.5 flow: no finish menu, Tibber token required, 74 entities |
| D5-s1-02 | medium | I5 | F5.1 (L2 seam: the quick-setup text in en.json and sv.json), F8.3 (docs/setup.md) | setup.md Quick setup promises buffer storage and two-tank physics that the quick-setup answers cannot produce |
| D5-s1-03 | low | I5 | F8.3 | dashboard-card.md says the card version lags the integration; the stamp keeps them equal every release |
| D5-s1-04 | low | N-markdown | F8.1 | configuration.md has 9 lines a GFM renderer misplaces: 3 table rows as pipe text, 6 prose lines as rows |
| D5-s1-05 | low | I5 | F8.2 | Docs name 5 option fields by labels the options forms do not show |
| D5-s2-01 | low | I5 | F6.2 | Card comments cite 12 private members the card no longer has (17 mentions) |
| D5-s2-02 | low | I5 | F1.10 | Three comments cite a number the code beside them does not deliver |
| D5-s2-03 | low | I5 | F2.3 | DHW_COLD_WATER_TEMP comment claims the draw model heats from it; the draw reads the configured inlet |
| D5-s2-51 | low | I5 | F2.1 | Two optimizer comments describe a data flow the code does not have (warm-start alignment, buffer-series stash) |
| D6-s1-01 | low | I5 | F8.2 | README's Heat Pump Action state list omits idle and system_identification, which the sensor publishes |
| D6-s1-02 | low | I5 | F8.2 | README puts the two-zone split and the orientation factor on the wrong options pages |
| D6-s1-03 | low | I5 | F8.2 | README's disabled-by-default census omits six hot-water sensors that the no-hot-water install disables |
| D6-s1-81 | low | P11 | F8.3 | README's SEK currency fallback is unreachable under Home Assistant core, which defaults Config.currency to EUR |
| D6-s2-01 | low | I5 | F8.1 | configuration.md says 'All 74 entities'; the six platforms create 75 |
| D6-s2-02 | low | I5 | F8.1 | configuration.md: the weather page does not create the entry; the setup flowchart omits the menu and overview |
| D6-s2-03 | low | I5 | F5.1 (L2 seam: the curve-bias figure in strings.json), F8.3 (docs) | Curve-bias 'at most 0.5 K per week' is false: 0.6 K in a 7-day window |
| D6-s2-04 | low | I5 | F8.2 | how-it-works.md: space solve 'from two starting points'; it runs four, each refined and polished |
| D6-s2-05 (merged: D5-s1-06) | low | I5 | F8.1 | configuration.md simulate_plan field list omits the five wood fields |
| D7-s1-01 | low | N-structure-blind | F10.4 | Structural ratchet does not price coordinator state reached via module-level _helper(self, ...) |
| D7-s1-02 | low | I1 | F10.3 | Drift-gate comparison and stress per-scenario budget verdict are deletable with every runnable check green |
| D7-s1-71 | low | P2 | F2.3 | Cold-water inlet default held three times: 3 of 5 sites ignore DEFAULT_DHW_INLET_TEMP when it moves |
| D7-s2-01 | medium | N-fit-integrator | F4.2 | sysid two-state fit rolls the candidate one Euler step per sample: UA 17-25% low, 0/3 presets adopt |
| D7-s2-02 | medium | P2 | F1.5 | Defrost derate fallback folds meter ratios _cop_fold_blocked refuses to the COP learner |
| D7-s3-01 | low | N-dead-member | F10.4 | 10 class members are reached by no production code; 9 are kept only by tests that pin them |
| D7-s3-02 | low | I4 | F10.4 | structure.py dead_methods reads 0 while 9 members are dead: properties skipped, bare-name loads count |
| D7-s3-51 | low | N-finally-return | F9.2 | nightly_ha._async_check_a4 returns inside finally: an in-flight CancelledError or KeyboardInterrupt is swallowed |
| D7-s3-72 | low | N-dead-member | F10.4 | 4 of 5 ThermalModel per-step scratch members are written every step and read by no production consumer |
| D8-s1-02 | low | P2 | F7.2 | DHW Heating Schedule counts 15-minute steps as 'heating periods', disagreeing with DHW Heating Plan's slot count |
| D8-s1-03 | low | P2 | F2.4 | Recommended Power publishes a sub-threshold draw at steps Heat Pump Action reports 'off' |
| D8-s2-01 | medium | N-availability | F7.3 | Climate entity is unavailable with no indoor thermometer, taking the thermostat control with it |
| D8-s2-02 | high | P2 | F7.1 | Climate hvac_action publishes off while an active boost runs the pump in optimizer mode off |
| D8-s2-03 | low | P2 | F7.1 | Mode actions publish a state that mixes the live mode with the stale payload mode |
| D8-s3-01 | low | N-name-sort | F5.1 | Accuracy and Energy-dashboard meter families split in both English and Swedish name sort |
| D8-s3-02 | low | I5 | F5.1 | Swedish name of Sensor-Gap Advisor reads 'sensor gap in the currency' and drops the advisor role |
| D8-s3-03 | low | N-dup-entity | F7.2 | Upper Floor Temperature, a byte duplicate of Indoor Temperature, is enabled by default on every install |
| D8-s3-61 | low | P2 | F7.2 | Valve Target Recommendation ships disabled where a mixing valve is set, and available-but-unknown where none is |
| D9-s1-01 | medium | N-solve-recompute | F2.2 | Per-row Python loop in _comfort_terms_batch costs 13-32% of every solve; a row-vectorized twin is bit-identical here |
| D9-s1-02 | medium | N-solve-recompute | F2.2 | L-BFGS-B asks the scalar objective for f(x) every iterate at ~19-26x a batched row: 9-19% of the solve |
| D9-s1-03 | low | N-loop-cpu | F1.7 | The sysid two-state fit runs inside one event-loop callback: 43-228 ms here (1.1-6x a reference solve) |
| D9-s1-04 | low | N-solve-recompute | F2.2 | DHW min-run repair: a full-suffix re-simulation per refused weak slot, 12-23% of a single-zone DHW solve |
| D9-s1-71 | low | N-solve-recompute | F2.2 | Constant DHW parameter helpers recomputed ~15-45k times per solve; a per-solve cache saves 3-17 % of CPU |
| D9-s2-01 | low | N-loop-cpu | F1.7 | sensor_advisor ranking re-simulated on the event loop at every plan-sensor write: ~32% of loop CPU |
| D9-s2-02 | medium | N-cpu-gate-blind | F10.2 | No budgeted check sees a 2x of the coordinator's loop-thread work; stress.py reaches none of it |
| D9-s2-03 | medium | N-cpu-gate-blind | F10.2 | stress.py misses a 2x solve regression in one scenario when the extra work is outside the simulate seams |
| D9-s2-71 | medium | N-cpu-gate-blind | F10.2 | stress.py samples 0 of 51 throttling-valve plants; a valve adds 1.3-2.7x solve CPU the gate never sees |
| D10-s1-01 | medium | P2 | F1.8 | Entry unique id is not re-derived after reauth or an options edit, so the same plant can be set up twice |
| D10-s1-02 | medium | P2 | F1.3 | Optimize-now button press returns normally when the solve did not run; the run_optimization action raises |
| D10-s1-03 | low | P11 | F1.7 | Tibber auth refusal reaches HA as ConfigEntryNotReady/UpdateFailed, never ConfigEntryAuthFailed |
| D10-s2-01 | low | P6 | F5.2 | Climate presets auto and economy are non-standard and have no translation or icon in any language |
| D11-s1-01 | medium | I3 | F11.2 | A code-owned change pushed after the owner approval merges on that stale approval (dismiss_stale_reviews=false) |
| D11-s1-02 | medium | I3 | F11.1 | A non-stamp direct push to main over the DeployKey bypass is reported by no enumerator |
| D11-s1-03 | low | I3 | F11.2 | Three pull_request jobs execute the PR's own code-owned scripts while holding contents:write + actions:write |
| D11-s1-04 (merged: D11-s2-03) | medium | I3 | F11.2 | Owner approvals given by the orchestrator are indistinguishable from the owner's in GitHub's record |
| D11-s1-71 | low | I4 | F11.1 | Two parsers of a rule's paths: frontmatter disagree on 2 of 6 legal shapes (rules_sync vs policy_lint) |
| D11-s1-72 | low | I4 | F11.1 | entities.py GOV pin reads governance.yml only: a new governance job in 3 of 3 other workflow files passes |
| D11-s2-01 | low | I3 | F11.3 | Per-file policy caps count lines, so a capped rule file grows in prose with its per-file budget check green |
| D11-s2-02 | low | I3 | F11.1 | policy_lint --hooks never reads a hook's matcher: a PreToolUse matcher naming no edit tool passes as wired |
| D11-s2-04 | low | I5 | F11.3 | CLAUDE.md rule 1 quotes a mode line the gate does not print, and says FULL prints a zero it does not |
| D12-s1-01 | high | P6 | F1.2 | Hot water without a tank probe: every solve starts from the 55 C ThermalState default, never advanced |
| D12-s2-01 | medium | P2 | F2.4 | On an on/off pump, the switch path switches off steps whose planned heat the plan books as delivered |
| D12-s2-02 | medium | P2 | F3.2 | The pump-duty arbiter writes the operating mode with select.select_option whatever domain the mode slot holds |
| D12-s2-03 | medium | P3 | F2.1 | On an on/off pump every full-power step publishes as 'eco' and power_normalized runs to -60 |
| D12-s3-01 (merged: D4-s2-04, D12-s1-02) | medium | P2 | F1.2 | Full config-flow wizard invents a DHW tank and a second zone the user never affirmed |
| D12-s3-81 | medium | P8 | F1.8 | Grid-fee bounds are SEK numbers: a 0.05 EUR/kWh fee is unenterable in HUF, ISK, JPY and KRW |
| D13-s1-01 | medium | I4 | F11.1 | --stats API-mode enumerator silently drops 52 of 253 window merges whose /commits/<sha>/pulls answers [] |
| D13-s1-02 | medium | N-approval-rebuy | F11.3 | 22 re-verification rounds after a moved head caught 0 defects; 12 heads moved only by merges or ci: commits |
| D13-s1-03 | medium | I3 | F11.2 | Body-answer blocks (8) exceed every engineering block class (max 1); record-and-body 12 vs engineering 7 |
| D14-s1-01 | medium | P1 | F1.6 | P1: a malformed store leaf raises out of a loader or consumer; a naive legionella timestamp wedges every refresh |
| D14-s1-02 | low | P6 | F1.10 | P6: horizon_hours read from coordinator.data but never written; boost probes a field only a test double defines |
| D14-s2-01 | medium | P2 | F1.2 | P2: the two-zone and wood-furnace facts are re-derived from a proxy key at three seams beside their canonical predicate |
| D14-s2-02 (merged: D4-s2-02) | medium | P8 | F1.8 | P8: a money figure's currency comes from the label source, never from the price feed that denominates it |
| D14-s2-03 | low | I4 | F11.4 | I4: class roster and finding grammar have disagreeing readers (P11 on no D14 seat; intake admits schema-refused ids) |
| D14-s3-01 | low | P3 | F1.10 | P3: 22 quantities are read through a positive floor at one seam and raw at a sibling; no check enumerates them |
| D14-s3-03 | medium | P5 | F4.2 | P5: sysid adoption gate keys on the UA half-width, which barely moves while unmodelled free heat biases UA to -21 % |
| D14-s4-01 | high | P7 | F1.1 (coordinator, accuracy, dhw_learning and external_heat seams, plus the DST tracer barrier), F2.1 (optimizer seam: get_current_action step length) | Eight production seams still do wall-clock datetime arithmetic across DST; the forecast grid lands 60 min off |
| D14-s4-02 | low | P11 | F1.1 | The replay lane freezes a fixed-offset clock, so a DST-day replay reports zero P7 seams |
| D14-s5-01 | medium | I2 | F10.3 | Python closures miss every file a spawned child process reads; select() skips the script on a change to it |
| D14-s5-02 | medium | I1 | F10.3 | Mutation ratchet inventory cannot see 528 of 2313 production guard seams; a new guard of those shapes raises it by 0 |

## Sweep-confirmed instances beyond the judged findings (Phase D)

Line numbers are at baseline `1936d5ca`; each probe is under its sweep's commit. N final = judged findings + these.

| instance | class | sweep | PR | seam | what fails | probe |
|---|---|---|---|---|---|---|
| P1-sw1 | P1 | S3 @ `053c4869ad` | F1.6 | comfort_learning.py: ComfortLearner.from_dict, the stored_configured leaf (baseline line 236) | a NaN stored_configured passes the stale-weight gate instead of being discarded by it | `tools/audit/round9/D14/sweep/P1/probes.py` |
| P1-sw2 | P1 | S3 @ `053c4869ad` | F1.6 | comfort_learning.py: ComfortLearner.from_dict, the learned_weight and evidence leaves (baseline lines 244-245) | a float() cast with no isfinite check | `tools/audit/round9/D14/sweep/P1/probes.py` |
| P9-sw1 | P9 | S5 @ `51a2e98a86` | F6.1 | www/heatpump-optimizer-card.js: the chart's SVG axis number and unit label pairs | the unit suffix sits at a fixed offset from its number with no measured-width check, so the pair overlaps at 1280 and 375 px wide (the enumerator's overlap_instances, distinct from D4-s1-05's now-marker collisions) | `tools/audit/round9/D14/sweep/P9/enumerate.mjs` |
| RC-sw1 | N-solve-recompute | S5 @ `51a2e98a86` | F2.2 | optimizer.py: cycling_penalty_batch | the same per-row Python loop as D9-s1-01's, in an independent function called once per iterate | `tools/audit/round9/D14/sweep/avoidable-interpreter-bound-recomputation/enumerate.py` |
| FI-sw1 | N-future-instant | S7 @ `1152a74346` | F1.9 | coordinator.py: the fuse advisor's 7-day recompute cooldown (_fuse_advisor_at restored from the ledger store; baseline lines 8007 and 8023-8024) | a restored instant written ahead of the clock holds the cooldown active indefinitely | `tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/probe_fuse_advisor.py` |
| FI-sw2 | N-future-instant | S7 @ `1152a74346` | F1.9 | coordinator.py: the heavy-snow damping window (_last_heavy_snow restored from the store; baseline lines 2953 and 6306) | damping stays on while the restored instant is ahead of now | `tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/probe_more_instances.py` |
| FI-sw3 | N-future-instant | S7 @ `1152a74346` | F1.9 | coordinator.py: _detect_outage's staggered-recovery window (the stored last_tick; baseline lines 7343 and 8099-8114) | a future last_tick masks a real outage | `tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/probe_more_instances.py` |
| FI-sw4 | N-future-instant | S7 @ `1152a74346` | F1.9 | coordinator.py: the immersion-event recency count (_immersion_events; baseline line 8381) | same shape, lower confidence: not separately probed, and it needs three or more corrupted entries to move the output; probe it first and disposition it with the measurement if it does not reproduce | `none (S7 disposed it on the mechanism)` |
| FI-sw5 | N-future-instant | S7 @ `1152a74346` | F3.2 | pump_arbiter.py: hold()'s write-echo grace period (held.written restored in _load; baseline lines 629 and 405-407) | a restored write instant ahead of the clock keeps the grace period open | `tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/probe_more_instances.py` |

## Class to PR

Seams are the sweep's own dispositions (`instance`, `guarded`, `not applicable`), every one listed in the lane brief of each lane that holds the class.

| class | N judge | N final | rca | sweep | seams | PRs | barrier PR |
|---|---|---|---|---|---|---|---|
| P2 | 27 | 27 | yes | S1 @ `c44e7bcd60` | 27 instance | F1.3, F3.1, F3.2, F4.1, F3.3, F2.3, F1.7, F4.2, F5.2, F1.5, F7.2, F2.4, F7.1, F1.8, F1.2 | F1.10 |
| I5 | 19 | 19 | yes | S2 @ `38f1230e92` | 16 instance, 4 not applicable | F5.1, F8.1, F8.3, F8.2, F6.2, F1.10, F2.3, F2.1, F11.3 | F10.4 |
| I1 | 11 | 11 | yes | S3 @ `053c4869ad` | 12 instance | F9.1, F1.1, F9.2, F10.3 | F10.3 |
| P1 | 9 | 11 | yes | S3 @ `053c4869ad` | 6 guarded, 14 instance, 2 not applicable | F3.1, F1.4, F3.2, F3.3, F1.6 | F1.6 |
| I3 | 7 | 7 | yes | S4 @ `b2e3560671` | 1 guarded, 26 instance, 3 not applicable | F11.2, F11.1, F11.3 | F11.3 |
| P11 | 6 | 6 | yes | S4 @ `b2e3560671` | 6 instance, 2 not applicable | F10.1, F8.3, F1.7, F1.1 | F10.3 |
| I4 | 5 | 5 | yes | S4 @ `b2e3560671` | 2 guarded, 8 instance | F10.4, F11.1, F11.4 | F11.4 |
| P6 | 5 | 5 | yes | S4 @ `b2e3560671` | 1 guarded, 12 instance | F1.5, F5.2, F1.2, F1.10 | F1.10 |
| P9 | 4 | 5 | yes | S5 @ `51a2e98a86` | 5 instance, 1 not applicable | F6.1 | F6.3 |
| N-solve-recompute | 4 | 5 | yes | S5 @ `51a2e98a86` | 7 instance, 1 not applicable | F2.2 | F10.2 |
| P3 | 3 | 3 | yes | S5 @ `51a2e98a86` | 1 guarded, 3 instance | F2.1, F1.10 | F1.10 |
| P5 | 3 | 3 | yes | S5 @ `51a2e98a86` | 3 instance, 1 not applicable | F4.2 | F4.2 |
| N-cpu-gate-blind | 3 | 3 | yes | S5 @ `51a2e98a86` | 3 instance | F10.2 | F10.2 |
| P8 | 2 | 2 | no | S6 @ `6b65c9c4a8` | 2 guarded, 8 instance, 1 not applicable | F1.8 | - (N below 3, not barriered) |
| N-loop-cpu | 2 | 2 | no | S7 @ `1152a74346` | 2 instance | F1.7 | - (N below 3, not barriered) |
| N-plausibility | 2 | 2 | no | S6 @ `6b65c9c4a8` | 2 guarded, 2 instance | F1.6 | - (N below 3, not barriered) |
| N-future-instant | 2 | 7 | yes | S7 @ `1152a74346` | 10 instance, 9 not applicable | F3.1, F1.9, F3.2 | F1.9 |
| N-dead-member | 2 | 2 | no | S6 @ `6b65c9c4a8` | 7 instance, 1 not applicable | F10.4 | - (N below 3, not barriered) |
| N-restart | 2 | 2 | yes (barriered) | S5 @ `51a2e98a86` | 1 guarded, 2 instance | F1.4 | F1.4 |
| I2 | 1 | 1 | no | S7 @ `1152a74346` | 2 instance | F10.3 | - (N below 3, not barriered) |
| P4 | 1 | 1 | no | S6 @ `6b65c9c4a8` | 2 instance | F2.4 | - (N below 3, not barriered) |
| P7 | 1 | 1 | no | S7 @ `1152a74346` | 1 guarded, 8 instance, 1 not applicable | F1.1, F2.1 | - (N below 3, not barriered) |
| N-sign-floor | 1 | 1 | no | S6 @ `6b65c9c4a8` | 3 instance, 1 not applicable | F2.1 | - (N below 3, not barriered) |
| N-approval-rebuy | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F11.3 | - (N below 3, not barriered) |
| N-name-sort | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 2 instance | F5.1 | - (N below 3, not barriered) |
| N-dup-entity | 1 | 1 | no | S7 @ `1152a74346` | 1 instance, 2 not applicable | F7.2 | - (N below 3, not barriered) |
| N-late-try | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance | F1.5 | - (N below 3, not barriered) |
| N-euler-coupled | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F2.3 | - (N below 3, not barriered) |
| N-fit-integrator | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance, 1 not applicable | F4.2 | - (N below 3, not barriered) |
| N-clamp-range | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F4.1 | - (N below 3, not barriered) |
| N-markdown | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 2 instance | F8.1 | - (N below 3, not barriered) |
| N-service-icons | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F5.1 | - (N below 3, not barriered) |
| N-debug-swallow | 1 | 1 | no | S6 @ `6b65c9c4a8` | 3 guarded, 1 instance | F1.5 | - (N below 3, not barriered) |
| N-keyboard | 1 | 1 | no | S7 @ `1152a74346` | 3 guarded, 1 instance | F6.2 | - (N below 3, not barriered) |
| N-finally-return | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance, 2 not applicable | F9.2 | - (N below 3, not barriered) |
| N-step-grid | 1 | 1 | no | S7 @ `1152a74346` | 2 instance, 1 not applicable | F5.2 | - (N below 3, not barriered) |
| N-min-gap | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance, 1 not applicable | F3.3 | - (N below 3, not barriered) |
| N-service-clamp | 1 | 1 | no | S7 @ `1152a74346` | 1 guarded, 1 instance, 1 not applicable | F1.4 | - (N below 3, not barriered) |
| N-reap-lock | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 instance | F1.5 | - (N below 3, not barriered) |
| N-shared-config | 1 | 1 | no | S7 @ `1152a74346` | 1 instance | F7.1 | - (N below 3, not barriered) |
| N-staleness | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 2 instance, 2 not applicable | F4.1 | - (N below 3, not barriered) |
| N-menu | 1 | 1 | no | S7 @ `1152a74346` | 1 guarded, 1 instance | F5.2 | - (N below 3, not barriered) |
| N-structure-blind | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 6 instance, 1 not applicable | F10.4 | - (N below 3, not barriered) |
| N-language | 1 | 1 | no | S7 @ `1152a74346` | 4 instance | F6.4 | - (N below 3, not barriered) |
| N-escape | 1 | 1 | no | S6 @ `6b65c9c4a8` | 1 guarded, 1 instance | F5.1 | - (N below 3, not barriered) |
| N-availability | 1 | 1 | no | S7 @ `1152a74346` | 1 instance, 2 not applicable | F7.3 | - (N below 3, not barriered) |

## Owned files and borrow edges

| lane | name | thread model | owns |
|---|---|---|---|
| F1 | Coordinator cycle, state and clock | opus | coordinator.py, services.py, store.py, button.py, manual_plan.py, accuracy.py, external_heat.py, dhw_learning.py, tests/dst_checks.py, tests/open_meteo.py |
| F2 | Solver and plant model | opus | optimizer.py, pv.py, thermal_model.py |
| F3 | Persisted stores and price/weather feeds | opus | snapshots.py, curve_learning.py, comfort_learning.py, pump_arbiter.py, freq_control.py, defrost.py, legionella.py, boost.py, away.py, drift.py, disinfection.py, price_model.py, tariff.py, open_meteo.py, grid_fee.py, dhw_draws.py, ledger.py |
| F4 | Inputs, constants, sysid and flow-lift | opus | inputs.py, const.py, sysid.py, flow_lift.py, currency.py |
| F5 | Config flow and translated text | sonnet | config_flow.py, strings.json, translations/en.json, translations/sv.json, icons.json, quality_scale.yaml, quick_setup.py, modbus_prefill.py, topology.py, tests/config_flow_steps.py |
| F6 | Dashboard card | opus | www/heatpump-optimizer-card.js, tests/card.mjs, tests/card_rig.mjs, tests/card_drift.mjs, tests/card_browser.mjs |
| F7 | Entities | opus | sensor.py, climate.py, switch.py, entity.py, binary_sensor.py |
| F8 | User documentation | sonnet | README.md, docs/configuration.md, docs/setup.md, docs/how-it-works.md, docs/dashboard-card.md, docs/ecl110.md |
| F9 | Test pins for unpinned guards | sonnet | tests/finite_boundary.py, tests/nightly_ha.py |
| F10 | Gate, stub and ratchet infrastructure | opus | tests/hastub/**, tests/ha_contract.py, tests/replay.py, tests/stress.py, tests/stress_budgets.json, tests/env_drift.py, tests/closure.py, tests/derive_closures.sh, tests/deployment_shape.py, tests/doc_claims.py, tests/mutation_table.py, tests/mutation_budgets.json, tests/structure.py, tests/harness.py |
| F11 | Governance tooling and policy | opus | .claude/workflows/**, .github/**, CLAUDE.md, AGENTS.md, .claude/rules/**, .cursor/rules/**, .claude/settings.json, tools/audit/**, tools/release/**, docs/decisions/** |

## Proposed merge queue (priority among PRs that are ready: review `merge`, CI green, `after` edges merged; one merge at a time)

Ordered by dependency depth, then severity, then non-owner-gated first. The orchestrator may swap two adjacent PRs that share no file and no edge; it may not move a PR ahead of its `after`.

1. F2.1 (high, fixture) - get_current_action seams, two-zone comfort floor, PV margin, stale comments
2. F3.1 (high) - Stored instants: naive and future timestamps
3. F4.1 (high) - Input freshness and plausibility; flow-lift clamp
4. F7.1 (high) - Climate entity: hvac_action during boost, mode reads, away target
5. F5.1 (medium) - Translated text, icons and names (no config_flow.py)
6. F6.1 (medium) - Card layout, colour and hit targets (P9)
7. F8.1 (medium) - configuration.md: initial setup, entity count, services
8. F9.1 (medium) - Pins for deletable guards (I1), part 1
9. F11.1 (medium) - Governance parsers and enumerators (not code-owned)
10. F10.1 (low, fixture) - Home Assistant stub fidelity (P11) and its contracts
11. F1.1 (high) - DST wall-clock seams and the gate's clock
12. F2.2 (medium) - Interpreter-bound recomputation in the solve
13. F3.2 (medium) - Pump-duty arbiter and the frequency map
14. F4.2 (medium) - System identification: adoption gate, fit integrator, sizing (P5)
15. F6.2 (medium) - Keyboard route in the layout editor; stale comments; #1643 surviving mutants
16. F9.2 (medium) - Pins for deletable guards (I1), part 2; return inside finally
17. F11.2 (medium, tvofi) - Required-check boundaries (I3, owner-gated)
18. F8.2 (low) - Labels, pages and solver description
19. F1.2 (high) - Presence inferred from untouched defaults; DHW start state
20. F2.3 (medium, fixture) - Plant-model physics and the thrice-held inlet default
21. F3.3 (medium) - Learner stores and feed parsers
22. F8.3 (medium) - Setup promises, curve-bias figure, currency fallback, card version
23. F10.2 (medium, tvofi) - CPU gate blind spots; per-solve CPU budget
24. F11.3 (medium, tvofi) - Policy text: per-file caps, CLAUDE.md rule 1, verdict carry on merges-only moves; I3 barrier
25. F6.3 (barrier, tvofi) - P9 class barrier in the browser lane
26. F1.3 (high, fixture) - Cycle outcome: stale spot price, unfenced cycle calls, failures reported as success
27. F5.2 (medium) - Setup wizard and options UX
28. F7.2 (low) - Sensors: schedule count, duplicate entity, valve recommendation
29. F1.4 (medium) - Restart durability (barriered class) and store bounds
30. F1.5 (medium) - Cycle failures: swallowed errors, late try, reap, P6 defaults, defrost fold
31. F1.6 (medium) - Plausibility bounds and the P1 load-layer barrier
32. F2.4 (medium, fixture) - On/off pump threshold at both seams; multi-start seeds
33. F1.7 (medium, fixture) - Coordinator readers across lanes: loop CPU, auth, settlement scale
34. F7.3 (medium, tvofi) - Climate availability without an indoor thermometer (owner's ruling)
35. F1.8 (medium) - Currency and unit (P8) and entry identity
36. F10.3 (medium, tvofi) - Owned gate scripts: verdict pins, mutation inventory, child-process closures; I1 and P11 barriers
37. F6.4 (medium) - Language-aware setup text; raw-thermometer source for staleness gaps
38. F1.9 (barrier) - Persisted future instants in the coordinator; the class barrier
39. F1.10 (low, tvofi) - Class barriers P2, P3, P6; comment drift; boost test hook
40. F10.4 (low, tvofi) - Structural ratchet truth: dead members and uncounted helpers; I5 barrier
41. F11.4 (low, tvofi) - Class roster readers agree (I4 barrier); owed driver fixes
