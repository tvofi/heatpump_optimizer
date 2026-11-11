Fix review: blocked 3861ae76214c26900658bfa52c91d880fe8865a1 root-cause-unanswered: tests / fast (3.14) is red at this head and ## Red checks does not name it; pr-contract / pr-contract is red refusing that silence

bus-nonce: 495aac398e8c2c665d9afc11058e90b6

Round 2, a delta review of PR 3431 (R10-SUITE-ENV-RESIDUE) at head 3861ae76214c26900658bfa52c91d880fe8865a1. Round 1 blocked d710f5ddf91ae498d6d8a8193fc62c04e4b01f24 as mutation-vacuous on M1a. `review_carry.py d710f5dd 3861ae76` prints FRESH-REVIEW.

The PR's own delta, from comparing the three-dot diffs at both heads:
- `tests/harness_headers.py`: the decoy now holds `tests/profiles.py`, and checks P2 and P3 are new.
- `tests/arch_score.py`: Carry 6, `RUNNER_TEMP` is now merged last.

The rest of `git diff d710f5dd 3861ae76` is main, merged cleanly by 628e9d3058. No `custom_components/` change belongs to this PR, so nothing widens the review (step 12).

## Block

- `tests / fast (3.14)` (check run 130474184553) concluded `failure` at this head at 11:05:07Z. It is in `merge_train.py owed-reds` (`ev/owed-reds.txt`).
  - The body's `## Red checks` names only the policy_lint budgets and `tests/arch_score.py`.
  - `pr-contract / pr-contract` (run 130491674136) started at 11:26:31Z, after that red concluded. It is red with: `ERROR [pr-body] /tmp/pr-body.md: check `tests / fast (3.14)` is red and `## Red checks` does not name it` (`ev/job-130491674136.log`).
  - `merge_train.py classify` reads `RED ... red: gate` (`ev/classify-1.log`, `ev/classify-2.log`).
- The red is main's, not this diff's:
  - The one failing check is `features.py`'s `combi_type_branch census` (`1 of 5237 FEATURE CHECKS FAILED`, `ev/job-130474184553.log`).
  - Its vendor hits are const.py:812 and :1595, heat_curve.py:72, pump_arbiter.py:256 and :1015, and thermal_model.py:1870.
  - The three-dot diff touches none of those files and nothing under `custom_components/` (`ev/untouched.txt`). This matches the dispatch's note that main has been red on this census since #3398.
- Re-read at 12:42Z: a re-run of `tests / fast (3.14)` (130501374703) concluded `success` at 12:37:52Z. The `pr-contract` run that started after it (130527218358, 12:38:52Z) is still red with the same refusal (`ev/job-130527218358.log`). Gate run 130528106302 is red, and classify reads `RED ... red: gate` (`ev/classify-polls.txt`). The earlier red run at this head is still owed its answer.
- Owed: a body-only edit that names `tests / fast (3.14)` in `## Red checks` as inherited from main (the combi census, with its hotfix in flight), and then a fresh `pr-contract` run. The head need not move.
- Everything else at this head checks out (see Evidence). Once the body answers this red and CI is green, the next round is a body-only delta.

## Evidence

- Round-1 survivor M1a is now KILLED. The round-1 block is resolved.
- Mutant driver: `tools/audit/seat/mutant_run.py --in-place`, run in a detached worktree at 3861ae76. Command: `env PYTHONPATH=tests/hastub python3 tests/harness_headers.py`. Spec: `ev/mutants-harness.json`. Output: `ev/mutant_run-harness.log`, rc=0.
  - SURVIVED NULL.
  - KILLED M1a-tests-insert-relative.
  - KILLED M1b-cc-insert-relative.
  - KILLED M1-both-inserts-relative.
  - KILLED M2-translations-relative.
  - KILLED M1a-tests-insert-cwd-abspath. This is my own extra mutant: `os.path.abspath("tests")` is absolute but resolves against the cwd.
  - KILLED M3-harness-at-base.
- M3 is approximated in a single edit. The `_ROOT` definition and both inserts go back to the base form, and the translations line still names `_ROOT`. Its kill is therefore partly a NameError. The faithful parts of the base are M1 and M2, and both are killed separately.
- The first pass ran with the default `--copy-tree`. It printed `KILLED NULL` (rc 3) because the `git archive` copy has no `.git`, the runner fault the body describes (`ev/mutant_run-harness-copytree.log`). The in-place re-run above settles it. `git status` was clean after the run (`ev/wt-status-after.txt`).
- `tests/arch_score.py` at the head, in place, with `RUNNER_TEMP=/opt/hpo/runner-temp` exported: `ALL 280 ARCHITECTURE SCORE CHECKS PASSED`, rc=0. `/opt/hpo/runner-temp/base` is absent afterwards (`ev/arch_score-head.txt`). This matches the body's 280 and its null control.
- Carry 6 mutant A1 (merge order reverted): `mutant_run.py --in-place --timeout 2700`, spec `ev/mutants-archscore-a1.json`, cmd `env PYTHONPATH=tests/hastub python3 tests/arch_score.py`: SURVIVED NULL, KILLED A1-runner-temp-merged-first, rc=0 (`ev/mutant_run-archscore.log`); as the body says, A1 left `/opt/hpo/runner-temp/base` behind (removed after). A first pass at the driver's default timeout printed `KILLED NULL` (rc 3) on a 27-minute command (`ev/mutant_run-archscore-default-timeout.log`); the null survives at 2700 s.
- CI state, read live through the commit's `check-runs` API at about 11:30Z and again at 12:42Z (`ev/checks-final.txt`):
  - red: `tests / fast (3.14)`, `pr-contract / pr-contract` and `gate` (two runs, the latest 130493857741 at 11:29:22Z). `gate` is the aggregate. I did not re-derive its inputs beyond those two.
  - red: `tests / nightly-status`, which is not in `owed-reds`, so it is neither answered nor a block.
  - Nothing was pending.
- Merge with origin/main ee64358be7: `git merge-tree --write-tree` rc=0, no conflict (`ev/merge-tree.txt`).
- Structure ratchet at the head: `STRUCTURE RATCHET PASSED`, rc=0 (`ev/structure.txt`). No `*_budgets.json`, `tests/closures.json`, `VERSION`, manifest, `RELEASE_NOTES.md` or `tests/golden/` path is in the three-dot diff (`ev/untouched.txt`).
- Three-dot diff against merge base a7628041dc: 5 files, +74/-10. They are `dev/programme/delivery/3431.md`, `tests/arch_score.py`, `tests/harness.py`, `tests/harness_headers.py` and `tools/audit/seat/cloud-setup.sh`.
- Delta commits 8933c424f and 7215e37c7 carry no Co-Authored-By, Claude-Session or claude.ai text (`ev/delta-commits.txt`).
- Roles contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the rendered contract is current.
- Finder's harness: none is committed for 6d58568e, as in round 1. P2 now pins the case the round-1 capture showed: `profiles` resolves to the cwd's tree under M1a. I did not re-run the round-1 capture probe; M1a is killed in the closure.
- Figures not re-derived in this round: the scoped-gate line (`MODE: SCOPED -- 21 script(s) run, 12 scoped out`) matches CI's fast log at this head. I did not re-run the gate, per step 11. The seam-enumeration greps for the cwd-capture class and for `**throwaway_git_*` were not re-run; that class was settled in round 1.
- Self-audit: `carry_audit.py check` over the PR body with this verdict as the comment, rc in `ev/carry-audit.txt`.

## Findings

none
