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
`claude-web/`. Owner decisions recorded 2026-09-03: full merge-and-stamp
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
| triage B2 | solver, suite, browser and timing judges | #304 #258 #242; #291 #232 alone | — | pending |
| 1b | gate instruments, suite gaps, card, stores | 26 issues in 14 groups | v6.3.11 | prepared |
| 2 | coordinator lifecycle, learners, options grouping | #236 #237 #240 #239 #243 #283 #284 #279 #278 #277 #244 #325 #280 #198 | v6.3.12 | pending |
| 3 | solver, DHW planner, GIL process route | #232 #234 #289 #290 #199 #242 | v6.3.13 | pending |
| 4 | the #193 decomposition programme, S0–S13 | #193 #223 #224 #225 | one per stage | pending |
| 5 | typing lane, and the coverage deficit #195 raised | #303 #304 #195 | per tranche | pending |

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
  adds coordinator lines pays for them elsewhere or re-records with the reason
  in the commit — a decision, not bookkeeping. `cross_seam_fraction` carries a
  tolerance band and is never re-recorded: within the band there is nothing to
  record, outside it the gate fails, so a re-record can only loosen.
- **Ownership.** `owner:<session>` and a `claimed-by:` comment before a branch
  is cut. An unlabelled issue is *unknown*, not free.
- **Every fix PR body**: `Closes #N`, `Part of #201`, the head SHA measured,
  and every executed number.

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
