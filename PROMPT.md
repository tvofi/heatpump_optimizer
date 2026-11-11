CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-relay-arm-order, at head ee64358be7eeccaec5178a923cb3b83a18a924a0. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch ee64358be7eeccaec5178a923cb3b83a18a924a0 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-relay-arm-order before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-relay-arm-order, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-relay-arm-order, even with no code. Then push the code to refs/heads/handoff/r10-relay-arm-order, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-relay-arm-order <body.md>`, which pushes refs/heads/handoff-body/r10-relay-arm-order; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-relay-arm-order`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-relay-arm-order and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-relay-arm-order and refs/heads/handoff-wip/r10-relay-arm-order-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
REPAIR fixer for R10-RELAY-ARM-ORDER (PR 3465, topic r10-relay-arm-order, branch fix/r10-relay-arm-order), round 2. The handoff review BLOCKED handoff tip 332f882cf8e9ba5c0415df400d89dda1682babf1; the PR head is 76e9852fad (no code since: a delivery row and an origin/main merge).
Scope: kill mutants m2 and m3 named in the verdict (the listing reuse); the P603 carry is now on R10-SEAT-IDENTITY-P5, cite it there (do not re-route it to R10-REVIEW-DISPATCH-RESIDUE).
Verdict first line, verbatim: Fix review: blocked 332f882cf8e9ba5c0415df400d89dda1682babf1 carry-missing: P603 OPENER-LIVE-TIP re-routed to R10-REVIEW-DISPATCH-RESIDUE without its control
Full text verbatim follows (also: git fetch origin verdict/3465; git show origin/verdict/3465:VERDICT.md).
----
Fix review: blocked 332f882cf8e9ba5c0415df400d89dda1682babf1 carry-missing: P603 OPENER-LIVE-TIP re-routed to R10-REVIEW-DISPATCH-RESIDUE without its control

bus-nonce: cd1b04434e82dad0afc7b24eb33c9f6a

Round 1 (handoff review, no pull request yet). Measured head 332f882cf8e9ba5c0415df400d89dda1682babf1, base cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf, from a detached worktree at the handoff tip.

## Block

- carry-missing. The roster assigns P603 OPENER-LIVE-TIP to this group as its carry 0 (`origin/handoff/audit-r10-roster` at caad4cfe5422d123bddd539ac28922aff536a127, group R10-RELAY-ARM-ORDER). Triage `s6-batch183.md#P603` accepted it onto this group, which is not-started and carry_receivable, because it is the same incident. The dispatch brief also covers "its continuation for carry P603". The body builds none of it. Instead it re-routes the carry to R10-REVIEW-DISPATCH-RESIDUE, and the relay folded that as that group's carry 27 (roster commit 8cb4ab1c5). Three problems with that:
  - the destination is the group this group's own brief names as "excluded as a destination";
  - its `files` do not list `tools/audit/seat/open_driver.py`;
  - the folded text drops the control: no self-test (board line at A, live clean tip B opens at B), no mutation proof (restoring the skip fails it), no null control (handoff ref gone still prints SKIP moved), and no measurement (18 SKIP moved lines).

  `finding-propagation.md` requires a carry to keep its control, and `fixer.md` allows a group to hand on its own assigned carry only under a pending owner or orchestrator ruling, which the body does not name. The remedy is either of:
  - build OPENER-LIVE-TIP in `open_driver.py` here, with the card's self-test, mutation proof and null control (the card admits the file overlap);
  - name an orchestrator ruling that moves it, with the card's control carried verbatim into a receivable destination that lists `open_driver.py`.
- Surviving mutants on the listing claim the body makes ("`handoff_arm` and `confirm_arm` reuse the listing"; the brief asks that "`handoff_arm` reuses the listing"). Both pass the full self-test at rc 0 (`ev/mutant2.diff`, `ev/mutant3.diff`):
  - m2: delete the `open_prs > "$pst/cloud-prs-open.$$"` line in `pass()`;
  - m3: make `handoff_arm` always list for itself (`if false`).

  No check pins the one-listing hoist or its reuse. Add an arm that counts lister invocations per pass (one under `--confirm`) and fails on each mutant. They ride the same re-cut and are settled in this PR, so they are not carried.

## Evidence

- RESULT head self-test: `bash tools/audit/seat/cloud_relay.sh --self-test` rc 0, no FAIL line (`ev/selftest-head.log`). The body's "420 checks" total was not re-derived: my log keeps only the time and rc tail.
- RESULT mutation proof (named predicate, m1: old order `handoff_arm; carry_fold_arm; probe_arm; confirm_arm`): rc 1, `FAIL a verdict returned before the pass is POSTED before handoff_arm starts` (`ev/mutant1.diff`, `ev/selftest-mutant1.log`). This matches the body.
- RESULT m4 (drop the listing `rm -f` in `pass()`): rc 1, `FAIL the pass leaves no listing file behind`. That cleanup is pinned.
- RESULT m2 and m3: rc 0 (survivors, see Block). The m3 and m4 runs may have overlapped in time (the runner issued them together). Their outcomes are opposite, and each matches its own diff's expectation.
- Null control: the body's controls (a second pass posts nothing more; `handoff_arm` runs once per pass) are arms of the same self-test and are green at the head. The old-order arm is red under m1.
- Finder's harness: the finding (probe-to-POSTED latency, n=45 over 24 h, median 6.8 min) has no committed harness. It is a log measurement in triage s6-batch182, so it was not re-run at either end. The self-test arm is the fixer's instrument.
- Class rule: one seam, the arm order in `pass()`. The body names no enumeration rule, and the issue states one seam.
- Order attack: under the new order, `probe_arm` publishes a verdict before `handoff_arm` takes its `verdict/*` listing, so a merge-verdicted head is no longer updated in the same pass. That is safer than before. `confirm_arm` uses the listing only for PR numbers, so a listing taken before the posts is not stale for it.
- Merge with main: `git merge-tree --write-tree origin/main <head>` rc 0, origin/main ee64358be7eeccaec5178a923cb3b83a18a924a0 (`ev/merge-tree.txt`).
- VERSION, manifest, RELEASE_NOTES and claim files are untouched. The diff is `cloud_relay.sh` and its instrument doc only (`ev/diffstat.txt`).
- `tests/structure.py` at head: STRUCTURE RATCHET PASSED (`ev/structure-head.txt`).
- CI: no pull request exists, so there are no check runs, no review packet and no red to answer. The owed-reds set is in `ev/owed-reds.txt`.
- The body's head line names 332f882cf8e9ba5c0415df400d89dda1682babf1, which is the handoff tip measured here.
----
Task: failing test first for each of m2 (delete the open_prs > "$pst/cloud-prs-open.$$" line in pass()) and m3 (handoff_arm always lists for itself), re-run the mutants through the mutant runner and show each killed, keep a null control. Merge origin/main if it moved (never rebase); every step naming a head re-executes at the new head; tools/pr/prepr.sh rc=0; update the PR through the instruments (update_pr.sh / body_push.sh) and read the refs back with git ls-remote. Mind the zero-headroom structure ratchet. Keep output capped; BLOCKED.md with the exact question if stuck.
