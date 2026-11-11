Triage batch 177 rules queue lines 273-275 and the P588 follow-up hour of the gh logging shim, 2026-11-11. It holds three rulings.

- **P594, ACCEPT, narrowed: GATE-SWEEP-QUEUE-WAIT.**
  - #3446's gate-sweep run was created 3 s after the green gate, but its job waited 10 min 38 s for a runner. The train settles for one 240 s poll.
  - The ruling adds a carry to R10-GATE-DEFER-BARRIER: a red GATE is a wait while a gate-sweep run created after the green is queued or running.
- **P595, ACCEPT: A5-ROLLUP-PAGES.**
  - `platform_gate` reads 100 rollup contexts and refuses `hasNextPage`. #3355 has 114, so it can never merge by the train.
  - The ruling adds a carry to R10-GATE-DEFER-BARRIER to page the rollup.
- **P596, ACCEPT: TICK-CONDITIONAL-READS, as the new not-started group R10-GH-READ-RESIDUE-P3.**
  - Core used is about 4390 an hour against 5000.
  - The tick's per-PR comment and check-run reads become ETag-conditional. A 304 is measured free. This removes an estimated 210-350 calls an hour.
  - The group also fixes the shim's caller field, which loses the script name, and records P591's second instance.

The diff is one file against the merge base: `dev/programme/triage/s6-batch177.md`, the ruling. No product behaviour changes.

## Head

`2cfc5a2886e9fee830d636a481626dba9c4f3c7b`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P594, P595 and P596 as ACCEPT, and a citation of each passes (`None`).
- With the verdict flipped to REJECT in the file text, the P594 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P597 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...2cfc5a2886e9fee830d636a481626dba9c4f3c7b`: 1 file, 1 commit.
- The figures come from the Actions API at #3446's head and for `gate-sweep.yml`, from `gh-calls.log` over 07:40-08:41Z, from `gh api rate_limit`, and from a 304-against-200 trial. Each is cited beside its source in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
