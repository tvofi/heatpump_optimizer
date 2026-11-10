R10-CARRY-SINK-BARRIER: the owner-approved barrier (tvofi 2026-11-10). A carry goes to the live group owning the seam; where none exists, the producing group keeps the fix. Before this change `carry_audit.py` refused only a destination gone or at a `CARRY_CLOSED` stage, and `roster_edit.py append-carry` and `roster_sync.py carry_plan` accepted any open group, so a carry could be parked on a group whose pull request had already merged (`carries-open`) or on a group created only to receive carries.

This is policy (`finding-propagation.md` changes what a seat must do). It is merged under the mandate and surfaced to tvofi.

The fix is one predicate, `roster_lib.carry_receivable`, read by every destination reader:
- `carry_audit.Dests.live`, which `Dests.check` uses for the group token, for the issue token (`Dests.receiving`, round 2) and for the refusal's valid-target list;
- `roster_edit.py` `append-carry`, `mark-carry moved` and `set-stage absorbed --into`;
- `roster_sync.carry_plan`.

`carry_receivable` refuses two things:
- a stage in the new `roster_lib.CARRY_DEST_CLOSED`, which is `CARRY_CLOSED` plus `carries-open` and `refuted`;
- a receiver-only sink: a group with no `resume.pr`, no `issues`, no `fixes` and a recorded `files` list that is empty.

Every refusal names the rule.

Design choices the reviewer should check:
- **`CARRY_CLOSED` itself is unchanged.** It also decides what a group still *holds* (`stranded`, `legacy_carries`, `roster_report`). A carries-open group must keep holding and discharging its own carries, so the destination set is a separate tuple derived from it.
- **The sink test does not count a brief as work.** All 431 groups on the round roster have a non-empty brief, and `append-group` requires one, so a "no brief" test could never fire on a real group.
- **The sink test keys on `files == []`, not a missing key.** A group with no `files` key has an unrecorded seam, not an empty one. The self-test fixtures that omit the key stay live.
- **No live group on the round roster is a sink today** (harness below), so that arm guards the next sink and takes nothing away now.

Alternatives considered:
- Widening `CARRY_CLOSED` would have stranded every pending carry on the 10 carries-open groups in `carry_audit.py roster`, and changed `set-stage` closing.
- Fixing `carry_audit.py` alone, as the brief scoped it, would have left `append-carry` and `roster_sync` writing the carries the audit then refuses. That route is the one that parked them.

Closes no issue: the group lists none.

## Round 2

Answers verdict/3417 (blocked 34a9cf1251fa6046f3182a21aea60a84b477609f, class-open).

- **The block.** `Dests.check` accepted `Carry: #N` whenever `owns(n)`, and `Dests.__init__` fills `owned` from every `is_open` group, carries-open and refuted included. So a carry refused on the group token passed when re-spelled as the group's issue (#3313, #2728). The round-1 census below misfiled `Dests.__init__` as "issue ownership"; it is also the destination test for `#N`.
- **The fix.** `Dests.__init__` now also builds `receiving`: the issues of every group `Dests.live` (that is, `roster_lib.carry_receivable`) accepts, plus every carry-file issue and every issue an O-brief names. `check` refuses an owned `#N` outside `receiving`, naming the owner, its stage and the rule. There is one rule and no second copy: the issue arm calls the group arm's `self.live`. `owned` and `owns` are unchanged, so `sweep --issues` and `orphaned` behave as before.
  - **A design choice to check:** an issue counts as receivable if *any* open group listing it is live, a carry file owns it, or an O-brief names it. A carries-open group that shares an issue with a live group does not block a carry, because that issue has a live owner.
- **Merge.** origin/main was merged into the handoff (44c77b585, claimnotes driver, no conflict). That brings in #3409/#3410's selftest-closures changes.
- **The reviewer's ci_predict.py finding** (Carry: R10-CARRY-SINK-BARRIER) is in this group's own seam, so it is built here. `ci_predict.self_test` picked the first `is_open` group as the carry destination it predicts green. It now picks with `carry_audit.Dests.live`. Commit a8563e945 restores that line: a mutant-restore race in this seat's own run left the `is_open` mutant in 27a61185f's copy of `ci_predict.py`. The three-dot diff at the head carries the fix.

## Approval

This is a policy change: `dev/governance/rules/finding-propagation.md` and its generated copies. The barrier is owner-approved per the group's brief (tvofi 2026-11-10), which says it merges under the mandate and is surfaced to tvofi. The approval itself is recorded at merge, by one of:
- tvofi's approving review at this head;
- an approving review citing mandate 6329234399 (scope all), if that mandate is in force when it merges.

This seat holds no approval.

## Head

a8563e94535f3838b0f43ff4ce2dfe6645c0fdb0, merge base 04dfcafccdde1ee5df21a02fe4f06a5bc1083ea0 (origin/main at 2026-11-10T11:18:11Z). Round 1 was measured at 22f3ba79a7a6f2832bb37d4bfa97b627459226db and reviewed at 34a9cf1251fa6046f3182a21aea60a84b477609f.

## Mutation proof

Round 2, tree a8563e945 plus each mutant (`carry_audit.py --self-test`, 415 checks; restored after each):
- Failing first: the two new arms, written before the fix, failed against the merged round-1 code. FAIL `sink barrier: a carry to #900, owned only by R10-CO, is refused naming the owner and the rule` and the same for `#901 ... R10-RFT` (2 failed of 415).
- M1, the issue-token predicate `if n not in self.receiving` changed to `if False`: the same 2 FAIL, rc 1.
- M2, `receiving` filled by `roster_lib.is_open` (the base rule) instead of `self.live`: the same 2 FAIL, rc 1.
- M3, an O-brief's issue not added to `receiving`: 2 FAIL, `an O-brief owns the issues its file name carries` and `sink barrier (null control): a carry to #906 passes, an O-brief names it`, rc 1.
- M4, carry-file issues not in `receiving` (`set()`): 3 FAIL, `an issue with a carry file is a destination`, `... #905 passes, a carry file owns it` and `P43: ... and routes once the head is the extra ref (after)`, rc 1.
- ci_predict.py mutant, the pick back on `roster_lib.is_open`: FAIL `a carry to a live group of the roster is predicted green`, `ci_predict self-test: 1 failed`. With the fix it reads `0 failed`. This mutant is killed only while the in-tree roster's first open group is not receivable. At this merge base that group is R10-PREPR-CAP, at carries-open.

Round 1, each mutant is run against the named file's `--self-test`, then the file is restored.

Tree 1c6a77a6a (before the predicate moved to `roster_lib`):
- `CARRY_DEST_CLOSED = CARRY_CLOSED`: FAIL `sink barrier: a carry to R10-CO / R10-RFS / R10-RFT / R10-SINK is refused, naming the rule and the live targets` (4 failed of 409).
- `Dests.live` reads `CARRY_CLOSED` again: the same 4 FAIL.
- Refusal text without the rule: the same 4 FAIL.
- Sink clause short-circuited to `True`: FAIL `sink barrier: a carry to R10-SINK is refused` (1).

Tree 91ea49295, through `python3 tools/audit/seat/r10_roster_ops_mutants.py` (full run):
- `K10` (mark-carry moved check → `if False`): rc=1, fails=9, first `mark-carry refuses moved to a done group`.
- `W6` (append-carry check → `if False`): rc=1, fails=6, first `append-carry to a done group refuses and writes nothing (carry 3)`.
- `W12` (absorb `--into` check → `if False`): rc=1, fails=3, including `sink barrier: set-stage absorbed --into R9-WC is refused` and `... --into R9-WS is refused`.
- `L7` (new: `CARRY_DEST_CLOSED = CARRY_CLOSED`): rc=1, fails=1, `carry_receivable: carries-open, refuted and every CARRY_CLOSED stage take no carry`.
- `L8` (new: sink clause dropped): rc=1, fails=1, `carry_receivable: a receiver-only sink (no PR, issue or fix; files []) takes none`.
- **`Y6` retired as equivalent** (commit 22f3ba79a). It drops `legacy` from the write path's projection, which only decides a same-pass `Carry:`. Both stages that projection chooses between (done, carries-open) now refuse the carry, and the write path discards the refusal text (`appends, _`). At base: rc=1, fails=1. Here: rc=0, fails=0.

MUTANT-SYNC, tree 22f3ba79a: `roster_sync.carry_plan` reads `is_open` again. `roster_sync.py --self-test`: 2 failed of 96:
- `a destination holding a post-cut-over carry projects carries-open: the dry run refuses the append, naming the stage`;
- `and the write refuses it too and writes carries-open with its own carries only`.

`dev/audit/harnesses/r10_carry_parser_mutants.py`: `L-landed`, `L-words` and `L-source` matched nothing at main (`landed()` was reworded by 67a823c2e) and are re-anchored here. Each is killed: failed=12, 4 and 2, `survived=0`. Its 6 `UNMAPPED` sites are all in `seg_dests`, which this diff does not touch.

## Unpinned sites

`tools/` sites only, each pinned by an in-tree mutant above:
- `roster_lib.carry_receivable`: L7, L8.
- `roster_edit.py` sites: K10, W6, W12.
- `carry_audit.Dests.live`: the four carry_audit mutants above.
- `carry_audit.Dests.__init__` `receiving` and the `Dests.check` issue-token refusal (round 2): M1-M4.
- `ci_predict.self_test`'s pick: the ci_predict mutant (a self-test's own fixture, not a production site).
- `roster_sync.carry_plan`: MUTANT-SYNC below.

## Null control

- Round 2: `sink barrier (null control): a carry to #902 passes, a live group lists it`, `#903 ... a live group also lists it` (shared with a carries-open group), `#905 ... a carry file owns it` and `#906 ... an O-brief names it`. Every issue-token arm that was there before still passes (415 checks, 0 failed). At the live roster, harness `issue_accepted[live]` is the same at both ends (Figures).
- The unmodified base tree accepts a carry to every carries-open group: harness at the base, below.
- The new self-test arms check that a carry to a live group still passes:
  - `sink barrier (null control): a carry to the live group R10-WORK / R10-NEXT / R10-PR still passes`;
  - `carry_receivable (null): live stages take a carry, and so does a group with an empty files list but a PR, an issue or a fix, or no files key`;
  - `append-carry to an open group with no PR appends without a WARN` (unchanged).

## Figures

Round 2 (head a8563e94535f3838b0f43ff4ce2dfe6645c0fdb0):
- Rule for the reviewer's instrument, re-run at both ends: `python3 <rev's tools/audit/carry_audit.py> --roster-ref <ref> check --body <body>`, where the body is one `## Forward-carry` item ending `Carry: <tok>`. Roster refs: 5076c9e6caad07d561929555bba5078a14fde713 (the verdict's) and 2e749ce5f2f2bb756badaa13561b2e7559e91a54 (origin/handoff/audit-r10-roster at this run). Rev 34a9cf125 is the reviewed head; "fix" is this head. Both refs read the same:
  - `R10-REVIEW-ENUMERATE`: rc 1 at both ends (the group token, the round-1 arm).
  - `#3313`: rc 0 at 34a9cf125 (`1 routed`); rc 1 here, `BAD-DEST ... #3313's roster owner R10-REVIEW-ENUMERATE (resume.stage carries-open), which takes no carry; a carry goes to the live group owning the seam, else the producing group keeps the fix`.
  - `R10-CLOSEOUT-CLEANUP`: rc 1 at both ends.
  - `#2728`: rc 0 at 34a9cf125; rc 1 here, owner R10-CLOSEOUT-CLEANUP (carries-open).
- Class census (fixer.md step 8), the issue arm added to `dev/audit/harnesses/r10_carry_sink_barrier.py`. Rule: `Carry: #N` is driven through `Dests.check` for every `n` in `Dests.owned` (every issue an open group lists; no carry file or O-brief), keyed by owner stage, with `live` meaning some `carry_receivable` group lists it. That is every issue a group token's refusal could be re-spelled as.
  - `python3 dev/audit/harnesses/r10_carry_sink_barrier.py 34a9cf1251fa6046f3182a21aea60a84b477609f 2e749ce5f2f2bb756badaa13561b2e7559e91a54`: `RESULT issue_accepted[carries-open]=5 of 5`, `RESULT issue_accepted[live]=23 of 23`.
  - `python3 dev/audit/harnesses/r10_carry_sink_barrier.py 27a61185f446ee15f91024bcd03902c01dab56a9 2e749ce5f2f2bb756badaa13561b2e7559e91a54` (the fix commit; the harness reads only `carry_audit.py` and `roster_lib.py`, which are unchanged since): `RESULT issue_accepted[carries-open]=0 of 5`, `RESULT issue_accepted[live]=23 of 23` (null control, flat).
  - At 5076c9e6, `python3 dev/audit/harnesses/r10_carry_sink_barrier.py 9ecbd4f6371de662ad7fa731d22b06dc38806903 5076c9e6caad07d561929555bba5078a14fde713` (the round-1 merge base): `RESULT issue_accepted[carries-open]=5 of 5`. At `HEAD`: `RESULT issue_accepted[carries-open]=0 of 5`, `RESULT issue_accepted[live]=23 of 23`. The verdict's own census also found 5.
  - No refuted group lists an issue on either ref, so the refuted arm is pinned by the self-test (`#901`) and not by the harness.
- Seam census re-run, round 2: `git grep -nE "CARRY_CLOSED|CARRY_DEST_CLOSED|carry_receivable\(|is_open\(|Dests\.live|self\.live\(" HEAD -- 'tools/**.py' ':!tools/audit/seat/r10_*mutants.py'`. Changes from round 1:
  - `carry_audit.py` `Dests.__init__` (`is_open`, then `self.live`) is a destination reader and is closed in this diff.
  - `ci_predict.py` `self_test` picks a destination and is closed in this diff.
  - `carry_audit.roster_report` (`CARRY_CLOSED`, ISSUE-STRANDED) is on the holding side: it reports an issue only closed groups list, which is ownership and not a destination.
  - `tools/ci/sweep.py`'s `self.live` is a PR-liveness method of another class and not a destination.
  - The rest is as in round 1.
- `python3 tools/audit/archscore/score.py --diff 04dfcafccdde1ee5df21a02fe4f06a5bc1083ea0 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff 04dfcafccdde1ee5df21a02fe4f06a5bc1083ea0`: `MODE: SCOPED -- 1 script(s) run`, `tests/entities.py`; `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2707 ENTITY CHECKS PASSED`.
- Self-tests at head: `carry_audit.py --self-test` `415 checks, 0 failed`; `ci_predict.py --self-test` `0 failed`; `tools/ci/selftest_scope.py --self-test` `103 checks, 0 failed`.

Round 1 (head 22f3ba79a):
Rule for the harness: `Dests.check` from each rev's own `carry_audit.py` + `roster_lib.py`, over every group of `origin/handoff/audit-r10-roster` at 43495fb6113e902630a0ac60b8012683c7cac97e. `pending_on_accepted_closed` is `roster_lib.pending_carries` (unmarked, no legacy exemption) summed over the carries-open, refused and refuted groups that rev still accepts. The brief's 116 counts every carry on the 10 carries-open groups, marked or not.

- `python3 dev/audit/harnesses/r10_carry_sink_barrier.py 699f4d9ef40f4eaf62397e81ae000680e417baf3` (base):
  - `RESULT accepted[carries-open]=10 of 10`
  - `RESULT accepted[refuted]=1 of 1`
  - `RESULT pending_on_accepted_closed=47`
  - `RESULT accepted[in-progress]=14 of 14`
  - `RESULT accepted[not-started]=22 of 22`
- `python3 dev/audit/harnesses/r10_carry_sink_barrier.py 22f3ba79a7a6f2832bb37d4bfa97b627459226db` (head):
  - `RESULT accepted[carries-open]=0 of 10`
  - `RESULT accepted[refuted]=0 of 1`
  - `RESULT pending_on_accepted_closed=0`
  - null control: `RESULT accepted[in-progress]=14 of 14`, `RESULT accepted[not-started]=22 of 22`, the same at both ends. Every live group is still accepted, so no live group reads as a sink.
- Seam census (fixer.md step 8): `git grep -nE "CARRY_CLOSED|CARRY_DEST_CLOSED|carry_receivable\(|is_open\(" HEAD -- 'tools/**.py' ':!tools/audit/seat/r10_*mutants.py'`.
  - **Destination readers, all closed in this diff:**
    - `carry_audit.py` `Dests.live`;
    - `roster_edit.py` `_absorb_into`, `op_append_carry`, `mark-carry moved`;
    - `roster_sync.py` `carry_plan`.
  - **Not destination readers:**
    - holding side, unchanged by design: `roster_lib.legacy_carries`, `roster_lib.stranded`, `carry_audit.roster_report`;
    - issue ownership: `Dests.__init__` (`is_open`);
    - planner and merge openness: `plan_page.py`, `replan.py`, `size_durations.py`, `merge_throughput.py`, `ci_predict.py:1383`, `roster_sync.py:441`, `roster_lib.open_groups` / `held_behind_deferred`.
- `python3 tools/audit/archscore/score.py --diff 699f4d9ef40f4eaf62397e81ae000680e417baf3 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`.
  - The rule text was cut to fit the `finding-propagation.md` line and token caps, which are already at zero headroom on main. No cap was raised.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (the scope's one script, `MODE: SCOPED`): `ALL 2707 ENTITY CHECKS PASSED`.
- Self-tests at head, all `0 failed`: `carry_audit`, `roster_lib`, `roster_edit`, `roster_sync`, `carry_fold`, `queue_pre_flight`, `orchestrator_tick`, `r10_roster_ops_mutants`.

## Red checks

- `governance / instrument-self-tests`, red at 34a9cf125. It is outside `merge_train.py owed-reds` (owner ruling 2026-11-07), so no answer is owed. It is answered anyway, for two causes:
  - **Stale base.** The branch predated main's #3409/#3410 selftest-closures changes. The merged tree passes `tools/ci/selftest_scope.py --self-test` (`103 checks, 0 failed`). The cheaper detector is `git merge-tree` plus a re-merge before handoff. Its standing cost is one merge per stale branch. fixer.md step 6 forbids a merge without a conflict, so no countermeasure is built: the train re-proves heads on current main.
  - **This PR's own `ci_predict.py --self-test` failure**, fixed in round 2. The cheaper detector was running locally the self-test of every tool that imports a changed module (`ci_predict.py` imports `carry_audit`). Measured standing cost: one `ci_predict.py --self-test` run took real 1m29.7s here. `prepr.sh` step 6d lists predicted reds but not importer self-tests. No countermeasure is built in this PR: the cost test needs the class frequency, and the root-cause seat owns that analysis (`defect-root-cause.md`).

## Forward-carry

none

## Friction

none
