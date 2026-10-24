# Fix review — R10-ROSTER-OPS (roster editor operations)

Role: **fix reviewer**, adversarial. Read `dev/governance/roles/fix-review.md` and
`dev/governance/roles/COMMON.md` first. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**

Pull request: **#2513** (`fix/r10-roster-ops`). Code head at dispatch: `c89cdf73`; **the head is moving** —
a second fixer is adding the missing `instrument-self-tests` wiring for `r10_roster_ops_mutants.py`, which
`selftest_wiring.py` refuses at `c89cdf73`. Review the deliverable now and re-run only the delta at the new head;
do not post a verdict for `c89cdf73`.
Body: `refs/heads/handoff-body/r10-roster-ops` (`a38f30ac…`; `## Forward-carry` reads the bare word `none`).
No `bus-nonce` is issued yet — the orchestrator dispatches at the final head; hold the verdict until it arrives.

Work from a detached worktree at the head you are measuring, under
`/Users/timmalmstrom/hpo-seats/r10s3/r10-roster-ops-review/` (scratch and evidence there, absolute paths only).
`export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`. Long runs detached via
`tools/audit/seat/daemonize.py --log`; the gate lease is shared, so no two heavy checks at once. The box is loaded:
state load1 beside wall-clock numbers and prefer counts.

## What this is

`roster_edit.py` gains two operations, `set-after <group> <G1,...|->` and `drop-carry <group> <index|--match TEXT>`,
so replans and stale-carry drops go through the load-validate-dump flow and the lint gate instead of a string
splice, plus `r10_roster_ops_mutants.py` proving each op's self-test arm fails when its predicate is deleted, and
the `INSTRUMENTS.md` entries.

## What to verify, with your own harness

1. **The round-trip rule.** A no-op edit reproduces the roster's bytes exactly (the self-test claims it). Construct
   a no-op `set-after` (same edge set, different order) and a `drop-carry --match` that matches nothing, and show
   the file is byte-identical; a formatting rewrite would touch every one of ~7,500 lines.
2. **`set-after` semantics.** Adding an edge, replacing an edge set, and `-` (clear). A cycle must be refused, an
   unknown group refused, and a dependency on a `done` group allowed or refused per the documented intent — read
   the code and state which it does and whether the body says the same.
3. **`drop-carry` semantics.** By index and by `--match`; a match hitting two entries; an out-of-range index; an
   absent match; the interaction with `append-carry`'s duplicate refusal. Show each rc.
4. **The mutant driver.** Run it; delete each predicate it targets and show the corresponding self-test arm reddens.
   The driver must itself be wired in `.github/workflows/tests.yml` — that is the delta under repair; check it when
   the new head lands.
5. **The lint gate.** `brief_lint` runs before push; show a roster edit that would break a citation is refused
   before the push, not after.
6. **The body.** Run the body checks yourself at the head: `carry_audit.py check --body` 0 unrouted (the
   `## Forward-carry` exemption is the bare word `none`); the delivery row exists; every figure resolves. The
   policy status: `roster_edit.py` and the workflow are code-owned, so tvofi reviews at merge — confirm the body
   says so.
7. **What the branch does not do.** It does not build the brief's second deliverable (the `state_docs.py beat
   --apply` reconciler); that is a separate handoff. Say whether the body is honest about that, and whether anything
   here presumes the reconciler exists.

Post the verdict with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` once the nonce
arrives; a head that moved under the review is `blocked`. No host path in the verdict (#2310) — write `~/…`.
Report under 250 words: verdict line, each item confirmed/not, what you could not establish.
