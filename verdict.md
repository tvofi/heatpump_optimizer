Fix review: merge 9ddadc7666829f2550c61f1bfc9e6d7d2745aa2f

bus-nonce: 64c74994d5f442bb6f5d51e5f6b15bd1

Round 2 (delta review of the round-1 re-cut). I measured head 9ddadc7666829f2550c61f1bfc9e6d7d2745aa2f, and it was still `refs/pull/2829/head` and `triage/s6-batch29` when I wrote this. Reviewed against dev/governance/roles/proposal-triage.md and dev/governance/roles/fix-review.md. Neither changed between merge base c9cbe6b45 and origin/main 8aee66b77, because the roles diff is empty.

## Round-1 block, item by item

- **P162 is closed.** The verdict is now "DEFER -> already enforced". The ruling quotes the `pr_trap` / `open_pr.sh:48` stop before the create at `:54-58`, says the old control was vacuous, and records that #2817's DIRTY state came from main moving after the open. The OPENPR-ATOMIC carry is dropped. A wording residue remains (see Findings).
- **P161 is closed.** The verdict is now DEFER, and the carry is dropped. "4 have no whole word `\bcontrols?\b` ... A substring rule ... refuses 14" re-derives exactly on roster 63d8938eb: 54 groups in the pool, 4 under the word rule, 14 under the substring rule, 3 with empty `files`, and 6 in the union. "R10-RCA-HEADMOVED's kind is `study`, so it would not be exempt" also holds. Evidence: ev/p161_rederive.txt.
- **P166 is closed.** It now reads "DEFER -> owned by R10-LEGIONELLA-COMPLETION (queued), whose brief point (3)", citing the `s5-batch1.md` precedent. The group is queued on origin/main.
- **The P158 `ci.yml` citation is closed.** It now reads "`gate` needs `[prelude, pr-contract]` (`ci.yml:301-302`), and `pr-contract` needs `codeql` (`ci.yml:254`)". Both lines hold at dfcd8d9be.
- **The P158 76-of-144 figure is closed as a citation.** It now cites `codeql_scope.py:19`, and the figure is there. The paraphrase is loose (see Findings).
- **The P164 citation is closed.** It now reads "the drop is asserted at `merge_train.py:4655` and `:4659`; `:4876-4890` assert only no drop on a red main". Both hold.

## Findings

- **P158 is the ruling I would change, from a build trial to measure-first. This does not block, because the ruling meets rule (c).** On origin/main 8aee66b77 the group R10-PROOF-CODEQL was already appended on handoff/audit-r10-roster at 362a47062, and its brief there lacks the trial's removal criterion ("reverted if CodeQL's tail beyond the other checks was under 5 min"). It also cites "triage ruling P158 in PR #2829" rather than `triage: dev/programme/triage/s6-batch29.md#P158`. The file's own brief text for `append-group` lacks the removal criterion too, so a fixer would build the skip and never see the condition for reverting it. The criterion is also ambiguous as written: once proofs skip, their CodeQL tail is zero by construction, so it has to be read from proofs that still analyze.
  - Evidence that the trial's premise needs measuring first: on the full main push of dfcd8d9be (run 40215411184, Actions jobs API), `Analyze (python)` took 30.7 min, which confirms the 28-30 min figure. It ended at 17:56Z, though, while `tests / closures` ran to 18:09Z and `arch-instrument` to 18:11Z, so CodeQL was not the tail of that full-scope push (ev/p158_main_push_codeql.txt). A batch proof is the same full-scope push shape (`prelude.py:226`).
  - The first step should read the CodeQL tail of past `batch/*` proof runs from Actions history, which costs no code. Build the skip only if the median tail exceeds 5 min, and put that criterion into the group's brief as a precondition.
  - Carry: R10-PROOF-CODEQL
- **P158's docstring paraphrase is loose.** The ruling says `codeql_scope.py:19` "records that 76 of the 144 pull requests merged in round 10 skipped". The docstring (`:15-19`) says those 76 *paid* the 23-26 min python analysis for a result that could not differ from main's. That is the motivation for the PR-head skip, not a count of skips. The figure is cited correctly. Carry: dismissed: wording only, the cited figure and its source line are correct and no carry text quotes it
- **P162 reads "DEFER -> already enforced, and owned where it is not" but names no owner.** Its fourth bullet ("What is left is that a conflicting handoff must never become a PR. This is the atomic-open seam.") and its `Cost: XS` paragraph still describe building the merge-tree refusal, which contradicts "already enforced" and "Closure saving: none; the refusal is already enforced". The verdict is right, and no roster text cites P162 (`roster_edit.triage_refusal` refuses a P162 citation as DEFER, ev/mutant_ruling_consumer.txt). Carry: dismissed: residual wording in a DEFER ruling that routes nothing; strike it in the next triage touch of this file if one comes

## Evidence

- Re-check of the triage rule on every ruling:
  - **P158** is ACCEPT as a trial, with measurement (proof wall time over three batches) and a removal criterion (tail < 5 min). It is a new group, already appended as queued on the roster branch, with files `tools/pr/codeql_scope.py` and `tools/ci/prelude.py`. No group on origin/main owns either file. R10-FLY-ROW-HEAD-CARRY holds `codeql.yml` with three after-edges, as stated.
  - **P163** is ACCEPT as a trial, removed if no STUCK line appears in 48 h. R10-UPDATE-PR-SIGNALS is in-progress on origin/main, and `dispatch/fixer-r10-pusher-reap` exists (4347a0b74). The carry names its controls.
  - **P164** is ACCEPT measure-first. R10-TRAIN-OVERLAP-GRADE is queued and owns `merge_train.py`. The carry's first step is `merge_train.py stats`, built only past 0.5 h/day of lost time. The arithmetic holds: 0.8^3 = 0.512 >= 0.5 and 0.8^4 = 0.41.
  - **P159, P160, P161, P167** are DEFER, and each names what would change the answer. P159 names R10-FLOW-DESIGN-STAGES, which is not-started.
  - **P165** is DEFER, owned by R10-REPLAY-REAL-DAY, which is not-started.
  - **P166** is DEFER, owned by R10-LEGIONELLA-COMPLETION, which is queued.
  - No DEFER names a done or absorbed group. R10-INPUT-STALENESS is cited as done, as landed work, not as an owner. Re-cuts cite verdict 6402371947, and the earlier rulings (P129, P140, P144, P153) are cited by number. ev/destinations.txt.
- No roster text on handoff/audit-r10-roster or origin/main cites `s6-batch29`, so no carry was appended from a ruling that is now DEFER. ev/destinations.txt.
- Ruling consumer, as RESULT lines: `roster_edit.triage_refusal` passes P158, P163 and P164 citations and refuses all seven DEFER citations. A mutant that flips P163 to DEFER makes the P163 carry refused. The null case, P168, returns None. ev/mutant_ruling_consumer.txt.
- Body figures: "3 ACCEPT, 7 DEFER" re-derives with the body's own grep. The body's per-ruling list matches the file.
- Diff (three-dot from c9cbe6b45) touches only `dev/programme/triage/s6-batch29.md` (+139) and `dev/programme/delivery/2829.md` (+1). There is no host or home path, and VERSION, manifest and notes are untouched. `git merge-tree --write-tree origin/main 9ddadc7666829f2550c61f1bfc9e6d7d2745aa2f` exits 0 with tree 20fdec822. ev/diff_merge_counts.txt.
- Citations re-read at dfcd8d9be and found to hold: `codeql_scope.py:19,29-31`, `prelude.py:226,343-344`, `ci.yml:254,301-302`, `merge_train.py:5435,4655,4659,4876-4890`, `pr_args.sh:32-35,66`, `update_pr.sh:35`, `open_pr.sh:6,15,34,48,54-58`, `cloud_relay.sh:101-105`, `ledger.py:90-98`, `orchestrator_tick.py:844-848`, `tests/dst_checks.py`. There is no `pool.py` on origin/main. ev/citations.txt.
- Not re-derived: the s41 batch-1 proof timing (2ac575d0, about 18:55Z), the #2819 "20 min or more" stuck push, and the plan-opt handoff-to-open median of 0.99 h. These are orchestrator or filing figures that neither the tree nor git answers. I did not re-derive the closure-saving model figures either.
- CI on 9ddadc7666829f2550c61f1bfc9e6d7d2745aa2f, from the check-runs API:
  - `governance / delivery-status` is red with OVERDUE on rows #2780, #2749, #2775, #2797, #2762 and #2795. None of them is #2829, so the red comes from main's backlog and not from this diff. It is not a required check and does not block, as the job itself prints.
  - Every other completed check is green. `instrument-self-tests`, `lane-proofs` and a second `prelude` were still running.
  - No red check owes a root-cause answer. ev/ci.txt.
