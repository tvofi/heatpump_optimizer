Fix review: blocked 63c3886a4a2bb173898db4a5c8f06f9c9c382ac2 mutation-vacuous: diff_forkcap_branch, null_forkcap, headtail

bus-nonce: 1a45ffea6de2f41c3f6ba218b547deb3

Round 2 (delta d68d3074..63c3886a, reviewed from a detached worktree at the head; `ev/HEAD.txt`). The class-open block is answered. Three of the first round's surviving mutants are still alive.

## Block

- Surviving mutants on the fix's own lines, carried unchanged from round 1 (the delta adds no check for them; the body's Mutation proof does not mention them). Self-test at the head is 55 checks, 0 failed. Each mutant below also leaves it at 55 checks, 0 failed (`ev/mut_*.txt`, diffs `ev/mut_*.diff`):
  - `diff_forkcap_branch` (`if rc == FORKCAP_RC:` in `run_diff` -> `if False:`): SURVIVED. Diff-mode FORKCAP has no test.
  - `null_forkcap` (`if rc == FORKCAP_RC:` before `print("FORKCAP NULL")` in `run_spec` -> `if False:`): SURVIVED. The documented `FORKCAP NULL` line has no test.
  - `headtail` (STMT_DEL shared-line skip, `if head.strip() or (tail and not tail.startswith("#")):` -> `if False:`): SURVIVED. Nothing exercises `a = 1; b = 2` or `if x: y = 1`.
  Fix: add a diff-mode FORKCAP check (exit 1, `FORKCAP file:line OPERATOR`), a spec-mode NULL-FORKCAP check, and a shared-line STMT_DEL check; or answer each in the body as equivalent with a `survivor_triage` record.

## Findings

none

## Evidence

- RESULT block answered: the class-open block (descendants leaving the group or the session). Own harness (`ev/harness.sh`, `ev/esc.py`; the reviewer's, not the finder's; a 150-deep chain, `--fork-cap 32`, one mode per link: pgrp = setpgid, session = setsid, cleanenv = setsid + empty env, plain = control). Clean re-run in `ev/escape_clean_rerun.txt`. At d68d3074: pgrp FORKCAP in 1 s but 150 left; session KILLED (timeout) at 40 s, 150 left; cleanenv KILLED at 40 s, 150 left; plain FORKCAP, 0 left. At the head: pgrp, session and cleanenv FORKCAP in 1 s, 0 left; plain FORKCAP, 0 left. A first all-modes run (`ev/escape_both_ends.txt`) showed 123 leftovers at the head. That was residue from the earlier base runs: my cleanup was incomplete (the hook forbids pkill). I re-ran pgrp, session and cleanenv on a clean host and got 0 left each, and I rely on those re-runs.
- RESULT self-test at head: 55 checks, 0 failed, rc 0 (`ev/selftest_head.txt`, under `ulimit -u`, timeout 400). Matches the body's 55.
- RESULT mutants KILLED: `forkcap_no_kill` (3 failed: the pgrp, session and cleanenv chain checks); `finally_kill_off` (2 failed: both daemon checks); `ppid_leg_off` (`root = 0`; 2 failed, then the self-test crashed with ProcessLookupError at its own cleanup kill, so killed, not cleanly). These match the body's claims.
- RESULT `git merge-tree --write-tree origin/main 63c3886a4a2bb173898db4a5c8f06f9c9c382ac2`: rc 0, no conflict (`ev/merge_tree.txt`).
- RESULT carry: the body's `Carry: R10-MUTANT-RUN-FORKCAP` names the pending orchestrator ruling (a `fixer.md` exception), and the item is on origin/handoff/audit-r10-roster at c25798dfec, group R10-MUTANT-RUN-FORKCAP, in the roster `carry` list. Acceptance (23 sites, >= 14 from 7) stays unmeasured; I do not re-measure it.
- RESULT CI: `merge_train.py classify` printed `WAIT 63c3886a4a2bb173898db4a5c8f06f9c9c382ac2 pending: gate red: none`. No required check was red at that time. `owed-reds` is in `ev/owed_reds.txt`. The block is independent of CI.
- RESULT delta scope: tools/audit/seat/mutant_run.py and its instrument note, plus main-merge noise (gh_calls.py, seat-gh, delivery notes). VERSION, manifest and notes untouched.
