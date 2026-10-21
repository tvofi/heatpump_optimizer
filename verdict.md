Fix review: merge cb48de247b39b47ffe9e010689f8ff4f971b7e32

bus-nonce: aa42fa3468a15c64be454da5c30aa04d

Round 2 of review (round 1 blocked 90788b1e5). Measured head: cb48de247b39b47ffe9e010689f8ff4f971b7e32, read from a detached worktree; still the branch tip when this verdict was written (`git ls-remote`, ev/head_at_verdict.txt). Merge base with origin/main: e7c664856, the base end of every both-ends figure below. The role file is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Findings

- **Two of the joiners the body says it left out are not pinned, and the body's reason for leaving them out is wrong for both.** The body says that allowing `;`, `so` or `)` as a joiner in `NOT_REQUIRED` "frees one of the review's attack sentences, or its `semicolon` case". I widened the joiner one way at a time (ev/joiner_mutants.txt, run with `-B` so no stale bytecode is read):
  - `)` frees round 1's parenthetical case, and the self-test kills it (1 failed).
  - `;` and `so` each free none of round 1's five attack sentences. Both survive the self-test (`189 checks, 0 failed`).
  - Each one does free a defect of the same shape: "The guard misses a deleted ref; mutation is not a required check; not blocking." and "The guard misses a deleted ref, which is not a required check so not blocking."

  `r10_carry_parser_mutants.py` has deletion mutants only for the clause (`P-notreq-*`), so its `survived=0` cannot see a widening. The live regex refuses both joiners, and both sentences are findings at this head (ev/class_attack_r2_head.txt). So this blocks nothing now. It leaves the boundary that round 1 blocked on guarded on only one of its three sides. The fix is two self-test rows, one with each sentence, plus two widening mutants in the harness. Carry: dismissed: the code at this head is correct, both sentences flag here, and the gap is only in pinning; it rides any later edit of `NOT_REQUIRED`.

## Evidence

- **Round 1's block is resolved.** I ran round 1's attack (ev/class_attack_r1.py, from verdict/2571 at 378816bc) and my own wider set (ev/class_attack_r2.py) under `## Evidence` of a merge verdict.
  - At the head every round-1 case is a finding: same-sentence nit, minor, defect, parenthetical and semicolon.
  - The #2544 sentence ("it is not a required context and does not block the PR") is no finding at the head. At e7c664856 it is a finding, so the parked verdict is freed.
  - Under `## Notes` every case is a finding at both ends.
- **Residual inherent to the design, not a block.** Three of my sentences are freed at the head (ev/class_attack_r2_head.txt):
  - "The guard misses a deleted ref; composed-proof is not a required check, not blocking."
  - a sibling of that sentence;
  - two stacked check clauses.

  In each, the only block-state words are the check's own clause, which the narrowing round 1 proposed deliberately frees. With no such words, the defect sentence alone ("The guard misses a deleted ref.") reads as no finding under the parser's word grammar anyway.
- **Mutation proof (step 1), my own mutants** (ev/mutation_mine.txt; the unmutated head reads `189 checks, 0 failed` and cloud_dispatch reads `32 checks, 0 failed`):
  - the whole Evidence arm deleted: many rows fail (as the body's M-A);
  - `claims` freed whenever `NOT_REQUIRED` is in the item: 7 failed;
  - the clause tail made unmatchable: 5 failed;
  - the `(?!\s*:)` guard removed: 1 failed;
  - `NONBLOCK` read over `t`, not `claims`: 5 failed;
  - `DEFERRED` dropped: the DEFERRED rows fail;
  - joiner widened to `;` or `so`: survive (see Findings).

  cloud_dispatch M-B': the carve-out sentence reverted to round 1's wording gives `32 checks, 1 failed` (ev/mutation_MB.txt).
- **Per-site mutants**: `r10_carry_parser_mutants.py` at the head prints `RESULT sites=166 unmapped=0 mutants=232 survived=0`, as the body says (ev/mutants_head.txt).
- **Finder's instrument at both ends (step 2).** `R10-VERDICT-ITEM-BARRIER` has no entry in the roster at origin/handoff/audit-r10-roster 2c76c3128, as in round 1, so no brief names a harness. I used the instrument that parked the verdicts, `carry_audit.py pr N` (ev/finder_carry_audit_pr.txt). The head and e7c664856 print the same lines, as the body says:
  - #2513: 2 routed / 0 unrouted;
  - #2544: 1 routed / 0 unrouted;
  - #2547: 0 routed / 1 unrouted.

  One earlier head run returned a different #2547 thread and no #2513 line. It did not reproduce on two re-runs and reads as a transient fetch (kept as ev/finder_carry_audit_pr_run1_transient.txt).
- **Companion (the fixer's replay harness, disclosed as the fixer's).** At the head it prints `fetch_*=identical`; RESULT verbatim 1/1/1, evidence 1/1/1, reshaped 0/0/0, planted 1/1/1, attack 1/1/1. At e7c664856 (harness copied in) it prints reshaped 0/1/0, planted 1/2/1, attack 1/2/1. Both ends match the body's table (ev/replay_*.txt).
- **Null control:** v*_planted=1 at the head for all three verdicts, and the #2544 clause is freed.
- **Not re-derived:** the body's 83-PR sweep and `--whatif` counts (33/33/17). They come from a live corpus fetched at 14:43Z. Round 1 re-derived the base and round-1 values on its own corpus, and I did not rebuild it.
- **Generator (step 10 of fixer):** I rendered the reviewer prompt at the head, 90788b1e5 and e7c664856. The counts for `never in the rest of its sentence`, `evidence only in a sentence saying` and `## Evidence` are head 1/0/1, round 1 0/1/1 and base 0/0/0, matching the body (ev/generator.txt).
- **Merge:** `git merge-tree --write-tree origin/main(b6a38f858) cb48de247` exits 0, tree a5ff6b16b, with no conflict (ev/merge_tree.txt).
- **Untouched files:** VERSION, the manifest, RELEASE_NOTES, tests/golden and the claim files are untouched (ev/untouched.txt is empty).
- **Cheap checks at the head:** STRUCTURE RATCHET PASSED; tmp_paths 0 refused; `Architecture score: dS +0.0000 NULL`; `MODE: SCOPED -- 1 script(s) run`; claims hygiene ok (ev/cheap_checks.txt).
- **Moved numbers (step 14):** tests/closures.json gains one line, classifying the new harness. The mutant harness grows by the new sites. Both are earned by the diff.
- **Head (step 7):** the body names cb48de247 as the head and describes the main merge of e7c664856, as the brief expects.
- **Forward-carry (step 10):** the body says `n/a` with a reason (the pre-flight fails closed on old-format verdicts).
- **CI on this head, read once from the check-runs API at the end (ev/check_runs.tsv):**
  - Green: pr-contract (twice; the second started 15:24:11Z, after nightly-status concluded at 15:23:46Z), mutation, scope, closure-scope, briefs, policy-docs, delivery-status, budget-raise-gate (x2), hassfest, validate-hacs, env-matrix, wave-script, instrument-self-tests, typing, browser, arch-score (one run), and Analyze for actions and js-ts. CodeQL is neutral.
  - Still running when read: fast (3.14), coverage (queued), Analyze (python), and a second arch-score run. I judged on the rest.
  - Red: `nightly-status` only. It grades main's scheduled runs, and this diff does not reach what it reads. The body's Red checks section names it and answers it (step 11).
