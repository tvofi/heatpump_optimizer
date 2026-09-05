# The open-issues program, September 2026

Written 2026-09-03 against `main` at `4b6e076` (v6.3.9, eight merges
unstamped). This is the worklist for every issue open at that moment — 61 of
them — planned in one pass after three sessions stood down and handed over
(`tvofi-claude-09` and `tvofi-claude-40` on #201, the latter also in
`docs/handover-2026-09-03.md`; `cloud-ratchet` is one-way).

It supersedes `docs/plan-open-issues.md`, which covered #86–#101 and is
complete. The audit register stays `docs/audit-2026-09.md`; this file is the
delivery plan, that file is the evidence.

**Session:** `tvofi-claude-web`, label `owner:claude-web`, branch prefix
`claude-web/` — an identity, not a runner; see Model routing, every seat is a
Cursor Task agent. Owner decisions recorded 2026-09-03: full merge-and-stamp
authority under the standing protocol; #372, #373 and #374 released from
`owner:cloud-ratchet` to this session on the owner's instruction; the triage
judge settles the money-attached questions with numbers; the #193
decomposition program runs to its end state.

## Why this order

Five principles decide it, each a measured fact rather than a preference.

1. **Instruments before the fixes they judge.** `structure.py --record` cannot
   tell an improvement from a regression (#370), headroom never fails (#350),
   `duplication_blocks` has never been able to fire (#369), the ratchet has no
   method-level metric (#374), `stamp.py --self-test` has never run (#372) and
   the closure table contradicts the INERT list (#357). Every later wave is
   judged by these, so they land first.
2. **Budget-table writers never run in parallel.** `tests/structure_budgets.json`
   is rewritten by six separate pieces of work; one at a time, each rebasing
   on the last.
3. **A behaviour fix in a region lands before that region's move PR.** A fix
   inside relocated lines is reverted silently by the move's rebase, with no
   conflict and no failing test — #324 nearly lost that way inside #340.
4. **Fixture-movers share a fork and a stamp**, and a mover never claims a
   fixture that is already `may-drift` (`env_drift.may_drift_error` refuses
   the pair).
5. **Measure-first issues are triaged, not coded.** Eight close on a number;
   nine are re-scoped before a fixer is spent on them.

## Delivery status

Updated as the program lands; each row names the release that carried it.
Where this table and a wave body disagree, this table is the truth.

| Wave | Scope | Issues | Release | Status |
|---|---|---|---|---|
| 0 | stamp REST fallback (#376); then #367, #368 | #364, #282 | **v6.3.10** | **done** — all three merged, both reviews `merge`, tag `d7fa97f`, 0 unstamped |
| triage A | closed or re-scoped on a measured number | #197 #233 closed; #195 #244 #325 #334 re-scoped | — | **done** |
| 1a | the stress ruler, alone on an idle box | #346 | v6.3.11 | **done** — W1-G7 merged PR #378 (`291ae76`), 0 unstamped |
| triage B1 | read-only judges, run beside the ruler | #281 #225 closed; #303 #224 #193 re-scoped | — | **done** |
| triage B2 | solver, suite, browser and timing judges | #304 #258 re-scoped; #242 weakened to a structural zero; **#291 closed** (keep `_MULTI_START_SOLVES=4`); **#232 scoped** (smooth top-k alone → W3-G1) | — | **done** |
| 1b half I | gate instruments, suite gaps, ratchet, entity pins | 16 issues in 7 groups: #369 #370 (W1-G1), #350 #374 (W1-G2), #372 #357 (W1-G3), #373 (W1-G4), #334 (W1-G5), #247–#252 (W1-G10), #246 #251 #395 (W1-G11) | **v6.3.12** (tag `84a27b6`) | **done and released, 2026-09-04** — all seven groups merged, issues closed: PR #383, #406, #397, #384, #386, #385, #402 (merge SHAs in `.claude/workflows/wave-1b-groups.json`, each group's `resume.merge_sha`). `main` green after every merge, head `841fe0f`, stamped `84a27b6`. Five more PRs landed in the same run with no tracked issue of their own — #396 (roster/plan truth-up), #399 (the #387 coverage-floor backstop), #407 (operational docs), #409 (the ratchet-raise policy), #410 (claim priority) |
| 1b half II | card contrast/geometry, coordinator loaders, wood_share, may-drift partition, layout-editor recovery | 12 issues in 8 groups: #288 (W1-G6), #238 (W1-G8), #260 #261 #263 #266 (W1-G12), #262 #258 (W1-G13), #403 (W1-G16, added 2026-09-04), #265 (W1-G14), #254 (W1-G15), #245 (W1-G9) | **v6.3.13** (tag `f94ae13`) | **done and released, 2026-09-05** — all eight groups merged, issues closed: PR #419 (`7cc75a1`, W1-G6/#288), #421 (`a7c1e54`, W1-G8/#238), #424 (`47ded95`, W1-G14/#265), #427 (`598c83d`, W1-G15/#254), #431 (`cabcce1`, W1-G9/#245), #428 (`6bee53f`, W1-G12/#260 #261 #263 #266), #432 (`1801b76`, W1-G13/#262 #258), #433 (`ac35bf8`, W1-G16/#403). Record/tooling since v6.3.12 stamp: #414/#398, #415, #417, #418, #416/#411, #420, #426, #413; inherited-card-claims fix `7044a27` before stamp. Stamped `f94ae13`, 0 unstamped |
| — | **#387, the blocker**: the basin coverage floor is runner-dependent | #387 | v6.3.12 | **fixed** — merged as `32f309f` (PR #388); sixth acceptance criterion ruled (comment 5541519696): the WORK-channel stale-cheap downgrade is kept as necessary to the `env_drift` shape, and the coverage floor's strictness is restored by a follow-up PR that hard-codes it |
| 2 | coordinator lifecycle, learners, options grouping | #236 #237 #240 #239 #243 #283 #284 #279 #278 #277 #244 #325 | **v6.3.13** (tag `f94ae13`) | **W2-G1 + W2-G2 + W2-G6 + W2-G7 merged, 2026-09-05** — PR #437 @ `44a6351` (#236 #237 #240), PR #440 @ `90c71c4` (#239 #243, review `merge` 5550082479), PR #438 @ `e1a14f9` (#280), PR #436 @ `3c141d7` (#198). G2 tightened `coordinator_loc`/`max_class_loc` 10420 → **10418**, `max_cc` 87 → 86, `max_method_loc` 540 → 538. G1's owner-confirmed raise still binds the other rows (attrs 178, methods 255, multiassigned 136, cut_views 121, internal_call_edges 374, cut_grid 234). Next seat **W2-G3** (#283 first, then #284) |
| 3 | solver, DHW planner, GIL process route | #232 #234 #289 #290 #199 | v6.3.13 | pending — **W3-G4 is struck**, #242 has no admissible formula |
| 4 | the #193 decomposition programme, S0–S13 | #193 #223 #224 #225, and **#304 as S11's precursor** | one per stage | pending |
| 5 | typing lane, and the coverage deficit #195 raised | #303 #195 | per tranche | pending — **#304 moves ahead of S11**, see below |

v6.3.12 is stamped at the Wave-1b/half-I boundary as a **gate and test-hardening release** — not for the accumulated no-op merges alone, and not by waiting for a runtime fix that half I will not produce, because half I is entirely test, docs and tooling.

### Wave 1b, half I delivered 2026-09-04

Twelve PRs merged in sequence, `main` green after each, ending at `841fe0f`: #383 (W1-G1, #369 #370), #385 (W1-G10, #247–#252), #396 (truth-up), #384 (W1-G4, #373), #386 (W1-G5, #334), #397 (W1-G3, #372 #357), #399 (the #387 coverage-floor backstop), #402 (W1-G11, #246 #251 #395), #407 (operational docs), #409 (the ratchet-raise policy), #410 (the claim priority), #406 (W1-G2, #350 #374). **Released**: `v6.3.12` is tagged at `84a27b6f21690edcd340c6d74ff303c8e0774180`, now `origin/main`.

Half II (`.claude/workflows/wave-1b-groups.json`) started 2026-09-04 and completed 2026-09-05. **Released**: `v6.3.13` tagged at `f94ae13a75ed58ab53b70b5dbb13786c1c081a4c`, 2026-09-05. Eight fixer groups merged in sequence, `main` green after each; record PR #433 at `3bcea26`, inherited-card-claims fix `7044a27`, then stamp. Merge SHAs in the roster's `resume.merge_sha` fields. Record/tooling since v6.3.12: #414/#398, #415, #417, #418, #416/#411 (Wave 2 prerequisite), #420 (stress closure 64→22), #426 (W2-G2 citation re-anchor), #413 (brief corrections, W1-G16 added).

### The #387 blocker, 2026-09-04

**Fixed 2026-09-04, merged as `32f309f` (PR #388), released under the v6.3.12 framing decision above.** The reasoning below is kept because it is what the fix rests on, including the "one CI runner is not the fleet" lesson.

`main` is red on roughly half of all merges and the v6.3.12 stamp is blocked
behind it, from a regression this programme itself introduced in #346 / PR #378
and released as v6.3.11. Every push to `main` forces `GATE_SCOPE=full`, so
`tests/stress.py` runs on every merge; its coverage check demands **≥ 40 of 51**
scenarios land in a *recorded* solver basin, and on a runner whose basins are not
the recorded set it gets **29**.

Exactly 22 entries in `tests/stress_budgets.json` carry an `alt_basins` list, and
exactly those 22 flip together — one cause (the CPU model and its BLAS kernels
choosing the multi-start basin), one cohort. The floor was sized on the
assumption in its own comment that "a third platform may hold a third basin *for
some scenario*", i.e. that the misses are per-scenario and independent, leaving
eleven scenarios of slack. They are not independent. Four full-scope pushes after
#378: two green, two red, on commits differing only in INERT paths.

The owner chose **the `env_drift` shape** — capture each scenario's solver work
twice in one run, tree and merge base, compare computed against computed, no
basin table — at an accepted **≈ +500 s** on full-scope runs, and chose to fix it
**alone before anything else merges**. Recording the observed basins was rejected
as a treadmill (the `ubuntu-latest` fleet is heterogeneous and not enumerable, so
each new runner model contributes another basin for all 22); lowering the floor
was rejected as discarding what #346 existed to buy.

The general lesson, which the remaining gate-instrument groups are now reviewed
against: **one CI runner is not the fleet.** #378's reviewer asked exactly the
right question — whether a 2× regression is still caught on a machine whose
basins are not the recorded set — and the answer was measured on a single runner
and generalised.

### What triage changed, 2026-09-04 (batch B2)

Three read-only judges, run on this idle box (`load1` 0.17–0.58, `thread_factor` 1.00) at
`291ae76`. Two of the three overturned a brief this plan had already written, so the
corrected version is recorded here as well as on the issues.

- **#258 is re-scoped, and W1-G13's brief was wrong.** #333 did fix the clipping half:
  `units_with_ink_on_top_row` **12/12 → 0/12**. But its `uy` clamp traded the clipping for a
  new ink collision — the value-axis unit and the top tick of its own axis overlap by
  **1.00–1.25 px vertically and 4.0–8.5 px horizontally** on every tile that engages the
  font floor, **9 of 13** measurable pairs, leave-one-out **9 of 9**. This plan's hypothesis
  (a horizontal right-axis unit at `ux = x + 5` running past the viewBox) is **refuted**:
  right-edge headroom is −21.5 to −80.7 viewBox units and `ink_at_right_col` is false in
  every arm. The residual is vertical, not horizontal, and W1-G13's brief has been rewritten
  to say so. The finder's `card_geometry.mjs` is **void** for this row — its
  `text_overlap_pairs` reads 941 before and 941 after a perturbation that takes the collision
  9 → 0. The measured fix is `plotT = Math.max(MARGIN.top * marginScale, font * 1.45)` plus
  the `uy` offset 4 → 5.2; raising `plotT` alone does not work because `uy` tracks it.
  **No committed check can see this defect**: the DOM stub returns a constant 900×400 rect so
  the font floor never engages, the browser lane measures fonts and hit targets and never
  label proximity, and CI run 33829697839 at `291ae76` is green with the defect present. The
  fixer's failing test must therefore be a real-Chromium proximity check in the committed
  browser lane, or the fix ships without a witness.
- **#304 is re-scoped to 21 named statements, and its mechanism is refuted.**
  `config_flow.py` measures **96.2 %** (547 statements, 21 missed) — the third independent
  measurement to land on that figure, across two Python versions and two coverage cores. The
  body's mechanism (“no test submits `async_step_user` with input”) is false:
  `tests/config_flow_steps.py` is unconditional in `run.sh` and drives all three token
  verdicts plus `create_entry` through the real validation path, 89 checks passing. What made
  the gap look open was the frozen `coverage_suite.sh`, whose hand-typed `SCRIPTS` list omits
  that script — the same instrument-rot class as #334. All 21 residual statements are
  reachable by extending the existing harness with **no production change**; the largest
  single bite is 6 of 21, one repeated `return vol.Optional(key, default=existing)` idiom
  across six options pages.
  **Sequencing consequence:** #304 lands *before* the #223 registry stage, not in
  Wave 5. (That stage is numbered S11 here and S10 in #193's own stage list; the
  issue number is the stable reference, not the stage number.) #223 rewrites
  exactly those six options pages into a registry, so the coverage extension is the witness
  S11 needs, and writing it afterwards would mean writing it against code that has already
  moved.
- **#242 is weakened to a structural zero, and W3-G4 is struck.** The derivation spike
  returned **no admissible candidate**, and the obstruction is analytic rather than a
  coefficient that needs tuning. The base curve's log-slope budget is **+0.03030/K at 0 °C
  and exactly 0 above +27 °C**, while any ratio anchored on `(T_ref − T_out)` contributes
  **−0.01429/K at 0 °C, −0.04667/K at 20 °C** and diverges as `T_out → 35 °C`. The 0.0000 SEK
  plan consequence is therefore structural, not a sampling artefact: **189,882 Carnot-branch
  calls** across all nine shipped cells, every one at `T_out ∈ [−16, −8] °C`, against a
  coldest turnover of **+9.96 °C** — a 17.96 K margin. Wave 3 loses its fourth group; the
  physics half of the issue stands as verified and documented.

### What triage changed, 2026-09-03

The judges overturned this plan three times, which is what they are for. Recorded here
because the corrected version is what the waves now execute; the full numbers are in the
judge comments on each issue and summarised on #201.

- **#195 was not superseded and is now fix work.** #304's judge comment is aggregates, not
  the per-module table #195 asked for, and the only committed table on main is the stale
  88.4 % artefact. Re-measured: **89.7 %, 23 of 48 modules under the 95 % bar, and
  `coordinator.py` alone is 789 of the 1,338 missed statements** — 59 % of the deficit, so
  its half sequences behind the #193 seams. The leave-one-out is the planning fact:
  `validate`, `edge`, `backtest`, `optimality` and `plan_view` each move the total **0.0
  points**, so coverage cannot be bought with end-to-end scripts.
- **#325 is not an accepted limit.** The settle hour buys the identifiability — discrimination
  0.036 (below its own null floor) to **0.288** — but only if the settle hour's real delivered
  power is recorded. `sysid.step()` hard-codes 0 kW, and admitting those rows unchanged makes
  it *worse*: 0.012, with a −0.064 UA bias on an honest install. Record the power first,
  widen the filter second.
- **#334's residue was inverted.** `D6/claims.py` is repaired; **`D9/d9lib.py` is the one still
  dead**, in ten files. The README has contradicted `HARNESSES.md` since #348, and no file on
  main names the SHAs the tag moved between.
- **#277, #244 and #325 are one group**, three views of one lead in `sysid.py`'s
  `step()`/`identify()`; splitting them would lose #325's ordering constraint.
- **The Wave 4 order was inverted, by the ratchet's own numbers.** The plan of
  record put DHW before fetch. The measured cut costs on main read
  **views 120 < fetch 132 < dhw 195 < grid 236 < learning 350**, so the stages
  now run in that order. A stage is never justified by cut cost alone: three
  tools give three different orderings of the same class, so cut cost is a
  property of the partition rule rather than of the code.
- **The context object separates nothing, and #377 says so.** The round-2
  comment justified extracting the six hub attributes by citing a separability
  result. Leave-one-out overturns that reading: drop **all six** and 200 of 254
  methods remain one connected component, with every other component a
  singleton. What it is actually worth is a cut discount — **189 of 1,033
  cross-seam references, 18.3 %, changing no rank** — plus the deletion of a
  coordinator back-reference every later stage would otherwise need. It goes
  first because it relocates no method body, so no open fix can be silently
  reverted by it.
- **`optimize` is the most decomposable of the five monoliths, not the least.**
  The plan assumed the opposite. It has five ratchet-clean verbatim blocks at
  6–11 interface cost, the first being 64 lines at 6 in / 0 out after the solve,
  where no hot-loop question arises. The real carrier case is only the DHW tail,
  and it wants a dataclass of the 14 keys the method already returns rather than
  a state object threaded through. Constraint that decides the cuts:
  `functions_cc_over_15` sits at 39 of 39 with zero headroom, so every extracted
  helper must come in at or under complexity 15 — the otherwise obvious cut is 18
  and fails the gate.
- **#225 is closed, not re-scoped.** Its two named targets measure worst-boundary
  37 and 30 live locals inside the batched objective the gradient solver
  evaluates, no cold target remains above the 150-line mark, and `ThermalModel`
  binds no ratchet metric at all — the class contributes 3 of 23 oversized
  methods, behind the coordinator's 8 and the optimizer's 7.
- **#303 now has a ruler that cannot be gamed**: with the stub excluded by
  construction rather than subtracted afterwards, main measures **427**
  production-only strict errors, against 743 with the test fake — so 42.5 % of
  the historical headline was an artefact of a fake class. One correction to the
  brief it was given: `--warn-unused-ignores` does **not** prevent
  ignore-stuffing, since four real annotations and four live ignores move the
  count identically, so the ignore count has to be its own hard metric.
- **#197 and #233 closed**, each with a sharper reason than the plan's: 160 mypy errors was a
  *different ruler* (non-strict) rather than a stale count, and #233's restart gap fails its
  own flat-price null at both 24 and 48 hours.

## Standing rules

Unchanged from the repository's own protocol; restated here because a fresh
session reads this file first.

- **Fixer** (`tools/audit/briefs/fixer.md`): failing test first, importing the
  production symbol; mutation proof pasted into the PR body; the finding's own
  harness re-run before and after at the measured head SHA; a null control on
  every cost, gain or time claim; a learner or guard measured at both ends of
  its range; claims only for drift you measured; the scoped gate green locally
  through the gate lock; never `VERSION`, the manifest version or the
  `RELEASE_NOTES.md` heading. **After any rebase, steps 2–4 are re-executed** —
  the evidence describes one tree and a rebase makes a new one.
- **Reviewer** (`tools/audit/briefs/fix-review.md`): a fresh worktree at the
  head SHA, the mutation proof re-run, the measurement taken with the
  **finder's** harness rather than the fixer's, `env_drift.py --all` against
  the claims, and an attack at other configurations. Verdict `Fix review:
  merge` or `Fix review: blocked — <why>`. A reviewer never ranks below its
  fixer.
- **Claims.** A branch that moves fixtures claims them with a direction; the
  check is three-dot, never two-dot. A name cannot be both claimed and
  `may-drift`. Value-bearing fixtures are **never re-recorded on this box** —
  only an environment that records them all can honestly re-record one — so
  value drift is claimed and `golden.py --record --only` is for new key paths.
- **Stamps.** Only `tools/release/stamp.py --push`, only after the merge
  commit's own `fast` and `closures` are green, with a notes section naming
  every PR since the last tag. Never by hand, never in a branch. No new branch
  is cut between a fixture-mover's merge and its stamp.
- **Ratchet.** `python3 tests/structure.py` before every push. A change that
  adds coordinator lines pays for them elsewhere, re-records with the reason
  in the commit, or — for a genuine new production feature whose lines cannot
  honestly be paid for elsewhere — **raises** the budget because the capability
  is worth the structure it costs. All three are a decision, not bookkeeping,
  and all three carry their reason in the commit message. A raise additionally
  **requires the repository owner's explicit confirmation before the branch is
  pushed**: it is not a fixer's, a reviewer's or a judge's call, so an agent
  that wants one stops and asks. It is not a route for accommodating
  sloppiness, an unexamined refactor or an unmeasured feature — the first
  question is still whether the lines can be paid for elsewhere — but a metric
  at zero headroom is not a veto on new capability either (#398 read it as
  one). `cross_seam_fraction` carries a
  tolerance band and is never re-recorded: within the band there is nothing to
  record, outside it the gate fails, so a re-record can only loosen.
- **Ownership.** `owner:<session>` and a `claimed-by:` comment before a branch
  is cut. An unlabelled issue is *unknown*, not free.
- **Every fix PR body**: `Closes #N`, `Part of #201`, the head SHA measured,
  and every executed number.

## Model routing

Every seat in this programme — orchestrator, fixer, reviewer, judge, recorder —
runs as a **Cursor Task subagent** inside one Cursor Multitask session. There is
no Claude Code CLI seat, no `claude.ai` web-agent seat and no external runner:
where this file, the handover or a brief says `claude-web`, that is a **session
identity** (label `owner:claude-web`, branch prefix `claude-web/`) kept for
continuity with the branches already on origin, never a product to route work to.

The orchestrator seat is this session's parent (Auto), which executes
`web-fix-wave.js`'s control flow by hand. Workers are Cursor Task agents:

| seat | Cursor Task model | when |
|---|---|---|
| orchestrator | Auto (parent session) | control flow, merges, reconciliation, all sequencing decisions |
| architectural fixer + its reviewer | **Opus 5** (restructuring — not Grok) | W2-G1, W2-G2, every Wave 4 move PR and its review, and the decomposition judgement this plan assigns to the orchestrator seat |
| Wave 4 per-stage survey | **Opus 5** (restructuring — not Grok) | the survey that precedes a move stage |
| adversarial reviewer, `fix-review` with the **finder's** harness | **Grok 4.6** | every group whose brief carries a refuted or corrected claim; every fixture-moving group. Opus 5 when the group is a restructuring group |
| judge | **Grok 4.6** | all triage judges, including the #291 and #232 timing judges (still solo on an idle box). Opus 5 for any decomposition judgement |
| fixer on production code, mutation proof required | **Grok 4.6** | groups the wave file marks `"fixerModel": "opus"` that are not restructuring; restructuring groups stay Opus 5 |
| fixer on tests, tooling or docs | **Grok 4.6** | groups the wave file marks `"fixerModel": "sonnet"`; Sonnet 5 remains acceptable |
| record / roster / truth-up / citation-freshness PR | **Grok 4.6** | mechanical docs edits; Composer 2.5 optional for ones carrying no measured claim of their own |
| read-only reporting | **Grok 4.6** | Reconcile, post-merge gate watching, the pre-merge checklist, label hygiene, release-notes source material, issue digests, Wave 4 inventories, the #303 typing and #195 coverage inventories |
| stamp | scripted `stamp.py` via `web-stamp.js`, drafted by **Grok 4.6** under orchestrator oversight | rule 4 refuses notes omitting a merged PR, and the refusals are the product; the orchestrator reads every refusal |

**Grok 4.6 (`cursor-grok-4.6-high-fast`) is allowed in every seat except
restructuring.** Restructuring — Wave 4 decomposition, survey and move PRs and
their reviews, W2-G1 and W2-G2, and any module-move or decomposition judgement —
stays **Opus 5**. The orchestrator stays Auto. The former "Grok is read-only,
never a fixer, never a reviewer, never rules" constraint is withdrawn by owner
instruction. `tierOk` still applies: a reviewer may not rank below its fixer.

**The tier tokens in the wave files are not model names.** `web-fix-wave.js`
ranks `haiku < sonnet < opus` and throws if a reviewer ranks below its fixer, so
the tokens stay as they are and map: `opus` → Opus 5, `sonnet` → Sonnet 5,
`haiku` → Haiku 4.5 (unused today). Architectural seats route to Opus 5, so they
need no token above `opus` and `tierOk` accepts them as written. Grok 4.6 is
routed per the table above and satisfies an `opus` or `sonnet` token where the
seat is not restructuring; the tokens do not need editing.

**An architectural reviewer on the same model as its fixer is still a fresh
agent, not the fixer continuing.** Independence here is procedural, not
model-family: the reviewer works in a fresh worktree at the head SHA and
measures with the **finder's** harness, per `tools/audit/briefs/fix-review.md`.

## What this container changes

The previous sessions ran on the owner's M1 with the `gh` CLI. This one runs
in a 4-core cloud container with no `gh` and no way to install it, so:

- every GitHub action goes through the GitHub MCP tools;
- `tools/release/stamp.py`'s rule 2 gains a REST fallback (Phase 0), because
  it shells out to `gh` before any flag is read and would otherwise make
  stamping impossible here;
- the drift baseline cache starts cold, so the first `env_drift --all` per
  fork pays a full baseline capture — hence one fork per wave;
- at most two agents run at once, and anything needing a quiet box (the
  stress ruler, the timing judges) runs alone;
- **the gate lock is scoped to the runs that need it.** `fixer.md` step 5
  mandates it for every local gate; that was written for a dedicated
  eight-core machine, and on a shared container it serialises every agent.
  The lock exists for one script — `tests/stress.py`, whose solve-time guard
  measures the machine while it solves — so the rule now asks
  `closure.py select` what the diff actually runs and takes the lock only
  when the answer includes `stress.py`, reports `MODE: FULL`, or fails.
  Measured on this tree: a test file selects one script, the card five, and
  none of them `stress.py`; `optimizer.py` and `coordinator.py` select
  sixteen and do. The trap the rule is written around is that a gate file or
  an unmapped file prints **zero** selected scripts while meaning *run
  everything* — so it keys on the mode line, never on the count. What is run
  locally regardless is the evidence CI cannot produce: the mutation proof,
  the failing test at the merge base, and the finder's harness;
- `tests/card_browser.mjs` runs locally against the pre-installed Chromium
  (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) but CI's `browser` job is the
  authority, because the local Playwright is not CI's pinned version.

## When a merge turns main red

The programme has been in this state, so it gets a written answer rather than a
judgement call each time. `web-fix-wave.js` logs `MAIN IS RED after <group>` and
stops merging; `audit-merge.js` returns `{green:false}`. What follows:

1. **A behaviour change in the merged diff → revert first, diagnose after.** The
   revert is cheap and main being trustworthy is what every later merge is judged
   against. Re-land with the fix and the evidence.
2. **A failure the diff cannot reach → do not revert.** Establish it first, the
   way the register requires: an error naming a subsystem the diff does not
   touch, reproducing identically, or red on the base branch too. Then it is its
   own issue with its own number, and the wave holds until it lands. #387 is the
   worked example — a released gate instrument that was runner-dependent, found
   only because main went red on roughly half its merges.
3. **Never `--allow-red` to get a stamp out.** The flag exists for a human with a
   reason, not for an agent with a deadline.

A red main is work *now*, at every wake, whatever else is running: only a green,
mergeable head waits on reviewers.

## Documentation discipline

So that an aborted session loses nothing:

| When | Where |
|---|---|
| before a branch is cut | the issue: `owner:claude-web` + `claimed-by:` comment |
| after the failing-test commit, and after every commit | the branch is pushed |
| PR opened | the issue: PR link and head SHA |
| reviewer verdict | the PR: `Fix review: …` with RESULT lines |
| cannot finish | the issue: `state at stop:` naming branch, pushed SHA, last green check, what is missing |
| wave end | this file's Delivery status, `docs/audit-2026-09.md` status cells, a #201 comment |
| stand-down | a #201 comment and `docs/handover-<date>.md` |

The per-group briefs are committed too, not only the wave tables above:
`.claude/workflows/wave-1b-groups.json` holds all fourteen Wave 1b groups as
`web-fix-wave.js` consumes them, cut from the same fork. They are worth reading
before re-deriving anything, because several exist only to stop a fixer redoing
work a judge already refuted — W1-G13 names the measured fix for #258 and the
harness that must not be used to check it. Later waves add their own file at the
same path when they are prepared.
