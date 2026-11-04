R10-PREPR-CAP slot arm: `tools/pr/prepr.sh` takes its heavy slot lazily, just before its first heavy step that is not skipped, instead of for the whole run (carries 25 and 26). It also refuses a body whose `## Head` names another sha before any heavy step (carry 23) and pins the interpreter-spawn cost of step 6g (carry 24). Carry 6 was already built at the merge base. Roster carries 7, 12, 15, 16, 19 and 20 of this part are not built here and stay open on the roster as they were; carry 6 was already built at the merge base. Closes #2267.

## Head

f7585aa24d7b0003051d5ef25b74dcdae3fceb8c (code head after merging origin/main a9c2f90fc; main had not moved since the last prepr run on this head).

## Mutation proof

Each mutant run is `bash <copy of prepr.sh> --self-test` from the worktree, `PYTHONPATH=tests/hastub`; the production line named is the one changed.
- `take_slot` called unconditionally at step 1b (undoes the lazy take): red rows `the main flow calls take_slot at the mutants, self-test, closures and diff-mutants steps (and defines it once)` (got 5, wanted 4) and `and the first call sits after the light policy_lint step: a run that skips every heavy step never takes one`.
- a `python3 -I -c pass` spawned per link target in `claims_reg_line`: red row `6g spawns the same few interpreters for 40 link targets as for 4 (7/43)`.
- `if [ "$EARLY_HEAD_RC" -ne 0 ]` replaced by `if false` in step 1a3: red rows `step 1a3 exits nonzero on a head_arm refusal, naming it, before any heavy step` and `and does not fall through to the heavy steps`.
(The copy runs also redden `a change to prepr.sh owes the self-test` because a /tmp copy is not PREPR_PATH; that is the runner, not the mutant. Unmutated copy of the final file: 477 passed, 0 failed.)

## Null control

- Pool of four slots full (`HPO_GATE_LOCK_DIR` throwaway, four live holders), a diff whose heavy steps are all skipped (`PREPR_SKIP_CLOSURES=1`, docs-only): main's prepr.sh stalls at the slot-take and is killed by `timeout 90` (rc=124); this branch's finishes rc=0 with zero `heavy slot` lines.
- A diff reaching the self-test or a scoped recording still takes exactly one slot: the full run on this branch prints one `heavy slot taken slot=0` line before the mutants drive; self-test rows `take_slot called twice takes exactly one slot (idempotent)` and `a take_slot inside an inherited slot takes none` drive the function.
- Unmutated tree: head_arm passes a body naming this head; a diff touching only `tests/features.py` still skips 6g (rc 3), existing rows.

## Figures

- Pool behaviour, `HPO_GATE_LOCK_DIR=$(mktemp -d)/lk python3 tests/gate_lock.py slot-take --label sN --owner-pid <pid>` x4 then `slot-status`: `4/4 slots held`; a fifth `slot-take` under `timeout 8` returns rc=124 (queued); `holding_slot()` under `HPO_SLOT_LABEL=s1` is True (a nested step joins, does not re-take).
- Self-test: `PYTHONPATH=tests/hastub bash tools/pr/prepr.sh --self-test` prints `477 passed, 0 failed` on the tip before the merge.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; `node tools/policy/policy_lint.mjs` prints `0 error(s)`.
- Not measured: slot-wait minutes per prepr over a day (needs the live tick); the carries' logs (35 logs, 29 no-heavy) are the brief's.

## Approval

Policy files `dev/governance/rules/gate-scoping.md` and `dev/governance/roles/nudge.md` change: both state that prepr takes a slot at its first heavy step. gate-scoping.md is token-neutral against its cap (policy_lint 0 errors). Needs the owner's approving review (tvofi).

## Red checks

none

## Forward-carry

none

## Friction

none
