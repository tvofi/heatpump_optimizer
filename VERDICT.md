Fix review: merge e8b0c871c7287f08a63dc63c82e0b59a877a0857

bus-nonce: e3d02c7c645df1e977aaa5a89e7366d9

## Head

Round 3, final. Measured `e8b0c871c7287f08a63dc63c82e0b59a877a0857` in the
orchestrator's recarry tree at `~/.local/state/hpo/pr/upd-handoff-r10-plan-opt`;
the live head is re-read before posting. PR #2517, origin/main `e4d47457b`, merge
base `990e90af` (three-dot). The head moved twice under the review — `2275ba66`
(the earliest-attempt commit), `b8558f0d` (the mutation harness's null control
and target), and `e8b0c871c` (the recarry of main plus
`dev/programme/delivery/2517.md`) — and each move is a resolution delta I
measured: the plan bytes at `e8b0c871c` are **byte-identical** to `b8558f0d`, and
the body's `## Head` names the final head.

## The two findings from the held rounds are resolved

- **CI dedupe (was blocked).** At the file's own `measured_at` 17:53:14Z, the
  earliest-`started_at` rule reproduces every committed value and the body's
  figures: fast n=29 / 55.2 / [41.2, 56.7]; closures n=30 / 28.35→28.4 /
  [21.7, 30.1], the `0c298f6b` rerun (22.1, listed first) dropped and its first
  attempt (29.4) kept; Analyze n=30 / 27.15→27.1 / [21.5, 27.9], 2 cancelled,
  0.067; 29 complete triples. Gate = 55.2 + 28.4 + 27.1×1.067 = 112.5157 → 112.5;
  51 runs = 44 batches + 7 stamps → 5737.5.
- **Mutation harness (was blocked).** The harness now copies `durations.json`
  beside the copy, asserts the unmutated copy exits 0, assembles its anchors at
  run time so the table is not self-matched, and scopes each deletion to its
  function. My independent audit reproduces the null control (rc 0) and all six
  deletions (earliest-attempt, coordinator-cap, dispatch-order, stamp-cadence,
  ci-formula, gate-cancellation) exiting 1. The self-test prints 32 `ok`, as the
  body now says.

## The brief, item by item

1. Confirmed: closure `2026-10-30T03:17Z`, wall 226.2833 h, 44 batches, 7
   stamps, 5737.5 CI minutes; chain 13577 min over 12 links; wall == chain. Seven
   groups wait off-path (max 2539 min), none on the critical path, so the
   equality holds; "no queueing" is true of the closure. `--batch-window-minutes
   20`/`120` print 228.28/238.28 h, 44 batches.
2. Confirmed: three live coordinator groups against cap 2, `exceeds_cap true`;
   deleting `generated.inherited_coordinator` exits 1; the inherited inversion
   record is empty, a planted one is recorded and passes, deleting it exits 1;
   the six inherited groups are the top six live by height.
3. Confirmed: over-cap exit 1, cycle exit 2, ahead-of-dependency recorded rc 0
   then unrecorded rc 1, two builds byte-identical.
4. Confirmed: the corrected medians and n, as above.
5. Confirmed: `closure.is_inert` true for `tools/plan/replan.py` and
   `durations.json`; `tools/plan/` in `INERT` and `_INERT_TOOL_HOMES`; in no
   recorded closure; no gate script opens it.
6. `carry_audit` 0 unrouted; `figure_lint` 3 resolved, 0 refused; `preflight`
   clean; `tmp_paths` and `agreement` rc 0; `policy_lint --pr-body` at this head
   0 errors. At 17:53:14Z exactly one PR was open, #2510 (17:19:57–18:20:45);
   #2491 merged 17:19:19. The Forward-carry bullets name the retired documents
   in prose, not as paths.
7. `plan.json` carries the fields the renderer draws; there is no in-tree
   `--check` staleness guard — the body places the refusal in the out-of-tree
   renderer, which the tree cannot show. `VERSION` 7.0.2, the manifest and the
   notes heading are untouched; no claim or golden file moved; `merge-tree
   --write-tree origin/main` is clean and origin/main is the merge base.
   At the live head `pr-contract` is **success** (runs 21:22:59 and 21:23:27,
   the later after the push, both green) and `delivery-status` is success (the
   row landed). `nightly-status` is main's red, not this diff's; the heavy
   checks (`fast`, `closures`, `Analyze (python)`, `browser`, `coverage`,
   `instrument-self-tests`) were still running when measured — CI is their
   authority, not a local re-run.

## RESULT lines

RESULT schedule closure=2026-10-30T03:17:00Z wall_h=226.2833 chain_min=13577 links=12 batches=44 stamps=7 gate=112.5 ci_51=5737.5
RESULT ci_window@17:53:14 fast n=29 55.2 [41.2,56.7]; closures n=30 28.35->28.4 [21.7,30.1]; analyze n=30 27.15->27.1 [21.5,27.9] 2 cancelled 0.067; samples=29
RESULT ci_duplicate 0c298f6b earliest=29.4 kept, rerun=22.1 dropped
RESULT mutation_harness null_control rc=0; six_deletions rc=1 each; self_test_ok=32
RESULT queueing wall_eq_chain=True off_path_waits=7 max_wait_min=2539 on_critical_path=0
RESULT inherited_coordinator groups=3 cap=2 exceeds=True; inherited=6 top6_by_height=same
RESULT refusals overcap=1 cycle=2 ahead_recorded=0 ahead_unrecorded=1 two_builds_byte_identical=True
RESULT classification is_inert(replan.py)=True is_inert(durations.json)=True INERT=True entities_home=True closures.json=False
RESULT head_delta plan_e8b0c871c_byte_identical_to_b8558f0d=True; delivery_row_present=True; body_head_matches=True
RESULT checks pr_contract=success delivery_status=success nightly_status=main_red heavy=in_progress_at_measure
RESULT merge_tree rc=0 vs origin/main e4d47457b; VERSION 7.0.2 unchanged; claims-only ok
