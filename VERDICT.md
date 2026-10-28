Fix review: merge d4b017368d585900b2705a39821cc78681fb4217

bus-nonce: e47408d9b3fa832194c541cd8e503990

Round 2 of PR #2736 (policy(D11): mechanise-first). I reviewed head d4b017368d585900b2705a39821cc78681fb4217 in a detached worktree. It was still the PR head when I wrote this (`ev/heads_at_write.txt`). origin/main is now 73b69fe0a. It moved from the base e97f5749b by delivery rows only (`ev/main_moved.txt`). The role contract is origin/main's fix-review.md: `git diff $(merge-base)...origin/main -- dev/governance/roles/` prints nothing. I reviewed this as a policy change. I checked every sentence the three-dot diff adds, cuts or rewrites in D11.md for a binding it adds, drops or loosens.

## Findings

- **I could not verify the owner quote as verbatim.** The body names its source as the orchestrator's session chat on 2026-10-24 and says there is no GitHub record. I found none either:
  - tvofi's 48 #201 comments from 2026-10-23T10:23Z to 2026-10-24T15:04Z contain no "mechani" or "one shot".
  - `git log --all -S'could be mechanical'` finds only this PR's commits and the round-1 verdict refs.
  - The two rounds quote the ruling differently. Round 1 (cf212c29e, fbbd3e61) has "operation or shape that is not clearly a one shot". This head has "that that [sic] is not clearly". Commit 715dd4193 calls the new text the verbatim correction.
  - Only the holder of the chat can say which is true, and the orchestrator merges this under the mandate, not after an owner review. Nothing else in the quote moved between rounds.

  Carry: dismissed: the quoted source is the orchestrator's own session chat, which it compares before merging under the mandate
- **The body's root-cause answer for the round-1 `governance / wave-script` red stops short of the cause.** `tools/pr/prepr.sh:3082-3087` runs the wave-script step only when the diff touches certain paths, and one of them is `'tools/audit/briefs/*.md'`. That directory no longer exists: the briefs moved to `dev/governance/dimensions/`. So a diff that touches only a brief skips the local step, which CI runs unconditionally. `dev/audit/config/rotation.json` and `scopes.json` are not on the trigger list either (`ev/prepr_wave_trigger.txt`). The repair is a path fix in the N-move-stale-path class, not a new mechanisation proposal. The body's `Carry: proposal-triage` sits under `## Red checks`, which `carry_audit.py` does not read as a finding (`ev/carry_audit_body.txt`: 0 items), so nothing routes it. Step 11 is still met: the red is named and answered with a cheaper detector and its standing cost. Carry: R10-FLOW-JIDOKA

## Evidence

- **Head.** Reviewed d4b017368d585900b2705a39821cc78681fb4217 (`ev/HEAD.txt`). The body's `## Head` names the same SHA.
- **Merge.** `git merge-tree --write-tree origin/main` (73b69fe0a) gives tree b8f35532ae, rc=0, no conflict (`ev/merge_tree.txt`).
- **Versions.** VERSION, the manifest and `RELEASE_NOTES.md` are untouched by the three-dot diff (`ev/version_untouched.txt`, `ev/diff_three_dot.txt`). The head commit carries no Co-Authored-By or Claude trailer.
- **Critical severity line.** The `Severity:` paragraph through "hygiene." is byte-identical to origin/main (`diff` prints nothing). This settles round-1 Block item 1.
- **Scope.** "the repository's history and GitHub's own records" is restored unchanged. This settles round-1 Block item 3.
- **Step 5 against the quote.** Step 5 is the quote followed by two routing sentences:
  - The quote keeps "or shape", "wired into the machinery" and the owner's test "could be built at a reasonable cost (tokens, time, complexity)".
  - "A finding goes to `proposal-triage.md` as a mechanisation proposal, costed in its terms and D13's" adds routing only. It narrows no finding.
  - "a non-finding records why no script could be built at that cost" restates the owner's test rather than a weaker "no script exists".
  - No recurrence-count burden is left.
  - This settles round-1 Block item 2.
- **Cuts I confirmed against the text that carries them at this head:**
  - "Record every such source under `exposure`": COMMON.md (".. or GitHub (D11), record it under `exposure`").
  - "The audit register and earlier findings stay off-limits": COMMON.md ("do not look for earlier findings anywhere").
  - "You get a worktree with `.git`": `.claude/workflows/audit-find.js` ISOLATED and its GitHub-reader list. COMMON.md also names D11 among the isolated-worktree briefs.
  - The definition of a perturbation: COMMON.md item 3.
  - "a ruleset read with both arms": the branch-rules fooled-before item.
  - The checks-summary trap: step 3's "(the commit's check-runs listing, which keeps the red run a summary drops)".
  - "A number about the document it sits in goes stale": step 1's "Derive the row count; never carry it from a document". `brief-citations.md` and `brief_lint.mjs` enforce the same rule for brief text. This was a fooled-before caution, not a binding.
  - No cut removes a binding.
- **Figures.** I re-derived all of them with `node tools/policy/policy_lint.mjs --budgets` at origin/main 73b69fe0a and at the head (`ev/budgets_main.txt`, `ev/budgets_head.txt`). The D11 row is byte-identical between main and the base. All match the body:

  | figure | before | after | cap |
  |---|---|---|---|
  | D11 lines | 99 | 99 | 103 |
  | D11 tokens | 1497 | 1499 | 1499 |
  | Corpus tokens | 66415 | 66417 | 66434 (+500 band) |

  The add-only variant's 6688 bytes and 109 lines are the drafter's out-of-tree draft, and I could not re-derive them. 5997 bytes is consistent with 1499 × 4.
- **Lint and wave-script at the head.** `node tools/policy/policy_lint.mjs` reports 0 errors across 50 policy files (`ev/policy_lint_head.txt`). `node tools/policy/check-wave-script.mjs` reports 209 passed, 0 failed (`ev/wave_script_head.txt`). Main gives the same results (`ev/*_main.txt`).
- **D11.M5 placement.** `scopes.json` D11 has steps M1–M5, and seat s3 holds `["M4","M5"]`. `rotation.json` D11 steps are M1–M5.
- **Mutation proof.** Every mutant below was aimed at D11 only, and the tree was restored after each one. Everything also re-ran clean afterwards.

  | mutant | result | evidence |
  |---|---|---|
  | rotation.json D11 without M5 | rc=1, "rotation.json D11 lacks D11.M5" | `ev/mutant_rotation_D11_noM5.txt` |
  | scopes.json s3 seat without M5 | rc=1, "no D11 seat names D11.M5" | `ev/mutant_scopes_D11seat_noM5.txt` |
  | scopes.json D11 steps without M5 | rc=1, "scopes.json D11 steps [M1..M4] != the brief's" | `ev/mutant_scopes_D11steps_noM5.txt` |
  | D11.md step 5 unnumbered | rc=1, "rotation.json D11 names D11.M5, which the brief no longer has" | `ev/mutant_brief_noStep5.txt` |
  | step 5 names `tools/audit/seat/INSTRUMENTS.md` | rc=1, `[named-docs] ... has no cap` and `[budgets]` 1508 > 1499 | `ev/mutant_instruments_md.txt` |
  | quote cut to drop "(tokens, time, complexity)" | lint rc=0 | `ev/mutant_quote_trim_lint.txt` |

  My first rotation and scopes mutants hit D2's block, not D11's. Their outputs are kept as `ev/mutant_*_noM5.txt` and were re-run targeted.
- **No instrument pins the quote.** The quote-trim mutant passing shows that no check holds the quote's wording. Its fidelity rests on the comparison in the first finding.
- **CI on the head** (`ev/check_runs.txt`, commit check-runs listing): no run is red.
  - Succeeded: arch-score, budget-raise-gate, tests / briefs, prelude, refresh, cancel-superseded.
  - Queued or running: wave-script, policy-docs and the others listed in the file.
  - No `pr-contract` run was listed yet.
  - The only red in the range is round 1's `governance / wave-script` at fbbd3e61, and the body names and answers it.
- **Round.** This is round 2.
