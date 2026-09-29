# Round 9 fix plan (step E2)

Final plan for tvofi, 2026-09-26. Drafted by the E2 fix-plan designer seat (strongest model) and
finished once the seven Phase D sweeps (S1–S7) had landed; section 9 lists what the sweeps changed. The
fourteen round-9 RCA seats then reported, and section 10 lists what their results changed (the RCA fold,
2026-09-26; tvofi's asks from them are collected in `TVOFI-ASKS.md` beside this file). Sections 11
and 12 carry tvofi's 19:05Z rules: every seat resumable from git after a crash, and every role routed to
the cheapest feasible model. Section 13 applies tvofi's answers to all 35 asks (19:16Z), recorded card
by card in `TVOFI-ASKS.md`'s DECISIONS section, and lists wave 1. It
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
  ids travel with their canonical), all {n_inst} counted instances beyond them (the sweeps' and the RCA
  fold's, sections 9 and 10) and {n_latent} latent seams an RCA placed. tvofi (17:44Z): the PR count does
  not matter; the reasons for each PR are below.
- **Why not fewer.** `fixer.md` caps a PR at five findings and about 400 production lines, and PLAN
  §8.2 keeps that cap; a sweep instance counts toward it like a finding. So 145 findings need at least
  29 PRs. The rest come from three constraints: lanes own disjoint files, so a PR packs findings from
  one lane's files only and a lane's last PR is often part-full; {n_tvofi} PRs need tvofi and are kept apart so
  nothing else waits on them; and one PR (F6.3) is a class barrier alone, because P9's barrier lives in
  `tests/card_browser.mjs`, which is code-owned.
- **Why 41 at the sweeps (superseded by the next bullet).** S7 raised "persisted future instant trusted without bound" from 2 to 7, so it
  owes an RCA seat and a barrier. Four of its five new instances are in `coordinator.py`, which only F1
  owns, and the instruction is that a class's sweep instances travel with its barrier PR where the lane
  allows. No F1 PR has more than two free slots, and one of the two
  roomiest, F1.10, is tvofi-gated, which would make the instances wait on tvofi. So the four
  instances and the barrier are a new PR, **F1.9** (the old F1.9 is now F1.10). Keeping 40 would mean
  merging two unrelated card PRs (F6.2 with F6.4), which delays the keyboard fix and the #1643 mutant pins
  behind F1.8 for no gain; I did not.
- **Why 45 after the RCA fold (superseded by the next bullet).** Four PRs were added, each forced by the five-item cap or by
  owner-gating: **F2.5** (the recompute RCA found the class's largest member, `peak_cost_batch`, and a
  closure the sweep mis-disposed, while F2.2 is at five); **F6.1b** (the P9 RCA's grid found four
  instances, while F6.1 is at five); **F1.11** (the old F1.10 would carry the P2, P3 and P6 barriers
  together, several hundred test lines, so P2 and P6 moved to their own PR); **F11.5** (the RCA seats
  drafted policy changes and landed none; the approved drafts need a PR, and it is tvofi-gated, so it is
  last in its lane and nothing waits on it). F1.9 stayed, shrunk: the future-instant barrier moved to
  F3.1, and F1.9 keeps the one seam no bound fixes plus the regression tests.
- **Why {n_prs} after tvofi's answers (section 13).** Two PRs left and four arrived: F6.1b merged back
  into F6.1 (card D2, over the cap by recorded exception) and F7.3 dropped with D8-s2-01 refused (card
  C15); F9.3 (the P1 declared-domain barrier, card C1), F10.5 (the nightly kill-ledger writer, C5),
  F10.6 (the comparison-bound mutation operator, C6) and F11.6 (the verdict carry, C18, split from F11.3
  for the 400-line bound) are new.
- **Why not more.** Classes are merged into one PR wherever they share a file set and fit the cap; a
  class over the cap (P2 with 27, I5 with 19, I1 with 11, P1 with 9) is split into instance PRs by
  subsystem with its barrier in the last one (PLAN §8.2). Instances fill PRs that already held their
  class where a slot is free: F1.6 (P1's two latent seams), F6.1 (all four P9 instances, over the cap by tvofi's D2 exception), F2.2 (RC-sw1),
  F3.2 (FI-sw5's test), F4.2 (the new P5 instance, after D2-s4-02 moved to F4.1) and F1.9 (the
  future-instant tests); each is at five or under.

## 2. How the PRs were clustered

tvofi's order (13:04Z): class first, then shared file set, then fixer skill; owner-gated work in its
own PRs.

1. **Class first.** A class that fits one PR is one PR with its barrier (P5 in F4.2; the CPU-gate
   class in F10.2; the restart class in F1.4). A class whose instances sit in several lanes takes its
   barrier in a PR that waits on all of them (I5 in F10.4, I3 in F11.3, I4 in F11.4), unless its RCA
   measured the barrier's check not to read the later instances: P11's lands in F10.1 and the
   future-instant boundary in F3.1 (section 10), and the generator lists each such residual.
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
   `structure_budgets.json` re-recorded once at the hand-off; delivery rows one file per PR). The RCA fold
   adds two: `tools/audit/bugclasses.json`, where each barrier PR edits only its own class's entry, and the
   mutation ledger's `killed_by` rows.
4. **Then skill.** Lanes F5 (config flow and translated text), F8 (docs) and F9 (test pins) run on
   sonnet; everything else on the strongest model (tvofi 12:21Z).

The four fix-together sibling pairs DEDUP.md names each land in one PR: D12-s2-01 with D8-s1-03 in
**F2.4** (D12-s2-01 first, at both seams; D8-s1-03 then re-measures); D12-s1-01 with D12-s1-02 (merged
into D12-s3-01) in **F1.2**; D1-s5-01 with D1-s5-51 in **F4.1**; D8-s2-02 with D8-s2-03 in **F7.1**.
DEDUP's other "fix together" notes are honoured too (D1-s2-51/D1-s2-91 in F1.3; D7-s1-71/D5-s2-03 in
F2.3; D5-s1-01/D6-s2-01/D6-s2-02 in F8.1; D5-s1-05/D6-s1-02 in F8.2; the plausibility trio D1-s5-52 →
D1-s2-02, D1-s1-03 share F4.1's window and land in F1.6).

**Five findings are split across two PRs**, because their seams sit in two lanes' files; each closes
when its last PR merges, and the first PR's body says which finding it leaves open (its class issue is `Part of #N` there):

- D14-s4-01 (high, P7): its `get_current_action` seam in F2.1 (first, and short), everything else plus
  the DST tracer barrier in F1.1, which waits on F2.1.
- D5-s1-02: the quick-setup text in `en.json`/`sv.json` (an L2 extra seam) in F5.1, `docs/setup.md` in F8.3.
- D6-s2-03: the figure in `strings.json` (an L2 extra seam) in F5.1, the docs in F8.3.
- D14-s4-02 (P11 RCA): the stub half (freeze normalisation, `utcnow` under an aware freeze) in F10.1, with
  the P11 barrier; the replay half in F1.1, which waits on F10.1.
- D6-s2-05 (I5 RCA): the `simulate_plan` field list in F8.1; the two service seams the I5 RCA found in F8.3.

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
- **RCA seats**: {n_rca}, one per `rca: true` class; fourteen ran before fixing (tvofi, 17:44Z) and
  have reported, and the fifteenth (the restart class) is RC2's, merged. Each named its barrier's form
  and left a prototype branch; the fixer of the PR that lands the barrier cherry-picks it (section 5).
- **Startable at once (wave 1):** {wave1}: {n_wave1} threads, one per lane (the PRs with no `after`
  edge unmet; the table and `WAVE1.json` are in section 13).

## 4. What needs tvofi, and why (answerable in one pass)

**Owner-gated PRs ({n_tvofi})** — each is its own PR so nothing else waits on it (generated from the
plan data; the old F1.10 is no longer gated: no barrier needs `tests/harness.py` after the RCA fold):

| PR | why tvofi |
|---|---|
{tvofi_rows}

**The RCA asks are answered.** tvofi answered all 35 at 19:16Z; `TVOFI-ASKS.md`'s DECISIONS section
records each card's answer, whether it differs from the recommendation, and where it is applied
(section 13). What the owner-gated PRs above still need is tvofi's approving review at their heads,
which code ownership and budget-raise-gate require anyway, and, for {n_blocked} of them, an action:

| PR | blocked on |
|---|---|
{blocked_rows}

**Other asks that may arrive during the wave:**
- Any budget raise a fixer hits (most likely in F1, whose coordinator class sits at zero headroom on several
  metrics; each F1 PR pays for its lines first).
- Any RCA seat that finds no barrier within "The bound" asks tvofi for a ruling rather than recording a
  refusal (PLAN §8.3).
- D0-s2-02 (F2.4) may end as a recorded refusal priced in money and CPU, standing on the #1294 refusal;
  that is the fixer's to record, reported to tvofi.

## 5. RCA seats ({n_rca}, all on the strongest model)

All fourteen reported (write-ups under `/mnt/project-files/audit-r9/rca/<slug>/RCA.md`; the restart
class is RC2's). Each row names the prototype the barrier PR cherry-picks, whether its files are
code-owned or policy, and its line estimate.

| class | N judge | N sweep | N final | process state | barrier lands in | prototype | code-owned / policy | lines |
|---|---|---|---|---|---|---|---|---|
{rca_rows}

N final is judged findings plus counted instances (PLAN §7). Each barrier PR comes after every PR
holding an instance of its class, except the residual instances its RCA measured the barrier not to
read; the generator refuses the plan otherwise and prints the residuals.

**Barrier forms, as the seats chose them:**

{rca_forms}

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
| The RCA seats' carries ({n_carries}, `finding-propagation.md`), each delivered into its destination's roster brief and lane brief | section 10 |

## 7. Findings I could not place

None. Every one of the 145 survivors is placed in a PR or refused by tvofi, and every one of the {n_inst} counted instances and the {n_latent} latent seams maps to a PR (tables below). FI-sw3 (F1.9) ends in tvofi's decision (card C13: treated as an outage). Refused by tvofi, with no PR:

| finding | class | disposition |
|---|---|---|
{refused_rows}

D11-s1-04 ends in a refusal in `budget_raise_gate.py` (card C17, F11.2), D13-s1-02 is built (card C18,
F11.6), and D0-s2-02 may still end as a recorded refusal priced in money and CPU (F2.4).

## 8. Merge order, stamps and throughput

- **One merge at a time**, in the proposed queue below, which respects every `after` edge. When two PRs
  are ready together, the one on the longer remaining chain goes first: **F1 is the critical path**
  (eleven PRs, the coordinator), then F2.
- **Critical path (inferred, not measured):** {chain}, {chain_len} PRs deep (the longest chain of
  `after` edges, derived by the generator). The high findings all sit in the first waves: D14-s4-01
  (F2.1, F1.1), D1-s3-01 (F3.1), D1-s5-52 (F4.1), D8-s2-02 (F7.1), D12-s1-01 (F1.2), D2-s3-01 (F1.3).
- **Stamps.** The plan's standing rule holds: no new branch is cut between a fixture-mover's merge and
  its stamp. PRs marked fixture (drift plausible): F1.3, F1.7, F1.10, F2.1, F2.3, F2.4, F2.5, F10.1. If one of them
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
  with the P1 barrier. *Superseded (section 10): not store-reachable, N back to 9.*
- **P9** (S5): 4 → 5. The new instance is the chart's SVG axis number/unit label overlap (P9-sw1, F6.1).
  *Superseded (section 10): P9-sw1 is a box-metric artefact; N is 8 with the RCA's four.*
  The keyboard route is **not** a counted instance: S5 ran with the keyboard cells off and records it as
  exposure, so it is a check for F6.2 (below), not an instance.
- **avoidable interpreter-bound recomputation** (S5): 4 → 5. `cycling_penalty_batch` (RC-sw1, F2.2); the
  other ThermalParameters properties S5 found are folded into D9-s1-71.
- **persisted future instant trusted without bound** (S7): 2 → 7, now `rca: true` with its own RCA seat
  and barrier. The five instances: four in `coordinator.py` (fuse-advisor cooldown, heavy-snow damping,
  `_detect_outage`, and the lower-confidence immersion recency) in the new F1.9 with the barrier;
  `pump_arbiter.py`'s `hold()` echo grace in F3.2. *Superseded (section 10): the barrier is in F3.1,
  N is 8 with the legionella seam.*
- **P5** (S5): stays 3 (*section 10: 4 after the RCA*). `async_update_thermal_params` writing two gated parameters with no gate is a
  lead, not an instance: S5 disposed it not applicable, since there is no gate to key wrong.
- Every other class kept its N; a few PRs gained a borrow to reach a seam their finding already owned
  (F1.8 borrows `price_model.py` for P8's money-code seam).

**Barrier order corrected.** The draft stated that a barrier lands after every instance PR of its
class but did not check it. The generator now does, and it refused five barriers in the draft; each
moved to a PR that waits on all its class's instance PRs:

- I5: F8.3 → **F10.4** (instances in F2.1, F2.3, F6.2, F1.10 and F11.3 as well as F8); F10.4 now waits on F11.3,
  and F8.3 no longer borrows `tests/doc_claims.py`.
- P11: F10.1 → **F10.3** (instances in F1.1, F1.7 and F8.3); F10.3 now waits on F1.7 and edits `tests/ha_contract.py`.
  *Superseded (section 10): back to F10.1; its check reads none of those three.*
- I1: F10.3 stays, and now waits on F9.2 (the last I1 pin PR).
- I3: F11.2 → **F11.3** (D11-s2-01 is an I3 instance in F11.3, and the barrier's shape lives in its files).
- I4: F11.4 stays, and now waits on F10.4 (D7-s3-02, the dead_methods census), so F11.4 is the round's last PR.

The draft's critical path was 13 PRs deep and is now {chain_len}: F11.4 now follows F10.4. The new F1.9
sits between F1.8 and F1.10 at the depth F6.4 already had there, so it adds none.

Leads placed as instructions, not instances:

{leads}

Ledger notes (not RCA triggers this round; no PR unless a finding already covers them):

{ledger_notes}

## 10. The RCA fold (2026-09-26)

tvofi (17:44Z) asked for the RCA seats before fixing, with any cost-effective countermeasure folded
into this plan. All fourteen reported; every barrier's prototype branch was read back with
`git ls-remote`. The orchestrator's rulings on their plan folds are applied as follows.

**PR set** (45 at the fold; section 13 has the current set): new F2.5, F6.1b, F1.11 and F11.5 (section 1; F6.1b merged back into F6.1 at section 13); F1.9 shrunk; D2-s4-02 moved from
F4.2 to F4.1.

**Barrier moves.**
- **Future instant → F3.1** (was F1.9). The store-load boundary is the fix for F3.1's own class
  findings and closes FI-sw1, FI-sw2, FI-sw4, FI-sw5 and the legionella seam in one place. F3.1 borrows
  `store.py` and two lines of `coordinator.py` from F1 and `tests/finite_boundary.py` from F9; F1.1 and
  F9.1 now wait on F3.1, so every F1 and F9 PR follows it. F1.9 keeps the FI-sw3 decision and the
  regression tests, after F3.1; F3.2 keeps FI-sw5's test.
- **The `store.py` order.** P1's barrier (the magnitude drop, F1.6) and the instant bound (F3.1) touch
  the same sanitising walk. Lane ownership stays (F1 owns `store.py`; F3.1 borrows it), and the edge
  orders them: F3.1 first, and F1.6 (after F3.3, after F3.2, after F3.1) extends the same predicate.
  F1.4, which also edits `store.py`, follows F3.1 through F1.1.
- **P11 → F10.1** (was F10.3). F10.3 drops P11, `tests/ha_contract.py` and its edges on F1.7 and F8.3;
  F1.1 gains an edge on F10.1; F1.7 borrows `tests/ha_contract.py` for its own contract.
- **Solve cost.** F2.5 carries `peak_cost_batch` (RC-rca1) and the terminal twin (RC-rca2), after
  F2.2 and F3.3; F10.2 now waits on F2.5.
- **P2 and P6 → F1.11**, **P3 → F1.10**. Neither is tvofi-gated: the P6 RCA showed the boost test hook
  can be dropped without `tests/harness.py`, and no other barrier needs it.
- **I5** is split: the `doc_claims.py` arms in F10.4, the `policy_lint.mjs` quoted-line pass in F11.3.
- **P9**: F6.3 after F6.1 (through F6.2); the grid's browser cost is scoped to card-surface diffs
  through the scoped gate, `main` forced full (orchestrator's ruling).

**N changes** (issue drafts and `INDEX.json` follow): P1 11 → 9 (P1-sw1, P1-sw2 not store-reachable);
P5 3 → 4 (the half slab mass); P9 5 → 8 (P9-sw1 out; three new and one candidate in); the recompute
class 5 → 7 (`peak_cost_batch`, the terminal closure); the future-instant class 7 → 8 (legionella).
Latent seams (P1-rca1, P1-rca2) fill F1.6's freed slots and are not counted.

**Carries** ({n_carries}), delivered into each destination's roster brief (`carry`) and lane brief:

| to PR | from RCA | carry |
|---|---|---|
{carry_rows}

## 11. Resumability (tvofi, 2026-09-26 19:05Z)

tvofi: *"Make sure that the plan can always be resumed either by local or cloud threads and that any work
lost in threads, seats and subagents is minimal should this session crash."* The plan meets it with three
records, each on a remote branch or the shared project files, so no crash loses more than the last step.

1. **The seat's branch.** Every seat (fixer, reviewer, RCA, runner, subagent) commits and pushes to its
   remote handoff branch at each step boundary — failing test written, fix green, body drafted — and at
   least every ~30 minutes of work; it never holds unpushed work across a long run (a gate or stress run,
   a subagent), and reads `git ls-remote` back after each push. Fixer: `handoff/<lane topic>-<k>` (the
   roster's `resume.branch`). Reviewer: the same with `-review`. A runner or subagent pushes its output,
   or hands it to the seat that pushes, before it reports.
2. **The resume note.** On that branch, `handoff/round9/fix/resume/<PR-id>.md` (a review:
   `<PR-id>-review.md`): last completed step, next step, `branch@commit`, merge base, open questions,
   what is waiting on whom. Updated in the same commit as every push. For in-flight state it outranks the
   roster, which the orchestrator (or a sonnet record seat) brings up to date at each hand-off and merge.
3. **The run log.** One dated line per milestone (branch cut, failing test, green, body drafted, hand-off,
   verdict, merge) in `/mnt/project-files/audit-r9/RESUME.md`, and the same line in its mirror,
   `handoff/round9/RESUME.md` on `handoff/audit-r9-plan` (fetch, append, commit, push; re-fetch and
   re-append on a non-fast-forward; never force). The Mac cannot read `/mnt/project-files`, so the mirror
   is what makes the Mac able to resume from git alone; a Mac seat writes the mirror only and the
   orchestrator copies its lines into the `/mnt` log at its next pass.

**Picking up any PR.** The roster entry `R9-<PR-id>` in `.claude/workflows/wave-r9-groups.json` (on
`handoff/audit-r9-fixplan`) carries a concrete `resume` object: `branch`, `commit`, `last_step`,
`next_step`, `note_file`, `review_branch`, `plan` (the lane brief section and this file), `log`, and two
pickup recipes:

- **Cloud seat** (`pickup_cloud`): `git fetch origin <branch>`; if it exists, `git worktree add --detach
  $S/<lane topic>/wt FETCH_HEAD`, read the note, check its commit against the fetched head (if the branch
  is ahead, trust the branch and its log), `git merge origin/main` if main moved and re-run `fixer.md`
  steps 2-8, then continue at the note's next step. If the branch does not exist, cut from origin/main and
  start at `fixer.md` step 1. Plan and briefs from `handoff/audit-r9-fixplan`; the log from `/mnt`.
- **Mac seat** (`pickup_local`): the same git commands from the Mac checkout, with the plan, briefs and
  roster from `handoff/audit-r9-fixplan` and the log from `handoff/audit-r9-plan`'s mirror; nothing it
  needs lives only under `/mnt`.

A crashed seat is restarted from its branch and resume note, never from scratch. A crashed orchestrator is
restarted from the mirror log, the roster and `git ls-remote 'refs/heads/handoff/r9-*'`, which together
name every branch in flight and its last pushed step. This plan itself follows the rule: its generator
sources are committed beside it (`handoff/round9/fix/src/`), and each rebuild is pushed.

## 12. Model routing (tvofi, 2026-09-26 19:05Z)

tvofi: *"Work that is feasible for sonnet and haiku should be routed as such."* Each role goes to the
cheapest model that can do it; the roster's per-PR `model` object (`fixer`, `fixer_why`, `reviewer`,
`rca`, `runner`, `record`) and each lane brief name them, and `gen.py` refuses a strongest-model fixer
without a reason, or a barrier PR routed below the strongest model.

| role | model |
|---|---|
{role_rows}

Fixers per PR ({n_sonnet} sonnet, {n_opus} strongest; no fixer is haiku, because every fix owes a
failing test and a mutation proof that need judgement):

| PR | fixer | why |
|---|---|---|
{model_rows}

## 13. tvofi's answers (2026-09-26 19:16Z) and wave 1

tvofi answered every card (message `cmsg_01EL5jLi4rokGBbkaevYXSJV6CQVMDN96YfVMTcN5QGSx2`);
`TVOFI-ASKS.md`'s DECISIONS section records each answer with its card. Where an answer differs from the
orchestrator's recommendation it is applied as given:

- **A1-A9 approved**, A9 included: all nine drafts land in F11.5 (A2: A1 rides F11.5). **B1-B5 allowed**,
  each at its measured value; B2's valve rows cover only the cheaper members C9 picks. Every raise still
  merges only on tvofi's approving review at its head (budget-raise-gate).
- **C1, domain table** → new **F9.3**, the P1 declared-domain barrier (strongest model), after F1.6; it
  covers D1-s3-06, D1-s4-01, D1-s5-02 and D1-s4-03 and the fields rca/p1 names, on the design basis of
  rca/p1/RCA.md's residual section. F1.6's cap was full, so it is its own PR.
- **C5, build** → new **F10.5**, the nightly mutation-kill ledger writer, in the gate/infra lane and
  gated on tvofi; its new writer identity (decision 0011) is a Mac/tvofi setup action, not a fixer's.
- **C6, commission** → new **F10.6**, the comparison-bound mutation operator, its cost measured first.
- **C9, cheaper** → F10.2 samples cheaper valve-axis members, and records the residual blind spot (a
  regression only a throttling valve's winter two-zone path exercises).
- **C10, derive** → F11.3's field-coverage barrier derives the governance-check set from `CHECKS`,
  `codeowners_gap.py` and stamp rule 4.
- **C15, keep** → A3(e) stands, D8-s2-01 is refused against it, F7.3 is dropped. **C16, leave** →
  D11-s1-01 is refused by tvofi; no policy edit. **C17, refusal** → `budget_raise_gate.py` in F11.2.
- **C18, build** → new **F11.6**, the diff-equivalence verdict carry (D13-s1-02), split from F11.3.
- **D2, enlarge F6.1** → F6.1b merged back; F6.1 is over `fixer.md`'s five-item cap by tvofi's explicit
  choice, recorded in its brief and accepted by `gen.py` only through its exception list:

| PR | cap exception |
|---|---|
{cap_rows}

- C2, C3, C4, C7, C8, C11, C12, C13, C14, D1 and D3 are as recommended (C13: outage decides F1.9).

**Owner-gated PRs** ({n_tvofi}): {tvofi_list}.

**Wave 1** ({n_wave1} PRs, one per lane, none with an unmet `after` edge; also
`/mnt/project-files/audit-r9/fix/WAVE1.json` and `handoff/round9/WAVE1.json`):

| PR | lane | fixer | branch | brief | tvofi |
|---|---|---|---|---|---|
{wave1_rows}

Lanes with no PR in wave 1: {wave1_absent}.

---