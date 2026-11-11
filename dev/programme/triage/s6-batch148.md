# Proposal triage, session s14, batch 148 (P557 to P558)

This batch rules `s7/triage-queue-s7.txt` lines 241 and 242, which arrived after batch 147. The bar
and the denominators are batch 141's.

Sources: origin/main `d08ed31049`.

## P557: S14-BODY-PUSH-LANDED-MAIN-ONLY

Verdict: ACCEPT. It repairs an observed wrong behaviour: the code contradicts its own stated rule,
and returned fixers block with no PR.

Source: queue line 241 (2026-11-11T01:15:03Z, the orchestrator and the bodies seat).

Instances:
- **The stated rule.** `body_push.sh` lines 182-184 (CARRY 11, P287) say: "a body carry its group
  does not yet hold, on main's roster or the round's branch, is refused here".
- **What it runs.** Line 187 runs `carry_audit.py --roster-ref origin/main landed`.
  - `bus.sh` runs the same with `--roster-ref origin/main` at lines 236, 241 and 256.
  - `cloud_dispatch` renders briefs from the round branch (`roster_lib.reader_ref`).
  - So a carry added since the last roster landing on main is refused CARRY-LANDED (exit 4). The
    relay's fold then folds zero items, which are already on the branch, and refuses again on every
    pass.
- **The cost.** The source measured three of four returned fixers blocked with no PR (plan-page item
  4143bf92, tick a5ff6af4, train e3fd6216 three times). At the round ref the plan-page check reads
  0 missing. These figures are the source's.
- **The reader already exists.** `roster_lib.default_roster_ref` (line 287) names the round branch
  when the clone has it, and warns when main carries roster edits the branch lacks.

Cost: `carry_audit.py landed` counts a carry as landed when its group holds it on main's roster or
on the round branch, as the stated rule says.
- The round branch is the one `default_roster_ref` names when this clone has it.
- `body_push.sh` and `bus.sh` drop their hard-coded `--roster-ref origin/main`, so one rule serves
  both callers.
- Self-test:
  - a carry on the round branch only passes;
  - a carry on main only passes;
  - the null control: a carry on neither is refused, exit 4;
  - a mutant on each arm of the or.

Binding: one carry, R10-PREPR-RESIDUE (`body_push.sh` is on its seam), as a later part. The
orchestrator adds `tools/audit/seat/bus.sh` and `tools/audit/carry_audit.py` to its files. Carry
file: `b148-P557.txt`.

## P558: S14-CLOUD-PREPR-ENV-FAULTS

Verdict: DEFER. One instance, and the source itself marks it unverified.

Source: queue line 242 (2026-11-11T01:16:14Z, the R10-DEPENDABOT-3414-COMPAT cloud fixer's blocked
stop).

Instances:
- **The report.** In the cloud seat, `prepr.sh` refused on two faults:
  - `hooks stop-selfcheck.sh --self-test`: "fatal: bad config line 1 in file /dev/null";
  - `tests/entities.py` exit 1, from `tests/throwaway_git.py` `git init` (exit 128).
- **Unconfirmed.** The fixer says both also fail on clean origin/main `d08ed31049`. No second seat
  confirmed it, and other cloud fixers that hour reached `body_push`. So it may be a path only that
  diff's scope selects.
- **The cost.** One fixer fire. A local seat completed the handoff.

What would change it: a cloud probe seat running `prepr.sh` at origin/main reproduces either fault.
That would make it a repair of an observed wrong behaviour on R10-SUITE-ENV's seam (`cloud-setup.sh`,
or the two tests' git config isolation). Firing the probe is the orchestrator's call. The owning
group is R10-SUITE-ENV.

Binding: no carry.
