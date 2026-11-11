Carry 1 (the brief's Carry 0, MUTVAC-STMT-DEL) is implemented here as STMT_DEL, after the fork cap.

mutant_run.py bounds the command's process tree and gains a STMT_DEL operator (P604 FORKCAP; carry P607 STMT_DEL). The command's session is polled every 0.5 s and SIGKILLed whole past `--fork-cap` (default 256) processes; the outcome is `FORKCAP`, never KILLED, since a cap stop proves no test pins the mutant. Diff mode's STMT_DEL replaces each simple statement an added line falls in with `pass` (compile-checked, deduped against CALL_DEL/RETURN_DEL). No reproduction ran an unbounded self-test; all runs were under `ulimit -u` in a subshell with a timeout.

Alternatives: an RLIMIT_NPROC soft limit lost (not enforced for root, counts the whole user, and a fork failure would read as KILLED rather than FORKCAP). A FORKCAP diff run exits 1 (0 under --report-only); survivor_list.py reads only SURVIVED lines, and its pinned producer strings are unchanged.

## Head

d68d307421b117a807b0734ccea1e9d57f8b09b6 (merge base ee64358be7eeccaec5178a923cb3b83a18a924a0 = origin/main at 2026-11-11).

## Mutation proof

- Cap check disabled (`if FORKCAP[0] and len(` -> `if False and len(`): self-test fails `forkcap: an endless-style chain past a cap of 32 is FORKCAP...`.
- STMT_DEL dispatch removed (`found.extend(_stmt_del(` -> `_ = (_stmt_del(`): fails `diff: the added lines yield all six operators`, `diff: a self-test that does not pin them leaves survivors...`, both `STMT_DEL:` listing/survivor checks.
- Both restored; self-test green (47 checks, 0 failed).

## Null control

- Bounded 10-process chain under the same cap of 32: unaffected (`SURVIVED ret_hi`).
- Same endless-style chain with `--fork-cap 0`: runs out and reports SURVIVED, so the FORKCAP arm is the cap's doing.
- Comment- and docstring-only diff lists zero STMT_DEL.
- Unpinned assignments SURVIVE, the pinned one is KILLED; a three-line continuation yields exactly one mutant at its first line.
- Not run: the carry's acceptance over the 23 reviewer-named Python sites. Their heads.tsv is not in the tree or reachable from this seat, so the >=14 count (today 7) is unmeasured. Carry: #3394 (the relay owning the Card re-runs `mutant_run.py --diff <base>...<head> --list`).

## Figures

- `( ulimit -u $(( $(ps -e --no-headers | wc -l) + 300 )); timeout 200 python3 -I tools/audit/seat/mutant_run.py --self-test )`: 47 checks, 0 failed (enumerator: the script's own check count).
- `tools/pr/prepr.sh`: rc 0 at the head above; MODE: SCOPED; structure ratchet passed; closures step ran (not skipped).

## Red checks

none

## Forward-carry

none

## Friction

none
