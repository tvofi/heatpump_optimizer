Fix review: merge 31e0bab01a714bf949cb99efce04dab19c44563b

bus-nonce: 66ccbf7352f24fb43b6ce3529110ba2a

## Summary

This is the fifth fix review of #3085 (R10-CLOSEOUT-CLEANUP) and round 9 of the repair seat. The coordinator ruled it the last round. I measured head 31e0bab01a714bf949cb99efce04dab19c44563b from a detached worktree at that SHA. Its tree a85e770d is identical to 5a8fd981, the merge of handoff 7f80e2dc with origin/main 499162c8.

The class C orphaned-seat `rm -rf` is now leased. The reviewer's class C harness reads race lost=0 and null 0 at the head, and lost=1 at 5aae1e12 and at a45cf7f5. My own attached-orphan variant gives the same result. The hoist changes no class A, B or C outcome except the one intended. All 28 mutants are killed. This review found no code defect, so no split is named.

CI on this head is RED. Every red comes from a cancellation or is main's; none is an assertion this diff causes. See Evidence; the gate needs a re-run before the merge train can merge.

## Evidence

- Round: fifth review (rounds 1-4 were reviews; this is round 9 of the repair seat). fix-review.md is current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Head: 31e0bab0 = merge(5aae1e12, 5a8fd981). `git rev-parse 5a8fd981^{tree} 31e0bab0^{tree}` gives a85e770d for both. The body's `## Head` names 31e0bab0.
- Merge with current origin/main 7c274274: `git merge-tree --write-tree origin/main 31e0bab0` exits 0. `LEDGER-MERGE: resolved tests/closures.json`, and no claim-file conflict (ev/merge-tree.txt).
- Re-cut diff (5aae1e12..7f80e2dc, non-merge commits b1320783 and 7f80e2dc): 3 files, +50 -6, as the brief states (ev/recut.diff).
- Reviewer's class C harness: ev/wtgc-classC-orphan-race.sh, from probe/rev-3085-07a1b8ac, sha1 d297bfe672021d02e28fc5bfbb5b68d39ad23221, run unchanged (ev/classC-race.txt):
  - head: `RESULT race=1 orphan-detached-moved-head-lost=0`, with `FAILED to remove .../seat-a: its HEAD is no longer <read sha>, kept` and the seat wt present. Null: `RESULT race=0 ...lost=0`, seat removed.
  - 5aae1e12: race `lost=1`, null `lost=0`.
  - a45cf7f5: race `lost=1`, null `lost=0`.
  - mutant worktree_gc-6 on the head: race `lost=1`, null `lost=0`.
- Reviewer-built harness, disclosed as mine: ev/wtgc-classC-attached-race.sh. It is an ATTACHED orphan on branch fix/x with a gh stub that reads the PR as MERGED, and the seat commits right after `unpushed_of`'s rev-list, which is the last read before the lease (ev/classC-attached-race.txt):
  - head: race `lost=0` (lease refused, seat kept), null `lost=0` (removed).
  - 5aae1e12: race `lost=1`, null 0.
  - mutant 6: race `lost=1`, null 0.
  - The body's git 2.43 claim holds on real git: a stale old value on a symbolic HEAD is refused (`is at X but expected Y`), and a fresh one deletes .git/HEAD while refs/heads/main stays.
- Hoist judged against old code, case by case:
  - abbrev-ref fails (no git, or a broken gitfile): wt_branch is empty, ohead is empty, and the seat is removed unleased as before (the pruned class).
  - Unborn branch: abbrev-ref returns rc 128 and prints `HEAD`. Old code keeps it as `unmerged-head`. New code reaches `head_is_merged_ancestor ""`, which is false, so it also keeps it as `unmerged-head`. No change.
  - Attached or detached with HEAD unresolvable after a good abbrev-ref: new code keeps it as `unreadable-head`. Old code kept it as `unpushed` (`unpushed_of` prints `?`) or as `unmerged-head`. Only the label changes.
  - Every other case reaches the same branch and detached decisions, and the removal now takes the lease first. Classes A and B are untouched by these commits.
- Self-tests at the head (ev/selftests.txt):
  - `worktree_gc self-test: 105 checks, 0 failed`
  - `closeout self-test: 28 checks, 0 failed`
  - `SELF-TEST PASS (74 checks)`
- Named mutant worktree_gc-6, applied by hand (ev/mutant6-selftest.txt): `105 checks, 3 failed`. The three rows are exactly the body's: the class C lease row, "orphan with a merged branch: removed" and "null control: the unmoved detached orphan in the same run is removed". The restored null gives `105 checks, 0 failed`. As the body discloses, the stub kills the mutant through its lease-argument row, and real git kills it through the moved-HEAD race (above).
- Reviewer's own extra mutants:
  - Dropping the lease block is KILLED: 3 failed, including "the orphaned seat whose HEAD moved is kept".
  - Leasing only the detached arm is KILLED: 1 failed.
  - Dropping the `unreadable-head` keep SURVIVES (0 failed). This is an equivalent mutant: with ohead empty, the attached arm is still kept as `unpushed` (`?`) and the detached arm as `unmerged-head`, so the seat never reaches the rm -rf except through a race between two git reads. The keep is defensive and redundant, and the body claims no test for it. This is not a defect.
- Mutant driver, the body's exact 28-id command run at the head (ev/mutants.txt): `M0: 0 seat step(s) red`, all 28 KILLED, `RESULT survivors=0`, rc 0. Every per-mutant count matches the body: worktree_gc-1..6 failed 5, 2, 2, 3, 17 and 3 of 105; closeout-1..4 failed 6, 5, 1 and 2 of 28.
- Class sweep, the body's grep over worktree_gc.sh and closeout.py less comments and self-test sections (ev/class-sweep.txt). Production sites at the head, which were :636, :673/:678, :727, :833 and :884 at 5aae1e12. Each body disposition is TRUE:
  - :662 `dispose_seat_dir` rm -rf: callers are :759 and :788, classes A and B only, each after `remove_worktree ... || return 0`. Out of class.
  - :699/:704 `remove_worktree` lease, then rm -rf: closed.
  - :753 class A leased branch delete: closed.
  - :869/:873 class C lease, then rm -rf: closed (this round).
  - :924 class D venv: out of class.
  - closeout.py :265 and :283 are leased. :320-321 is the `--orch-root` sweep, disposed with its stated limit. :618 and :711 lie inside `self_test()` (:442-:719).
  - The sweep returns no other site.
- Cheap checks at the head:
  - `STRUCTURE RATCHET PASSED`.
  - `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - Claim files are byte-identical to the merge base.
  - VERSION, manifest and RELEASE_NOTES.md are not in the three-dot diff (ev/three-dot-files.txt).
  - Scoped scripts: `ALL 2616 ENTITY CHECKS PASSED` and `ALL 112 HARNESS HEADER CHECKS PASSED` (ev/scoped-scripts.txt).
  - Re-read before return: `refs/pull/3085/head` is 31e0bab01a714bf949cb99efce04dab19c44563b.
- CI at this head, all 68 check runs read (ev/check-runs.tsv). `merge_train.py classify` gives `RED 31e0bab0... pending: none red: gate` (rc 1, ev/ci-classify.txt). The concluded non-green runs:
  - `gate` 127035819504, failure: `FAIL tests / fast (3.14): cancelled (run 41957409301)`; `tests / closures` and `codeql / Analyze (python)` were also cancelled (ev/gate-failure.txt).
  - CI code run 41957409301 was cancelled from outside at 03:42Z, and every in-flight job stopped in the same second: fast, closures, coverage, instrument-self-tests, codeql, lane-proofs, ratchets and autofixes. No assertion failed. The jobs that completed are success: mutation, typing, policy-docs, wave-script, env-matrix, closure-scope, hassfest and hacs. The two earlier `gate` runs were cancelled (127032284460, 127034469391).
  - `tests / nightly-status` 127019738795, failure. The log reads `NIGHTLY FAILED: record-autofix failed in the last verification dispatch`, dispatched run 41912550258, head 62f94f3. It is main's nightly and pinned at 499162c8. This diff does not reach what it reads.
  - `governance / delivery-status` 127019738698, failure: `OVERDUE ... 4 overdue`, on main's rows #3174, #3091, #3089 and #3192. Row #3085 is not among them, so it is not this PR's.
  - `CodeQL` is neutral.
- The body's `## Red checks` names `gate`, `tests / nightly-status` and `governance / delivery-status` by exact name, and answers each as a cancellation, main's nightly and main's rows. The trigger is answered. Its details were read at 5aae1e12, not at this head; see Findings.
- Forward-carry: the body routes the prune_refs archive-tag re-plan block to #2727 (`Carry: #2727`). carry_audit counts it as routed. #2727's body and comments do not yet state it; see Findings.
- Figures I could not re-derive: none of the code figures. The body's prepr.sh run and its counts (486 self-tests, FIGURES and CARRY-AUDIT lines) were not re-run, since that run belongs to the fixer and is heavy. The packet's own figure_lint and carry_audit at the head agree: `FIGURES: 12 resolved, 4 not verified, 0 refused`, and 1 routed carry.

## Findings

- The body's `## Red checks` still reads "The PR head is still 5aae1e12" and quotes that head's runs. At 31e0bab0, `gate` failed on the cancelled CI code run 41957409301. `tests / nightly-status` now fails for a different cause: record-autofix in dispatch 41912550258, not the `slow` lane the body cites. `governance / delivery-status` is red on main's overdue rows, where the body says `success` for 5aae1e12. The body must be re-read at this head, and CI code re-run to GREEN, before the merge train merges. This is the orchestrator's body update, not a code change. Carry: dismissed: answered in this PR's body by the orchestrator before merge, not a later stage
- The prune_refs `archive/<name>` tag that blocks a re-plan after a lease refusal (the body's `## Forward-carry`) is routed to #2727 only through the body's `Carry: #2727` line. #2727's own body and comments do not state it yet. The orchestrator should write it into #2727, or into the group's roster carry, with its control, before this group is set done. Carry: #2727

## Friction

- The exported harness takes `<worktree_gc.sh>` but `cd`s into its temp repo, so a relative path reads as rc 127 (missing script) and still prints `lost=0`. My first run fell into this and had to be re-run with absolute paths. A harness that prints a passing RESULT when its target is missing would mislead a careless reader; it should check `gc rc` itself.
