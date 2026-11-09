R10-HOTFIX-CODEQL-HEADROOM part 2 (topic r10-hotfix-codeql-headroom-p2)
Closes: none (triage ruling P463; design note design/r10-hotfix-codeql-headroom sections 3 and 7)
Cap change only: the module-scope-try wrap is not used, tests/features.py is untouched and no file is excluded from the scan.

Main's `codeql / Analyze (python)` job outgrew the job-level 45-minute cap. The cap moves into the matrix `include` entries of `.github/workflows/codeql.yml`: python 75, actions and javascript-typescript 45, with `timeout-minutes: ${{ matrix.timeout }}`. The cap-paragraph comment is rewritten. The `tests/entities.py` pin (`_analyze_cap`) now reads the include entries: `timeout-minutes` is exactly the matrix expression, python an int at least 51 (the design's projected worst case), each other leg exactly 45. Check count unchanged. The brief's "do not edit tests/entities.py" binds that file's structure; "every check must still pass" forces this one pin's edit. Alternatives (blanket 75, three jobs, refuse) lost as in design section 4. A stopgap; the structural cure (split tests/features.py) awaits an owner ruling, design section 5.

## Head

Code head a325da3809246b9571938795021f9b7a03bba2ea (merge base 3fdaa9da9ab667042338fcf034147bde16b91fe4, origin/main at 2026-11-09T04:59Z).

## Mutation proof

Run: `PYTHONPATH=tests/hastub python3 tests/entities.py` on the pin, mutating the workflow's predicate values; baseline restored after each.
- Before the YAML change (pin rewritten first): FAIL "codeql.yml's analyze cap is per leg: ..." (include caps={}), 1 of 2668 checks failed.
- Head: ok, ALL 2668 ENTITY CHECKS PASSED.
- python 75 to 50: FAIL (1 of 2668).
- actions 45 to 75: FAIL (1 of 2668).
- drop python's timeout from the include entry: FAIL (1 of 2668).
- comment-only edit: ok, ALL 2668 ENTITY CHECKS PASSED (diff stat shows the file modified).

## Null control

The two legs left at 45 read 45 in the diff (`git diff $(git merge-base origin/main HEAD)...HEAD -- .github/workflows/codeql.yml` shows actions and javascript-typescript at 45); the pin fails when actions is raised to 75 (mutant above). Runner-speed control for the PR's own python job: tests/closure.py extraction time in that job's log against the base job's, to be read from the PR's own run; this seat opens no PR and cannot report it, the reviewer reads it at the head.

## Figures

- Python jobs of main's ci.yml push runs, newest 20, at merge base 3fdaa9da, taken 2026-11-09T04:59Z: 10 cancelled at 45.1 min and 10 other; capped (duration >= 44.9 min) also 10, equal to the cancelled count (null control: a cap that did not bind would show cancelled below capped). Enumerator: `python3 -I py_jobs.py` (scratch; `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs?filter=all` over `ci.yml` push runs on main, jobs named `codeql / Analyze (python)`, duration = completed_at - started_at). The newest of the 20 started 2026-11-09T03:06Z; window 2026-11-08T15:23Z to 2026-11-09T03:06Z.
- Fixture and claim files: none moved; `git diff $(git merge-base origin/main HEAD)...HEAD --stat` lists only codeql.yml and tests/entities.py.

## Red checks

none

## Brief carries

- Carry 1 (item 93aad749, extra CodeQL figures via a ci.yml dispatch with inputs empty): no extra figure was needed or dispatched; this seat makes no GitHub writes. Carry: R10-HOTFIX-CODEQL-HEADROOM|dismissed: not applicable, no dispatch made
- Carry 2 (item e017bcd8, the brief's dispatch-inputs contradiction): resolved by the per-leg matrix form of design section 3, as the note states. Carry: R10-HOTFIX-CODEQL-HEADROOM|dismissed: followed as designed
- Carry 3 (item 6e003ed3, leave tests/features.py and the wrapping alone): honoured, the diff touches only .github/workflows/codeql.yml and tests/entities.py. Carry: R10-HOTFIX-CODEQL-HEADROOM|dismissed: followed as designed

## Forward-carry

- Reopen trigger for this group: any python job capped at 75, or a 7-day python p90 over 65 min; the structural cure (split tests/features.py) is put to the owner as a new group. Carry: R10-HOTFIX-CODEQL-HEADROOM|dismissed: already recorded in design note sections 5 and Reopen trigger on design/r10-hotfix-codeql-headroom

## Friction

none
