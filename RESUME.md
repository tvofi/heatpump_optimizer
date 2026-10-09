# #2066 cop-floor: resume

State: **round 9 (update-branch) handed off** at code head `386b7e2ff79821a91ae5c4bc95afca9b150b7b9d`
in `/Users/timmalmstrom/.local/state/hpo/pr/upd-fix-cop-duty-floor` (branch `fix/cop-duty-floor`
merged to `origin/main d8a4bd36f`), published to `handoff/r9-cop-duty-floor`; body
`body/BODY-r9.md` on `handoff-body/r9-cop-duty-floor`. Round 8 blocked on `conflict`; the
resolution is measured, not picked (see the PR body "What round 9 adds"). `fix/cop-duty-floor`
was NOT pushed -- the orchestrator moves the head.

## Round 9 in one screen
- Live head at start: `d1538a73b` (round 7 head `b511f9dc5` + bot pin `ci: pin killed mutants` x1).
- `git merge origin/main` (twice -- main moved from a8ce87571 to d8a4bd36f mid-work; second merge
  clean). Conflicts: claims.py, deployment_shape.py, features.py. All three re-derived: claims.py
  prints 75/75 (branch draw_range over main flow_meter+entry_config), deployment_shape merged
  census 93/123/18 (rule reproduces the base exactly: 406/120/18/91/81/73/55/20/89/56 --
  `ev/r9/census_full.txt`, `ev/r9/census_final.txt`).
- features.py: both sides' appended blocks kept verbatim; module-scope name check: no collision
  (`coord` collides only in function-local scope, 1003/1093...).
- Silent-agreement sweep caught TWO false-clean docs numbers: architecture.md "74 modules" (both
  sides wrote 74; merged is 75 -- claims C32 turned false until corrected) and "the other 46
  modules HA-free" (main recorded 46 against its 74; merged is 75-28=47, caught by
  `tests/entities.py` "architecture.md's HA-free count is the tree's"). entities then
  ALL 2236 PASSED.
- Ledger: the a3cd4cc3 CMP_BOUND triage's twin sentence corrected (the round-8 FINDING 3:
  "pinned by the round-5 pass" -> pinned by this branch's own d1538a73b against b2b6acd64).
- mutation_table --normalize: 1346 dispositions, 0 retired keys, tree byte-unchanged (ledger is
  anchor-keyed, main line shifts need no re-key).
- Validators all []; structure PASSED (four caps DOWN vs base 153->151,120->118,8818->8808,
  762->760; no raise). Guard pins 50/50. Harness headers 109/109 except h7 memory line which
  fired false once under box load and True standalone (branch touches no D9 file; CI's fast is
  the verdict). features.py 1 of 3948 FAILED = known R9-F2.1 P3 BLAS float (3929+main's 19).
- Counts at this head: unpinned 4615 vs base 4622, added 10 sites / 9 keys, pool 12, shards 2,
  in-pool-not-charged 2 (coordinator.py:4526 6deb0603 CMP+GUARD, main's line re-anchored by
  this PR's rename; r8 drove the CMP arm, survivor). Refusal None.
- prepr rc=0 (`ev/r9/prepr_r9b.log`), PR-BODY 0 errors, ancestry reds answered (40 rows / 5
  names, ev/r9/ancestry_reds.tsv; head census d1538a73b in ev/r9/head_d1538_census.tsv).
- Claim files byte-identical to LIVE origin/main (3d017e611ec1 / 459c54964fa7).

## What round 6 did
1. Merged `origin/main b2b6acd64` (50 commits over the old base) -- merge, not rebase. The
   `tests/closures.json` conflict was resolved to the merge driver's own bytes (verified:
   `git merge-tree --write-tree origin/main 630849897`'s `tests/closures.json` blob `diff`s
   empty against `git show HEAD:tests/closures.json`). Production is untouched by the merge:
   `git diff --stat 16c06fd32 HEAD -- custom_components/` is empty, which is why the acceptance
   rows read the same at both heads (item 4 re-ran the harness to confirm it).
2. Added 12 `features.py` boundary checks (3917 -> 3929 checks; the block is green; the single
   failure at both heads is the known Mac/BLAS `R9-F2.1 P3`).
3. Wrote 25 ledger rows: 20 `killed_by` (all naming `tests/features.py`) + 5 `survivor_triage`
   (4 equivalent, 1 gap). 24 of the 37 charged sites are now disposed; 13 remain and all are
   #2065's lines. `unpinned 4620 <= base 4623`, `ratchet_refusal None`, `added 13`.
4. Re-took the fixer's harness at this head (`dev/audit/harnesses/cop_duty_floor.py`, 31 RESULT
   lines, exit 0, every row identical to round 5's reading) -- it is cheap, so the body quotes a
   re-run rather than a carry. The reviewer's probes carry on the production-identity argument.
5. Re-cut the body (`body/BODY-r6.md`), including the disclosed correction of round 5's false
   "This PR's heads skip that lane" claim about `nightly-ha (stable)`.

## The method that mattered (do not re-derive it blind)
- **Re-derive the charge set** with main's own functions, read-only, 8 s
  (`ev/r6/rederive_unpinned.py`): `inventory`, `unpinned_sites`, `base_unpinned_sites`,
  `diff_sides`, `added_unpinned`, and `new_unpinned` for the pass pool. **`added_unpinned`
  (the lane's charge) and `new_unpinned` (the pins pass's pool) are different sets** -- that is
  why round 5 saw two coordinator survivors in no listing. At this head: 13 added, 16 in pool.
- **Measure a kill without CI**: `ev/r6/verify_kills.py FILE LINE KIND ...` copies the package
  (excluding `__pycache__` -- a copied cache makes the mutant a no-op), rewrites one line to the
  operator's own `new` text, and re-evaluates the 18 conditions in `ev/r6/checks_eval.py`.
  `killed_by` reason text must state that this is a condition measure, not `--pin-killed`.
  The full driver cannot run here: `features.py` is red at baseline on Darwin (BLAS float) and
  `mutation_table` refuses to drive from a red baseline; the container lane is gone since
  2026-10-04.
- **The float facts** every boundary case turns on are in `ev/r6/probe_floats.out`:
  `0.8 x 1.0 == 0.8`, `(1.0-0.15)*10.0 == 8.5`, `0.92-0.8 == 0.15*0.8`, `1.5/5.0 == 0.3`,
  `log(sqrt(e)) == 0.5`, percentile-on-data-point fixtures, and no double `r` with
  `abs(r-1.0) == 0.15` (the equivalent triage at `accuracy.py:703`).

## Where things are
- Worktree `~/.local/state/hpo/pr/cop-duty-floor/wt`, branch `seat/fixer-cop-r6`. The seat's old
  worktree (`hpo-seats/live-cop-floor/wt`, branch `fix/cop-duty-floor-min-power`) and the
  updater's (`.../pr/upd-fix-cop-duty-floor/wt`) are stale; do not build on them.
- Body: `body/BODY-r6.md`. Evidence: `ev/r6/` (unpinned listings, kills tables, local arm logs,
  prepr log, check-run census).
- Stack: still on #2065; #2066 merges after it. #2065's head has moved past the `1e957282e` this
  branch carries, and its ledger already disposes two of the 13 (`draw_range.py:113 CLAMP_DROP`,
  `thermal_model.py:1280 RETURN_DEL`) -- an orchestrator lever, not this seat's call.

## Round 7 (the orchestrator's two refusals, both fixed)
The first handoff body failed `prepr` at `b511f9dc5` on two arms. Neither needed a code change.
1. **`ancestry reds` REFUSED** (`briefs fast (3.14) mutation nightly-ha (stable) nightly-status`
   unanswered). The re-cut had dropped `briefs` and `fast (3.14)` because their causes are closed --
   but the arm enumerates every red on every commit of `git rev-list <merge-base>..origin/<head-ref>`
   (39 commits here), so a closed round-4 red still has to be named. Enumerate it yourself with
   `ev/r6/ancestry_reds.sh` (one `gh api --paginate .../commits/<sha>/check-runs` per commit, the
   same jq as prepr's `REDS_JQ`): 37 red rows, 5 names -- mutation 14, nightly-status 12,
   fast (3.14) 7 (3 of them on #2065's commits, which this range carries through the stack),
   briefs 2, nightly-ha (stable) 2. Answer each by name in `## Red checks`; for a red on a
   `#2065` commit, attribute it to that PR and say what you measured here, do not guess its cause.
   NOTE: the step is SKIPPED unless the local branch has a remote head ref -- create one
   (`git branch handoff/<topic> <sha>` + `branch.handoff/<topic>.remote origin`) before you trust
   a local rc=0.
2. **`unpinned sites` WARN counted 11, not 12/13.** Not drift: this head's `predict_line` sed has a
   `(\*[0-9]+)?` group and captures `draw_range.py:125 CMP_BOUND*2`; the pre-merge copy has no such
   group and silently drops that line from the SAME `ci_predict` output. Three instruments, three
   counts, one tree: lane `added_unpinned` 13 sites, `ci_predict` summary 12, step-6d file 12 (new
   sed) or 11 (old sed). The body names the pair in BOTH printed forms so step 7d is disposed under
   either, and states the three counts with their commands. Logged as `prepr-6d: contradiction` in
   `## Friction`.

## Next
1. The orchestrator pushes the head as the App -> that creates the `pull_request` run the pin
   lane needs (`event_name == 'pull_request'` gates all three jobs; a bot `GITHUB_TOKEN` head
   gets only `workflow_dispatch` and no governance contexts at all).
2. If the pass reports a survivor among the 13, it returns here for a disposition; #2065's own
   body owes those rows too.
3. The line-shift recurrence (round 4, twice) is still owed a `root-cause.md` seat; round 6 adds
   a second instance of a related class -- a disposition naming an actor that cannot act.


## Next (unchanged lines, current reading)
1. Orchestrator: App-push this head to `fix/cop-duty-floor` -> pull_request run -> `mutation` reds
   on the 10 added sites + whatever the shards report for the 6deb0603 pair; #2065 must merge first
   for green (all 10 have killed_by rows on its head, verified 9 digests x1 each).
2. The 6deb0603 pair is this branch's disposition to write when the matrix reports it.
3. RCA seats still owed: line-shift recurrence; disposition-naming-an-actor-that-cannot-act
   (partly falsified this round -- the bot CAN act once the pull_request run exists; the standing
   unenforced half is the survivor-triage deferral).
