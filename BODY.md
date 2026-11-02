Refuse `pkill`, `killall` and a pgrep-fed `kill` at command position in a new PreToolUse `Bash` hook, key `policy_lint --hooks` on each script's own tool set, and drop the duplicate `attribution` entry from `field_coverage`'s hooks `pending` map (#2732, R10-BASH-KILL-HOOK; folded R10-FLY-BASH-KILL-GUARD brief carried whole). A seat ran `pkill -f` with an empty pattern, and `pkill -f tests/entities.py` on 2026-10-15 killed every seat's run of that script; the rule lived in process state only.

Not closing #2732: this branch is predicted red on `governance / policy-docs` (see Red checks), so it cannot merge as cut. Owner call needed.

## Head

efada17e901b70d0442d408f3bd987dbc3a71e1e, the merge of `origin/main` into the work branch (the `handoff/r10-bash-kill-hook` ref). Base c7aa121650058ec9f1540b5bf60ffd69eea75298; `origin/main` had moved to 8f286293be2d03817a2de23a3a0c884ec2e94fab, merged without conflict. `prepr.sh` ran on the pre-merge head 408644f7 (rc=1, only the CI PREDICT arm); it was not rerun after the merge, which touches none of the ten files.

## Mutation proof

Each run is `bash .claude/hooks/pre-bash.sh --self-test` on the mutated copy, original restored after (26 passed, 0 failed).
- Drop the pkill arm: 8 failed (every pkill row and the end-to-end exit-2 row).
- Drop the killall arm: 1 failed (`killall is refused`).
- Drop the pgrep-feed arm: 3 failed (`$(pgrep)`, `pgrep | xargs kill`, backtick rows).
- Widen to quoted text (`if at:` to `if True:`): 2 failed (`bash -c` row, `grep -n pkill` null control).
- `policy_lint`: `HOOK_TOOLS = {}` (edit-only again): `--hooks` on the repo's own settings prints `MATCHER BLIND ... pre-bash.sh` and refuses; `bash-matcher.json` and `star-matcher.json` go red.
- Failing first: with the hook's decision program stubbed out, the self-test read 11 FAIL rows; the two new fixtures were red against the old `policy_lint` (`bash-under-edit-matcher.json` rc 0 where 1 is wanted, `bash-matcher.json` rc 1 where 0 is wanted).

## Null control

Allowed, and green in the self-test: `kill 1234`, `kill $!`, `kill $(cat run.pid)`, `kill -9 1234; pgrep -f x` (different statements), `grep -n pkill file`, `git log --grep=killall`, `echo "never pkill"`, single-quoted `killall`, a heredoc body holding `pkill -f x`, a `#` comment, `git status` (prefilter path). End to end over stdin: unparseable payload and non-object `tool_input` exit 0. `pre-bash.sh` under a `Bash` matcher is accepted; under the edit matcher it is refused (`bash-under-edit-matcher.json`), and `pre-edit.sh` under `Bash` is still refused (`bad-matcher.json`). The three existing matcher null controls (`star`, `no`, `empty`) gain a `Bash` group and still pass.

## Figures

- `bash .claude/hooks/pre-bash.sh --self-test`: 26 passed, 0 failed.
- `node tools/policy/policy_lint.mjs --hooks`: 4 wired hooks pass their own self-test.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. No budget moved.
- `node tools/policy/field_coverage.mjs`: FIELD COVERAGE ok, blind=0 dead=0 refused=0.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2592 ENTITY CHECKS PASSED.
- `python3 tests/closure.py select`: MODE: SCOPED, selects `tests/entities.py` only; `.claude/` and `tools/policy/` are INERT prefixes, so the new script needed no classification line.
- Census of the class (name-kill calls in tracked non-doc files): `git grep -nE '(^|[;&|(`]|\$\(|sudo |xargs )\s*(pkill|killall)\b' -- ':!dev/' ':!*.md'` returns only `pre-bash.sh` itself (its self-test rows and comments). `tools/audit/seat/cloud_dispatch.py:210` mentions `pkill` in a rule sentence, not a call. No tracked script needs editing.

## Red checks

`governance / policy-docs`: predicted red by `prepr.sh` step 6d, two arms, both from the pinned grader. The base's `policy_lint.mjs --hooks` tests every PreToolUse matcher against the edit tools only, so it reads this PR's `Bash` group as `MATCHER BLIND` (the fix to that is in this same diff, which CI does not use for grading); `field_coverage.mjs` then refuses because the base's grader leaves settings red before perturbing. Cheaper detector: `prepr.sh` step 6d already predicted it before handoff. The settings change and the grader change cannot land in one pull request under a pinned base grader. Options for the owner, none taken here: (a) land the `policy_lint` change first with `.claude/settings.json` split out into a follow-up, (b) register the group with no `matcher` (fires on every tool, passes the old grader, costs one prefilter `case` per non-Bash call), or (c) accept the red under the code-owner override. The roster names matcher `Bash`, so I kept it.

## Forward-carry

- Carry 1 (`attribution` out of hooks `pending`): built.  The entry was in both `ignore` and `pending` at the base; `pending` is now gone from the hooks registration, so an unmatched entry is DEAD again (`field_coverage.mjs`: dead=0 with the key present). Carry: dismissed: built in this diff, nothing left.
- Carry 2 (folded R10-FLY-BASH-KILL-GUARD): built for items 1 to 5, with the hook script `pre-bash.sh`, settings entry, `policy_lint` keyed on script, `REQUIRED` entry, self-test rows and mutants as listed. Item 6 (ownership and effect) is the orchestrator's: `.claude/hooks/` and `.claude/settings.json` are code-owned, and a local seat loads the hook only once its checkout advances. Carry: #2732
- Departure from the dispatch text: it says the hook "fails closed"; the roster brief says fails open, exits 2 only on a positive match, and models `pre-edit.sh`. I followed the roster. Known gaps are in the script header: a name held in a variable, a wrapper option taking a value (`sudo -u root pkill x`), and a pid list built in an earlier statement. Carry: dismissed: recorded here, roster words govern.
- `prepr.sh`'s hooks loop gained `bash-under-edit-matcher` (refused) and `bash-matcher` (passes); outside the listed files, required by the test-first rows. Carry: dismissed: built in this diff, nothing left.

## Friction

ci-autofix: contradiction: a PR that adds a hook registration and the grader change that accepts it is predicted red by the base's pinned grader, with no one-PR path; the group's file list puts both in one PR. Carry: #2732
