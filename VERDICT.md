Fix review: merge 411bb47a0bfc17a689b4fdc1133ada9beb1c0b7a

bus-nonce: af3e46f592165892ded15ec69afa7993

Round 3, at the same head as rounds 1 and 2 (comments 6268247849 and 6268507266). Both earlier rounds blocked only on carry-missing. I measured head 411bb47a0bfc17a689b4fdc1133ada9beb1c0b7a (ev/HEAD), and it was still refs/pull/2447/head when I wrote this (ev/head-at-writing.txt). The role contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Step 10, forward-carry: all five carries landed

handoff/audit-r10-roster is at 2e6418bce467413411b56f3e77d45163b466c4e0, its tip, made by `roster_edit append-carry R10-CI-LAYOUT`. The roster there holds five `Source: #2447` entries (ev/carries.txt, ev/carries-groups.txt, ev/roster-2e6418bce.json):
- R10-BRIEFS-FOLD carry[15]: Forward-carry 2. The `mutation` line goes stale after mutation-autofix pins the site.
- R10-POLICY-FIXER-MD carry[1]: Forward-carry 1. Step 6f reads the committed tree, so commit before prepr.
- R10-POLICY-FIXER-MD carry[2]: Friction fixer.md#6. handoff_push.sh conflicts with "no GitHub writes".
- R10-CI-LAYOUT carry[6]: Friction tests/throwaway_git.py#check. It greps its own repository, so plants are spelled in halves.
- R10-CI-LAYOUT carry[7]: `## Red checks`, ref_privacy --check as the cheaper detector, not yet in prepr. This was round 2's missing carry, and it is now present.

Every carry in the PR body cites `(roster 2e6418bce)`, and that commit is on handoff/audit-r10-roster.

## Re-checked this round
- Step 13: `git merge-tree --write-tree origin/main(d4fb5351b) 411bb47a0` returns rc 0 and tree f4629584ef71. There is no conflict and the claim driver was not invoked (ev/merge-tree.txt).
- Step 11, CI from the commit check-runs API (55 runs, all completed; ev/check-runs.tsv). The only red is `nightly-status`, which the body answers as main's red; this diff touches no nightly record. `instrument-self-tests` is green, and the body answers its red on the first head. The latest `pr-contract` run started at 13:36:13, after the body edit at 13:36:07 and after nightly-status concluded at 13:01:33, and it is green. `mutation` is green.
- Step 1, mutation proof, re-taken at this head (ev/mut_A.txt, ev/mut_B.txt; each mutant is a copy in tools/pr/ run with `--self-test`):
  - A, line 715 `reds+=(mutation)` replaced by `:` : FAIL on both rows the body names, plus the copy-path row
  - B, line 751's throwaway_git.py call replaced by `out=ok; r=0` : FAIL on all three rows the body names, plus the copy-path row
  - head: `303 passed, 0 failed`, rc 0 (ev/selftest-head.txt)
- Step 8, figures at the head (ev/figures.txt):
  - throwaway_git: `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`
  - ref_privacy: `... 0 refused`
  - `STRUCTURE RATCHET PASSED`
- Steps 4 and 5: VERSION, manifest.json, RELEASE_NOTES.md and tests/golden are untouched (three-dot diff, empty).
- Steps 2-3, 6-7 and 14: verified in round 1 at this same SHA. The finding has no committed harness, so I measured with the brief's three-arm self-test rows. Round 1 also killed reviewer mutants C, D and E. The class is one seam. No budget, closure or score file moved. Those results stand.

## Non-blocking (carried from rounds 1-2)
R10-PREPR-UNPINNED-RED's own carry list still holds the #2441 body_push.sh/ci_predict entry, which R10-CI-LAYOUT also holds. That gives one item two destinations, and dropping the duplicate is the orchestrator's call.
