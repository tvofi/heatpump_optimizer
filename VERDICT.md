Fix review: merge d8988a473a4d1c282278ecee1c1b37ddd22754f5

bus-nonce: e3cdb09c0f8b544a7fd741cac6c8de87
seat: review-2069 (round 3, the last under the three-round rule; reviewed the one commit e23a19ac..d8988a473a4d1c282278ecee1c1b37ddd22754f5, app_push.sh only)
head measured: d8988a473a4d1c282278ecee1c1b37ddd22754f5 (PR body ## Head names it; live head re-read at posting)

## RESULT lines

Round-2 blocker (SIGPIPE under pipefail), production recarry_verdict on a local clone of the real repository (evidence/attack_r2_sigpipe.sh -> attack_r3_sigpipe.txt):
RESULT run=1..3 honest-recarry-real-history pipefail=on rc=0 SKIPPED (was rc=1 x3 at e23a19ac)
RESULT control pipefail=off rc=0
Round-1 harness (evidence/attack_p2_side.sh -> attack_r3_head.txt):
RESULT attack=p2-side-branch rc=1 (first-parent refusal); control=honest-main-merge rc=0; spoof, extra commit, swapped parents, -s ours, body whitespace rc=1; API/fetch failures rc=1 (fail closed); CRLF rc=0, harmless (bytes PATCHed equal the bytes compared).
Mutation proof: restoring `grep -qx` (evidence/app_push.r3-mutant.sh) -> app_push self-test 91 checks, 3 failed (the honest null control and both (b) cases now hit (a)); at head 91 checks, 0 failed. The fixture's 6000-commit main asserts > 64 KB of rev-list output.
Local at head: merge_train self-test 83/0 failed; throwaway_git --check 0 refused.

## Early-exit scan under pipefail

Every pipeline the PR adds or touches in *.sh (three-dot from the merge base): grep -E (no -q/-m) with || true, python3 json.load(sys.stdin) (reads to EOF), sed, wc, awk without exit, grep -x >/dev/null, grep -c. No reader that quits before EOF remains.

## Step 11 (settled)

40 check-runs at this head, all completed: 25 success, 14 skipped, 1 failure -- nightly-status, main's nightly, named in Red checks as not this PR's; this diff reaches nothing it reads. The reds at 6b1d0c46 (instrument-self-tests, pr-contract) are answered in the body with the cheaper detector and its routing to root-cause. Full suite and mutation are CI's; cited, not re-run.

## Decision fit (6070202495) and (c)

(a) parent 1 = live head, parent 2 on origin/main's first-parent chain after a fresh fetch; (b) tree == clean merge-tree; (c) body equal to the live body before the script's note, whose head sha comes from the judged HEAD (pr-contract re-checks it) and whose main sha is parent 2. The departure keeps (c)'s intent. HEAD is pinned at the verdict and re-checked before minting; the push is non-force, so a moved PR head refuses. Step 15: no fixer.md 17 breach on added lines.

Residual, not blocking: the skip relies on the PR's existing head having passed prepr; a head pushed around app_push is outside this flag and is still graded by CI's pr-contract and suite.
Evidence: /Users/timmalmstrom/hpo-seats/review-2069/evidence
