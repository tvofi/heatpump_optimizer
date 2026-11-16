Fix review: merge 842b068dd0ea4b8edb6f3de1c7955380e10ca23c

bus-nonce: 3c3e1fbb01246141808cc8274b237884

Round: fourth. This is a delta review over the reviewed head 43c1c7dbfd7a642a3543c1912469b2ce30f05584. The delta has three commits:
- 6554be71fc merges origin/main 47f0f18a7e (#3646).
- 363f3e7df7 trims the instrument-freeze paragraph of `dev/governance/roles/orchestrator.md`.
- 842b068dd0 merges 363f3e7df7 into the reviewed head.

Nothing under custom_components/ changes, so the review is not widened. The previous verdict's block (orchestrator.md over its files_tokens cap) is resolved: `policy_lint.mjs` now exits 0 and the file reads 4250 against its cap of 4251.

## Findings

- Note: figure: the body is stale in two places since the previous rounds.
  - "P2, the rest" and `## Approval` still name `dev/governance/roles/proposal-triage.md` as changed by this PR, although the own diff no longer touches it (12 files, `ev/own_diff_stat.txt`).
  - The Carry 0-2 paragraph quotes the old freeze wording ("never changes production code, loosens a gate or budget, or skips a review"), but the head now reads "never touches production code, gates, budgets or reviews".
  Carry: R11-PRE-MACHINERY-LIMITER
- Note: figure: commit 363f3e7df7 says "no rule changed", but the trim does more than reword (`ev/orchestrator_delta.txt`):
  - It drops "never built in-round". Deferral is now only implied by "ACCEPTs are built before the next round's finders".
  - It drops "every round" and "you or a seat".
  - It turns "loosens a gate or budget, or skips a review" into "touches ... gates, budgets or reviews". That is a stricter ban on any change to a gate, not only a loosening.
  This is policy text the owner approves in the required review, so it is not a block under C5. The owner should read the paragraph as it now stands, not the commit subject. Carry: R11-PRE-MACHINERY-LIMITER
- Note: figure: orchestrator.md now sits 1 token under its cap (4250/4251). The next merge of main that touches it, or any edit to it, will repeat this round's introduced red. Carry: dismissed: a known headroom state, and policy_lint catches it in seconds as the body's own `## Red checks` names
- Note: instrument: the `gate_raise_only` note from earlier verdicts still stands and was not re-examined here. Carry: dismissed: an instrument defect outside this PR's diff, handed to the orchestrator in an earlier verdict

## Evidence

- Head reviewed: 842b068dd0ea4b8edb6f3de1c7955380e10ca23c (`ev/HEAD.txt`), checked out in a detached worktree. The PR body's `## Head` names it.
- Merge resolutions:
  - `git merge-tree --write-tree 2fa85b69db 47f0f18a7e` gives tree a5ca011a63, equal to 6554be71fc's tree.
  - `git merge-tree --write-tree 43c1c7dbfd 363f3e7df7` gives tree a734e6dfcc, equal to the head's tree.
  - Both merges are pure auto-merges with no hand edit.
  - The delta's `tools/audit/prepare_baseline.sh` and `dev/programme/delivery/3646.md` changes are main's #3646, not this PR's.
- Merge with main: `git merge-tree --write-tree origin/main 842b068dd0` exits 0 (`ev/merge-tree.txt`). origin/main is 47f0f18a7e, already in the head.
- Policy lints:
  - `node tools/policy/policy_lint.mjs` exits 0 with `TOTAL: 0 error(s) across 51 policy file(s)` (`ev/policy_lint_head.txt`).
  - `--budgets` shows the orchestrator.md row at 4250 against its cap of 4251 (`ev/budgets_orchestrator.txt`).
- Self-tests at the head (`ev/selftest_*.txt`):
  - machinery_ratchet: 72 checks, 0 failed;
  - pr_cap: 32 checks, 0 failed;
  - orchestrator_tick: 322 checks, 0 failed.
- Mutants re-applied at the head (`ev/mutants.txt`), each killed:
  - `pr_cap.py:230` with `and v > PRODUCTION_SLOTS` removed: 1 check fails;
  - `machinery_ratchet.py:359` with `max(0, ...)` removed: 1 check fails.
- `machinery_ratchet.py --check --base origin/main --head HEAD --pr 3627` exits 0 (`ev/check.txt`):
  - ok nonproduction_merges 481 <= 478 + band 5;
  - ok churn 13932 <= 14797 + 3636;
  - ok target 481 <= 478 + band 5 (18 merges past anchor).
  The body's "11 merge(s) past anchor" and churn figure 13785 are from earlier heads. The anchor count grows with main, so this is not a defect.
- Untouched by this PR's own diff (`ev/own_diff_stat.txt`): VERSION, the manifest, RELEASE_NOTES.md, tests/golden and custom_components.
- CI: `merge_train.py classify 842b068dd0 --pr 3627` read WAIT from 01:35:59 UTC, then exited 4 at 01:59:08 UTC (`ev/classify.log`):
  `APPROVAL-OWED 842b068dd0ea4b8edb6f3de1c7955380e10ca23c 5 budget raise(s), first dev/governance/config/machinery_target_budgets.json: ... tvofi's approval is on 56fda94e8568, not this head 842b068dd0ea: an approval covers only the commit it was given on`
  I judged the head as GREEN. The only red left is the raise's approval, and that follows this verdict.
- Red checks: the reds from the previous head (policy-docs, env-matrix, instrument-self-tests, fast, graders-head-copy) each carry a `## Red checks` answer in the body. Classify reads none of them red at this head.
