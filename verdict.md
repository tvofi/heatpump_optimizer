Fix review: blocked 7c64db1b3ee50453bf3f5d12055d6a2bca8baeb7 carry-missing: not carried to R10-MERGE-SUBJECT-HARDEN or R10-MERGE-SUBJECT-CASEARM

bus-nonce: 06f37283b35b5cc5575d9b42b0ee9621

Round 1 review of root-cause PR #2798 (R10-RCA-MERGE-SUBJECT-CLASS-OPEN), measured at head `7c64db1b3ee50453bf3f5d12055d6a2bca8baeb7`, merge base and origin/main `102f74975840088fbb29ea37c40b47aa2c126d15`. Contracts current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Block

`fix-review.md` step 10 and `finding-propagation.md` "Enforcement" both apply. The producing PR does not merge until the carry is **in the tree**, and the body has to name the file, the stage and, for a roster carry, the branch SHA. This body's `## Forward-carry` names only group ids (`Carry: R10-MERGE-SUBJECT-HARDEN`, `Carry: R10-MERGE-SUBJECT-CASEARM`). It names no file and no `handoff/audit-r10-roster` SHA, and the carry is not there:
- The roster branch `handoff/audit-r10-roster` at `f57b6d52e` (2026-10-25T09:33:28+01:00) is the latest commit. In `dev/programme/rosters/wave-r10-groups.json`, the R10-MERGE-SUBJECT-HARDEN group (`resume: in-progress`) has no string holding `differential.mjs`, `planted`, `R10-RCA-MERGE`, `#2798` or the 54 `other` lines. The same holds for R10-MERGE-SUBJECT-CASEARM (`resume: not-started`). CASEARM's only `carry` entry comes from #2697's round-8 verdict. It carries the hand-bounded corpus ("the finder's harness corpus plus the reviewer's unmatched-closer line"), not this record's tree-planted differential.
- `dev/programme/carries/` on that branch has no carry for either group. `git grep -l differential.mjs` over `dev/programme` and `.claude/workflows` at `f57b6d52e`, and over the same paths at origin/main, returns nothing.
- The out-of-tree round-9 brief, `PROMPT.md` on `dispatch/fixer-r10-merge-subject-harden-r9` at `1d13cb91e` (09:30:30+01:00), still states acceptance (1) as the hand-bounded corpus that this record calls insufficient. It does not name the planted differential or the 54 lines.

The finding meets the bar for carrying: it is measured with its null control (planted `main_not_head=0` with origin/main at both ends, 54 `other` lines at `4aad9c117`; both re-derived here). It also narrows what round 9 and CASEARM must accept. The fix needs no change to the record. Append the two carries with `roster_edit.py` on `handoff/audit-r10-roster`, putting the control as a precondition and adding a re-measure-at-merge-base instruction. Read them back with `brief_lint.mjs`. Then name the file, both groups and the roster SHA in the body's `## Forward-carry`. If round 9 is still running, also send the change to its out-of-tree brief.

Everything else in the review passes; see Verdict basis and Evidence. Round 1.

## Verdict basis

The record names all four products `root-cause.md` requires:
1. **Cause**: the guard's acceptance was measured only on a writer-free tree, so both-ends runs read flat; the loss direction (refused at base, missed at head) had no unit and the gain direction no generated corpus. I re-derived both populations with the instrument (11 of 11 named OPEN-AT-BOTH, 3 of 3 REGRESSION against main, review 6 a REGRESSION against `d0d35231c`) and the round-1 regression (planted `main_not_head=8484` at `09b1d002c`).
2. **Process state**: (c), with quoted steps (`fixer.md` step 3, `fix-review.md` steps 2 and 6), and a sub-finding (a) for the missing class-open split rule. The (a) sub-finding is confirmed by reading `fixer.md:307-314`: its only split fires on a re-cut body blocked on `claims`.
3. **Cost test**: every figure I could re-derive matches (Evidence). P(recurrence) is stated as an estimate from one instance, disclosed as such.
4. **Countermeasure**: M1 (policy, proposed only), M2 (instrument), M4 (brief template), M3 recorded as the owner's call. M1 maps to state (c); M3 maps to the (a) sub-finding.

Check-shaped M1/M2 demonstration: fails on the defect (planted 8484 at `09b1d002c`, 8070 at `4aad9c117`) and the null control (`main_not_head=0` with origin/main at both ends) both reproduce at both ends. "Passes once fixed" has no fixed head (round 9 has no pushed head: `git ls-remote origin` shows `fix/r10-merge-subject-harden` still at `4aad9c117`); the record says so and carries the run to M2's builder.

Scope: the three-dot diff touches only `dev/audit/rca/R10-RCA-MERGE-SUBJECT-CLASS-OPEN.md`, `dev/audit/rca/merge-subject-class-open/differential.mjs` and `dev/programme/delivery/2798.md`. No production code, no check code, no policy file. M1's draft lines appear only as quoted drafts in section 6; `fixer.md` and `fix-review.md` are unchanged.

## Findings

- The record's section 2 quotes `grep -rn -i 'three-round\|split the' dev/governance/` as returning "only that line" (`fixer.md`'s re-cut split). At origin/main it returns `dev/governance/config/policy_budgets.json:6` and `dev/governance/roles/designer.md:20`, and not the `fixer.md` line, since `fixer.md:314` says "splits the". The conclusion, that no policy splits a class-open PR, holds: I read `fixer.md:307-314` and `designer.md:17-20`. Only the quoted output is wrong, and no figure, state or countermeasure depends on it (`ev/census.txt`). Carry: dismissed: conclusion re-derived by reading the two files; a wrong grep transcript changes nothing the record decides
- The record's section 6 "does not go green by skipping" leg says a run that read nothing "reads `planted=0`". Under a planted mutant with an empty file list, the instrument prints `files=0`, an empty `corpus` line, no `planted=` token at all, `main_not_head=0` at every head, and exit 0. That is the same `main_not_head` line a passing guard prints (`ev/instrument_mutants.txt`, mutant `m_empty_tree`). Recommended M2 runs `differential.mjs planted` as an acceptance differential, so it should refuse, with a non-zero exit, a corpus of zero lines and a base that refuses fewer than the corpus, before any seat keys on `main_not_head=0`. Carry: R10-MERGE-SUBJECT-HARDEN

## Evidence

- `ev/HEAD.txt`: the head reviewed.
- `ev/named.txt`, `ev/named_d0d.txt`: `named origin/main` matches the record's per-review table row for row. `named d0d35231c` prints REGRESSION for review 6's wrapped argv.
- `ev/corpus.txt`: corpus 192/96/8. origin/main at both ends gives `main_not_head=0`, null 0. Rounds 1 to 6 give 0 lead-closer refused and `main_not_head=192`. Rounds 7 and 8 give 45 and 147. Matches.
- `ev/planted_head_tree.txt` (run from a worktree at the head) and `ev/planted_base_tree.txt` (the head's script run in a checkout at the merge base): identical. files=289, planted=82735. Null control 0. `09b1d002c` gives 74251 refused, `main_not_head=8484` (8412 closer, 16 comment, 56 other). `4aad9c117` gives 74665, 8070 (8016 closer, 54 other). This took 9.6 s here against the body's 12.1 s.
- `ev/instrument_mutants.txt`: a head guard that refuses nothing gives `main_not_head=82735` (detected). Disabling the base-minus-head test gives `main_not_head=0` at `4aad9c117` (the null mutant reads as a pass, which is expected and shows the comparison carries the signal). The empty-tree mutant is the finding above. A bogus mode exits 2, as claimed.
- `ev/figures.txt`: the 8 verdict timestamps re-derive the per-round gaps 3.10, 4.94, 1.49, 1.90, 5.88, 1.99, 2.32 and 2.71 h and the 24.3 h wall from `09b1d002c` (08:01:01Z). Blocks are 2 mutation-vacuous and 6 class-open. Merges touching the four guards are 10, 1, 16 and 9, 29 distinct of 809. Guard is 596 lines at main and 916 at `4aad9c117`. Main's last guard commit is `ca1bc2b0e` (2026-10-23).
- `ev/census.txt`: review 8's `evidence/census.txt` prints `TOTAL old=63 new=63 over 290 file(s)`, no DIFF line, as quoted. Ref census now: 141 `review/*` refs, 300 verdict commits, 16 class-open over 9 PRs (2697: 6, 2711: 2). This matches the record, though it is a ref listing rather than a tree figure, as the record says.
- Figures I did not re-derive: the seat counts (8 reviewer dispatches; 9 fixer dispatch commits on 7 refs plus 3 local seat branches) and the 28 to 32 s `agreement_py.py --run` timing. I also did not run the finder's `md_plant.sh` at the three ends; the instrument's `named` mode covers the same spelling.
- Finder's harness: none applies, because this is a root-cause record with no production change. Mutation proof: n/a, because no production or check line is written, and CI `tests / mutation` is green.
- `ev/gate_checks.txt`: `closure.py select` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` `structure.py` prints STRUCTURE RATCHET PASSED. `ref_privacy --check` and `tmp_paths --check` print 0 refused. VERSION, the manifest and RELEASE_NOTES are untouched. The commits carry no trailers. `entities.py` (`ev/entities.txt`) ran under `PYTHONPATH=tests/hastub` and hit my 300 s timeout (exit 124) with every printed line `ok`. It did not finish here, so I record no result for it. CI `tests / fast (3.14)` runs it and was still in progress.
- Merge: `git merge-tree --write-tree origin/main 7c64db1b3` exits 0 (tree `c54b1d6f0`), with no conflict and no claim file touched.
- CI on this head (check-runs API, 39 runs): no run concluded failure. Completed ones are success, skipped or neutral (CodeQL). Still in progress when read: `tests / browser`, `tests / fast (3.14)`, `tests / closures`, `governance / env-matrix`, `governance / instrument-self-tests`, `codeql / Analyze (python)` and one `prelude`. Red checks: none, so step 11 has nothing to answer.
- Forward-carry (step 10): see `## Block`. I confirmed the 54 `other` lines are present at `4aad9c117` (`ev/planted_head_tree.txt`). The destinations were read at `handoff/audit-r10-roster` `f57b6d52e` and `dispatch/fixer-r10-merge-subject-harden-r9` `1d13cb91e` (`ev/carry_search.txt`).
- The head is unchanged at the time of writing: `fix/r10-rca-merge-subject-class-open` is at `7c64db1b3ee50453bf3f5d12055d6a2bca8baeb7`.
