Fix review: merge 53e4dd425b49f84897317f784e99355eb43f8342

bus-nonce: c7192a5043e5cba022a9afa2f4038d36

Round 1. Measured at head 53e4dd425b49f84897317f784e99355eb43f8342 (authored code head 37f800f9; the head adds only the delivery row).

## Findings

- Killing r10_merge_subject_mutants.py mid-run (SIGTERM) restores tools/policy/agreement.mjs but leaves the untracked scratch directory .agreement-git-* that agreement.mjs creates in the repo root (mkdtempSync at tools/policy/agreement.mjs:868). The guard's scratch= option is not used there, so the stray directory shows in git status after a kill. It does not affect the next run, since only tracked paths are compared. Carry: dismissed: untracked scratch of the mutated tool, not a tracked file left mutated; the defect this PR closes is the tracked-file leftover

## Evidence

- RESULT mutant_guard.py --self-test: 6 of 6 ok at the head (ev/ in this commit).
- RESULT kill-left-mutant, finder's harness r10_flow_dispatch_mutants.py, SIGTERM once cloud_dispatch.py differs from HEAD. At origin/main the file stays mutated (reproduces the defect). At the head it is restored to HEAD's sha256, rc 143, and the harness prints "mutant_guard: signal 15, restored" (ev/kill-head.txt).
- RESULT null: at the head, flow_dispatch M0 prints null-ok, rc 0 (ev/null.txt). A clean tree is not refused.
- RESULT staged edit: with a staged edit to cloud_dispatch.py the harness refuses rc 2 naming the file (ev/staged.txt). The guard compares against the HEAD blob, so staged edits are caught.
- RESULT my own mutants of mutant_guard.py: with "if dirty:" changed to "if False:", the self-test goes red on the planted-leftover refusal and "the refusal leaves the planted file as found". With the handler install removed, it goes red on the on-exit restore and on the SIGTERM and SIGINT checks. Restored; the self-test passes again (ev/mut-dirty.txt, ev/mut-handler.txt).
- RESULT spot-checks, adopted harnesses killed mid-run with SIGTERM: train_overlap_grade_p2 left 4 _mutant_*.py scratch copies mid-run and 0 after the kill, rc 143. merge_subject and carry_parser exit rc 143 with no tracked file modified (ev/spot.txt, ev/overlap-kill.txt).
- Class enumeration: 25 mutant harness entries, of which 12 are adopted. The in-place writers not adopted are exactly the body's dispositions. The five Python ones (ci_layout_p0, cloud_setup, gh_read_retry, heat_meter, nightly_pyspy_retry) write only in temp trees (mkdtemp / TemporaryDirectory). The five shell harnesses are dismissed carry in the body. r10_mutant_skip is a directory. No missed in-place writer.
- git merge-tree --write-tree origin/main HEAD: exit 0, only "LEDGER-MERGE: resolved tests/closures.json".
- The three-dot diff touches no claim file, golden, VERSION, manifest or notes heading. tests/closures.json gains one inert entry for mutant_guard.py. The delivery row dev/programme/delivery/3060.md is present.
- python3 tests/structure.py: STRUCTURE RATCHET PASSED. The body's red-checks section says none, and the packet's gate digest shows no red check.
- merge_train.py classify 53e4dd425b49f84897317f784e99355eb43f8342: GREEN, pending none, red none (ev/classify.txt). The packet shows figure_lint 4 resolved, 0 not verified.
- tests/harness_headers.py needs the homeassistant stub path in this seat. I ran it with PYTHONPATH=tests/hastub:tests:custom_components and it did not finish within my window, so I do not report it as run. It is covered by CI (tests / fast and the gate are green).
- The scoped-gate MODE line was not re-derived here; I cite CI's gate result (green) as the evidence.
- No finder's harness is named by the PR. I used the finder's r10_flow_dispatch_mutants.py for the kill reproduction and built the mutants of the guard myself; they are disclosed as mine above.
