Fix review: blocked d538f2daff18ad39520b75eab718044da461b9c6 carry-missing: not carried to R10-FLY-TRAIN-DEFAULTS PART 2, the body has no Carry: marker for the folded R10-FLOW-POSTMERGE carry

bus-nonce: 4df60ace6c3c1094b3da834875819640

## Round

Round 1. Measured head d538f2daff18ad39520b75eab718044da461b9c6, the head the PR body names (`## Head`). It was still the head when this verdict was written. Merge base 4d2f32b2e. origin/main is a9ba3022e.

## Block

The brief, under mandate 6329234399, accepts the orchestrator's disposition: the folded R10-FLOW-POSTMERGE carry (after-merge bookkeeping in merge_pr.sh and merge_train.py) is owed by R10-FLY-TRAIN-DEFAULTS PART 2. It asks the reviewer to check only one thing: that the body routes that carry with a `Carry:` marker to R10-FLY-TRAIN-DEFAULTS. The body does not:
- Its "Roster carry" paragraph says "Carry 1: **not done in this pull request**".
- It leaves the routing open ("The orchestrator either re-dispatches the folded brief onto this branch or splits R10-FLOW-POSTMERGE back out").
- `## Forward-carry` reads `none`.
- No `Carry: R10-FLY-TRAIN-DEFAULTS ...` line appears anywhere in the body, and the packet's carry_audit counts 0 items.

To repair it, edit the body only: add a `Carry: R10-FLY-TRAIN-DEFAULTS` marker (PART 2) for the R10-FLOW-POSTMERGE after-merge bookkeeping, and name it under `## Forward-carry`. The code needs no change. The P269 change itself held under every attack below.

## Findings

- Survivor T4 (reviewer's own mutant): train.sh's `--no-mandate` branch (`mandate=""`) can be replaced by a no-op and the self-test stays green. Arm 8c tests `--no-mandate` only beside a mandate file. In that case the file branch is skipped anyway, so the assignment is never exercised. The behavior is wrong only when both `--mandate ID` and `--no-mandate` are given. The mutant would then pass `--mandate ID` to the child while the launch line prints `mandate: none (owner reviews only)`. A one-line arm (`--mandate 7 --no-mandate` passes no `--mandate`) pins it. Carry: R10-FLY-TRAIN-DEFAULTS
- Approval for the merge: `dev/governance/roles/standing-merge.md` is policy, and `merge_train.py` and `train.sh` are code-owned, so tvofi's approving review is owed at merge. This is flagged and not blocked, per the brief. Carry: dismissed: the owner's review at merge is the code-owner rule, not a defect

## Evidence

- RESULT train.sh --self-test at head: ok, rc=0. The effective set of a bare launch is `--overlap|--approval-carry|--skip-bad|--free-holders|--bot-prs|--pre-flight` (ev/train_selftest.txt).
- RESULT merge_train.py --self-test at head: 381 checks, 0 failed (ev/merge_train_selftest.txt). This matches the body's figure.
- RESULT the body's mutation proof reproduces. With `"--pre-flight"` dropped from RECOMMENDED, train.sh's self-test refuses with "an explicit --skip-bad/--overlap launch is not the recommended set", and merge_train's self-test fails "RECOMMENDED is the owner's six" (ev/reviewer_mutants.txt, T9).
- RESULT each `--no-<flag>` removes exactly its own flag. All six were run against a stub python3 that records argv (ev/head_controls.txt). The old `--<flag>` spellings, all six given together, produce an argv identical to a bare launch's.
- RESULT null control: a head launch with all six `--no-<flag>` plus `--no-mandate` gives the child argv `... batch Q --repo x/r --state-dir S --min-runs 1`. The base 4d2f32b2e's bare (all-off) launch gives the same argv (ev/head_controls.txt, ev/base_null.txt).
- RESULT mandate source order:
  - `--mandate 9` beats a file holding 55.
  - The file alone passes `--mandate 4242` and prints `mandate: 4242 (from <state>/mandate)` (self-test arm 8c).
  - `--no-mandate` beside a file passes none.
  - With no file: `mandate: none (owner reviews only)`.
  - The digits-only refusal fires on a bad file: `12x` gives rc=2 with "must hold one comment id (digits), got '12x'". An empty file also gives rc=2.
  - An explicit `--mandate abc` is not digit-checked. That is unchanged from base, and the brief scoped the check to the file. Evidence only.
- RESULT reviewer mutants on train.sh and merge_train.py (ev/reviewer_mutants.txt), 11 run:
  - Killed: T1 (`--no-*` ignored), T2 (digit check dropped), T3 (file never read), T5 (file before `--mandate`), T7 (the `set:` launch line dropped), T8 (set_flags not passed), T9, T10 (`auto_train_argv` re-adds the flags), T11 (`--no-*` not subtracted).
  - Equivalent: T6 (writes an unused variable).
  - Survived: T4, listed under Findings.
- RESULT harness dev/audit/harnesses/r10_flow_autotrain_mutants.sh at head: M0 baseline green (merge_train 381/0, tick_loop 17/0, bus 110/0). S1–S7 (the sweep and RECOMMENDED mutants this diff re-points) are all killed, with 3, 1, 1, 2, 1, 3 and 13 checks failing (ev/mutants_S_head.txt). The full run was stopped once the block was settled, after 14 of 43 mutants (A1–A12, V1, V2), all killed (ev/mutants_head_partial.txt). The remaining 22 are untouched by this diff and were not re-run.
- RESULT selftest_wiring.py --check at head: 103 self-testing, 103 wired, 0 unwired, 0 index gaps. governance.yml runs `merge_train.py --self-test` (line 888) and `train.sh --self-test` (line 908) (ev/selftest_wiring.txt).
- RESULT `git merge-tree --write-tree origin/main(a9ba3022e) d538f2daf` exits 0 with tree 8c01f44af: no conflict (ev/merge_tree.txt).
- RESULT CI on the head, from the check-runs API (43 runs): no run concluded red. Still in progress when read: prelude (run 41117997987), governance / instrument-self-tests, tests / graders-head-copy, codeql / Analyze (python). The body's one red, policy-docs at an earlier tree, is answered in `## Red checks` with the cheaper detector, policy_lint.mjs --budgets. That check is green at this head.
- VERSION, the manifest and the RELEASE_NOTES heading: the three-dot diff touches none of them (6 files, listed in the packet).
- The class: the body states one seam (where the flag set is defined). The brief's three homes are now one: standing-merge.md names RECOMMENDED by reference, AUTO_TRAIN_FLAGS is gone (grep finds it only in the roster and triage text), and train.sh reads the line. The body names sweep_render.py and sweep_template.md as still rendering an explicit flag list. I did not open them, so this is evidence only, as the body discloses.
- No finder's harness is named. P269 is an owner-directed change, not a measured finding. The controls are the roster brief's item (6), and every one was re-run above.
