prepr's `closures` step (6b) default-skips off Linux, since CI's required `closures` context and
`closures-autofix` own the check, with `PREPR_RECORD_CLOSURES=1` as the opt-in for a lane that needs a
first-green head. The recorder also dies with the prepr. Step 6b runs `closures_line` as a job the prepr
`wait`s on (`closures_step`), and a `$$` watchdog reaps the recorder's process group. Linux is unchanged.
The policy half is `dev/governance/rules/gate-scoping.md` and its two generated copies.

This round changes no code. The review's block was carry-missing: the sibling seams (prepr's
foreground heavy steps 3 to 3h) were routed to `#201`, whose carry file held no entry. They are now
carried to the live roster group R10-FLOW-JIDOKA, which owns `tools/pr/prepr.sh`, and its brief cites
#2528 on the roster ref (`## Figures`). The three round-1 items the review found unrouted are settled
under `## Forward-carry`.

## Head

`20d129b11e3dc3880e1c9cb2fe3ce0d6b9345370`: the previous head `1723d8743619f397bcf9e04a219e1a581f4a736c` plus one merge of
origin/main `752f697cc` (read 2026-10-22T17:03:52Z), never a rebase; it merged without conflict. The merge base is
`752f697cc`. No code changed this round. `tools/pr/prepr.sh` at this head is blob `a0edc03ab`; main's own
changes to it came in with the merge. Every figure below is at `20d129b11` over base `752f697cc`.

## Mutation proof

Rule: each mutant is a detached worktree at `bb53ba321` with one patch to `tools/pr/prepr.sh`, applied with
`git apply` (the patches are the review's own `mut-*.diff` evidence, which apply unchanged to this blob).
The run is `bash tools/pr/prepr.sh --self-test` under `/etc/profile.d/hpo-toolchain.sh`. The count is the
totals line, and the names are every `^  FAIL` line. Each worktree was restored and read 0 dirty files
before removal. The driver is a scratch seat script.

- **M7**: the watchdog's `kill -TERM -- -"$rpid"` becomes `kill -TERM "$rpid"`. Result 320/3. All three
  reap arms fail with `got gone:gone:alive`: the lane is orphaned.
- **M9**: 6b's `closures_step "$BASE"` becomes `CLOSURES_LINE=$(closures_line "$BASE")`. Result 321/2.
  The TERM-alone arm and the group arm fail with `got alive:alive:alive`.
- **M4sub**: `closures_step` goes back to `$(closures_line ...)`. Result 321/2, the same two arms.
- **M3wd**: the watchdog body becomes `( : ) & wpid=$!`. Result 320/3, all three reap arms
  (`got gone:alive:alive`).
- **M3setm**: delete `set -m`. Result 321/2, the KILL arm and the TERM-alone arm (`got gone:alive:alive`).
- **M1**: delete `closures_records_here`'s `return 1`. Result 319/4: the off-Linux default arm, its two
  skip-line arms and the `=0` arm.
- **M2**: delete the `PREPR_RECORD_CLOSURES` override line. Result 321/2, the opt-in arm and its
  null-control refusal arm.
- **M6**: the override becomes `[ -n ... ]`. Result 322/1, `and PREPR_RECORD_CLOSURES=0 is no opt-in`.
- **M4** (`closures_line` in the foreground, no `&`) and **M5** (`exit_on_signals` emptied) give 323/0.
  Both are the equivalent mutants round 2's review accepted (items 25985327 and 7362c299).

## Null control

M0 (unmodified, `bb53ba321`) gave `323 passed, 0 failed`, so every failure above belongs to its mutant. The mutant counts above are at `bb53ba321` and were not re-taken: this round changes no code, and the merge only brought main's own edits to `prepr.sh`. The unmodified self-test at `20d129b11` reads `333 passed, 0 failed` (`## Figures`). The carry
harness's null control is in `## Figures`: the same count reads 0 on the review's roster `5ffe2a933`.

## Figures

- Finder's harness at both ends (the review's `ev/carry-owner.txt` check, re-keyed to the destination):
  a scratch script counts lines citing `#2528` in `dev/programme/carries/carry-201.json` and in
  R10-FLOW-JIDOKA's `brief` and `carry` on a roster SHA (`git show <sha>:...wave-r10-groups.json | jq ... | grep -c '#2528\b'`).
  At the review's roster `5ffe2a933`: carry-201.json 0, R10-FLOW-JIDOKA 0. At roster `743463c61`
  (`origin/handoff/audit-r10-roster` read 2026-10-22T01:01:24Z; the sentence landed in `2ce054264`):
  carry-201.json 0, R10-FLOW-JIDOKA 1. Null control for the counter: the same
  script keyed to `#2582`, which R10-FLOW-JIDOKA's carry already names, reads 1 at both SHAs, so a 0 is
  not the counter failing to match.
- Carry audit at `20d129b11`: `python3 -I tools/audit/carry_audit.py check --body <this body>` (no `--roster-ref`, main's roster)
  printed `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)` (rc 0). Null control: the
  run at `1723d8743` on main's roster before R10-FLOW-JIDOKA existed there is the three red `pr-contract` runs above.
- Self-test at `20d129b11` (`bash tools/pr/prepr.sh --self-test`, seat toolchain from `/etc/profile.d/hpo-toolchain.sh`): `333 passed, 0 failed`.
  Main added 10 arms since `bb53ba321`. Under the ambient python3 (3.11, no toolchain profile) 9 arms fail with the interpreter-not-found refusal; that is the environment, and the null control for the 0.
- At `20d129b11`, under the seat toolchain with `PYTHONPATH=tests/hastub`, each rc 0:
  `node tools/policy/rules_sync.mjs --check` (`RULES-SYNC ok`).
  `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` printed
  `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, with `scope.run` = `tests/entities.py`.
  `python3 tests/entities.py` (`ALL 2397 ENTITY CHECKS PASSED`),
  `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)` (`claims hygiene: 752f697ccc... ok`),
  `python3 tests/closure.py selftest` (`ALL 112 closure shrink pins PASSED`), `python3 tests/layout.py`
  (`layout self-test: ok`), `python3 tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`),
  `python3 tests/structure.py` (`STRUCTURE RATCHET PASSED`), `python3 tests/throwaway_git.py --check`
  (0 refused), and `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`
  (`Architecture score: dS +0.0000 NULL`).
- Class enumeration (step 8). `grep -n 'PREPR_RECORD:-' tools/pr/prepr.sh` returns one production line,
  in `closures_line`, which is closed. The sibling-seam rule is
  `awk -v r=$(grep -n '^rc=0$' tools/pr/prepr.sh | cut -d: -f1) 'NR>r && /(node|python3|bash) [^|]*>\/tmp\/prepr-/' tools/pr/prepr.sh`;
  it returned 18 lines (steps 3 to 3h) at both `df97bd446` and `bb53ba321` (not re-run at `20d129b11`). Its null control: the same rule
  over a scratch copy of `prepr.sh` with one appended line, a python3 run redirected to a
  `/tmp/prepr-null` file, returns 19. All 18 are one
  distinct finding, carried to R10-FLOW-JIDOKA (`## Forward-carry`).
- Release and claim files: `git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md tests/golden`
  exits 0.
- nightly-status filter: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -E '^(custom_components/|tests/replay|tests/hastub/|tools/replay/|tests/mutation)'`
  prints nothing (rc 1).

## Red checks

- The required `pr-contract` check ran red four times at `1723d8743` (check-runs API, read 2026-10-22):
  119585492906, 119585669593, 119587185157 and 119691498245. Cause: BAD-DEST R10-FLOW-JIDOKA. `carry_audit`
  read main's roster, where that group did not exist when those runs read it. It exists on main's roster now
  (`git show origin/main:dev/programme/rosters/wave-r10-groups.json | jq '.groups[]|select(.group=="R10-FLOW-JIDOKA")|.group'`
  prints it), and at this head `python3 -I tools/audit/carry_audit.py check --body <this body>`, with no
  `--roster-ref`, prints `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)` (rc 0).
- Every other red in the branch history, from the check-runs API: `10f85c3ee` 49 runs, one red,
  `nightly-status` (job 119521063745); `5332c59f9` 49 runs, one red, `nightly-status` (job 119339580088).
  `nightly-status` grades main's last scheduled `Tests` run and is not a required context on `main-protect`;
  this diff reaches nothing either nightly lane reads (the filter in `## Figures` prints nothing). The red is
  main's. The other commits in the branch history (`df97bd446`, `bb53ba321`, `d7ab16465` and the rest) list 0 runs.
- `20d129b11` has not run CI yet: it is pushed to the handoff ref only.

## Forward-carry

- Sibling seams of the orphaned-recorder class: prepr's foreground heavy steps 3 to 3h, the 18 lines the
  `## Figures` rule returns, among them step 3h's `bash tools/pr/prepr.sh --self-test` and the
  policy-lint mutants drive. Control: a KILL or TERM to the prepr during step 3h leaves the self-test or
  mutants drive running (KILL orphans it) or deferred (a TERM to the prepr alone waits behind it). Fix
  shape: this diff's `closures_step`, a job the prepr `wait`s on with a `$$` watchdog over its own
  process group, per heavy step. R10-FLOW-JIDOKA owns `tools/pr/prepr.sh` and its roster brief now
  carries this from #2528 (`## Figures`).
  Carry: R10-FLOW-JIDOKA (item 11113f3e)
- Round 1's unpinned reap arm: repaired in round 2, and at this head M3wd, M7 and M9 each fail the reap
  arms. Carry: dismissed: repaired, the arms are load-bearing at this head (item c7585c9b)
- Round 1's finder's harness: none is committed, so the probe is the reviewers' own instrument, and this
  round's carry counter stays a scratch probe (a one-off grep, `fixer.md` step 18).
  Carry: dismissed: no committed harness exists, disclosed (item b50893bf)
- Round 1's `PREPR_RECORD_CLOSURES=0` opting in: fixed by `[ "${PREPR_RECORD_CLOSURES:-}" = 1 ]`, and M6
  pins it. Carry: dismissed: fixed and pinned by M6 (item 2a8ed562)

## Friction

none

## Approval

Policy half: `dev/governance/rules/gate-scoping.md` and its generated copies. They carry tvofi's
2026-10-20 ruling ("yes, do that": default-skip off Linux, CI's gate plus `closures-autofix` as the
owner, and an opt-in for a lane that needs a first-green head), made under mandate 6175172275. It still
owes tvofi's approving review at the head.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01CEFcwib7dF1PvNxG4UDPjQ

