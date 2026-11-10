Fix review: blocked f0b7564596d2725f87090f921e0d3ceb51ceec8b root-cause-detectable: tests / fast (3.14) is red on this PR's own new harness (harness_headers: its inlined repo_root drops the canonical helper's `from pathlib import Path`) and ## Red checks says none; PYTHONPATH=tests/hastub python3 tests/harness_headers.py shows it locally

bus-nonce: 30df47c3b32489a3d0981e3a26c58093

## Summary

Round 1 (no earlier `Fix review:` on #3401). I measured head f0b7564596d2725f87090f921e0d3ceb51ceec8b, the head the PR body names, in a detached worktree; the head was re-read before return and is unchanged. The fix itself survives my attack. All five null controls the brief names still PARK at the pre-flight and in the real path. My differential harness finds no pre-flight PASS that the real gate refuses, except under an unchecked precondition carried below. The block is CI: a required check is red because of a file this PR adds, and the body does not answer it.

## Block

- `tests / fast (3.14)` concluded `failure` at this head (job 129597668418, run 42743953498): `1 of 112 HARNESS HEADER CHECKS FAILED`, `>>> FAILED: python3 tests/harness_headers.py`. It is in `merge_train.py owed-reds` (`ev/owed_reds.txt`). It is not inherited: main's CI at the merge base b0762725 (run 42741176573) has one failed job, `governance / instrument-self-tests`, and its `tests / fast` passed.
- Reproduced locally at this head: `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` gives `FAIL every inlined walk matches the canonical helper and no depth root remains  [FAIL python copies=174 differ=['dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py']`, then `1 of 112 HARNESS HEADER CHECKS FAILED`, rc 1 (`ev/harness_headers_local.txt`).
- Cause: the new harness's inlined `repo_root` lacks the canonical `tools/audit/repo_root.py` body's line `    from pathlib import Path` (`ev/repo_root_diff.txt`: `3d2 <     from pathlib import Path`). Fix: copy the canonical function verbatim. That is a harness-only change, so the fix's code and its proofs stand.
- Unanswered: `pr-contract / pr-contract` (job 129613603373) started at 03:38:44Z, after `fast` concluded red at 03:12:47Z. Its output was `ERROR   [pr-body] /tmp/pr-body.md: check `tests / fast (3.14)` is red and `## Red checks` does not name it` and `PR-BODY: 1 error(s)`. `gate` is red on both rollups (jobs 129614067930 and 129614060688) only through these two checks. merge_train classify gives `RED f0b7564596d2725f87090f921e0d3ceb51ceec8b pending: none red: gate`, rc 1 (`ev/classify.txt`).
- Cheaper detector: `tests/harness_headers.py` is `run_always` and ran in 188 s in CI's fast lane (`wall clock` block). Run locally before the handoff, it shows this red, against the fast lane's roughly 13 minutes. The body's own `ci_predict --apply-inert` predicted no fast red, so the predictor missed it (see Findings).

## Findings

- Follow-up: `python3 tools/pr/ci_predict.py --apply-inert` printed `CI PREDICT: no closures, fast, governance or instrument red predicted` for this branch, beside `APPLIED inert_reads tests/harness_headers.py: dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py`. It added the new harness to `harness_headers`' inert reads but did not run that `run_always` script's canonical-helper check, which is red at this head. So a new harness whose inlined `repo_root` drifts gets a clean prediction. Control: predicting on this head (or on any harness whose `repo_root` lacks `from pathlib import Path`) must predict the fast red. Carry: R10-FLY-CIPREDICT-RESTORING
- Follow-up: the pre-flight's simulated review (`policy_admits`, merge_train.py:2457) is built with the owner's pinned identity, and nothing checks that the train's ambient `gh` account is that owner. `_post_agent_approval` (merge_train.py:2381) posts with whatever account `gh` is logged in as, and no `gh api user` read happens anywhere in the train. Under a non-owner account, world A17 in `ev/reviewer_differential_a17.txt` gives `preflight=PASS real=PARK posted=1  <-- SLIP`. Before this diff that head parked at the pre-flight before anything was posted. Now it is admitted, a stray approval is posted, and `land`'s `policy_gate` then refuses it, so the merge still fails closed. A cheap barrier already exists: `ci_probe.py:154-161` `owner_check` refuses when `GET /user` is not tvofi. Applying it once per train run, before `policy_approve` or `policy_admits` runs, would close this. Control: world A17 must PARK at the pre-flight. Carry: R10-TRAIN-MERGE-LOOP-2
- Follow-up (pre-existing, outside this diff): the real path posts the mandated owner-account approval even when the owner's own latest decisive review is CHANGES_REQUESTED. Worlds N5 and A1 give `real=PARK posted=1`: `policy_approval_due` does not consult `approval()`'s CHANGES_REQUESTED rule. The train still refuses at `policy_gate`. But GitHub now reads the owner account's latest review as APPROVED, so the PR's GitHub-side code-owner state no longer shows the owner's request for changes. This diff's pre-flight posts nothing in those worlds (`posted=0` in pre-flight runs; check "... and the pre-flight posts nothing"). Control: worlds N5 and A1 must give `posted=0` in the real path. Carry: R10-TRAIN-MERGE-LOOP-2
- Out of scope: the body's class-rule figure says `git grep -n "policy_gate(\|\.policy_admits(" -- tools .github` gives "4 lines at e414ab71". At both e414ab71 and f0b75645 the enumerator prints 5 (`ev/class_rule.txt`). The fifth line is `policy_gate`'s own `def` (merge_train.py:2049), not a caller. The body's four dispositions cover every call site, so the class is closed and only the stated count is wrong. Carry: dismissed: a miscounted figure with a complete disposition set; nothing downstream reads the count

## Evidence

- Null controls. Command: a reviewer copy of the pre-flight self-test (`ev/reviewer_harness_README.txt`), `python3 tools/audit/seat/_rev3401_pf.py --self-test` at f0b75645. Output in `ev/reviewer_differential.txt`:
  - `SCEN N1 no --mandate: preflight=PARK(policy) real=PARK posted=0`, why `no decisive review by tvofi (id 70032254)`
  - `SCEN N2 revoked mandate: preflight=PARK(policy) real=PARK posted=0`, why `... the train posts no approval under its --mandate: mandate 4100000001 was revoked by tvofi's comment 4100000002`
  - `SCEN N3 mandate scope code-owned: preflight=PARK(policy) real=PARK posted=0`, why `... has scope code-owned, which does not cover p[olicy merging]`
  - `SCEN N4 expired mandate: preflight=PARK(policy) real=PARK posted=0`, why `... expired at ...`
  - `SCEN N5 owner CHANGES_REQUESTED at head: preflight=PARK(policy) real=PARK posted=1`, why `tvofi's own latest decisive review is CHANGES_REQUESTED, and a mandated approval does not override it`
- Attacks. Same run, 18 more worlds, all agreeing between the pre-flight and the real path:
  - Owner CR on an older commit: PARK/PARK.
  - Owner CR, then an uncited owner APPROVED on an older commit: PASS/PASS.
  - Uncited owner APPROVED at the head: PARK/PARK, "cites no mandate".
  - Mandate not yet in force, edited, written by a look-alike account, or absent (404): PARK/PARK.
  - A `--mandate` label naming two ids, or no id: PARK/PARK.
  - Reviews unreadable: PARK(approve)/PARK.
  - A budget file beside the policy: PARK/PARK.
  - Look-alike-account CR: PASS/PASS. Owner DISMISSED: PASS/PASS. Look-alike revocation: PASS/PASS.
  - Owner CR, then a mandated agent approval at the head: PARK/PARK.
  - Positive arms, a live mandate and a programme-end window: PASS/PASS.
  - Result: `ok   REVIEWER: no world where the pre-flight PASSes and the real path parks (0 slips)`, `queue_pre_flight self-test: 54 checks, 0 failed`. A4 is not relied on (fixture limit in the README).
- Mutation proof: `python3 dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py` at f0b75645 gives `8 mutant(s), 0 not as required`, rc 0 (`ev/mutants.txt`). The tree was clean afterwards and the throwaway copy was deleted (`git status --porcelain` empty).
- `python3 tools/audit/seat/queue_pre_flight.py --self-test` at f0b75645 gives `queue_pre_flight self-test: 53 checks, 0 failed`, rc 0 (`ev/pf_selftest.txt`). This matches the body's figure, which was taken at e414ab71.
- `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
- Not re-run: the body's `merge_train.py --self-test` 608 checks, `entities.py` 1-of-2706 and `ci_predict` figures. These are CI's heavy runs (fix-review step 11), and CI's verdict at this head is cited below.
- Head: f0b7564596d2725f87090f921e0d3ceb51ceec8b is the head the body's `## Head` names. Since e414ab71 the only commits are a main merge and `dev/programme/delivery/3401.md`.
- Merge: `git merge-tree --write-tree origin/main f0b75645...` printed `272565d1...` with rc 0, a clean merge (`ev/merge_tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched in the three-dot diff from b0762725. No claim file moved, and no solver code changed, so `env_drift` has nothing to compare.
- Roles: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Owed reds: `merge_train.py owed-reds` (`ev/owed_reds.txt`) lists the required set. The body's `## Red checks: none`.
- Class: the body's enumeration rule returns the land, batch, `policy_admits` and queue_pre_flight call sites. All are dispositioned, and no seam lies outside the diff.
- Forward-carry: the body has none, and this PR creates no later-stage constraint. The two follow-ups above are routed by their own `Carry:`.
- CI: settled RED at this head, per the Block. Every other context in `owed-reds` that ran at this head concluded success or skipped.
