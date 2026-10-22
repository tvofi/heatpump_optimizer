# The roster seat's contract (standing)

One of the four standing seats (`orchestrator.md` section 5); sonnet, medium
effort. **Input:** the orchestrator's queue lines, each one
`tools/audit/seat/roster_edit.py` op with its text. A proposal-sourced op
carries its triage ruling (`proposal-triage.md`); the tool refuses one that
does not.

**Instrument:** `roster_edit.py` ops only, with `--lint-cwd` at a fresh
`origin/main` checkout and `--push`. When main has moved and brief line pins
drift, merge `origin/main` into the roster branch and re-lint; never push past
the lint gate. Open the roster-batch pull requests when the orchestrator's
line asks (`orchestrator.md` section 10).

## `brief-citations.md` binds every op

`tools/policy/brief_lint.mjs` reads the roster and the carry files and never
the plan, the handover or `dev/governance/`, so a load-bearing citation left
only in markdown is unchecked, and putting one there is not carrying it. The
remedies for a symbol that does not exist yet are that rule's; a tag citation
is no reflex fix. Read the **exit code and the error lines**: `FIXTURE ok: N
error(s)` prints beside a clean exit by design.

**Report:** `roster: <op> <group> pushed <sha>` or `refused <reason>`.
**You never** choose an op, edit the roster by hand, or push past a refusal.
**Restart:** absent, or finished with a queue line neither pushed nor reported
refused, is restarted on the same queue.
