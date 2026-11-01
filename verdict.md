Fix review: blocked 815039200ac5c5e353dc918e35443eb658830125 mutation-vacuous: check_plan's "closure stamp must be last" and "unknown stamp kind" arms and round_n's required keyword are pinned by no self-test row

bus-nonce: aa1392e575981a1404282bc612196fb1

Round 1.

## Block
The body claims `check_plan` refuses a closure stamp that is not the single last stamp and any stamp kind other than `patch` and `round-close`, and that `round_n` is a required keyword so no caller can omit it. I planted each of these in a copy of `tools/plan/replan.py` at the head. `replan.py --self-test` still printed "self-test: 0 failed" and exited 0 for all three:
- P3: `plan["stamps"][-1] is not closes[0]` removed from the closure test. No row plants a round-close stamp that is not last.
- P4: `"minor"` added to the accepted kinds. The self-test's wrong-closure rows all turn the last stamp itself into `minor`, so they trip the zero-closure arm and never reach the stray-kind arm. No row plants an extra stray stamp.
- P5: `round_n: int = 10` default. The call sites all pass `round_n`, so nothing pins its absence.
The three mutants the body lists, and my P1 (closure_version bumps minor) and P2 (round read from VERSION), are killed. Fix: add rows that plant (a) a round-close stamp followed by another stamp, (b) an extra `minor` stamp beside a correct closure, and (c) a `build_plan` call omitting `round_n` (expect TypeError), and add matching mutation-table rows.

## Evidence
- At the base the plan's last stamp is `v7.2.0` kind `minor`. At the head it is `v10.0.0` kind `round-close` with `generated.round` 10. I built both from the real roster with the same start time. Interim patch stamps are unchanged.
- `stamp.next_version('7.1.0', None, 10, 10)` returns 10.0.0. At VERSION 10.0.0 and at 11.0.0 it refuses "not above the current major". `replan.closure_version` refuses with the same message in both cases and also on a missing round. `stamp.py --round-close 10 --dry-run` itself refuses here (rule 1: head is not origin/main), so I compared against `next_version` directly.
- VERSION, the manifest and RELEASE_NOTES.md are untouched, and there are no golden or claim file changes. The diff is four files: replan.py, plan_page.py, state_docs.py and the delivery row.
- The replan, plan_page and state_docs self-tests all pass. Architecture score dS +0.0000 NULL, which matches the body. `structure.py` passes. Scope is `MODE: SCOPED -- 1 script(s) run`.
- The merge with origin/main is clean. The role-contract diff against main is empty. `merge_train.py classify` at the head prints GREEN, and the packet's whole gate digest is green with no red check, so the body's "Red checks: none" holds.
- The body does not claim the roster carry is closed. It says the roster disposition is the roster seat's op.
- I did not run the CI-only entities.py. That job is green in CI.
