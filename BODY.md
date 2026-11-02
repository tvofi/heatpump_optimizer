R10-BASH-KILL-HOOK part 2: wire the PreToolUse Bash hook `.claude/hooks/pre-bash.sh` (registered in `.claude/settings.json`) that refuses `pkill`, `killall` and a `kill` fed by `pgrep` at command position, now that part 1 (#3168, graders) is on main. A seat killing by name on the shared host killed every seat's run of one script on 2026-10-15; the preamble rule "kill only by PID" had no enforcement. Resumed from efada17e (handoff/r10-bash-kill-hook) with origin/main merged (no rebase); the older handoff-wip ref 408644f7 is an ancestor of efada17e and held nothing it lacks. A new driver, `tools/audit/seat/r10_bash_kill_hook_drive.py`, runs the hook from the REAL `.claude/settings.json`.

Roster carries (group R10-BASH-KILL-HOOK, both named here): Carry 1 (move `attribution` from `pending` to `ignore` in `tools/policy/field_coverage.mjs`) is already in the tree: `grep -n "'attribution'" tools/policy/field_coverage.mjs` shows it under `ignore` of the hooks registration, and this branch's registration has no `pending` map. Carry 2 (a local seat loads hooks from its own checkout, so local seats are protected once the orchestrator advances that checkout or installs the same script as a user-level PreToolUse Bash hook; cloud seats get it from a fresh checkout) is the orchestrator's operational step, not a code change in this diff.

## Head

bc4eb3daacae3d7f88932669c896293679b1b51a (bc4eb3d). Merge base with origin/main (279cb497fa76, unmoved since the merge): 279cb497fa764f89a961d94c87e57f16176c2fcc.

## Mutation proof

`python3 tools/audit/seat/r10_bash_kill_hook_drive.py` plants one mutant per arm in a scratch project dir holding a byte copy of the real settings.json and runs the registered command against it; each prints `MUTANT <name> killed=yes` (the real hook is never edited):
- M-pkill (pkill dropped from the refused words): killed=yes
- M-killall (killall dropped): killed=yes
- M-pgrepkill (the pgrep-fed kill arm removed): killed=yes
The hook's own `--self-test` (26 cases) is also run by `policy_lint.mjs --hooks` and prepr's hooks step.

## Null control

Same driver, unmutated hook: `CASE ok` for kill 1234 (plain kill of an owned pid), `git status`, and `echo "never pkill"` (all rc 0), and rc 2 for pkill, killall, `kill $(pgrep -f x)` and `pgrep -f x | xargs kill`. `--null` exits 0. An unparseable payload fails open (self-test END TO END cases).

## Figures

- `python3 tools/audit/seat/r10_bash_kill_hook_drive.py`: 7 CASE ok, 3 MUTANT killed=yes (rule: one line per case or plant).
- `bash .claude/hooks/pre-bash.sh --self-test`: 26 passed, 0 failed.
- `node tools/policy/policy_lint.mjs --hooks`: 4 wired hooks exist and pass their self-test.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget raised.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, runs tests/entities.py.
- `bash tools/pr/prepr.sh` at the head above, with origin/main unmoved since the merge (279cb497fa76 at 2026-11-02): rc=0 except the one predicted closures red, repaired by `python3 tools/pr/ci_predict.py --apply-inert` (tests/closures.json lists the new driver).

## Red checks

none beyond the predicted `tests / closures` INERT READS red the new driver would have caused; it is answered by naming it (`ci-autofix.md`) and was repaired before the handoff by `ci_predict.py --apply-inert`.

## Unpinned sites

none: the diff adds no `custom_components/` mutation site (prepr step 6d lists none).

## Forward-carry

none

## Friction

none
