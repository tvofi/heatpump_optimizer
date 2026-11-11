Fix review: blocked 68646456c774b1d0e58e6c79f6fd0a38281d334c carry-missing: the roster carry for R10-ECL110-MQTT-OFF-NEUTRAL is on the branch but reads "the sibling publish sites above", which names nothing in the roster, and the body gives no roster branch SHA

bus-nonce: c9cdd61a64ba8c50f284d4cb7a65bffe

Round 2 (delta re-check, no pull request yet, so no review packet and no CI). Delta b3b51d42..68646456c774b1d0e58e6c79f6fd0a38281d334c is one commit, one file: tests/mutation_ledger/killed_by/pump_arbiter.py/cycle_supply.RETURN_DEL.011422a2.json (ev/delta-stat.txt). No production or test code changed.

## Block

The earlier block was: the item was not carried to R10-ECL110-MQTT-OFF-NEUTRAL. Partly repaired. The group's entry on origin/handoff/audit-r10-roster (ff4fefa44ebd4459797490bf65db37e133a63588) now has a `carry` item "From r10-outside-supply-stale-step, body item 30ec8edf" (ev/roster-carry-entry.txt). Two defects remain under finding-propagation.md:

1. The carry's text is the body line verbatim: "The sibling publish sites above land in the R10-ECL110-MQTT-OFF-NEUTRAL group". In the roster nothing is "above". It names neither `async_publish_current_action` (displace value and set-point of the earlier step) nor the legacy payload's `heat_pump_on` that can disagree with the switch for a landing step, nor pull request 3457 or `cycle_supply`. The fixer of that group cannot act on it. The group's `brief` still covers only off/unload neutrality. The carry must say what the two sites are and give their control (a cycle landing one step late: compare the published `heat_pump_on` and displace against the switch write, null control the same cycle inside its step).
2. The body's `## Forward-carry` names the file and the group but not the roster branch SHA, which the rule requires ("The body names the file, the stage and (a roster carry) the branch SHA"). The body is unchanged on this point from the blocked round (ev/body-forward-carry.txt).

Repair: rewrite the roster carry to name both sites, and add the SHA of handoff/audit-r10-roster carrying it to the body.

## Findings

- The two earlier findings (vacuous `stale plan` null control wording under `## Unpinned sites`; no committed finder's harness) were dismissed there and are unchanged; the delta touches neither. Carry: dismissed: settled in the previous round, no production behaviour at stake

## Evidence

- RESULT delta: the only added file is the ledger row pinning cycle_supply RETURN_DEL, killed_by tests/typing_ruler.py, matching the body's `## Unpinned sites` claim in form. I did not re-run mutation_table.py --pin-killed (the body says it needed a locally raised census bound); the row's anchor and old line match "return on if step is None else step". Mutation proof and null controls from round 1 stand because no code changed.
- RESULT merge: `git merge-tree --write-tree origin/main 68646456c774b1d0e58e6c79f6fd0a38281d334c` rc=0, no conflict (ev/merge-tree.txt).
- Reds: no CI exists before the pull request opens. The body answers `tests / fast` as the inherited combi census (PR 3466); not re-run in this delta.
- Body Code line equals the tip 68646456c774b1d0e58e6c79f6fd0a38281d334c.
