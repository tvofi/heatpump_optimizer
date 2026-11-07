Fix review: merge 0542969c33313f54db611ca0609fade7c1b14989

bus-nonce: 8a39ab9fef186274ec553075b934e33d

Round 3 of this review (round 2 blocked 0ce1f09bd196 at verdict/3264 f201386b). Measured head 0542969c33313f54db611ca0609fade7c1b14989, still the branch head at verdict time, merge base a37c58e5f321. 0ce1f09b is an ancestor; the only authored change since it is afde870be (tools/plan/replan.py, +34/-3); the rest are merges of origin/main. No finder's harness is committed for this instrument group (packet: "Finder's harness: none named"), so the harness is the round-1 and round-2 reviewers' scripts from verdict/3264 (mut.py, mutg.py, m2.py, attackA.py), re-run unchanged, plus my own mutant script, disclosed as mine (ev/mine.py).

## Findings

none

## Evidence

- RESULT round-2 block 1 is closed (part-branch credit). I re-ran round 2's attackA.py unchanged at this head against the live roster (handoff/audit-r10-roster, ev/roster-sha.txt). Over v7.1.0..v7.1.1 it credits 12 production groups, was 8; the 4 added are R10-COP-GATE, R10-COP-PARTLOAD, R10-SAV-COMFORT and R10-UX-HEALTH. Over v7.1.2..v7.1.3 it credits 9, was 8. The head now matches the reviewer's own perturbation exactly, with 0 added and 0 lost in every window (ev/attackA-r3.out). Null control: v7.1.1..v7.1.2 stays at 1, and v7.1.3..v7.1.4 stays at 0. This re-derives the body's figures "12 of 12" and "9 of 9".
- RESULT round-2 block 2 is closed (`## Red checks`). The PR has 68 check runs on one page. Two concluded red at this head: `pr-contract / pr-contract` (latest attempt 128470376626, 16:22Z) and `tests / nightly-status` (128470374844). The body names and answers both, citing the earlier attempts' job ids. It also names the reds of the earlier head, and gate 128436038602 as a deferral. A later `pr-contract / pr-contract` run, 128469857807 in run 42394658094, started at 17:08:44Z, after the last red to conclude, and ended in success: that run is the evidence that the body check passed. nightly-status is not this PR's red: a scout traced it to tests/nightly_status.py:139, which sets DEFAULT_WORKFLOW = "nightly.yml" and so grades nightly.yml only. The diff touches governance.yml and not nightly.yml.
- RESULT round-2 non-blocking findings are settled. The squash fallback is now pinned: squash-longest (`max` -> `min`) is KILLED, where round 2 saw it survive. Item 7 (inflow 0.4 and the slot_sensitivity note) is now dismissed with a reason in the body, no longer carried to the closing group. The edit-run deadlock stays carried on R10-PROCESS-SLIM, as round 2 routed it.
- RESULT mutation proof on afde870be's lines. The fixer's in-table mutants since-tag-part-branch, -part-boundary, -part-longest and -squash-longest are all killed (rc=1) in --self-test (ev/replan-selftest-head.txt). My own mutants (ev/mine.py, ev/r3-own-mutants.txt) are KILLED: part-hit-or-swap (drop the exact-equal arm), part-endswith, part-hit-ignored (back to an exact by_topic.get) and part-sep-underscore. One survivor, part-no-squash-after-topic (skip the subject fallback when a topic parsed but matched nothing), is equivalent on main's merge subjects. "Merge pull request #N from <owner>/<branch>" names no upper-case group, so the fallback never fires for a parsed topic.
- RESULT earlier mutants re-run at this head:
  - round 1's mut.py: 15 of 15 anchored mutants killed (ev/r1-mutants-r3.txt).
  - round 2's m2.py: credit-lane-r2, credit-done-r2, squash-fallback-dropped, squash-longest, since-prod-lane and since-substantive are killed (ev/r2-mutants-r3.txt). merge-topic-lastseg, merge-topic-lower and merge-re-anchor survive. Round 2 judged all three equivalent, and that is unchanged. The other m2.py entries are anchor-ambiguous or no longer anchor; the in-table mutants that cover them are killed in --self-test.
  - round 1's mutg.py: 4 of 4 gantt_drift mutants killed (ev/gantt-mutants-r3.txt).
  - A local stash taken in that worktree during the mut.py run held the post-after-mark mutant; that mutant reported KILLED, and a reverted file cannot produce a false kill.
- RESULT self-tests at this head:
  - replan.py --self-test: "self-test: 0 failed", rc 0.
  - gantt_drift.py --self-test: 45 checks, 0 failed.
  - plan_page.py --self-test: 67 checks, 0 failed.
  - tests/structure.py: STRUCTURE RATCHET PASSED.
  - selftest_wiring --check: 0 index gaps (ev/structure-wiring.txt).
- The body's "gantt_drift kills 16 mutants" is not re-derived. I re-ran only the 4 reviewer mutants and the self-test's 45 checks.
- Diff base...head: 9 files (ev/diff-files.txt). No custom_components, VERSION, manifest or RELEASE_NOTES.md. dev/programme/delivery/3264.md is present, and gantt_drift.py is classified in tests/closures.json. No *_budgets.json changed. `git merge-tree --write-tree origin/main 0542969c` exits 0, and its stderr reports "LEDGER-MERGE: resolved tests/closures.json". The review roles are unchanged between the merge base and main.
- `## Head` is current. 0542969c merges a37c58e5 into 84ef1285, whose parents are ec3b2460 and 28ec0da0. The 84ef1285..0542969c delta is main's content only (tests/closures.json, tools/policy/agreement.mjs).
- Routing is unchanged and was verified in rounds 1 and 2: carries 1 and 7 (brief index) go to R10-BODY-CONTRACT, and 4, 5 and 6 are dismissed as duplicates.
- Observation: v7.1.4..origin/main credits 0 of 3 code-changing merges. Two of them (r10-sav-wood-heat #3244 and r10-ext-3226 #3232) are merges of groups whose topic is on no roster group: no group is named R10-SAV-WOOD-HEAT or R10-EXT-3226, and no resume.branch names those branches. That is roster coverage, not this matcher. Carry: dismissed: evidence, not a finding
- CI: merge_train classify 0542969c --pr 3264 returned rc=0 at 17:39:34Z: "GREEN 0542969c33313f54db611ca0609fade7c1b14989 pending: none red: none" (ev/classify-final.txt).
- Closing self-audit: `carry_audit.py check` over this verdict exits 0 with "1 routed, 0 unrouted" (ev/carry-audit.txt). I passed an empty --body there: the packet's own carry_audit at the head reports the PR body holds 0 finding items. Re-classify immediately before return: GREEN, and the branch head is still 0542969c.
