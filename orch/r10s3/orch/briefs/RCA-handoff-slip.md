# Root-cause seat — completed handoffs that are never opened

Role: **root-cause**, running beside the fix (no fix is in this brief). Read `dev/governance/roles/root-cause.md`
first and `dev/governance/rules/defect-root-cause.md`; your product is a named cause, **one** named process state
(a)–(d), a cost test with numbers, and a countermeasure or a recorded refusal. **LOCAL seat only — no cloud.**

## The defect, as measured at 2026-10-20T18:00Z

`bash tools/audit/seat/bus.sh orphans --min-age-h 0` reports **12 stranded handoffs**. Five complete, unopened
deliverables have aged: `r10-earlycutoff-coverage` 96.3 h, `r10-merge-pr-mandate` 48.6 h, `r10-roster-ops` 47.3 h,
`r10-i5-docs` 44.1 h, `r10-rca-harness-friction` 41.6 h. The tick (`orchestrator_tick.py`, via `tick_loop.sh`)
printed an `OWED handoff:` line for each of them on every ~4-minute pass throughout that window — the detector was
never blind to them. The orchestrator opened almost none: two of five were dispositioned as folded carries, three
were re-queued only today.

Two harder cases the same window produced:
- **A design deliverable with no body ref**: `handoff/orch-machinery` at `09174d94` (DESIGN.md 828 lines +
  EVIDENCE.md 600) was approved by `review/orch-machinery-design` at `0bd5d12f` on 2026-10-20T12:40Z and no
  builder was dispatched. `bus.sh orphans` cannot see it: the scan skips refs with no `handoff-body/<topic>` as
  `no-body=26`.
- **A brief that grew after its seat finished**: `R10-ROSTER-OPS` handed off at `9969e3ca` on 2026-10-18T18:37Z;
  its brief gained the `state_docs.py beat --apply` roster-sync deliverable on 2026-10-20, so the branch predates
  its own brief and the roster records the group `in-progress / next_step open_pr` for the *old* deliverable only.

## What to establish

1. **Reproduce the state yourself**, at the SHAs above: run `bus.sh orphans --min-age-h 0`, read the tick's OWED
   lines in `orchestrator_tick.py`'s output, and check each group's roster stage against
   `git merge-base --is-ancestor` and `gh pr list --head`. Do not accept this brief's numbers.
2. **Name ONE process state** for the primary defect — completed handoff, no pull request — applying the rule's
   own distinction: (a) no process existed, (b) it existed and was not followed, (c) it was followed and did not
   produce the result, (d) it was sound and its preconditions changed. Quote the process line (the rule, the check,
   the brief) and show it present or absent, obeyed or not. Note in your report if you find the other observations
   above are different states; do not average them into one.
3. **Run the cost test** with the numbers: cost of the countermeasure, recurring, against cost of the defect ×
   P(recurrence). Use a measured class frequency if one exists — the repository's own escape record is
   `RELEASE_NOTES.md` plus closed `bug` issues; the orphaned-handoff class has been counted before (7 of 212 refs,
   and this round's 12). Say where each number came from.
4. **Design the countermeasure, or record a refusal.** The candidates, which you must test rather than assume:
   (i) an aging rule in the tick — an OWED handoff above N hours becomes a `DISPATCH:` line naming group and
   opener, above M hours flagged to the owner — which converts a level into a queue;
   (ii) the obligations ledger the machinery design specifies, with `handoff-no-pr` as a kind carrying a deadline;
   (iii) teaching the orphan scan to treat a design ref (a `DESIGN.md` with an approved review ref) as a
   deliverable whose obligation is a *build dispatch*, not a PR;
   (iv) a rule that a brief may not gain a deliverable after its seat's handoff.
   If your state is (c) or (d), say why a firmer instruction is the wrong answer. A check-shaped countermeasure
   must be demonstrated failing on the defect and passing once fixed, with a null control that does not fire on a
   healthy tree; it obeys the ratchet; and **policy changes only with tvofi's approval** — draft, name the state it
   addresses, do not land it.
5. **Overlap check**: the machinery design (`dev/audit/design/orch-machinery/DESIGN.md` at `09174d94`, §6.3 and
   §6.4) already proposes an obligations ledger and the ROSTER-OPS record verifier. State whether your
   countermeasure is one of these, extends one, or conflicts — do not propose a second ledger.

## Environment

Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/rca-handoff-slip` (absolute; create it). No worktree is needed for
reads; use `/Users/timmalmstrom/heatpump_optimizer` for git reads and do not write there. Read the repo and API only.
`export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`. Long commands run detached
with `tools/audit/seat/daemonize.py --log`. The box is loaded; state load1 beside any wall-clock number and prefer
counts. No host path in any report text (#2310) — write `~/…`.

## Report under 400 words

The re-measured numbers; the one state and the quoted process; the cost test; the countermeasure with its
demonstration or the recorded refusal; the overlap verdict against the machinery design; and what you could not
establish.
