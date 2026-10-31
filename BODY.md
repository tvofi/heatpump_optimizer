Triage batch 86 rules the orchestrator s8's slip proposal of 2026-10-31 (~04:30Z). The dispatch seat ran `pkill -f` with an empty pattern while restarting its watch loop. No other process died. The seat preamble and a memory note both forbid it already, and an earlier instance did kill processes. This is the next rolling batch after batch 85, with one ruling and one held roster op.

- **P323: ACCEPT narrowed**, as a new fly-in group R10-FLY-BASH-KILL-GUARD (S).
  - A PreToolUse hook on the `Bash` tool refuses `pkill` (any arguments), `killall`, and `kill` fed by `pgrep`. It refuses them at command position only, and allows `kill <pid>`, `kill $!` and a pidfile.
  - A bash prefilter exits early on any command without `kill`, measured at about 3 ms per call. A python start costs about 26 ms.
  - The same PR fixes `policy_lint.mjs`'s hooks check, which tests every PreToolUse matcher against the edit tools and would report a `Bash` matcher as `MATCHER BLIND`.
  - The hook files are code-owned, so the PR merges on tvofi's review or under mandate 6329234399.
  - A local seat loads hooks from the main checkout, so the hook takes effect there once that checkout advances. The ruling names a host-level interim as the orchestrator's call.
  - REJECTED: a firmer preamble sentence. The rule is already stated twice and was broken a second time, which is process state (b).

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`a85408ac69881df06ddfa90ac9780e007ff7edb0`; the file is the whole diff against `851d1ce6b`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P323 as `ACCEPT`. `triage_refusal` passes the new group's brief, which cites `triage: dev/programme/triage/s6-batch86.md#P323`: it returns None.
- With `Verdict: ACCEPT narrowed` changed to `Verdict: REJECT`, the same brief is refused: `dev/programme/triage/s6-batch86.md#P323 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main. The group, appended to the live roster, gives `brief_lint.mjs` `TOTAL: 0 error(s)`.

## Figures

- `git grep -nwE 'pkill|killall' origin/main -- tools/ .claude/hooks/ .github/` finds prose only: the reviewer prompt and its self-test row in `cloud_dispatch.py`, and a comment in `pr_args.sh`. There is no call site.
- `git show origin/main:.claude/settings.json` wires one PreToolUse group, matcher `Edit|Write|MultiEdit|NotebookEdit`, and no Bash hook.
- On this host, 20 `python3 -c 'import json,sys'` runs took 0.52 s and 20 bash `case` runs took 0.056 s.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
