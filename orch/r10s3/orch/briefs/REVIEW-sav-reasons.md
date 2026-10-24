# Fix review — R10-SAV-REASONS (revenue attribution)

Role: **fix reviewer**, adversarial. Read `dev/governance/roles/fix-review.md` and
`dev/governance/roles/COMMON.md` first. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**

Code head: `84eb9c1abad0a4460f764f4cab916db0f66df48e` (`handoff/r10-sav-reasons`).
Body: `refs/heads/handoff-body/r10-sav-reasons` = `c4993ff6863c10833e6ed67d1821e70cb9f61a62`.
Pull request: open or being opened for `handoff/r10-sav-reasons`; find it with
`gh pr list --head handoff/r10-sav-reasons --state open --json number,headRefOid`. If it is not open yet,
review anyway and hold the verdict, saying so.

Work from a detached worktree at the head: create it under `/Users/timmalmstrom/hpo-seats/r10s3/r10-sav-reasons-review/wt`
with `git -C /Users/timmalmstrom/heatpump_optimizer worktree add --detach <wt> 84eb9c1a`. Scratch root:
`/Users/timmalmstrom/hpo-seats/r10s3/r10-sav-reasons-review` (absolute paths only). Verdict file there too, with
`bus-nonce: r10-sav-reasons-r1`. Environment: `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`.
Long runs go detached via `tools/audit/seat/daemonize.py`; the gate lease is shared, so no two heavy checks at once.

## The fix, in one paragraph

Two booking paths put money under a cause that did not draw it. `_accumulate_energy` tagged every metered kWh with
the plan step's reason, including a channel the plan was not drawing on, and the boost overlay rewrote a channel's
power while leaving the plan's reason, so a boost over an idle step booked as idle. The fix partitions in
`ledger.explain_metered`: a channel whose reason says the plan drew nothing (idle codes, `pump_mode`, no reason)
books `REASON_UNTAGGED` outside the plan; a channel the plan ran keeps its step's reason at any meter magnitude
(sub-floor steps are duty cycling *within* the step, per `thermal_model.planned_draw_runs`). The overlay tags its
channel `REASON_BOOST`, the three fixed-mode actions name their cause, and `payload.IDLE_REASONS` becomes the one
owner of the seven idle codes.

## What to verify, with your own harness

1. **The partition boundary — the fixer names this as the first target.** A channel the plan ran keeps its step's
   reason at *any* meter magnitude. Construct an install where the meter reads far above the plan's step average
   and decide, with evidence, whether booking it on the plan's reason is honest; say what definition of "the plan
   drew this" the code implements and whether the alternative (energy beyond the commanded kWh is outside the plan)
   would misbook duty cycling. The fixer attempted and abandoned that alternative; falsify or confirm that call.
2. **`pump_mode` added to `IDLE_REASONS`** widens the set the optimizer's blocked relabel reads (it now contains
   its own output). Show whether that is a no-op today and what it would take to make it bite.
3. **`ZERO_ENERGY_REASONS` as an alias of `IDLE_REASONS`** — a future narrative wanting a narrower set now silently
   widens. Judge whether the one-owner consolidation is worth that coupling.
4. **Both ends of the finder's harness** (`dev/audit/harnesses/sav_reasons_booking.py`, committed): run it at the
   merge base `4e5801eb5` and at the head yourself and confirm the stated flip (`reason:idle 0.4 → 0.0`,
   `untagged 0.0 → 0.4`, boost reason `idle → boost`). The harness must refuse a tree it did not load.
5. **The five mutants** — reproduce at least two independently (the `code = reason` revert; deleting the boost tag)
   and show each reddens the named check.
6. **Null controls** — the flat-price control must still be a genuine NULL with the pre-fix and post-fix mappings;
   show why the defect was attribution, not pricing.
7. **Ratchet and score** — `class_excess_loc 18301→18299`, `max_class_loc 8543→8541`, `functions_cc_over_15 31→30`,
   `seam_cut_total 719→718` re-recorded at `4e5801eb5`; archscore `dS +0.0023`. Re-run both; a metric that rose is
   a finding.
8. **The body** — run `tools/pr/prepr.sh`'s body checks at the head yourself (carry routing 0 unrouted; figures
   resolve; `## Unpinned sites` disposes of all five). The scoped gate was not run to completion locally; check
   whether the body says so and whether `golden.py`, `env_drift.py`, `stress.py`, `validate.py`, `card.mjs` are
   honestly named as unrun rather than implied green.
9. **The carry** — the fixer says the `REASON_LABELS` gap is carried to `R10-ADVISOR`; the orchestrator lands it
   in the roster. Confirm the body routes it and does not claim the card is fixed here.

Post the verdict with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>`; the evidence dir
must be absolute and hold your harness, its output and the mutant transcripts. Grammar per `fix-review.md`; a head
that moved under the review is `blocked`. No host path in the verdict (#2310) — write `~/…`. Report under 250 words.
