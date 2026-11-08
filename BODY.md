R10-TICK-LEVELS part 2 (part of #201). Part 1 (#3200) is merged; this part builds the carries origin/main did not yet hold and gives the rest a one-line disposition. Six items were built: carries 13, 14 (tick), 7 (topic grammar, RCA, bugclasses), 15 (open cap, opener), 16 (owed_unactioned) and 17 (dispatch text). The two carries that touch the same tick seat as the settled ones (6, 7's RED-UNOWNED reader) are extended in place.

## Head

f641f97bd22fa315e51663415bc249a6f2a21585 (measured on this tree; origin/main 5bc009bc8 at the cut, `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main was not merged and prepr was not re-run for main's moves, by the owner ruling 2026-11-07).

## Dispositions of carries

The review packet numbers carries 1-18; the brief's own headings run "Carry 0" to "Carry 17", so packet N is the brief's heading N-1. Each was re-checked at 5bc009bc8 by reading the named symbol.

Already on origin/main (`[implemented: 6777ec33]` or read at the symbol), not rebuilt:
- Carry 1 (brief 0, approval-owed, review-stalled, record-branch skip, owed buckets): settled in `owed_levels`/`_bucket`.
- Carry 2 (brief 1, `ledger.review_owed` `skip_branch`, standing-dispatch.md sentence): settled.
- Carry 3 (brief 2, per-PR buckets with one OWED line, critical path first): settled.
- Carry 4 (brief 3, train-parked is owed): settled (`_parked`).
- Carry 6 (brief 5, BODY-AHEAD, RED-UNOWNED, FIRE-OWED): settled; its last clause (reconcile the fired-session ledger against the cloud run list, RETURN-MISSING) is not built: it needs a cloud run list this instrument cannot read. Destination: the dispatch seat's owner, by this note.
- Carry 8 (brief 7 is Carry 7 below; brief 6 = packet 7): the packet-7 definition of "a seat is on it" (FIRED line naming number, topic or payload file, or a moved handoff-wip/handoff/handoff-body ref) is `_seat_on`/`_fire_names`: settled.
- Carry 9 (brief 8, roster-group tick lines): settled.
- Carry 10 (brief 9, gate-race line instead of NOT REVIEWABLE): settled in `one_pr`.
- Carry 11 (brief 10, the line names `GATE_WAIT_MAX_S`): settled.
- Carry 12 (brief 11, a reviewer's `merge_train.py --self-test` is no merge race): settled in `_seat_procs`.
- Carry 18 (brief 17, fixer and reviewer text on a moved main): built here; fixer.md and fix-review.md step 13 already say merge-tree only, so no policy file changed.

Built here: Carry 7 (brief 6's reader, the tick's `_seat_on` reads `family`) and brief 7 (topic_grammar, packet carry 8, below), carries 13 (brief 12 is settled: `STUCK_FACTOR`, null started_at), 14, 15, 16, 17 as listed next.

## Built here

- Carry 14 (brief 13): `Tick._disposed` reads `lg.dispositions`; BODY-AHEAD does not owe when `refs/heads/handoff-body/<topic>` holds a disposition at the ref's sha; an older sha still owes.
- Carry 15 (brief 14): `blocked_stops` prints `OWED blocked-stop <topic> <sha12> <Question line>` for a `handoff-wip/<topic>` tip holding BLOCKED.md with no newer `dispatch/fixer-<topic>` and no disposition at the sha; `_seat_on` does not count such a tip; ledger.py gains the `blocked-stop` kind and the `handoff-wip/` arm; the fixer brief gains the BLOCKED.md sentence.
- Carry 8 (brief 7): tools/audit/seat/topic_grammar.py (`pr_topic`, `family`, `family_refs`, `group_of`, `owner_topic`, CLI `pr-topic` and `family-refs`); `noreturn_arm` counts a moved full-matching family member as a return; `open_driver.resolve` and `roster_sync.matches` call the moved rules unchanged; cloud_relay.sh calls `pr-topic`; `_seat_on` reads `family` for handoff-wip; dev/audit/rca/topic-family.md and the R10-TOPIC-FAMILY class with its `_rca` entry are landed (also registered in finding.schema.json and CLASS_GUESS, which the agreement lane requires).
- Carry 16 (brief 15): `pr_cap.counted` skips `triage:` and `roster:` titles; the opener skips `triage-` and `roster-` topics (`batched`).
- Carry 17 (brief 16): `owed_unactioned.key_of` keys the tick's `OWED <kind> #<n> <head12>` lines (every bucket kind), `OWED fire-owed <payload>` and `OWED blocked-stop <topic> <sha12>`.
- Carry 18 (brief 17): the rendered fixer text hands off at the first clean prepr.sh head and merges main only on a `git merge-tree --write-tree origin/main HEAD` conflict; the reviewer text blocks on main only on a merge-tree conflict.
- Carry 5 (brief 4, third blocked verdict owes a re-cut), Carry 13 (brief 12): settled as above (`RECUT_BLOCKED`; `Tick.stuck`).

## Mutation proof

Each mutated in place, the named self-test run, the file restored (command: /tmp mutation script, one `sed`-equivalent replacement per row):
- orchestrator_tick.py: drop `and not disposed` fails "carry 13"; drop the disposition read in `blocked_stops`, the dispatch comparison (`if newer`), the `_seat_on` BLOCKED.md exclusion, or the family wip read fails "carry 14" / "carry 7" (one check each).
- pr_cap.py: `("record:",)` fails the triage/roster row. open_driver.py: dropping the `SKIP_TOPIC_PREFIXES` test fails both batched rows. owed_unactioned.py: dropping the `OWED <kind> #n` arm raises Unreadable in the self-test.
- topic_grammar.py: counting a bare `-<N>` as a member fails 2 rows; matching by prefix fails 5. cloud_dispatch.py: restoring the unconditional merge sentence fails the first-clean-head row.
- cloud_relay.sh self-test: new rows r10-agreement-bootstrap (not reported), r10-roster-ops and r10-deeplink (reported), r10-quiet (null: reported).

## Null control

At the merge base (5bc009bc8) the same arms read: a body ref with a disposition still owes; a BLOCKED.md tip prints nothing; `noreturn_arm` fires on a seat that returned on `handoff/<topic>-p1`; a triage: title counts toward the cap; the fixer text instructs the merge on a moved main. The null rows above (older-sha disposition, newer dispatch, tip without the file, a family that moved nothing, a production title) keep the old behaviour.

## Figures

- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: all checks pass at this head.
- `python3 tools/audit/seat/topic_grammar.py --self-test`, `python3 -I tools/audit/seat/owed_unactioned.py --self-test`, `python3 -I tools/audit/seat/open_driver.py --self-test`, `python3 tools/audit/seat/pr_cap.py --self-test`, `python3 tools/audit/seat/cloud_dispatch.py --self-test`, `python3 tools/audit/seat/ledger.py --self-test`, `bash tools/audit/seat/cloud_relay.sh --self-test`: pass.
- `python3 tools/audit/fold_ledger.py check`: 0 violations.
- Diff-mutant run (\`tools/audit/seat/mutant_run.py --diff <base>...HEAD --max-mutants 40\`, MUTANT_CMD a \`bash -c\` chain of the five tick/opener/cap/grammar self-tests): wall time 4m24s, 20 survivors (listed under Unpinned sites).

## Unpinned sites

20 survivors, each dispositioned:
- cloud_dispatch.py:1056-1058 (4), open_driver_selftest.py:154-158 (4), open_driver.py:256 (1): mutations of test-side \`find\` bounds and \`pass\` call-deletes in the self-test lines themselves; the production predicates they test are killed by the mutation proof above. Value checks, no pin owed.
- orchestrator_tick.py:866 (\`age <= SEAT_WINDOW_MIN\` boundary): a minute-boundary value, same class as the existing window arms; not pinned.
- orchestrator_tick.py:933-947 (\`_dispatch_newer\`'s failed-read arms and its equal-timestamp edge, 12): the read-failure arms return None (the caller names it UNREADABLE) and the strict \`>\` is the stated rule (a dispatch committed in the same second as the tip is not newer). A tools/ site: mutation-autofix's lane mutates custom_components/ only, so these stay unpinned here and are the disposition-by-triage of this body; no behaviour change is claimed for them.

## Red checks

- \`governance / wave-script\` (AGREEMENT DIVERGENT \`finding-class-id "R10-TOPIC-FAMILY"\` and the class_guess GRADER line), predicted by \`ci_predict.py\` at this head: the base's copy of the agreement lane grades an edit to the lane's own enum, so it cannot see the registration this head carries in finding.schema.json and audit-find.js (RCA R10-RCA-2671-WAVE-SCRIPT cause 3); the head's copy has no local repair. No cheaper detector exists: the base-copy grading is the lane's design.
- \`governance / instrument-self-tests\` UNWIRED topic_grammar.py and \`tests / closures\` INERT READS: repaired in this diff (a governance.yml run line, \`ci_predict.py --apply-inert\`).

## Forward-carry

none

## Friction

none
