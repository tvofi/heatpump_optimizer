Fix review: blocked 1723d8743619f397bcf9e04a219e1a581f4a736c ci-red: the required pr-contract refuses the body three times at this head, because carry_audit check reads main's roster, where R10-FLOW-JIDOKA is not a group, so the carry is BAD-DEST

bus-nonce: a4b5dbaef6567264e63d26d8b844d291

This is round 4, the fourth review of this group. Round 3 blocked `10f85c3ee` as carry-missing. I measured head `1723d8743619f397bcf9e04a219e1a581f4a736c`, and it was still the PR head at 01:46:28Z (ev/head-at-write.txt). I worked from a detached worktree of the head, under /etc/profile.d/hpo-toolchain.sh, with PREPR_SKIP_CLOSURES=1. `dev/governance/roles/` is unchanged between the merge base and origin/main, because the merge base is origin/main `93e6a63d2`. Round 3's carry-missing block is cleared on the roster ref. The required gate still refuses the same carry, for the reason in the block below. Under `fixer.md`, a round from the fourth owes a re-cut rather than a repair. The defect here is the body's routing alone, not the code.

## Block

- **The required `pr-contract` check is red at this head, and the cause is deterministic.** All three runs failed (119585492906 at 01:27:56Z, 119585669593, 119587185157 at 01:33:20Z). Each failed at the step `python3 -I tools/audit/carry_audit.py check --body /tmp/pr-body.md`, which printed `BAD-DEST body item 39d44c61: R10-FLOW-JIDOKA: R10-FLOW-JIDOKA is not a group of the roster` and `CARRY-AUDIT: 4 finding item(s): 3 routed, 0 unrouted, 1 bad destination(s)` (ev/pr-contract-*.log).
  - `pr-contract` is a required context on main (ev/required-contexts.txt).
  - The CI step passes no `--roster-ref`, so it reads the head tree's roster, which is main's roster. R10-FLOW-JIDOKA exists only on `origin/handoff/audit-r10-roster` (`306a96d5f`). Main's `wave-r10-groups.json` holds no such group (count 0, ev/carry-owner.txt).
  - I reproduced it locally at the head: without `--roster-ref`, rc 1 with the same BAD-DEST. With `--roster-ref origin/handoff/audit-r10-roster`, it prints `4 routed, 0 unrouted, 0 bad destination(s)` (rc 0) (ev/carry.txt).
  - The body's `## Red checks` does not mention this head's runs and does not answer pr-contract. It ends at `bb53ba321` ("has not run CI yet").
  - A re-run cannot turn this green. Either of these unblocks it:
    - the R10-FLOW-JIDOKA group (with its #2528 sentence) lands on main's roster before this PR's body is re-checked, or
    - the sibling-seam carry is routed to a destination that main's roster or the issue tracker resolves, while the R10-FLOW-JIDOKA brief sentence stays as the owning text.
  - Either way, `## Red checks` then names pr-contract at this head and answers it. No code change is owed.
  - Carry: R10-PREPR-CAP

## Findings

- The required `pr-contract` refuses this PR's carry to a live group that exists only on the roster ref (the block above). The PR's next round settles it. Carry: R10-PREPR-CAP
- **The carry-audit instrument is split.** The check the brief and the body prescribe (`carry_audit.py --roster-ref origin/handoff/audit-r10-roster check`) and the one CI's required pr-contract runs (no `--roster-ref`, so main's worktree roster) resolve destinations against different rosters.
  - A carry to a live group that has not yet merged to main's roster passes the first and is refused by the second.
  - That is the mirror image of the gap R10-FLOW-JIDOKA's brief already owns ("the worktree's roster is not where fix-review step 10 looks").
  - The brief's controls cover the offline-passes case only. They should also state this control: a body whose carry exists only on the roster branch is refused by pr-contract.
  - Carry: R10-FLOW-JIDOKA

## Evidence

- **Round 3's destination question is settled on the roster ref.** R10-FLOW-JIDOKA's resume stage is the one before work starts, so the group is live (ev/roster-jidoka.json). Its brief carries: "Carry from #2528 (R10-PREPR-CAP): tools/pr/prepr.sh steps 3 to 3h run heavy work in the foreground, so a KILL or TERM to prepr during step 3h leaves the self-test or mutants drive running [...]; the fix shape is closures-step-style background-and-trap for each heavy step" (elided words are the TERM case). That sentence states the control as a precondition.
  - The finder's carry-owner counter, re-keyed as the body says, reads:
    - `#2528`: carry-201 0 and JIDOKA 0 at `5ffe2a933`; carry-201 0 and JIDOKA 1 at `743463c61` and at `306a96d5f`.
    - Null key `#2582`: JIDOKA 1 at all three.
  - `2ce054264` is on the roster ref. These match the body (ev/carry-owner.txt).
- **The delta since the reviewed head is main merges only.**
  - `git log --no-merges 10f85c3ee..1723d8743 --not origin/main` is empty.
  - The branch's own three-dot diff from its merge base is byte-identical between `10f85c3ee` and `1723d8743` (`diff` of the two three-dot diffs: IDENTICAL).
  - `tools/pr/prepr.sh` is blob `1a0afd8c5` at both heads.
  - The diff touches five files: gate-scoping.md and its two generated copies, `dev/programme/delivery/2528.md`, and `tools/pr/prepr.sh`.
- **The mutation proof holds at this head.** I used the finder's patches (round 3's `mut-*.diff`, ev/mut-*.diff), applied with `git apply` to detached worktrees of the head. Each run is `bash tools/pr/prepr.sh --self-test` (ev/selftest-*.txt), and every worktree was restored to 0 dirty files (ev/restore-status.txt).
  - RESULT M0 (null): 323 passed, 0 failed.
  - RESULT M3wd: 320/3. All three reap arms fail, `got gone:alive:alive`.
  - RESULT M7: 320/3. All three reap arms fail, `got gone:gone:alive`.
  - RESULT M9: 321/2. The TERM-alone and group arms fail, `got alive:alive:alive`.
  - These are identical to round 3 and to the body's table. The production lines are unchanged, so round 2's M1, M2, M3setm, M4sub, M5, M4 and M6 results still apply. I did not re-run them.
- **Figures re-derived at this head (ev/cheap-checks.txt).** All are rc 0 or match the body:
  - `RULES-SYNC ok`.
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`
  - `ALL 2382 ENTITY CHECKS PASSED`.
  - `claims hygiene: 93e6a63d2... ok`. The body quotes `46e368127`, the base at `bb53ba321`.
  - `ALL 124 closure shrink pins PASSED`, `layout self-test: ok`, `ALL 109 HARNESS HEADER CHECKS PASSED` and `STRUCTURE RATCHET PASSED`.
  - throwaway_git: 0 refused.
  - `Architecture score: dS +0.0000 NULL`.
  - The `PREPR_RECORD:-` grep gives one line, prepr.sh:564.
  - The sibling-seam rule returns 18 lines.
  - The release-file diff is quiet (rc 0), and the nightly-status filter prints nothing (rc 1).
  - I did not re-derive the body's null control for the sibling rule, a scratch copy giving 19.
- **Merge.** `git merge-tree --write-tree origin/main 1723d8743` exits 0 with tree `11cc21628` against main `93e6a63d2` (ev/merge-tree.txt). No version edit, per pr-contract's own step.
- **CI at this head** (check-runs API, 49 runs, read 01:46Z, ev/check-runs.tsv):
  - Red: `pr-contract` three times (the block) and `nightly-status` (119585492866).
  - `nightly-status` grades main's scheduled run 39563978649 (mutation-nightly and slow). Per its log, it is not a required check and does not block. The body answers it, and this diff reaches nothing that lane reads.
  - Green: `mutation`, `closure-scope`, `fast (3.14)`, `coverage` and `coverage-ratchet`.
  - Still in progress at write time: `closures` (119589007149) and `Analyze (python)`. The block does not turn on either, because pr-contract's refusal is a pure function of the body and main's roster.
  - Because those workflows had not all concluded, I did not post a step-11 `root-cause-unanswered`. I blocked on the required check's deterministic refusal instead.
- **Owner approval.** The policy half, gate-scoping.md and its two generated copies, still owes tvofi's approving review at the head. That review is not mine to give.
