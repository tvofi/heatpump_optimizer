Fix review: blocked a8d19cf1950250e378b3cf0dfd4f8c5c29e01255 policy-unapproved: the dispatched head is the round-3 blocked head unchanged, so the cut #2429 bound survives; the round-3 repair sits on handoff-wip/r10-friction-records and never reached the pull request

bus-nonce: a4a444801a1988a171381afd57cac97a

Round 4. I measured head `a8d19cf1950250e378b3cf0dfd4f8c5c29e01255` from a detached worktree at that head.

## Block

1. **The round-3 block survives, because no repair reached this head.** The brief says this head is the round-3 repair, a minimal restore of the approved #2429 bound. It is not. `a8d19cf1950250e378b3cf0dfd4f8c5c29e01255` is the head that round 3 blocked (`verdict/3255` at 68a200f53). It is also the live PR head (MCP `get`) and the tip of `fix/r10-friction-records` (`ev/head_vs_repair.txt`). Line 79 of `dev/governance/rules/ci-autofix.md` still reads "Until `mutation-pins` concludes the body says `unmeasured`;". That is the cut bound: it has no terminating condition and no "the pin is owed by the handoff".
   - The approved text (`R10-RCA-FRICTION-RESIDUE.md` section 7) is: "if `mutation-pins` has not concluded by the next `tests / mutation` conclusion, the pin is owed by the handoff and the body says `unmeasured`".
   - `R10-RCA-FRICTION-SWEEP.md` line 134 at this head still says "the wait is bounded". The body's `## Approval` still calls the `ci-autofix.md` sentences the approved countermeasures. Both claims are therefore still wider than the text.
   - **Where the repair is.** The round-3 repair exists as a9d4bf12 ("restore the approved #2429 bound, kill two survivors") and 9ca25bb8d (sweep section 4) on `handoff-wip/r10-friction-records`. 9ca25bb8d is not an ancestor of the head. `handoff/r10-friction-records` is still fa17a2ce3e95e244f6cc02fb9b5e569d48d9d908, which is the code already in this head. So the dispatch resolved the stale handoff ref, and the body's `## Head` ("unchanged: its code was already in it") was set from it.
   - **Cure:** promote the round-3 repair to `handoff/r10-friction-records`, push it to the PR via `app_push.sh`, then re-dispatch review at the new head.
   - **What I could not do this round:** the line-by-line diff against the approved text and the mutation of the restored bound, which the brief asks for. They have nothing to run on until the restored bound is in the PR.

## Policy touch

This PR changes policy. It merges **only on tvofi's approving review at the head**, which `main-protect-checks`' code-owner rule requires. The changed policy sentences, base -> head, are unchanged from round 3:

- Removed: "A failed recording reads files a clean run never does (`linecache`): an UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records." The body discloses this as not covered by the approval.
- Changed: "When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants` stales the body's `## Red checks` `mutation` line; the reviewer re-checks it." -> "When `mutation-autofix` goes red, run `--pin-killed` yourself. Until `mutation-pins` concludes the body says `unmeasured`; `pinned` only if `--pin-killed` ran on this head. A pin stales the body's `## Red checks` `mutation` line; the reviewer re-checks it." The first added clause is narrower than the approved text (Block 1).
- `tools/policy/policy_lint.mjs` filing behaviour:
  - a derived `other (untaught)` verdict family;
  - a declared `root-cause` family;
  - three `mutation` members (`mutation-unpinned`, `unpinned-site`, `mutation-survivors`), which the body discloses as not covered by the approval.
- The approval citation ("All of these are approved.", 2026-10-29) still resolves only to restatements posted from the tvofi account (round 3's `ev/approval.txt`). The approving review at the head is the approval of record.

## Findings

- The stranded repair a9d4bf12 also differs from the approved text. It writes "by `tests / mutation`'s conclusion", where section 7 says "by the next `tests / mutation` conclusion". Round 3's cure suggested the same shorter wording. The next round should diff the two. Either say "the next", or name the difference under `## Approval`. Carry: R10-FRICTION-RECORDS
- Round 3's surviving `policy_lint` mutant, where the derived family is applied to friction ids, is unchanged at this head. The repair claims to kill two survivors, so this must be re-checked once the repair is on the PR. Carry: R10-FRICTION-RECORDS
- Round 3's unaddressed and undisclosed `ci_predict` survivor is also unchanged here (`(quoted | {rel}) & changed` -> `quoted & changed`). Carry: R10-FRICTION-RECORDS
- #3156 (`ci-red`) is still in the group's `issues` and is not disposed here. The orchestrator owes the re-route before wiring `fixes`. Carry: #3156
- The dispatch for this round named an unrepaired head as the repair: `handoff/` was never advanced past fa17a2ce while the repair sat on `handoff-wip/`. That cost one full review round. Carry: dismissed: one instance, recorded here for the orchestrator; it is not a class yet.

## Evidence

- HEAD reviewed: `a8d19cf1950250e378b3cf0dfd4f8c5c29e01255` (`ev/HEAD.txt`). The live PR head is the same.
- Refs, ancestry, the head's bound line, the approved text and the stranded repair's bound: `ev/head_vs_repair.txt`.
- CI: `merge_train.py classify a8d19cf1950250e378b3cf0dfd4f8c5c29e01255 --pr 3255` gave rc 2, "the check runs at a8d19cf19502 could not be read". There is no `gh` in this cloud seat (`ev/classify.txt`). I read the check runs instead through MCP, over both pages: 120 runs.
  - The only non-green is `governance / instrument-self-tests` 128230551793, cancelled at 21:54:20 -> 22:24:35Z, the 30-minute timeout. That is the owner's standing line (cure R10-PROCESS-SLIM, #3245), and the body answers it.
  - Every `gate` run succeeded, including the latest, 128232646122 (00:16:29 -> 00:17:02Z). There is no edit-run deferral red, and that race is settled green.
  - `pr-contract / pr-contract` 128231701668 succeeded.
  - So CI is not the block; Block 1 is content.
- Merge with main: `git merge-tree --write-tree origin/main <head>` against origin/main 80016a71f567, rc 0, tree 893cf3207402 (`ev/merge-tree.txt`).
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`, rc 0 (`ev/rules_sync.txt`).
- `node tools/policy/policy_lint.mjs --budgets`: `.claude/rules/ci-autofix.md` reads 88 / 96 lines and 1450 / 1469 tokens, rc 0 (`ev/budgets.txt`). Round 3 showed that the approved clause fits at 1469 / 1469.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
- Untouched: the three-dot diff over `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files and every `*_budgets.json` is empty (`ev/untouched.txt`). There is no budget raise.
- There is no closing keyword in the body. The `Disposes` lines are the roster `issues` less #3156, which is unchanged from round 3.
- Not re-run: the mutation suites and the `--stats` figures. The code is byte-identical to the head round 3 measured, so its measurements stand (`verdict/3255` at 68a200f53).
