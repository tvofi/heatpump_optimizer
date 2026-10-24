# Fixer — a stopped pusher must not leave its work running

Role: **fixer**, one fix. Repository `tvofi/heatpump_optimizer`. Read `dev/governance/roles/fixer.md` first:
failing test first, mutation proof, a null control for every quantified claim, `tests/structure.py` before the
push, and the handoff freezes the branch. **LOCAL seat only — no cloud.**

## The defect (measured 2026-10-20, on this box)

Stopping a pre-PR pusher leaves its whole subtree running. Every one reparents to launchd and keeps consuming
CPU until it finishes on its own. Six were still alive when the orchestrator swept the table, and every kill
needed a second pass two levels further down:

| survivor | what it was | age when found |
|---|---|---|
| `closure.py record` + its parent | recorder of a stopped roster-ops-wire prepr | 26 min |
| a second recorder chain, same lane | same | 32 min |
| `app_push` + `prepr`, train-hold | left by an opener that was stopped | 55 min |
| `app_push`, codeql | direct child of a killed `update_pr` | 62 min |
| `app_push`, i5-docs | direct child of a killed `open_pr` | 50 min |

The cost was not incidental: with six preprs live against a four-slot pool and load at 77 on 8 cores, these
survivors were a material part of why every remaining job took 20-60 minutes. The orchestrator's own
instrumented watch (`tick_loop.sh`) could not see them, and neither could the slot pool — they hold no slot
once their parent is gone.

## The shape

`tools/audit/seat/pr_args.sh` already owns the shared stop report: `pr_trap()` installs the ERR trap that turns
every silent `set -e` stop into a named `STOPPED:` line, and it is sourced by `open_pr.sh` and `update_pr.sh`.
That is the one place a TERM/INT reaping trap belongs, so both pushers get it from one edit, and `app_push.sh`
is the other caller to check — if it does not source `pr_args.sh`, either make it, or justify in the body why
its own trap is the right seam.

Requirements:

- **On TERM and INT, terminate the whole descendant tree** — not just the direct child, since the tree is
  three deep (`app_push` → `prepr` → `derive_closures` → python). Walking `pgrep -P` recursively is
  acceptable; putting the child in its own process group and killing the group is cleaner if the scripts
  can carry it.
- **Never a pattern kill.** `pkill -f` on a shared box reaches other seats' processes; the programme has been
  burned by this. Kill by pid or by process group, never by command line.
- **Do not reap on a clean exit mid-work**: an EXIT trap that kills children unconditionally would break a
  pusher's normal path. Reap on signals, and on EXIT only after the run has finished or aborted.
- If `app_push.sh` and `update_pr.sh` share the code, the self-test must drive both call sites, not one.

## Controls

- **Failing test first**: spawn a stub tree under the pusher (a parent that sleeps, a grandchild that sleeps),
  TERM the pusher, and count survivors. At the base there are survivors; at the head there are none. Show both
  counts and the pids.
- **Null control**: a normal successful run must leave nothing behind either, and must not kill anything it did
  not start — assert that an unrelated sleeper started beside the run is still alive afterwards.
- **Mutation**: remove the reap line and show the survivor arm reddens; remove the by-pid rule and show the
  unrelated-process arm reddens. A mutant that crashes instead of reddening is not a proof.
- The existing `pr_args.sh --self-test` arms must all still pass; it runs offline against copies of the scripts.

## Environment and handoff

Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/pusher-reap` (absolute). Worktree:
`git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/pusher-reap/wt -B handoff/r10-pusher-reap origin/main`.
`export PATH=/Users/timmalmstrom/.local/state/hpo/bin:$PATH` before every python invocation.
Run prepr with `env PREPR_SKIP_CLOSURES=1` (owner ruling in force) and name the skip in `## Head`.
The box is saturated: anything long goes behind `tools/audit/seat/daemonize.py --log`, and state load1 beside any
wall-clock figure, prefer counts. Push code to `handoff/r10-pusher-reap` and body to
`handoff-body/r10-pusher-reap`; no host path (#2310).
Report under 200 words: the counts before and after, each control's rc, what you could not establish.
