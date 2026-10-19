Fix review: blocked 411bb47a0bfc17a689b4fdc1133ada9beb1c0b7a carry-missing: not carried to R10-POLICY-FIXER-MD

bus-nonce: 9c0a897988cfaf9fbd1524cba69702e4

Round 1 (the PR carries no earlier `Fix review:` comment). Measured head 411bb47a0bfc17a689b4fdc1133ada9beb1c0b7a (ev/HEAD), still the PR head at writing; merge base e8c67e1d3 = origin/main. Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty.

## Blocking (step 10, finding-propagation.md Enforcement)

The body records four findings with destinations, and none is in the tree:
- Forward-carry 1 (step 6f reads the committed tree; commit before prepr) -> `Carry: R10-POLICY-FIXER-MD`
- Forward-carry 2 (`mutation` line goes stale after mutation-autofix pins) -> `Carry: R10-BRIEFS-FOLD`
- Friction fixer.md#6 (handoff_push.sh vs no GitHub writes) -> `Carry: R10-POLICY-FIXER-MD`
- Friction tests/throwaway_git.py#check (greps its own repo; fixtures owe a shared clone, plants owe halves) -> `Carry: R10-CI-LAYOUT`

`handoff/audit-r10-roster` at fd84738671d96eb7ae8eaea62cb8dacf3bdb94cb and origin/main both: `grep -c '#2447' dev/programme/rosters/wave-r10-groups.json` = 0. R10-POLICY-FIXER-MD carries one entry (from #2368), R10-BRIEFS-FOLD's and R10-CI-LAYOUT's carry lists hold no #2447 entry, and no `dev/programme/carries/` file names 2447. The body names no roster SHA. The carries exist only in the PR body, which is `carry-missing` under fix-review.md step 10. carry_audit (pr-contract) passes because it checks only the markers and that the destinations are live, not that the text landed. Remedy: land the four roster carries (compare #2441 and #2448, which have `Source: #N ...` entries) and name the roster SHA in the body. Everything else below is verified, so a re-review needs check only the carry.

## Verified

- Step 1, mutation proof, re-run by me (ev/mut_*.txt, each a copy in tools/pr/ run with `--self-test`):
  - control (unmutated copy): 302 passed, 1 failed, and the one is `a change to prepr.sh owes the self-test` (path artefact, as the body says)
  - A, `reds+=(mutation)` line -> `:` : FAIL both mutation-arm rows the body names
  - B, the throwaway_git.py call -> `out=ok; r=0` : FAIL all three rows the body names
  - C (mine), `[ -s "$7" ]` dropped: FAIL `a diff with no unpinned site is unaffected` (the empty-file null control is load-bearing)
  - D (mine), `"$UNPINNED_SITES"` dropped from the step-7 call: FAIL the pr-body call-site row
  - E (mine), step 6f's `throwaway_line "$PWD"` replaced: FAIL the repository-build call-site row
  - head: `303 passed, 0 failed`, rc 0 (ev/selftest-head.txt)
- Step 2: the finding has no committed harness. The roster brief (wave-r10-groups.json, R10-PREPR-UNPINNED-RED) prescribes a three-arm control (refused / passes when named / unaffected with no site), and the self-test rows implement exactly those arms plus an absent-file arm and a budget-raise arm. I measured with those rows and with my own mutants C to E; I built no separate harness.
- Step 3, null controls: present and killed (mutant C proves the empty-site arm, and the control copy proves no spurious FAIL).
- Step 4: no golden or claim file touched (ev/golden.txt is empty).
- Step 5: VERSION, manifest.json and RELEASE_NOTES.md are untouched (ev/version.txt).
- Step 6: the brief states one seam and the body names no enumeration rule, so the class is one seam. Arms tried: empty site file, absent site file, and site plus budget raise (both reds owed, rc 1), all in the self-test and all pass.
- Step 7: the body's head 411bb47a0 matches.
- Step 8, figures re-derived at the head:
  - `throwaway_git.py --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`
  - `ref_privacy.py --check`: `... 0 refused`
  - `structure.py`: `STRUCTURE RATCHET PASSED`
  - `closure.py select`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, 3 changed files (the body lists 2 plus the delivery row it describes separately)
- Step 11, CI on this head (ev/check-runs.tsv): the only red is `nightly-status`. The body answers it as main's own red, and the diff touches no nightly record. `instrument-self-tests`, red on the first head, is answered in the body with its cheaper detector and is green here. `pr-contract` is green, and its run started 13:01:48, after nightly-status concluded at 13:01:33. `mutation` is green, and this diff's production lines are a shell instrument, not a mutation site. At writing, `Analyze (python)` (CodeQL) was still in progress and no other run was pending.
- Step 13: `git merge-tree --write-tree origin/main 411bb47a0` exits 0 (tree 0f8a6ca543dd), with no conflict and no claim-driver invocation.
- Step 14: no budget, closure, INERT, ledger or score file moved. The new fixture is classified, since `closures` and `fast` CI are green.

## Note (non-blocking)

Roster group R10-PREPR-UNPINNED-RED carries `Source: #2441 Friction. body_push.sh: unenforced: ... ci_predict.py ...`. The diff does not address it and the body does not disposition it. The same entry was copied to R10-CI-LAYOUT at roster 557f75372, which holds it now. The orchestrator should drop it from this group, or the body should disposition it, so the item does not have two destinations. Carry: R10-CI-LAYOUT
