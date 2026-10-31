Record PR: rewrites `dev/programme/HANDOVER.md` in place against main `a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0` (merge of #3016); `updated-for:` names that merge. The file was last written on main at `b161681af` (2026-10-23). It now states what a resuming session cannot derive in one command: the standing seats and their contracts, the instruments in daily use (a pointer to `tools/audit/seat/INSTRUMENTS.md`, not a restatement), the mandate's operating rules (read from the API at use; the kill stem voids it beside an id and an identifier such as a group name counts; scope `all` means the orchestrator approves code-owned, policy and budget-raise merges), the critical path to closure as `roster_lib.critical_path` derives it, and the merge, train and stamp sequence including decision 0016's `--round-close 10`.

Removed because false or answered by the tree: the 2026-10-14 mandate and its dates (superseded; id and dates live on #201), the owed item that the soft-cap instrument refuses an owed handoff (`pr_cap.py dispatch-gate` now exists and states the exemption), the per-merge chronology, and traps a detector now carries. Volatile state (open PRs, the cap in force, the mandate id) is left to #201 by pointer. Not policy: the file sits outside `POLICY_GLOBS`; no `## Approval` owed. It surfaces one divergence under Owed: `standing-merge.md` still names `merge_pr.sh` for budget and policy heads, which the owner's 2026-10-26 ruling supersedes; that policy edit is not made here.

## Head

`c2ebaeb5963642b5b4e55d15ad4072796ef3e206`, on main `a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0`.

## Figures

- critical path named in the file: load `wave-r10-groups.json` from `origin/handoff/audit-r10-roster` and call `critical_path` in `tools/audit/seat/roster_lib.py`; it is a snapshot dated 2026-10-31 and the file says to re-derive.
- structure ratchet at this head: `python3 tests/structure.py` (STRUCTURE RATCHET PASSED).
- layout guard: `python3 -I tests/layout.py --guard --base $(git merge-base origin/main HEAD)` (0 refusal(s)).
- policy lint: `node tools/policy/policy_lint.mjs` (0 error(s), rc 0).

## Mutation proof

n/a: record-only diff, one prose file; no production, test or check code to mutate.

## Null control

`tests/entities.py`'s handover checks (single handover, `updated-for:` reachable from HEAD and `origin/main`) pass on the base and at this head; the `updated-for:` SHA is a main merge commit, so a squash cannot orphan it.

## Red checks

none

## Forward-carry

none

## Friction

none
