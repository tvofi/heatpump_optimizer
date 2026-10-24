# Fix review — R10-PREPR-CAP, gate lease priority (owner's own ask)

Role: **fix reviewer**, adversarial. Read `dev/governance/roles/fix-review.md` and `dev/governance/roles/COMMON.md`
first. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**

Pull request: **#2526** (`fix/r10-gate-priority`), head `31529479c13d413…` at open. Body ref
`handoff-body/r10-gate-priority`. **The head may move once** — the orchestrator recurries main and adds the
delivery row. Measure the deliverable now, poll `gh pr view 2526 --json headRefOid`, re-run only the delta, and
**hold the verdict** for a `bus-nonce`; `push-verdict` refuses without one.

Work in a detached worktree at the head you measure, under `/Users/timmalmstrom/hpo-seats/r10s3/r10-gate-priority-review/`
(absolute). `export PATH=/Users/timmalmstrom/.local/state/hpo/bin:$PATH`. The box is loaded: prefer counts, state
load1 beside any wall-clock figure, long runs behind `tools/audit/seat/daemonize.py --log`.

## The ruling this implements (tvofi, 2026-10-20)

> "I want a fix to the local gate lease. Any PR on the critical path should get first in line if there is a
> queue." … "Or any group, rather." … "I mean that the group should be on the critical path for a ticket to get
> first in the queue by default."

So the default must be **derived**, not hand-marked: a ticket whose group is on the current critical path takes
first place, with no per-PR human decision. The lease stays generic — an integer priority, and it does not decide
who deserves one. The caller (`prepr.sh`) derives the default from
`dev/programme/rosters/critical-path.json` on the roster branch.

## What to verify

1. **The precedence.** `$HPO_GATE_PRIORITY` > `.gate-priority` in the worktree > the derived default > 0. Try each
   channel and one that is unreadable or malformed: every unreadable, malformed or unmapped input must resolve to
   **0**, never to a crash and never to a silent 1.
2. **The derivation reads the ref, not a local file.** Confirm it fetches `origin/handoff/audit-r<N>-roster` and
   reads `critical-path.json` from there; a group whose branch is not on the critical path must get 0, and a group
   that is, 1. Check what happens when the roster ref is missing or the file is stale — the body should say.
3. **Aging cannot starve normal work.** 600 s promotion to `PRIORITY_MAX`, between the pool's 69 s heavy floor and
   the 1800 s lease. Verify the arithmetic and that a low-priority waiter still gets a slot.
4. **The slot-lifetime amendment** (the second half of this fix, and the one that cost real queue time): `take_slot`
   records a pid; an **expired** slot is freed only when that pid is gone. Attack this: is a live holder that has
   outlived its lease kept, and does a dead holder get reclaimed without waiting for the expiry? `slot-status`
   prints `past-lease=N` and `unleased=N` — drive both.
5. **The mutants.** The fixer claims nine, each rc 1 with its named arm. Re-run at least the ordering+aging one,
   the live-holder one, and the `names_pid=False` one; a mutant that crashes instead of reddening is not a proof.
6. **The rollout boundary it discloses.** A peer still running main's `prepr.sh` can steal an expired slot because
   the fix binds only takers that run it. Say whether the body states this plainly, and whether it matters for the
   window between this merge and the next seat start.

## The body and merge

`prepr.sh` on the body; `carry_audit`; `figure_lint`; `## Head` names the head and records the closures skip under
the owner's ruling. The diff carries `dev/governance/rules/gate-scoping.md` and its generated copies, so this is
**policy** — tvofi approves it under mandate 6175172275; say so.

Post the verdict with `tools/audit/seat/bus.sh push-verdict 2526 <verdict file> <evidence dir>` once the nonce
arrives; a head that moved under the review is `blocked`. No host path in the verdict (#2310) — write `~/…`.
Report under 250 words: verdict line, each item confirmed/not, what you could not establish.
