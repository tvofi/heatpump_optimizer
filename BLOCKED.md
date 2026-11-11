# BLOCKED: r10-prepr-residue

Question: the brief holds 21 carries on one seam (prepr.sh, ci_predict.py, body_push.sh), against the fixer contract's limit of five findings per group. Which subset is this group to build, and should the rest split into further groups?

State at stop (head 45adb0c3b4 plus one uncommitted-to-handoff step on handoff-wip):
- Carry 4 (.gitignore): `config/` re-anchored to `/config/`. `git check-ignore -v config/x` still matches .gitignore:28; dev/audit/config/x and dev/governance/config/x no longer match (they did before). No failing test is committed yet, so this step is unproven by the contract's standard.
- Carry 6 (nested slot livelock): not reproduced. A read-only scan found no place where prepr.sh or its --self-test drops HPO_SLOT_LABEL; gate_lock.py reads it only as non-empty env. Candidate cause, unverified: take_slot's WARN branch sets SLOT_TAKEN=1 without exporting, and a take that runs in a subshell exports nothing. Needs a live `gate_lock.py slot-status` during a stall, or a planted all-slots-taken fixture, before any fix.
- Carries 0-3, 5, 7-20: not started.
