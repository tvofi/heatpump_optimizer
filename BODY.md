Carry 1 (the brief's Carry 0, MUTVAC-STMT-DEL) is implemented here as STMT_DEL, after the fork cap.

Carry 2 (the acceptance carry, item 803fdcf8, in Forward-carry below) has landed on the group's roster entry at roster commit c25798dfec (origin/handoff/audit-r10-roster, dev/programme/rosters/wave-r10-groups.json).

mutant_run.py bounds the command's process tree and gains a STMT_DEL operator (P604 FORKCAP; carry P607 STMT_DEL). The command's family is polled every 0.5 s and SIGKILLed whole past `--fork-cap` (default 256) processes, and again at the command's exit, on timeout and on a signal; the outcome is `FORKCAP`, never KILLED, since a cap stop proves no test pins the mutant. Family is four legs: the command's session, its process group, every process carrying the run's `MUTANT_RUN_TOKEN` environment mark, and every descendant of the driver, which sets `PR_SET_CHILD_SUBREAPER` for the command's lifetime (restored after) so an orphan reparents to it rather than to init. The ppid leg is the one no descendant can leave: setsid, setpgid, a cleared environment and an exited parent all keep a process under the subreaper. Children the driver had before the command are excluded; reparented orphans that die are reaped each poll, and zombies are not counted. Diff mode's STMT_DEL replaces each simple statement an added line falls in with `pass` (compile-checked, deduped against CALL_DEL/RETURN_DEL). No reproduction ran an unbounded self-test; all runs were under `ulimit -u` in a subshell with a timeout.

Alternatives: an RLIMIT_NPROC soft limit lost (not enforced for root, counts the whole user, and a fork failure would read as KILLED rather than FORKCAP). A per-command cgroup lost to the subreaper: it needs a writable, delegated cgroup v2 hierarchy, which a seat container does not guarantee, while prctl needs no privilege. A FORKCAP diff run exits 1 (0 under --report-only); survivor_list.py reads only SURVIVED lines, and its pinned producer strings are unchanged.

## Head

09a166660de9528e4bec9ee030320ad161e4bfae (merge base ee64358be7eeccaec5178a923cb3b83a18a924a0 = origin/main at 2026-11-11).

## Mutation proof

Repair for the second block (a descendant that leaves the session and clears its environment): the self-test gains `forkcap: a chain that leaves its cleanenv at every link is FORKCAP, not waited out`, `forkcap: no cleanenv-leaving descendant outlives the run` and `forkcap: a daemon that left the session, cleared its environment and outlived its command is killed at the command's exit`, written first. Each mutant below was applied in place, the self-test run under `ulimit -u` with `timeout 230`, and the file restored:

- ppid leg off (`root = 0`, the predicate at e87b955): 3 failed, the three new checks.
- subreaper not set (`_subreaper(1)` -> `_subreaper(0)`, closure kept): 1 failed, the clean-env daemon check (the orphan reparents to init, outside the closure).
- closure walk stopping at a pid another leg already counted: 1 failed, the clean-env chain check (this was the first draft's bug, caught by the chain check).
- First block's mutants, re-run at e87b955 by the reviewer and unchanged here: cap disabled, counter reverted to `session == sid`, token clause removed, exit-time kill removed, STMT_DEL dispatch removed; each fails at least one check.
- Restored head: 55 checks, 0 failed.

## Null control

- Finder's harness (`ev/harness.py`, `ev/harness2.py`, `ev/chain.py` at probe/revt-r10-mutant-run-forkcap-1e9d4484), both ends. At e87b955: E1 clean-env setsid chain TIMEOUT after 16.1 s, 80 left; E2 `setsid env -i` daemon rc 0, 1 left. At the head: E1 FORKCAP in 0.7 s, 0 left; E2 rc 0, 0 left. Controls unchanged at both ends: E1-null (chain keeping its environment) FORKCAP, 0 left; E2-null, E3, E4 rc 0, 0 left.
- Bounded 10-process chain under a cap of 32: unaffected (`SURVIVED ret_hi`). Same endless-style chain with `--fork-cap 0`: runs out and SURVIVES, so the FORKCAP arm is the cap's doing.
- Comment- and docstring-only diff lists zero STMT_DEL; unpinned assignments SURVIVE, the pinned one is KILLED; a three-line continuation yields exactly one mutant at its first line.

## Figures

- `( ulimit -u $(( $(ps -e --no-headers | wc -l) + 400 )); timeout 230 python3 -I tools/audit/seat/mutant_run.py --self-test )`: 55 checks, 0 failed (enumerator: the script's own check count).
- Class enumeration rule, every spawn under `tools/` and `custom_components/` that leaves the session, group or environment: `git grep -lE 'start_new_session|os\.setsid|setsid |setpgid|daemoni[sz]e\(|env -i' -- tools custom_components ':!*.md' ':!*.json'` returns 12 files: tools/audit/judge_batch.py, tools/audit/seat/beatd.py, tools/audit/seat/cloud-setup.sh, tools/audit/seat/cloud_relay.sh, tools/audit/seat/daemonize.py, tools/audit/seat/merge_train.py, tools/audit/seat/mutant_run.py, tools/audit/seat/open_driver.py, tools/audit/seat/pr_args.sh, tools/audit/seat/tick_loop.sh, tools/pr/app_approve.sh, tools/release/stamp.py. Disposition, every one: closed in this diff. Each forks from its caller, so a run of it under the driver stays in the ppid-closure whatever it does to its session, group or environment; the seam the block named (beatd.py's `BASE_ENV` allowlist and `start_new_session=True` job, and `_discovery`) is the setsid-plus-cleared-environment shape the new chain and daemon checks drive. mutant_run.py's own hit is the command's spawn.
- The one shape the ppid leg cannot reach is a process the command does not fork: work handed to an already-running service. Enumerator: `git grep -nE 'systemd-run|crontab|docker (run|exec)|\bat now' -- tools custom_components ':!*.md' ':!*.json'` returns 3 lines, all text (a coordinator.py comment, a gantt_drift.py comment, an export.py help string), no spawn: no seam.
- `tools/pr/prepr.sh`: rc 0 at the head above; MODE: SCOPED; self-test step 515 passed, 0 failed; merged structure ratchet passed; closures step ran (not skipped).

## Red checks

- `tests / fast (3.14)`: red on main, not from this diff, which touches only tools/audit/seat/mutant_run.py and its instrument note. It is the combi census failure PR #3466 fixes; the cheaper detector (the census script in prepr's fast lane) exists and this branch's closure does not reach it. No PR run of this head exists yet.

## Forward-carry

- Residual: MUTVAC-STMT-DEL's acceptance (the 23 reviewer-named Python sites reach >= 14 STMT_DEL-visible mutants, from 7) is unmeasured: the sites' heads.tsv is in neither the tree nor the dispatch payload, so this seat cannot run `mutant_run.py --diff <base>...<head> --list` over them. `#3394` is refused by `carry_audit.py check` as having no owner. It stays with this group pending the orchestrator's ruling: supply heads.tsv to a re-run, or name a receiving group. Carry: R10-MUTANT-RUN-FORKCAP

## Friction

none
