Triage batch 203 rules P631-P633 (queue lines 309-311; their own text numbers them 307-309), 2026-11-11. It holds three rulings.

- **P631, DEFER: bounding every instrument self-test.**
  - The one instance was two orphaned `roster_lib.py --self-test` processes, about 3.5% of the 8-core box for 4 h.
  - The launcher is unknown. The only tracked caller is governance.yml on a CI runner.
  - It is to be revisited with the next instance's parent captured, or the self-test's normal wall time measured.
- **P632, ACCEPT as a carry on R10-GATE-DEFER-BARRIER: a gate re-run's re-queued needs make its run busy() to every gate beside it.**
  - This is the producer side of the at-once deferral-red class that group barriers.
  - The group gains `tools/ci/gate.py` and an `after` on R10-HOTFIX-GATE-REDISPATCH-LOOP (#3473).
- **P633, ACCEPT as a carry on R10-TRAIN-REVIEW-PRESETTLE: re-admit a skipped train entry whose head moved by a carry range.**
  - `already_held` holds it at the same verdict, and bus.sh refuses a second reviewer. Today #3445, #3438 and #3454 have no route back onto the live train.

The diff is one file against the merge base: `dev/programme/triage/s6-batch203.md`, the rulings. No product behaviour changes.

## Head

`bd0632c9873ec087b58240a3ff1afae2afb4f0cf`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P632 and P633 as ACCEPT, and a citation of either passes (`None`).
- A citation of P631 is refused as "not an ACCEPT ruling (DEFER)".
- With P632's verdict text flipped, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P634 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ceb3070ccb...bd0632c9873ec087b58240a3ff1afae2afb4f0cf`: 1 file, 137 insertions, 1 commit.
- The figures come from:
  - the roster tip at 14:33Z;
  - `~/.local/state/hpo/merge_train/train.log`;
  - `seat/unstick-3445/MECHANISM.md`;
  - `git grep` at origin/main `ceb3070ccb`;
  - `sysctl -n hw.ncpu` and `uptime`.

## Red checks

none

## Forward-carry

none

## Friction

none
