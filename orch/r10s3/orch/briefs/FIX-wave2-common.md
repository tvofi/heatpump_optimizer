# Fixer — one roster group of wave 2

Role: **fixer** for one pull request in one roster group. Repository `tvofi/heatpump_optimizer`.
**LOCAL seat only — cloud dispatch is forbidden in this session.**
Read `dev/governance/roles/fixer.md` first and follow it: failing test first, mutation proof, the finder's harness at
both ends, a null control for every quantified claim, `GATE_SCOPE=auto`, `tests/structure.py` before the push, and the
handoff freezes the branch.

## Your specification is your roster entry, not this file

```
git -C /Users/timmalmstrom/heatpump_optimizer fetch origin handoff/audit-r10-roster
git -C /Users/timmalmstrom/heatpump_optimizer show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json \
  | jq '.groups[]|select(.group=="<YOUR GROUP>")'
```

Its `brief` is the owner's own words for the work and its `carry` list is binding: every carry names a control
(a command and its expected output) and a re-measure instruction. Derive every set and count with the command the
carry gives; never carry a number or a name from the text. If a carry's control does not reproduce at your base, say
so in the body and the handoff report rather than working around it.

## Environment

- Scratch: **`/Users/timmalmstrom/hpo-seats/r10s3/<topic>`** (absolute; create it), worktree under it:
  `git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/<topic>/wt -B handoff/<topic> origin/main`.
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH` (pinned python 3.14).
- Instruments: `/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/` and `tools/pr/`; the inventory is
  `tools/audit/seat/INSTRUMENTS.md`. Do not hand-roll a loop, relay, queue, watcher or merge — look it up first.
- The box is shared: wall-clock numbers carry `load1`, and CI is the authority for anything heavy.

## Handoff

- Code head to `handoff/<topic>`, body to `handoff-body/<topic>` via `body_push.sh`. **You write no GitHub** — the
  orchestrator opens the pull request and dispatches the reviewer.
- The body owes the template's sections and, for every red the branch turns, the cheaper-detector answer under
  `## Red checks`. Every finding ends with `Carry: <GROUP>|#<issue>|dismissed: <reason>`, and
  `python3 -I tools/audit/carry_audit.py check --body <body>` must print 0 unrouted.
- No host path in a ref name, commit message or body (#2310): write `~/…`.
- If the pull request changes a code-owned path (`.github/CODEOWNERS`), or a policy path, write the body so the
  owner can approve it on its own terms — state what changes, why, the control that shows it, and the rollback.
- Report back to the orchestrator: both ref SHAs, each control's actual output, what you could not establish, and
  the one thing a reviewer should attack first.
