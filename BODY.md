Root cause for the third recurrence of one red: #2065, #2066 and #2070 each added a harness under the retired `tools/audit/harnesses/` and each turned `fast (3.14)` red on `tests/layout.py` ("re-adds a moved path"), with "Red checks: none" in the body.

**Cause.** The instruction was obeyed and wrong. `CLAUDE.md` Instruments (per-group harnesses in `tools/audit/harnesses/`) and `fixer.md` step 18 (a harness in `tools/audit/harnesses/`) both named a directory that R9-RO-8 moved to `dev/audit/harnesses/` on 2026-10-07; nothing re-pointed them (`tests/layout.py --stale` lists 867 live lines citing a landed move at this head, report-only). **Process state: (d)**, a sound process whose precondition moved underneath it; plus the detector was in no local path (`prepr.sh` never ran the layout guard), so nothing noticed before CI.

**Countermeasure.** (1) Re-point the two instructions to `dev/audit/harnesses/` and `dev/audit/rounds/round9/`. (2) `prepr.sh` step 6e (6d is `predict_line`) runs `tests/layout.py --guard` against the merge base, so the process notices its own changed precondition for any future move, not only this one. Not built: a `pre-edit.sh` hook (a Bash-created file bypasses it, and prepr covers every route at 0.4 to 2.1 s); the other stale lines (867, the move stage's report-only backlog).

**Cost test.** Cheaper detector: `layout.py --guard` run locally. Standing cost 0.44 s on a quiet box (my run, load not recorded) and 0.95 to 2.10 s over 11 runs at load average 46 to 58 on 8 cores (the reviewer's measurement); take 0.4 to 2.1 s. Defect cost, three samples of the fast job going red on this guard: #2065 30m28s (check-run 113574473913), #2066 30m48s (113577108665), #2070 29m50s (113595667988), so 29m50s to 30m48s each, three times in one evening. Verdict: passes, by about 860x (30m28s against 2.1 s at the worst measured load).

**Class search (root-cause.md section 3).** The same obeyed-and-wrong shape also sits in `.claude/workflows/audit-find.js` and `audit-verify.js`, which tell a seat to write under the retired round directory. Disposition: not re-pointed here (about twenty strings across two wave scripts, graded by the wave-script checks), carried to R9-RO-9 (#1922, the stage that retires canon) in `dev/programme/carries/carry-1922.json`. Caught meanwhile: a planted new file under a retired round directory is refused by the guard's zero-categories arm (rc 1), so round 10's first commit fails in prepr, not in CI.

CLAUDE.md is policy: it merges on the owner's approving review (orchestrator gives it under the mandate).

## Head

`00e31e8a364e2657d8db32e97d1853895c476170` is the handoff head: `bca74aa97b35f6cdd02810f5f6cbf965a7e6daa6` (the round-2 fix below) with main `7cd5a588cbbbef354c00148040da2d720b8a888c` merged in, no resolution.

`bca74aa97` fixes the round-1 head `04d10721b612fab802e57516bf57c5cae876ab91`, which is the clean merge of the judged head `316a364148cfdd47019314decae0037890c7211d` with main `23d354970fcaababe8e67a5c04c326cc8bc79e49`. `04d10721b` is the head both reds were measured at; main moved to `7cd5a588c` after it, so the round-2 delta re-takes every `origin/main`-dependent figure. The judged code is unchanged; the round-1 head carried only this PR's own row, `dev/programme/delivery/2072.md`, on top of `8766b840f5582e96d13b7a322da0662433cce9a5`.

8766b840f5582e96d13b7a322da0662433cce9a5

## Mutation proof

Retaken at `00e31e8a3` (a merge re-executes steps 2–8). Replacing the guard call in `moved_line` (`out=$(cd "$1" && python3 -I tests/layout.py --guard --base "$2" 2>&1); r=$?`) with `out=ok; r=0` turns these prepr self-test rows red:

- `a new file under a landed-retired directory is refused` (got 0, wanted 1)
- `and the refusal names the new path` (got 0, wanted 1)
- `and the ok line is the guard's own, so it ran` (got 0, wanted 1)
- `a new line citing a retired path is refused` (got 0, wanted 1)
- `and the hint says to re-point the citation, not to place a file` (got 0, wanted 1)
- `a new file in no category is refused` (got 0, wanted 1)
- `and a refusal with no new path does not say to move it there` (got 0, wanted 1)

**240 passed, 7 failed** (rc 2), against the clean tree's `247 passed, 0 failed`: the 7 reds are exactly the layout-guard rows the mutated `moved_line` stops driving, and no other row moved. Run took 1083 s at load average ~62 on 8 cores (other seats' suites were running); the tree was restored to `00e31e8a3` before the next measurement.

## Null control

The unmodified tree at `00e31e8a3`: `python3 tests/layout.py --guard --base origin/main` prints `layout: GUARD: 0 refusal(s) against 7cd5a588cbbb`. The self-test's clean row (the same file at `dev/audit/harnesses/`) passes and prints the guard's own ok line; a tree with no `tests/layout.py` skips (rc 3), never refuses. With a planted `tools/audit/harnesses/draw_range_evidence.py` committed over origin/main, the guard prints `placement: ... re-adds a moved path; it lives at dev/audit/harnesses/`, rc 1, 0.44 s (the defect, reproduced). Full self-test at this head: `247 passed, 0 failed` (`bash tools/pr/prepr.sh --self-test`, rc 0).

## Figures

- `layout: 867 live line(s) cite a landed retired path`: `python3 tests/layout.py --stale` at `00e31e8a3`
- `layout: GUARD: 0 refusal(s) against 7cd5a588cbbb`: `python3 tests/layout.py --guard --base origin/main`
- `STRUCTURE RATCHET PASSED`, 16 metrics at their recorded caps: `python3 tests/structure.py`
- `ALL 2250 ENTITY CHECKS PASSED`: `PYTHONPATH=tests/hastub python3 tests/entities.py`
- `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (empty `scope.run`): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <fresh mktemp dir>` — a fresh directory each run, because the command writes `scope.{json,run,skip,txt}` into its workdir and a second run there reads its own output as a change
- `247 passed, 0 failed`: `bash tools/pr/prepr.sh --self-test` at `00e31e8a3`

## Red checks

`instrument-self-tests`: at `04d10721b` the job reported `FAIL no early-exit grep reads a pipe under pipefail in the drained scripts (got 1, wanted 0)`, pointing at `tools/pr/prepr.sh:1398`: `printf '%s\n' "$flow" | grep -q 'moved_line "'` (243 passed, 1 failed, exit 2). `grep -q` exits on its first match, the `printf` writer is SIGPIPE'd, and under `set -o pipefail` the pipeline then reads 141 — no match — so the call-site arm read as a failure. The rule is right; the line was this branch's own new self-test arm, latent until main drained `prepr.sh` under it.

**Provenance.** At the judged head `316a36414` both `instrument-self-tests` and `pr-contract` were green (check-runs API). The rule came in from main: commit `09d2061b247a77e27ba625c81ef25a9909726ef9` ("drain every early-exit grep under pipefail in the gating scripts", PR #2067, merge `d0f085ffb`) added `PIPE_GREP_Q_FILES` and `pipe_grep_q_sites` (the `tools/pr/prepr.sh:1941` region), and it is **not an ancestor of `316a36414`**. The recarry at `04d10721b` merged a main carrying it under an already-reviewed, green head, so the wider rule scanned this branch's own lines for the first time in CI. A real latent bug the wider rule caught, not a false positive.

**Fix.** `bca74aa97` replaces the piped form with the file's own non-pipe idiom for a captured string — the `case "$flow" in *'moved_line "'*) true ;; *) false ;; esac` its two sibling arms already use two lines above, so nothing can SIGPIPE. Sweep of this branch's added lines for the same class (an early-exit `grep` — `-q` or `-m` — reading a `printf | echo` pipe under `pipefail`): **2** sites. The one CI named, and `grep -m1 '^    '` over a `printf` pipe in `moved_line` (line 691), whose status was never read — latent, not a second red, fixed here to `grep -m1 '^    ' <<<"$out"`. The two remaining piped `grep -m1` sites in `prepr.sh` (lines 390, 676) predate this branch's base and are outside this lane. **The fix is the line, not an exemption**: the rule is not weakened, widened, narrowed or allow-listed anywhere.

**Cheaper detector and its standing cost.** The same arm is in the local `prepr.sh --self-test`, which any change to `prepr.sh` already owes (`selftest_owed`) and which the push path normally runs. Standing cost on this box: the whole self-test took 221 s, 406 s and 551 s over three samples (box load varying; the class arm itself is a 0.036 s `grep` over the six drained scripts), against the CI job's 100 s at `04d10721b`. So the honest claim is not that the local run is cheaper in wall-clock — it is that the detector is reachable before the push, and its arm is sub-second. The recarry path that produced this head skips prepr (`app_push.sh`: `RECARRY: prepr SKIPPED`, PR #2069 / `a9baf164c9386ad2973bea129c9aaf4f73e4b433`), so the local gate never re-ran on the widened set: **process state (d)**, the process sound and its precondition (main's rule set) changed underneath it. The definitive cause and any countermeasure are the root-cause seat's, not this fix's.

`pr-contract` was red only as the consequence: `check instrument-self-tests is red and ## Red checks does not name it`, which this section now answers.

## Forward-carry

`dev/programme/carries/carry-1922.json` (the fifth entry): the round-runner workflows' retired round paths.

## Friction

none

## Approval

Pending, not yet given. This diff re-points one line each in `CLAUDE.md` and `dev/governance/roles/fixer.md` (two retired directory names to their current ones) and states no new obligation. It merges only on the owner's approving review at its head, which the orchestrator gives under the standing mandate; this section records that the approval is owed, not that it was granted.
