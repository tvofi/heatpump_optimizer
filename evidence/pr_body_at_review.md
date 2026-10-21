fix(seat): a row-only `update_pr.sh` push takes pr-contract's body contract and carry check, not the full prepr

`update_pr.sh <branch> - <body>` exists to add a pull request's own delivery row. Before this change its push ran the full `prepr.sh`: suites, mutants and the heavy-slot lease. On 2026-10-21, on a box queued on `gate_lock.py`'s four slots, the one-line rows for #2557 and #2558 waited 30+ minutes. `bus.sh dispatch` refuses a head without `dev/programme/delivery/<N>.md`, so reviewer dispatch waited on them too.

**What changed.** `tools/pr/app_push.sh` gains `--row-only` beside `--recarry`, built the same way as `recarry_verdict`. `row_only_verdict` reads HEAD once. It takes the live head, number, title and body from the open-pull-request listing that app_push already reads. It skips prepr only when all four of these hold. Each one fails closed, and the result is named on one `app_push: ROW-ONLY:` line:

- (a) HEAD has exactly one parent, and that parent is the live pull-request head.
- (b) `git diff --name-status <live> HEAD` is exactly one added file: `delivery_row.sh`'s `$ROW_DIR/<N>.md` for the listing's `<N>`.
- (c) That file is one line, a row anchored on `<N>` and open: `len(ls) == 1`, `tests/delivery_status.py`'s `anchored` and `OPEN_STATUS`, over `splitlines()` of the committed blob.
- (d) The body file is the live body under one new `## Head` note, as `head_note.py`'s own `prefix(live, note)` builds it.

When the skip is taken, `row_only_checks` runs two of pr-contract's body checks, at the judged head and with the pull request's live title:

1. Step 7's body contract, `policy_lint.mjs --pr-body --head --title --paths-file --existing-file`. It is handed the credential prepr's step 7c reads (`gh_credential`'s order: `GITHUB_TOKEN`, then `GH_TOKEN`, then `gh auth token`), so the contract's red-history walk reads the ancestry reds.
2. The carry check, `carry_audit.py check --body`.

A refusal from either pushes nothing. In every other case prepr runs exactly as without the flag. The push is pinned to the HEAD the verdict judged. `update_pr.sh` passes `--row-only` only for code sha `-` (`# mut:rowonly`) and prints app_push's `ROW-ONLY:` line; a code sha never asks for it.

**This round answers `Fix review: blocked f1695654...` (W11).** The production predicate already refused a multi-line row file: `len(ls) == 1` is (c)'s first conjunct. No arm drove one, so deleting it left the self-test green. Two arms now do, each a row file whose first line is the open row anchored on #7 and which carries a second line:

- the stubbed `omulti` (a second line that is another pull request's open row), which must run prepr;
- `real git: a row file of two lines, the first the open row anchored on #7, runs prepr`: `ensure_row`'s own commit, amended with one appended line.

So a multi-line row file can never skip prepr while the self-test is green: W11 is now killed by both arms (`## Mutation proof`). The production predicate is unchanged, so no other path moved. The header's (c) now says "one line", and both comments say "two of" pr-contract's body checks (the review's non-blocking note).

**Why the other prepr steps are not re-run on the skip.**

- The body contract and the carry check run.
- The row lint is (c).
- **7c (ancestry reds).** prepr's 7c reads every failed check run on the branch's pushed commits from `merge-base..<remote head>` and feeds them to the body check, which exempts the main-graded reporters (`MAIN_STATE_REPORTERS`) and pr-contract. The contract's red-history walk (`redHistoryForHead`) reads the same endpoint over `merge-base..HEAD`. HEAD is the live head plus the row commit, which is unpushed, so the walk reads it as no runs. Same commits, same exclusions, same `checkPrBody`; `row_only_checks` hands on 7c's credential.
- **Figure lint and preflight**, which pr-contract and prepr (7a) both run, are not re-run. Each reads only the body and the tree. (b) leaves the tree the live head's plus one row file, and (d) leaves the body the live one plus the caller's note, so both read what already passed on the live head.
- **Claim files, `VERSION`, the manifest, code, closures and transport.** None can move under (a)+(b). A second path in the diff, a claim file included, fails (b) and takes the full prepr. That is the null control below.

**Alternatives and why each lost (fixer.md step 17).**

- **Decide the skip in `update_pr.sh` alone, via `PREPR_BODY_PATH_ONLY`.** This bends a flag built for one step's test into a bypass, and makes the tool that mints and pushes take a caller's word that the push is row-only.
- **A `prepr.sh --row-only` mode.** A second entry point to prepr, which still needs app_push's live-head read to decide.
- **`--recarry`.** Its (a) requires a two-parent merge.
- **Calling prepr's `reds_line` directly.** app_push would have to source prepr.sh, which runs its own main on load, and run a second walk over check runs the contract already reads.
- **For W11, a byte-exact compare of the blob against `row_line`'s output.** It would pin the row's wording to the title the listing carries now, so a retitled pull request's row would take prepr for no reason. `len(ls) == 1` already states the property; the defect was the missing arm.

`delivery_row.sh` is unchanged: the verdict sources it for `ROW_DIR`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01MzT8ZzVMxZmcsVb2S5EAAH

## Head

`54bf182104e450c0ac2e6eb007da59b9315e0565` merges the authored code head `a8bb9a9c1ebda970fadfb1f24e3f8f35aa283389` and then merges origin/main `e7c664856` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`a8bb9a9c1ebda970fadfb1f24e3f8f35aa283389` is the code head: one commit on the previous PR head `f16956542b2c4470de5a3e12fc843f97cef1840e`, which already contains origin/main `5d433771aa88bbfd49b8868a9b53ea1241ab85a3` (merge base equals origin/main's tip, read 2026-10-21T14:40Z). Everything below is measured at `a8bb9a9c1`, 2026-10-21, unless it names `f1695654`.

## Mutation proof

The runner applies each mutant as one exact-string replacement in the worktree (refusing a replacement that matches other than once), runs the owning self-test, and restores the file with `git checkout`; it ended `worktree restored to HEAD a8bb9a9c1`.

- **W11** deletes `len(ls) == 1 and ` from (c) (the blocking item). At `f1695654`: `app_push self-test: 179 checks, 0 failed`, so it survived there. At this head: `182 checks, 2 failed`: `omulti`'s `... prepr ran once ... (got '002', want '110')` and `real git: a row file of two lines, the first the open row anchored on #7, runs prepr`. That is the failing test first: both new arms fail against the predicate without the conjunct and pass with it.
- W1 widens (b) to `grep -qF` of the row line in the diff: 2 failed, including `real git: the same commit with one more file runs prepr (null control)`.
- W2, (a)'s `-eq 1` to `-ge 1`: 1 failed (`otwo`).
- W3, (d)'s refusal to `|| :`: 2 failed (`obody`, `real git: a body that is not the live one under one new note runs prepr`).
- W4 deletes ` and OPEN_STATUS in ls[0]`: 2 failed (`oclosed`, `real git: a row anchored on #7 that is not open runs prepr`).
- W5 replaces the `row_only_checks` call with `true`: 8 failed, among them `the body contract ran in its place ...` and both credential arms.
- W6, `update_pr.sh`'s `RO=--row-only` for every code sha: `pr_args self-test: 57 checks, 1 failed`, the arm `null control: a code sha never asks for --row-only, so its push runs the full prepr`.
- W7 narrows the head guard to `[ "$recarry" = 0 ] || ...`: 1 failed (`romoved`, got `018`).
- W8 replaces the `gh auth token` fallback with `:`: 1 failed (`the contract was handed gh's stored token ...`).
- W9 drops the carry check: 3 failed.
- W10, (a)'s parent-is-live refusal to `true`: 2 failed (stub `olive`, `real git: the row on a commit past the live head runs prepr ...`).
- W12 deletes the `anchored(...)` conjunct: 1 failed (`orow`).
- W13 drops the contract's rc propagation: 2 failed.
- W14 takes the skip unconditionally: 10 failed.
- W15, `--head HEAD` for the judged sha: 1 failed.

## Null control

- M0 is the same runner with no replacement: `app_push self-test: 182 checks, 0 failed` at this head and `179 checks, 0 failed` at `f1695654`. So the runner fails only on a mutant, and W11's 0-failed at `f1695654` is a survivor, not a runner that cannot fail.
- Skip versus prepr on the same row commit: `real git: ensure_row's own row commit on the live head skips prepr` passes, so the two-line arm's refusal comes from the second line, not from the fixture.
- `oenvcred` sets `GITHUB_TOKEN`: that token is handed on and `gh auth token` is not called, so the credential read adds a token only where 7c would find one and the environment has none.

## Figures

- `bash tools/pr/app_push.sh --self-test` printed `app_push self-test: 182 checks, 0 failed`. The counts per mutant are in `## Mutation proof`.
- `bash tools/audit/seat/update_pr.sh --self-test` printed `delivery_row self-test: 5 checks, 0 failed` and `pr_args self-test: 57 checks, 0 failed`.
- `python3 tests/closure.py select --diff 5d433771aa88bbfd49b8868a9b53ea1241ab85a3` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, over five changed files; `scope.run` is empty.
- The `run_always` lines of `tests/run.sh`, run with `PYTHONPATH=tests/hastub` under a Python 3.13 venv built from `tests/requirements-ci.txt`:
  - `python3 tests/env_drift.py --claims-only 5d433771aa88bbfd49b8868a9b53ea1241ab85a3` printed `claims hygiene: 5d433771aa88bbfd49b8868a9b53ea1241ab85a3 ok`.
  - `python3 tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`.
  - `python3 tests/layout.py` printed `layout self-test: ok`.
  - `python3 tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `python3 tests/entities.py` printed `ALL 2375 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 5d433771aa88bbfd49b8868a9b53ea1241ab85a3` printed `Architecture score: dS +0.0000 NULL`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` exited 0 at the head with no REFUSE line, ending `PRE-PR: a8bb9a9c1ebda970fadfb1f24e3f8f35aa283389`; its `unpinned sites` step printed `the diff adds no unpinned mutation site`. On this unpushed seat branch its push-order and ancestry-reds steps print their skip; the pull request's own ancestry reds are under `## Red checks`.
- The seams of the class (fixer.md step 8). The rule: every refusal in `row_only_verdict`, enumerated by `sed -n '/^row_only_verdict() {/,/^}/p' tools/pr/app_push.sh | grep -o '_rv_no "[^"]*'`, plus the conjuncts of its two inline Python predicates. It returns nine refusals, one success line, three (c) conjuncts and two (d) conjuncts. Dispositions:
  - parent count, parent is live, the one-file diff, (c)'s three conjuncts, (d), and "no open pull request": pinned by W2, W10, W1, W11/W4/W12, W3 and the stubbed `onone` (W14 fails it).
  - "HEAD does not read back" (W16) and "the diff ... could not be read" (W19): each mutant left `182 checks, 0 failed`. Both are fail-closed reads with a refusing successor: an empty HEAD gives `rev-parse ^@` no parents, so the parent count refuses; an empty diff is not the one-file diff, so (b) refuses. Only the named reason changes. Written triage, not pinned.
  - "delivery_row.sh did not load" (W18): `182 checks, 0 failed`. Under the script's `set -u` an unloaded `ROW_DIR` aborts app_push before the row read (probe: `ROW_DIR: unbound variable`, rc 127). With `ROW_DIR` exported by a caller and the file missing, (b) and (c) still demand exactly one added one-line open row at that path. Written triage, not pinned.
  - (d)'s `j > i` (W20, deleted): `182 checks, 0 failed`. The equality beside it still holds the property: with no `## Head` in the body file, `prefix` inserts the note under the live body's heading, so the two cannot be equal; with a note that ends the body (`j = -1`), what the equality then accepts is still the live body under one note. The conjunct only narrows. Written triage, not pinned.

## Red checks

- **nightly-status** was red on `f1695654`. It is main's red: it reports the last concluded scheduled run of `Tests` on main. This diff touches only seat tooling and its own row, so it does not reach what that run reads. Not this PR's red.
- **pr-contract** was red on 947d3631 (two runs) and on 93015eca, each time at `Every finding the body records names its destination` (`carry_audit.py check`), caused by the round-1 body. Both runs on `f1695654` are success. The cheaper detector is the seat's pre-push gate: prepr runs step 7's contract but not `carry_audit.py`, which is how the red got past it. Its standing cost is one Python call per prepr run. This PR adds it to the row-only path; adding it to prepr or to fixer.md step 5 is carried under `## Forward-carry`.

## Forward-carry

- prepr.sh does not run `carry_audit.py check`, which is one of pr-contract's body steps, so "prepr passes" does not mean "pr-contract's body steps pass", while fixer.md step 5 names a body passing prepr as the seat's gate. This PR's round-1 body passed prepr and was refused by pr-contract three times for exactly this reason. The decision is one of two: prepr runs the carry check beside step 7, or step 5 names `carry_audit.py check --body` beside prepr. Carry: R10-POLICY-FIXER-MD

## Friction

fixer.md-step-5: cost: this cloud container's default `python3` is 3.11, which cannot parse `tests/entities.py`; the always-run checks needed a 3.13 venv built by hand with `uv` from `tests/requirements-ci.txt`. Carry: dismissed: environment-only, the container image's interpreter, no repository change can fix it

