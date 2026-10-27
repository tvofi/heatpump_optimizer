The root-cause record for #2697 (R10-MERGE-SUBJECT-HARDEN), which was blocked eight rounds out of eight (six `class-open`, two `mutation-vacuous`). The record is `dev/audit/rca/R10-RCA-MERGE-SUBJECT-CLASS-OPEN.md`. Its evidence instrument is `dev/audit/rca/merge-subject-class-open/differential.mjs`, the seat's own (not the finder's, a fixer's or a reviewer's). This runs beside the fix and never inside it. #2697's branch, `tools/policy/agreement.mjs` and its harness are not touched.

- **Cause.** The guard's acceptance was measured only on the tree, and the tree holds no merge writer, so every both-ends run read `refused=0` at base and head. The PR's one differential (`r10_merge_subject_census.mjs`) compares `MERGE_CALL` counts, not refusals. Nothing generated the guard's domain at either end.
- **Two symptoms.** Reviews 2 to 6 sampled spellings that main misses too (11 of 11 named: OPEN-AT-BOTH). Reviews 7 and 8 found a regression against main (3 of 3 named). A tree-generated differential shows that regression at round 1's first commit `09b1d002c`: 8484 lines that main refuses and the head does not, 8412 of them in the lead-closer class review 8 named.
- **Process state (c).** `fixer.md` step 3 and `fix-review.md` step 2 were followed and are flat on a writer-free tree. Their companion rule reads only the defect direction. Sub-finding (a): no policy splits a class-open PR; `fixer.md`'s split fires on `claims` only.
- **Cost test.** 24.3 h wall and 8 of 8 verdicts blocked; the regression arm alone cost 5.03 h (2 of 8). The proposed countermeasure M1 is a refused-set differential at both ends over a generated corpus. Its standing cost is under 10 s per guard PR, against about 10 min of expected loss per guard PR (P estimated 1 in 29). It passes. M1 is policy and is proposed only, for the owner, as state (c); its draft lines for `fixer.md` step 3 and `fix-review.md` step 2 are in the record's section 6. The record also leaves two items there rather than carrying them: M3, a split rule for a PR still class-open past round 3, is the owner's call; M4, naming the corpus generator in a lexical-guard brief from round 1, is the orchestrator's brief template.

## Head

`b85b5f37667839ea2fe88fa23b18ce10b9486b20`, one commit on its merge base `102f74975840088fbb29ea37c40b47aa2c126d15`. Everything below was measured at that head. Round 2 is body-only: the head and the record are unchanged. origin/main has since moved to `de794b537`; the tree-planted run below was repeated with that origin/main as base and gives the same figures.

## Mutation proof

n/a: this PR adds a record and a non-gating evidence script, and no production or check code. Its detector demonstration (root-cause.md step 5) is in the record, section 6: planted mode prints `main_not_head=8484` at `09b1d002c` and `8070` at `4aad9c117` (the defect), and `0` with origin/main as both ends (the null control).

## Null control

`node dev/audit/rca/merge-subject-class-open/differential.mjs planted origin/main origin/main` prints `main_not_head=0` over `planted=82735` lines. `corpus` mode with origin/main at both ends prints `main_not_head=0` and `null=0` of 8 over-fire nulls. `named` mode prints no `REGRESSION` for review 1's shape, which both ends refuse.

## Figures

- The per-review table (OPEN-AT-BOTH for reviews 2 to 6, REGRESSION for 7 and 8): `node dev/audit/rca/merge-subject-class-open/differential.mjs named origin/main`; the review-6 regression against its previous head: `node dev/audit/rca/merge-subject-class-open/differential.mjs named d0d35231c`
- Lead-closer corpus, 192/96/8 rows, `main_not_head` 192 at all seven heads from round 1 through round 6 and 147 at rounds 7 and 8: `node dev/audit/rca/merge-subject-class-open/differential.mjs corpus origin/main origin/main 09b1d002c b4dd11917 96ad30e87 455d7c200 5d79db511 d0d35231c 683dd52cb e73424f24 4aad9c117`
- Tree-planted corpus, `files=289`, 82735 lines, `main_not_head` 8484 (8412 lead-closer) at round 1 and 8070 (8016) at round 8, 12.1 s with `time`: `node dev/audit/rca/merge-subject-class-open/differential.mjs planted origin/main origin/main 09b1d002c 4aad9c117`
- Rounds, timestamps and the 24.3 h wall: `git log --reverse --format=%cI origin/review/2697` against `git log -1 --format=%cI 09b1d002c`
- Merges touching the four lexical guards (10, 1, 16, 9; 29 distinct of 809): `git log --first-parent --merges --since=2026-09-25 --oneline origin/main -- tools/policy/agreement.mjs`, and the same for the other three files, as in the record's section 4
- Guard size, 596 lines against 916: `git show origin/main:tools/policy/agreement.mjs` piped to `wc -l`, and the same at `4aad9c117`
- Seat counts (8 reviewer dispatches, 9 fixer dispatch commits on 7 refs) and the 141-ref, 300-verdict, 16-class-open review census are ref listings at the time of writing, not tree figures; the record says so
- Gate at this head: `python3 -I tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out` (`dev/audit/` is INERT). `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `python3 tests/layout.py` prints `layout self-test: ok`. `python3 -I tools/audit/seat/tmp_paths.py --check` and `python3 -I tools/audit/seat/ref_privacy.py --check` print 0 refused. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` predicts no red

## Red checks

none

## Forward-carry

Both carries are in the tree on the roster branch `handoff/audit-r10-roster`, in `dev/programme/rosters/wave-r10-groups.json`, written with `roster_edit.py append-carry`. Each one's precondition is the planted differential with its null control, measured at a merge base:

- To R10-MERGE-SUBJECT-HARDEN (its round-9 brief), at roster SHA `3cd2bab6a67d6ee3361b523b13e049dc1454d1a2`. Acceptance (1) asks for a differential over the finder's corpus, the reviewer's cases and the fixer's own closer-in-lead lines. That is a hand-bounded corpus. At `4aad9c117` the tree-planted corpus returns 54 `main_not_head` lines outside the quote-blind closer bucket (a quote, or a bracket inside a quote, in the lead, for example `stamp.py`'s `'raise Refuse("rows"'`). The carry, as it reads at that SHA: "Precondition control: `node dev/audit/rca/merge-subject-class-open/differential.mjs planted origin/main <head>` must return main_not_head=0, re-measured at the merge base. At 4aad9c117 it returns 54 other lines, and the null control with origin/main at both ends returns main_not_head=0. A hand-bounded corpus alone does not satisfy it." Carry: R10-MERGE-SUBJECT-HARDEN
- To R10-MERGE-SUBJECT-CASEARM, the group that inherits whatever round 9 leaves open, at roster SHA `00ceb9aa4455b0f1270ef6c7755d51838a2dd536`. It carries the same precondition, word for word, after #2697's round-8 carry, which it does not replace. Carry: R10-MERGE-SUBJECT-CASEARM

Read back: `git show <sha>:dev/programme/rosters/wave-r10-groups.json` holds each string under its group, and `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json`, run in a checkout of `00ceb9aa4`, raises no error on either group; it prints `TOTAL: 1 error(s)`, and that one is `[R10-IMMERSION-LATCH]`'s `coordinator.py:8761-8820` citation, which it prints identically at `fe2648fe7`, before both carries. Re-measured for this body: `node dev/audit/rca/merge-subject-class-open/differential.mjs planted origin/main origin/main 4aad9c117` prints `main_not_head=0` for origin/main as head (the null control) and `main_not_head=8070`, of which 54 are `other`, at `4aad9c117`.

## Friction

none
