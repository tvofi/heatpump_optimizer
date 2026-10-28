Fix review: blocked 172afa85d2bc2f68b402217981f22cfb26e86b56 class-open: review_carry.py answers CARRY for a hand-resolved conflict merge (this PR's own 98c6676a8), which app_approve.sh --carry refuses and the new fix-review.md step 12 sentence would carry

bus-nonce: 357739f494f0bd9d00313d33c001f85e

## Round

First review of this PR at this head.

## Block

`review_carry.py` decides CARRY from the commit range alone. Any range whose branch-only commits are all merges counts as clean, and the merge's own tree is never compared against git's automatic merge. Its docstring says "a merge authors no code of its own". That is false for a merge whose conflict was resolved by hand. Measured on this PR's own history: `review_carry.py 32221ca27 98c6676a8` prints `review_carry: CARRY` (rc 0). But `git merge-tree` of 98c6676a8's parents conflicts in `tools/pr/app_approve.sh`, and the body says that conflict was resolved by hand in `carry()`. Over the same range, `app_approve.sh --carry` refuses with "98c6676a8… is not the automatic merge of its parents" (rc 1). See ev/carry-disagreement.txt.

So two instruments now disagree on the case that matters most. Policy and tooling both act on the weaker of the two:
- The new fix-review.md step 12 sentence says a `merge` verdict "carries while `review_carry.py <verdicted> <new>` prints `CARRY`". The "Else a main merge is its resolution delta" sentence then never applies to a hand-resolved merge, because CARRY already fired. This contradicts step 13 and orchestrator.md section 7: a hand resolution is a resolution delta for the same reviewer.
- `bus.sh dispatch --reviewed-head` refuses to mint a nonce on that CARRY. So the reviewer cannot be dispatched over a hand-written conflict resolution, while `app_approve.sh --carry` will still refuse to carry it. The result is a head that neither carries nor can be re-reviewed through the documented path. The alternative is a seat that reads the policy sentence as permission to treat unreviewed resolution code as reviewed.
- The new orchestrator.md sentence makes this worse: it calls a second reviewer over a clean range "the error, not diligence" and makes review_carry's `CARRY` the arbiter.

The fix is small. `review_carry.py` should count a merge as clean only when its tree equals `git merge-tree --write-tree` of its parents outside the driver files, as app_approve.sh already does, and print FRESH-REVIEW otherwise. Add a self-test fixture for the hand-resolved merge, plus its null control. Alternatively, the two contract sentences could name app_approve.sh's `--carry` as the predicate rather than review_carry.py. None of the existing mutants or self-tests reach this case: all 14 review_carry checks pass with it open.

## Policy judgement (does each changed sentence change what a seat must do?)

fix-review.md:
- Publish paragraph: the parenthetical about the nonce and the evidence file was dropped. **No change**: the same two obligations move into the closing verdict paragraph.
- Step 9: the #373/#258 examples were removed. **No change**: they were motivation only, and the rule stands.
- Step 11: "only the run's own log separates them" was merged with the next sentence. **No change**: the obligation to read the lane's log stays.
- Step 12, head-moved paragraph: reworded shorter. **No change**.
- Step 12, carry paragraph: **changes what a seat must do.** The carry predicate moves from orchestrator.md section 11's predicate to `review_carry.py` printing CARRY. It also adds "attaches to the head its first line names". This is the sentence the Block concerns.
- Closing verdict paragraph: **changes what a seat must do.** It states the verdict first-line grammar, the nonce line, the evidence-file rule, and the cloud seat's probe layout (`ev/`, subject, ref) as obligations of the role file. Before, the role file deferred to the dispatch prompt and web-fix-wave.js. Substantively it matches what cloud_relay.sh enforces, and the cloud_relay self-test pins it.

orchestrator.md:
- Section 7, the reworded freeze paragraph: mostly no change. **One change**: a new duty forbids dispatching a second reviewer over a range clean against the reviewed head, with review_carry's CARRY as the refusal (see Block).
- Section 11, the carry bullet: **changes what a seat must do.** "the claim files equal origin/main's" becomes "each claim file a pure union of both sides". This loosens the carry condition, which the body says follows a coordinator addition on 2026-10-27.

Every sentence marked as a change is policy. It needs tvofi's approving review at the head before merging, as the body's ## Approval section already says.

## Findings

- The Block above: review_carry.py's merge predicate treats a hand-resolved conflict merge as clean, so the step-12 carry sentence, the orchestrator section-7 refusal and `bus.sh dispatch --reviewed-head` all CARRY a resolution no reviewer saw, and app_approve.sh refuses the same range. Carry: R10-REVIEW-CARRY
- The review packet refused with `hot-file: #2920 holds an unboarded merge verdict and shares tools/audit/seat/cloud_relay.sh` (HPO_BUS_TRAIN_STATE was unset on this seat, so every merge verdict reads as unboarded). This is a merge-train ordering matter for the orchestrator, not a defect in this diff. Carry: dismissed: train-ordering signal for the orchestrator, not a defect of this diff; re-read at merge time.

## Evidence

- Reviewed head: 172afa85d2bc2f68b402217981f22cfb26e86b56 (ev/HEAD.txt). The PR body names this head, and its ## Head section explains the one record-only commit above the code head 98c6676a8.
- Self-tests at the head (ev/selftests.txt): review_carry 14 checks, 0 failed; cloud_relay 280, 0; bus 94, 0; app_approve 265, 0. These match the body's figures.
- policy_lint: TOTAL 0 error(s) across 50 policy files. fix-review.md is at 140/140 lines and 2449/2451 tokens; orchestrator.md is at 294/295 lines and 4251/4251 tokens. Both are at cap, with no budget file touched.
- Mutation proof re-run (ev/mutants.txt), with every mutant killed: review_carry merge predicate (3 failed); bus.sh refusal branch (1 failed); app_approve first-parent walk (3 failed); app_approve claim-union test (4 failed). That last mutant is my own and is not in the body. The tree was clean after each restore.
- `git merge-tree --write-tree origin/main 172afa85d2bc2f68b402217981f22cfb26e86b56` exits 0, tree e8a0658a2: it merges cleanly.
- VERSION, the manifest version and RELEASE_NOTES.md are untouched against the merge base.
- CI (ev/ci.txt): at read time no gate or pr-contract run had concluded on this head, only prelude, refresh and cancel-superseded jobs, some queued. CI state was not verified green.
- Not re-derived: the body's 377-pure/23-not claim-resolution count over 200 main merges. It is a sliding window, and figure_lint lists it as unverified. I did not re-run it, so it is not verified by me.
- The finder's harness: none is named. This group implements an owner ruling rather than an audit finding, so there is no finder's harness to run at both ends.
