Fix review: blocked 6ac0d3e67f6a602e4a14e47d75e85e086934c4a6 figure-wrong: bucket 5 counts 5 registry-only entries as substantive (hm4.py truncates the file list at 160 chars), and CM-2's "tenth (#2772)" is #2753

bus-nonce: b509e86af59fbf1d88ddb90e525b1950

Round 1. The review was done from a detached worktree at 6ac0d3e67f6a602e4a14e47d75e85e086934c4a6, and the head was still that SHA when this verdict was posted. Governance roles show no change base..origin/main. Origin/main is 0b8f8b585.

## What holds (RESULT lines, evidence/)

- RESULT CM-1 fixed, `app_approve.sh --self-test` from tools/pr/: 256 checks, 0 failed (selftest_head.txt).
- RESULT mutant A, the fix removed (main's line restored, new cases kept): 256 checks, 2 failed. The failures are the two named in the body: the #2876 shape got 1 and wanted 0, and the hand-resolved reason got 0 and wanted 1 (selftest_mutA_fix_removed.txt).
- RESULT mutant B, the inner answer ignored (`e=$(carry ...; true)`): 256 checks, 3 failed. These are the three the body names (selftest_mutB_inner_ignored.txt).
- RESULT null control, base 0b8f8b585's script: 252 checks, 0 failed (selftest_base_0b8f8b5.txt). The body says 254 and 258 and I get 252 and 256. The script did not change between 6d86acc9 and 0b8f8b585, so the absolute count depends on the environment. The +4 delta reproduces. I could not re-derive the body's absolute counts.
- RESULT my own run of base (6d86acc9) against the fixed carry, over all 75 hm_out pairs at main@t: 8 flips, all no->yes, and 0 yes->no (rerun_carry.py, rerun_carry.tsv). This matches hm6_out.tsv entry for entry.
- RESULT hm.py re-run now, over 592 refs: TOTAL 75, 55 PRs. Columns 1-6 are identical to hm_out.tsv. The split is 54 before and 21 after, on 12 PRs, which is 0.116 and 0.241 per merge. The merge counts are 467 and 87, and both reproduce.
- CM-1 is sound as built. The recursion runs in a subshell, so the outer `set --`, `x` and `bots` are untouched. Every off-main second parent recurses, and every merge it reaches must still be git's automatic result. The outer own-diff still covers the whole head, and bot rows on the inner side are not excluded outside. That makes the outer check stricter, not looser. The range is strictly smaller on each call, so the recursion terminates. VERSION, the manifest and the notes are untouched.
- The checks at the head have no red so far. Some are still in progress: codeql python, instrument-self-tests, closures, prelude (check_runs.tsv).
- The four parts are present: the cause, the process states (a), (b) and (c) with evidence, the cost test, and a countermeasure with recorded refusals. CM-1 is a check-shaped countermeasure, and it is shown failing on the defect and passing once fixed.

## What blocks (figure-wrong: step 8, a quoted number re-derived under the PR's own rule)

1. **The section 2 table's buckets 4 and 5 are wrong under hm4.py's own stated rule** ("G = the own patch moved only in shared registries").
   - hm4 tests the hm3 file column, which is truncated to 160 characters. The test `len(files)<160` sends every truncated list to S.
   - I re-bucketed with the full list of differing files (rebucket.py, rebucket.tsv). **5 of the 23 S entries are registry-only.**
     - #2411 2026-10-19T03:05 (blocked) and #2465 2026-10-20T14:18 (blocked) are before the split.
     - #2745 2026-10-25T09:08, #2819 2026-10-26T04:02 and #2834 2026-10-26T09:07 are after it.
   - The corrected figures:

     | bucket | entries | after split | blocked | lag (min) |
     |---|---|---|---|---|
     | 4 | 28 | 7 | 3 | ~1122 |
     | 5 | 18 | 6 | 6 | ~1200 |

     The record has bucket 4 at 23/4/1/737 and bucket 5 at 23/9/8/1585.
   - This error reaches the prose too:
     - "In 8 of bucket 5's 23 entries" (section 3, cause 1) and "8 in 23" (section 2) become 6 in 18.
     - Section 3 cause 2 says CM-1 turns entries "in buckets 4 and 5 (#2368, #2745, #2819)" to yes, where the own patch moved only in carry-excluded files. That sentence contradicts bucket 5's own definition (production code moved). Corrected, they are bucket 4 only.
   - The conclusions and process states do not change. But the figures are the product of this record and will be read as established fact, so they must be right.
2. **CM-2's figure is wrong against the record's own outputs** (p242_consistency.txt).
   - "9 of the 10 entries whose delta held a bot commit carried at the time. The tenth (#2772) is an empty delta" does not match hm2_out.tsv.
   - 23 entries' deltas hold a bot commit. 13 of those also hold a code merge, and all 13 have carry@t=no.
   - Of the 10 entries whose kind is `bot`, the one that did not carry is #2753 at 2026-10-26T01:36 (`{'main': 1, 'bot': 1}`, carry@t=no). #2772 is kind `empty`.
   - State the population, and say why #2753's bot delta refused. If it is the 2b context case, say so.
   - CM-2's refusal itself stands.
3. **Minor.** "Only #2673 skips its reviewer turn outright (lag 48 min)", and the cost test's "about 48 min". hm2_out.tsv gives #2673's lag as 42.

## Triage P242 consistency (asked by the dispatch)

- **The direction is consistent with P242.** P242 says the bot moves (3 of 8) carry and a bot hold buys nothing. The record refuses CM-2 for the same reason, and it places the cost on seat-side main merges (bucket 2) and orchestrator pushes.
- **None of P242's 8 moves is a re-verification under the record's keying.** The hm.py re-run still prints 75, and #2883, #2887 and #2894 have 0 entries.
- **The record does not name P242 or its instances.** It also does not name the costs P242 hands to this RCA: #2887's stranded fixer branch, and the 5 seat-side `Merge remote-tracking branch 'origin/main'` merges.
- **The fixer was not bound by P242.** The ruling (40bec0ab6) is only on origin/handoff/triage-s7-batch49. It is not on main and not in this group's roster carry. So I raise it as owed for the re-cut, not as the block. One line would do it: the record's harness shows the 8 cost no re-verification, and the residue is bucket 2 and the post-split pushes. The owner of #2887's stranded-branch cost should be named, or the record should say it was not measured.

## Repair

- Fix hm4.py's truncation: bucket from the full file list. Re-take the hm4 and hm5 outputs and every section 2, 3 and 5 figure that depends on them.
- Correct CM-2's population sentence.
- Correct #2673's lag.
- Add the P242 paragraph.
- CM-1 and its self-test cases need no change.
