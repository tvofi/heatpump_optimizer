R10-FLY-CARRY-CLAIM-DRIVER (triage P290, `dev/programme/triage/s6-batch62.md#P290`): a merge verdict never carried across a main move whose claim file git's own driver resolved. `tools/pr/app_approve.sh`'s `carry` required each `merge=claimnotes` file in a merge commit to equal the union of its parents' lines, but `tests/env_drift.py`'s `merge_claim_file` takes the claim list from the side that changed it and never unions it, so a merge in which main cleared a claim the branch kept was refused. `tools/audit/seat/review_carry.py` asks `app_approve.sh --carry`, so this one change serves both.

The fix, in `carry`'s merge-commit arm: a claim file that is not the union now also passes when it is byte-equal to what `claim_driver_wrote` reports main's driver writes, `env_drift.py --merge-claim-file` run on copies of the file at the parents' merge base, first parent and second parent. The driver is `git show "$main:tests/env_drift.py"`, read at main like the `.gitattributes` list, never at the head. A driver refusal (both sides rewrote the claim list) writes nothing that can match, so the union rule decides there, unchanged. Byte-equality, not the union's sorted-line comparison: git writes the driver's output verbatim, so any other byte is a hand edit.

Alternatives: make the driver union (rejected: the driver's docstring measures that a union reinstates a claim the branch deleted); a train hold or reordering (rejected in P290, out of scope). Descriptions of the carry rule that named only the union were corrected in the same diff: `review_carry.py` (module docstring, `_carry` docstring, a self-test comment), `tools/audit/seat/instruments/app_approve.sh.md`, `tools/audit/seat/instruments/review_carry.py.md`, `dev/governance/roles/orchestrator.md`'s carry bullet loses its clause "and each claim file a pure union of both sides": it restated `--carry`'s own claim-file rule and, after this fix, was stricter than the tool, sending a driver-resolved merge to a delta review the tool would carry. Deleting it rather than extending it also keeps that file under its `files_tokens` cap (an extended clause measured 4261 against 4251). **That hunk is policy** (see `## Approval`); the code half stands alone, so the orchestrator may drop commit bfbb22301 to land the fix without it, leaving the bullet stricter than the tool.

## Head

bfbb223013b89463bf2697c3914d7eaa25edcbd8, branched from origin/main da066609fb1f076333d064f5f49612998253f7ce (merge base; main's tip at 2026-10-30T00:25Z).

## Mutation proof

Each mutant is applied to `tools/pr/app_approve.sh` at the head, the self-test run (`bash tools/pr/app_approve.sh --self-test`), then the file is restored:

- M1, drop the driver arm (`[ "$got" = "$want" ] || claim_driver_wrote ... \` becomes `[ "$got" = "$want" ] \`): `271 checks, 1 failed`, `FAIL CARRY: a claim file resolved by main's driver, which is not the union (got '1', want '0')`.
- M2, read the driver at the head (`claim_driver_wrote "$main" "$c"` becomes `claim_driver_wrote "$c" "$c"`): `271 checks, 2 failed`, `FAIL NO CARRY: main's side dropped by hand, which only the head's own driver would write` and `FAIL refused on main's driver, not the head's`.
- M3, trust the driver's exit and skip the byte comparison (`&& git show "$c:$p" | cmp -s - "$d/A" && r=0` becomes `&& r=0`): `271 checks, 4 failed`, the two hand-added-line checks and the two head-driver checks.

Failing test first: the new fixture was committed to the self-test before the fix and read `269 checks, 1 failed`, `FAIL CARRY: a claim file resolved by main's driver, which is not the union (got '1', want '0')` at the base's `carry`.

## Null control

- The existing arm still refuses a non-union hand resolution: `ok   NO CARRY: a claim resolution that drops a line`, `ok   refused as a claim resolution that is not the union` (twice, the drop and the rewrite fixtures), in the head's self-test. That fixture repo has no `tests/env_drift.py` at main, so the driver arm cannot run there and the union alone decides, as a driver refusal leaves it.
- The new fixture's hand-added claim line beside the driver's output is refused: `ok   NO CARRY: the driver's resolution with one hand-added claim line`.
- On the real tree, a branch-authored commit of #2917 still does not carry: `bash tools/pr/app_approve.sh --carry 3f33c67960605c1cb33a6e62baf0b25340dbc1d4 535015a87f0c61778444fd9cb9f125ab3db921d7 origin/main` at the head prints `CARRY: no ... is a commit of the branch's own`, rc 1.

## Figures

- The finder's predicate, before and after, on the 4 merges of #2917 P290 names, each from its first parent: `bash tools/pr/app_approve.sh --carry <merge>^1 <merge> origin/main` for f53ac2a39, 2fda9547e, c861c0e7b, 2a5bd4dd2. At da066609f (base): each rc 1, `resolves tests/golden/claimed_drift.txt to something other than the union of its parents`. At ea363c733 (the fix commit; bfbb22301 changes only `orchestrator.md`): each rc 0, `CARRY: yes`.
- The replay P290 states, re-taken: for each of the same 4 merges, `tests/golden/claimed_drift.txt` at the merge differs from the sorted union of its parents' lines and is byte-equal to `python3 -I <git show origin/main:tests/env_drift.py> --merge-claim-file O A B 7 tests/golden/claimed_drift.txt` on copies at (merge base, first parent, second parent), the driver exiting 0 each time. Null control for that replay: main's own merge da066609f reads union EQUAL and driver EQUAL, so the comparison is not stuck at DIFFERS.
- Self-test: `bash tools/pr/app_approve.sh --self-test` at the head, `271 checks, 0 failed` (6 new checks); `python3 tools/audit/seat/review_carry.py --self-test`, `26 checks, 0 failed`.
- Gate scope: `python3 tests/closure.py select --diff da066609fb1f076333d064f5f49612998253f7ce`, `MODE: SCOPED`, running `tests/entities.py`.
- At bfbb22301: `PYTHONPATH=tests/hastub python3 tests/entities.py`, `ALL 2477 ENTITY CHECKS PASSED`; `python3 tests/structure.py`, `STRUCTURE RATCHET PASSED`; `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`, rc 0. Null control for the entities run: at ea363c733, with the extended clause over the `files_tokens` cap, the same command printed `1 of 2477 ENTITY CHECKS FAILED` (the template-acceptance arm, which runs `policy_lint`).

Class seams (step 8): the rule enumerating every reader of the carry predicate is `git grep -l -- '--carry' -- tools/ .github/`, 14 files at the head. Dispositions: `tools/pr/app_approve.sh`, closed in this diff (the one implementation). `tools/audit/seat/review_carry.py`, `merge_train.py`, `bus.sh`, `ledger.py`, `orchestrator_tick.py`, `queue_pre_flight.py`, `row_position.py`, `tools/policy/policy_lint.mjs` and `tools/pr/merge_main_bot.py` name or shell out to `app_approve.sh --carry` and hold no copy of the claim-file rule (`grep -ci union` over each: 0, or a hit unrelated to the carry — `merge_train.py:4649` the driver's note union, `merge_main_bot.py:400` a fixture driver, `policy_lint.mjs` none about claims); `merge_train.py`'s refusal classifier keys on `is not an ancestor of` only, so the reworded refusal text reaches no matcher (`git grep -n "other than the union"` outside `app_approve.sh`: only the triage record, a recount left as written). The four `.md` instrument entries: `app_approve.sh.md` and `review_carry.py.md` corrected here, `merge_train.py.md` and `queue_pre_flight.py.md` state no claim-file rule.

## Approval

Pending: the owner's approving review. This diff touches `dev/governance/roles/orchestrator.md` (one clause deleted from the carry bullet, above), which is policy under `CLAUDE.md`; no approval has been given.

## Red checks

none

## Forward-carry

none

## Friction

none
