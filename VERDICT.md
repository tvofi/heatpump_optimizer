Fix review: merge cf687605d2678912b80d7e4c909b2471f32a680b

bus-nonce: c9b0df972a73e7e46b9b421307817f0c

Round 1: no `Fix review:` comment or review exists on #2419 (issue comments and reviews read empty at 2026-10-19T02:2xZ).
Measured head: cf687605d2678912b80d7e4c909b2471f32a680b (ev/HEAD); refs/pull/2419/head still there at write time.
Contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the fix-review.md I read is current.

## Resolution delta (orchestrator's main merge)
- 99cec61c2 (merge of code head 758b6152) has the same tree as 758b6152.
- cf687605 has the same tree as `git merge-tree --write-tree origin/main 758b6152`: an empty diff. The main merge is a clean automatic merge with no resolution.
- `git merge-tree --write-tree origin/main cf687605`: exit 0, no conflict, and no claim file involved (ev/merge_tree.txt).

## Mutation proof (step 1), my own mutants on this pass's added lines (ev/mutants.txt, ev/mutant_runner.sh)
18 mutants; the baseline is `cloud_relay self-test: 69 checks, 0 failed`.
- 17 of 18 were KILLED. Each body-named mutant reproduced with the named checks failing: non-rev OWED off (3), list rev-only (3), disposed() false (2), disposed() true (7), disposed() keyed on ref only (2), dispose namespace test off (1), dispose sha test off (1), no-PR membership made `continue` (4) and `:` (3), no-PR OWED off (4), handoff-body prefix kept (2), failed PR listing continuing with an empty list (1).
- Extra mutants beyond the body's list, also killed: dispose namespace without handoff-body (1), PR-topic `fix/` strip removed (3), `-pr` strip removed (3), handoff-body/* dropped from the shared listing (10), dispose writes nothing (2).
- 1 SURVIVOR: no-PR membership `grep -qxF` loosened to the substring `grep -qF`. The fixtures' topics (topic-a, -b, -c) never contain one another, so a handoff ref named `foo` beside an open PR whose topic is `foo-2` would go silent under that mutant without any check failing. The production line is correct (`-x`). This is a test-strength gap, not a defect, and it does not block: the body's mutation proof does not name an exactness mutant. A later pass could add one fixture topic that is a prefix of another.
- relay() is byte-identical to the previous head 15ef95bd and cloud_dispatch.py is unchanged (ev/identity.txt), so the body's statement that the earlier arms' mutants carry over holds.

## Figures re-taken at cf687605 (the body took them at b87e8f19; every one matched)
RESULT relay_selftest="69 checks, 0 failed" (ev/relay_selftest.txt)
RESULT dispatch_selftest="29 checks, 0 failed"
RESULT gate_scope="MODE: SCOPED -- 1 script(s) run, 32 scoped out; RUN tests/entities.py"
RESULT entities="ALL 2349 ENTITY CHECKS PASSED" (PYTHONPATH=tests/hastub env -u BASH_ENV)
RESULT structure="STRUCTURE RATCHET PASSED"
RESULT tmp_paths="0 refused"  ref_privacy="0 refused (827 added lines judged)"  throwaway_git="0 raw ... refused"
RESULT agreement="divergent=0, AGREEMENT ok"
RESULT delivery="DELIVERY STATUS OK, 138 rowed, 2 pending, 0 overdue"
RESULT version_manifest_notes_golden="untouched" (step 5; no claim file in the diff, so step 4 has nothing to move)
I re-ran neither the prepr line nor the agreement --self-test 27/27 (prepr is a fixer-side gate run; CI's wave-script is green at this head). Those two are cited from the body, not verified by me.

## Harness (steps 2, 9)
The finding has no finder harness. It is an instrument feature (the cloud-seat return path), and the committed self-tests are the fixer's own, disclosed as such. For an independent measurement I built a reproduction of the no-PR rule over live origin refs (ev/first_pass_*.txt). It is my own instrument, and I name it so.

## The two fixer choices, judged on soundness
1. Counting handoff-body/* as handoff refs. Sound. A handoff-body ref without its code ref (or the reverse) is itself a half-pushed return the orchestrator must see. The pairing on an open PR is pinned by the "nor its handoff-body ref (null control)" check, and the prefix strip is killed by its mutant. Cost: an orphaned topic owes two lines and needs two disposes.
2. Making the no-PR lines disposable as a level. Sound, with a measured cost the orchestrator should know about. Against live refs at 2026-10-19T02:26Z with 14 open PRs, the first `pass` would append 162 handoff-no-pr lines (of 188 handoff/handoff-body refs) and 13 non-rev probe-ref lines (of 41 probe refs). It would repeat those 175 lines on every pass (about every 120 s under --loop) until the refs are pruned (`prune_refs.py` deletes handoff refs whose PR merged) or disposed one by one. INSTRUMENTS.md states the case ("a merged PR's refs not yet archived"). This is accepted, not blocking: the level is the stated design, and the remedy (prune first) already exists in the tree. Suggestion: run prune_refs.py before the first live `pass`.

## Class (step 6)
The body states one seam: the orchestrator's ref scan over probe/* and handoff*/*. Its enumeration is the ls-remote namespaces, and the diff covers all three (probe/*, handoff/*, handoff-body/*). No other namespace the session-local watcher read is named. Class = one seam.

## Forward-carry (step 10)
The destination is tools/audit/seat/INSTRUMENTS.md at this head. It carries `OWED <utc> probe-ref <ref> <sha>`, `OWED <utc> handoff-no-pr <ref> <sha>`, `dispose`, and the timestamp-position caveat for `OWED reviewer-fire` (lines 187-230). R10-TICK-DRIVERS (#2390, merged this round) touches INSTRUMENTS.md only on fold_ledger and body_push. It reads no relay log, so no merged group's brief is a stale destination. The governance.yml wiring is left as an open orchestrator question, as the body says (policy surface).

## CI (step 11)
check-runs at cf687605 (45 runs): none concluded failure, and pr-contract is success (both runs). `closures` (117859049333) was still in_progress at my last read; my local closure select agrees with the body. Earlier heads' reds (wave-script, delivery-status, pr-contract, instrument-self-tests) are each named and answered in `## Red checks`, and both inherited ones are green at this head. If `closures` concludes red, this verdict does not cover it.

## Head (step 7)
The body's `## Head` names cf687605 and its two parents, consistent with what I measured.
