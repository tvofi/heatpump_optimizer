Carry 1 (the brief's Carry 0, MUTVAC-STMT-DEL) is implemented here as STMT_DEL, after the fork cap.

mutant_run.py bounds the command's process tree and gains a STMT_DEL operator (P604 FORKCAP; carry P607 STMT_DEL). The command's family (its session, its process group, and every process carrying the run's `MUTANT_RUN_TOKEN` environment mark, so a descendant that left the group or the session, or was orphaned, is still counted) is polled every 0.5 s and SIGKILLed whole past `--fork-cap` (default 256) processes, and again at the command's exit, on timeout and on a signal; the outcome is `FORKCAP`, never KILLED, since a cap stop proves no test pins the mutant. Diff mode's STMT_DEL replaces each simple statement an added line falls in with `pass` (compile-checked, deduped against CALL_DEL/RETURN_DEL). No reproduction ran an unbounded self-test; all runs were under `ulimit -u` in a subshell with a timeout.

Alternatives: an RLIMIT_NPROC soft limit lost (not enforced for root, counts the whole user, and a fork failure would read as KILLED rather than FORKCAP). A FORKCAP diff run exits 1 (0 under --report-only); survivor_list.py reads only SURVIVED lines, and its pinned producer strings are unchanged.

## Head

e87b955dabe3b5e7016997e1d343998fa2317e17 (merge base ee64358be7eeccaec5178a923cb3b83a18a924a0 = origin/main at 2026-11-11).

## Mutation proof

Repair for the blocked verdict (descendants leaving the group or session): the new self-test checks `forkcap: a chain that leaves its pgrp/session at every link is FORKCAP`, `no ... descendant outlives the run`, and `a daemon that left the session and outlived its command is killed at the command's exit` were written first and failed (5 of 52) on the session-only counter and killpg kill; with family counting by session, group and token and a family kill they pass (52 checks, 0 failed). Reverting the counter to `session == sid` fails the session-chain and daemon checks again.

- Cap check disabled (`if FORKCAP[0] and len(` -> `if False and len(`): self-test fails `forkcap: an endless-style chain past a cap of 32 is FORKCAP...`.
- STMT_DEL dispatch removed (`found.extend(_stmt_del(` -> `_ = (_stmt_del(`): fails `diff: the added lines yield all six operators`, `diff: a self-test that does not pin them leaves survivors...`, both `STMT_DEL:` listing/survivor checks.
- Both restored; self-test green (52 checks, 0 failed).

## Null control

- A chain that stays in the session and group (plain fork chain) is still capped as before; a daemon-free command leaves no residue.
- Bounded 10-process chain under the same cap of 32: unaffected (`SURVIVED ret_hi`).
- Same endless-style chain with `--fork-cap 0`: runs out and reports SURVIVED, so the FORKCAP arm is the cap's doing.
- Comment- and docstring-only diff lists zero STMT_DEL.
- Unpinned assignments SURVIVE, the pinned one is KILLED; a three-line continuation yields exactly one mutant at its first line.
- Not run: the carry's acceptance over the 23 reviewer-named Python sites. Their heads.tsv is not in the tree or reachable from this seat, so the >=14 count (today 7) is unmeasured. Carry: #3394 (the relay owning the Card re-runs `mutant_run.py --diff <base>...<head> --list`).

## Figures

- `( ulimit -u $(( $(ps -e --no-headers | wc -l) + 300 )); timeout 200 python3 -I tools/audit/seat/mutant_run.py --self-test )`: 52 checks, 0 failed (enumerator: the script's own check count).
- `tools/pr/prepr.sh`: rc 0 at the head above; MODE: SCOPED; structure ratchet passed; closures step ran (not skipped).

## Red checks

- `tests / fast (3.14)`: red on main, not from this diff, which touches only tools/audit/seat/mutant_run.py and its instrument note. It is the combi census failure of PR #3466; the cheaper detector (the census script run in prepr's fast lane) exists and this branch's closure does not reach it, so the standing cost is nil here. Nothing in this branch changes it.

## Forward-carry

none

## Friction

none
