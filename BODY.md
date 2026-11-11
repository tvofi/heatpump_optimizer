Triage batch 167 rules queue line 264. It holds one ruling.

- **P581, ACCEPT (narrowed): BEAT-CHECKOUT-ROTATION-BY-HAND.**
  - The opener's log shows 8 of 25 open attempts (32%) in 20.4 h refused `STALE CHECKOUT` by `pr_args.sh:188`. The two refused topics that have opened since were delayed 36 and 48 min.
  - The carry goes to R10-SEAT-IDENTITY-P5. `beatd` restarts itself in place, on its branch-backed checkout, once it is behind on `tools/audit/seat` or `tools/pr` and no job instance is running. This is the shape of `tick_loop.sh`'s `fresh_check`, as P552 extended it.
  - The proposed rotate instrument rewrites `beatd.tools`, `orch-checkout` and the launch files. REJECTED: the in-place restart removes the same 8 refusals and rewrites nothing.

The diff is one file against the merge base: `dev/programme/triage/s6-batch167.md`, the ruling. No product behaviour changes.

## Head

`30d2c0fb1bdd313e1a05c5d49eda39209755606c`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P581 as ACCEPT, and a citation of P581 passes (`None`).
- With P581's verdict flipped to REJECT, the same citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P582 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".
- In the measurement, 17 of the 25 `RESULT` lines (all 14 `rc=0` among them) carry no `STALE CHECKOUT`, so the count does not read every refusal as this cause.

## Figures

- `git diff --stat a7628041dc...30d2c0fb1bdd313e1a05c5d49eda39209755606c`: 1 file, 1 commit.
- The figures come from `open-driver.log`'s `RESULT` lines (2026-11-10T09:50Z to 2026-11-11T06:12Z) and from `s14/sweep.md`'s `beat rotated` lines.
- No API calls.

## Red checks

`none`. The merge base is main `a7628041dc`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
