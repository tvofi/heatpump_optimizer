# R9-ORPHAN-HANDOFF: `bus.sh orphans`, the level-triggered obligation for the handoff family

A lane publishes its code on `handoff/<topic>` and its body on
`handoff-body/<topic>`. Nothing enumerates the obligation those refs mint:
`bus.sh watch` reports each ref's appearance once and mints no counterpart
check, so a lane's work can sit on the ref, `main` can not have it, and the
record still reads in-progress or `done`. The root-cause seat measured seven
such refs in one round, 9-90 seat-hours old, one of them costing a fresh opus
seat 5.13 seat-hours re-implementing work that already existed
(`dev/audit/rca/R9-ORPHAN-HANDOFF.md`). This lands the countermeasure the
analysis proposed: a new `bus.sh orphans` subcommand that asks the repository
for every ref at once, over the git protocol, token-free.

It reports three states and repairs nothing:

- **STRANDED** -- a `handoff-body/<t>` ref (the protocol's own statement that
  `handoff/<t>` owed a pull request) whose tip no pull request carries at
  `fix/<t>` or `fix/<t>-pr` and is no ancestor of `main` or a live head, older
  than `--min-age-h` (default 2). The line names the repair: `opener`
  (`open_pr.sh`), `update` (its pull request is behind the ref -- `update_pr.sh`)
  or `review` (a ref and its pull request diverged, a commit only one side has).
- **SUPERSEDED** -- flagged by the ancestry test, but a content-equivalence arm
  finds `main` already carries every path the ref's uncovered commits touch: a
  recovery rewrote the commit and landed the change under a moved path. It needs
  pruning, not an opener, and does not fail the run.
- **IN FLIGHT** -- inside the age window, a lane's own push, counted, never a
  line. Red is STRANDED only.

## Head

`1965925bbea7d959e20b249fabff509786f06cc4` -- measured against `origin/main` = `7cd5a588c` (2026-10-10).

## Mutation proof

`bus.sh --self-test` drives it. Disable the content-equivalence predicate in
`orphans` (the `&& content_superseded "$tip"` condition) and two arms go red --
the arm that names the superseded state, and the green arm, because the ref the
content arm spares then reads as stranded:

```
$ bash tools/audit/seat/bus.sh --self-test      # with the predicate disabled
  FAIL a ref whose file main already carries under a moved path is SUPERSEDED
  FAIL green: with the pull requests pushed nothing is stranded and the run is 0
bus self-test: 53 checks, 2 failed
```

Restored, the whole suite is green (Figures). The two live-remote junctures are
mutated too, by deletion, in Figures: dropping the ancestry juncture adds 45
refs whose content `main` already has, and dropping the body juncture adds 111
refs that never owed a pull request -- the ~45 and ~112 the analysis measured.

## Null control

- **A handoff ref with no `handoff-body/<t>` ref is never owed**: 161 of the 212
  handoff refs carry no body ref this pass, and every one is silent. Depends on
  the OWED juncture (`--no-body` drops it and the run floods; Figures).
- **A ref inside the two-hour window is in flight, not an orphan**: `young=1`
  this pass, silently counted, no line. The self-test pins it hermetically:
  after the red arm, the same ref at the default window reports 0 and `young=1`.
- **The green arm is a repaired remote, not an exclusion**: the self-test pushes
  the carrying pull requests for every stranded ref and asserts `0 stranded`,
  exit 0 -- not `--exclude-topic`, which the analysis says is a fixture hook, not
  a control.

## Figures

Re-taken 2026-10-10 against the live remote, `origin/main` = `7cd5a588c`; the
remote is live (this class regenerated during the session), so the counts are a
function of that tip and the clock.

- `bash tools/audit/seat/bus.sh --self-test` -> `bus self-test: 53 checks, 0 failed`.
- `bash tools/audit/seat/bus.sh orphans` -> `orphans: 10 stranded, 1 superseded; skipped no-body=161 named=4 ancestor=44 young=1`, exit 1. The stranded lines name `repair=opener` (8), `repair=update` (`r9-early-cutoff`, its PR #2070 behind its own round 4) and `repair=review` (`r9-cop-duty-floor`, ref and PR diverged); `r9-eg-coordinator-seams` is the `SUPERSEDED` line.
- `bash tools/audit/seat/bus.sh orphans --no-content` -> `12 stranded, 0 superseded`. The content arm is load-bearing: `r9-eg-coordinator-seams` moves stranded->superseded and no other ref moves.
- `bash tools/audit/seat/bus.sh orphans --no-ancestry --no-content` -> `55 stranded` -- 45 more than the 10 the ancestry juncture leaves, the false positives the analysis measured (refs whose content `main` already carries).
- `bash tools/audit/seat/bus.sh orphans --no-body --no-content` -> `121 stranded` -- 111 more, refs (planning, state, prototype) that never owed a pull request, the ~112 the brief names.
- `python3 -I tools/audit/fold_ledger.py check` -> `fold_ledger: 29 classes, 556 instances, 39 in-tree judge survivors (rounds [8]), 102 rca entries` / `fold_ledger: 0 violation(s)`.
- `python3 -I tools/audit/fold_ledger.py --self-test` -> rc 0.
- `node tools/policy/check-wave-script.mjs` -> `172 passed, 0 failed` (the class_guess enum equals the ledger ids plus `new`).
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs` -> `TOTAL: 0 error(s) across 40 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check` -> `RULES-SYNC ok`.

## Red checks

- `budget-raise-gate` -- **red by design**. `policy_budgets.json` raises six
  caps (the two changed policy files' per-file caps, and the `corpus_tokens`
  and `role record` aggregates, every one to its measured value) to make room
  for the two policy diffs; the gate clears on tvofi's approval at the head
  (0013). Cheaper detector: **none** -- `budget-raise-gate` _is_ the detector
  the rule names for a raise (`.claude/rules/ratchet-budgets.md`), and it is the
  cheapest place the raise can be caught.

## Forward-carry

The finding binds every orchestrator turn, so its destination is the role
contract, once (`finding-propagation.md`): `dev/governance/roles/orchestrator.md`
section 5b, "Before dispatching a seat to a lane, read the ref, not the record",
and `dev/governance/rules/delivery-status-tracking.md`, "a row's status word is
reconciled by nothing". Both are **policy** and await the owner.

## Approval

**Owed, not yet given.** Both `orchestrator.md` and
`delivery-status-tracking.md` are policy (`CLAUDE.md`): a change to them needs
the owner's approving review before merging, which the orchestrator posts under
mandate 6067089637; and `policy_budgets.json`'s raise is owner-gated with it
(`budget-raise-gate`, 0013). I judge both right and applied them; the argument
for each:

- **orchestrator.md 5b** -- the finding invalidates an assumption the
  orchestrator's dispatch rests on (the roster's `branch` resolves, a row
  reading `open` means the pull request is open). It binds every turn, so it
  goes to the role contract once, not to each stage's brief.
- **delivery-status-tracking.md** -- the rule already says "status stays true";
  the measurement is that a row's *word* is graded by nothing, and the
  instrument is named.

**Budget.** The two capped policy files sit at zero headroom by design
(`policy_budgets.json` `_band_note`: "per-file caps are compared exactly"),
so adding the obligations requires raising the caps. `policy_budgets.json`
raises `.claude/rules/delivery-status-tracking.md` 26->35 lines and 606->766
tokens, `tools/audit/briefs/orchestrator.md` 291->316 lines and 4096->4462
tokens, and the `corpus_tokens`/`role record` aggregates to their measured
values -- all to the measured values. This raise is owner-gated with the policy
(`budget-raise-gate`, 0013).

**Payments considered and not taken, measured:** neither file holds spendable
prose -- `dev/governance/roles/orchestrator.md` is 290 lines of load-bearing
obligation with no historical narrative to delete (read in full); the
delivery-status rule is 26 lines. Deferring the diffs to a carry file would
misroute a finding that binds every seat (`finding-propagation.md`: "constrains
every seat -> the role contract", and a comment or carry is not propagation).

## Friction

- `tools/audit/seat/bus.sh`: cost: merging `handoff/r9-bus-fetchhead`
  (`ea69cee3`) into `handoff/r9-orphans` conflicts in `bus.sh` -- both lanes add
  to the same `local` line in `self_test` and both append their arms at the same
  anchor (my orphans arms; its append_commit/poster arms). Reported and stopped,
  not side-picked, per the brief: a shared-line conflict is the shape this class
  is about. My `bus.sh` edits are the `orphans` subcommand alone (function,
  dispatcher entry, one header paragraph, the appended self-test arms); the
  sibling owns `append_commit`, `ROOT` and the poster. The two are independent
  and combine by union.
