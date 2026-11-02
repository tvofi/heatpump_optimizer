R10-CLOSEOUT-CLEANUP, instrument half (Part of #201; issues #2505, #2727, #2728). Lands the closeout instrument and folds in the two fly-ins: `prune_refs.py` (batched push arm, keep guards, `--topic`) and `worktree_gc.sh` (unpushed keep, `on-remote` class). The `--apply` run is the orchestrator's final act and was not run here; merging this sets the group carries-open, not done.

Carry dispositions, every carry of the group's roster entry (dev/programme/rosters/wave-r10-groups.json on handoff/audit-r10-roster), (numbered from 1, in roster order):
- Carry 1 (delete the probe refs for #2654 #2656 #2657): residue-no-pr in `prune_refs.py`'s plan, deleted by the final run; no new rule.
- Carry 2 (the `--apply` run is a separate, last step, the orchestrator's, with step 4 refusing until every open issue but the successor is dispositioned; roster-gated): `closeout.py` refuses while any other group is open, naming each; arms and mutants `closeout-1` and `closeout-2`.
- Carry 3 (folded R10-FLY-PRUNE-REFS, issue 2727): the batched push arm (0 gh calls, tags before deletes, every delete leased at the planned sha and atomic per chunk, null control 2N), the `claude/*`, open-group `design/` and age keeps; its inner carries (dispatch/`brief/` residue, stranded handoff refs) fall to the same plan as archive-delete residue.
- Carry 4 (folded R10-FLY-WORKTREE-GC, issue 2505): the `unpushed` keep on both the classify and apply paths, and the `on-remote` class with its cwd, fetch and lsof controls.
- Carry 5 (s9 script census, `prune_refs.py --topic <t>`): archive-then-delete, refused on a `+` cherry line or an open PR; mutants `prune_refs-5` and `prune_refs-6`.
- Carry 6 (plan-regain study, build the tooling now, run last): the instrument lands here; the `--apply` run is not made.
- Carry 7 (s9 local cleanup: worktree_gc "eligible 0, kept 131" at 7.8 GiB free): not built here. It needs a seat-branch to PR-topic mapping read from the live PR list, a configurable seats root and a class for plain repo copies with no `.git`. Its text, failing test and null control already sit as `carry[6]` of this group on handoff/audit-r10-roster, which is where it is routed. It is not re-filed under `#2505`, which two live groups list. It stays pending there, so the group cannot be set done while carry[6] is neither built nor re-carried (`carry_audit.py roster` reads a pending carry on a done group as STRANDED).
- The review's two findings: the moved-ref arm, its mutant and the closeout step-2 re-run are built in this diff (`## Mutation proof`), and carry 7 is the line above.

Design notes: `--topic`'s `git cherry` refusal covers `handoff/` code refs only, since body and dispatch refs are orphan commits that always carry a `+`; local branches holding commits no remote or tag has are never deleted.

Repair round for the first review (`Fix review: blocked 7f95f9084b42aa5bd651a9aa98cc5b4292adcaaa`, verdict/3085 at 4c0fc0af): `prune_refs.apply_plan_push` deleted a ref that moved after the plan read it, leaving the new tip archived nowhere. The class is closed at every delete site the two files hold (enumeration and dispositions in `## Figures`):
- `apply_plan_push` (the default `--via push` arm; `--apply`, `--topic --apply`, and `closeout.py` step 2 all call it): each delete chunk is pushed `--atomic` with one `--force-with-lease=refs/heads/<name>:<planned sha>` per ref. A ref that moved is not deleted, its chunk is refused whole (`delete-FAILED`) and the rest aborts, as the arm already does on a refusal. The ref survives at its new tip, so no tip is ever deleted unarchived, and the docstring and `closeout.py`'s header still hold.
- `apply_plan` (`--via api`): the REST DELETE has no precondition, so each delete first reads the ref (`gh api repos/<repo>/git/ref/heads/<name>`) and stops on a ref not at the planned sha. The race narrows to one request round-trip; it cannot close it, and the docstring says so. The arm also now stops on its first refused write, so a failed tag is never followed by its delete (before this, it continued).
- `closeout.py` step 3, local branches: deleted by `update-ref -d refs/heads/<b> <sha>` at the sha `rev-list --not --remotes --tags` proved pushed, the local lease, in place of `branch -D`. A branch another process moved since is kept as `moved`.

## Head

`2f5cd4188618cccf0d2a76e3df6d31ac59a1c706`: one commit on the PR head 7f95f9084b42aa5bd651a9aa98cc5b4292adcaaa (a fast-forward of handoff/r10-closeout-cleanup at e80cdedb). origin/main moved to 871a20da138592ac892f4652a4f82992a6626783 (read 2026-11-02T19:34Z; it was 38dcb6c5 when the final prepr.sh run started) after the head's merge base ea59e9a09; `git merge-tree --write-tree origin/main HEAD` reports no conflict (a set-merge of tests/closures.json by the ledger driver only), so the branch is not merged (brief and fixer.md step 6). `tools/pr/prepr.sh <body>` was run at this head against that main, with no skip flag set, and ended rc=0 against 38dcb6c5. Main's later move to 871a20da is conflict-free by the same merge-tree read, so under the brief's merge-only-on-conflict rule the head is not re-cut for it. Its `closures` step printed `skip` on its own ("the diff cannot be scoped, so CI re-records every closure; a full derive here is forbidden").

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 closeout-1 closeout-2 closeout-3 prune_refs-1 prune_refs-2 prune_refs-3 prune_refs-4 prune_refs-5 prune_refs-6 prune_refs-7 prune_refs-8 prune_refs-9 prune_refs-10 worktree_gc-1 worktree_gc-2 worktree_gc-3` -> M0 `0 seat step(s) red`, every mutant KILLED, `RESULT survivors=0`. The five new mutants, each against a production line outside the self-test:
- `prune_refs-7` drops the `--force-with-lease` refspecs: red on "a ref moved after the plan read is not deleted: delete-FAILED, its new tip stays" (plus the atomic arm, which then has no lease to fail).
- `prune_refs-8` drops `--atomic`: red on "the moved ref's chunk is refused whole (atomic): its unmoved partner stays too".
- `prune_refs-9` drops the api arm's sha compare (keeps the read): red on "gh-api arm: a ref read at another sha than planned is not deleted".
- `prune_refs-10` drops the api arm's abort on a refused write: red on "gh-api arm: a refused tag aborts before any read or delete".
- `closeout-3` drops the old value from `update-ref -d`: `closeout self-test: 26 checks, 1 failed` ("step 3: a local branch moved after the read is not deleted").
The eleven existing mutants (closeout-1, -2, prune_refs-1..6, worktree_gc-1..3) stay KILLED.

Failing first: with the new arms and the old production code, `prune_refs.py --self-test` failed the five new non-null arms, and `closeout.py --self-test` read `26 checks, 3 failed` (step 2 moved ref, step 3 moved branch, and the step-3 null, which failed because the old `branch -D` had already deleted the moved branch).

## Null control

- Finder's harness, null arm (the plan taken at the live tip; `lease-null.py` is ev/lease-race.py with the planned sha set to the live tip, sha1 below): `RESULT null-plan-at-live-tip moved-tip-deleted-untagged=0` before and after. After the fix the ref is still archived at its tip and deleted (`heads: (none)`, tag at the live tip). The lease does not block an unmoved ref.
- Self-test: "null: the unmoved ref, planned alone at its live tip, archives and deletes" (push arm, leased); "null control: the gh-api arm makes 2N writes (and N reads) for N unmoved refs"; closeout "null: the same branch at the sha read is deleted"; and the existing closeout arms "the deleted refs are gone from the remote" and "every tag precedes every delete" run step 2 through the leased deletes on unmoved refs.
- CodeQL alert 49's fix (`_write_stub`, `O_EXCL` at 0o700) and its self-test with the 0o755 null are kept; the gh stub now also answers a ref read with `GH_STUB_SHA`.

## Figures

- Finder's harness at both ends, from the verdict's export (`git archive origin/verdict/3085 evidence | tar -x -C $EXPORT`), run from the worktree root: `python3 $EXPORT/evidence/lease-race.py` (sha1 1bd5a9518656b7b017cc6860da51efbaf2457aa6). At 7f95f9084b42aa5bd651a9aa98cc5b4292adcaaa it printed `RESULT moved-tip-deleted-untagged=1`. At 2f5cd4188618cccf0d2a76e3df6d31ac59a1c706 it printed `delete-FAILED ... atomic push failed`, `heads:` fix/x at the moved tip, `RESULT moved-tip-deleted-untagged=0`.
- `python3 -I tools/audit/seat/prune_refs.py --self-test` -> SELF-TEST PASS (74 checks); the number is the passing-check count the script prints (69 before; +5 arms, one null control rewritten).
- `python3 -I tools/audit/seat/closeout.py --self-test` -> 26 checks, 0 failed (23 before; +3).
- `bash tools/audit/worktree_gc.sh --self-test` -> 91 checks, 0 failed (unchanged; run inside M0).
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> 0 index gaps.
- The class enumeration, every delete site in the two files: `grep -nE '"--delete"|"-X", "DELETE"|"branch", "-D"|"update-ref", "-d"|"worktree", "remove"|rmtree\(|\.unlink\(\)' tools/audit/seat/prune_refs.py tools/audit/seat/closeout.py`, less the lines inside `self_test`/`_self_test_*`, with every caller of the two apply arms from `grep -nE "apply_plan(_push)?\(" ...`. Dispositions:
  - prune_refs `--delete` push in `apply_plan_push`: closed in this diff (lease + atomic). Callers: `main()` for `--apply` and `--topic --apply` (both funnel through `args.via`), and `closeout.step_refs` (step 2).
  - prune_refs `-X DELETE` in `apply_plan`: closed to one round-trip in this diff (read-and-compare, abort). Caller: `main()` with `--via api`. The REST endpoint offers no precondition, so this is the limit for that arm.
  - closeout `update-ref -d` (was `branch -D`), step 3: closed in this diff (old-value delete).
  - closeout `worktree remove --force`, step 3: deletes no ref. The worktree's branch ref and its commits survive the removal, and step 3's branch loop then judges that branch by the leased rule. Out of class (it is a working-tree removal, not a ref delete).
  - closeout `rmtree`/`unlink` of orchestrator scratch, step 3: no ref. Out of class.
- `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED, no budget file touched.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (tests/entities.py, tests/harness_headers.py), both run with `PYTHONPATH=tests/hastub`, rc 0.

## Red checks

Reds at earlier heads of this PR (1be96319; the whole check-run set read then, all pages), each repaired before 7f95f908, which concluded none red:
- `governance / instrument-self-tests`: failure at 1be96319, on self-test 69, the `prune_refs.py` gh stub test. Repaired in fc47684e. Cheaper detector: `prune_refs.py --self-test`, which runs locally and on every prepr.sh path that names the file. At this head it reads SELF-TEST PASS (74 checks), inside M0's `0 seat step(s) red`.
- `pr-contract / pr-contract` and `gate`: failures at 1be96319. pr-contract refused a stale body that named the old code head, and `gate` failed on those required checks and on the self-test above. Both followed from the body retake. The cheaper detector is `tools/pr/prepr.sh --body-check`, rc 0 on this body.
- `CodeQL`: red at an earlier head of this PR (1be96319), with open `code-scanning alert 49 (py/overly-permissive-file)`. The self-test wrote its `gh` stub by `open()` and then `os.chmod(..., 0o700)`. fc47684e creates the stub exclusively at 0o700 via `os.open(..., O_EXCL, mode)` (`_write_stub`), with no chmod. The self-test asserts the group/other bits are clear (`_wide_bits`), with a 0o755 null, and that fix is kept unchanged here. The PR-level `CodeQL` run concluded success at 7f95f9084b42aa5bd651a9aa98cc5b4292adcaaa (verdict/3085 evidence). Cheaper detector: none runs offline, since CodeQL's query is the only one; the local `--self-test` assertion now covers the bits at no standing cost beyond the self-test.

At 2f5cd4188618cccf0d2a76e3df6d31ac59a1c706: no check run exists yet at 2f5cd4188618cccf0d2a76e3df6d31ac59a1c706, because this head is not the PR's until the handoff moves it. The previous head 7f95f9084b42aa5bd651a9aa98cc5b4292adcaaa had no concluded red check (41 runs, all pages, verdict/3085 evidence/checks.txt, `merge_train.py classify` GREEN). The block this repairs was not a CI red, so no cheaper-detector answer is owed. The new self-test arms are now the cheaper detector for the race, and they run in `instrument-self-tests`.

## Forward-carry

- After a lease refusal, the moved ref's archive tag `archive/<name>` already sits at the old sha. A re-plan at the new tip then has its tag push refused (`tag-FAILED`, abort), and the self-test arm "the first refused tag push aborts" shows the mechanism. That is safe, since nothing is deleted, but a re-run stays blocked on that ref until the old tag is retargeted or a per-sha tag name is adopted. It is a `prune_refs.py` defect, and the issue for those, #2727, is held by one live group, this one, since R10-FLY-PRUNE-REFS was folded in. Carry: #2727

## Friction

none
