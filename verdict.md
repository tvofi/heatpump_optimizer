Fix review: blocked cb803e9eedff0a2ea947110e1321cdd6afe0b1d6 class-open: open_pr.sh:125 is dismissed as "no pipefail" but runs under pr_trap's pipefail and misreads a registered worktree (48/50 runs at 81 worktrees)

bus-nonce: a366776e0c62dabea74d6a02c920ecc5

## Block

- The brief asks for each sweep dismissal to have a reason that holds. One does not. The body dismisses `ci-watch.sh`, `open_pr.sh` and `update_pr.sh` as "no pipefail, so grep's status wins". That holds for `ci-watch.sh` only. `open_pr.sh:29` and `update_pr.sh:39` both call `pr_trap`, and `pr_trap` (`pr_args.sh:36-38`) runs `set -Eeo pipefail`.
- `open_pr.sh:125` (`op_clear_leftover`) is `if git -C "$M" worktree list --porcelain | grep -qxF "worktree $WT"; then`. This is the shape the hotfix sweeps: an unbounded producer piped into an early-exit reader under pipefail. Harness (`ev/wt.sh`, `ev/open_pr-worktree-demo.txt`), with SIGPIPE at its default, `set -Eeo pipefail` and 50 runs per row:
  - 81 worktrees (7781 bytes of porcelain), target `w1`: 48/50 runs read the registered worktree as absent.
  - 601 worktrees (58202 bytes): `w1` 50/50, and `w600` (listed last) 48/50, because three porcelain lines follow the match.
  - Null control, 21 worktrees (2021 bytes): 0/50, and `PIPESTATUS=0 0`.
  
  A false negative skips the left-over checkout's removal, so a re-open after a closed-after-p2 stops later at `worktree add` on a host with about 80 or more worktrees. The harness moves under its own perturbation, so this is a live seam. It is neither in the diff nor dispositioned on a reason that holds. The fix has the hotfix's own shape, `grep -qxF "worktree $WT" <<<"$(git -C "$M" worktree list --porcelain)"`, or the body may re-disposition it with a reason that holds.
- `update_pr.sh:69` cites the same false reason, but the line is safe for another reason: the two upstream stages, `git worktree list` and `grep -F "[$BR]"`, read to the end, and `grep -vqF` sees only the few lines on `[$BR]`. Write that reason in place of "no pipefail". It does not block on its own.

## Findings

- Residual (non-blocking): surviving targeted mutants: the sweep's defensive rewrites have no row that fails on the old line. Each was reverted to its origin/main form and its instrument's `--self-test` run on Linux. `app_approve.sh` `$bt` (`if printf '%s\n' "$bt" | grep -qxF "$e"`) gives `355 checks, 0 failed` (`ev/mutant-bt.txt`). `bus.sh` re-cut gives `230 checks, 0 failed`. `handoff_push.sh` gives `6 checks, 0 failed`. The `pr_args.sh` census gives `261 checks, 0 failed`, but with 14 `printf: write error: Broken pipe` lines on stderr (lines 454 and 464), against 0 at the head (`ev/st-*-base.txt` against `ev/st-*-head.txt`). The body claims mutation proof only for the carry and gh_transient lines, and both of those mutants are killed. These four are an unpinned residue, which the barrier lint owed by the body's Forward-carry would pin. Carry: R11-INTAKE-R10-RESIDUE
- Residual (non-blocking): the class control's figure does not re-derive. The body and the carry already written to `handoff/audit-r10-roster` at 7576896c74 (group R11-INTAKE-R10-RESIDUE, carry 151) say the enumeration prints 236 lines at 6858b4abc1. On Linux at 6858b4abc1 it prints 235, and 231 at the head (`ev/sweep-count.txt`, `ev/sweep-base.txt`, `ev/sweep-head.txt`). Whoever acts on the carry re-measures the count at their own merge base and does not trust 236. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Round 1. Reviewed head cb803e9eedff0a2ea947110e1321cdd6afe0b1d6 (`ev/HEAD.txt`), merge base 6858b4abc1941f8f69fe8eebc5a1101527733dff, origin/main at 5b8f05ba4e at review time.
- No pull request exists yet, so there is no review packet, no CI run, and no checks or owed reds to read. `merge_train.py owed-reds` prints `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing` and `validate / validate-hacs`. None has run on this head.
- `git merge-tree --write-tree origin/main cb803e9eed` prints tree b8cd44eee2 with rc 0: it merges cleanly.
- `dev/governance/roles/` has not changed between the merge base and main, so the contract is current. VERSION, the manifest, RELEASE_NOTES and `tests/golden` are untouched.
- The SIGPIPE cause is confirmed (`ev/pipestatus.txt`, `ev/pipe.sh`). Under `set -uo pipefail` with the match first, 8001 lines give `PIPESTATUS=141 0` in 3 of 3 runs, and 1 line gives `0 0`. The here-string returns rc 0 in both cases. With SIGPIPE ignored, the pipe prints `printf: write error: Broken pipe` and returns `1 0`, which is the CI flake's message class. `git ls-remote --heads origin` lists 7952 heads now; the body says 7937, and the commit message says 7933.
- `app_approve.sh --self-test` on Linux (`ev/selftest-*.txt`):
  - head: `355 checks, 0 failed`.
  - merge base: `350 checks, 0 failed`.
  - origin/main: `350 checks, 0 failed`.
  
  The body says 353 and 348, from a macOS run. The +5 delta matches. The absolute counts differ by host, so I could not re-derive them as quoted.
- The mutation proof re-runs and kills both named mutants:
  - Carry line restored: `FAIL CARRY on a head of ours listed first among 20001 branch heads of origin (got '1', want '0')`, `355 checks, 1 failed` (`ev/mutant-carry.txt`).
  - gh_transient restored: `FAIL ... (got '141', want '0')` and `FAIL (and with SIGPIPE ignored ...) (got '...line 160: printf: write error: Broken pipe`, `355 checks, 2 failed` (`ev/mutant-ght.txt`).
- The null control holds at the head: `NO CARRY: the same 20000 heads without it (null control)` and `refused as a head that is not ours` both print `ok`.
- I could not re-derive the body's live `review_carry.py 2b88938 341677c` reading. `fix/r10-hotfix-main-selftest-scope` is no longer on origin, so 341677c1 is no longer a tip, and FRESH-REVIEW is now the correct answer for it. The deterministic stubbed rows above stand in for that reading.
- The other touched instruments' self-tests pass at both ends on Linux:
  - bus: `230 checks, 0 failed`.
  - handoff_push: `6 checks, 0 failed`.
  - pr_args: `261 checks, 0 failed`. The base run prints 14 `Broken pipe` lines and the head run none, which confirms the body's account of where the CI `Broken pipe` lines come from.
- `handoff_push.sh`'s `grep -vE ... >/dev/null` was checked because GNU grep can short-circuit when its output is `/dev/null`. On GNU grep 3.11 it reads to the end: `PIPESTATUS=0 0` against `141 0` for `grep -vq`, over 20001 lines with the match first, in both signal regimes (`ev/handoff_push-devnull.txt`, `ev/devnull.sh`).
- The other dismissals were checked and hold:
  - `app_approve.sh:154`: one line from `tail -1`.
  - `bus.sh:827`: a review_packet message. The 151 rows at `bus.sh` line 1267 and later are self-test rows.
  - `cloud_relay.sh` (9): hex values, plus the self-test fixtures at 967 and 1139.
  - `heartbeat.sh`: lines 75-95 are inside `hb_self_test`.
  - `seat_venv.sh`: self-test.
  - `tick_loop.sh:184`: `sed '2{p;q;}'` emits one line. The rows from 224 on are in the self-test, which turns pipefail off at 216.
  - `ci-watch.sh`: no pipefail, and no source of `pr_trap`.
  - `app_push.sh:930/945`: one `ps` character.
  - `prepr.sh:3198/3200`: `log -1 %B`.
  - `push.sh:170/206`: the `## Head` section, read with awk.
  - `pr_args.sh:1399`: the `## Head` section.
- The forward-carry is in the tree. It is on `handoff/audit-r10-roster` at 7576896c74, under `groups[503]` R11-INTAKE-R10-RESIDUE, as carry 151. It states the precondition and the control.
