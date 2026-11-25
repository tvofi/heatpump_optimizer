Fix review: blocked d339e84355ce1be351fd42c77ccafd2694b08dbf class-open: code_red counts units whose grader the stale pin restores (tests / briefs, governance / policy-docs, governance / wave-script, governance / env-matrix, codeql / Analyze), which the fresh dispatch re-grades with fresh programs

bus-nonce: 59cbf798e0d16a714b2518706b48270a

Round 1 (first review of #3895). Measured at d339e84355ce1be351fd42c77ccafd2694b08dbf; merge base bb6377b4da.

## Block

`Sweep.code_red` (tools/ci/sweep.py) treats every `gate.REQUIRED["no-pr"]` unit as "the PR head's own code, which no pin restores". The module doc and the PR body both say so. For 4 of those units, plus the codeql analyses, that is false. Under a pull_request event each one restores its grader from `github.event.pull_request.base.sha`. Under the sweep's workflow_dispatch it restores the grader from a fresh `origin/<base>`. See `ev/pinned-graders.txt`: tests.yml:674 `briefs`, governance.yml:145/256 `policy-docs`, :1805 `env-matrix`, :1907/1992 `wave-script`, codeql.yml:182/202 `analyze`. A red in one of these units under a stale pin can be the pin's own verdict, and re-judging that is the job the STALE-PIN dispatch exists to do. The fix now leaves that red standing until the next push.

The PR's own corpus shows this happens. On 2026-11-22, dispatch run 45005979443 at head 3883d9bb99 has the line `left governance / env-matrix, governance / policy-docs, governance / wave-script, tests / briefs` in `ev/stalepin-head-2026-11-22.txt`. At this head the sweep would not have fired it. Under fresh programs, that dispatch turned 3 of those 4 units green: env-matrix, wave-script and briefs succeeded, and policy-docs failed (`ev/run-45005979443-units.txt`). So the premise "a fresh run grades the same code again", and the body's "none ended green" taken as unit evidence, do not hold for this set. The fix withholds a run that a required check needed.

Self-test demonstration (`ev/reviewer-null-cases.diff`, `.out`): I added 2 cases to the head's own null loop, `tests / briefs` red and `governance / policy-docs` red. Each expects one dispatch. Both FAIL at this head (`sweep self-test: 114 checks, 2 failed`).

Remedy space (the fixer's to choose): restrict code_red to units that no pin grades, derived from the workflows rather than listed by hand; or exempt units whose grader is pinned; or dispatch whenever any red unit is pin-graded. Whichever is chosen needs a self-test case per pinned unit kind.

## Findings

- Surviving mutants on the diff's own predicate, at this head (`python3 tools/ci/sweep.py --self-test`, 112 checks). M6: `j.get("status", "completed") == "completed"` -> `True` survives (rc 0). No case puts an in-progress newer job beside an older red. M7: ordering key `(started_at, run_id)` -> `(run_id, started_at)` survives (rc 0). The "red then green" null uses a later id and a later start together, so the newest-started rule, which the module doc says ids cannot stand in for, is untested. Carry: #3885
- Note: figure: sweep.py's module doc and the `code_red` docstring say "none of the 17 STALE-PIN dispatches of 2026-11-22/23". The body and this re-run count 16 (14+2: `ev/stalepin-head-2026-11-22.txt`, `-2026-11-23.txt`). Carry: #3885

## Evidence

- RESULT: mutation proof at head. M1 guard off, M2 `!= "success"`, M3 first-wins, M4 `REQUIRED["pr"]`, M5 `return False` each fail exactly the case the body names (rc 1). M6 and M7 survive (above). Unmutated: 112 checks, 0 failed. Carry: dismissed: evidence, not a finding
- RESULT: harness, both ends. I ran the fixer's `ci3885_light.py stalepin` and the finder's `dup` from detached worktrees at the head and at the base `bb6377b4da`, with the head's harness file copied in. They reproduce the body: 11-22 head `leaves 9 (2865 runner-min) and still dispatches 5 (3357); unattributed 7 (6412)` and base `leaves 0 ... dispatches 14 (6222)`; 11-23 head `leaves 2 (304)` and base `leaves 0 ... dispatches 2 (304)`; `dup 2026-11-22` `21 runs, 12635 runner-min; sole grader: 14 runs, 4666`. On 11-25, head `leaves 3 (924) ... dispatches 1 (421)`: the run counts match and the minutes grew because the runs have since finished, as the body says they would. The `stalepin` arm is the fixer's instrument, not the finder's. Carry: dismissed: evidence, not a finding
- RESULT: local harness adaptation, disclosed. This seat's gh 2.89.0 rejects `--allow-escape-sequences`, so every log read came back empty and all dispatches read `unattributed` (first run kept in `ev/stale-run1/`). I removed the flag in both worktree copies only (`ev/harness-local-patch.diff`) and nothing was pushed. That arm silently reports `unattributed` when its gh lacks the flag. Carry: dismissed: evidence, not a finding
- RESULT: null control (the body's). The base tree with no `code_red` leaves 0 on every day, as the body states. The three committed self-test nulls pass. Carry: dismissed: evidence, not a finding
- RESULT: `git merge-tree --write-tree origin/main d339e843` exits 0 (tree 23a69b62), with no conflict. VERSION, the manifest, RELEASE_NOTES.md and the golden fixtures are untouched; the diff has 4 files (`ev/diff-files.txt`). Carry: dismissed: evidence, not a finding
- RESULT: CI. `merge_train.py classify` was still WAIT when this verdict was written (`pending: gate red: none`). No check is red at this head, so no red is owed an answer. The block is on code, not CI. Carry: dismissed: evidence, not a finding
