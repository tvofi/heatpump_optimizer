Fix review: merge 076ec95075c4ebb5b3914402c2854b6ba9e8c729

bus-nonce: 275243050789f0bb47b1fd83a2783e4a
pending-ci: gate

## Summary

Round 1 (no earlier verdict on #3839). Policy PR: `fixer.md` step 8 and "Past three rounds", `fix-review.md` step 6 (axis block), and `bus.sh` `axis_repeat` with five self-test arms. No `custom_components/` line, no budget, VERSION, manifest or notes heading touched. The mutation proof re-runs on Linux and kills every mutant. The instrument has one fail-open edge in how it captures the set (a finding, not a block). Three figures from the RCA do not re-derive at this head (notes, paperwork, C5).

## Findings

- Follow-up: `bus.sh` `axis_repeat` captures `<set>` with the greedy BRE `\(.*\) unenumerated`, so a seam in `(e.g. ...)` that contains the word "unenumerated" pulls part of the seam into the set. Two blocks on one axis then compare unequal and the second block dispatches: a missed refusal (fail-open), never a false refusal. Shown by `ev/greedy-edge.txt`: `[dependency writers unenumerated (e.g. an]` against `[dependency writers]`. Anchoring the capture on ` unenumerated (e.g. ` closes it. Carry: dismissed: a fail-open on free text the reviewer seat writes itself, rare, with the orchestrator reading every block anyway; it does not change what a later stage must do
- Note: figure-unverified: the RCA's "Block 1 to block 6: 51.9 h wall clock, mean 10.4 h" does not re-derive with its stated command (`git log --format='%cI %s' origin/verdict/3729`). The six blocked subjects run from 2026-11-18T16:54:04+01:00 to 2026-11-21T20:48:23+01:00, which is 75.9 h, mean 15.2 h over 5 intervals. Carry: dismissed: paperwork in a done RCA record; the cost test uses the 6.2 h median from R11-RCA-CLASS-OPEN.md, not this figure
- Note: figure-unverified: the RCA's `git grep -nE 'create_task|create_background_task|ensure_future' custom_components/heatpump_optimizer` at 63c6d1cf "returns 16 lines". The same command at 63c6d1cff9a29ec0c99bcbd5e12c229b61e7c184 returns 11 lines (11 at this head too) across 9 files. The qualitative point (the axis is live) stands. Carry: dismissed: paperwork; the count is illustrative and moves no rule
- Note: figure-unverified: "All 1129 `verdict/*` and `archive/verdict/*` refs". `git ls-remote origin` lists 142 such refs now, so I could not re-derive 1129, nor the 108 / 11 / 8 PR counts and 31 blocks / 23 rounds derived from it. The body says itself that the subject classification is the RCA seat's reading. I built no definition of my own. Carry: dismissed: the cost test's inputs are disclosed as an estimate, and the shadow measure over round 12 re-measures the effect

## Evidence

- HEAD: `ev/HEAD.txt`. The body's `## Head` names 076ec95075c4ebb5b3914402c2854b6ba9e8c729 = the head measured.
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty (merge base 4ebd430fbf = origin/main).
- Merge: `git merge-tree --write-tree origin/main 076ec950...` exit 0, tree 63a027d3d68f; no conflict, no claim file touched.
- Step 4: the diff touches no golden, claim file or production code, so `env_drift.py --all` has no drift to compare. Step 5: VERSION, the manifest and the RELEASE_NOTES heading are absent from the three-dot diff.
- Mutation proof (step 1), hand-rolled on five worktrees at the head, `bash tools/audit/seat/bus.sh --self-test` each (`ev/mutants.diff`, `ev/mut1..5.txt`):
  - M1 guard `if false &&` (mut:axisrepeat): KILLED, 1 failed ("a second class-open block on one axis refuses at round two ...").
  - M2 drops the head inequality: KILLED, 2 failed (the different-axes and same-head null controls).
  - M3 drops the set equality: KILLED, 1 failed (the different-axes null control).
  - M4 reads the latest axis block instead of the latest block: KILLED, 1 failed (the later-other-class null control).
  - M5 drops the `--past-three` escape: KILLED, 1 failed ("--past-three dispatches past a repeated axis"). This mutant is not in the body's set; it is my addition.
- Null controls (step 3): at the head (Linux), `bus.sh --self-test` gives `245 checks, 0 failed` on the re-run (`ev/bus-selftest-head-rerun.txt`). The base 4ebd430fbf gives `240 checks, 0 failed` (`ev/bus-selftest-base.txt`). The first head run had 1 failure, "null control: a dead holder's lock is taken over and released (P354)" (`ev/bus-selftest-head.txt`), which is a lock-timing check the diff does not touch; it passed on the re-run. The body's macOS figures (28 failed at both ends) are host-specific and do not reproduce here, where both ends are clean.
- Lints at the head (`ev/lints-head.txt`):
  - `policy_lint.mjs --budgets` rc 0, with `fixer.md 313 315 5215 5216` and `fix-review.md 137 140 2774 2775`, as the body states.
  - `policy_lint.mjs` FIXTURE ok; `rules_sync.mjs --check` RULES-SYNC ok; `brief_lint.mjs` rc 0.
  - `check-wave-script.mjs` `296 passed, 0 failed`; `review_packet.py --self-test` `133 checks, 0 failed`; `fold_ledger.py check` `0 violation(s)`; `tests/structure.py` rc 0.
- Step 14: no budget, closure, INERT, ledger or golden figure moves. The caps were paid by cutting prose. I read each cut against the old text, and none removes a rule:
  - Step 12's "Other deltas never widen it" keeps the production-only widening.
  - `fixer.md` step 8 drops "If no such instrument exists, say so", which the new rule-or-residue clause supersedes and tightens.
- Step 6 / 9: the class is the instrument's input grammar. `axis_repeat` is the one reader of the new subject shape (`grep -n 'class-open: axis' tools/audit/seat/bus.sh` gives one site). `blocked_rounds` and `mechanical_block` read the same `verdict:` subject prefix (bus.sh:647, :676), so the prefix is consistent. The finder's harness is none named (packet); this is an RCA countermeasure, not an audit finding.
- Step 16: no actuator path.
- carry_audit at the head (packet): 1 item routed, 0 unrouted.
- Packet refusal `introduced-red: unreadable` at render (instrument-self-tests in progress); the classify waiter decides, below.
- CI: `merge_train.py classify 076ec950... --pr 3839` polled from 23:11Z to 23:40Z UTC, about every 90 s (`ev/classify.log`). Last line: `WAIT 076ec95075c4ebb5b3914402c2854b6ba9e8c729 pending: gate red: none`, hence `pending-ci: gate`. No red, so no `## Red checks` answer is owed. Owed-reds set: `ev/owed-reds.txt`.
- Head re-read before return (step 12): `refs/pull/3839/head` = 076ec95075c4ebb5b3914402c2854b6ba9e8c729, unchanged.
- carry_audit self-audit: `python3 -I tools/audit/carry_audit.py check --body <body excerpt> --comments <this verdict>` rc 0, `2 routed, 0 unrouted, 0 bad destination(s)`. The body passed as an excerpt (its Forward-carry and Friction sections); the packet's run over the full body at the head is routed 1/1.
