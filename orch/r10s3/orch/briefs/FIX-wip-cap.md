# Fixer — move the open-PR cap to the dispatch side (WIP cap)

Role: **fixer**, one architecturally sound fix. Repository `tvofi/heatpump_optimizer`. Read
`dev/governance/roles/fixer.md` first: failing test first, mutation proof, a null control for every quantified claim,
`GATE_SCOPE=auto`, `tests/structure.py` before the push, and the handoff freezes the branch. **LOCAL seat only.**

## The ask (tvofi, 2026-10-20)

> "move the cap to the dispatch instead. dont dispatch new fixers for new unblocked groups when there are already
> 6 in WIP."

Why: the cap blocked **opening**, and opening is how work leaves WIP, not how it enters. On 2026-10-18 openers were
parked because 13 PRs were open against a cap of 6; the parked handoffs then sat invisible for up to 96 h (the
round-10 orphaned-handoff RCA, `dev/audit/rca/N-orphaned-handoff.md` once merged). The cap's real purpose — bound
work in progress — belongs on **dispatch**, where a new group enters the pipe.

## The change

1. **Opening is never blocked by a cap.** `tools/audit/seat/open_pr.sh` stops refusing when the open count reaches
   the threshold. Keep printing the count as information (`open_pr: N open PRs; the cap gates dispatch, not
   opening`). Keep accepting `--over-cap "<reason>"` as an argument so existing callers do not break, but it no
   longer changes whether a PR opens; say so where the flag is parsed.
2. **A dispatch gate in `tools/audit/seat/pr_cap.py`.** New mode(s): count **WIP** as roster groups whose
   `resume.stage` is `in-progress`, read through `roster_lib` at the roster ref (never a second parser). A
   `dispatch-gate` command refuses when the count is **at or over** the cap (`HPO_WIP_CAP`, default 6) unless
   `--over-cap "<reason>"` is given, and prints the WIP group ids. Keep the existing open-PR counting rule
   (bot/record exclusions) as its own function; it stays used by the tick.
3. **The tick reports WIP, not the open-PR cap**: `orchestrator_tick.py`'s per-pass level line becomes
   `WIP: N/6 (open PRs M)` — WIP from the roster, M from the existing counting rule — flagged at or over the cap.
   It stays read-only; it does not dispatch.
4. **Policy text (needs tvofi's approving review at merge, which the body's `## Approval` must say):**
   `dev/governance/roles/orchestrator.md` §5 gains the dispatch rule — *do not dispatch a new group while the
   in-progress count is at the cap; opening and merging are always allowed* — and the §11 pre-merge line about the
   cap is corrected if it names the open-PR form. Check `INSTRUMENTS.md`, `pr_args.sh` and `cloud_relay.sh`'s
   comment for stale statements and update them in the same diff.

## The tests this owes

- **Failing test first**: on the base, an open attempt at the cap is refused (construct the fixture or use the
  existing self-test shape); write the test that fails there and passes after. In the same pull request, show the
  base has no dispatch gate at all.
- **Dispatch-gate arms**: 5 WIP → pass; 6 → refuse; 7 → refuse; `--over-cap` with a reason → pass and print it; a
  roster it cannot read → refuse, never a clean zero; a group counted once even when it also has an open PR.
- **Null control**: with 0 WIP the gate passes; opening a PR when 20 are open succeeds.
- **Mutation proof**: each arm independently red — (a) opening still refused at the cap, (b) the gate passes at
  the cap, (c) record/bot PRs counted as WIP, (d) an unreadable roster treated as zero. Show each mutant's `rc`
  and the failing test name.
- Keep `pr_cap.py`'s existing self-test green and `selftest_wiring.py --check` clean; wire any new self-test in
  `.github/workflows/tests.yml` in this pull request.

## Constraints

- `tools/audit/seat/pr_cap.py`, `open_pr.sh`, `orchestrator_tick.py` and `dev/governance/roles/orchestrator.md`
  are code-owned paths: tvofi reviews at merge; state the behaviour change and a one-line rollback in
  `## Approval`. The policy paragraph is a policy change — surface it, do not treat this brief as its approval.
- Do not change `HEAVY_SLOTS`, the gate lease, or `merge_train.py`.
- No host path in any ref, message or body (#2310); no temp-path dependency. The box is loaded: `GATE_SCOPE=auto`,
  state load1 beside wall-clock numbers, prefer counts.

## Environment and handoff

Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/wip-cap` (absolute; create it). Worktree:
`git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/wip-cap/wt -B handoff/r10-wip-cap origin/main`.
`export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`. Push code to `handoff/r10-wip-cap`,
body to `handoff-body/r10-wip-cap`; every finding carries `Carry: <dest>` (0 unrouted). Report under 250 words:
both refs, the gate's arms, the mutations' rcs, the null controls, the tick's new line, and the prepr summary.
