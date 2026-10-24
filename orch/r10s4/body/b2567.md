fix(seat): a row-only `update_pr.sh` push takes pr-contract's body checks, not the full prepr

`update_pr.sh <branch> - <body>` exists to add a pull request's own delivery row. Before this change its push ran the full `prepr.sh`: suites, mutants and the heavy-slot lease. On 2026-10-21, on a box queued on `gate_lock.py`'s four slots, the one-line rows for #2557 and #2558 waited 30+ minutes. `bus.sh dispatch` refuses a head without `dev/programme/delivery/<N>.md`, so reviewer dispatch waited on them too.

**What changed.** `tools/pr/app_push.sh` gains `--row-only` beside `--recarry`, built the same way as `recarry_verdict`. `row_only_verdict` reads HEAD once. It takes the live head, number, title and body from the open-pull-request listing that app_push already reads. It skips prepr only when all four of these hold. Each one fails closed, and the result is named on one `app_push: ROW-ONLY:` line:

- (a) HEAD has exactly one parent, and that parent is the live pull-request head.
- (b) `git diff --name-status <live> HEAD` is exactly one added file: `delivery_row.sh`'s `$ROW_DIR/<N>.md` for the listing's `<N>`.
- (c) That file is one row, anchored on `<N>` and open. It is read with `tests/delivery_status.py`'s `anchored` and `OPEN_STATUS`.
- (d) The body file is the live body under one new `## Head` note, as `head_note.py`'s own `prefix(live, note)` builds it.

When the skip is taken, `row_only_checks` runs the two body checks that pr-contract runs. Both run at the judged head and with the pull request's live title:

1. Step 7's body contract, `policy_lint.mjs --pr-body --head --title --paths-file --existing-file`. It is handed the credential prepr's step 7c reads: `gh_credential`'s order, which is `GITHUB_TOKEN`, then `GH_TOKEN`, then `gh auth token`. So the contract's red-history walk reads the ancestry reds.
2. The carry check, `carry_audit.py check --body`.

A refusal from either one pushes nothing. In every other case prepr runs exactly as it does without the flag. The push is pinned to the HEAD the verdict judged. `update_pr.sh` passes `--row-only` only for code sha `-` (`# mut:rowonly`) and prints app_push's `ROW-ONLY:` line. A code sha never asks for it.

**This round answers the four blocking items of `Fix review: blocked 93015eca...`:**

1. W4 now dies. Two new arms drive a row that is anchored on #7 but `**merged**`: the stubbed `oclosed`, and `real git: a row anchored on #7 that is not open runs prepr`.
2. W7 now dies. `romoved` is the `--row-only` twin of `rmoved`: HEAD moves after the verdict, the push is refused, and nothing is minted or pushed.
3. The body routes every finding item. `carry_audit.py check` on this body gives 0 unrouted (`## Figures`). The row-only path now runs the same check, so a row-only push cannot carry such a body.
4. Step 7c is no longer dropped. The contract is handed 7c's credential and reads the same check runs; see the next paragraph.

**Why the other prepr steps are not re-run on the skip.**

- The body contract and the carry check run.
- The row lint is (c).
- **7c (ancestry reds).** prepr's 7c reads every failed check run on the branch's pushed commits from `merge-base..<remote head>`. It feeds them to the body check, which exempts the main-graded reporters (`MAIN_STATE_REPORTERS`) and pr-contract. The contract's red-history walk (`redHistoryForHead`) reads the same endpoint over `merge-base..HEAD`. HEAD is the live head plus the row commit. That commit is unpushed, so the walk reads it as no runs (404). This gives the same set of commits and the same exclusions, through the same `checkPrBody`. The only gap the reviewer found was the credential, which 7c takes from `gh auth token` and the walk does not. `row_only_checks` now hands that token on.
- **Claim files, `VERSION`, the manifest, code, closures and transport.** None of these can move under (a)+(b). A second path in the diff, a claim file included, fails (b) and takes the full prepr. That is the null control below.

**Alternatives and why each lost (fixer.md step 17).**

- **Decide the skip in `update_pr.sh` alone, via `PREPR_BODY_PATH_ONLY`.** This bends a flag built for one step's test into a bypass. It would also make the tool that mints and pushes take a caller's word that the push is row-only.
- **A `prepr.sh --row-only` mode.** This adds a second entry point to prepr and still needs app_push's live-head read to decide.
- **`--recarry`.** Its (a) requires a two-parent merge.
- **For item 4, calling prepr's `reds_line` directly.** app_push would have to source prepr.sh, a 2977-line script that runs its own main on load. It would also run a second walk over check runs the contract already reads. Handing on the credential reuses the one walk that pr-contract runs in CI.

`delivery_row.sh` is unchanged: the verdict sources it for `ROW_DIR`.
🤖 Generated with [Claude Code](https://claude.com/claude-code)
https://claude.ai/code/session_01HtDdgVefD3aTZG3Qi94jUw

## Head

`daa1d0dbd544588b25920e971a4261dfe1622560` is the code head. It is the round-2 commit on top of `bea33c801e2a9c79c5b105a5fcc03be0080a5afe`. That commit merges origin/main `22615537a497c87cf0560ecc7dd09faac52b1de5` (tip at 2026-10-21T13:10:39Z) into the round-1 code head `e6dba2408a5f101ee43917b9e64b245888ec664f`, with no conflict. Everything below is measured at `daa1d0dbd`, on 2026-10-21.

## Mutation proof

Each mutant is applied in place in the worktree as an exact-string replacement, then the owning self-test runs, then the file is restored with `git checkout`:

- W1 widens (b) to "the diff contains the row" (`printf '%s\n' "$d" | grep -qxF ...`). Result: 2 failed: `omore`'s `... prepr ran once ...` and `real git: the same commit with one more file runs prepr (null control)`.
- W2 changes (a)'s `-eq 1` to `-ge 1`. Result: 1 failed: `otwo`.
- W3 replaces (d)'s exit with `sys.exit(0)`. Result: 2 failed: `obody` and `real git: a body that is not the live one under one new note runs prepr`.
- W4 deletes ` and OPEN_STATUS in ls[0]` (blocking item 1). Result: 2 failed: `oclosed` and `real git: a row anchored on #7 that is not open runs prepr`.
- W5 replaces the `row_only_checks` call with `true`. Result: 8 failed. Among them are `the body contract ran in its place ...`, `and the carry check pr-contract runs ...`, and both credential arms.
- W6 changes `update_pr.sh` to `RO=--row-only` for every code sha. Result: `pr_args self-test: 57 checks, 1 failed`, and the failing check is `null control: a code sha never asks for --row-only, so its push runs the full prepr`.
- W7 narrows the head guard to `[ "$recarry" = 0 ] || ...` (blocking item 2). Result: 1 failed: `romoved`'s `naming both shas, and nothing was minted or pushed` (got `018`: the push ran and 8 curl calls followed).
- W8 drops the `gh auth token` fallback (blocking item 4). Result: 1 failed: `the contract was handed gh's stored token, so its red-history walk reads the ancestry reds prepr's 7c reads`.
- W9 drops the carry check (blocking item 3). Result: 3 failed: `and the carry check pr-contract runs ...`, `--row-only: a body whose finding names no destination refuses (carry_audit.py) ...`, and its `nothing was minted or pushed`.

Failing test first: W8 and W9 are the round-1 production lines, so the new arms fail against them. W4 and W7 restore round-1 code that was already correct but that no arm pinned. Each mutant fails only its new arm.

## Null control

- M0 is the same runner with no replacement. Result: `app_push self-test: 179 checks, 0 failed`. So the in-place runner fails only on a mutant.
- `oenvcred` sets `GITHUB_TOKEN` in the environment. The token handed on is that one, and `gh auth token` is not called (`... gh's store is not read`). The credential read therefore adds a token only where 7c would find one and the environment has none.
- Skip versus prepr on the same row commit: `real git: ensure_row's own row commit on the live head skips prepr` passes. The same commit amended with one more file runs prepr, and so does the stubbed `omore`.
- The live walk on the reviewed head 93015eca with the round-1 body, using the same command and inputs:
  - With no token: `skip red-history ... UNCHECKED`.
  - With the environment's token: `record red-history 3 commit(s) between origin/main and this head, every failure conclusion across them: nightly-status`.
  - Both gave `PR-BODY: 0 error(s)`, because `nightly-status` is a `MAIN_STATE_REPORTERS` member. So the credential is what turns an unread history into a read one. The refusal of an unanswered red is pinned by policy_lint's own fixtures.

## Figures

- `bash tools/pr/app_push.sh --self-test` gave `app_push self-test: 179 checks, 0 failed` at the head. The counts per mutant are in `## Mutation proof`.
- `bash tools/audit/seat/update_pr.sh --self-test` gave `delivery_row self-test: 5 checks, 0 failed` and `pr_args self-test: 57 checks, 0 failed`. The drop from round 1's 59 is main's rewrite of pr_args.sh's open_pr cap arms, as the review found.
- `python3 tests/closure.py select --diff 22615537a497c87cf0560ecc7dd09faac52b1de5` gave `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, over four changed files.
- The `run_always` lines of `tests/run.sh`, run with `PYTHONPATH=tests/hastub` under a Python 3.13 venv built from `tests/requirements-ci.txt`:
  - `python3 tests/env_drift.py --claims-only 22615537a497c87cf0560ecc7dd09faac52b1de5` printed `claims hygiene: ... ok`.
  - `python3 tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`.
  - `python3 tests/layout.py` printed `layout self-test: ok`.
  - `python3 tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `python3 tests/entities.py` printed `ALL 2375 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 22615537a497c87cf0560ecc7dd09faac52b1de5` printed `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/carry_audit.py check --body <this body>` printed `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, and it printed the same with `--roster-ref origin/handoff/audit-r10-roster`. The null control is the same command on the round-1 body, which printed `CARRY-AUDIT: 2 finding item(s): 0 routed, 2 unrouted, 0 bad destination(s)`, the reviewer's reading.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` exited 0 at the head, with no REFUSE line. On this unpushed seat branch its push-order and ancestry-reds steps print their skip, because no remote branch exists yet. The ancestry reds of the pull request's own commits are answered under `## Red checks`, read from the check-runs API.
- Not measured: the wall-clock time of a live row-only push. It needs the App key, which no seat holds. The 30+ minutes is the brief's measurement.

## Red checks

- **pr-contract** was red on 947d3631 (two runs) and on 93015eca. Each time the failing step was `Every finding the body records names its destination` (`carry_audit.py check`). The cause was the round-1 body: its `## Forward-carry` and `## Friction` items named no destination.
  - The cheaper detector is the seat's own pre-push gate. prepr runs pr-contract's contract (step 7) but not `carry_audit.py`, so the red got past it.
  - The standing cost of adding it is one ~0.1 s Python call per prepr run. This PR adds it to the row-only path. Adding it to prepr, or to fixer.md step 5's gate, is carried to R10-POLICY-FIXER-MD under `## Forward-carry`.
- **nightly-status** was red on 93015eca. It is main's red: it reports the last concluded scheduled run of `Tests` on main, and that run (39563978649, 2026-10-21, `c77f89dc6`) failed. This diff touches only seat tooling. It is not this PR's red.

## Forward-carry

- prepr.sh does not run `carry_audit.py check`, which is pr-contract's last step. So "prepr passes" does not mean "pr-contract's body steps pass". fixer.md step 5 nevertheless names a body passing prepr as the seat's gate. This PR's round-1 body passed prepr and was refused by pr-contract three times for exactly this reason.
  - R10-POLICY-FIXER-MD disposes fixer.md's recurring friction (#2378), and this is one more line for it. The roster's R10-PREPR-CAP, which touched prepr, is done on the tree's roster, so it is not a live destination.
  - The decision is one of two: prepr runs the carry check as a body step beside step 7, or step 5 names `carry_audit.py check --body` beside prepr. Carry: R10-POLICY-FIXER-MD

## Friction

fixer.md-step-5: cost: in this cloud container the system `python3` is 3.11, which cannot parse `tests/entities.py`. The always-run checks needed a 3.13 venv built by hand with `uv` from `tests/requirements-ci.txt`. Carry: dismissed: environment-only, the container image's interpreter, no repository change can fix it
