Fix review: merge dcf5e329dceabbf35716800fbacf4e2ff58741bd

bus-nonce: c7bbf515da8d4ecdf04ef52cec5f7cdf

## Scope

Round: a later round (the fourth merge verdict on #3451's line: 4c24160f, 9c5485e3, 4b43164c, now dcf5e329), judged as **its delta** from the reviewed head 4b43164c066faa16b508726512ca0314fb884edd (`fix-review.md` step 12). `review_carry.py 4b43164c dcf5e329` prints `FRESH-REVIEW` (ev/review_carry.txt), so the earlier verdict does not carry. The previous verdict (verdict/3451 at 7c163a48) records no findings, so none are owed resolution. The delta writes nothing under `custom_components/`, so nothing widens the scope. There is no review packet. There is no pull request at this head yet, so there is no CI to read: no required check has run at dcf5e329, step 11 has nothing to answer, and the train re-proves the head when the pull request is open.

## Evidence

- Head: `git ls-remote origin refs/heads/handoff/r10-process-slim-p2` prints dcf5e329dceabbf35716800fbacf4e2ff58741bd, re-read before the push. The body's `## Head` names the same SHA. All checks below ran in a checkout detached at it (ev/HEAD.txt).
- Merge with main: `git merge-tree --write-tree origin/main dcf5e329` exits 0 at origin/main f47250150a33d5f3e8502a50ec056cd821f1408b (ev/merge_tree.txt). It also exits 0 at the earlier origin/main f44e761c19; that run's `LEDGER-MERGE: resolved tests/closures.json` is the closures driver, not a claim file.
- Role contracts current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Own delta, re-derived under the body's rule. For each file in the union of the two own diffs, I compared the sorted `+`/`-` line set of the own diff at 4b43164c (base ef579d9b) with the own diff at dcf5e329 (base a18e2e9d). The union has 44 files and exactly six differ (ev/own_delta_files.txt): the three defect-root-cause.md copies, fix-review.md, tests/gate_lock.py and tools/audit/seat/bus.sh. This matches the body's "44 files ... exactly six".
- tests/gate_lock.py has left the branch's own diff. Main's 80779d2e pins the same normal waiter with `_Env(None)`. a18e2e9d holds no `_Env("0")` (count 0), and the own diff of this file is empty, as the body states.
- bus.sh delta: the self-test's `run()` keeps both sides of the conflict, this branch's `HPO_BUS_PENDING="bash $W/pending"` (C8) and main's `HPO_BUS_GH="${BUS_GH:-bash $W/ghstub}"`. Main's CARRY-LANDED arms are restored as main wrote them.
  - `bash tools/audit/seat/bus.sh --self-test` at the head prints `bus self-test: 186 checks, 0 failed`, rc 0 (ev/bus_selftest_head.log). This matches the body's figure.
- Mutation proof on the merge resolution. Each side was dropped in a throwaway worktree, and each kept side is load-bearing:
  - PENDING stub removed: `186 checks, 6 failed`, rc 1. The failures are the C8 WAIT arms, the null control and P345 (ev/mutant_pending.log).
  - `${BUS_GH:-...}` override reduced to main's old fixed stub: `186 checks, 2 failed`, rc 1. The failures are CARRY-LANDED-OWN-TOPIC and CARRY-LANDED-UNREAD (ev/mutant_gh.log).
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2701 ENTITY CHECKS PASSED`, rc 0, in 7m59s (ev/entities_head.log). Its `FAIL` lines are the script's planted negative controls. Without `PYTHONPATH=tests/hastub` it stops at import (`No module named 'homeassistant'`); this is environment, not this diff.
- Lints at the head:
  - `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
  - `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
  - `policy_lint.mjs --pr-body BODY.md`: `PR-BODY: 0 error(s)`. Its red-history row is a `skip`, because no head SHA was given.
  - `brief_lint.mjs` exits clean.
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `carry_audit.py check --body BODY.md`: `6 routed, 0 unrouted, 0 bad destination(s)`, rc 0.
- Versions and claims: `VERSION`, the manifest, both claim files and `RELEASE_NOTES.md` are byte-identical to the merge base a18e2e9d.
- Required reds: `merge_train.py owed-reds` prints 22 checks, and `nightly-status` is not among them (ev/owed_reds.txt). The new parenthetical in step 11, "set (`nightly-status`)", is therefore true as an example of a red outside the set.
- Policy sentences in the delta, each checked against what a seat must do (ev/policy_delta_own.diff):
  - `fix-review.md`: "(card C5)" and "(card C4)" are shortened to "(C5)" and "(C4)", with the same obligation.
  - Step 11's root-cause `Note:` text is re-wrapped with no change of class or route.
  - Step 12 keeps head-moved as a block ("A head whose own diff moved under you is `blocked <sha> head-moved ...`"). This agrees with main's wording and with the C4 carry clause just above it, so a carried head is not head-moved and a moved own diff is.
  - "Name the SHA you measured in the verdict" becomes "Check the SHA your verdict names". The first-line grammar still forces the measured SHA, so no obligation is lost.
  - `defect-root-cause.md`: the Enforcement opening and the `nightly-status` sentence are re-worded with the same duties: the reviewer is the checker before `merge`, and the orchestrator fixes the lane and dispatches Nightly.
  - Dropping `delivery-status` and "or drain the overdue rows" from main's sentence was already in the reviewed 4b43164c. It is consistent with this branch deleting the `governance / delivery-status` job.
- nudge.md: this PR does not touch `dev/governance/roles/nudge.md`, and none of its own-diff lines present it as binding every orchestrator session.
  - The three references in its own diff are context or citations to nudge.md steps (the CLAUDE.md `orchestrator.md` row "turn `nudge.md`", unchanged from main; the closures.json listing; sweep_template.md step citations).
  - nudge.md's own scope line still reads "This file binds the Cursor orchestrators on grok and qwen. Any other agent uses it as the reference". `orchestrator.md:19` ("The turn is `dev/governance/roles/nudge.md`.") and `sweep_template.md:8` ("binds a Cursor orchestrator and is the reference for any other agent's timer") are byte-identical to origin/main.
- Not re-derived at this head: the body's prepr figures, the tick-loop control (dcf5e329 -> 82af113b in a throwaway clone) and the 39-file shortstat against 0a803330. These are outside this delta and were not re-run here.
