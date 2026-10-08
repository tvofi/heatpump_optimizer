Fix review: merge afe9cfd87649cfc1de24608267fab4fdcf33ce6a
bus-nonce: 87355895ca90024075c4c3f6f2bb090f

Round 2. I measured head afe9cfd87649cfc1de24608267fab4fdcf33ce6a, which was still the live head at posting. Evidence: /Users/timmalmstrom/hpo-seats/review-2059/evidence (RESULTS-r2.txt, r2_*.out, r2_checkruns.json).

Both round-1 blocks are cleared.
1. Reds. At this head CI has settled: 38 check runs, none pending. Only delivery-status and nightly-status are red, both main's state, and the body names and answers both. The round-1 reds are named and answered too (CodeQL alert #35, pr-contract run 37777939476). The CodeQL fix is chmod 0o700 at merge_main_bot.py:247, and CodeQL passes at this head.
2. pr-contract's bot-merge check. autofixMerge now requires the second parent to be on origin/main and reads .gitattributes at origin/main.
   - Both of my round-1 forgeries (3f27aed, ae285c7) and their re-forges on this head (17d94aa, 74f5717) are refused with "not on origin/main".
   - A bot merge of a real main is still accepted.
   - Mutant: removing the ancestor check lets the code-edit forgery through again, so the check does real work. The entities fixture now includes both forgery shapes.
   - pr-contract checks out with fetch-depth 0, so origin/main is present there.

Carry, with forged authors:
- A seat-authored commit under a bot subject is refused.
- A claim subject adding a claim line is refused.
- Two mutants confirm the new tests catch each guard removed: author check off gives 1 of 153 failed; claim add-only check off gives 1 of 153 failed.
- A forged bot email still carries. The code comment says so: the author check narrows the forgery surface but does not close it.

Pre-existing, not introduced here: a generic "ci: <anything>" commit can still add a claim line or edit a driver file such as structure_budgets.json and carry; main's copy behaves the same. orchestrator.md section 11's separate condition that the claim files equal origin/main's catches the claim case, and budget-raise-gate gates the budget case. One wording point: the new code comment says a forged commit cannot add a claim, but that is true only for the named subjects.

Round-1 notes, all addressed:
- fixer.md step 6 now names the merge-main bot.
- The ci-autofix.md heading is rewritten.
- The merge-main.yml concurrency comment is corrected.
- The self-test count in the body is now 24.
- Policy caps hold and rules_sync passes.

Self-tests at this head: app_approve 153/0, merge_main_bot 24/0. VERSION and the manifest are untouched.
