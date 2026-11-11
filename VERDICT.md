Fix review: blocked f4532701a9d41e1b53a868a8df99a4734151623d mutation-survivor: the main-push full-set pin survives inverting or bypassing its guard

bus-nonce: fc97a06cd277775bb5b21466ee24d0dd

Round 1, at the handoff tip. No pull request exists yet, so there is no review packet and no CI to read.

## Block

- The new check "codeql.yml: tests/ and dev/ are ignored on a pull request's python leg only; a full run ignores workflow scripts alone" (tests/entities.py, the `_CODEQL_GUARD` check) only checks that the guard text appears once and that the two JSON lists exist. It never checks how the guard selects between the lists. Two one-token mutants of codeql.yml that make main's push run ignore tests/ and dev/ both keep `tests/entities.py` green (rc=0, check `ok`):
  - M2 `${{ !(github.event_name == 'pull_request' && matrix.language == 'python') && ...` turns the selection around: every non-PR run, including main's push on all three legs, gets the tests/dev list, and only the PR python leg keeps the full set.
  - M3 `(... matrix.language == 'python' || true)` makes every run ignore tests/ and dev/.
  
  Main's push run is the only full python analysis (there is no schedule). A run that analyses less still goes green, so no CI lane would notice either mutant. That means the ruling's one protection, "main's push run keeps the full path set", is not pinned, even though the check's name says it is. Fix: pin the whole expression shape, for example a full anchored match of `${{ (<GUARD>) && '<PR list>' || '<BASE list>' }}`, or evaluate it for (push|pull_request|merge_group|workflow_dispatch) x (3 legs). Then show M2 and M3 going red. The deployed expression itself is correct (Evidence), so this block is about the pin, not the behaviour.

## Findings

- Follow-up: the body leaves two measurements to the first PR run: the python leg's before and after job seconds, and whether ignored-path alerts show as fixed in the PR alert view under the shared category. I could not re-derive either without CI, and both stay unmeasured. Carry: dismissed: the body already routes both to the orchestrator; this verdict adds nothing to them

## Evidence

- RESULT head: handoff/r10-codeql-pr-paths = f4532701a9d41e1b53a868a8df99a4734151623d, same as the body's `## Head` (ev/HEAD.txt). Diff is .github/workflows/codeql.yml and tests/entities.py only. VERSION, the manifest, RELEASE_NOTES.md and the claim files are untouched (three-dot diff is empty).
- RESULT merge: `git merge-tree --write-tree origin/main f4532701a9d41e1b53a868a8df99a4734151623d` rc=0 (tree 56f8e9b74), with the head 11 commits behind origin/main ee64358be.
- RESULT null control M0 (unmutated head): `PYTHONPATH=tests/hastub python3 tests/entities.py` rc=0, both codeql checks `ok` (ev/entities-M0.txt).
- RESULT mutation proof M1 (the body's: drop ` && matrix.language == 'python'`): rc=1, the new check FAILs (ev/entities-M1.txt). This reproduces the body's claim.
- RESULT M2 (guard negated) rc=0, check ok: SURVIVOR. RESULT M3 (guard `|| true`) rc=0, check ok: SURVIVOR (ev/mutant-M2.diff, ev/mutant-M3.diff, ev/entities-M2.txt, ev/entities-M3.txt).
- RESULT expression at head, simulated by this reviewer in Python with the `a && 'x' || 'y'` idiom (the reviewer's instrument, not the Actions evaluator): push, merge_group and workflow_dispatch on all legs, and pull_request on actions and javascript-typescript, ignore `.claude/workflows/*.js` only; pull_request on python ignores that plus tests/** and dev/**. So main's push scan is not dropped at this head. The D-5 push-only step and ci.yml's `codeql` caller are unchanged.
- Other readers of the config: tests/closure.py names codeql.yml's paths-ignore only in a comment, and no other tool reads the init config.
- Red checks: none. No PR or CI run exists at this head. `merge_train.py owed-reds` (ev/owed-reds.txt) lists `codeql / Analyze (python)`, so the context stays required as the ruling says.
- Figures I could not re-derive: the 2173-3623 s and 48-104 s job times in the header and body, because they need authenticated CI run data, which this seat does not have.
- Forward-carry: the body states none, and the change constrains no later stage.
