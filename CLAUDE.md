# Working on this repository

A session loads this file automatically. It exists because a resumability audit
found that every one of its auditors had to be *told* what to fetch before it
could work out what was in force.

Everything in this section is **permanent** — it describes the repository, not
any particular piece of work. Anything dated lives in the fenced block at the
bottom, which is allowed to go stale and says so.

**This file is not the whole of what applies.** `.cursor/rules/*.mdc` hold four
`alwaysApply: true` project policies — `delivery-status-tracking.mdc`,
`ci-autofix.mdc`, `brief-citations.mdc`, `defect-root-cause.mdc`. Cursor loaded them for you; Claude Code
loads only this file, so **open all three yourself at session start**. The
sections below summarise them and cite them by name; a summary is not the policy.

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
   class fails — and the correct response is to pay for the lines, to re-record
   deliberately with the reason **in the commit message**, or, for a genuine new
   production feature, to **raise the budget with the repository owner's
   explicit confirmation, obtained before the branch is pushed** — never to
   loosen a budget quietly, and never to delete working functionality merely to
   fit. Pay for the lines first; a raise is what you do when the honest answer
   is that you cannot, and an agent that wants one stops and asks rather than
   pushing and explaining. `cross_seam_fraction` is a tolerance metric and is
   never re-recorded.
3. **Value-bearing golden fixtures are claimed, not re-recorded.** Solver floats
   do not reproduce across BLAS builds, so only a canonical environment can
   honestly record one. Drift is declared in `tests/golden/claimed_drift.txt`
   (or `card_claimed_drift.txt`) with its direction, and `claims-for:` must equal
   `VERSION`. A fixture cannot be both claimed and may-drift — `env_drift.py`
   refuses that. Check claims — and any branch-vs-main comparison — three-dot
   (`git diff $(git merge-base origin/main HEAD)...HEAD`), never two-dot:
   two-dot shows main's own newer commits as if the branch had made them.
4. **Versions are assigned after the merge, by `tools/release/stamp.py`.** Never
   touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading in a
   branch. The stamp has its own refusal rules, including one that rejects notes
   omitting any merged PR.

A new tracked file must be **deliberately classified** — put in a measured
closure, or on `tests/closure.py`'s `INERT` list — or `tests/entities.py` fails
with *"these force the FULL suite when touched"*.

## Programme tracking (#201)

After each programme merge — wave group, tooling the plan tracks, or a closed
tracked issue — the same session or an immediate record PR updates
`docs/plan-2026-09-open-issues.md` Delivery-status (authoritative vs wave
body; if they disagree, fix the table first), the roster `resume` fields in
`.claude/workflows/wave-*-groups.json`, and posts one #201 comment per
meaningful state change (merge, block, wave start). Do not wait for a stamp
to truth the table. See `.cursor/rules/delivery-status-tracking.mdc`.

## Programme plans and the brief linter

Load-bearing citations go in `.claude/workflows/wave-*-groups.json` in a form
`node .claude/workflows/brief_lint.mjs` can resolve (that path is what #416
lands; run it locally the same way). The linter does not read `docs/plan-*.md`
or `tools/audit/briefs/`. Extending the plan format means extending the linter
in the same PR.

## Root-cause remediation

A defect that reached a released version, or that turned a PR red on a check a
cheaper detector could have run, owes two things beyond its fix: the cause, and
the **process** that let the cause get that far. The process failure is in one
of four states — the process did not exist, existed and was not followed, was
followed and did not work, or was sound and its preconditions changed — and the
countermeasure differs by state. Build one only when it pays for itself against
the measured recurrence of its class; **recording that none is worth building is
a legitimate result**. Any countermeasure that is a check must be demonstrated
failing on the defect it was written for.

The analysis runs in **its own seat**, beside the fix and never inside it:
`tools/audit/briefs/root-cause.md`. Policy is `.cursor/rules/defect-root-cause.mdc`.
Repository rules and policy change only with the owner's approval.

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
`stress.py` does not need it. Use `tests/gate_lock.py` — not `mkdir` and a
shell pid:

```
python3 tests/gate_lock.py take --label <your-label>
HPO_GATE_LOCK_LABEL=<your-label> GATE_SCOPE=auto GOLDEN_MODE=drift \
  GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
python3 tests/gate_lock.py renew --label <your-label>   # between commands
python3 tests/gate_lock.py release --label <your-label>
```

The owner file carries your label and an `expires_at` lease (30 minutes, above
the longest observed gate). Every script under lock renews it; an expired lease
or an abandoned hold (`holding` marker, no live flock) may be taken without
forensics. `run.sh` holds `flock` for the gate run so a crash drops flock and
a waiter can take immediately — the lease covers the window between commands
when nothing holds flock (#404).

Node lanes (`tests/card.mjs`, `tests/card_drift.mjs`) record on Darwin via
`node --import tests/node_fs_trace.mjs` (Node `fs` / loader, not `strace`).
`--single` of an existing node script **unions** into the committed list;
it cannot shrink a Linux `strace` closure. Python closures re-derive locally
as before. Do not Darwin `--single` a CI `UNDER-SCOPED` — autofix already
has the Linux recordings.

## CI already repairs two mechanical failures — do not re-implement them

`.github/workflows/tests.yml` jobs `closures-autofix` and `claims-autofix`
already exist on same-repo PRs. Do **not** open a second PR, run Darwin
`--single`, or hand-empty claim files for these. Wait for the bot commit
(`ci: re-record closures` / `ci: drop inherited claims`) and the dispatched
recheck. Loop-guarded: those subjects are not repaired again.

- **`UNDER-SCOPED`:** `closures` already recorded under strace. Autofix
  merges those recordings into `tests/closures.json` and retriggers Tests.
  Policy: `closure.py` `apply_under_scoped_recordings`.
- **`INHERITED CLAIMS`:** a list identical to `origin/main`. Autofix deletes
  bare claim lines, keeps `claims-for:` and `# may-drift:`. Policy:
  `env_drift.py` `apply_inherited_claims`.

Not automated (still a human/agent judgment): golden drift, structure
budgets, `no-copies`, orphans → `INERT`, briefs lint, a failed recording,
an INERT contradiction. Do not add a third autofix job without a new
mechanical, uniquely-detected failure.

See `.cursor/rules/ci-autofix.mdc` and `tests/README.md` (scoped gate).

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
