Fix review: blocked 185699076fb42c0082be4e5eaae31ab1abf2c1ad mutation-vacuous: rv-real-bodypush-outside-wt rv-nohandoff-not-on-level rv-folded-memo-no-entry rv-privref-not-deleted

bus-nonce: dd0783524bf6f8b4eeccb75eb4441eae

## Block

Round 1 (first review). Measured head 185699076fb42c0082be4e5eaae31ab1abf2c1ad, still the tip of `handoff/r10-review-dispatch-residue-p1` when this verdict was written (`ev/head-recheck.txt`).

The body's seven named mutants are all KILLED. But the driver run at this head (`ev/mutants.txt`, spec `ev/mutants.json`) reports four survivors on changed production lines in `tools/audit/seat/cloud_relay.sh` `carry_fold_arm`. Two of them leave behaviour the body claims with nothing testing it:

- `rv-real-bodypush-outside-wt`: `(cd "$wt" && bash "$HERE/body_push.sh" ...)` becomes `(bash "$HERE/body_push.sh" ...)`. It SURVIVES. That one-token edit puts back exactly the Carry 14 defect: body_push.sh runs in the relay's own checkout, at main's tip, not the handoff tip. The self-test always sets `HPO_RELAY_BODYPUSH`, so the production `body_push.sh` line is never executed. Its stub twin `rv-stub-outside-wt` is KILLED. The body says "`HPO_RELAY_BODYPUSH` now replaces only the `body_push.sh` call inside that worktree", but in fact it replaces a separate copy of the whole line. A cure that is cheap and in place: one shared call, the way `HPO_RELAY_FOLD` already works (e.g. `(cd "$wt" && ${HPO_RELAY_BODYPUSH:-bash "$HERE/body_push.sh"} "$topic" "$body")`). Then the stub runs the production line.
- `rv-nohandoff-not-on-level`: `if [ $rc = 0 ]` becomes `if [ $rc = 0 ] || [ -z "$htip" ]`. It SURVIVES. Under this mutant, a CARRY-LANDED topic with no `handoff/<topic>` is recorded in `cloud-folded` and announced FOLDED, with no body ever pushed. The body claims "A missing handoff is now on the level; at the base it was only printed, with no level line", and no self-test arm creates a fold topic without a `handoff/` ref (the self-test's `cfref handoff/` calls are only for cf-a, cf-e, cf-f and cf-g). One arm is owed: a CARRY-LANDED topic with no handoff ref is OWED "no handoff/<topic>", on the level, and not in `cloud-folded`.
- `rv-folded-memo-no-entry` (a topic already in `cloud-folded` is not memoed) SURVIVES. It is equivalent: the `cloud-folded` grep that follows also skips with no fetch. It needs no test and is listed because survivor_list.py requires every survivor.
- `rv-privref-not-deleted` (`git update-ref -d refs/hpo-relay/fold/<topic>` replaced by `true`) SURVIVES. This is cleanup only: the refspec is forced (`+`), so a stale private ref cannot be the next worktree's head. It is listed for completeness, and no test is required.

The re-cut owes the two arms or edits above, plus a mutant run showing `rv-real-bodypush-outside-wt` and `rv-nohandoff-not-on-level` KILLED.

## Evidence

- RESULT base self-test at a7628041dc: `cloud_relay self-test: 416 checks, 0 failed`, rc=0 (`ev/selftest-base.txt`). The body's figure is re-derived.
- RESULT head self-test: `433 checks, 0 failed`, rc=0 (`ev/selftest-head.txt`). Re-derived.
- RESULT failing-test-first: head file with base's `carry_fold_arm` spliced in, giving `433 checks, 9 failed`, rc=1 (`ev/selftest-red.txt`). The nine FAIL names include all four the body quotes. Re-derived.
- RESULT body's mutants re-created by this reviewer: foldref-fetch-head, foldtip-assert-off, foldmemo-drops-line, foldmemo-no-skip, foldttl-never-retry, foldttl-always-retry and foldtip-wide-lsremote are all KILLED, and NULL SURVIVED. The reviewer's own rv-memo-key-ignores-body, rv-blocked-never-stands, rv-memo-not-saved and rv-stub-outside-wt are KILLED. The four survivors are above.
- Null controls: the self-test checks `null control (carry 14): ...` and `null control: a moved wip ref is judged again` / `... as is a moved body ref` pass at the head. The carry-14 null control fails on the spliced base arm, because there the stub ran outside the worktree. `foldmemo-drops-line` is KILLED, as Carry 22's control requires.
- Harness: the finding has no committed out-of-tree harness. The carries' own instrument is the self-test arms the roster prescribes, and all the prescribed arms are present: Carry 14's planted concurrent fetch, the sequential null control and two mutants; Carry 22's not-refetched check with the level line standing, the moved-ref re-judge, and the TTL before and after. The cost figures (27-33 s, about 181 s per pass) are the triage's live-relay numbers. This reviewer could not re-derive them either, because no relay state exists in a cloud seat.
- Base anchors 805, 818, 838, 843 and 849 were re-derived (`ev/anchors-and-class.txt`).
- Class: `git grep 'worktree add[^|;]*FETCH_HEAD'` at the head over tools/ and .claude/ returns one other site, `.claude/workflows/audit-plan.js:144`. That is a one-shot plan reviewer's prose instruction in its own session, not a long-lived checkout with concurrent fetches. It is outside P556's cause and the reviewer finds no open seam. The body names no rule, but each carry states one seam.
- merge-tree: `git merge-tree --write-tree origin/main 185699076f` gives rc=0 and tree e67f818dc0, so it is clean against origin/main f24d107bd7 (`ev/merge-tree.txt`).
- VERSION, RELEASE_NOTES.md and the manifest are untouched (`ev/version-untouched.txt`). The diff is one file. Claims files are untouched, so there is no golden drift to compare.
- Gate scope: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `tests/doc_claims.py` printed `ALL 297 checks PASSED` (`ev/doc_claims.txt`). `tests/structure.py` printed `STRUCTURE RATCHET PASSED` (`ev/structure.txt`). Archscore printed `dS +0.0000 NULL` (`ev/archscore.txt`). No budget moved.
- CI: no pull request exists yet, so there is no review packet and no CI run to read. There are no red checks to answer. `merge_train.py owed-reds` is in `ev/owed-reds.txt`.
- Carry accounting: the roster group R10-REVIEW-DISPATCH-RESIDUE at `handoff/audit-r10-roster` dbff400dec now holds 26 carries. Carry[14] (P556) and carry[22] (P580) match the body's scope, and the body's Carry 17 / part-6 exclusion and the "do not widen dispose" constraint are honoured. The body's statement that "Carry 24 refers to no carry" held at 88fe33042c (24 entries) and no longer holds at dbff400dec, where index 24 is DESIGN-REVIEW-ROUND-CONTEXT. See Findings.
- Forward-carry: the body says none, and this reviewer found no later-stage constraint produced by the diff.

## Findings

- The body's filler "Carry 24 refers to no carry" is stale at roster tip dbff400dec: index 24 now exists (0-based), and review_packet.py's whole-group 1-based count would now demand Carries 1-26. That is the BRIEF-CARRIES-PART-SCOPE defect the roster already holds as this group's carry[25]. The re-cut body should restate its carry note against the roster at its own push. Carry: dismissed: already carried as R10-REVIEW-DISPATCH-RESIDUE carry[25] (BRIEF-CARRIES-PART-SCOPE) on handoff/audit-r10-roster dbff400dec

## Friction

none
