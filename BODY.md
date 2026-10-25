R10-PROOF-CODEQL (size S, orchestrator-sourced under mandate 6329234399; triage ruling P158 in PR #2829). A merge-train batch proof analyzed every CodeQL leg in full, and the python leg held the 2026-10-25 s41 batch-1 proof after every other check was green. With this change a proof skips a leg when every entry head it merges already analyzed that leg, or legitimately skipped it, at that head. The skipped leg uploads the stand-in category, as a skipped pull-request leg does.

**This revises DESIGN-P2 D-5's push arm for proof refs only, under mandate 6329234399.** Pushes to `main` and every other event still analyze every leg in full, so main keeps a full analysis of every merged tree. The D-5 extracted-files soundness step still runs on every push.

**The proof is a dispatch, not a push.** `ci.yml`'s `push` trigger fires on `main` alone. A proof is `merge_train.py`'s `launch`: it calls `app_push.sh --branch-only` and then runs `gh workflow run ci.yml --ref batch/<tag>-<n> -f recheck=true` (`DISPATCH`). The arm the brief calls "a push to a `batch/` ref" is therefore keyed on `workflow_dispatch` with `GITHUB_REF` under `refs/heads/batch/` and no `pr` input. An actual `push` to a `batch/` ref analyzes; the self-test pins that.

What changed:
- `tools/pr/codeql_scope.py`:
  - `decide` gains the proof arm. It fails closed: a changed file under `.github/` analyzes, an unreadable or empty entry list analyzes, and an entry head without the leg analyzes.
  - `proof_entries` reads and verifies the proof chain. Each link must carry `merge_train.build`'s subject, have the two parents that subject names, and have a tree equal to `git merge-tree --write-tree` of those parents. A forged or misnamed link returns `None`.
  - `proven_legs` reads the evidence. A leg counts only when `codeql / Analyze (<leg>)` is `completed`/`success`; a skipped leg's job concludes success too.
- `tools/ci/prelude.py`: `proof_scope` reads the chain, the proof's changed files (`changed_files(base, tip)`) and each entry head's `pull_request` runs of `ci.yml`. A dispatch run at an entry head is no evidence. Any `ApiError` or git failure gives `([], None)`, which analyzes every leg.
- `.github/workflows/ci.yml`:
  - The prelude restore step gives a dispatch on a `batch/` ref main's programs, taken from the proof's merge base with main, never the entries' copies.
  - It also restores `tests/closure.py`. That is `codeql_scope.changed_files`' producer (#2406), and it was previously run from the checked-out tree. A pull request, or a proof entry, editing it chose the changed-file list its own skip was decided on.
- `tests/entities.py`: pins that restore (batch arm, merge base, and both files restored).
- `.github/workflows/codeql.yml` and `governance.yml`: comments corrected (step 9). Their old text said every non-`pull_request` event analyzes.

What a skip does not cover: a proof does not analyze anything its entries' interaction alone could add (cross-entry dataflow). Main's push run after the merge analyzes that in full, as before. The stand-in on a proof is main's newest error-free analysis, because the dispatch carries no `pull_request.base.sha`. A proof's code-scanning upload is read by nobody: the train reads check contexts only.

Alternatives considered:
- Skip by O17's suffix rule over the proof diff. Rejected: a proof's diff is the union of the code entries, so it almost never stays inert, and it would not have moved the measured hold.
- Read code-scanning analyses instead of jobs. Rejected: a PR's analyses are keyed on its test-merge commit, not its head, so they cannot be matched to an entry head.
- Pass the proof's base sha through to `codeql.yml` for an at-base stand-in. Rejected: it adds a callee input and an entities re-pin for an upload nothing reads.

## Head

d4b5be92f codeql_scope arm, 189cb733e comment, 7ac871272 restore and pin. Everything below is measured at 7ac871272bc1725a882d9538e359b3aa71a52d87, cut from origin/main c9cbe6b458a7053f914649eb02d5296d6cd8c0f4. The checks ran before the three commits were re-authored, which changed one commit's author identity and nothing else; the head's tree is byte-identical to the tree measured.

## Mutation proof

Each mutant was applied to a scratch worktree at d4b5be92f; `git diff d4b5be92f 7ac871272 -- tools/` is empty, so those files are the head's. Each was then checked against `python3 -I tools/pr/codeql_scope.py --self-test` and `python3 -I tools/ci/prelude.py --self-test`, and restored:
- M1, proof arm off (`proof = False`): 5 codeql_scope FAILs, including "a proof whose entries all analyzed python skips it". Also 2 prelude FAILs ("proof: full evidence skips every leg").
- **M2, skips on any push** (`proof = event != "pull_request"`): 9 FAILs, including "push to main analyzes python on the same evidence (null control)", "a push to a batch/ ref analyzes python: the proof is the dispatch" and "a dispatch on main analyzes python".
- M3, `.github/` force deleted: 3 FAILs ("a proof's .github/ change analyzes <leg>"), plus 1 prelude FAIL.
- M4, bare-entry check deleted: 2 FAILs ("a proof with one entry lacking python analyzes python"), plus 2 prelude FAILs.
- M5, `if not proven` → `if proven is None`: 1 FAIL ("a proof with no entry analyzes").
- M6, tree re-merge deleted: 1 FAIL ("proof_entries: a link whose tree is not its parents' merge is refused").
- M7, parent naming deleted: 1 FAIL ("proof_entries: a link naming another head is refused").
- M8, any job state counts: 1 FAIL ("proven_legs: only a completed, successful codeql job counts").
- M9, the run-event filter deleted: 1 prelude FAIL ("an entry with no pull_request run analyzes every leg (a dispatch run is no evidence)").
- M10, a `pr`-naming batch dispatch treated as a proof: 1 prelude FAIL ("a batch/ dispatch naming a pr analyzes every leg on full evidence (null control)").
- M11, `proof_scope`'s failure return replaced by `(files, {})`: survives, because it is equivalent. `decide` refuses an empty `proven` (M5 pins that), so the leg still analyzes.

The entities pin was mutated by executing its own source lines over a mutated `ci.yml`:
- the batch arm deleted: FAIL;
- `tests/closure.py` dropped from the restore: FAIL;
- the proof restoring its own tip (`git rev-parse HEAD`) in place of the merge base: FAIL;
- the head: ok.

## Null control

- At the base c9cbe6b458a7, `decide` returns `analyze` for any event except `pull_request`, so every proof leg analyzed in full.
- At the head, the same evidence under `push` to main, under a dispatch on main, and under a `push` to a `batch/` ref analyzes every leg. These are the codeql_scope self-test rows "push to main analyzes <leg> on the same evidence (null control)" and the prelude rows "push to main / a dispatch on main / a batch/ dispatch naming a pr analyzes every leg on full evidence (null control)".
- The restore step was run in a throwaway repo, with main moved past the proof's base. On `GITHUB_REF=refs/heads/batch/t-1` it restored all three programs as main's copies from the merge base, not main's moved tip. On `GITHUB_REF=refs/heads/main` with no base (the null control) it left the tree's own copies.

## Figures

- `python3 -I tools/pr/codeql_scope.py --self-test` prints its tally line with 0 failed at the head (the new proof rows are part of that tally).
- `python3 -I tools/ci/prelude.py --self-test` prints its tally line with 0 failed at the head.
- `python3 -I tools/ci/gate.py --self-test` and `python3 -I tools/ci/codescan_wait.py --self-test` (both import prelude) print 0 failed.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL <n> ENTITY CHECKS PASSED` at the head. With the container's `BASH_ENV` set, two checks fail at any tree (see Friction).
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `python3 tests/harness_headers.py` passes.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL`, because `.github/workflows/ci.yml` changes the gate itself. Locally I ran the scripts whose recorded closure in `tests/closures.json` holds a changed file (`tests/entities.py`, `tests/harness_headers.py`), plus the `run_always` lines; CI runs the rest.
- Before: proof wall time on the last four `batch/` proof runs of `ci.yml`. I listed them with `actions_list list_workflow_runs ci.yml event=workflow_dispatch` and their latest jobs with `list_workflow_jobs <run>`. The hold is `codeql / Analyze (python)`'s completion minus the latest completion of any other successful non-gate job, both measured from the run's first job start:

  | run | branch | python leg | python end | other end | hold |
  |---|---|---|---|---|---|
  | 40222343141 | `batch/20261025-183357-1` | 33.1 | 34.3 | 17.2 | **17.1** |
  | 40210241293 | `batch/20261025-124825-b5-1` | 20.5 | 45.5 | 43.0 | 2.5 |
  | 40199336598 | `batch/20261025-124825-b2-1` | 24.3 | 25.6 | 32.7 | 0 |
  | 40147334039 | `batch/20261024-231508-m2-1` | 22.1 | 27.5 | 30.5 | 0 |

  All values are minutes; "other end" is `tests / *`. The null control is that a proof whose `tests` lane ends last shows hold 0, as two of the four do. So the change saves the hold, not the python leg's duration, and only when every entry analyzed python at its head.
- After: **not measured**. A skip needs this decision on main, whose copy the proof restores, so no proof can take the new arm before this merges. That is owed over at least three batches after merge.

## Red checks

none. The tree is predicted green: `tools/pr/ci_predict.py --base origin/main` predicts no closures, fast, wave-script or instrument red. Main's push `tests / ci-ratchet` red (the artifacts listing) is main's, and this diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

none

## Friction

- gate-scoping: cost: in this cloud container `BASH_ENV=/etc/profile.d/hpo-toolchain.sh` re-prepends the toolchain to `PATH` in every `bash -c`. A `PATH`-planted fake `python3` is therefore never run, and `tests/entities.py` fails "gate-sweep.yml: on CI's completion…" and "graders-head-copy's delivery_status step…" at any tree. The same run under `env -u BASH_ENV` passes every check. Carry: dismissed: the container's BASH_ENV is environment configuration outside the tree, reported in the handoff result
