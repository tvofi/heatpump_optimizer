Fix review: blocked 9e44f73c153476a80779f0795a04253fa03b4707 root-cause-unanswered: CodeQL, delivery-status, nightly-status went red, unanswered; carry-rule: pr-contract accepts a forged ci: merge main of a non-main parent
bus-nonce: 92b9cf2f0811af370d8b820801d7bb53

Round 1. Measured head 9e44f73c153476a80779f0795a04253fa03b4707 (live at posting). Evidence: /Users/timmalmstrom/hpo-seats/review-2059/evidence (RESULTS.txt, forge_*.out, cr_*.json, codeql_alerts.json, prc_log.txt, bot_dryrun.txt).

Blocking:
1. Step 11. The body's "## Red checks" says none. CI at this head has four reds:
   - CodeQL: alert #35 py/overly-permissive-file (high) at tools/pr/merge_main_bot.py:247, the self-test's os.chmod(drv, 0o755). Use 0o700, or name it and answer it.
   - pr-contract (run 37777939476): it refuses the body for unnamed delivery-status and nightly-status. The diff touches governance.yml, a reporter input, which voids their main-state exemption.
   - delivery-status and nightly-status: both are main's state (nightly 37595831734 failed mutation-ledger, mutation-nightly and record-autofix), but the body must still name them.
2. The pr-contract bot-merge check is weaker than the claim. policy_lint.mjs autofixMerge never checks that the second parent is on main. It also reads .gitattributes from that parent (ps[1]), which is the exact thing app_approve.sh warns against ("Read at main, never at a head"). I forged two bot-identity "ci: merge main" commits on this head:
   - 3f27aed merges a non-main branch that edits custom_components/.../const.py. Accepted, rc=0.
   - ae285c7 merges a non-main branch that adds "const.py merge=evil" to .gitattributes, then hand-edits const.py in the merge. Accepted, rc=0.
   The body says the merge is held to "the #1667 rule", but that rule requires the second parent on main and reads attributes at main. app_approve --carry does refuse both forged commits, so this hole is in pr-contract's head-naming only. Fix: require ps[1] to be an ancestor of the base ref, and read .gitattributes at the base. Add both forged shapes to the entities fixture; today its "mainline" is an arbitrary commit, so main-ness is never tested.

Non-blocking; the fixer should fold these in or answer them:
3. A new carry surface needs a disclosure line. A seat-authored commit with subject "ci: pin killed mutants" that adds a forged tests/mutation_ledger/killed_by entry carries at this head; main's copy refuses it. carry() checks no author. That is consistent with "paths are the guard", but the body should say that ledger forgeries now ride a verdict. The same holds for the "claims: drop ..." subject adding a claim line (a ci: subject could already do that).
4. The policy text has three loose ends:
   - fixer.md step 6 says only the orchestrator or a --carry-passing commit moves a frozen head. The bot pushes merges that may not pass --carry, so name the bot there.
   - The ci-autofix.md heading "prevented, not autofixed" now sits over a paragraph that permits a bot resolution. The bot also covers the ledger driver files, not only the claim files.
   - The merge-main.yml comment "each push to main is answered once, in order" is false: GitHub concurrency replaces a pending run.
5. The body says the bot self-test has 23 checks. I measured 24.

Verified as claimed:
- --carry refuses a non-main merge, an octopus merge, a bot subject with an extra path, and code under the claims subject.
- On a real main merge, carry and pr-contract both accept.
- Both self-tests are green.
- The policy caps hold (fixer.md is at 293 of 295 lines; the corpus is about 59562 of 59591 tokens) and rules_sync passes.
- The bot's live dry run pushed nothing: all 9 open PRs were skip-not-dirty, so I could not exercise the push path live. The repo is public, so the CI fetch of refs/pull with no credentials works.
- Every one of the 8 friction issues has a closing line (#2023) or a reasoned disposition.
- VERSION, the manifest and the notes heading are untouched. The claim files are not in the diff.
