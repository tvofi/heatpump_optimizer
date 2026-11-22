Fix review: merge 9f7807595e6db0a2b48f0071ac69fcc16222e4a2

bus-nonce: 039392fbc28a8db148319b0aaa75c365
pending-ci: gate

## Summary

Round 1 (first review, full scope). The diff adds two files: `dev/audit/rca/R11-RCA-ENOBUFS.md`, a root-cause record, and its delivery row. It changes no production code, test or policy file, so there is no mutant to draw. Steps 1 to 3 are n/a by construction: no finder's harness is named for a record, and the hotfix's own mutation proof is #3840's to carry. `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched.

Note: figure-wrong: section 5 says "A new uncapped reader written today fails on its author's first run, because the listing already exceeds 1 MiB". That contradicts section 1's own table: main at `4ebd430fbf` lists 1,033,586 bytes, under 1,048,576, and `origin/main` `f269ecccb5` is still under the cap. Only branch heads exceed it. Since the hotfix #3840, the barrier for that shape is #3840's `TREEREV` probe, which lists over 1 MiB on any tree, not the real listing. The refusal's conclusion survives on that ground, but the stated reason is false.
Note: figure-wrong: the section 2 table gives `64fd552732`'s listing as 564,030 bytes. `git ls-tree -r --name-only 64fd552732 | wc -c` prints 552,952, and first-parent main at 2026-11-05 (`7d95405e38`) prints 566,049. Neither matches. The share of the cap is 53% to 54% either way, so no conclusion moves.
Note: precondition-unmerged: the decision in section 6 rests on #3840's shared `gitRead`, and #3840 is open and unmerged at review time. `git grep gitRead origin/main -- tools/policy/` prints nothing. If #3840 changes shape or does not land, this record's refusal has no basis. This PR should merge after #3840.
Note: carry-control: the roster carry (`handoff/audit-r11-roster` tip `582010efc2`, `a12d6d0950` an ancestor) is present and names its revisit trigger, but it states no re-measurement command for its figures. The enumerator is `git ls-tree -r --name-only <rev> [-- <path>] | wc -c`.

## Findings

- Follow-up: the class-search counts in section 4 (14 / 16 / 13 uncapped sync `git` calls) come from `buffer_scan.mjs`. That instrument is out of tree, at `hpo-orch/r10s6/r11/proto/RCA-ENOBUFS/`, and this seat cannot run it, so those three counts are not verified here. The record keeps it as a prototype and proposes no gate. Because nothing gates on it, landing it is owed only if a later sweep re-uses the counts. Carry: dismissed: the record proposes no gate, and the counts support a refusal that #3840's own scan corroborates independently (its body's scratch scanner lists no tree-listing read beyond the closed helpers).

## Evidence

- `git merge-tree --write-tree origin/main 9f7807595e6db0a2b48f0071ac69fcc16222e4a2` printed one tree, rc 0: it merges cleanly with `origin/main` `f269ecccb5`.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` printed nothing, so this role contract is current.
- Re-derived at the cited commits, all equal to the record (`ev/rederive.txt`): listings 1,030,967 / 1,033,586 / 1,074,652 / 1,069,422; `tests/mutation_ledger/` 552,886, `dev/audit/` 356,425, product 5,989; 2026-09-07 20,402; 2026-11-19 903,376; 11-08 to 11-21 growth 420,975 bytes (421 KB); 11-15 to 11-21 growth 287,741 bytes (288 KB); `0b42121411` 17,162. `282731eaed` lists 164,790 against the record's "~164,275 (10-01)", which the record marks approximate and dates to the day before.
- The reader line citations hold at `4ebd430fbf`: `brief_lint.mjs:76` and `:116`, `agreement.mjs:43`. None of the three sets `maxBuffer`.
- `git grep -il maxbuffer` over `dev/governance .claude/rules CLAUDE.md RELEASE_NOTES.md` at `origin/main` prints nothing, as section 3 states.
- Not re-derived: the CI run 44939097064 ENOBUFS line split (58 across six jobs), the red-run count of 7, the wall-hour estimates, and the #608/#672 dates of the existing 64 MiB caps. The tools moved to `tools/policy` on 2026-10-06 (`3b0a39216b`), so `-S maxBuffer` on the current paths starts there.
- Section 3's process state (d) is consistent with the measured shares: 1.6% of the cap at the first helper's introduction and 54% at `treeListing`'s.
- The body's carry_audit, as rendered in the packet: `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`.
- CI: `merge_train.py classify 9f7807595e6db0a2b48f0071ac69fcc16222e4a2 --pr 3842` printed `WAIT 9f7807595e6db0a2b48f0071ac69fcc16222e4a2 pending: gate red: none` (rc 3) on every poll from 02:41:52 to 03:09:28Z (`ev/classify-poll.log`). At 03:09Z every other required lane read success, `pr-contract / pr-contract` was queued, and `tests / coverage` and `tests / coverage-ratchet` were green. The earlier `gate` failure (job 137065157377) is the aggregator's run before the lanes finished, and classify reads it as pending with no red. The relay posts this verdict only once CI is green at this head.
- Owed reds (`merge_train.py owed-reds`, `ev/owed-reds.txt`): no required check is red at this head, so `## Red checks` owes nothing.
- Head re-read before return: `git ls-remote origin refs/heads/fix/rca-enobufs` = 9f7807595e6db0a2b48f0071ac69fcc16222e4a2, unchanged.
