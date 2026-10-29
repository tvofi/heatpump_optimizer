Fix review: blocked 2c62c682d180b6270a42d8c3a9a010fb6dd1ac4c class-open: budget-raise-gate.yml's budget-raise-gate job restores and runs the base's budget_raise_gate.py, outside restore_jobs and undispositioned

bus-nonce: 95bc79c3734d0aa5c0ff5360f87b1ea2

## Round

This is review round 5, dispatched past the three-round rule. The head is the fixer's re-cut `7d1fbc055`, carried to `2c62c682d` through two merges: `ca0a400c7` merges origin/main `66974d473`, and `2c62c682d` merges that into the previous PR head.

All three round-4 points are answered at this head:
- **Class-open on `markdown-it.min.js`: closed.** The arm now keys on each restoring job's restore pathspecs (`restored_hit`), not on a load grammar. On a commit that edits only `tools/policy/vendor/markdown-it.min.js`, `keyed_jobs` keys all three governance.yml restoring jobs, and each lists the vendored file (`ev/plant-mdit-keyed.txt`). `named_loads`, `mjs_closure`, `grader_hit` and the `GRADER_NAMED_EXEMPT` table are gone.
- **Stale head note: answered.** `## Head` names `2c62c682d`.
- **Packet `host-path` refusal: answered.** The packet rendered on this seat with no refusal (`ev/packet.txt`, `ev/review-packet.md`). It stays carried to R10-RECORD-API-O1, as the body says.

The merge delta keeps both RCA records. `dev/audit/config/bugclasses.json` is valid JSON and holds `_rca["R10-RCA-PREPR-HEAD-GRADERS"]` and `_rca["R10-RCA-FRICTION-RESIDUE"]`, and I3's `rca` list cites this record (`ev/bugclasses.txt`).

## Block

**Step 6 (the class).** I ran the body's own rule, the job that holds the step "Restore the check source from the base commit", over all of `.github/workflows/` instead of only `governance.yml`. It returns three more workflows:
- `tests.yml:603` (`briefs`)
- `pr-contract.yml:93` (`pr-contract`)
- `budget-raise-gate.yml:66` (`budget-raise-gate`)

`restore_jobs` reads only `agreement_py.WORKFLOW`, which is `.github/workflows/governance.yml` (`ev/class-open-budget-raise-gate.txt`). The record's `## 7. Recorded` "Left open" line names `briefs` and `pr-contract`. Neither the record nor the body names `budget-raise-gate`.

That job is the class exactly:
- `ci.yml:247-250` calls it on pull requests.
- Its restore pathspecs (`.claude/workflows/*.py`, `tools/policy/*.py`, `tools/pr/*.py`, `tests/layout.py`) check out the base's `tools/policy/budget_raise_gate.py`.
- `budget-raise-gate.yml:105-109` then runs that file.

A branch that edits `budget_raise_gate.py` is graded by `budget-raise-gate` with the base's copy, and this arm predicts nothing for that job. That is the same file as round 2's seam, which the arm keys only through governance.yml's `policy-docs`.

The remedy is a disposition, not more predictor code:
- Name `budget-raise-gate` in the record's "Left open" line, beside `briefs` and `pr-contract`.
- Give the open set a destination, as the finding below asks.
- Alternatively, widen `restore_jobs` to every workflow that holds the step. `budget-raise-gate` reads live reviews, so that run can only be partial.

**Split recommendation.** Do not split the group. The governance.yml arm is sound, mutation-proven and closed over its own population. What is left is one record line and one carry. If the orchestrator would rather not spend another round, the right split is:
- merge this PR as the governance.yml countermeasure once the record names all four out-of-scope restoring jobs;
- send the other workflows' restoring jobs to a new group.
Do not grow this arm again.

## Findings

- Class-open, the block: `budget-raise-gate.yml`'s `budget-raise-gate` job restores and runs the base's `tools/policy/budget_raise_gate.py`. The job is outside `restore_jobs` (governance.yml only) and is not dispositioned in the record or the body. Carry: R10-RCA-PREPR-HEAD-GRADERS
- The record's "Left open" restoring jobs in other workflows (`briefs` in tests.yml, `pr-contract`) are deferred with no destination. After the block is fixed, `budget-raise-gate` joins them. `finding-propagation.md` requires a later stage's brief to carry them before this merges. Today they are only a sentence in the record. Carry: R10-RCA-PREPR-HEAD-GRADERS
- The body's `## Red checks` section gives the `nightly-status` answer and then a stray `none.` paragraph about `5a119e8af`'s cancelled `instrument-self-tests`. The section contradicts itself: it answers a red and also says there is none. Fix the wording in the same push as the block. Carry: R10-RCA-PREPR-HEAD-GRADERS

## Evidence

- Head measured: `2c62c682d180b6270a42d8c3a9a010fb6dd1ac4c` (`ev/HEAD.txt`), from a detached worktree. Merge base is `66974d473`. `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Merge: `git merge-tree --write-tree origin/main 2c62c682d` exits 0 against origin/main `d24ee8abd` (`ev/merge-tree.txt`). There is no conflict.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched in the three-dot diff.
- The self-test, re-run at this head: `python3 -I tools/pr/ci_predict.py --self-test` prints `ci_predict self-test: 0 failed` in 118 s (`ev/self-test.txt`).
- Mutation proof, re-run with `mutants.py .`: M1 bad 5, M2 bad 1, M3 bad 1, M4 bad 1, M5 bad 3. Each FAIL label is the one the body names (`ev/mutants.txt`). No mutant survived.
- Population, at this head: `grader_gaps` on governance.yml returns `[]`. `pinned_runs` lists 7 policy-docs runs, 1 env-matrix run and 6 wave-script runs (`ev/run-population.txt`).
- CI on this head: all 68 check runs have completed (`ev/check-runs.txt`). The only red is `tests / nightly-status`. The body answers it as main's and not this diff's, and this diff touches nothing that job reads. `pr-contract / pr-contract` (123427941747) started after that red concluded and is green. `tests / mutation`, `gate`, `policy-docs`, `env-matrix`, `wave-script` and `budget-raise-gate` are green.
- Not re-taken: the 477 s, 608/609 s and 325 s plant and arm timings, the `jobtime.py` 215.5 s, and the `keycount.py` 584/69/1/71 census with its 57 s and 85 s derivations. These are heavy runs, and the block does not turn on them, so I have not verified them.
- I re-derived the population of other-workflow restore steps with a scout read of the three workflow files and `ci_predict.py` (reported in this verdict, not committed). I built no harness of my own.
