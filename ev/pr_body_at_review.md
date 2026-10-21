fix(seat): a row-only `update_pr.sh` push takes pr-contract's body contract and carry check, not the full prepr

`update_pr.sh <branch> - <body>` exists to add a pull request's own delivery row. Before this change its push ran the full `prepr.sh`: suites, mutants and the heavy-slot lease. On 2026-10-21, on a box queued on `gate_lock.py`'s four slots, the one-line rows for #2557 and #2558 waited 30+ minutes, and `bus.sh dispatch` refuses a head without `dev/programme/delivery/<N>.md`, so reviewer dispatch waited on them too.

**What changed.** `tools/pr/app_push.sh` gains `--row-only` beside `--recarry`, built the same way as `recarry_verdict`. `row_only_verdict` reads HEAD once, and takes the live head, number, title and body from the open-pull-request listing app_push already reads. It skips prepr only when all four hold; each fails closed, and the result is named on one `app_push: ROW-ONLY:` line:

- (a) HEAD has exactly one parent, and that parent is the live pull-request head.
- (b) `git diff --name-status <live> HEAD` is exactly one added file: `delivery_row.sh`'s `$ROW_DIR/<N>.md` for the listing's `<N>`.
- (c) That file is one line, a row anchored on `<N>` and open: `len(ls) == 1`, `tests/delivery_status.py`'s `anchored` and `OPEN_STATUS`.
- (d) The body file is the live body under one new `## Head` note, as `head_note.py`'s `prefix(live, note)` builds it.

When the skip is taken, `row_only_checks` runs two of pr-contract's body checks at the judged head with the live title: `policy_lint.mjs --pr-body --head --title --paths-file --existing-file` (handed prepr step 7c's credential, so the red-history walk reads the ancestry reds) and `carry_audit.py check --body`. A refusal from either pushes nothing. In every other case prepr runs as without the flag, and the push is pinned to the HEAD the verdict judged. `update_pr.sh` passes `--row-only` only for code sha `-` (`# mut:rowonly`) and prints app_push's `ROW-ONLY:` line; a code sha never asks.

**This round** merges `origin/main` into the branch; the one conflict was `tools/audit/seat/pr_args.sh`, where main (#2548, #2560) added the open_pr/update_pr race arm and the unpushed-work arms. Main's arms are kept verbatim. This branch's row-only arm used the same fixture branch `fix/r` and marker `$t/fixr` as main's race arm, so it now has its own, `fix/w` and `$t/fixw`; its mutant id stays `mut:rowonly`, unique in the file. `update_pr.sh` and `app_push.sh` merged without conflict. No production line changed in the merge.

**Why the other prepr steps are not re-run on the skip.** The row lint is (c). Prepr's 7c reads the failed check runs on `merge-base..<remote head>`; the contract's red-history walk reads the same endpoint over `merge-base..HEAD`, where the unpushed row commit reads as no runs, and `row_only_checks` hands on 7c's credential. Figure lint and preflight read only the body and the tree: (b) leaves the tree the live head's plus one row file and (d) leaves the body the live one plus the caller's note. Claim files, `VERSION`, the manifest, code, closures and transport cannot move under (a)+(b); a second path in the diff fails (b) and takes the full prepr.

**Alternatives and why each lost (fixer.md step 17).** Deciding the skip in `update_pr.sh` alone via `PREPR_BODY_PATH_ONLY` bends a flag built for one step's test into a bypass and takes a caller's word. A `prepr.sh --row-only` mode is a second prepr entry point that still needs app_push's live-head read. `--recarry`'s (a) requires a two-parent merge. Calling prepr's `reds_line` means sourcing `prepr.sh`, which runs its own main on load. A byte-exact compare of the row blob would pin its wording to the title the listing carries now.

`delivery_row.sh` is unchanged: the verdict sources it for `ROW_DIR`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_015dUg6poUKeLkzQ3TBdmzAL

## Head

`4ef1a8270f3bd30bc6c313c950f6f44713a1442d` merges the authored code head `4b46b23ecaf3ccfb92977455176442d5411ad400` and then merges origin/main `57f0c9c77` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`4b46b23ecaf3ccfb92977455176442d5411ad400` is the code head: a merge of origin/main `f2fb1b0e950ecd047b7f08b3adef93776a622540` (read 2026-10-21T18:00Z) into the previous PR head `54bf182104e450c0ac2e6eb007da59b9315e0565`. Everything below is measured at it, 2026-10-21.

## Mutation proof

Each mutant is one exact-string replacement in its own detached worktree at the head (a replacement matching other than once aborts), run against the owning self-test, then the worktree is discarded. The runner is the M0 control below. Production predicates only, none a tail line.

- W1, (b) widened to `grep -qF` of the row in the diff: `app_push self-test: 182 checks, 4 failed`, among them `real git: the same commit with one more file runs prepr (null control)`.
- W2, (a)'s `-eq 1` to `-ge 1`: 1 failed (`otwo`).
- W3, (d)'s refusal to `|| :`: 2 failed (`obody`, `real git: a body that is not the live one under one new note runs prepr`).
- W4, ` and OPEN_STATUS in ls[0]` deleted: 2 failed (`oclosed`, `real git: a row anchored on #7 that is not open runs prepr`).
- W5, the `row_only_checks` call replaced by `true`: 8 failed, among them `the body contract ran in its place ...` and `... the carry check pr-contract runs ...`.
- W6, `update_pr.sh`'s `RO=--row-only` for every code sha: `pr_args self-test: 63 checks, 1 failed`, `null control: a code sha never asks for --row-only, so its push runs the full prepr`.
- W7, the head guard narrowed to `[ "$recarry" = 0 ] || ...`: 1 failed (`naming both shas, and nothing was minted or pushed`).
- W8, the `gh auth token` fallback replaced by `:`: 1 failed (`the contract was handed gh's stored token ...`).
- W9, the carry check replaced by `true`: 3 failed.
- W10, (a)'s parent-is-live refusal to `true`: 2 failed (`olive`, `real git: the row on a commit past the live head runs prepr, though the tree diff is the row alone`).
- W11, `len(ls) == 1 and ` deleted from (c): 2 failed (`omulti`, `real git: a row file of two lines, the first the open row anchored on #7, runs prepr`).
- W12, the `anchored(...)` conjunct deleted: 1 failed (`orow`).
- W13, the contract's rc propagation `[ "$rc" = 0 ] || exit "$rc"` replaced by `:`: 2 failed.
- W14, the skip taken unconditionally: 30 failed.
- W15, `--head HEAD` for the judged sha: 1 failed.

## Null control

- M0 is the same runner with no replacement: `app_push self-test: 182 checks, 0 failed` at this head. So the runner fails only on a mutant.
- The unmodified tree: `bash tools/audit/seat/update_pr.sh --self-test` printed `delivery_row self-test: 5 checks, 0 failed` and `pr_args self-test: 63 checks, 0 failed`; `bash tools/pr/app_push.sh --self-test` printed `app_push self-test: 182 checks, 0 failed`.
- `real git: ensure_row's own row commit on the live head skips prepr` passes, so the refusal arms come from the defect they name, not from the fixture.
- `python3 tests/throwaway_git.py --check` printed `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`: no self-test builds a git repo by hand.
- `git merge-tree --write-tree origin/main 4b46b23ecaf3ccfb92977455176442d5411ad400` printed one tree sha and no `CONFLICT` line: the head merges clean into origin/main `f2fb1b0e9`.

## Figures

- `bash tools/pr/app_push.sh --self-test`: `app_push self-test: 182 checks, 0 failed`. `bash tools/audit/seat/update_pr.sh --self-test`: `pr_args self-test: 63 checks, 0 failed`.
- `python3 tests/closure.py select --diff f2fb1b0e950ecd047b7f08b3adef93776a622540` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`; `scope.run` is empty.
- The `run_always` lines of `tests/run.sh`, run with `PYTHONPATH=tests/hastub` under Python 3.13 built from `tests/requirements-ci.txt`: `python3 tests/env_drift.py --claims-only f2fb1b0e950ecd047b7f08b3adef93776a622540` printed `claims hygiene: f2fb1b0e950ecd047b7f08b3adef93776a622540 ok`; `python3 tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`; `python3 tests/layout.py` printed `layout self-test: ok`; `python3 tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`; `python3 tests/entities.py` printed `ALL 2381 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff f2fb1b0e950ecd047b7f08b3adef93776a622540` printed `Architecture score: dS +0.0000 NULL`.
- The class's seams (fixer.md step 8): the rule is every refusal in `row_only_verdict`, enumerated by `sed -n '/^row_only_verdict() {/,/^}/p' tools/pr/app_push.sh | grep -o '_rv_no "[^"]*'`, plus the conjuncts of its two inline Python predicates. Pinned: parent count, parent is live, the one-file diff, (c)'s three conjuncts, (d), "no open pull request" (stub `onone`; W14 fails it). Written triage, each mutant left `182 checks, 0 failed`, not pinned: "HEAD does not read back" (the `_rv_no` line in `row_only_verdict`; an empty HEAD gives no parents, so the parent count refuses); "the diff ... could not be read" (an empty diff is not the one-file diff, so (b) refuses); "delivery_row.sh did not load" (under `set -u` an unloaded `ROW_DIR` aborts app_push before the row read, and a caller-exported `ROW_DIR` still needs (b) and (c) to hold); (d)'s `j > i` (the equality beside it still holds the property; the conjunct only narrows).

## Red checks

none

## Forward-carry

- prepr.sh does not run `carry_audit.py check`, one of pr-contract's body steps, so "prepr passes" does not mean "pr-contract's body steps pass", while fixer.md step 5 names a body passing prepr as the seat's gate. The decision is one of two: prepr runs the carry check beside step 7, or step 5 names `carry_audit.py check --body` beside prepr. Carry: R10-POLICY-FIXER-MD

## Friction

fixer.md-step-5: cost: this cloud container's default `python3` is 3.11, which cannot parse `tests/entities.py`; the always-run checks needed a 3.13 venv built with `uv` from `tests/requirements-ci.txt`. Carry: dismissed: environment-only, the container image's interpreter, no repository change can fix it

