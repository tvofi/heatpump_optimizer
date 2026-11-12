# BLOCKED: r10-advisor-steady-start, round 4

Question: tools/pr/prepr.sh refuses the head at its push-order step and names one repair, a merge of origin/fix/r10-advisor-steady-start (143279b4f, the bot's merge of main). The brief allows a merge only when `git merge-tree --write-tree origin/main HEAD` conflicts, and it reports none against origin/main and none against that branch. Does this seat merge that branch and hand off at the merge commit, or does the relay take the unmerged head as it stands?

## The refusal, verbatim

```
  REFUSE   push order             origin/fix/r10-advisor-steady-start and HEAD have diverged, 138 commit(s) there against 4 here: the push is refused as a non-fast-forward and the force-push past it is forbidden -- merge origin/fix/r10-advisor-steady-start, then rewrite `## Head` at the merge commit
PRE-PR: af7646a863459218148893e15e3fcfa91ccea412 00000000000000000000000000000001 rc=1
```

It is the run's one refusal: 34 steps `ok` (`pr-body` with 0 errors among them), 7 `skip`. The skips that are not empty-handed: `unpinned sites` (`the diff adds no unpinned mutation site`); `diff mutants` (`MUTANT_CMD unset`: this seat did not set it, so the 40-mutant draw of fixer.md step 2 did not run; the mutants run are the body's); `closures` (`the diff cannot be scoped, so CI re-records every closure`); `ancestry reds` (`the check runs at 14f227c5bd0eb80855b21055cc668857a5f820b4 could not be read, so the ancestry reds are UNCHECKED this run, not confirmed empty`).

## State

- Code: af7646a863459218148893e15e3fcfa91ccea412, four commits on 737823acd1b143311e19d4b8ac5066100d136ccc, no merge; this ref's tip is its tree with this file added. refs/heads/handoff/r10-advisor-steady-start is still 737823acd and refs/heads/handoff-body/r10-advisor-steady-start still 07985b131: neither was pushed, because no head passed prepr.
- Body: the draft for af7646a86 is BODY.md on refs/heads/handoff-wip/r10-advisor-steady-start-body. body_push.sh was not run.
- The ruling is built: `price_tiles.take` holds the cap tile to a six-hour clock that a coordinator's first cap turn starts without solving; the fuse advisor is unchanged, its pair already inside its weekly gate (the body says where that leaves the ruling's wording). `PYTHONPATH=tests/hastub python3 tests/replay.py` on this container, the owner fixture's `cycle_cost`: `cpu_ratio` 420.1 `FAIL` at 737823acd; 257.2 and 269.3, `ok`, in two runs at db60ef2df, which differs from the head by two literals of one check and the ledger rows. Each run's one red is the synthetic fixture's loop figure, red at 737823acd and at 61afd4f2d on this box as well.

## What a merge would bring, measured on the merge this seat made and took back out

- Self-correction: this seat merged origin/fix/r10-advisor-steady-start (32b0ddfde) on prepr's word, drove the pins and one replay on that tree, then saw the brief did not allow it and removed the merge. This ref's history holds that merged tree at 1df5f08ad; its tip does not. Nothing else was pushed with it.
- On that merged tree prepr's ancestry step could read the pull request's checks and refused the body for `tests / briefs`, red at 143279b4f (job 131107413262): `LEGACY-CONTROL VACUOUS: carry-1412.json: its controls lint clean without the exemption: remove it from LEGACY_CONTROL_FILES`. `node tools/policy/brief_lint.mjs` exits 1 with that line on the merged tree and 0 at fefd58c898 and at af7646a86; dev/archive/carries/carry-1412.json and tools/policy/brief_lint.mjs are byte-identical between fefd58c898 and the merged tree, so the cause is something this branch adds that the carry's control cites, not found by this seat. The check is in `merge_train.py owed-reds`, and its named repair edits a pinned grader. It is not answered in the draft body, which describes the unmerged head.
- The pin drive ran on the merged tree (`PIN KILLED: 7 pinned, 0 left unpinned`); the rows are in the head, the two files holding the seven sites are byte-identical between the trees, and each site has a kill measured at the head by hand (the body's Mutation proof). `python3 tools/pr/ci_predict.py` at the head predicts no red and lists no unpinned site.
