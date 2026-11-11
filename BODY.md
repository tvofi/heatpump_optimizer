Triage batch 183 rules queue lines 281-284, 2026-11-11. It holds four rulings.

- **P602, ACCEPT narrowed: CODEQL-PYTHON-CRITICAL-PATH, as a carry on R10-TICK-RESIDUE-P2.**
  - The carry adds a pulse line that names the single unfinished job against its baseline. Two near-complete python jobs (2173-3623 s) were cancelled at 10:29Z, misread as hung.
  - paths-ignore and a non-gating PR leg are routed to the owner. Each narrows the finding set or changes a required context, and `codeql.yml` already names the features.py split as an owner ruling.
- **P603, ACCEPT: OPENER-STALE-LEVEL-TIP, as a carry on R10-RELAY-ARM-ORDER.**
  - open_driver opens at the live tip on `moved`.
  - The log holds 18 SKIP moved lines over 2 topics, one of them the top-priority outside PR, starved 45 min.
- **P604, ACCEPT narrowed: SELFTEST-FORK-EXHAUSTION, as the new group R10-MUTANT-RUN-FORKCAP.**
  - `mutant_run` kills the command's group on timeout, but it has no process cap, and its 600 s default timeout outlasts the 4-min exhaustion.
  - The self-test re-entry guard is rejected, because it is itself mutable. A root-cause seat is rejected too: the launcher is identified.
- **P605, ACCEPT: CARRY-LANDED-OWN-GROUP, as a carry on R10-CARRY-AUDIT-P5.**
  - bus.sh carry_landed passes no `--topic`, so a part-N body's own-group status lines are refused CARRY-MISSING (#3448: 23 lines, one repair seat).

The diff is one file against the merge base: `dev/programme/triage/s6-batch183.md`, the ruling. No product behaviour changes.

## Head

`3a863c295285fda9502501a4bf22c918093d40c2`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P602-P605 as ACCEPT, and a citation of each passes (`None`).
- With the verdict flipped to REJECT in the file text, the P602 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P606 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...3a863c295285fda9502501a4bf22c918093d40c2`: 1 file, 1 commit.
- The figures come from three sources, each cited beside its command in the ruling:
  - `codeql.yml`, `open_driver.py`, `mutant_run.py`, `pr_args.sh`, `bus.sh` and `carry_audit.py` at `cbd23f1c8b`;
  - `open-driver.log`;
  - the orchestrator's CodeQL durations.

  Nothing was run to measure P604.

## Red checks

none

## Forward-carry

none

## Friction

none
