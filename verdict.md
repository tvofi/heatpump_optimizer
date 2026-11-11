Fix review: blocked e87b955dabe3b5e7016997e1d343998fa2317e17 class-open: a descendant that leaves the session and clears its environment is never counted or killed (tools/audit/seat/mutant_run.py family token predicate; in-tree seam tools/audit/seat/beatd.py:301,336,895)

bus-nonce: 1e9d448424ec3bb74ff1bd44dca30ff1

Round: second review of R10-MUTANT-RUN-FORKCAP (first block at d68d307421b117a807b0734ccea1e9d57f8b09b6); a third block is not yet the fourth round that owes a re-cut.

## Block

The repair closes the two instances the first block named (pgrp-leaving and session-leaving chains, an outliving setsid daemon) by adding a third membership leg: the `MUTANT_RUN_TOKEN` environment mark. That leg is the predicate's new unguarded domain, and `family()`'s own docstring concedes it ("inherits the token unless it clears its environment"); the body dispositions none of it and names no enumeration rule.

- E1, a chain that calls setsid and execs with a cleared environment at every link (`ev/chain.py cleanenv 80`, cap 32, timeout 15 s), went to TIMEOUT after 16.1 s, and 80 processes outlived the run. Null control: the same chain keeping its environment is FORKCAP in 1.6 s with 0 left (`ev/escapes-head.txt`). So the cap fails because of the cleared environment and nothing else.
- E2, a double-fork daemon made by `setsid env -i ...` that outlives its command, returned rc 0 with 1 process left behind, on both runs. Null control: the same daemon without `env -i` left 0.
- The in-tree seam exists. `beatd.py` builds each job's environment from the `BASE_ENV` allowlist (`:300-301`), which drops `MUTANT_RUN_TOKEN`, and starts the job with `start_new_session=True` (`:336`). `_discovery` (`:895`) also runs with an allowlisted environment. `beatd.py` is a `--diff` target, since it is not under tests/ or dev/. A mutant there that makes a job re-enter or hang therefore escapes the cap, the exit kill and the signal kill: the four-hour ppid-1 orphan shape seen on the orchestrator's host today.
- A remedy that does not depend on what a descendant keeps: make the driver a child subreaper (`prctl(PR_SET_CHILD_SUBREAPER)`) so orphans reparent to it, and count the ppid-closure of the command plus the session, group and token; or run each command in its own cgroup. The fixer chooses; this review did not build either.

## Findings

- Follow-up: the body names no class-enumeration rule for "processes that can leave the family predicate", so a reviewer has to hunt escapes by hand. The repair should state the rule, for example every `start_new_session`, setsid, `daemonize` and allowlisted-`env=` spawn under `tools/` and `custom_components/` reached by `--diff`, and disposition each one. Carry: R10-MUTANT-RUN-FORKCAP
- Residual: the roster carry MUTVAC-STMT-DEL's acceptance (23 reviewer-named sites reach >= 14, mutation proof returning to 7) was not run at this head, because heads.tsv is not in the tree. The body routes this to `Carry: #3394`, but `carry_audit.py check` refuses that destination ("#3394 has no owner"), so the carry stays with this group until it is measured or routed to a receivable owner. Carry: R10-MUTANT-RUN-FORKCAP

## Evidence

- Head reviewed: e87b955dabe3b5e7016997e1d343998fa2317e17 (`ev/HEAD.txt`), from a detached worktree. No pull request exists yet, so there is no review packet, no CI run and no check-runs to read: no red can be owed by this head.
- `git merge-tree --write-tree origin/main(0e28afd38b) e87b955` exits 0 (`ev/merge-tree.txt`). The head is behind main and merges cleanly.
- VERSION, the manifest and RELEASE_NOTES.md: the three-dot diff is empty for all three. The diff touches only `tools/audit/seat/mutant_run.py` and `tools/audit/seat/instruments/mutant_run.py.md`. No golden fixture or claim file moved, so step 4 has no input.
- Self-test under `ulimit -u` with a 230 s timeout: 52 checks, 0 failed (`ev/selftest-head.txt`). This re-derives the body's figure of 52/0.
- Mutation proofs, each restored afterwards (`ev/mutants-summary.txt`, `ev/mut-*.txt`):
  - cap disabled: 3 failed (the endless chain and the pgrp and session chains);
  - counter reverted to `session == sid`: 3 failed (session chain, session leftover, daemon);
  - my own: token clause removed: 3 failed;
  - my own: exit-time `_kill_family` removed: 1 failed (daemon);
  - STMT_DEL dispatch removed: 4 failed.
  
  No survivor. The body's two mutant claims reproduce.
- Escape attempts beyond the block (`ev/harness2.py`, `ev/escapes-head.txt`):
  - E3, a double fork without setsid whose orphan outlives the command: rc 0, 0 left, so it is covered.
  - E4, an orphan that setsids and clears its environment after 0.3 s: 0 left, so it is covered. The exit kill catches it while it still carries the token. This holds only because its re-exec comes after the command exits; it is not a general guarantee (see E2).
  - Four lines from the first harness run are marked VOID in the file: dash has no `exec -a`, so the sleeper never started.
- Not re-derived: `tools/pr/prepr.sh` rc 0 / MODE: SCOPED. The heavy gate is cited, not re-run.
- `merge_train.py owed-reds` lists `tests / fast (3.14)`. The body answers it as main's census red (PR #3466); with no PR run, it is not this head's red.
