Fix review: blocked 09ed5f73f99a2b9048c18ac7bfb9b7832f3fce02 pin-wrong: R10-LEARNER-DEFAULT coordinator.py:1113-1119 names _learned_zone_temperature not _learning_frozen (6664-6673); R10-IMMERSION-LATCH _accumulate_energy pin 10122-10136 not re-pinned (carve-out is 10201-10214)

bus-nonce: c37c5a6839496c3366563a6c0a7adf9c

Round 1 for this head. Measured head `09ed5f73f99a2b9048c18ac7bfb9b7832f3fce02`; origin/main `bc52ad2af1d0cfe95896119b649fa56e14c74b5b` (also the merge base). Role contract checked current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Block

Commit `e96f70d34` says it re-pins "R10-LEARNER-DEFAULT and R10-IMMERSION-LATCH coordinator.py ranges to origin/main 60cd447a0". coordinator.py is byte-identical at 60cd447a0 and origin/main, so every pin can be checked at main (`ev/coordinator-pins.txt`):

- **R10-LEARNER-DEFAULT, wrong function.** The brief now says "`_learning_frozen` deliberately does not freeze an unconfigured slot (coordinator.py:1113-1119)". At main, lines 1113-1119 are `def _learned_zone_temperature(...)`, which returns `state.room_temperature`. `_learning_frozen` is at 6610, and the unconfigured-slot exemption the sentence describes is lines 6664-6673: the `reading.entity_id` comment and the `if reading is not None and reading.entity_id and not reading.ok` guard. A fixer following this citation would be sent to the wrong function under the wrong name. The fix is to re-pin to `coordinator.py:6664-6673`. If the replay-read site should also be cited, add `_learned_zone_temperature` 1113-1119 as a separate citation under its own name.
- **R10-IMMERSION-LATCH, one range of two left stale.** The `_detect_immersion` re-pin to 8838-8895 is correct: the def is at 8838 and the function ends at 8895. The same brief's second seam, "`_accumulate_energy` (coordinator.py:10122-10136) books as immersion everything the meter drew above the PLAN's ask", was not re-pinned. At main, 10122-10136 are the price, `planned_total` and `_roll_month` set-up. The `immersion_excess = ... (sample.actual_power_kw - planned_total)` carve-out is at 10201-10214. The fix is to re-pin it to `coordinator.py:10201-10214`.

`node tools/policy/brief_lint.mjs` exits 0 at this head, so the linter cannot see either defect: it accepts any range that exists in the tree. This is a hand check the brief asked for.

## Findings

- The PR body's `## Head` section has a stale sentence: "the pull request merges origin/main `c29f3089beff847adbdd0ae3dc739f4a071f5756` into it". The merge commit `17c548a6b` actually merges `bc52ad2af`, which the sentence just before it states correctly. The body's other figures are right. Carry: dismissed: body wording only; correct it in the same re-push that fixes the block.

## Evidence

- Scope: the diff against the merge base touches exactly `dev/programme/delivery/2812.md` (+1) and `dev/programme/rosters/wave-r10-groups.json` (+14 -10). This matches the body's diff-stat (`ev/scope-and-merge.txt`).
- Merge: `git merge-tree --write-tree origin/main 09ed5f73f99a2b9048c18ac7bfb9b7832f3fce02` prints tree `78c3b9827cbd6922fe84d194a5ca51e0c7db59bb` and exits 0. No conflict.
- Blob hashes re-derived: main `d3b890726e4c580732d1d257318efe78730a7b34`, head `c3d331ec4ffe0732c1052a3a540311d9decc59ba`. Both match the body.
- Group diff re-derived with my own script (`ev/fig.py`, built by this seat to the body's stated rule: an object holding both `group` and `resume`). Its output matches the body's line for line: 189/189 groups, none removed or new, 7 changed (`ev/figures.txt`). R10-FLOW-AUTOTRAIN, R10-LEARNER-ETA and R10-MUTANT-SKIP go in-progress->done. R10-FLY-LEDGER-SAMPLE carry goes 0->1 and R10-MERGE-SUBJECT-CASEARM goes 2->3. R10-IMMERSION-LATCH and R10-LEARNER-DEFAULT change only in `brief`. Stage counts: done 117->120, in-progress 10->7, the rest unchanged.
- Roster commits: `origin/main..HEAD` lists dbd592fe4, e96f70d34, 027c38705, eaf10309d and e64be204d, and the body names all five. `origin/main..origin/handoff/audit-r10-roster` lists those five plus four newer commits: 5986d2266, 8eb7b1c1a, ceceee42f and 6852f10b9. The body scopes itself "through e64be204d", so those four belong to the next batch and not to this PR (`ev/roster-commits.txt`).
- Set-done groups: each recorded commit is a merge into main. R10-LEARNER-ETA is 60cd447a0 (#2775), R10-MUTANT-SKIP is 6b5d2a816 (#2749), and R10-FLOW-AUTOTRAIN is 0825aee64 (#2780) (`ev/done-groups.txt`).
- Carry destinations: neither new carry names a done group. The R10-FLY-LEDGER-SAMPLE carry quotes #2712's friction item verbatim, including its original "Carry: R10-FLOW-JIDOKA", which is in-progress. It is homed on FLY-LEDGER-SAMPLE, whose files include `tests/mutation_table.py`. The CASEARM carry is homed on a not-started group.
- Brief lint at head: EXIT 0. Every listed ERROR line comes from the linter's own malformed-fixture self-tests (`CARRY ok: 10 error(s) pin the carry acceptance ...`), and none is on `wave-r10-groups.json` (`ev/brief-lint.txt`).
- VERSION, the manifest and the release notes are untouched: neither file is in the diff. Mutation proof is n/a because the PR changes no production or test code.
- CI on this head when read: `tests / briefs`, `governance / wave-script` and `budget-raise-gate` succeeded; record, kernel-points and delivery-status-publish were skipped. The rest were still queued: closure-scope, policy-docs, nightly-status, mutation, validate-hacs, env-matrix, instrument-self-tests, delivery-status, codeql, arch-score and hassfest. No red check was concluded, so step 11 owes nothing yet.
- Not re-derived: the body's claim that each push passed the roster lint gate. I ran the lint only at this head.
