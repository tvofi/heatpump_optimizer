Fix review: blocked 20d5aab00a01cb3bf3738e1e78a13273089bc523 root-cause-detectable: governance / instrument-self-tests

bus-nonce: 3b5bbd75cbe15952821ac03c940ad9fa

## Block

This is round 2, a delta round after the block of 794fe6a7.

1. **The diff turns `governance / instrument-self-tests` red, and the body does not name it.** The failing step is `bash tools/audit/seat/pr_args.sh --self-test`, which the job runs for open_pr.sh, pr_args.sh and update_pr.sh. It gives `pr_args self-test: 172 checks, 19 failed` in CI (job 127067016573). I reproduced the same 19 FAIL rows locally at 20d5aab0 (rc=1, 287 s). At base 8364e624 it gives `172 checks, 0 failed` (rc=0, 209 s), and the base commit's own `instrument-self-tests` run is green (127049851918).
   - The failing rows are the ones keyed to the push flags this diff changes in open_pr.sh and update_pr.sh, for example:
     - `open_pr: its row push passes --row-only, and its code push does not`
     - `null control: a new code sha is merged and pushed through the full prepr, main still unmerged`
     - `null control: a code sha the head lacks is merged and never asks for --row-only, so its push runs the full prepr`
     - the `mut:oprowonly`, `mut:rowclose`, `mut:oplock` and `mut:bodyonly` mutant rows.
   - The code push now passes `--reuse` (open_pr.sh p1, and update_pr.sh `RO=--reuse`), and pr_args.sh's fixtures were not updated for it. The diff edits open_pr.sh and update_pr.sh without running their own self-test: the body's Figures name only prepr.sh and app_push.sh.
   - `## Red checks` says `none` and describes acd20e42, not the PR head. `pr-contract` refuses it (127078917945, started 05:58, after instrument-self-tests concluded at 05:52): ``check `governance / instrument-self-tests` is red and `## Red checks` does not name it``.
   - A cheaper detector existed before the handoff: `bash tools/audit/seat/pr_args.sh --self-test`, about 5 min locally, run on the two edited seat scripts. That makes this `root-cause-detectable`.
   - The repair is to update pr_args.sh's fixtures to the new `--reuse` contract, or fix the wiring they catch, keep both null controls meaningful, and answer the red in the body.

2. **mutation-vacuous on reuse_verdict's condition (e).** The mutant replaces `[ "$n" = 0 ] ||` with `true ||` on tools/pr/app_push.sh line 313. It survives `app_push.sh --self-test` (`225 checks, 0 failed`) and all 15 rows of my planted-receipt harness.
   - (e) is load-bearing. In my plant F9, HEAD is the clean merge of C and main plus two commits that net to no tree change. At the head (e) refuses it: `HEAD carries 2 commit(s) beyond code ...`. Under the mutant it is REUSED (`ev/plant_F9.*`).
   - The body justifies dropping `agreement lane` by "the only new [first-parent subjects] are the open's or update's automatic merge and the row", which only (e) enforces. A surviving (e) therefore lets a reuse skip a check on subjects the body says cannot exist. (d) does not cover this, because the tree is identical.
   - The repair is one real-git row, with F9's shape, in app_push.sh's reuse block.

## Findings

- The diff breaks pr_args.sh's self-test (19 of 172 rows), so instrument-self-tests is red on 20d5aab0. Carry: R10-HANDOFF-PATH
- `## Red checks` does not answer the red instrument-self-tests at the PR head, and pr-contract refuses the body. Carry: R10-HANDOFF-PATH
- Surviving mutant on reuse_verdict (e) (app_push.sh:313 `[ "$n" = 0 ] ||` -> `true ||`). No row pins the tree-neutral extra-commit case. Carry: R10-HANDOFF-PATH
- Surviving mutant A6 (app_push.sh:564 `if [ "$reused" = 1 ]` -> `if true`). Carry: dismissed: equivalent mutant -- RV_C is set only on a reusing verdict, so the export is PREPR_SKIP_CODE="" and REUSE stays empty

## Evidence

- Head measured: 20d5aab00a01cb3bf3738e1e78a13273089bc523 (ev/HEAD.txt). It merges 794fe6a7 with acd20e42, and its tree equals acd20e42's tree (`git diff --stat 20d5aab0 acd20e42` is empty). The code delta since the blocked head is 7ad8eff5 and d30e0846; the other commits are clean merges of main (remerge-diff is empty for 1acf58eb, c058f0d9, e830261a, acd20e42 and 20d5aab0).
- Roles diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- Merge with main: `git merge-tree --write-tree origin/main 20d5aab0` (origin/main 6125b263) exits 0 with tree 894471d4, a clean merge.
- Resolution 6e652a3e (the conflict in tools/pr/prepr.sh) kept both sides. `git diff c0b082bc 6e652a3e -- tools/pr/prepr.sh` has the same +/- line set as `git diff af941ad4 91a75ed8 -- tools/pr/prepr.sh` (SAME-CHANGESET), so the resolution is main plus exactly the branch's own changeset. Main's step 1a3, the lazy take_slot and the closures_owes_slot fixture are kept (ev/resolution_6e652a3e.remerge.diff, ev/branchside.diff, ev/afterres.diff).
- The previous round's mutant P1 is KILLED. It deletes the main flow's `merged_steps "${1:-}" "$UNPINNED_SITES"` line (ev/mutant_P1.diff). Under it, `prepr.sh --self-test` gives `508 passed, 1 failed` with `FAIL (a) and runs tests/structure.py and ci predict on HEAD merged with main, once each (got 00, wanted 11)` (ev/prepr_selftest.mutant_P1.log). Null control: unmutated, `509 passed, 0 failed` (ev/prepr_selftest.head.log).
- `app_push.sh --self-test` at the head gives `225 checks, 0 failed` (ev/app_push_selftest.head.log). The body's 509 and 225 are re-derived.
- My mutants on reuse_verdict (ev/app_mutants.sh, ev/app_mutants.txt): A1 (b) tree check is killed by the self-test and by plant F1b. A2 (c) ancestor check is killed. A3 (c) clean merge is killed. A4 (d) tree equality is killed by 2 rows. A5 (e) SURVIVES. A6 is equivalent.
- Planted receipts (ev/plant_rv.sh, my own harness against the production reuse_verdict). The 15 rows are:
  - nulls: an open (NULL) and an update over the live head (NULL2), both reused;
  - F1 a trailer naming another head;
  - F1b HEAD's sha with C's tree;
  - F2 an extra code commit after the receipt;
  - F2b new code below the merge;
  - F3 a receipt from a different base (patch re-cut on main);
  - F3b the old-base sha with the new tree;
  - F4 an evil merge;
  - F5a to F5c malformed trailers;
  - F6 the receipt on a non-tip commit;
  - F7 a row commit plus another file;
  - F8 another PR's row.

  All 15 PASS at 20d5aab0 and at 794fe6a7 (ev/plant_rv.head.txt, ev/plant_rv.794fe6a7.txt). Every forged or stale receipt is refused fail-closed.
- A receipt never skips the merged-tree checks. `merged_steps` runs outside every REUSE block, and P1 shows that the self-test pins the call.
- No weakening for a PR without a receipt. With PREPR_SKIP_CODE empty, every new `if [ -n "$REUSE" ]` block takes its else branch, which holds the original steps. The only removed lines in tools/ are moved or split lines (the recorder cache moved up; `rm -f "$COPY_PATHS"` split from the cache removal). Full runs gain `merged structure`. update_pr.sh's `--reuse` on a failing verdict runs the full prepr. `bash -n` passes on all five scripts.
- Figures at the head (ev/figures.txt): `STRUCTURE RATCHET PASSED`; `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`; claims, VERSION, notes and manifest untouched (rc=0).
- The body has all 7 template headings (Head, Mutation proof, Null control, Figures, Red checks, Forward-carry, Friction).
- CI: `merge_train.py classify` final `RED 20d5aab0... pending: none red: gate` (ev/classify.log, ev/classify.out). These are the head's non-green runs (ev/nongreen_checks.txt):
  - gate x3 and pr-contract x3, failing on the body's red-checks answer;
  - instrument-self-tests, caused by the diff (Block 1);
  - delivery-status, whose OVERDUE rows are #3174, #3091, #3089 and #3192, not this PR's open row;
  - nightly-status, which this diff does not reach.

  Neither delivery-status nor nightly-status is this PR's (fix-review.md 11).
- I did not re-take the body's kept-step wall time under PREPR_SKIP_CODE (27 s); the body also says it was not re-taken.

## Friction

- The brief says to pass `--reviewed-head 794fe6a7...` to review_packet.py render, but at this tree it has no such option (`unrecognized arguments`). I rendered without it; the delta was reviewed by hand from 794fe6a7.
- The brief's "push handoff-wip at each milestone" conflicts with "push nothing else" and "never write to any branch except your return refs". I pushed only the probe ref.
- The frugal routing hook refused inline file reads mid-review, so the template heading check went through a scout agent.
