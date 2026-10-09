# #2066 cop-floor: resume

State: **round 6 handed off** at code head `b511f9dc5b9ee076d3113aaad4b9e296222bbd7c` (branch
`seat/fixer-cop-r6` in `/Users/timmalmstrom/.local/state/hpo/pr/cop-duty-floor/wt`, published to
`handoff/r9-cop-duty-floor`; body on `handoff-body/r9-cop-duty-floor`). Round 5's block was
`root-cause-unanswered` on the mutation lane; round 6 adds the dispositions it named and re-cuts
the body. The PR branch `fix/cop-duty-floor` was **not** pushed -- the orchestrator moves the head.

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
