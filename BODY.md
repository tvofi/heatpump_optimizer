R10-CI-LAYOUT-P2, sub-PR P2b ("cut-over"), unit **U6**: `pr-contract` as a `workflow_call` callee with the code-scanning wait, plus `ci_probe.py`'s `sarif-upload`, `dismiss-alert` and `workflow-disable`. Part of #2495.

## Head

Code head `e75ea158c5bc7d5cc99a03b04001a852f5850b66` (`handoff/r10-ci-layout-p2-u6`), stacked on U0c's head `d22b5f303e09a67106fb44da03ad9e014eb1f840` (`handoff/r10-ci-layout-p2-u0c`), which is on `origin/main` `fef4a1351db3e8e328d714e84299284c6876eecb`. The unit is the 4 commits `git log d22b5f303..HEAD` lists, no merge (`git log --merges origin/main..HEAD`: empty). `origin/main` has since moved to `d6308d77c5d02b2001e58a5436715d0c45a4fa9e`, which is not merged here; `git merge-tree --write-tree HEAD origin/main` is rc 0, a clean merge. Figures were taken 2026-10-23T00:00Z to 01:03Z (`date -u`).

The toolchain: the session had no `/opt/hpo/venv-ci`; every Python figure below ran under Python 3.13 in a venv built from `tests/requirements-ci.txt` (`pip install --require-hashes`), not 3.14, with `PYTHONPATH=tests/hastub`. The self-tests that need only the stdlib ran under the system Python 3.11.

## Unit

U6, `git diff --stat d22b5f303..HEAD` (the unit alone; `origin/main...HEAD` also lists U0c):

```
 .github/workflows/pr-contract.yml                 | 166 ++++++++++------
 dev/audit/harnesses/r10_ci_layout_u6/pc_map.json   |  (new)
 dev/audit/harnesses/r10_ci_layout_u6/unitcheck.sh  |  (new)
 dev/audit/harnesses/r10_seat_selftests_mutants.py |  11 ++
 tests/entities.py                                 | 135 +++++++++----
 tools/audit/seat/ci_probe.py                      |  98 ++++++++-
 tools/ci/codescan_wait.py                         | 231 ++++++++++++++++++++++
```

Production: `.github/workflows/pr-contract.yml` (about 107 added, 59 removed), `tools/ci/codescan_wait.py` (new; 138 lines before its `# ---- the self-test` marker, docstring included, the other 93 its self-test), `tools/audit/seat/ci_probe.py` (the three subcommands and their parser and dispatch lines; the self-test rows are the 43 lines between the `# sarif-upload, dismiss-alert, workflow-disable (P2b U6)` and `# dry run and the log` markers). Tests: `tests/entities.py`, `ci_probe.py --self-test` (40 → 53 checks), `codescan_wait.py --self-test` (13 checks), mutants `ci_probe-8`…`-14`. Classification: `tools/ci/` is already a measured gate prefix in `tests/closure.py`, so the new program needs no new line; `dev/audit/harnesses/` is inert (`closure.is_inert('dev/audit/harnesses/r10_ci_layout_u6/unitcheck.sh')`: True).

What the conversion does to `pr-contract.yml`:
- `on:` is `workflow_call` with inputs `pr`, `base`, `head` (`type: string`, `default: ""`). `pull_request`, `merge_group` and `concurrency` are gone (ci.yml's run-id group holds the run alone). The job has no `if:`: the caller's decides.
- Floor `contents: read`, `security-events: read`, `actions: read`; the job block adds `checks: read` and `pull-requests: read` (the caller grants all five, per U0c's Interface).
- `timeout-minutes` 5 → 20, for the ten-minute wait bound.
- "Name the pull request a queue entry carries" becomes "Name the pull request this run grades": a `merge_group` entry is named from the queue ref as before; every other event takes `inputs.pr` and `inputs.head`, and the base commit from the payload, else `GET pulls/N`.
- The restore step's `PINNED` falls back to `origin/<inputs.base>` where the event carries no base commit (a dispatch); `'tools/ci/*.py'` joins its pathspec, so the wait's program is the base's.
- New step "Wait for code scanning and list its open alerts" runs `python3 -I tools/ci/codescan_wait.py`, writing `/tmp/pr-alerts.txt`.
- "List the red checks at this head" excludes `pr-contract / pr-contract` and `gate` (N4) and folds `/tmp/pr-alerts.txt` into `/tmp/pr-reds.txt`.
- The title is always read off the API (a dispatch's payload has none), so `PR_TITLE` no longer interpolates `github.event.pull_request.title`.

## Interface

Consumes (U0c's contract): the `pr-contract` caller in `ci.yml` passing `pr`, `base`, `head` from `needs.prelude.outputs.*`; grant `contents`, `checks`, `pull-requests`, `security-events`, `actions`, all `read`; `if: !cancelled() && workset names pr-contract`; `needs` every other unit. Check name: `pr-contract / pr-contract`. `base` is the base ref NAME; the callee reads the base commit itself.

Exports, exact names:
- `tools/ci/codescan_wait.py --pr N --base B [--base-repeats]`. Env: `GITHUB_REPOSITORY`, `GITHUB_RUN_ID` (the caller's), a token as `GITHUB_TOKEN`/`GH_TOKEN`. Stdout on rc 0: one `code-scanning alert <n> (<rule id>)` per line, none when none. rc 1: `FAIL closed: <why>`; a rate limit and any failed read are rc 1, never an empty list. Constants `POLL_S = 60`, `WAIT_MAX_S = 600`. It imports `alert_list` (`match`, `reds`, `bind`; the SARIF read and the alert-level dismissed read are its, not re-implemented) and `gate.UNITS`, `prelude.parse_title/title_sha/workset`.
- The workflow's `CS_BASE_REPEATS` env on the wait step: empty (alerts open on the base are NOT subtracted) until live case 6 shows the merge ref repeats them; setting it to anything non-empty passes `--base-repeats`.
- `ci_probe.py` subcommands: `sarif-upload <pr> --commit SHA --category /language:<name>` (POST `code-scanning/sarifs`, ref `refs/pull/<pr>/merge`, an empty CodeQL SARIF, `automationDetails.id` = `<category>/`), `dismiss-alert <n> --reason {false positive|won't fix|used in tests} [--comment TEXT]` (PATCH `code-scanning/alerts/<n>`), `workflow-disable <file|id>` (PUT `actions/workflows/<w>/disable`). Each: `--repo` spelled out, `/rate_limit` read before the write and refused below 20 %, one log line, `--dry-run`.
- Step 1's source rule is gate.py's: this run when its `run-name` workset owns `codeql`, else the newest other `ci.yml` run at this head naming this PR and the PR's LIVE base (`GET pulls/N`) that owns `codeql` and whose three `codeql / Analyze (...)` jobs are all completed.

## Static map

`sh dev/audit/harnesses/r10_ci_layout_u6/unitcheck.sh origin/main` runs `archive/probe/design-ci-rev4:measure/rev/unitcheck2.py static` of `origin/main`'s `pr-contract.yml` against this head's, under `dev/audit/harnesses/r10_ci_layout_u6/pc_map.json` (one rename, one gained step placed after "List the paths this pull request changes", ten changed rows):

```
head, under the map (want rc 0):       STATIC rows 16->17 lost 0 gained 0 changed 10 (mapped 10) misplaced 0 rc 0
head, no map (want rc 1):              STATIC rows 16->17 lost 1 gained 2 changed 9 (mapped 0) misplaced 0 rc 1
plant, the wait step deleted (blind, rc 0):          STATIC rows 16->16 lost 0 gained 0 changed 10 (mapped 10) misplaced 0 rc 0
plant, the gate exclusion deleted (blind, rc 0):    STATIC rows 16->17 lost 0 gained 0 changed 10 (mapped 10) misplaced 0 rc 0
plant, an unmapped step added (want rc 1):         STATIC rows 16->18 lost 0 gained 1 changed 10 (mapped 10) misplaced 0 rc 1
```

rc 0 against current main under the map; the same pair without the map is rc 1, so the edits are real and the map is what admits them. The instrument's limit, measured by the two blind lines: a row the map admits as `changed` or `gained` is not compared further, so a deleted gained step and a gutted changed step both read rc 0 (the same blind spot U0c recorded for ci.yml). The entities pins below are the controls that refuse both (see `## Mutation proof`).

## Controls

Offline; none touches the API.

**`codescan_wait.py --self-test`** (13 checks, `python3 -I tools/ci/codescan_wait.py --self-test`) drives the ported step over `alert_list`'s own fixtures (`alert_list.world`, wrapped to serve the runs, jobs and pulls reads and to list an analysis only under the ref it was uploaded to):
- 1 plant: a code run lists `code-scanning alert 7 (py/code-injection)`; 2 null: the same run without the plant lists nothing;
- 3 carried: an edit run takes S from the code run and lists the same alert;
- 4 a leg whose "Perform CodeQL Analysis" step was skipped uploaded nothing and is neither waited for nor read;
- 5 case 7: an analysis id answering 404 FAILs closed;
- 6 no finished codeql unit at the head for an edit run FAILs; 7 a code run of another base is no source;
- 8 an uploaded leg with no analysis at the bound FAILs; 9 a leg whose analysis lands after two polls is waited for at the 60 s poll and then listed; 10 `POLL_S >= 60`;
- 11 a dispatch source is read at `refs/heads/<its branch>` and not found at the merge ref (null); 12 a rate limit is rc 1; 13 null: the plant exits 0.
`alert_list.py --self-test` still reads `25 checks, 0 failed`.

**The red filter, driven** (`tests/entities.py`, check "the red filter lists a red non-required job and neither `gate` nor the contract's own name (plant and null)"): the jq program is cut out of the step and run with `jq` over a listing of five check runs. Plant: `tests / fast (3.14)` (failure, not required) comes out. Nulls: `gate` and `pr-contract / pr-contract` (both failure) and a green and a running check do not. The control moves: with the `gate` exclusion cut out of the program, the same listing returns `gate` too.

**`ci_probe.py --self-test`** (53 checks, `python3 -I tools/audit/seat/ci_probe.py --self-test`: `ci_probe self-test: 53 checks, 0 failed`): the 13 new rows pin the three calls' exact paths and bodies, the SARIF decoded (gzip, base64: empty `results`, tool `CodeQL`, `automationDetails.id` `/language:python/`, ref `refs/pull/9/merge`), the refusals (short or upper-case commit, a category that is not `/language:<name>`, a non-number, an unlisted reason, a host path in the comment, a path-shaped workflow name), the 20 % rate-limit refusal with no write, `--dry-run` with no write, and one `ok` and one `dry-run` log line per subcommand.

**Entities** (`PYTHONPATH=tests/hastub python tests/entities.py` at `0c04d5da4`; the commit after it adds only inert harness files): `1 of 2402 ENTITY CHECKS FAILED`, the one being the `policy_lint` template arm under `## Red checks`. Edits there, each because this diff turned the check red or its subject vanished:
- the permission set of the contract job now holds five reads;
- `_PC_EXCLUSION` is the pair `.name != "pr-contract / pr-contract"` and `.name != "gate"`;
- "refuses a version edit on every pull request" no longer requires a job-level `if: github.event_name == 'pull_request'` and instead requires that the job has none;
- `tools/ci/codescan_wait.py` joins `_PT_EXEMPT` with a reason (it needs `actions: read` and `security-events: read`, which `graders-head-copy` lacks; the same entry U0c made for `gate.py`);
- U0c's Wiring items: `pr-contract.yml` leaves `_EDITED_FILES` and `_CC_TWIN_ROUTE`; its two same-SHA-twin checks (they read `pr-contract.yml`'s own `concurrency`) are replaced by one callee pin (lists `workflow_call` alone, no `concurrency`) with a two-shape null;
- the merge-queue check reads a callee through its caller: a `workflow_call`-only producer needs `ci.yml` listing `merge_group` and a job `uses:` that file;
- three new pins: the red-filter drive above, the wait-step ordering and fail-closed shape (before the listing, `set -euo pipefail` before the program, its output a file, folded into `pr-reds.txt`, `tools/ci/*.py` in the restore), and the callee shape.

**Hygiene**: `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `python3 tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`; `python3 tests/closure.py selftest`: `ALL 112 closure shrink pins PASSED`; `python3 tests/layout.py`: `layout self-test: ok`; `python3 tests/env_drift.py --claims-only fef4a1351`: `claims hygiene: fef4a1351 ok`; `python3 tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries`; `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries`. No new push site (`sarif-upload` is an API write; `PUSHERS` unchanged).

## Null control

The real tree passes `tests/entities.py` except the one known red. The null for the new pins is the mutation runs below, each of which reddens its pin and leaves the rest.

## Mutation proof

**`ci_probe-8`…`-14`** (`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py ci_probe-8 … ci_probe-14 ci_probe-2`), run at `0da21897c`; `ci_probe.py` is unchanged since:

```
== ci_probe-2 ci_probe.py: KILLED rc=1 | ci_probe self-test: 53 checks, 5 failed
== ci_probe-8 ci_probe.py: KILLED rc=1 | ci_probe self-test: 53 checks, 2 failed
== ci_probe-9 ci_probe.py: KILLED rc=1 | ci_probe self-test: 53 checks, 2 failed
== ci_probe-10 ci_probe.py: KILLED rc=1 | ci_probe self-test: 53 checks, 1 failed
== ci_probe-11 ci_probe.py: KILLED rc=1 | ci_probe self-test: 53 checks, 2 failed
== ci_probe-12 ci_probe.py: KILLED rc=1 | ci_probe self-test: 53 checks, 2 failed
== ci_probe-13 ci_probe.py: KILLED rc=1 | ci_probe self-test: 53 checks, 1 failed
== ci_probe-14 ci_probe.py: KILLED rc=1 | ci_probe self-test: 53 checks, 2 failed
RESULT survivors=0
```
-8 the commit shape, -9 the category, -10 the SARIF's ref (`refs/heads/main`), -11 the dismissal reason list, -12 the comment's host-path refusal, -13 the disable endpoint (`enable`), -14 the workflow-name guard of `workflow-disable` alone. `-2` is the existing rate-limit mutant: it now also reddens the new rows.

**`codescan_wait.py`**, one predicate each, by hand (it has no `instrument-self-tests` step yet, so `r10_seat_selftests_mutants.py` cannot drive it; see `## Wiring`). Edit the line, run `python3 -I tools/ci/codescan_wait.py --self-test`, restore with `git checkout`:

```
the poll bound `if now() + POLL_S > stop:` → `if True:`            KILLED (check 9 raises Fail)
the base filter `t[2] != base or not owns_codeql` → `not owns_codeql`   KILLED: BAD 7
the uploaded-leg test `s["conclusion"] == "success"` → `!= "x"`          KILLED: BAD 4
the ref `if s["event"] == "pull_request" else` → `if False else`        KILLED: BAD 1, 2, 3, 4 (and the run ends: the clock is bounded)
the finished-unit test `if all(done.get(n) == "completed" ...` → `if True:`   KILLED: BAD 6
the own-run test `if owns_codeql(me, pr):` → `if False:`            KILLED: check 9 raises Fail
```

**The three new entities pins**, one mutation each on `pr-contract.yml` in a detached worktree at `0c04d5da4`, the full `tests/entities.py`, the aimed check required among the FAILs (the template-arm red is in all three, and in the unmutated head):

```
delete `| select(.name != "gate")`   3 of 2402 FAILED: "the contract lane passes the head's red checks…" (exclusion=[True, False]); "the red filter lists a red non-required job…" (reds=['tests / fast (3.14)', 'gate'])
delete `'tools/ci/*.py'` from the restore   3 of 2402 FAILED: "the contract lane waits for code scanning…"; "every pinned grader given a token runs its own copy…" (the program would run the head's copy)
delete `cat /tmp/pr-alerts.txt >> /tmp/pr-reds.txt`   2 of 2402 FAILED: "the contract lane waits for code scanning…"
```
Unmutated: `1 of 2402`.

## Figures

- Rule that produced the check counts: the totals are the scripts' own last lines (`ci_probe self-test: <n> checks, <k> failed`, `codescan_wait self-test: <n> checks, <k> failed`, `<k> of <n> ENTITY CHECKS FAILED`); a figure from a sliding window is stated by instrument, not carried.
- Scoped gate: `python3 tests/closure.py select --diff d22b5f303e09a67106fb44da03ad9e014eb1f840` prints `MODE: FULL -- every test script runs`, `reason: tools/ci/codescan_wait.py changes the gate itself, so every closure is suspect`. The same select against the merge base is FULL too, for `ci.yml` (U0c's). CI owns that run (`fixer.md` step 5); locally I ran `run_always`'s scripts this diff can move and the scripts it edits (the Hygiene line above, `tests/entities.py`, and the three self-tests).
- Class census (fixer.md step 8), the rule being "every reader that excludes the contract job's own check name from a head's red list": `grep -rn 'name != "pr-contract"' tools .github tests` after this diff returns two lines, each dispositioned: `tools/pr/prepr.sh:1025` (`REDS_JQ`) is U9d's, named in DESIGN-P2 section 9 for the same two-string filter, already in its brief; `tools/audit/seat/body_patch.sh:92` (`contract()`, the seat's local copy of pr-contract's listing) is in NO unit's brief, and after the cut-over it would ask a body to answer `gate`'s and `pr-contract / pr-contract`'s reds. Not fixed here: its self-test stubs `gh api ... check-runs` with the already-filtered names (`body_patch.sh` line 233 `cat "$STUB/reds"`), so the jq program is never run and a one-line edit would have no check that moves; a fix owes a stub that applies the program first. A distinct finding, carried below with the other. The pr-contract.yml side of the class (readers of its old triggers) is closed by the entities edits above.

## Live checks owed

All for the coordinator, on the draft probe PR (App-pushed), exactly as DESIGN-P2 section 10's U6 row states, plus the pair:

1. **The `pull_request` pair** (runtime half): `pr-contract / pr-contract` AFTER on the probe's `ci.yml` run against BEFORE (the `pull_request` run of `pr-contract.yml` on the twin at main's layout), `unitcheck2.py runtime`, pass = lost 0, gained 0.
2. **(1) the plant**: a push adds a finding only the python leg reports (a `.py` file the leg extracts, carrying a pattern a query of its suite flags; record the query id). The code run S's `pr-contract` lists `code-scanning alert <n> (<rule id>)` in `--red`, and a body that does not name it is refused.
3. **(2) the null**: a push that removes the plant. Its code run's `pr-contract` lists no alert, and nothing else in `--red` changes.
4. **(3) the carried case**: at the plant head, a body-only edit after S completes. The edit run's wait keys on S's `sha=` token, matches S's analyses, and lists the same alert.
5. **(4) the different analysis**: after S completes, upload the empty python SARIF at another commit (the PR head):

       python3 -I tools/audit/seat/ci_probe.py --repo tvofi/heatpump_optimizer --log LOG sarif-upload <pr> --commit <head-sha> --category /language:python

   Record that `alerts?ref=refs/pull/<N>/merge&state=open` no longer lists the plant (the reading the design rejects), then a body-only edit, whose `pr-contract` still lists the plant from S's analysis. Record a same-M hand upload's `analysis_key` against the unit's. **Check first** that GitHub files the upload under category `/language:python` (the listing's `category` field): the program sets `automationDetails.id` to `/language:python/`, the trailing slash codeql-action writes, and that one string is a live-only assumption. If the listing shows another category, change `ci_probe.py`'s `automationDetails` line, nothing else.
6. **(5) a dismissal**: `python3 -I tools/audit/seat/ci_probe.py --repo tvofi/heatpump_optimizer --log LOG dismiss-alert <n> --reason "used in tests" --comment "U6 probe plant"`. The next edit run lists nothing.
7. **(6) the base**: whether the merge ref's analysis carries the alerts open on `main`. If it does, set `CS_BASE_REPEATS: "1"` on the wait step (one line); else leave it empty. Also each analysis's `results_count` against its SARIF's result count.
8. **(7) fail closed**: drive the ported step with an analysis id that answers 404: `codescan_wait.py` is rc 1 (offline, check 5 of its self-test); live, `GET code-scanning/analyses/<id>` for a deleted id.
9. **The wait's timing**: record, for the plant run, when `pr-contract` started its wait and when the python leg's analysis appeared; the poll is 60 s and the bound 600 s inside a 20-minute job timeout. Record whether `gate`, which needs `pr-contract`, waited the same time.
10. **A dispatch head** (`-f pr -f base`): the restore step's `PINNED` falls back to `origin/<base>`; confirm the step prints `check source restored from origin/<base>` and the body step finds the PR through `inputs.pr`.
11. **`workflow-disable` on rollback write 21**: dry-run first (`--dry-run workflow-disable pr-contract-rerun.yml`), then the write.

## Wiring

- **`governance.yml` `instrument-self-tests`** (not mine): one step for the new self-test, or `selftest_wiring.py --check` reads `88 self-testing, 87 wired, 1 unwired` (measured at this head, naming `tools/ci/codescan_wait.py`). Suggested text, in the form of the `ci_probe` step at `governance.yml:872`:

      - name: Show the code-scanning wait (tools/ci/codescan_wait.py) driving alert_list over fakes
        run: |
          set -euo pipefail
          python3 -I tools/ci/codescan_wait.py --self-test | tee "$RUNNER_TEMP/codescan-wait-self-test.txt"
          grep -Eq '^codescan_wait self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/codescan-wait-self-test.txt"

  Once wired, `r10_seat_selftests_mutants.py` can take the six hand mutants above as `codescan_wait-1`…`-6`.
- **`tools/pr/prepr.sh` `REDS_JQ`** (U9d): the same two exclusions, `.name != "pr-contract / pr-contract"` and `.name != "gate"`, and the alert listing through `tools/ci/codescan_wait.py`'s output (it needs a run id, so locally U9d reads `alert_list.py` directly, as its own brief says).
- **`policy_lint.mjs`** (U9b): nothing new from this unit; see the next section.
- `_EDITED_FILES` and `_CC_TWIN_ROUTE` are done here (U0c's items for U6). `_PR_WORKFLOW_NAMES`/`_crr_defects` stay with U10.

## Red checks

- **main's ancestry**: not re-read, to spare the API (`COMMON.md`). U0c's reading at `fef4a1351` stands for this unit's base: no check run concluded `failure` (163 runs); 27 `rerun-stale-contract` runs `cancelled` by design. Root-cause trigger: not fired by this branch.
- **At this head, locally**: the same single red U0c recorded, "the template arm turns the acceptance red on a template that fails its own contract (and the real template keeps it green)" (`1 of 2402 ENTITY CHECKS FAILED`). **This conversion does not change it.** `tools/policy/policy_lint.mjs` (line 3898) takes the contract's workflow as the one file matching `\n  pr-contract:\n`; `pr-contract.yml` still defines that job and `ci.yml`'s caller `pr-contract:` still matches, so `2 files define pr-contract` and the acceptance returns 1 exactly as at U0c's head. Nor does it make it worse once U9b makes the reader recognise a `uses:` caller as no definition: the two arms that then read this file, `--paths-file` in the body-check invocation and `--no-renames` in the path derivation, are both still in it (`grep -c -e '--paths-file' -e '--no-renames' .github/workflows/pr-contract.yml` is nonzero for each, in a `run:` block outside comments). `policy-docs` grades with the BASE's reader, so no edit in P2b clears this on P2b's own run. Carry: R10-CI-LAYOUT-P2

## P2a defect

None found. `alert_list.bind` forwards `headers` positionally as U6-lib documents, and `ghapi.paginate(path, params, get=...)` accepts the injected getter, both used here as merged.

## Forward-carry

- **The wait's program is the head's copy on P2b's own run**: `tools/ci/codescan_wait.py` is new, so the base has nothing to restore, and the restore step's `git checkout "$PINNED" --pathspec-from-file` skips it (the limit `policy-docs` states for any new file). From the first run after P2b merges, the program is the base's. Carry: R10-CI-LAYOUT-P2
- **R-10 policy text still owed**: owner ruling R-10 option B changes the `pr-contract` contract, so DESIGN-P2 section 9 names `.github/PULL_REQUEST_TEMPLATE.md:23` (`## Red checks` also answers each `code-scanning alert <n> (<rule id>)`) and `.claude/skills/steward/SKILL.md`'s pr-contract line. This unit changes neither; the owner approves both before merge. Carry: R10-CI-LAYOUT-P2
- **`policy_lint.mjs`'s red-history arm (#1144)** reads every branch commit's check runs and does not know the renamed `pr-contract / pr-contract` or `gate`; whether it excludes them is U9b's reading to confirm on the assembled tree, or a red `gate` at an earlier commit becomes a red the body must name. Carry: R10-CI-LAYOUT-P2
- **`tools/audit/seat/body_patch.sh:92` still excludes only `pr-contract`** (the census line under `## Figures`): after the cut-over a seat patching a body gets `gate` and `pr-contract / pr-contract` as reds it must name. Its owner is U9d or the orchestrator, and the fix owes a stub that runs the jq program (its self-test's `gh` stub returns pre-filtered names). Carry: R10-CI-LAYOUT-P2
- **A source run with zero uploaded legs** (every leg stood down) lists nothing and passes the wait; it is the design's reading ("a leg that stood down uploaded nothing"), but nothing checks that a stood-down run had a reason. Not built: `codeql`'s own scope decision owns it (U3). Carry: dismissed: the design's stated behaviour, owned by the codeql scope job

## Friction

none
