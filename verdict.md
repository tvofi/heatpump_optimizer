Fix review: blocked c562b07972c71226a8cb54d0efd4376c76921c1c mutation-vacuous: rv-folded-memo-no-entry rv-privref-not-deleted

bus-nonce: c044f4d463071aa4db6a45cbafb459e0

## Block

Round 2, a delta review over the reviewed head 185699076fb42c0082be4e5eaae31ab1abf2c1ad. Measured at head c562b07972c71226a8cb54d0efd4376c76921c1c. It was still the tip of `fix/r10-review-dispatch-residue-p1` when this verdict was written (`ev/head-recheck.txt`).

The dispatch brief for this round says all four of round 1's survivors must now be KILLED. The round-1 spec (`ev/mutants.json`, 15 mutants) was re-run through `mutant_run.py` (copy-tree) at the head (`ev/mutants.txt`, rc=0). Two of the four are now KILLED: `rv-real-bodypush-outside-wt` and `rv-nohandoff-not-on-level`. Two still SURVIVE:

- `rv-privref-not-deleted`: replacing `git update-ref -d "refs/hpo-relay/fold/$topic"` (`tools/audit/seat/cloud_relay.sh:864`) with `true` SURVIVES. The body's triage is only partly right. Because the refspec is forced, a stale ref cannot become the next worktree's head. But the deletion has an observable effect: without it, one `refs/hpo-relay/fold/<topic>` per folded topic stays in the relay's checkout for good. The body's Carry 14 text says the ref is "deleted after the push", and nothing checks that. Cure: one self-test check after a fold pass that `git for-each-ref refs/hpo-relay/fold/` prints nothing.
- `rv-folded-memo-no-entry`: replacing `fold_judge ... folded "$now"; continue` with `continue` at `cloud_relay.sh:834` SURVIVES. The body calls this mutant equivalent, because the `cloud-folded` grep that follows also skips the topic with no fetch. If that is true, line 834's memo write has no observable effect, which makes it redundant code. Cure: either delete the write so the mutant site is gone, or show its effect in a check (the `cloud-fold-judged` entry for an already-folded topic survives a pass, if anything reads it). The behaviour must not be left both claimed and unpinned.

## Evidence

- RESULT mutants at head (`ev/mutants.txt`): NULL SURVIVED. KILLED: foldref-fetch-head, foldtip-assert-off, foldmemo-drops-line, foldmemo-no-skip, foldttl-never-retry, foldttl-always-retry, foldtip-wide-lsremote, rv-memo-key-ignores-body, rv-blocked-never-stands, rv-memo-not-saved, rv-stub-outside-wt, rv-real-bodypush-outside-wt, rv-nohandoff-not-on-level. SURVIVED: rv-folded-memo-no-entry, rv-privref-not-deleted. That is 13 KILLED, 2 SURVIVED and NULL SURVIVED, which matches the body's figure.
- RESULT head self-test: `cloud_relay self-test: 441 checks, 0 failed`, rc=0 (`ev/selftest-head.txt`). This matches the body.
- RESULT failing-test-first, re-derived: the head file with merge-base f24d107bd7's `carry_fold_arm` spliced in prints `441 checks, 14 failed`, rc=1 (`ev/selftest-red.txt`). `cloud_relay.sh` is byte-identical at a7628041dc and f24d107bd7. The body's `433 checks, 9 failed` is round 1's arm set. See Findings.
- Delta 18569907..c562b079: of the PR's own files, only `tools/audit/seat/cloud_relay.sh` changed, with 15 lines added, all in the self-test (the cf-i and cf-h arms). `carry_fold_arm` is unchanged, as the body says. The rest of the delta is main's merge (#3424, #3427, #3433). The three-dot diff against origin/main is `dev/programme/delivery/3448.md` plus `cloud_relay.sh`. The delta touches no `custom_components/` code of this PR, so the review is not widened.
- The file mode stays 100644 at base, the reviewed head and this head (30277114c restores it).
- Body patch: `ev/body-diff.txt` compares handoff-body 90392b6aa's BODY.md with the live body (`ev/pr-body.md`). It shows 23 `Carry N` lines reworded with the same 23 numbers (1-13, 15, 16, 18-21, 23, 24, 26, 27), plus a `## Head` line. No carry was dropped: 17 (part 6's) and 25 (BRIEF-CARRIES-PART-SCOPE) are accounted for in the body's prose, as before. The reworded lines no longer carry `Carry: R10-REVIEW-DISPATCH-RESIDUE`. They name carries the group already holds, and the packet's carry_audit reads `0 finding item(s)`.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, rc=0 (`ev/structure.txt`). No `*_budgets.json` changed.
- VERSION, RELEASE_NOTES.md, the manifest and both claim files are untouched in the delta and in the three-dot diff.
- merge-tree: `git merge-tree --write-tree origin/main c562b079` gave rc=0, tree 9dd7ee2686, origin/main cbd23f1c8b (`ev/merge-tree.txt`). It is clean.
- CI: `merge_train.py classify c562b079 --pr 3448` printed `GREEN c562b07972c71226a8cb54d0efd4376c76921c1c pending: none red: none` (`ev/classify.txt`). The packet's `gate` failure (job 130472127525) was a provisional run that printed `FAIL run(s) [43004513744] at this head are still being judged; their gate decides`. Classify now reads it green. `## Red checks: none` is therefore answered, and no owed red stands (`ev/owed-reds.txt`). Carry: dismissed: evidence, not a finding
- Harness: as in round 1, the self-test arms the roster prescribes are the instrument. There is no out-of-tree finder harness. The live-relay cost figures (27-33 s, about 181 s a pass) are the triage's and are not re-derivable in a cloud seat.

## Findings

- The body's failing-first figure, `433 checks, 9 failed` "with the new self-test arms on the unfixed arm", is stale at this head. With round 2's arms it is `441 checks, 14 failed` (`ev/selftest-red.txt`). The re-cut body should restate it. Carry: dismissed: a body figure the re-cut restates; it constrains no later stage

## Friction

none
