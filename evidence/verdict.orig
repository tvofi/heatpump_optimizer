Fix review: blocked b419463b18a2a7da70c77b23e912769e4af6afe8 root-cause-unanswered: pr-contract went red, unanswered (117865632672: carry_audit BAD-DEST, R10-OPENPR-SILENT is not a group of the tree's roster; it exists only on handoff/audit-r10-roster)

bus-nonce: 17d3fa695dafe988e8ee366c51f929b1
Round: sixth review of #2404, at the same code head as round 5. Round 1 blocked 5cf5786b9 (item-ref over-fire). Round 2 blocked 354c84a96 and round 3 blocked 312f31923 (both mutation-vacuous). Round 4 blocked 03f1681a3 (root-cause-unanswered, a body edit only). Round 5 blocked b419463b1 (carry-missing: R10-TICK-DRIVERS closed under the PR). This round judges round 5's repair: the body edit (PR updated 02:48:14 UTC) and the roster commit 6c891ee6e.
Reviewed head: b419463b18a2a7da70c77b23e912769e4af6afe8 (ev/HEAD; still the PR head when written). Merge base 06c6f3cf2 = origin/main. Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
Evidence: ev/ (this probe ref)

## Block

Round 5's repair holds in substance, and the PR's own gate refuses it.

The substance (step 10) holds:
- R10-OPENPR-SILENT is on origin/handoff/audit-r10-roster (73bb15fe8). Commit 9cdbc67eb adds it, and 6c891ee6e (an ancestor of the branch head) appends the carry (ev/roster.json).
- The group is live. Its `resume.stage` is `in-progress`. Its `files` include `tools/audit/seat/orchestrator_tick.py`. PR #2422 is open at ee93af58a (ev/pr2422.txt), and it does not yet call carry_audit, which is right for a carry whose precondition is this PR merged.
- The carry text names the pass (`carry_audit.py sweep --last N --issues` with both roster refs, and a dispatch line on exit 1). It names the precondition (PR #2404 merged). It names the control: a self-test arm with its null control, where exit 0 prints no dispatch line and exit 1 prints one.
- The body's Forward-carry reads `Carry: R10-OPENPR-SILENT`. `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` gives `6 routed, 0 unrouted, 0 bad`. `--roster-ref 6c891ee6e` gives the same (ev/body_check.txt).

The red (step 11): the pr-contract run 117865632672 started at 02:48:20, after the body edit, and concluded failure. Its last step, the check this PR adds, runs `carry_audit.py check --body` with no `--roster-ref`, so it reads the tree's roster. That roster is main's, because this PR does not touch it. The run logged `BAD-DEST body item 5978f947: R10-OPENPR-SILENT: R10-OPENPR-SILENT is not a group of the roster` and `CARRY-AUDIT: 6 finding item(s): 5 routed, 0 unrouted, 1 bad destination(s)`, then exit 1 (ev/pr-contract-117865632672.log, lines 1766-1772). I reproduce it locally. With no ref, and with `--roster-ref origin/main`, I get the same BAD-DEST (ev/body_check_ci.txt and ev/body_check.txt). `git grep R10-OPENPR-SILENT origin/main -- dev/programme/rosters/` returns nothing. All 51 check runs on the head have concluded: 35 success, 15 skipped, and this 1 failure (ev/check-runs.tsv). This pr-contract run is the last to conclude red, and it checked the current body, so the step-11 posting condition holds. The body's `## Red checks` says "At the current head ... no check run is red". That is no longer true, and the section does not name this run.

Repair, by the fixer and orchestrator, no code change:
- (a) Land the roster's R10-OPENPR-SILENT entry, with its carry, on main through the roster's record path. Then re-run pr-contract, for example on a body edit, so the tree's roster holds the group. Or
- (b) leave the destination as it is and answer the red under `## Red checks`. Name pr-contract 117865632672 and its cause: the destination is on the roster branch and not yet on main. Then state the cheaper-detector answer. That satisfies step 11, but pr-contract stays red until (a) happens anyway.

(a) is the one that turns the PR green.

Note, not a block (an instrument finding, the mirror of the body's own Friction item on roster lag): the destination check reads a single roster. CI reads the tree's roster, which lags the roster branch. So a carry to a group newly added on the roster branch refuses until the record lands on main, while a carry to a group merged but not yet marked done passes (round 5). Either check fails on whichever roster lags. The check could read the roster branch as well as the tree, as `sweep` takes two refs. Carry: O10-policy-fixer-md

Note, not a block: with the verdict comments included (`check --comments`, the input the train's pre-flight `findings` step reads), round 3's non-blocking note on M17 (item 7321e737, "Not a block: M17 (`if ds else []` dropped) ...") reads `UNROUTED [non-blocking]`. It was written before the marker existed. Its substance is settled in this diff: the body's Alternatives say the `if ds else []` guard was deleted, and `grep "if ds else" tools/audit/carry_audit.py` at the head is empty. So this is no carry-missing for step 10, because no later stage changes. It will park the PR at a `findings` pre-flight, though, once one runs. The body can route it by reference: `Carry: dismissed: guard deleted in this diff (item 7321e737)`. Carry: dismissed: settled in this diff; the reference-form fix is the fixer's body edit, named here

## Verified

RESULT carry_audit_selftest=144 failed=0; queue_pre_flight_selftest=37 failed=0 (ev/selftest.txt; worktree clean after)
RESULT body_check roster=origin/handoff/audit-r10-roster: "6 routed, 0 unrouted, 0 bad" rc=0; roster=6c891ee6e: same
RESULT body_check roster=tree/origin/main: "5 routed, 0 unrouted, 1 bad" rc=1 (BAD-DEST R10-OPENPR-SILENT), matching CI's pr-contract 117865632672
RESULT body+comments check (roster branch): "9 items, 8 routed, 1 unrouted [non-blocking] 7321e737, 0 bad"
RESULT roster group R10-OPENPR-SILENT: present, stage in-progress, owns orchestrator_tick.py, carry holds the pass, its precondition and its control; #2422 open, unmerged
RESULT check_runs_head=51 concluded: 35 success, 15 skipped, 1 failure (pr-contract 117865632672)
RESULT merge_tree_vs_origin_main=clean (exit 0; origin/main 06c6f3cf2 = merge base)
RESULT version_manifest_notes=untouched (code head unchanged since round 5)

- Step 12 and #1667: the head is unchanged since round 5, and so is the code head (6f20f78a3). Round 5's code measurements stand: the drive (152 sites, 0 unmapped, 190 mutants, 0 survived), the self-tests and the resolution delta. I re-took the two self-tests. I did not re-run the drive or the heavy figures. CI is green on them at this head.
- Step 9: the fixer's instruments (r10_carry_parser_mutants.py, r10_carry_sweep_rows.py) are disclosed as such. The round-10 sweep still has no committed finder harness.
- Step 10: the second Forward-carry item and the Friction items route to O10-policy-fixer-md. It is out of tree and UNVERIFIED here, as the PR says.
- The round-6 dispatch named the instrument note as a Friction item carried to O10-policy-fixer-md. It is present (body item 9fba80da, "the destination check reads the roster's stage, which lags a merge").
