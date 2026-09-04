# Orientation

A cold session loads this file automatically. It exists because a resumability
audit found that every auditor had to be *told* what to fetch before it could
work out what was going on.

## If a programme is in flight, start here

1. **Issue #201** is the live record. Its most recent comment is the current
   state of the open-issues programme — what merged, what is held and why.
2. **`docs/plan-2026-09-open-issues.md`** is the plan of record. Its
   Delivery-status table is authoritative where it and a wave body disagree —
   so if that table looks stale against #201, the table is the bug, and fixing
   it is the first task, not a later one.
3. **`docs/handover-<latest date>.md`** carries what the code cannot say:
   per-group resume points, blockers, and the traps a previous session hit.
   Read the newest one; older handovers are bannered as archived.
4. **`.claude/workflows/wave-*-groups.json`** hold the per-group briefs, and
   each group's `resume` field says where it restarts (`done`, `merge`,
   `review`, `fix`). These are consumed by `web-fix-wave.js`. A brief carries
   what a judge already established *and refuted* — reading only the issue body
   will have you implement a plan that was overturned.

## The contracts, which are not optional

- `tools/audit/briefs/fixer.md` — failing test first importing the production
  symbol; the mutation proof pasted; the finding's own harness re-run at both
  ends; a null control for any cost, gain or time claim; claims only for
  measured drift. After any rebase, steps 2–4 are re-executed, because the
  evidence described a different tree.
- `tools/audit/briefs/fix-review.md` — the reviewer measures with the
  **finder's** harness, never the fixer's, in a fresh worktree at the head SHA.
  Four implementations on this project looked right and were wrong, one worse
  than its bug.
- `tools/audit/briefs/judge.md` — a finding whose harness does not move under
  its own perturbation is **void**, whatever the votes said.
- `tests/README.md` — why a test that re-implements a formula pins nothing.

## Three things that have cost this project real time

- **`MODE: SCOPED — 0 script(s) run` and `MODE: FULL` both print zero** and mean
  opposite things. Key on the mode line, never the count.
- **Value-bearing golden fixtures are never re-recorded on a developer box.**
  Drift is *claimed*, with its direction, because only a canonical environment
  can honestly record a float. A name cannot be both claimed and may-drift.
- **Versions are assigned by `tools/release/stamp.py` after the merge**, never
  in a branch. Never touch `VERSION`, the manifest version, or the
  `RELEASE_NOTES.md` heading in a fix.

## The gate

`GATE_SCOPE=auto` runs only what the diff can reach, decided from the measured
closures in `tests/closures.json`. A push to `main` forces `full` — that
asymmetry is the safety argument, so a closure that is wrong makes main red
within one merge rather than never. `/tmp/hpo-gate.lock` serialises anything
that runs `tests/stress.py`; its owner file records a pid so that a *dead*
holder is a decidable fact rather than a judgement call.
