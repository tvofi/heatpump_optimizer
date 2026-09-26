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

- **{n_prs} PRs in 11 lanes**, covering all 145 surviving findings (148 canonical less 3 refuted; the 7 merged
  ids travel with their canonical) and all {n_inst} sweep-confirmed instances beyond them (section 9).
  One over tvofi's 15–40 range; the reason is the next bullet but one.
- **Why not fewer.** `fixer.md` caps a PR at five findings and about 400 production lines, and PLAN
  §8.2 keeps that cap; a sweep instance counts toward it like a finding. So 145 findings need at least
  29 PRs. The rest come from three constraints: lanes own disjoint files, so a PR packs findings from
  one lane's files only and a lane's last PR is often part-full; {n_tvofi} PRs need tvofi and are kept apart so
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
3. **Borrowing, not sharing.** {n_borrow} PRs must edit a file another lane owns (a fix-together sibling
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
- **RCA seats**: {n_rca}, one per `rca: true` class (the fifteenth, for the future-instant class, is new at Phase D), each on the strongest model in its own thread, started
  beside the PR named in section 5 (not inside it). They name each barrier's form; the fixer of the PR
  that lands the barrier builds it.
- **Startable at once (wave 1):** {wave1} — ten
  threads, one per lane, which fills the ~10 cloud containers. F1's thread starts with F1.1 as soon as
  F2.1 merges (F2.1 is deliberately small), so the eleventh thread is not needed until then.

## 4. What needs tvofi, and why (answerable in one pass)

**Owner-gated PRs ({n_tvofi})** — each is its own PR so nothing else waits on it:

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

## 5. RCA seats ({n_rca}, all on the strongest model)

| class | N judge | N final | starts beside | barrier lands in | barrier proposal (the sweep's; the seat names the form) |
|---|---|---|---|---|---|
{rca_rows}

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

None. Every one of the 145 survivors and every one of the {n_inst} sweep instances maps to a PR (tables below). Five may end without a code change,
by design: D8-s2-01 (tvofi's A3(e) ruling), D11-s1-01 (a ruleset setting tvofi changes; the PR records it),
D11-s1-04 (tvofi's identity decision), D13-s1-02 (tvofi decides whether to build the carry), and D0-s2-02
(a recorded refusal is a legitimate outcome).

## 8. Merge order, stamps and throughput

- **One merge at a time**, in the proposed queue below, which respects every `after` edge. When two PRs
  are ready together, the one on the longer remaining chain goes first: **F1 is the critical path**
  (ten PRs, the coordinator), then F2.
- **Critical path (inferred, not measured):** {chain}, {chain_len} PRs deep (the longest chain of
  `after` edges, derived by the generator). The high findings all sit in the first waves: D14-s4-01
  (F2.1, F1.1), D1-s3-01 (F3.1), D1-s5-52 (F4.1), D8-s2-02 (F7.1), D12-s1-01 (F1.2), D2-s3-01 (F1.3).
- **Stamps.** The plan's standing rule holds: no new branch is cut between a fixture-mover's merge and
  its stamp. PRs marked fixture (drift plausible): F1.3, F1.7, F2.1, F2.3, F2.4, F10.1. If one of them
  merges with claimed drift, the orchestrator stamps before the next branch is cut; otherwise, proposed
  stamp points are (a) after the high-severity set above has merged, (b) after F1.6 (P1 barrier), and
  (c) after {last_pr}, the last PR.
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

The draft's critical path was 13 PRs deep and is now {chain_len}: F11.4 now follows F10.4. The new F1.9
sits between F1.8 and F1.10 at the depth F6.4 already had there, so it adds none.

Leads placed as instructions, not instances:

{leads}

Ledger notes (not RCA triggers this round; no PR unless a finding already covers them):

{ledger_notes}

---
