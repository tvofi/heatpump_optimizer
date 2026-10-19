Fix review: blocked 411bb47a0bfc17a689b4fdc1133ada9beb1c0b7a carry-missing: not carried to R10-CI-LAYOUT (the ## Red checks carry: ref_privacy --check in prepr)

bus-nonce: 825e21ceef0d7ea559c712acb9b0b594

Round 2. Round 1 (comment 6268247849, same head) blocked only on carry-missing. Measured head 411bb47a0bfc17a689b4fdc1133ada9beb1c0b7a (ev/HEAD). It is still refs/pull/2447/head at writing, so the head did not move. origin/main is now d4fb5351b (ev/main), 7 commits past the merge base e8c67e1d3. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Blocking (step 10)

The body names five carries, each marked `(roster 1c71becaa)`. 1c71becaa is on handoff/audit-r10-roster, one commit behind its tip f0625eee9, which adds no #2447 text. The roster at 1c71becaa holds four `Source: #2447` entries (ev/carries.txt, ev/roster-1c71becaa.json):
- R10-BRIEFS-FOLD carry[15]: Forward-carry 2 (the `mutation` line goes stale after mutation-autofix pins the site). Present.
- R10-POLICY-FIXER-MD carry[1]: Forward-carry 1 (step 6f reads the committed tree, so commit before prepr). Present.
- R10-POLICY-FIXER-MD carry[2]: Friction fixer.md#6 (handoff_push.sh vs no GitHub writes). Present.
- R10-CI-LAYOUT carry[6]: Friction tests/throwaway_git.py#check (it greps its own repository; plants are spelled in halves). Present.
- **Missing:** `## Red checks`: "Cheaper detector: `python3 tools/audit/seat/ref_privacy.py --check` ... not in prepr; the standing cost is one more step there, left to R10-CI-LAYOUT's decision. Carry: R10-CI-LAYOUT (roster 1c71becaa)". No R10-CI-LAYOUT carry, and no carry anywhere in the roster, names ref_privacy. The only `ref_privacy` hit in dev/programme/ at 1c71becaa, and at f0625eee9, is a `files` entry at line 3140. R10-CI-LAYOUT carry[0] (from #2419) asks prepr to run tests/throwaway_git.py. That is a different detector and does not cover this one.

So four of the five carries landed. The fifth exists only in the PR body, which is `carry-missing` under step 10. Remedy: land a `Source: #2447 Red checks. ...` entry in R10-CI-LAYOUT's carry list, then re-cite the new roster SHA in the body. Nothing else needs a re-review.

## Re-checked this round

- Step 13: `git merge-tree --write-tree origin/main(d4fb5351b) 411bb47a0` gives rc 0 and tree f4629584ef71. There is no conflict and the claim driver was not invoked (ev/merge-tree.txt).
- Step 11, CI on this head (get_check_runs, 52 runs, all completed; ev/check-runs.txt): the only red is `nightly-status`, and the body answers it as main's red. `instrument-self-tests`, red on the first head, is answered in the body and is green here. The latest `pr-contract` run (13:28:42) is green and started after nightly-status concluded (13:01:33). `mutation` is green. `Analyze (python)`, which was still running in round 1, has now concluded success.
- Self-test at the head: `303 passed, 0 failed` (ev/selftest-head.txt), which matches round 1.
- Step 5 / step 4: VERSION, manifest.json, RELEASE_NOTES.md and tests/golden are untouched (ev/version-golden.txt is empty).
- Steps 1-3 and 6-8, 14: the head is unchanged since round 1, which verified the mutation proof (mutants A and B as the body states, and the reviewer's C, D and E), the null controls and the figures. Those results stand at this same SHA. I did not re-take the mutants this round.

## Carried from round 1 (non-blocking)

R10-PREPR-UNPINNED-RED's own carry list still holds the #2441 body_push.sh/ci_predict entry, which R10-CI-LAYOUT also holds. That leaves one item with two destinations, and it is the orchestrator's to drop.
