Fix review: blocked 882da1e01b3d209cf7f8b6c02427166e7c0c7655 body-stale: the body's head, figures and mutation proof describe 72cfd904 (350 checks, 14 mutants), not this head (355 checks, 20 mutants), and its Red checks still says none beside a red tests / nightly-status

bus-nonce: a2ad2ea1888697df0668ec2b8bb87fae

This is round 2 of review for PR #2978 (R10-TRAIN-OVERLAP-GRADE part 2). I measured at 882da1e01b3d209cf7f8b6c02427166e7c0c7655, from a detached worktree at that head. `review_carry.py 6e89bf7f 882da1e01` prints FRESH-REVIEW: commit 5cd2f86eb carries code, and the other two are main merges.

## Block

The code repairs everything round 1 blocked on. All five surviving mutants are now killed, each by a named arm. The PR body was not updated to match this head, though, and fix-review.md steps 7, 8 and 11 check the body against the head:

- `## Head` still says the figures were taken at `72cfd904` and that `merge_train.py` and the harness are byte-identical between `72cfd904` and the head. At this head, `git diff --quiet 72cfd904 HEAD -- tools/audit/seat/merge_train.py` exits 1. Commit 5cd2f86eb adds about 120 lines to it. A stray paragraph still names `fbe478bb`.
- `## Figures` quotes `merge_train self-test: 350 checks, 0 failed` and `MUTANTS: 14 run, 0 not as required`. At this head I measured `355 checks, 0 failed` and `MUTANTS: 20 run, 0 not as required`.
- `## Mutation proof` lists M1–M13 and their red arms as of round 1. It never names M14–M19 or the five new arms. Several kill sets also changed: for example M2 now also turns the `--skip-bad` and `--overlap` arms red, and M9 also turns the drained, cure and ran arms red.
- The body never states the new behaviour, the skipped-then-merged cure (`CURED #<pr>`). Only the commit message and the instrument page do.
- `## Red checks` still says `none`. `tests / nightly-status` concluded failure on this head (job 123861683942: `NIGHTLY FAILED: slow failed in the last verification dispatch`, run 40948493872 at e5ddba1, which is main's). `review_packet.py` refuses `red-unanswered`. Round 1 recorded this line as owed, and it is still missing. The red is not this PR's: the diff reaches nothing nightly-status reads, and the job says it is not a required check. Still, the body has to name the check and give its cause and owner, which here is main's nightly `slow` lane.

The repair is a body edit, with no code change: rewrite `## Head`, `## Figures` and `## Mutation proof` for this head (355 checks, 20 mutants, M14–M19 and their arms, the cure), and name `tests / nightly-status` under `## Red checks` as main's.

## Findings

- The body describes a previous head. Its figures (350 checks, 14 mutants) and its byte-identity claim are false at 882da1e01, it does not state the cure behaviour, and `## Red checks` omits the red `tests / nightly-status`. Carry: R10-TRAIN-OVERLAP-GRADE
- `BRANCH-POLICY` same-verdict re-admission is still unbounded (round-1 finding). Each re-add while a code-owner approval is missing costs another `merge_tries` refusals. The body's carry 2 (park on a missing approval before attempting) is still open and is where the bound belongs. Carry: R10-TRAIN-OVERLAP-GRADE

## Evidence

- RESULT `python3 tools/audit/seat/merge_train.py --self-test` at 882da1e01b3d209cf7f8b6c02427166e7c0c7655: `merge_train self-test: 355 checks, 0 failed`, rc 0 (ev/selftest.txt).
- RESULT `python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` at 882da1e01b3d209cf7f8b6c02427166e7c0c7655: `MUTANTS: 20 run, 0 not as required`, rc 0 (ev/mutants.txt). M0 passes, M1–M19 are killed, and no mutant is STALE.
- Round-1 mutants re-run through the fixer harness's spans, each killed by a named arm with a null control:
  - X7 = M14 is killed by `a drained entry (#2, added while batch 1 ran) re-added while its batch runs and after it merges is ALREADY ...`.
  - X1 = M15 is killed by `an add against an old-code train (QUEUE_PENDING only, live pid) ...`. Its null control is #10 ADDED.
  - X2 = M16 is killed by `--overlap: an entry an EARLIER batch skipped, re-added, is recarried up front ...`.
  - X5 = M17 and X3 = M18 are both killed by `a rehearsal's serial entry not run is recorded ran: QUEUE_PENDING lists pending only ...`. That arm drives the real `review_packet.train_boarded`, and its null control is #3 boarded.
  - X4 was killed in round 1. X6 (the owner-pid guard in `seen_mark`) was ruled equivalent in round 1 and is unchanged.
- The skipped-then-merged over-count from round 1 is fixed. `Train.report` cures entries whose record is `merged`. M19 kills the `skipped-then-merged is cured` arm, whose null control (batch 1's own `SKIP REPORT: 1 skipped of 2`) holds.
- The round-1 dismissed item (unlocked `train_boarded` read) is unchanged and stays dismissed as round 1 recorded.
- Merge: `git merge-tree --write-tree origin/main 882da1e01b3d209cf7f8b6c02427166e7c0c7655` gives tree faeb463e, rc 0, no conflict (ev/merge-tree.txt). origin/main was 13871b7aa.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (ev/structure.txt). The diff does not touch VERSION, the manifest, RELEASE_NOTES.md or the claim files.
- Roles: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- CI at the head, read from check-runs:
  - `tests / nightly-status` concluded failure. That is main's nightly; it is not a required check and does not block.
  - Still in progress: `tests / closures`, `tests / coverage`, `governance / instrument-self-tests`, `codeql / Analyze (python)` and `prelude`.
  - `tests / fast (3.14)`, `tests / mutation`, `arch-score` and the governance checks are success. The rest are skipped or neutral.
  - The block does not turn on the in-flight runs.
- Finder's harness: none is committed for this group, and the packet says "none named". The only instrument is the fixer's own mutant runner, which the body discloses.
- Head re-read at write time: refs/pull/2978/head = 882da1e01b3d209cf7f8b6c02427166e7c0c7655 (ev/head-at-post.txt).
