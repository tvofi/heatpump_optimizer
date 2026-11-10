R10-CARRY-SINK-BARRIER: the owner-approved barrier (tvofi 2026-11-10). A carry goes to the live group owning the seam; where none exists, the producing group keeps the fix. Before this change `carry_audit.py` refused only a destination gone or at a `CARRY_CLOSED` stage, and `roster_edit.py append-carry` and `roster_sync.py carry_plan` accepted any open group, so a carry could be parked on a group whose pull request had already merged (`carries-open`) or on a group created only to receive carries.

This is policy (`finding-propagation.md` changes what a seat must do). It is merged under the mandate and surfaced to tvofi.

The fix is one predicate, `roster_lib.carry_receivable`, read by all five destination readers:
- `carry_audit.Dests.live`, which `Dests.check` and the refusal's valid-target list use;
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

## Approval

This is a policy change: `dev/governance/rules/finding-propagation.md` and its generated copies. The barrier is owner-approved per the group's brief (tvofi 2026-11-10), which says it merges under the mandate and is surfaced to tvofi. The approval itself is recorded at merge, by one of:
- tvofi's approving review at this head;
- an approving review citing mandate 6329234399 (scope all), if that mandate is in force when it merges.

This seat holds no approval.

## Head

`34a9cf1251fa6046f3182a21aea60a84b477609f` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

22f3ba79a7a6f2832bb37d4bfa97b627459226db, on base 699f4d9ef40f4eaf62397e81ae000680e417baf3 (origin/main at the cut).

## Mutation proof

Each mutant is run against the named file's `--self-test`, then the file is restored.

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
- `roster_sync.carry_plan`: MUTANT-SYNC below.

## Null control

- The unmodified base tree accepts a carry to every carries-open group: harness at the base, below.
- The new self-test arms check that a carry to a live group still passes:
  - `sink barrier (null control): a carry to the live group R10-WORK / R10-NEXT / R10-PR still passes`;
  - `carry_receivable (null): live stages take a carry, and so does a group with an empty files list but a PR, an issue or a fix, or no files key`;
  - `append-carry to an open group with no PR appends without a WARN` (unchanged).

## Figures

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

none

## Forward-carry

none

## Friction

none

