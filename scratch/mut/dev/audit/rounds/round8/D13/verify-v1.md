# D13, round 8: verifier v1 (the panel's only verifier)

Tree `/home/claude/audit-r8/seats/D13-v1`, a git worktree at baseline `cdf82da`. Window `c310541..cdf82da`.
Every number below is a count, so none is provisional. For the record: load1 was 19.17 at the start and 17.76 at the end, thread_factor 1.

## Runs
Both finder harnesses ran from my tree. I pointed their fetch at my own cache (`D13S1_TMP` and `D13S1_CACHE` set to `/home/claude/audit-r8/tmp/D13-v1`), so every API number was fetched fresh. Nothing else was rewritten.
- `s1_window.py`: first_parent_commits 92, window_merges 88, stamps 4, api_failures 0. This matches the finder.
- `s1_yield.mjs`: every figure the two findings cite matches exactly.
  - verdict_prs 80, extra_rounds 20, reverify->merge 15, repair->merge 3, duplicate 2, one_round_yield 0.8125, first_pass_yield 0.963, prod_head_moved_entries 19.
  - no_verdict 8: owner-approved 8/22, app-approved 0/66. Stale-head merges: [1444, 1426].
- Finder perturbations:
  - `--pin-head 1375`: reverify 15 -> 14 and production's row 19 -> 18.
  - `--reshape 1493`: no_verdict 8 -> 9, verdict_prs 80 -> 79, production's verdict_prs 80 -> 79.

My harnesses are independent of the finder's. Each has its own GET-only reader (`v1_gh.py`, with its own cache). Each enumerates merges from the "Merge pull request #N" subjects instead of `/commits/<sha>/pulls`, uses its own regex, and reads a third endpoint the finder's harness does not: inline review comments (`/pulls/<n>/comments`).

## D13-s1-01: vote weaken, to low
- **My metric:** each verdict after a PR's first counts as a round. It is a re-verification when the previous verdict was `merge` at another head. Each re-verification is then classified by `git diff -U0 <main-before-merge>...<head> | git patch-id --stable`, comparing the old head with the new one.
- **Harness:** `v1_rework.py`.
- **My number: 15 re-verifications, all returning `merge`.** 14 had a changed authored diff and 1 had a byte-identical one (#1433, a pure merge of origin/main). The other extra rounds: repair 3, same-head 2. extra_rounds 20 and one_round_yield 0.8125, both matching the finder.
- **Perturbation:** `--pin-head 1375` moves 15 -> 14.
- **Null control:** `--pin-head 1496` on a single-verdict PR leaves the count at 15.

### Attacks
1. **Contention.** Not applicable: the finding rests on counts.
2. **Gate mode.** Not applicable.
3. **Grid artefact.** 12 PRs, at most 2 rounds each. Dropping the largest cell leaves 13, so the result is not one PR's artefact.
4. **Null control.** The finder's null is the first-round block rate, 0.0375, which predicts 0.56 blocks across 15 rounds. Zero observed blocks has probability e^-0.56 = 0.57 under that rate. So the rounds cannot be called worthless, and the finder concedes this.
5. **Consequence.** This is where the finding weakens:
   - **(a) The rounds were mandated.** 14 of the 15 re-verified a head whose authored diff had changed. Orchestrator.md s11 then requires a fresh verdict, because its byte-identical carry path does not apply. The carry path could have saved at most 1 round (#1433).
   - **(b) The mechanism is already known and instrumented.** Round 6's D13-01 (#1405) landed `policy_lint.mjs:REWORK_CLASS` (`head-moved`). Production already prints this rework as 19 entries: 15 re-verifications, 3 repairs and 1 same-head verdict, all keyed against the first verdict's head, which is its documented definition. That rules out the brief's `medium` ("an instrument that cannot compute its own metric"). The claim does not reach `high` either, because no cost is shown to exceed catches.
   - **(c) The new content is narrower.** It is a reporting argument: 0.963 counts as first-pass 12 merges that were reviewed 2 or 3 times, and a one-round yield of 0.8125 would show them. That is true arithmetic about a figure production already exposes beside it, so low.
6. **A lead I did not vote on.** Counting only the branch's own first-parent commits between re-verified heads gives this mix: merge-of-main only 6, content only 4, content plus merge 3, bot plus merge 1, bot only 1. So 7 of the 15 rounds followed content pushed after a `merge` verdict. That is a possible freeze question under fixer.md ("the handoff to review freezes the branch"), but it is not the claim made.

**Mechanism.** This is not the same mechanism as D13-s1-02. It is the complement of D13-s1-02's side claim: #1426 is the case where the head moved and the re-verification was skipped.

## D13-s1-02: vote verify, medium
- **My metric:** a merge has no verdict when no issue comment, review or inline review comment has a trimmed first line matching `^Fix review:\s*(merge|blocked)`. Merges are split by whether their files touch a path that CODEOWNERS (at the baseline) assigns an owner, using app_approve.sh's own matcher.
- **Harness:** `v1_coverage.py`.
- **My number: 8.** By files: code-owned 8/31, not-owned 0/57. By approver: owner 8/22 and app 0/66, identical to the finder.
- **Inline endpoint and loose text:** the inline endpoint holds no verdict for any of the 8. A loose search for any "fix review" text anywhere finds only #1439, and that hit is prose quoting the grammar, not a verdict.
- **Perturbation:** `--drop 1493` moves 8 -> 9, in the not-owned arm.
- **Null control:** `--drop 1445`, a PR already without a verdict, leaves the count at 8.

### Attacks
1. **Missing endpoint.** Inline review comments add nothing, so the gap is not an artefact of which endpoints were read.
2. **The null control is a mechanism, not a control.** The app arm's 0/66 is `tools/audit/app_approve.sh` refusing a PR with no verdict (its self-test: "REFUSE: no Fix review verdict at all"). Nothing in `.github/` checks for a verdict, and the owner's GitHub review runs no such refusal. The 0 is therefore enforced by construction, not an independent baseline. It still names the cause: the only verdict check sits on the path the code-owned PRs never take.
3. **Is there an exemption?** CLAUDE.md says "only @tvofi reviews code-owned paths". A reader could take that as the owner's review replacing the fix review. Against that reading:
   - orchestrator.md s11 lists the verdict and the approval as separate prerequisites for every merge.
   - 14 of the 22 owner-approved merges do carry verdicts.
   - The D13 brief states that no rule exempts record PRs.

   The reading does not hold.
4. **Severity is earned.** 3 of the 8 are fix-class titles (#1445, #1423, #1439) and touch production-side tooling: `tests/mutation_table.py`, `tests/closure.py` and `policy_lint.mjs`. I show no consequence beyond the unreviewed merge, so medium, not high.
5. **The side claim is only half right.**
   - **#1444 is carry-eligible.** Its authored diff at the merged head is byte-identical to the one at its verdict: patch-id f87a14643e8d at both. The only commit between them is a merge of origin/main. s11's carry path applies, provided a reason was recorded, which I did not check.
   - **#1426 is a real stale merge.** Its authored diff changed after the verdict (patch-id b0690d19 -> 44db2b4a, including two content commits), and it merged on the owner's approval.

   So the side claim is 1 real stale merge, not 2, and the stale one sits on the same owner path.

**Mechanism.** D13-s1-01 is not the same mechanism (see above). The only link is #1426.

## Files
- `v1_gh.py`, `v1_rework.py`, `v1_coverage.py` under `tools/audit/round8/D13/`.
- Temporary output lives under `/home/claude/audit-r8/tmp/D13-v1/`.
- Production files are untouched: `git status` shows only the preparation's stripping deletions and the untracked `tools/audit/round8/`.
