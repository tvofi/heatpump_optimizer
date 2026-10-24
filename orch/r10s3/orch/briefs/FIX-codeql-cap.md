# Fixer — the CodeQL python leg's 30-minute cap

Role: **fixer**, one fix. Repository `tvofi/heatpump_optimizer`. Read `dev/governance/roles/fixer.md` before you start:
failing test first, mutation proof, the finder's harness at both ends, a null control for every quantified claim,
`GATE_SCOPE=auto`, `tests/structure.py` before the push, and the handoff freezes the branch.
**LOCAL seat only — cloud dispatch is forbidden in this session.**

## The defect, measured

`Analyze (python)` in `.github/workflows/codeql.yml` is a **required context** (ruleset `main-protect-checks`,
23698884). The `analyze` job carries `timeout-minutes: 30`, brought in with the workflow-based CodeQL migration
(`bc6866fae`). The python leg now needs more than that. Three cancellations at the cap today:

| sha | started | concluded | elapsed |
|---|---|---|---|
| `2bd5e90f` (main, #2485's merge) | 14:09:00Z | 14:39:19Z | 30:19 |
| `4e5801eb` (main) | 14:17:24Z | 14:47:33Z | 30:09 |
| `916431ae` (#2488 head) | 14:34:41Z | 15:04:48Z | 30:07 |

Job ids: 118679535262 (`4e5801eb`), and runs 39436564344 / 39437802530 / 39434809989.

The cancelled job's log shows it was **nearly finished, not hung** (`4e5801eb`, job 118679535262): extraction
14:17–14:19, a nine-minute quiet stretch to 14:28, TRAP import 14:33, `[6/52]` at 14:34, `[8/52 eval 7m20s]` at
14:41, `[42/52 eval 11m31s]` at 14:45, `Uploading code scanning results` 14:46, `##[error]The operation was
canceled.` 14:47:30. The post-step then wrote `CodeQL job status was configuration error`, which is what a
cancelled analysis reports, not a configuration fault of ours.

## The fix

Raise the `analyze` job's `timeout-minutes` from 30 to **45** in `.github/workflows/codeql.yml`, with a short comment
naming what measured it (the three timestamps above, and the date 2026-10-20) so the next reader does not shrink it
back. 45 leaves ~11 minutes over the longest observed run. Do not touch the other jobs' timeouts; `scope` (5) and
`cancel-superseded` (2) are unrelated.

Is there a sounder fix than a bigger cap? The nine-minute quiet stretch is worth one look — if a single file or an
extractor setting makes extraction pathological, say so in the body under `## Friction` and carry it; do not widen
the scope of this fix to chase it.

## Test first, and the pin

A cap with nothing pinning it will drift back. Add a check that parses `.github/workflows/codeql.yml` and refuses an
`analyze` timeout below **45**. Find the existing workflow-shaped check in `tests/` (grep for `codeql.yml` and for
`yaml.safe_load` under `tests/`) and extend it rather than inventing a new runner; if you add a file, it must be
**deliberately classified** — put it in a measured closure or on `tests/closure.py`'s `INERT` list, or
`tests/entities.py` fails with *"these force the FULL suite when touched"*.

- **Planted failing case**: set the value to 30 in a scratch copy (never commit it) and show the check exits 1.
- **Mutation proof**: the same mutant, with its `rc` before and after.
- **Null control**: the unmodified file passes, and every other job's timeout in the file is unchanged.

## Red-check answer — owed

This defect turned required checks red on a condition a cheaper detector could have surfaced (the job's own elapsed
time vs. its cap). Answer it in the body's `## Red checks`: name `Analyze (python)` and the pin above as the cheaper
detector.

## Environment

- Scratch: **`/Users/timmalmstrom/hpo-seats/r10s3/codeql-cap`** (absolute; create it). Worktree under it:
  `git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/codeql-cap/wt -B handoff/r10-codeql-cap origin/main`.
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH` so the seat python is the pinned 3.14.
- Instruments: `tools/audit/seat/` (see `INSTRUMENTS.md`) and `tools/pr/`. Do not hand-roll a loop, queue or watcher.
- CI is the authority for the workflow change itself: only a fresh `Analyze (python)` run can show the new cap works,
  and it will run on your PR head.

## Handoff

- Push the code head to `handoff/r10-codeql-cap` and the body to `handoff-body/r10-codeql-cap` with `body_push.sh`.
  The orchestrator opens the pull request — **you write no GitHub**.
- The body owes the template's sections (`## Head`, `## Mutation proof`, `## Null control`, `## Figures`,
  `## Red checks`, `## Forward-carry`, `## Friction`); every figure with the command that printed it; every finding a
  `Carry: <dest>` marker, and `carry_audit.py check --body <body>` must print 0 unrouted.
- **No host path anywhere** in a ref name, commit message or body (#2310): write `~/…`, never the absolute path.
- The **root cause is a separate seat** (it runs beside a fix, never inside it). Do not write a cause analysis; record
  what you measured under `## Figures` and leave the process question alone.
- Report back: both ref SHAs, the mutant's `rc` before and after, the null-control result, and anything you could not
  establish.
