# Fix review — R10-FREQ-DEFROST (a defrost interval must not teach the frequency map)

Role: **fix reviewer**, adversarial. Read `dev/governance/roles/fix-review.md` and `dev/governance/roles/COMMON.md`
first. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**

Pull request: **#2527** (`fix/r10-freq-defrost`), head `0be6047c` at open. Body ref `handoff-body/r10-freq-defrost`.
**The head may move once** — the orchestrator recurries main and adds the delivery row. Measure the deliverable
now, poll `gh pr view 2527 --json headRefOid`, re-run only what the delta touches, and **hold the verdict** for a
`bus-nonce` at the final head; `push-verdict` refuses without one.

Work in a detached worktree at the head you measure, under `/Users/timmalmstrom/hpo-seats/r10s3/r10-freq-defrost-review/`
(absolute paths). `export PATH=/Users/timmalmstrom/.local/state/hpo/bin:$PATH`. The box is loaded: prefer counts,
state load1 beside any wall-clock figure, and put long runs behind `tools/audit/seat/daemonize.py --log`.

## What this is

A defrost interval must not teach the frequency map, and defrost ticks must not stand the control down. Four commits
off `4e5801eb`, with a P2 registry entry pinning decision-context reads of `*.defrosting`.

## Attack these, in the fixer's own order

1. **The finder's harness stopped separating at the head.** The fixer reports its `--perturb` arm reading `8 → 0 → 0`
   instead of `8 → 0 → 8`, and says the fold now reads the predicate before `_freq_fold_blocked`. If the harness
   cannot separate, say whether the *finding* is still measurable by another arm you write, or whether the
   perturbation is now vacuous. A harness that moves nothing is not evidence either way.
2. **The two arm64-only reds.** `optimality.py` `1 of 84` and `stress.py`'s shoulder check are attributed to this
   box, with a baseline export as the control. Verify the baseline claim yourself: same check, same numbers, at
   `4e5801eb`. If they reproduce at the base they are not this diff's; if one does not, the diff owns it.
3. **The P2 registry entry is narrower than its name.** It pins attribute reads `*.defrosting`; a predicate that
   copies the flag to a local first (`d = signals.defrosting; if d:`) is invisible to it. Confirm that gap, and say
   whether the barrier's claim in the body is worded to match what it actually pins.
4. **`--pin-killed` was not run.** Three added sites are described as "pinned by mutation-autofix" from the checks
   that fail when the guard is removed, not from the lane's own verdict. Say which of the three you could kill
   yourself and how.
5. **The re-recorded structure budgets.** `class_excess_loc` 18301 → 18299, `max_class_loc` 8543 → 8541,
   `seam_cut_total` 719 → 718, re-recorded with `--record`. Confirm each moved **down** and that the reason is in
   the commit message; a raise here would be the owner's.

## The body

`prepr.sh` on the body; `carry_audit` 1 routed / 0 unrouted; `figure_lint` dispositions; the `## Head` names the
head and records the closures skip under the owner's ruling (CI's `closures` context is the covering check).
The `pump_offline` arm of D7-s2-01 is **not** closed and is carried to `R10-ARCH-SHAPES` — confirm the body says
so plainly and does not imply the finding is fully discharged.

Post the verdict with `tools/audit/seat/bus.sh push-verdict 2527 <verdict file> <evidence dir>` once the nonce
arrives; a head that moved under the review is `blocked`. No host path in the verdict (#2310) — write `~/…`.
Report under 250 words: verdict line, each item confirmed/not, what you could not establish.
