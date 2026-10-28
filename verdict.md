Fix review: blocked 9328902275ba97b94d71f1778cf23f1eb2df031c mutation-vacuous: ledger.covered deletion guard `if rc_m == 0: return False` removed, every owner self-test stays green

bus-nonce: 34b58e842636b27546ec1832f8ebdb4c

Round: 1 (first review of this PR). Measured head: 9328902275ba97b94d71f1778cf23f1eb2df031c, which is still the PR head as of the last read.

## Block

The body lists the content arm's per-path arms as new, including "a deletion main already made". It also states the class rule "every arm of the one classifier is driven by the shared self-tests and pinned by a plant". That arm's refusal half is not pinned anywhere. In `tools/audit/seat/ledger.py` `covered()`:

    if st == "D":
        if rc_m == 0:
            return False

I replaced `if rc_m == 0:` with `if False:`, so a tip that deletes a file main still holds counts as covered. Results under this mutant:
- `ledger.py --self-test`: 72 checks, 0 failed.
- `bus.sh --self-test`: 97 checks, 0 failed.
- `cloud_relay.sh --self-test`: 283 checks, 0 failed.
- `r10_ledger_mutants.py`: has no plant for this line.

This is the harmful direction for the classifier. A handoff whose patch deletes a file main still holds, alone or next to otherwise-covered paths, would read `content`. `bus.sh orphans` would then print it SUPERSEDED, and the relay's level would call it `carried`. Stranded work would leave both lists silently.

The level path is new behaviour. At the base, `covered()` refused every deletion ("a deletion: covered only by a byte-identical arm, not this one"). This diff makes the level accept deletions, and the guard that bounds that acceptance is untested. The opposite mutant (every deletion refused) is killed, by 2 `bus.sh` checks, so only the guard is vacuous. The same guard was already unpinned in the base's `content_superseded` (`D) git rev-parse "$main:$a" ... && return 1` deleted at eab04d0: `bus self-test: 92 checks, 0 failed`). The line now lives in the classifier this PR makes the single owner, and the body's own class rule says it is pinned.

Repair: add one self-test null control where a tip deletes a file main still holds and `landed` returns None. Add a plant on the guard in `r10_ledger_mutants.py`. Re-run the table.

## Findings

- `ledger.covered` deletion guard is unpinned. This is the block above, and the fixer settles it on this branch. Carry: R10-FLY-ORPHANS-REWRITTEN | #2721
- Four more mutants survived that I judged not worth a block. The same fix round can pin them if it is cheap:
  - `merged_lt`: `<=` changed to `<` in the merged-pr close. Only the equality second differs.
  - `merged_max_dropped`: the latest of several merged PRs per topic is replaced by the last listed.
  - `bus_die_dropped`: `|| die` on the `ledger.py landed` call changed to `|| true`. A failed classifier then reads every tip as ORPHAN, which is loud, not silent.
  - `same_blob_arm_off`: close to an equivalent mutant, because the line test takes the same paths.
  Carry: R10-FLY-ORPHANS-REWRITTEN | #2721
- `tools/audit/seat/prune_refs.py` `classify()` is a third reader of "this handoff was delivered by a merged PR". It uses a same-named merged PR or a roster-done branch and has no tip-time guard. It is outside the body's class rule (that grep does not return it). It decides deletion, not landing, and it predates this PR, so I am not counting it as class-open. Carry: dismissed: a different question (pruning, with roster-done evidence), predates this diff, and the body's stated rule does not return it.
- The finder's harness is missing. The packet reports "Finder's harness: none named", and issue #2721's body names no committed harness, only the reverse-apply test. `dev/audit/harnesses/r10_fly_orphans_landed.sh` was built by the fixer, and the body does not say it is the fixer's own instrument (fix-review step 9). I measured with it because no finder's harness exists. Carry: R10-FLY-ORPHANS-REWRITTEN | #2721

## Evidence

- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- The packet was rendered here: no refusals, and the gate digest was pending at render time (`ev/review-packet.md`).
- Merge: `git merge-tree --write-tree origin/main(beb570c81) 9328902` gives rc 0, and `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge-tree.txt`). No conflict.
- VERSION, the manifest, the RELEASE_NOTES heading and both claim files are untouched (three-dot, `ev/version-claims.txt`). The diff moves no golden fixture, so env_drift has nothing to compare.
- Self-tests at the head (`ev/selftests-head.txt`):
  - bus 97/0 and ledger 72/0, as the body says.
  - cloud_relay 283/0 at this head. The body's 279 is the authored code head d0f6de273: I measured 279 there, 279 at eab04d0 and 275 at 0b8f8b585 (`ev/relay-counts.txt`). The merge brought in 4 checks from main, so the body's figure holds at the SHA it names.
  - orchestrator_tick 215/0 and r10_ledger_mutants --self-test 118/0, as the body says.
- Mutation table at the head: `plants: 42, without a FAIL line: none`, rc 0. This matches the body.
- Harness `r10_fly_orphans_landed.sh` (the fixer's), run at both ends (`ev/harness.txt`):
  - main 57f0c9c77, base checkout eab04d0: MISREAD 5, LEVEL-MISREAD 5, LEVEL-LINES 12 for 7 topics.
  - main 57f0c9c77, head: MISREAD 3 (earlycutoff, pr2465 and pr2485 SUPERSEDED), LEVEL-MISREAD 0, LEVEL-LINES 1, `body-follows-code=7 carried=1 merged-pr=5 owed=1`.
  - main beb570c81 (current), base checkout: MISREAD 6, LEVEL-MISREAD 5.
  - main beb570c81, head: MISREAD 4, LEVEL-MISREAD 0.
  - The `null` case is ORPHAN/owed at both ends on both mains.
  - All of these match the body's figures. Its baseline was 0b8f8b585; I used eab04d0, whose classifier code is the same.
- My own mutants are in `ev/reviewer-mutants.txt`. `relay_pr_suffix_kept` was killed (2 relay checks). `D_arm_always_refuses` was killed by bus.sh (2 checks). The survivors are listed above.
- Not re-derived:
  - The body's failing-test-first count ("97 checks, 4 failed" for the new bus.sh cases on baseline production code). Plants B1 and B2 and my mutants cover the same direction.
  - The gate and structure figures. These are CI's heavy runs, cited, never re-run.
- Class rule: the body's grep at the head returns only `def covered` and `def landed` in ledger.py, and `content_superseded` is gone. Both are in the diff. The class is this one classifier, as the body says.
- CI on the head (`ev/ci-checkruns.txt`): no failed run when read. `governance/instrument-self-tests`, `codeql python`, `tests/closure-scope`, `tests/nightly-status` and one `prelude` were still running. `tests/mutation` is green, but this diff's changed lines are tooling, and its log was not read. The body's `## Red checks: none` matches what has concluded so far.
- Forward-carry: none named, and none is owed beyond the findings above.
