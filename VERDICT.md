Fix review: blocked a8d19cf1950250e378b3cf0dfd4f8c5c29e01255 policy-unapproved: the repair cut the approved #2429 bound (by tests/mutation's conclusion, the pin owed by the handoff) though the approved text fits the cap, and the body still calls it approved and bounded

bus-nonce: f3c0b7a78e657ecde3f7bb18b4959109

Round 2 (the second review; the body numbers the repairs from 0, so it calls this "repair round 1"). I measured head `a8d19cf1950250e378b3cf0dfd4f8c5c29e01255` from a detached worktree at that head. The merge base is `9cbd7dd0d7a66163b5b593dfe55f1d8b220785de` and origin/main is `28482eceeb6b`. `git diff <base>...origin/main -- dev/governance/roles/` is empty, so this contract is current.

## Block

1. **The repair weakened the approved #2429 countermeasure, and the body does not say so.** The text that was drafted and approved (`R10-RCA-FRICTION-RESIDUE.md` section 7) is a bound: "if `mutation-pins` has not concluded by `tests / mutation`'s conclusion, the pin is owed by the handoff and the body says `unmeasured`". The record names its cause as "states no terminating condition for the wait". Round 1's head carried that bound. This head has only "Until `mutation-pins` concludes the body says `unmeasured`". That drops both the terminating condition (`tests / mutation`'s conclusion) and the obligation (the pin is owed by the handoff). Under the new text, a body may say `unmeasured` for as long as the pins run and owe nothing at handoff. That is the state the countermeasure was written to end. The body's `## Approval` still says the `ci-autofix.md` sentences are the approved countermeasures, and calls them "shortened as far as they go". `R10-RCA-FRICTION-SWEEP.md` section 4(3) still says "the wait is bounded".
   - **The shortening was not forced by the cap.** I planted the approved wording in place of the head's sentence, in all three copies via `rules_sync.mjs`. `node tools/policy/policy_lint.mjs --budgets` then reads `.claude/rules/ci-autofix.md 88 96 1469 1469`, rc 0: it fits exactly. The head reads 1450 / 1469, which leaves 19 tokens of headroom.
   - **Cure:** restore the approved clause verbatim ("If `mutation-pins` has not concluded by `tests / mutation`'s conclusion, the pin is owed by the handoff and the body says `unmeasured`;"). It fits, as shown. Then correct `## Approval` and the sweep record to match. Alternatively, list this change under `## Approval` as one the approval does not cover, with its reason.

## Policy touch

This PR changes policy. The changed files are `dev/governance/rules/ci-autofix.md` with its generated `.claude/rules/` and `.cursor/rules/` copies, and the family map in `tools/policy/policy_lint.mjs`, which decides what the cron files. It merges **only on tvofi's approving review at the head**, as `main-protect-checks`' code-owner rule requires. Every changed policy sentence, base -> head:

- Removed: "A failed recording reads files a clean run never does (`linecache`): an UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records." The body now discloses this as not covered by the approval.
- Changed: "When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants` stales the body's `## Red checks` `mutation` line; the reviewer re-checks it." -> "When `mutation-autofix` goes red, run `--pin-killed` yourself. Until `mutation-pins` concludes the body says `unmeasured`; `pinned` only if `--pin-killed` ran on this head. A pin stales the body's `## Red checks` `mutation` line; the reviewer re-checks it." The first added clause is narrower than the approved text (Block 1).
- Restored since round 1: "(kept until M-3)" and "; the reviewer re-checks it". Both are byte-identical to base.
- `policy_lint.mjs` filing behaviour: a derived `other (untaught)` verdict family; a declared `root-cause` family over `root-cause-unanswered`, `-detectable` and `-unrecorded`; three new `mutation` members, `mutation-unpinned`, `unpinned-site` and `mutation-survivors`. The body discloses the last three as not covered by the approval.

## Findings

- The approval citation ("All of these are approved.", 2026-10-29) still resolves only to restatements. They are comments posted from the tvofi account at 2026-10-29T16:26Z, e.g. #2429 comment 6502326884, which say "tvofi approved the drafted countermeasures" (`ev/approval.txt`). No primary owner statement was found. The required approving review at the head supersedes it. Carry: dismissed: tvofi's approving review at the head is required for this policy PR and is the approval of record.
- One surviving `policy_lint` mutant on a line the PR changed. In `statsFindings`, `kind === 'verdict family' ? derivedInput(blocks, passing) : null` -> `derivedInput(blocks, passing)` (the derived family also applied to friction rule ids) keeps acceptance green, rc 0 (`ev/policy_lint_mutants.txt`). That would file a spurious `other (untaught)` family over every friction rule id. Cure: add a friction-id row to the end-to-end pin and expect no friction-family would-open. Carry: R10-FRICTION-RECORDS
- Round 1's undisclosed `ci_predict` survivor is not addressed. `tools/pr/ci_predict.py` is byte-identical to round 1's head (`git diff f676a8f5 HEAD -- tools/pr/ci_predict.py` is empty). With `(quoted | {rel}) & changed` -> `quoted & changed`, `--self-test` stays green, so a change to a driver alone does not run that driver's self-test. The body still does not disclose it. Carry: R10-FRICTION-RECORDS
- #3156 (`ci-red`) is still in the roster group's `issues`, on main and on `handoff/audit-r10-roster`, with `fixes: []`. The body and `R10-RCA-FRICTION-SWEEP.md` section 4b now state it is not disposed and ask to re-route it. No other group holds it yet, so the orchestrator owes the re-route before wiring `fixes` from `issues`. Carry: #3156
- The body's `## Head` again prints a bare `fa17a2ce3e95e244f6cc02fb9b5e569d48d9d908`, an earlier merge commit, under the sentence naming the real head. `## Red checks` again says "CI has not run on this repair head", and it cites check-run ids (128176685376, 128177203099, 128193127838, 128178014767, 128190924268) that are none of this head's 94 runs. The head's own cancelled run is `governance / instrument-self-tests` 128195844614. Carry: R10-FRICTION-RECORDS

## Evidence

- HEAD reviewed: `a8d19cf1950250e378b3cf0dfd4f8c5c29e01255` (`ev/HEAD.txt`); the PR head at the time of reading.
- CI: `python3 tools/audit/seat/merge_train.py classify a8d19cf1950250e378b3cf0dfd4f8c5c29e01255 --pr 3255` gave `GREEN ... pending: none red: none`, rc 0 (`ev/classify.txt`). The first run gave WAIT (gate pending).
- Check runs: 94 at the head, all pages, in `ev/check_runs.tsv`. The only non-green is `governance / instrument-self-tests` 128195844614, cancelled at 21:54:20 -> 22:24:35Z, which is the 30-minute timeout. That is the owner's standing line (cure R10-PROCESS-SLIM, #3245), and the body answers it by name. Every `gate` run is success (128195704504, 128195846523, 128196438112, 128197262837, 128197669350). The edit-run race is settled green. `pr-contract / pr-contract` 128196078575 succeeded at 22:38Z, after the cancel concluded. The step-11 trigger is answered.
- Merge with main: `git merge-tree --write-tree origin/main <head>` rc 0, tree `b7d86c188ce0` (`ev/merge-tree.txt`).
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`, rc 0 (`ev/rules_sync.txt`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc 0 (`ev/structure.txt`).
- `--budgets`: `ci-autofix.md` reads 88 / 96 lines and 1450 / 1469 tokens, rc 0 (`ev/budgets.txt`). With the approved clause planted it reads 1469 / 1469, rc 0 (Block 1).
- Untouched: the three-dot diff over `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files, every `*_budgets.json` and `tests/closures.json` is empty (`ev/untouched.txt`). There is no budget raise and nothing claimed.
- `policy_lint` mutants at the head (`ev/policy_lint_mutants.txt`). The null control is the unmutated tree: rc 0, `FIXTURE ok: 93 error(s) hold 269 pins`.
  - KILLED: `statsFindings` passes null; `cmdStats` passes no derived list; `derivedInput` returns null; each of `mutation-unpinned`, `unpinned-site` and `mutation-survivors` dropped; the passing exclusion removed; `root-cause-unrecorded` removed.
  - SURVIVED: the derived family applied to friction ids (Findings).
  - All of round 1's survivors in Block 3 are now killed. That block is cured.
- Round 1 Block 2 (#3156) is cured as a disclosure: the `Disposes` lines are the roster `issues` less #3156, and the body states #3156's disposition. Round 1 Block 1 is cured for the two restored phrases and the `linecache` disclosure, but the repair introduced Block 1 above.
- `R10-RCA-CLASS-OPEN.md` section 7 now reads 32 / 56 / 23, consistent with sections 1-5. That round-1 finding is fixed.
- Not re-derived this round: the `--stats --since v7.0.4` figures, the driver timings and the cost arithmetic. The records' figures are unchanged since round 1, which re-derived them (round-1 verdict, `verdict/3255` at 318fa443).
- There is no closing keyword in the body.
