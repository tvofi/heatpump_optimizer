Fix review: blocked e81028ccef62bed5e4c6b6042f28193bc1d7ce8b mutation-vacuous: the call-site recarry mutant the body names as killed survives, and git_recarry's clean-merge and main-parent predicates are unpinned

bus-nonce: 2f1addadff5e0e81e60ff5c7c7caafb4

## Block

Round 1 (first fix review of #3241). Measured head `e81028ccef62bed5e4c6b6042f28193bc1d7ce8b`, merge base `9315526f8dca6dcd07f9cf3f2685bd1dd633b4f6` (= origin/main at review).

The body's mutation proof says: "Dropping the recarry argument at the call site is killed by `null control: the same head without the recarry test is REVIEW OWED`". It is not. That check calls `review_owed` directly inside `ledger.py --self-test` and never reaches `orchestrator_tick.py`. With the argument `lg.git_recarry(self.checkout or ".", "origin/main")` deleted from `orchestrator_tick.py`, `orchestrator_tick.py --self-test` passes (272 checks, rc 0) and `ledger.py --self-test` is untouched (mutant M7 SURVIVED, ev/mutants.txt). The two predicates that make a merge commit a "clean merge of main" also survive deletion:
- the conflict-resolution test (`resolved.strip()`, M3);
- the second-parent-in-main test (M4).
So the carry's core claim, *only clean merges of origin/main*, is pinned by no test.

The head is RED as well, and the body answers none of it.
- `governance / instrument-self-tests` concluded `failure` because of this diff. `tools/audit/seat/r10_ledger_mutants.py:91` anchors mutant `T3_review_owed_silent` on the exact `review_owed(...)` call text in `orchestrator_tick.py`, and the diff rewrote that text. The suite's mutant for "the tick's REVIEW OWED goes silent" can no longer be planted. Reproduced: `python3 tools/audit/seat/r10_ledger_mutants.py --self-test` gives 135 checks, 0 failed at base and 135 checks, 1 failed (`FAIL T3_review_owed_silent: anchor occurs once`) at head.
- `pr-contract / pr-contract` concluded `failure`. Its run started 07:58:39Z, after instrument-self-tests concluded red at 07:58:36Z, and refused: "check `governance / instrument-self-tests` is red and `## Red checks` does not name it".
- The final `gate` (07:59:40Z) fails on that pr-contract.

A cheaper detector existed: the same self-test, which runs in seconds. The body names it nowhere, so this red is also `root-cause-detectable: governance / instrument-self-tests` (fix-review.md step 11).

## Findings

- Mutation-vacuous call site (M7): deleting the `recarry` argument at `tools/audit/seat/orchestrator_tick.py:758` survives every test the diff reaches. The body says this mutant is killed, which is false. Add an `orchestrator_tick` self-test row where a PR whose head is a verdicted head plus one main merge prints `CARRY:` unflagged. Carry: R10-CARRY-RESIDUE
- Mutation-vacuous predicates (M3, M4): in `git_recarry`, deleting `resolved.strip()` (a merge carrying a conflict-resolution edit) and deleting the `is-ancestor <second parent> main` test (a merge of a non-main branch) both survive `ledger.py --self-test`. Each needs a fixture: a merge with a hand-resolved conflict prints REVIEW OWED, and a merge of a side branch prints REVIEW OWED. Carry: R10-CARRY-RESIDUE
- Defect: a BLOCKED verdict carries. `review_owed` collects `priors` from every verdict line, blocked ones included, so a head that is a blocked verdict's head plus one clean main merge prints an unflagged `CARRY:` and no `REVIEW OWED`. The orchestrator then sees a carry for a PR that has no merge verdict. fix-review.md step 12 and orchestrator.md section 11 carry only a `merge` verdict, and the pre-existing `carries` arm checks `last.startswith("Fix review: merge ")`. Reproducer (reviewer-built, not the finder's): ev/blocked_carry.py prints `CARRY: #9 …` for a prior `merge`, `blocked … mutation-vacuous` and `blocked … root-cause-unanswered` verdict alike. Restrict verdict priors to `merge` verdicts (dispatched heads stay priors) and add the blocked-prior null row. Carry: R10-CARRY-RESIDUE
- Unpinned wiring: the `flag=not text.startswith("CARRY:")` arm (M8), the `record_owed` call in the tick (M9) and the `RECORD-OWED:` literal added to the `FAMILY` regexes of `beat_jobs.py` (M10) and `owed_unactioned.py` (M11) all survive their scripts' self-tests. `beat_jobs.py`'s own comment says "the self-test pins each literal there", and it does not pin this one. Carry: R10-CARRY-RESIDUE
- Boundary unpinned: `record_owed`'s `age >= minutes` changed to `>` survives (M5). The fixtures are 29 and 31 minutes, and the carry's rule is "open 30 minutes". Add a 30-minute row. Carry: R10-CARRY-RESIDUE
- Broken instrument: the diff moved the call text that `tools/audit/seat/r10_ledger_mutants.py:91` (`T3_review_owed_silent`) anchors on, so `governance / instrument-self-tests` is red at head and green at base (ev/base.r10_ledger_mutants.log, ev/head.r10_ledger_mutants.log, job log ev/job_127771317138.log). Re-anchor T3 on the new call text and show the T3 mutant killed again. Also: the scoped closure the body quotes (doc_claims.py and entities.py only) does not reach this instrument, though it reads `orchestrator_tick.py` by text. That closure gap is worth a check by whoever owns `tests/closures.json`. Carry: R10-CARRY-RESIDUE
- Red checks unanswered: `## Red checks` says `none`. At this head, over all 68 check runs:
  - `governance / instrument-self-tests` failed (the diff's own red, above);
  - `pr-contract / pr-contract` failed (refusing the unnamed red);
  - `gate` failed three times: 127771703222 and 127772016712 ran before their runs concluded ("still being judged"), and 127781394257 failed on pr-contract.

  review_packet refuses with `red-unanswered` and `required-red`. Name each red with its class and its answer: for instrument-self-tests, the cheaper detector (`r10_ledger_mutants.py --self-test`, seconds) and why the fixer's pre-PR run missed it. Carry: R10-CARRY-RESIDUE
- Carry 3 (loop_cpu_ratio) is answered by assertion ("not re-measured here"), which the brief forbids. I measured it at base: delivered. All five CI owner-fixture readings in the jobs `tests/replay.py` cites fall inside (0.1245, 0.249] across three runner classes (ev/carry3_band.txt). The tree comment's figure is contradicted, though. It states the spread as "0.137-0.227 … edges 9-10 % inside", but ref30 job 125240101580 reads 0.128, 2.8 % over the floor. The body must cite a measurement, and the comment's spread must be corrected, or the residual margin dispositioned. Carry: R10-CARRY-RESIDUE
- Body inconsistencies:
  - It numbers the six carries three ways: 1-6 in the prose, 0-3 in Figures, and 4/5 (roster indices) in Null control, so "Carry 5" names record-owed in one section and the CARRY arm in another.
  - Its Null control and Head sections measure at `b88684a21`, not at the PR's merge base `9315526f`.
  - Its Head section's second line names `849ceee29`, a commit of the branch, as if it were a head.

  Carry: R10-CARRY-RESIDUE

## Evidence

- HEAD measured: e81028ccef62bed5e4c6b6042f28193bc1d7ce8b (ev/HEAD.txt). `git merge-tree --write-tree origin/main HEAD` gave rc 0 and tree 7225bfc6fb21, so the branch merges cleanly. Roles dir: three-dot diff merge-base...origin/main is empty, so the contract is current.
- Diff, read three-dot: 5 files; `dev/programme/delivery/3241.md` is in it; VERSION, the manifest and RELEASE_NOTES are untouched. The body's Head names the dispatch head.
- Carries settled at origin/main 9315526f (ev/carries_at_main.txt):
  - carry 0 (field_coverage `attribution`): delivered. The key sits in HOOKS `ignore` at `tools/policy/field_coverage.mjs:114`, and `git log -S` names df9bfd301.
  - carry 1 (pre-bash.sh hook): delivered. The script is in the tree, wired in `.claude/settings.json:24`, and `policy_lint.mjs` has `HOOK_TOOLS` and the REQUIRED row (408644f7f).
  - carry 2 (agreement bootstrap): delivered. The `(awaits <path>)` clause is in agreement.mjs, and the harness dev/audit/harnesses/agreement_two_pr.mjs is in the tree (82f333b9c).
  - carry 3: delivered by my measurement (ev/carry3_band.txt), with the residual in Findings.
  - carries 4 and 5 (record-owed, CARRY arm): absent. `git grep -nE "CARRY|RECORD-OWED|record_owed|recarry" origin/main -- tools/audit/seat/ledger.py` is empty, so building them is owed.
- RESULT ledger.py --self-test: base 77 checks, 0 failed; head 86 checks, 0 failed, matching the body's 86. The new rows fail at base by absence: the functions do not exist there.
- RESULT orchestrator_tick.py --self-test: 272 checks, 0 failed, at base and at head. beat_jobs.py: 107/0 at both ends. owed_unactioned.py: 46/0 at both ends.
- RESULT doc_claims.py (hastub): ALL 296 checks PASSED at both ends. structure.py: STRUCTURE RATCHET PASSED at both ends (seam_cut_total 423 <= 423). RESULT entities.py (hastub): ALL 2632 ENTITY CHECKS PASSED at both ends (rc 0, ev/rc.txt `entities-full`; the earlier rows there are a run without hastub, which fails with ModuleNotFoundError, and one capped at 230 s).
- Mutants (ev/mutants.txt, ev/mutants.py): these are mine; the PR committed no finder's harness, because the group's harness is the ledger self-test. Killed: M1 (ancestor test), M2 (row-only arm), M6 (approval), M12 (dispatched priors). Survived: M3, M4, M5, M7, M8, M9, M10, M11.
- Figures: I re-derived 86 checks, 296 checks, STRUCTURE RATCHET PASSED and the base-empty grep, which I took at 9315526f rather than at b88684a21. I also re-derived 2632 entity checks. I could not re-derive "pre-bash.sh --self-test 26 passed" or "agreement.mjs 233 of 233": I did not run those two.
- CI at the head, all workflows concluded: `merge_train.py classify` printed `RED e81028ccef62bed5e4c6b6042f28193bc1d7ce8b pending: none red: gate` with rc 1 (ev/classify.txt). Every non-green run is in ev/checkruns_final.tsv (68 runs). The failing steps' logs are in ev/job_*.log. refs/pull/3241/head is still e81028ccef62 at verdict time.
