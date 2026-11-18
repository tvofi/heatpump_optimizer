Fix review: merge fcd576d7e8092e57a3623c776c9bfd87b55407ae

bus-nonce: 872217d4c28be05a74c147bc282228f1

## Round

Round 4 over this PR's review history: rounds 1 and 2 blocked on code, and round 3 (d40c045119) blocked on a merge conflict. This round reviews the delta d40c045119..fcd576d7e8 only (review packet `## Review scope: delta`). The delta changes nothing under custom_components/, so the scope is not widened. fix-review.md is unchanged on main since the merge base; only architect-planner.md and plan-review.md moved.

## Evidence

- Head reviewed: fcd576d7e8092e57a3623c776c9bfd87b55407ae (ev/HEAD.txt), checked out in a detached worktree. The PR body's `## Head` names this SHA.
- Previous verdict's block (tests/layout.json conflict) is resolved. 75b8f26b4c keeps both `product_reads.py` and `leak_detectors.py`. fcd576d7e8 also keeps main's `regret_oracle.py` beside `leak_detectors.py`. The remerge diffs show each glob as the union of both parents (ev/remerge_diffs.txt). `python3 tests/layout.py` rc=0 (ev/layout.txt).
- Merge with main: `git merge-tree --write-tree origin/main fcd576d7e8` exits 0 against origin/main 7ae657e0e2 (ev/merge_tree.txt).
- Delta, as the head's own content: three main-merges plus 1455a5ad97 (the closures repair). The only hand resolutions are tests/layout.json (twice) and b0a8effcd1's three conflicts: tools/audit/seat/gh_calls.py, gh_read.py and shims/seat-gh. In all three each side is kept: the docstring states both rules, both self-test blocks are kept, and the shim keeps the owner-only comment and main's install-fixed `loghome` (ev/remerge_diffs.txt). Self-tests at head: gh_calls `229 checks, 0 failed`; gh_read `176 checks, 0 failed`; owner_only, corpus_mirror, finder_overlap and leak_detectors each `ok (with mutants)`; ref_privacy `132 checks, 0 failed`; fold_ledger rc=0 (ev/st_*.txt).
- Mutant on the merged shim: line 315's `if [ -n "${HPO_OWNER_ONLY:-}" ]` changed to `if false`. `dev/audit/harnesses/owner_only_channel.py` goes from `RESULT arms=49 failed=0` / `OWNER-ONLY CHANNEL HELD` to `failed=2` / `OWNER-ONLY CHANNEL BROKEN: P5 ...` (ev/channel_head.txt, ev/mutant_seatgh_channel.txt): killed. owner_only.py's own self-test does not cover the shim (ev/mutant_seatgh_owner_only.txt, still rc 0); the channel harness holds it, as the body says.
- `python3 -I dev/audit/harnesses/owner_only_mutants.py` at head: `RESULT mutants=54 survived=0`, rc 0 (ev/owner_only_mutants.txt). This re-derives the body's figure, and its shim group runs against the merged shim.
- 1455a5ad97 (ev/1455a5ad97.diff) moves `dev/audit/config/scopes.json` into INERT_EXCEPT and the recorded closure of tests/entities.py, alongside ci_priority.json. The live `tests / closures` and `tests / closure-scope` checks are green at this head, so I cite CI rather than re-recording.
- Round 3 deferred two findings to this round; I checked both at head with targeted mutants.
  - owner_only.py:250: `rc != 1 or NO_LOGIN not in out + err` mutated to `rc not in (1,)`. The self-test goes red (rc=1, the two exit-1 gh arms FAIL; ev/mutant_owner_only_gh_rc.txt): killed.
  - corpus_mirror.py safe_extract: the host-write failure mutated so it returns a rule instead of raising. Three arms go red, `a write this host fails is raised` and both `local failure` arms (rc=1; ev/mutant_corpus_write.txt): killed.
  - Both mutants were restored, and the worktree is clean.
- CI: `merge_train.py classify fcd576d7e8092e57a3623c776c9bfd87b55407ae --pr 3679` printed `GREEN fcd576d7e8092e57a3623c776c9bfd87b55407ae pending: none red: none`, rc 0 (ev/classify.txt). No owed red exists. The packet's `tests / nightly-status` failure is not in the owed-reds set, so it is neither answered nor a block.
- VERSION, the manifest and RELEASE_NOTES.md are untouched by the PR's diff against the merge base 91674d15cd.
- Closing self-audit: `carry_audit.py check` over this verdict, with a stub body, rc 0, `0 finding item(s)` (ev/carry_audit_verdict.txt). The body's own items are audited in the review packet at this head: `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`.
- Figures I could not re-derive: F3–F7 (the scan's measured cost). The body states that they are not measured and why, and Carry 2 routes them.

## Findings

none
