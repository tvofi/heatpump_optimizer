Fix review: merge 7c18ebb5575b227393272567b6cc27d96311916f

bus-nonce: 1ca8e6ba6967b3cefadbadb089b88812
pending-ci: gate

## Evidence

Round 2. This is a delta review over the reviewed head 2e97faf4c1d23d6ab0dd1013efa6d68d1a7dbf0d, which got `merge` in round 1. The packet's `## Review scope` reads `delta`. Merge base 265e061f65.
RESULT review_carry 2e97faf4c..7c18ebb55: FRESH-REVIEW. Four branch-only commits: three main merges (6dc615668, 1f676837e, 7c18ebb55) and one authored commit, cb3915f98 (ev/delta.txt).
RESULT delta cb3915f98: deletes two mutation-ledger dispositions, sysid.py `SystemIdentification.conditions_met` GUARD_OFF fa6ac820 (`if price > cutoff:`) and RETURN_DEL f2ae865e (`return True, "ready"`). Both `old` lines are absent from sysid.py at the head (grep rc 1) and present at origin/main 265e061 (lines 1562, 1564), so this PR's diff is what removed the sites. The five remaining `conditions_met` dispositions all name lines that are present at the head.
RESULT main merges: for 6dc615668 and 7c18ebb55, `git merge-tree --write-tree` of the parents equals the committed tree (337ca547, 1d9bd84d). There is no hand resolution. 1f676837e merges the authored commit cb3915f98 into its own parent.
RESULT PR production diff: the `custom_components/` lines of `git diff <merge-base>...<head>` are identical at 2e97faf4c and at 7c18ebb55.
RESULT widening: none owed. Main's delta touches four files this PR also changes: coordinator.py, pump_arbiter.py, sysid.py and store.py (#3931 dead-state, #3932 store part 2). The PR's diff references none of the identifiers main changed: `record_miss`, `_observe_frequency`, `adoption_decision`, `slab_mode_identifiability`, `_last_manual_setpoint`, `quantise_setpoint_c`, store `choice`/`_tries`. A signature change would be caught by CI's typing and fast lanes, so it is not a non-obvious risk.
RESULT tests / mutation at this head (job 140886168936): `MUTATION TABLE REFUSED -- 1506 unpinned site(s) against 1394 at the ratchet base 265e061f65..., 118 of them added by this diff`. No stale-disposition refusal remains: the previous head's three are gone, two by cb3915f98 and flow_lift.py BOOLOP 04143c3f by main's #3939. The remaining red is the added unpinned sites, red by construction and in mutation-autofix's lane, as the body's `## Red checks` and `## Unpinned sites` answer (ci-autofix.md) (ev/mutation-ci.txt).
RESULT budget-raise-gate: red at the head on the owner approval of the `module_excess_loc` raise, which round 1 judged under mandate 6893738184. The delta does not touch `tests/structure_budgets.json` beyond main's merge.
RESULT VERSION, manifest, RELEASE_NOTES and both claim files: untouched (merge-base...head stat empty). `git merge-tree --write-tree origin/main 7c18ebb55`: rc 0.
RESULT dev/governance/roles/ diff, merge-base...origin/main: empty, so the contract is current.
RESULT previous verdict's notes: all three are dismissed evidence or owed-red notes and nothing in them is open. The red-at-head note's survivor question stays in mutation-autofix's lane.
Step 1 (mutation proof): the delta writes no production line, so it draws no mutant. Round 1's mutants at 2e97faf4c carry, because the PR's production diff is byte-identical.
Steps 2, 3 and 6: the packet names no finder harness. Round 1 ran the fixer's m5_tankfall and draw_map_sweep at both ends. They are not re-run here because no production line moved.
RESULT CI: `merge_train.py classify 7c18ebb55 --pr 3933` printed `WAIT ... pending: gate red: none` on every poll from 06:49 to 07:16 UTC, 19 polls (ev/classify.log). The verdict returns with `pending-ci: gate` for the relay to post once the head is green.
