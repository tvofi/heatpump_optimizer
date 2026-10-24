# Fixer — the roster-sync reconciler (`state_docs.py beat --apply`)

Role: **fixer**, one fix. Repository `tvofi/heatpump_optimizer`. Read `dev/governance/roles/fixer.md` first:
failing test first, mutation proof, the finder's harness at both ends, a null control for every quantified claim,
`GATE_SCOPE=auto`, `tests/structure.py` before the push, and the handoff freezes the branch. **LOCAL seat only.**

## The ask (tvofi, 2026-10-20, recorded in `R10-ROSTER-OPS`'s brief)

> Make the FACTUAL half of roster upkeep mechanical inside the beat, leaving only reasoned edits to the
> orchestrator's sweep. Add a roster-sync step (a switch of its own, `--apply`) run by `state_docs.py beat` that
> derives only what the repository measures — a group whose `resume.branch` has a MERGED pull request becomes `done`
> at that merge commit; one whose `resume.branch` has an OPEN pull request becomes `in-progress` with its number —
> and appends a merged body's `Carry: <dest>` item into the destination group's `carry` array (reusing
> `carry_audit.py`'s parser, not a second one). It must never overwrite a human-written `deferred` or `refused`
> stage, must be a dry run by default with `--apply` to write, must print each change it would make, and must go
> out through `roster_edit.py`'s load-validate-dump and lint gate. Destination choice and the precondition wording
> stay the orchestrator's.

Why this exists: 12 complete handoffs sat unopened for up to 96 h while the roster recorded stale stages, and the
record was never compared to the refs. This step is that comparison. The design's `§6.4` (`dev/audit/design/
orch-machinery/DESIGN.md` at `handoff/orch-machinery 09174d94`) allocates it to this group.

## What to build

A `--apply`-gated step in `tools/audit/seat/state_docs.py beat` (and a one-shot form the tests can drive):

1. **Derive, per group, from the repository only**: `resume.branch` → the branch's pull request. MERGED → stage
   `done` at the merge commit (write `resume.commit`). OPEN → stage `in-progress` with the PR number. A branch with
   no PR makes no change — absence is not evidence.
2. **Never overwrite a human disposition**: a stage written as `deferred` or `refused` (and any other non-derived
   wording the roster uses) stays. Enumerate the values you protect from the live roster, not from memory.
3. **Carry append**: for a merged PR's body, parse `Carry: <dest>` with `carry_audit.py`'s parser (import it;
   a second parser is a refusal, not a shortcut) and append into the destination group's `carry` array, refusing
   a destination that is `done`. Destination choice stays human: the marker names it.
4. **Write path**: through `roster_edit.py`'s load-validate-dump and its lint gate, unchanged. Dry run by default:
   without `--apply` it prints every change it would make and writes nothing. `state_docs.py beat` runs it each
   pass when `--apply` is given.

## The tests this owes

- **Failing test first**: on the base, a group whose branch's PR merged still reads `in-progress` after a sync;
  the test fails there and passes after.
- **Mutation proof**, each arm independently red: (a) a `deferred` stage overwritten, (b) an OPEN PR not setting
  `in-progress`, (c) a merged PR not setting `done` at the merge commit, (d) a `Carry:` to a `done` group appended
  instead of refused, (e) a second parser used, (f) `--apply` absent yet bytes written. Show each mutant's `rc` and
  the failing test name.
- **Null control**: a no-op pass reproduces the roster's bytes exactly (`roster_edit.py`'s round-trip rule), and a
  branch with no PR changes nothing.
- **Offline**: the self-test must not reach the network; feed it recorded `gh` output fixtures. `selftest_wiring.py`
  must see your new self-test wired in `.github/workflows/` in the same pull request.

## Constraints

- `tools/audit/seat/state_docs.py`, `roster_edit.py`, `carry_audit.py` are code-owned paths: the owner reviews at
  merge; state the behaviour change and a one-line rollback in `## Approval`.
- Do not change `roster_edit.py`'s existing ops or their no-op behaviour; this adds a caller.
- No host path in any ref, message or body (#2310); no temp-path dependency (`tmp_paths.py` refuses one).
- The box is loaded; run the scoped gate with `GATE_SCOPE=auto`, state load1 beside wall-clock numbers, and prefer
  counts.

## Environment and handoff

Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/roster-sync` (absolute; create it). Worktree:
`git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/roster-sync/wt -B handoff/r10-roster-sync origin/main`.
`export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`. Push code to
`handoff/r10-roster-sync`, body to `handoff-body/r10-roster-sync`; every finding carries `Carry: <dest>` and
`carry_audit.py check --body` prints 0 unrouted. Report under 250 words.
