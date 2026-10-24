# Planning seat — the most effective plan, mechanically re-derivable

You own the **plan model**, not the repository's code fixes: the schedule the round-10 programme
actually runs on, and the machinery that recomputes it at a wave edge without judgement.
**LOCAL seat only — cloud dispatch is forbidden in this session.**

## Read first, from the refs, never from memory

- `CLAUDE.md` at the repository root (the policy index; it names every rule that binds you) and
  `dev/governance/rules/writing-for-agents.md`.
- **The roster is the single source of truth for work, dependencies and done-ness**:
  `git -C /Users/timmalmstrom/heatpump_optimizer show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`
  — every group carries `after` edges, `size` (S/M/L/XL), `issues`, `brief`, `resume.stage` and
  `carry`. Do not edit it.
- The existing planning artefacts, all in `/Users/timmalmstrom/hpo-orch/r10s3/plan/`:
  `WAVES.md`, `DRAIN.md`, `wave-data.md`, `WAVES.json` (hand-cut and stale — 39 of 95 groups),
  and the current renderer `gen.py` + `tpl.html`. `round-10-plan.html` is its output.
- Delivery rows on main: `dev/programme/delivery/<N>.md` (one merged pull request each).
- The running programme's own record: issue **#201**.

## The owner's standing constraints — these are the constraint set, quote them back in your report

- **At most 8 seats at once**; clear a worktree when its seat is done.
- **At most 6 open pull requests**, at most **2 touching `coordinator.py`**; drain to about 4
  before opening more.
- **Stamps**: a patch stamp after roughly **5 production groups**, cut from main with
  `tools/release/stamp.py`.
- **Waves**: drain the wave's pull requests, stamp, then dispatch the next wave's groups
  together; no new group mid-drain. He has also asked whether waves may overlap, and the
  current answer is that they may — the six-pull-request cap is what binds.
- **Coordinate on #201** before each merge or release; record each state change there.

## The objective, stated before you compute anything

Minimise **time to programme closure**, then **total CI minutes**, subject to the constraints
above. Say which tie-breaks you use and why. Two things you must price, because he asked for
both:

1. **Wall time** — a schedule that keeps six slots busy and never idles on a drain.
2. **CI time** — every merge batch pays one `fast (3.14)` + `closures` + `Analyze (python)` run
   on the batch tree. Merging k pull requests in one batch shares that cost; merging them
   separately pays it k times. Quantify the trade against the wall-time gain.

## Measure, do not guess

- CI context durations from `gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`
  over recent main merges — report **median and IQR** for `fast (3.14)`, `closures` and
  `Analyze (python)`, with the shas and job ids you read. Today's full gate has been running
  21–56 minutes; do not carry my numbers, take your own.
- Group lead time (dispatch → merge) from the delivery rows and merged PR timestamps, if the
  data supports it; otherwise say so and keep the roster's S/M/L/XL durations as an explicit
  assumption, labelled as one.
- The `Analyze (python)` leg has been cancelled at its 30-minute cap three times today and
  succeeded once in 21.5 minutes: treat the cap as a risk term and price a cancelled leg
  (a rerun costs the full leg again).

## Deliverable A — `tools/plan/replan.py`, the mechanical replanner

One command, no judgement, runnable at a wave edge:

- reads the roster ref, the caps and a durations file (measured, cached to disk);
- computes the schedule — list scheduling, six concurrent slots, longest-path-first, stamps
  when five production groups have landed;
- writes `plan.json`: per group `{wave, start, finish, slot}`; per wave `{opens, drains, stamp,
  groups}`;
- prints the wave table and a one-line summary (closure, CI minutes, batch count);
- `--check` exits non-zero if the plan violates a constraint (more than six in flight at any
  instant, a dependency finishing after its dependent starts, a stamp cadence breach, a wave
  opening while the open-PR cap is exceeded);
- a **self-test** with a planted failing case (a dependency cycle, and an over-cap wave) that
  proves `--check` refuses rather than warns;
- deterministic output for the same inputs — a replan that changes the page when nothing changed
  is a defect.

Where it lives matters: a **new tracked file must be deliberately classified** — put it in a
measured closure or on `tests/closure.py`'s `INERT` list, or `tests/entities.py` fails with
*"these force the FULL suite when touched"*. Read `tests/README.md` before choosing.

## Deliverable B — the visualisation

He said the current chart has **"messy dashed lines everywhere"**. The chain is drawn as cubic
connectors between consecutive links, and across lanes and hours they cross the whole chart.

Make the critical path read cleanly. One credible shape — you choose, and justify it:

- chain bars carry a **◆** and a heavier outline; the dashed connector appears **only** between
  consecutive chain groups and **never** more than one per pair;
- a connector that would cross more than a lane or more than a couple of hours is **not drawn** —
  the ◆ marks and the caption carry the chain instead;
- the caption lists the chain in order with each link's wave, so the reading does not depend on
  the lines at all.

Then make `gen.py` a **renderer of `plan.json`**, not a second planner: one schedule model, one
place to change it.

## Deliverable C — alignment with the roster and the other plan documents

Cross-check your schedule against `WAVES.md`, `DRAIN.md`, `wave-data.md`, `WAVES.json`, the
roster and the delivery rows. For every disagreement: say which source wins and why. The
roster's `after` edges and `resume.stage` win on dependency and done-ness; the owner's caps win
on capacity; the hand-cut `WAVES.json` wins nothing and should be retired or regenerated.

Report the **wall-time and CI-time delta** between the current `gen.py` schedule and yours, with
the numbers that produce it.

## Environment and handoff

- Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/plan-opt` (absolute; create it). Worktree:
  `git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/plan-opt/wt -B handoff/r10-plan-opt origin/main`.
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH` (the seat
  python is the pinned 3.14). Instruments: `/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/`.
- The box runs eight seats; keep your own footprint small and prefer counts over long loops.
- Repo work goes on the branch and a **handoff ref** (`handoff/r10-plan-opt`, body at
  `handoff-body/r10-plan-opt` via `body_push.sh`); the orchestrator opens the pull request —
  you write no GitHub. **No host path anywhere** in a ref name, commit message or body (#2310):
  write `~/…`.
- The out-of-tree renderer (`~/hpo-orch/r10s3/plan/gen.py`, `tpl.html`) you edit in place; it is
  scratch, not the repo, and the orchestrator re-runs it.

## Report back, under 400 words

The objective and tie-breaks; the measured CI durations with their shas; the schedule deltas
(wall time and CI minutes, current vs yours); the files you changed and both handoff SHAs; every
disagreement you found between the plan documents and the roster, with the winner; and anything
you could not establish.
