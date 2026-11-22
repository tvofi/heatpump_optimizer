CI decision cards CI-1, CI-2, the workflow part of CI-5, the cap part of CI-7, and CI-17, from the 2026-11-21 CI bottleneck study. Owner approval 2026-11-21 (decision cards), built as a tooling-freeze exception. This is the workflows half. The policy-and-instruments half (CI-4's reading, CI-5's rule text, CI-6) is its sibling PR. CI-16 was approved, then dropped by the owner the same day, and is not built.

**CI-1: one full run per bot-pushed head.** Before this change, a head the merge-main bot, `claims-autofix`, `closures-autofix` or `mutation-autofix` pushed with `GITHUB_TOKEN` got two code runs:
- the `pull_request` run, held `action_required` and then approved by `hpo-runs`;
- a `workflow_dispatch` of `ci.yml`, sent from the push step.

Now the dispatch goes only to a pushed head whose held `CI` run was **not** approved: absent secrets, a refused approval, or none held in the poll window.
- `merge-main.yml`: the approve step records `branch sha` in `approved.txt` for each approved run named `CI`. A new last step, under `if: ${{ !cancelled() }}`, dispatches every pushed branch not in that file. A failed approve step therefore still dispatches, so no pushed head is left unrun.
- The three autofix jobs in `tests.yml`: the push steps no longer dispatch. Each approve step sets `approved_head=true` when it approved a `CI` run at the pushed head. A following step dispatches only when it did not.

**CI-2: a dispatched run is scoped the way a `pull_request` run is.** `tools/ci/prelude.py` gains `dispatch_diff`: `origin/<base>`'s SHA and the three-dot file list, read from the prelude's `fetch-depth: 0` checkout. For a dispatch that names a PR, has passed `verify_dispatch` and is not on a `batch/` ref, `outputs` scopes the CodeQL legs, `machinery`, `machinery_rowblind` and `selftests` exactly as for that PR's `pull_request` run. It fails closed: when the diff is unreadable or empty, every leg analyzes and every lane runs, as today. Batch proofs keep their own rule (r10-proof-codeql). The prelude runs the base's copy of itself, so this takes effect once it is on `main`.

**CI-5, workflow part: push-to-main runs are coalesced, never cancelled mid-flight.** In `ci.yml`, a push's first attempt joins one `CI-main` group with `cancel-in-progress: false`:
- One push run executes at a time.
- GitHub replaces a pending one with the newest before it starts.
- No started run is cancelled.

Every other event, and every re-run (attempt 2 or later), keeps its run-id group. A gate re-run therefore never displaces the pending main tip, and N1's hazard of a re-run cancelling a live run stays excluded. The policy sentence ("within one burst") is in the sibling PR.

**CI-7, cap part.** `tests / mutation-pins` `max-parallel` goes from 12 to 4. The head-kind skip was a trial on the card and is not built.

**CI-17: cache pip.** Every `setup-python` step in a job that pip-installs the hash-locked `tests/requirements-*.txt` now sets `cache: pip` with `cache-dependency-path: tests/requirements-*.txt`. That is 15 steps across `tests.yml`, `governance.yml`, `kernel-points.yml`, `nightly.yml` and `.github/actions/nightly-ha/action.yml`. A lock change is a new key, and `--require-hashes` still verifies every wheel a cache hit supplies. `setup-node` is unchanged. The study measured it as fast, and the one heavy node toolchain, the browser lane's Chromium, is already cached, keyed on `tests/pwlane/package-lock.json`.

`tests/entities.py` pins each of these:
- CI-5: the concurrency group, rendered per event and attempt.
- CI-1, merge-main: the order of the approve and dispatch steps, the dispatch's `if:` and the `approved.txt` record. The dispatch step is executed under `bash -e` against a stub `gh` and must dispatch exactly the unapproved branches.
- CI-1, autofix: per job, no dispatch from the push step, and a dispatch gated on `approved_head`, which is set only for an approved `CI` run.
- CI-7: `max-parallel: 4`, below `mutation_table.MAX_SHARDS`.
- CI-17: the cache lines on every pip-installing job, with each `-r` file inside the key's glob.

## Head

2eea9dc5590003aff93be979025c9744d4dd4063, one commit on origin/main 6fdc15354f0f6f4613370fdabe4bd82adbadc087, measured 2026-11-22T05:05Z (origin/main then f88ec8f8fa; the merge is clean). `git merge-tree --write-tree origin/main HEAD` prints one tree.

The finder's harness is the study's job-minute census of the CI run history, which only a merged workflow can move. This PR does not re-run it. The study's next read after merge is the before/after measure: dispatched code runs per bot-pushed head, python CodeQL legs analyzed on dispatches, push runs cancelled in progress, and peak `mutation-pins` concurrency. The companion the tree can measure is the prelude's own reading of a verified dispatch of a doc-only diff. At the base, it analyzes every leg and runs every lane. At the head, it skips every leg, idles `machinery` and scopes `selftests` (the `CI-2:` arms in `python3 tools/ci/prelude.py --self-test`).

Local overlay, declared: this branch's prepr ran with an untracked `find` shim ahead on PATH. The shim answers `-mmin -0` with no match and passes every other call through. Without it, two `prepr.sh --self-test` P351 rows fail on this host whatever the branch: `ancestry_reds` turns `PREPR_ANCESTRY_TTL_S=0` into `find -mmin -0`, which the host's BSD find matches for a file written in the current second, so a TTL-0 fixture reads the previous fixture's kept lines. The same rows failed on `fix/ci-cards-b`'s tree. The fix belongs to round-end triage (workaround P-R11-PREPR-TTL0-FIND), not this PR.

## Mutation proof

`tools/ci/prelude.py` was mutated in place and run with `python3 tools/ci/prelude.py --self-test`:

| mutant | killed by |
|---|---|
| `scoped` never set to `pull_request` | `CI-2: a verified PR dispatch of a doc-only diff skips every leg, idles machinery, scopes self-tests` |
| `if got and got[1]` becomes `if got` | `CI-2: an empty diff analyzes every leg and runs every lane (null control)` |
| `and not why` dropped | `CI-2: an unverified dispatch analyzes every leg and runs every lane (null control)` |
| the `batch/` exclusion dropped | `CI-2: a batch/ proof naming a PR analyzes every leg and runs every lane (null control)` |

Workflow mutants: each pin in `tests/entities.py` is checked against a planted copy of the real workflow text, and each plant must be refused. A plant that the check accepted would fail the run.
- **CI-5:** the pre-change group (`every push in its own group`); `push re-runs in the main group`; `the main group cancelling in progress`.
- **CI-1, merge-main:** the dispatch step placed before the approve step; the dispatch skipped after a failed approve step; an approval recorded for any workflow; and an executed null control whose dispatch ignores `approved.txt` and so dispatches an approved branch.
- **CI-1, autofix (per job):** a dispatch from the push step; a dispatch beside an approval; `approved_head` set on any approval.
- **CI-17:** `tests.yml` with one job's cache lines stripped.
- **CI-7:** a value check, not a plant: the pins check reads `mutation-pins`' own `max-parallel` line from `tests.yml` and requires exactly 4, below `mutation_table.MAX_SHARDS`, so the old 12 fails it.

## Null control

- The prelude's null arms each analyze every leg and run every lane: an unreadable diff, an empty diff, an unverified dispatch, a dispatch naming no PR, and a `batch/` proof naming a PR. A temporary git repository shows that `dispatch_diff` returns None for a base ref that does not exist.
- merge-main's dispatch step, executed over two pushed heads, dispatches both when `approved.txt` is absent, empty, or names `fix/a` at a different SHA. It dispatches only `fix/b` when `fix/a` was approved at its pushed SHA, and nothing after a PAT push.
- The CI-5 render keeps `CI-99` (a run-id group) for every event but a push's first attempt.

## Figures

The scope-line figure block is omitted. The gate's MODE line, from `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`, is `MODE: FULL`, because `.github/actions/nightly-ha/action.yml` changes the gate itself. CI runs the full suite.

- `python3 tools/ci/prelude.py --self-test`: `prelude self-test: 89 checks, 0 failed`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `1 of 2735 ENTITY CHECKS FAILED`. The one failure is `a measured script's late-writing descendant is waited for, not recorded as nodata`, a host failure this diff does not reach. That check drives `tools/coverage/coverage_tree.sh` and reads no workflow. Run alone by a scratch driver (`crv_probe.py`, which execs `_coverage_revalidation` by `ast`), it fails the same way on the sibling worktree, whose `tools/coverage/coverage_tree.sh` and `tests/entities.py` are the base's byte for byte. The first run at this branch printed `8 of 2735` failures. Six were this diff's pins reading the new text wrongly, and they are fixed (next bullet). The other two were host failures: this one, and `hb:positive_control`, a timing check that passed on the rerun.
- The six fixes, all in `tests/entities.py`:
  - The autofix `if:` is rendered with the two step outputs substituted as literals, because `_ghx` reads no `steps.` context.
  - The merge-main record is matched in the YAML value, whose block indent is stripped.
  - CI-17's `-r` reader takes only a `.txt` requirements file, not `read -r line;`.
  - The concurrency model `_cc_value` and `_cc_pr_event` gains `format()` and `github.run_attempt`, and `_CC_COALESCED` names CI-5's `(ci.yml, push)` shared group.
- The pins' planted mutants, read by a scratch driver that execs the predicates by `ast` over the real files (`ent_probe.py`):
  - Each real file reads clean.
  - Each plant is refused: the dispatch beside an approval (per autofix job), an approval recorded for any workflow, no `!cancelled()`, one stripped cache pair, and the pre-CI-5 `CI-${{ github.run_id }}` group.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`, with the declared `find` shim: rc 0, its receipt written for `2eea9dc55900`. `self-test` 571 passed, 0 failed; `ci predict` predicts no closures, fast, governance or instrument red.

## Red checks

none

## Forward-carry

none

## Friction

none
