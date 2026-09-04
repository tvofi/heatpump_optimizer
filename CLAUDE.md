# Working on this repository

A session loads this file automatically. It exists because a resumability audit
found that every one of its auditors had to be *told* what to fetch before it
could work out what was in force.

Everything in this section is **permanent** — it describes the repository, not
any particular piece of work. Anything dated lives in the fenced block at the
bottom, which is allowed to go stale and says so.

## Four rules that will refuse your pull request

1. **The gate is scoped by measured dependency closures.** `GATE_SCOPE=auto`
   runs only the scripts your diff can reach, decided from `tests/closures.json`
   rather than from anyone's opinion. A push to `main` forces `full`, and that
   asymmetry is the safety argument: if a closure is ever wrong, main goes red
   within one merge instead of never.
   **`MODE: SCOPED — 0 script(s) run` and `MODE: FULL` both print zero and mean
   opposite things.** Key on the mode line, never the count — but that line
   only exists on a branch; a push to `main` prints no mode line at all,
   because the forced `full` above never calls the code that prints it.
2. **A structural ratchet refuses growth.** `tests/structure.py` measures 22
   metrics against `tests/structure_budgets.json`, and every one may only move
   down. Several sit at zero headroom, so a change that adds lines to the wrong
   class fails — and the correct response is to pay for the lines, or to
   re-record deliberately with the reason **in the commit message**, never to
   loosen a budget quietly. `cross_seam_fraction` is a tolerance metric and is
   never re-recorded.
3. **Value-bearing golden fixtures are claimed, not re-recorded.** Solver floats
   do not reproduce across BLAS builds, so only a canonical environment can
   honestly record one. Drift is declared in `tests/golden/claimed_drift.txt`
   (or `card_claimed_drift.txt`) with its direction, and `claims-for:` must equal
   `VERSION`. A fixture cannot be both claimed and may-drift — `env_drift.py`
   refuses that. Check claims three-dot (`git diff $(git merge-base origin/main
   HEAD)...HEAD`), never two-dot.
4. **Versions are assigned after the merge, by `tools/release/stamp.py`.** Never
   touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading in a
   branch. The stamp has its own refusal rules, including one that rejects notes
   omitting any merged PR.

A new tracked file must be **deliberately classified** — put in a measured
closure, or on `tests/closure.py`'s `INERT` list — or `tests/entities.py` fails
with *"these force the FULL suite when touched"*.

## The contracts, when the work is a fix

- `tools/audit/briefs/fixer.md` — failing test first, importing the production
  symbol; the mutation proof pasted; the finding's own harness re-run at both
  ends; a null control for any cost, gain or time claim. After any rebase,
  steps 2–4 are re-executed, because the evidence described a different tree.
- `tools/audit/briefs/fix-review.md` — the reviewer measures with the
  **finder's** harness, never the fixer's, in a fresh worktree at the head SHA.
  Four implementations here looked right and were wrong, one worse than its bug.
- `tools/audit/briefs/judge.md` — a finding whose harness does not move under
  its own perturbation is **void**, whatever the votes said.
- `tests/README.md` — the suite, and why a test that re-implements a production
  formula pins nothing.

## Running it

`./tests/run.sh` is unscoped and long. On a branch, what you almost always want
is the scoped gate against your merge base:

```
GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
```

`/tmp/hpo-gate.lock` serialises anything that runs `tests/stress.py`, which
measures the machine while it solves and is wrong if something else is running.
Take it for a full or stress-selecting run; a scoped run that does not select
`stress.py` does not need it. The owner file records a pid, so a *dead* holder is
a decidable fact — but that pid is usually the gate shell, which exits normally
when the gate finishes while its agent is still alive, so check that the agent
has gone quiet too before clearing one.

<!-- ▼ DATED BLOCK. Everything below describes work in progress and expires with
     it. If the tracking issue is closed, this block is history, not instruction. -->

## In flight as of 2026-09-04 — the open-issues programme

Tracking issue **#201**; its newest comment is the live state. The plan of record
is `docs/plan-2026-09-open-issues.md`, whose Delivery-status table is
authoritative where it and a wave body disagree — so if that table looks stale
against #201, the table is the bug and fixing it is the first task.
`docs/handover-<latest date>.md` carries what the code cannot say: per-group
resume points, blockers, and the traps a previous session hit.
`.claude/workflows/wave-*-groups.json` hold the per-group briefs, each with a
`resume` field saying where it restarts. A brief records what a judge already
**established and refuted** — reading only the issue body will have you
implement a plan that was overturned.

When this programme closes, delete this block. The sections above stand alone.
