Part of #201.

The owner's rulings of 2026-10-03 (tvofi):
- Useful tools belong under `tools/` on `main`, as a permanent repository mechanism.
- Above all, the programme's own instruments (whatever merges, approves, carries, stamps, gates, watches CI or records state) are tracked, self-tested files.
- Audit instruments are not code-owned. Ownership follows decision 0013, which stands unamended.

That day a temp cleanup deleted `/private/tmp/audit-7`. It took the seat venv the `~/hpo-seats/bin` shims ran (built by hand, with no recipe anywhere), the state three tracked seat scripts kept there, and the design note decision 0012 cited.

This pull request does three things.

1. **Lands the instruments and recipes** that lived only in scratch or in `~/hpo-seats/bin`:
   - the merge train (`tools/audit/seat/merge_train.py`);
   - the seat venv recipe (`tools/audit/seat/seat_venv.sh`) and its two shims;
   - the PR open and update scripts (`open_pr.sh`, `update_pr.sh`);
   - the thermal_model parity harness (`tools/audit/harnesses/thermal_parity.py`).
2. **Makes the rule permanent.**
   - `fixer.md` step 18 states the obligation and the reusability criterion once. `fix-review.md` step 9 and `orchestrator.md` section 13 point to it.
   - A new detector, `tools/audit/seat/tmp_paths.py --check`, refuses a tracked script, workflow or decision record tied to a temp or machine path.
   - The detector runs, with its self-test, in `governance.yml`'s `instrument-self-tests` job and in `tools/audit/prepr.sh`. That job grades nothing, and it is the only place an unowned, unpinned copy may run (`codeowners_gap.py`, #1515). A red there is still a red at the head that `pr-contract` makes the body answer. Making it a required pinned grader is owed work (Forward-carry).
   - `CODEOWNERS` adds only `tools/release/`: the version stamp is release tooling, not an audit instrument. `tools/audit/seat/` stays unowned.
3. **Fixes the paths the detector finds**, and makes `app_approve.sh`'s carry run on macOS bash 3.2.

### Round 2: what #1879's round-1 review found, and what changed

`merge_train.py`:
- **B1.** The mandate path was taken on any substring "touches code-owned paths (" in `app_approve.sh`'s output. A blocked verdict's echoed reason carrying those words was mandate-approved and merged. The match is now anchored to `app_approve.sh`'s own line for this pull request: `^app_approve: REFUSE: #<pr> touches code-owned paths (...);`.
- **B2.** The file list was `git diff --name-only`, whose rename detection lists only a rename's new path. Moving a policy file out of the corpus escaped the policy stop. The list now uses `--no-renames`, so it names both paths.
- **B3.** A failing `git merge-base` or `git diff` fed its error text in as the file list. Either failure now stops the train.
- **CI read.** `wait_ci` reads every page (`gh api --paginate`). It treats only success, skipped and neutral as green, so `action_required`, `stale` and any conclusion GitHub adds later stop the train.

`tmp_paths.py`:
- It now judges each match on its own. A `$$` elsewhere on the line, even in a comment, no longer excuses a fixed name.
- It catches every gaming shape the review listed:
  - `${TMPDIR:-/tmp}/<name>`, `$TMPDIR/<name>`, `os.environ("TMPDIR")` plus a name;
  - a variable holding `/private/tmp`;
  - `os.path.join("/tmp", ...)`;
  - concatenation;
  - `tempfile.gettempdir()` plus a name;
  - a `?? '/tmp'` fallback with a fixed suffix;
  - the lease name with a suffix;
  - `/home/user` outside the cloud image's two roots.
- `.claude/settings.json` is now in scope.
- Its docstring states what it does not catch: a path assembled across lines, one built from pieces that never spell a root, one read at run time, and anything outside its scope.

`seat_venv.sh` reads the census with an interpreter named by absolute path (`$HPO_PYTHON`, then `/usr/bin/python3` and two fixed fallbacks). In the incident state (shims first on PATH, venv deleted), the bare `python3` it used before was the dead shim.

`governance.yml`: each comment now sits above its own step.

### Round 3: what the round-2 review found, and what changed

- **`merge_train.py`, the anchor.** Dropping the `^` anchor reopened B1 for a blocked verdict that quotes `app_approve.sh`'s own refusal line mid-line (the review's A1e), and the self-test stayed green. A new arm uses exactly that shape: it fails against an anchor-less copy and passes at the head. Another new arm covers a merge base that exits 0 but is not a sha. 41 arms.
- **`tmp_paths.py`, more shapes.** It now catches `Path("/tmp") / "x"`, `f"/tmp/{name}"`, `os.environ["TMPDIR"] + "/x"` and `Path(tempfile.gettempdir()) / "x"`. The docstring now lists exactly the `os.environ` forms covered. Its "does not catch" list adds a `printf`-built path and a temp root under a variable not named TMPDIR.
- Two existing `tests/` lines the wider check now finds are allowed, each with its reason: `doc_claims.py`'s fixture path that must not exist, and `ha_floor.py`'s disposable `--cache` default. 41 arms.

### Inventory

Reusable: a later round or seat reruns it, or a body figure needs it to be reproduced (`fixer.md` step 18). A one-off probe may stay in scratch.

| tool | where it lived | verdict | reason |
|---|---|---|---|
| `ci-watch.sh` state | `/private/tmp/audit-7/ci-watch-state` | fixed | `$HPO_STATE_DIR/ci-watch-state` |
| `handoff_push.sh` | `/Users/...` checkout and worktree, body in `/private/tmp/audit-7/v6612` | fixed | checkout from the git common dir, worktrees beside it, body in the state dir; header names its successors |
| `merge_pr.sh` | state in `/private/tmp/audit-7/orchestrator`, `cd /Users/...` | fixed | state dir, common-dir checkout; header points to the train |
| `remerge_main.sh` | `cd /Users/...` | fixed | toplevel of its own checkout; neutral wording folded in from `remerge.sh` |
| `worktree_gc.sh` keep-dir | `/tmp/hpo-ev` | fixed | cited evidence kept in `$HPO_STATE_DIR/ev`, outside every temp dir; the seats root `/tmp/hpo-orch` stays (scratch meant to die) |
| decision 0012 source | `/private/tmp/audit-7/r8prog/design-rotation-and-D14.md` | fixed | cited at commit `12743bf742e09cbe50b49ae02f8348798b273885`, branch `claude/project-thread-s8rmov` |
| `~/hpo-seats/bin/python`, `python3` | shims to the deleted venv | landed | `tools/audit/seat/shims/seat-python{,3}`, installed by `seat_venv.sh --install-shims <dir>` |
| the seat venv | hand-built in `/private/tmp/audit-7/r9-mac/ha-venv` | landed | `tools/audit/seat/seat_venv.sh` |
| `~/hpo-seats/bin/approve.sh` | `mapfile` shim for bash 3.2 | delete locally | `app_approve.sh` no longer needs it (Figures) |
| `~/hpo-seats/bin/mergewhen.sh` | reads `~/hpo-seats/tools/main`, already gone | superseded | `merge_train.py` with a one-entry queue; its stale-base guard is subsumed by the train's step 4, which refuses a head not containing the `main` it merges into |
| `~/hpo-seats/bin/waitci.sh` | local | folded | `merge_train.py wait-ci <sha>` |
| `~/hpo-seats/bin/openpr.sh`, `updatepr.sh` | local | landed | `tools/audit/seat/open_pr.sh`, `update_pr.sh`, state dir and venv PATH |
| `scratchpad/orch/train3.py` (and `train.py`, `train2.py`) | session scratch | landed | `tools/audit/seat/merge_train.py` |
| `scratchpad/orch/remerge.sh` | session scratch | folded | into `remerge_main.sh`, no duplicate |
| `scratchpad/orch/eta.py`, `demo-b.sh` | session scratch | leave | one session's ETA overlay and one PR's demo push |
| `mypar2.py`, `parity2.py`, `compare.py` | reviewer and fixer scratch (R9-EG-A2) | landed | `tools/audit/harnesses/thermal_parity.py` |
| `mutants_r4b.py`, `mutants3.py` (#1863), `rev_mut.py`, `mutate_pages.py` (#1876), `seat-p11-barrier/mutants.py`, `seat-r-p11/mut/mut.py` | seat scratch | leave | one PR's mutant generators, keyed to that diff |
| HA floor sweep (`seat-rca-hafloor/sweep.py`, `floor_names.py`, `census_fixer.py`) | RCA seat scratch | leave | the RCA seat's own evidence; it lands with that analysis if reused |
| `race_probe.py`, `mutants_r3.py`, `census.py` | deleted | lost | not recoverable from report text at a size worth retyping |

Left in place (fixtures and documented conventions, each named by `tmp_paths.py`'s rules or allow list): `gh_comment.py`, `app_comment.sh`, `app_approve.sh` and `prepr.sh` self-test fixtures, `/tmp/hpo-gate.lock`, a workflow runner's `/tmp`, the cloud seat image's `/home/user/heatpump_optimizer` and `/home/user/wt/`, `tests/card.mjs`'s legacy plan-data path, `tests/plan_view.py`'s per-checkout hashed payload, `tests/doc_claims.py`'s must-not-exist fixture path, `tests/ha_floor.py`'s disposable download cache, and `friction_issues.mjs`'s `RUNNER_TEMP` fallback. A bare `/tmp` named in prose or in a list of temp roots is not a hit.

### The merge train

`merge_train.py run <queue.json> [--mandate LABEL] [--approver-role ROLE]` works through the queue one pull request at a time and stops the whole queue at the first refusal. For each pull request it:

1. **Recarries** through `remerge_main.sh` when the head lacks `origin/main`.
2. **Waits for CI.** Every check run on every page must complete, with at least `--min-runs` of them. Any latest run that is not success, skipped or neutral stops the train, except names on `--ignore-red` (default `nightly-status`).
3. **Checks the carry** with `app_approve.sh --carry`.
4. **Re-checks** that `origin/main` is still in the head.
5. **Reads the changed files** with `git diff --no-renames` from a checked merge base. Any failure stops the train.
6. **Refuses any policy path** (`policy_lint.mjs --corpus-filter`, sentinel-probed as `preflight.sh` does).
7. **Approves.** The App approves when it can. A mandate approval (`gh pr review`, with a body naming the mandate label, role, paths, verdict comment and head) happens only when all three hold:
   - the App's refusal is exactly its own code-owned line for this pull request;
   - `--mandate` was given;
   - no `*_budgets.json` changed.
8. **Merges**: ready, title preflight (a `REFUSE` or a missing `clean` stops it), then `--match-head-commit` with main re-checked before each try. Afterwards it reads back the closing issues and runs `worktree_gc.sh`.

It is narrower than `train3.py` on one point: a missing-evidence refusal is not overridden by a mandate.

### What is not built

A `## Figures` check that a cited script is tracked or marked one-off. `figure_lint.mjs` already refuses an in-tree path that does not resolve, and reports an out-of-tree one `unverified`. A "one-off" marker would be the seat's own word on the very judgement the rule asks for. `fix-review.md` step 9 makes that judgement the reviewer's.

## Approval

Approval is by the orchestrator under mandate 5951564627 (the owner's instruction), after a `Fix review: merge` verdict at the head.

What the approval covers:
- **Policy files** (POLICY_GLOBS): `tools/audit/briefs/fixer.md`, `tools/audit/briefs/fix-review.md`, `tools/audit/briefs/orchestrator.md`.
- **Code-owned files**: `.github/CODEOWNERS`, `.github/workflows/governance.yml`, `docs/decisions/0012-process-diet-and-round-cadence.md`.

Each policy file pays for its new lines inside its existing cap, by cutting a motivating anecdote the rule does not need. No cap is raised.

`tools/audit/README.md` and `tools/audit/harnesses/README.md` are policy and untouched. `harnesses/README.md` still tables four instruments; `d907_kernel_band.py`, `hpo_ci_container_setup.sh` and now `thermal_parity.py` describe themselves in their headers.

Audit instruments carry no owner (tvofi, 2026-10-03): `tools/audit/seat/` is not added to `CODEOWNERS`, and decision 0013 stands unamended.

## Head

`5c5f211db6af8963fbd8e511b68d64beecef7a50` merges `origin/main` `4ead5c97aa3cd96a08cc6c55fe386751b1c9b0e0` (#1877) into the round-3 commit `4e5364076bfed82a48d3d9ab17b37b9d1170f4ee`.

**This merge is hand-resolved policy, as the orchestrator approved.** #1877 and this branch both edited two role contracts. Each conflict was resolved by taking #1877's text in the conflicted hunk, then re-adding this branch's clause beside it.

- **`tools/audit/briefs/fixer.md`, step 9:** #1877's wording, including its rewrap of the #386 sentence.
- **`tools/audit/briefs/fixer.md`, step 17 and the budget paragraph:** #1877's step 17 ("Take the fix that yields the better code") and its budget paragraph. This branch's obligation, numbered step 17 before the merge, is now step 18 and follows #1877's step 17.
- **`tools/audit/briefs/fix-review.md`, step 9:** #1877's step 9 with its #373/#258 examples. This branch's clause is appended to it, now pointing at `fixer.md` 18.
- **`tools/audit/briefs/orchestrator.md`:** merged cleanly. Section 13 now points at `fixer.md` step 18.
- **Cap payment:** `fixer.md` pays for step 18 inside its existing cap by shortening step 11's #546 example to the fact the rule needs (which of two artifacts was authoritative). No cap is raised.
- **Read-back of the merged files:** every #1877 clause named above is present once, this branch's step 18 and pointers are present once, and no conflict marker remains.

The round-3 commit sits on `fa735d6850bb07a7fd76f196935145960de171db`. That commit is the automatic merge of `origin/main` `243990abf` into the round-2 commit `44d5a4fe267da7cd4c7b0acc03c23d19386e11c0`, which sits on `6f1699dbbb4716c04da47b16c0fcf93dadc4887a`.

`origin/main` `4ead5c97a` is inside the head.

## Mutation proof

**`merge_train.py`:** 23 mutants, each killed by a named self-test arm.
- The set is the round-1 reviewer's 15 (`/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-tools-home/../seat-r-tools/attack/mut.py`), re-keyed to this head as `/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-tools-home/r2/mut2.py`, plus 6 for the round-1 findings:
  - an unanchored code-owned match;
  - an anchor without the PR number;
  - renames on;
  - the diff's rc ignored;
  - the merge-base's rc ignored;
  - no pagination.
  - Round 3 adds two more: the `^` anchor dropped, killed by "a blocked verdict QUOTING app_approve's own code-owned line mid-line is not mandate-approved (anchor)"; and the `is_sha` check dropped, killed by "a merge base that exits 0 but is not a sha stops the train".
- The 3 the review found surviving are now killed, each by its own arm:
  - M8 (min runs) by "fewer check runs than --min-runs is not complete CI";
  - M9 (pre-merge main recheck) by "main moving after approval and before the merge stops it";
  - M15 (`clean` required) by "a preflight that never says clean stops it".
- M6 (the head check inside the mandate approval) is now killed by its own arm.
- M7 is re-keyed: `action_required` added to the green list fails "action_required is not green".

**My own 13-mutant set** (`/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-tools-home/mut/mut.py`) is all killed. The code-owned-only mutant kills by a crash (no tally line), which the governance step's tally grep also refuses.

**`tmp_paths.py`:** 22 mutants (`/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-tools-home/r2/mut_tp2.py`, plus a clean environ-subscript mutant), all killed by named arms. They cover each class, the `os.environ[...]`, pathlib and f-string forms, each bare-root clause, per-match `$$`, runner, lease suffix, cloud roots, settings scope, evidence scope, per-file allow and stale entries.

**`app_approve.sh`:** the merge base is the mutant. Under macOS `/bin/bash` 3.2.57, its `--self-test` prints `141 checks, 2 failed` at the base and `141 checks, 0 failed` at the head.

## Null control

**The round-1 reviewer's harness** `/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-tools-home/../seat-r-tools/attack/attack.py`, run against `merge_train.py` at `6f1699db`:
- A1 (blocked verdict echo) and A2 (diff fails) print `mandate_approved=True merged=True`.
- A4 (`action_required`) prints `merged=True`.

**The same harness adapted to this head's CI read** (`/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-tools-home/r2/attack2.py`: JSON lines and a checked merge base; CI success per arm, with A4 alone `action_required`):
- A1 stops at approve.
- A2 stops at `files: git diff failed`.
- A4 stops at CI.
- Its control A3 (a policy file listed) stops at policy.
- None approved, none merged.

**The round-1 reviewer's gaming probe** `/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-tools-home/../seat-r-tools/attack/tpgame.py` at the head:
- G1-G9 and the control C1 are refused.
- The legitimate L1-L4 pass: `mktemp -d`, a workflow's `/tmp`, `$RUNNER_TEMP`, `tempfile.TemporaryDirectory`.
- L5 (a fixed `/tmp` name in a `.sh` under `tools/`) is refused deliberately: it is a fixed name.

**The round-2 reviewer's probe** `tpgame2.py`:
- H1-H4 are refused: pathlib, f-string, `os.environ[]`, and a `$$` in a later word.
- H5 (`printf`-built) passes, and is listed under "does not catch".
- L6-L8 pass.

**The reviewer's A1e case** (`attack_success.py`):
- At the head: `rc=1 mandate_approved=False merged=False`.
- Against an anchor-less copy: `rc=0 mandate_approved=True merged=True`.

**`tmp_paths.py --check`:**
- At `origin/main` `20f597c6`, and again at `243990abf`, it refuses 14 lines: `ci-watch.sh`, `handoff_push.sh` (3), `merge_pr.sh` (2), `remerge_main.sh`, decision 0012 (2), `worktree_gc.sh` (2), the two hastub doc lines and a harness comment. Its one stale allow entry there is the checker's own, which that tree lacks.
- At the head it reports `0 refused, 0 stale allow entries`.

**`seat_venv.sh` in the incident state** (shims first on PATH, `HPO_STATE_DIR` with no venv):
- At `6f1699db`, `--check` died with "cannot read the census python".
- At the head it reports "no venv at ...", and a full build from that state succeeds (python 3.14.7, numpy 2.4.6, scipy 1.17.1).
- Its `pip freeze --all` less pip matched the hand-built venv byte for byte (14 packages) in round 1.

**`thermal_parity.py`:**
- Two plain captures: `base_head_differing=0`, with 0 of 1872 scalar-vs-batch pairs unequal.
- The `--perturb` capture differs in 1200 arrays, none outside the two-zone cells.
- A one-ulp copy reads 1 differing array and 1 unequal pair.
- The round-1 reviewer re-ran all of these and matched them.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test`: 41 checks, 0 failed.
- `python3 tools/audit/seat/tmp_paths.py --self-test`: 41 checks, 0 failed.
- `python3 tools/audit/seat/tmp_paths.py --check --ref 243990abf`: 14 refused, 1 stale, rc 1.
- `python3 tools/audit/seat/tmp_paths.py --check`: 0 refused, rc 0.
- `bash tools/audit/app_approve.sh --self-test` on `/bin/bash` 3.2.57: 141 checks, 2 failed at the merge base; 141 checks, 0 failed at the head.
- `bash tools/audit/worktree_gc.sh --self-test`: 66 checks, 0 failed (round 1; this round leaves it unchanged).
- `python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --check`: `uncovered_files=0`.
- `node .claude/workflows/policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)`. `node .claude/workflows/policy_lint.mjs --budgets`: rc 0, no cap exceeded. `node .claude/workflows/rules_sync.mjs --check`: ok.
- `node .claude/workflows/field_coverage.mjs`: `FIELD COVERAGE ok`.
- `node .claude/workflows/brief_lint.mjs`: `TOTAL: 0 error(s) across 45 file(s)`.
- Scoped gate (`python3 tests/closure.py select --diff <merge base>`): `MODE: SCOPED -- 4 script(s) run`.
  - `entities.py`: 2113 passed (at `5c5f211d`).
  - `harness_headers.py`: 95 passed.
  - `open_meteo.py` and `solar_alignment.py`: passed.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

**`pr-contract` at `1190f105` (run 37136141404).** It refused because `nightly-status` was red and this diff touches `.github/workflows/governance.yml`.

**`nightly-status` at `1190f105` (job 111240949131).** It printed `NIGHTLY FAILED: mutation-ledger failed last night`, naming scheduled Tests run 37108891698 at `main` `2e569748`, 2026-10-03T08:11:57Z.

That is `main`'s own nightly. It ran before this branch was cut from `12dbd3a5`, and on a tree that does not contain this diff. `tests/nightly_status.py` reads the scheduled runs of `tests.yml` (its `DEFAULT_WORKFLOW`). `git diff --name-only <merge base> HEAD | grep -E 'tests.yml|nightly|mutation'` prints nothing, so this diff changes neither that workflow, nor the reporter, nor the mutation lanes. `governance.yml` is what the body check's heuristic keyed on.

No cheaper detector is owed by this pull request: the red is `main`'s own mutation-ledger lane, outside this diff. It goes green on the next scheduled or dispatched Tests run on `main` that passes, and dispatching one is the orchestrator's.

**`pr-contract` at `6f1699db`** (run 37136843240) failed for the same reason, with `nightly-status` (job 111243164480) red on the same scheduled run. This section answers both.

## Forward-carry

**`.claude/workflows/carry-201.json`**, new last entry. It owes the follow-up that makes `tools/audit/seat/tmp_paths.py` a pinned grader in a required `governance.yml` job:
1. Declare it in pinned `field_coverage.mjs` first.
2. Then restore it from the base in a required job, which needs a base that already carries the file.

It must not be made code-owned to get there.

The obligation itself is carried into `tools/audit/briefs/fixer.md` step 18, `tools/audit/briefs/fix-review.md` step 9 and `tools/audit/briefs/orchestrator.md` section 13.

## Friction

none
