Fix review: merge 9a3bbaa751b71a9b6c75a4c152b9c96d4f5a92a1

bus-nonce: 564bfe990f0840ed7de1bf08812d8565

## Scope

Delta review of PR #2762 (R10-CONFIG-NOTICES), fixer round r3 (body-only re-issue). The prior `merge` verdict was cut at code head 6e4e274a4afc889228f867b8ac41edd2adc646c8. The head measured here is 9a3bbaa751b71a9b6c75a4c152b9c96d4f5a92a1, which merges origin/main 21a1e04a7 into 6e4e274a. That head was still the PR's head when this verdict was written, with the PR last updated at 2026-10-25T06:58:52Z. Role contract: `dev/governance/roles/fix-review.md` from main, with no change to `dev/governance/roles/` between the merge base and origin/main (0 diff lines). Round: r3, below the fourth-round re-cut.

## Findings

- The body's `## Figures` budget bullet quotes absolute values from the authored head d7017b6 on base 662a3809: `class_excess_loc 18209 -> 18110` and `max_class_loc 8449 -> 8350`. At this head the same command (`git diff $(git merge-base origin/main HEAD)...HEAD -- tests/structure_budgets.json`) prints `18202 -> 18103` and `8442 -> 8343`. Main re-recorded both values (ab00437c9), and the 6e4e274a merge carried the branch delta on top. The delta is identical (-99 each, every row moves down, none up). The body states the figures were not re-taken ("No figure below was re-taken"). No grader refuses it: pr-contract is green at this head, and figure_lint reports 0 refused. The change does not depend on the absolute values. Carry: dismissed: disclosed as measured at d7017b6 on 662a3809; the delta and direction re-derive unchanged at this head; no rule or grader refuses it.

## Block

None.

## Evidence

- (1) The code tree is unchanged from 6e4e274a. I compared the branch's three-dot patch at 6e4e274a (merge base ab00437c9) with the one at this head (merge base 21a1e04a7) after stripping `index` lines: byte-identical, diff rc=0 (`ev/code_delta.txt`). There is no new code hunk; the 9a3bbaa merge brings in only main's files (47 paths, none in the branch's own 12).
- (2) Carry: from a checkout of origin/main 21a1e04a7, with the roster branches fetched as pr-contract fetches them, `python3 -I tools/audit/carry_audit.py check --body <live body>` printed `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc=0 (`ev/carry_audit.txt`). Null control: the same body with the Friction carry set back to `Carry: R10-POLICY-FIXER-MD` printed `BAD-DEST body item bc5348b4: R10-POLICY-FIXER-MD: R10-POLICY-FIXER-MD is done (resume.stage done)` and `CARRY-AUDIT: 1 finding item(s): 0 routed, 0 unrouted, 1 bad destination(s)`, rc=1 (`ev/carry_audit_null.txt`). The instrument moves under its own perturbation.
- (3) Body contract: `pr-contract / pr-contract` concluded success twice at this head (check runs 121112158508 and 121112604014, 07:53-07:56Z). Both ran after every other workflow at the head had concluded; the body was last edited at 06:58:52Z. Locally I ran main's `tools/policy/policy_lint.mjs` with this head and base, the API's commits, and the three-dot paths: `PR-BODY: 0 error(s)`, red-history `record` naming `tests / fast (3.14)`, which the body's `## Red checks` answers. `figure_lint.mjs`: `FIGURES: 7 resolved, 1 not verified, 0 refused`. preflight.sh: `clean no refusal`, with no intended closes. `prepr.sh --version-edit`: no version edit.
- (4) Figures re-derived at this head: `tests/structure.py` printed STRUCTURE RATCHET PASSED and `seam_cut_total = 420`, matching origin/main's 420. The per-seam owned-attribute column differs only for learning (37 -> 36) and grid (27 -> 24), as the body states (`ev/structure_*.txt`). `tools/audit/archscore/score.py --diff 21a1e04a7 HEAD`: `Architecture score: dS +0.0611 IMPROVES` (coord_footprint 2463 -> 2446, coordinator_multiassigned_attrs 114 -> 110), the same as the body's figure at the old base. Null control `--diff 21a1e04a7 21a1e04a7`: `dS +0.0000 NULL`. The budget three-dot moves only class_excess_loc, coordinator_attrs 146 -> 143, coordinator_multiassigned_attrs 114 -> 110, max_class_loc and recorded_at, all downward; `seam_cut_total` is untouched. The absolute values are under Findings.
- Mutation re-proof at this head, using the finder-independent suite the body names (`PYTHONPATH=tests/hastub python3 tests/features.py`, BASH_ENV unset):
  - Baseline: rc=0, `ALL 4374 FEATURE CHECKS PASSED`.
  - `setpoint_check.py:57 if offending is None: -> if False:`: rc=1, 5 of 4374 failed, including "ConfigNotices: a fresh instance (entry reload) still clears the notice" and the "corrected configuration clears" checks.
  - `setpoint_check.py:61 if self._raised.get(issue_id) == offending: -> if False:`: rc=1, 1 of 4374 failed, "ConfigNotices: the same offending value is created once, persistent WARNING".
  - Null mutant (an appended comment line in setpoint_check.py): rc=0, 4374 passed.
  - The worktree was restored clean after each run. I did not re-drive the issues.py and coordinator.py mutants: the code is byte-identical to the previously verdicted head, and those sites are pinned in the ledger.
- Merge: `git merge-tree --write-tree origin/main 9a3bbaa` exit 0, tree 04c4e72be5, which equals this head's own tree. The head already contains origin/main 21a1e04a7. There are no conflicts, and no claim file is touched. GitHub reports mergeable_state `clean`.
- CI at this head, read from the commit's check-runs API: 55 runs, 39 success, 16 skipped, 0 failure (`ev/check-runs-head.txt`). `gate` succeeded twice, `tests / fast (3.14)` succeeded, and `tests / mutation` concluded success. No check is red at this head. The red at 2f5bf7257 (`tests / fast (3.14)`) is named and answered in `## Red checks` with a cheaper detector; policy_lint's red-history recorded it and found it answered.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched (three-dot diff empty; prepr `--version-edit` clean).
- The head named in the body's `## Head` is 9a3bbaa751b71a9b6c75a4c152b9c96d4f5a92a1, the head measured here.

## UNCERTAINTIES

- I did not read the `tests / mutation` lane's log (an anonymous API read cannot fetch job logs), so its green conclusion does not show whether any mutant was evaluated or the run printed INCONCLUSIVE. The branch's production lines are byte-identical to 6e4e274a's, and the two targeted mutants above were killed locally.
- The finder's harness (`dev/audit/rounds/round10/D7/arch2-s2/`) was not re-executed here, as in the body; the architecture score it reads was re-run at both ends with a null control.
- I found no rule in the tree literally named "body-staleness". Brief check (4) was judged against pr-contract (green), figure_lint (0 refused), policy_lint's `## Head` check and fixer.md's re-take rule. The one stale absolute pair is disclosed and dismissed under Findings.
