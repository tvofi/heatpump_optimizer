Part 1 of R10-BASH-KILL-HOOK (#2732): key `policy_lint --hooks`' PreToolUse matcher check on the script each entry runs, and drop the duplicate `attribution` entry from `field_coverage`'s hooks `pending` map. Graders only; the hook script and settings registration are part 2 (`handoff/r10-bash-kill-hook`), which lands once this is on main. Same split as R10-MACHINERY-RATCHETS part 1. Case 2: the bootstrap. The branch's own graders pass the full change; main's copies refuse it as `MATCHER BLIND` on the `Bash` matcher. Not closing #2732.

## Head

df9bfd3011721ef28f55800629ffffb5fb659f40 (short df9bfd301), cut from origin/main 8f286293be2d03817a2de23a3a0c884ec2e94fab, no merge needed.

## Mutation proof

Delete the fix's line: `const HOOK_TOOLS = { '.claude/hooks/pre-bash.sh': ['Bash'] }` to `{}`. A settings file wiring pre-bash.sh under a `Bash` matcher then prints `MATCHER BLIND` again, as main's copy does (see Null control). The part-2 fixtures `bash-matcher.json` and `bash-under-edit-matcher.json` pin it from the other side and travel with part 2 (they need pre-bash.sh in the tree to be graded).

## Null control

`node tools/policy/policy_lint.mjs --hooks <settings wiring pre-bash.sh under matcher Bash>` on this head prints no MATCHER BLIND row (MISSING only, the script is part 2). The same command with main's copy of policy_lint.mjs (`git show origin/main:tools/policy/policy_lint.mjs`) prints `MATCHER BLIND PreToolUse (matcher) matcher "Bash" cannot fire on Edit, Write, MultiEdit or NotebookEdit`. The repository's own settings are unchanged here, so main's copies of both graders accept this head: `node <main policy_lint.mjs> --hooks` rc 0.

## Figures

- `node tools/policy/policy_lint.mjs --hooks`: HOOKS ok, 3 wired hooks pass their own self-test.
- `python3 tools/audit/carry_audit.py check --body <this body>`: reports every item routed.
- Cause of the predicted red on the combined change: `git show origin/main:tools/policy/policy_lint.mjs` run over the combined tree printed `MATCHER BLIND` and `HOOKS REFUSED: 1 of 5 hook(s)`; the branch's own `policy_lint.mjs --hooks` printed `HOOKS ok: 4 wired hook(s)`.

## Red checks

none

## Forward-carry

- Carry 0 (attribution out of hooks pending): built in this diff; the entry stays in `ignore`, so an unmatched key is DEAD again. Carry: dismissed: built in this diff, nothing left.
- Part 2 (the Bash kill hook script, its settings registration, REQUIRED entry, fixtures, prepr rows, mutants) is saved at `handoff/r10-bash-kill-hook` and re-cut on main after this merges. Lands in group R10-BASH-KILL-HOOK of dev/programme/rosters/wave-r10-groups.json. Carry: R10-BASH-KILL-HOOK

## Friction

ci-autofix: contradiction: a hook registration and the grader change that accepts it cannot land in one PR under the base-pinned grader. Carry: R10-BASH-KILL-HOOK
