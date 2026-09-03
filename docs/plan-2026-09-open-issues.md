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
| 0 | stamp REST fallback; #367, #368 | #364, #282 | v6.3.10 | in progress |
| triage | close or re-scope on a measured number | #281 #195 #197 #199 #244 #233 #325 #291 #232 #242 #304 #303 #225 #224 #193 #334 #258 | — | pending |
| 1a | the stress ruler, alone on an idle box | #346 | v6.3.11 | pending |
| 1b | gate instruments, suite gaps, card, stores | #370 #369 #350 #374 #372 #357 #373 #246 #251 #247 #248 #249 #250 #252 #288 #238 #260 #261 #263 #266 #262 #265 #254 #245 #334 | v6.3.11 | pending |
| 2 | coordinator lifecycle, learners, options grouping | #236 #237 #240 #239 #243 #283 #284 #279 #278 #277 #280 #198 | v6.3.12 | pending |
| 3 | solver, DHW planner, GIL process route | #232 #233 #234 #289 #290 #199 #242 | v6.3.13 | pending |
| 4 | the #193 decomposition program, S0–S13 | #193 #223 #224 #225 | one per stage | pending |
| 5 | typing lane | #303 | per tranche | pending |

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
