# BLOCKED: r11-seam-actuation-release

Question: which spelling of a round-11 group does a body's `Carry:` marker take, or does the relay fold these three carries? The dispatch brief lists `R11-SEAM-actuation-writes` and `R11-SEAM-kernel-step` as valid targets; `tools/audit/carry_audit.py`'s `GROUP_TOK` (`[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+`) reads a mixed-case id as no marker, and the upper-cased id is refused as no group of the roster. This seat may not write the roster or the grader.

Code head: 5dd27cfd07c5a5c655d1429be3fac51200d089b7 (this commit's parent), every commit of it on this ref. Not pushed to `handoff/r11-seam-actuation-release`: `tools/pr/prepr.sh` is clean at that head except for the carry check below, so no clean prepr head exists to hand off. The finished body is on `handoff-wip/r11-seam-actuation-release-body` (`BODY.md`, its `## Head` naming the code head); `body_push.sh` was not run, because with no `handoff/` ref on origin it would publish the body as a result body with the lint skipped.

## prepr.sh at the code head (`PREPR_SKIP_CLOSURES=1`, `MUTANT_CMD` the R11 section of `tests/features.py`)

```
    |            PREDICT pr-contract / pr-contract CARRY UNROUTED item 4668e1fd: '- `tests/features.py`: design invariant 2, for the group that reads the held rec'
    |            PREDICT pr-contract / pr-contract CARRY UNROUTED item 18104ee6: '- `custom_components/heatpump_optimizer/pump_arbiter.py`: the GCHV night-schedul'
    |            PREDICT pr-contract / pr-contract CARRY UNROUTED item 5553038e: '- `custom_components/heatpump_optimizer/pump_arbiter.py`: shared with R11-SEAM-k'
  REFUSE   ci predict             CI PREDICT: 3 predicted red(s) on pr-contract / pr-contract against 8751943e17ef -- repair before the handoff; the lines above name each arm's repair
  REFUSE   carry                  UNROUTED body item 4668e1fd (## Forward-carry) [section]: '- `tests/features.py`: design invariant 2, for the group that reads the held record after a release. After a r' -- CARRY-AUDIT: 7 finding item(s): 4 routed, 3 unrouted, 0 bad destination(s), at origin/handoff/audit-r10-roster 53871a0b84
PRE-PR: 5dd27cfd07c5a5c655d1429be3fac51200d089b7 0000000000000000000000001000000000010 rc=1; full log: /tmp/prepr-log.SDY6Zepd (PREPR_VERBOSE=1 prints it on stdout)
```

## carry_audit.py check, the body as written (the brief's spelling)

```
NOTE stale tree: 5dd27cfd07c5a5c655d1429be3fac51200d089b7 lacks origin/main 1723f9fdc9d8a6e6987190d2887686297a621dd4; roster read at origin/main
UNROUTED body item 4668e1fd (## Forward-carry) [section]: '- `tests/features.py`: design invariant 2, for the group that reads the held record after a release. After a r'
UNROUTED body item 18104ee6 (## Forward-carry) [section]: '- `custom_components/heatpump_optimizer/pump_arbiter.py`: the GCHV night-schedule registers (`_write_night_sch'
UNROUTED body item 5553038e (## Forward-carry) [section]: '- `custom_components/heatpump_optimizer/pump_arbiter.py`: shared with R11-SEAM-kernel-step with no edge; the s'
NOTE body item 090ab501: dismissed:recorded above as pending owner confirmation
NOTE body item 1763c92f: dismissed:one harness, stated with its command
NOTE body item f5eea194: dismissed:reported to the relay with the audit's output
NOTE body item 44317a41: dismissed:repaired in this diff
CARRY-AUDIT: 7 finding item(s): 4 routed, 3 unrouted, 0 bad destination(s)
```

## carry_audit.py check, the same body with the two group ids upper-cased

```
NOTE stale tree: 5dd27cfd07c5a5c655d1429be3fac51200d089b7 lacks origin/main 1723f9fdc9d8a6e6987190d2887686297a621dd4; roster read at origin/main
BAD-DEST body item d834f832: R11-SEAM-ACTUATION-WRITES: R11-SEAM-ACTUATION-WRITES is not a group of the roster or of origin/handoff/audit-r10-roster
BAD-DEST body item e92a6d03: R11-SEAM-ACTUATION-WRITES: R11-SEAM-ACTUATION-WRITES is not a group of the roster or of origin/handoff/audit-r10-roster
BAD-DEST body item 906b9289: R11-SEAM-KERNEL-STEP: R11-SEAM-KERNEL-STEP is not a group of the roster or of origin/handoff/audit-r10-roster
NOTE body item 090ab501: dismissed:recorded above as pending owner confirmation
NOTE body item 1763c92f: dismissed:one harness, stated with its command
NOTE body item f5eea194: dismissed:reported to the relay with the audit's output
NOTE body item 44317a41: dismissed:repaired in this diff
CARRY-AUDIT: 7 finding item(s): 4 routed, 0 unrouted, 3 bad destination(s)
```

## The three carries

They are the body's `## Forward-carry` items: design invariant 2 with its control, owed to R11-SEAM-actuation-writes by the design note; the GCHV night-schedule registers, which arm the arbiter's row and are not written back; and the re-run of the finder's restore harness owed by the second of this group and R11-SEAM-kernel-step to merge. `origin/handoff/audit-r10-roster` holds `dev/programme/rosters/wave-r11-groups.json` with both groups, spelled as the brief spells them.

## What resumes the handoff

With the carries folded on the roster, or the marker's spelling settled: re-render nothing but the three `Carry:` tokens, run `tools/pr/prepr.sh` on the body, push the code head to `handoff/r11-seam-actuation-release`, then `bash tools/audit/seat/body_push.sh r11-seam-actuation-release BODY.md`.
