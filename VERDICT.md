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
