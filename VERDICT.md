Fix review: merge 2ad28ecb50906877b34a378cacd8085e6afca029

bus-nonce: b204dffed05775f65504c26022ad6e5f

Round 4. I reviewed head `2ad28ecb50906877b34a378cacd8085e6afca029` from a detached worktree at that head. The merge base is `80016a71f567d936450d8708abcbb79d9e8071d7`. Round 3's block (verdict/3255 at 68a200f5, on head a8d19cf1) is cured: the #2429 terminating condition and obligation are back in all three copies, and the two round-3 survivors are now killed. Nothing that survives the repair or comes new from it blocks.

## Policy touch

This PR changes policy. It merges **only on tvofi's approving review at the head 2ad28ecb**, as `main-protect-checks`' code-owner rule requires. That review is the approval of record. The 2026-10-29 citation ("All of these are approved.") resolves only to restatements of an approval; see Findings.

Every changed policy sentence, base -> head, in `dev/governance/rules/ci-autofix.md` and its generated `.claude/rules/ci-autofix.md` and `.cursor/rules/ci-autofix.mdc`:

- Removed: "A failed recording reads files a clean run never does (`linecache`): an UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records." The approval does not cover this removal; the body lists it under `## Approval` with its reason.
- Changed: "When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants` stales the body's `## Red checks` `mutation` line; the reviewer re-checks it." -> "When `mutation-autofix` goes red, run `--pin-killed` yourself. If `mutation-pins` has not concluded by `tests / mutation`'s conclusion, the pin is owed by the handoff and the body says `unmeasured`; `pinned` only if `--pin-killed` ran on this head. A pin stales the body's `## Red checks` `mutation` line; the reviewer re-checks it."
- `tools/policy/policy_lint.mjs` filing map, which decides what the cron files:
  - a derived `other (untaught)` verdict family (#2436);
  - a declared `root-cause` family over `root-cause-unanswered`, `root-cause-detectable` and `root-cause-unrecorded` (#2437);
  - three new `mutation` members: `mutation-unpinned`, `unpinned-site` and `mutation-survivors`. The approval does not cover these three, and the body says so.

#2429 against the approved text, line by line. The approved text is `R10-RCA-FRICTION-RESIDUE.md` section 7 on main; the roster brief carries the same words.

| | approved | head |
|---|---|---|
| bound | "if `mutation-pins` has not concluded by **the next `tests / mutation` conclusion**, the pin is owed by the handoff and the body says `unmeasured`" | "If `mutation-pins` has not concluded by **`tests / mutation`'s conclusion**, the pin is owed by the handoff and the body says `unmeasured`;" |
| claim | "a body says `pinned` only when `--pin-killed` ran on this head" | "`pinned` only if `--pin-killed` ran on this head." |

The terminating condition, the obligation and the measured-claim rule are all present. The only drop is the word "next". The body's `## Approval` discloses this: "the bound as the reviewer quoted it from the draft (record section 7 words it 'the next `tests / mutation` conclusion')". The round-3 cure quoted the clause without "next". With "next" the file reads 1470 / 1469 tokens and `policy_lint` fails, rc 1 (mutant B4). So round 3's "it fits exactly" held only for its own quotation.

## Findings

- The #2429 sentence is not word-for-word the approved draft: it drops "next", and the compressed `pinned` clause drops "a body says". The body still calls it "landed verbatim" (`## Approval` heading, Carry 3). The `## Approval` bullet discloses the difference, and the bound's meaning is unchanged: on a given head, `tests / mutation`'s conclusion is the next one. The approved wording would exceed the 1469 cap by 1 token. Carry: dismissed: disclosed in the body and identical in meaning; tvofi's approving review at the head rules on the wording.
- A coordinated edit to the restored bound, regenerated into all three copies, passes every in-tree check (mutants B2 and B3 survive: rules_sync rc 0, budgets rc 0, policy_lint rc 0). An edit to one copy only is killed (B1, rules_sync rc 1), and so is growth past the cap (B4). Only the code-owner review guards policy prose. Carry: dismissed: policy prose has no mechanical pin by design, and the required owner review at the head is the guard.
- The approval citation ("All of these are approved.", 2026-10-29) still resolves only to restatements posted from the tvofi account (round-3 verdict, `ev/approval.txt` there). No primary owner statement was found. Carry: dismissed: tvofi's approving review at the head is required and is the approval of record.
- #3156 (`ci-red`) is still in the roster group's `issues` and is not disposed. The body and `R10-RCA-FRICTION-SWEEP.md` section 4b say so, and the orchestrator owes the re-route before wiring `fixes`. Carry: #3156
- The body is stale in two places. `## Head` prints a bare `9ca25bb8dedb81fffc74b65c176e5a07aa9b01c7`, which is the head's second parent. `## Red checks` says "no check run exists for `9ca25bb8…` yet". In fact all 68 check runs of head 2ad28ecb have concluded, with no failure or cancel. Carry: dismissed: cosmetic; this verdict reads the head's checks directly.

## Evidence

- HEAD reviewed: `2ad28ecb50906877b34a378cacd8085e6afca029` (`ev/HEAD.txt`), the PR head at the time of reading. The review packet is in `ev/review-packet.md`: Refusals none, CARRY-AUDIT 5 routed / 0 unrouted, FIGURES 5 resolved.
- CI: `merge_train.py classify 2ad28ecb… --pr 3255` gave `GREEN … pending: none red: none`, rc 0, on the first run (`ev/classify.txt`).
- Check runs: 68 in all, on one page (`ev/check_runs.txt`), and none failed or was cancelled.
  - `governance / instrument-self-tests` 128248097717 succeeded in 29m54s, inside the 30-minute timeout, so the standing timeout line is not triggered on this head.
  - All three `gate` runs succeeded (128257274132, 128257498742, 128257742496), so there is no mutual-deferral red.
  - `pr-contract / pr-contract` 128257095312 succeeded.
- Merge with main: `git merge-tree --write-tree origin/main 2ad28ecb…` rc 0, tree `73b80812516d` (`ev/merge-tree.txt`).
- Null controls at the clean head:
  - `rules_sync.mjs --check` RULES-SYNC ok, rc 0;
  - `--budgets` `.claude/rules/ci-autofix.md 88 96 1469 1469`, rc 0;
  - `policy_lint.mjs --self-test` `FIXTURE ok: 93 error(s) hold 269 pins`, rc 0;
  - `ci_predict.py --self-test` 0 failed, rc 0;
  - `tests/structure.py` STRUCTURE RATCHET PASSED.
  - Output is in `ev/rules_sync.txt`, `ev/budgets.txt`, `ev/selftest.txt`, `ev/ci_predict_selftest.txt` and `ev/structure.txt`.
- The round-3 survivors are now killed (`ev/mutants.txt`):
  - M1, `kind === 'verdict family' ? derivedInput(blocks, passing) : null` -> `derivedInput(blocks, passing)` (policy_lint.mjs:3205), fails the self-test, rc 1, with "3 untaught friction ids -> 1 friction-family would-open(s), want none".
  - M2, `(quoted | {rel}) & changed` -> `quoted & changed` (ci_predict.py:527), gives "FAIL a diff touching only the driver runs it", 1 failed.
  - Both pins arrive in a9d4bf12b (`ev/repair3.diff`).
- Mutants of the restored bound (`ev/bound_mutants.txt`); the null control N0 passes all three checks:
  - B1, the terminating condition cut in the canonical copy only: KILLED by rules_sync, rc 1.
  - B2, the terminating condition cut and regenerated (1460 / 1469): survives. See Findings.
  - B3, the obligation cut and regenerated (1461 / 1469): survives. See Findings.
  - B4, the approved "the next" wording restored and regenerated: KILLED by policy_lint, rc 1, at 1470 / 1469.
- Untouched: the three-dot diff from the merge base over `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files, every `*_budgets.json` and `tests/closures.json` is empty (`ev/untouched.txt`). There is no budget raise and nothing claimed.
- Body: it has no closing keyword. The `Disposes` lines are #2875, #2950, #2998, #2436, #2437, #2429, #2840, #2835, #2895, #2907 and #2860, which are the roster `issues` less #3156. The body states #3156's disposition.
- Not re-derived this round: the `--stats --since v7.0.4` record figures and the driver timings. The repair changed no counting code or record figure; round 1 re-derived them (verdict/3255 at 318fa443).
