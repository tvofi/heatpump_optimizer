Part of #201.

Group: R10-FLOW-RELAY-HOLD (registration pending: roster PR-B)

Pack file: dev/programme/flow-study/roster/groups/R10-FLOW-RELAY-HOLD.json at PACK_SHA f89bfb4e on branch claude/dazzling-gauss-7l3u2b.

`cloud_relay.sh`'s handoff arm updated every open PR whose `handoff/<topic>` tip was ahead of its head, with no way to exclude one. The roster PR's topic is `audit-r10-roster`, the branch every `roster_edit.py` push (forward-carries included) lands on, so a freeze had to stop all roster pushes (K13a). This adds the hold the study specifies:

- `<state>/cloud-handoff-hold` lists PR numbers, one per line (blank and `#` lines allowed). Only the orchestrator writes it. A final line without a trailing newline is read like any other.
- A listed PR whose handoff is ahead is not updated; the pass prints `cloud_relay: HELD #<pr> <handoff tip>` once. Removing the number resumes it.
- A missing or empty file holds nothing. Any line that is not a plain PR number (or a file that is not a readable regular file) refuses the whole handoff arm for that pass: rc 2, `refused: malformed hold file`, and `OWED <utc> handoff-hold-malformed <file> -` in `<log>.level` until a pass reads the file well-formed (since this round: see Conflict resolution). It never holds all and never holds none.
- `cloud_relay.sh held <pr>` (rc 0 held, 1 not held, 2 malformed) reads the same file through the same parser, so R10-ORCH-MACHINERY's `handoff` job can honour it unchanged: same path, same grammar, same refusal.

Design choices a later seat should not read as bugs, each now pinned by a check and a mutant: the hold is checked after the "handoff already contained in the PR head" test (a held PR with nothing to apply prints nothing; `cloud_relay-9`) and before the failed-update ledger (a hold outranks a recorded failure; `cloud_relay-8`); a refusal stops the handoff arm only, the probe arm of `pass` still runs; the grammar is strict (no leading zeros, no trailing text) because a lenient parse is how "hold nothing" happens silently.

Round 3 answers the review of a8a2778e: R6 (the unterminated-last-line check held #41 on line 1, so dropping `|| [ -n "$l" ]` survived), R3 (no check read the `OWED handoff-hold-malformed` log line) and R4 (the self-test called `held()` but never the `held` CLI arm). Each now has a check that goes red when its production line is removed. The review's notes R12 and R13 (the two orderings above) are pinned too. The hold mutants take per-file ids, `cloud_relay-1` to `cloud_relay-11`, never a new S number (the pack's P6 convention, in this group's own brief): the four formerly numbered S35 to S38 are `cloud_relay-1` to `cloud_relay-4`, and the harness docstring carries main's `S01..S38` plus one sentence stating the convention.

Code-owned: no. None of `tools/audit/seat/cloud_relay.sh`, `tools/audit/seat/INSTRUMENTS.md` or `dev/audit/harnesses/r10_seat_selftests_mutants.py` matches a `.github/CODEOWNERS` pattern (`grep -n "cloud_relay\|tools/audit/seat\|r10_seat" .github/CODEOWNERS` prints nothing).

Round 4 is a conflict-resolution round: main moved under the merge verdict (#2547, R10-TICK-OWED-LEVEL, and #2529, R10-CI-LAYOUT G), and `git merge-tree --write-tree origin/main bc313e7c` conflicted in `dev/audit/harnesses/r10_seat_selftests_mutants.py` and `tools/audit/seat/cloud_relay.sh`.

## Head

`f44296a61f42250b23c0f557a54c6295ab991dac` merges the authored code head `929ee160731596b654d2c69afa1e278d5ca7ec40` and then merges origin/main `46e368127` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

929ee160731596b654d2c69afa1e278d5ca7ec40: the merge commit 47a40f71f (origin/main 5a755f53e merged into the PR head bc313e7cad5e78ea918427db74d33e8109fb00d4, a merge, never a rebase), then one commit, 929ee1607, which moves the malformed-hold refusal onto #2547's level file. origin/main was 5a755f53e (`Merge pull request #2529`) when every figure below was taken, and `git merge-base --is-ancestor origin/main HEAD` held. Measured 2026-10-21T22:43Z.

## Conflict resolution

- `cloud_relay.sh`, header usage lines: both kept. Main's `dispose [--log FILE] <ref> <sha40>` (#2547) replaces the old dispose line, and this PR's `held <pr>` line follows it, padded to main's column.
- `cloud_relay.sh`, the handoff-arm comment: main's text is kept whole (`handoff-no-pr` lines live in `<log>.level`, which every pass rewrites; a failed PR listing leaves them; the log holds events only). This PR's `HOLD.` paragraph follows it, and its refusal sentence now names the level file (below).
- `r10_seat_selftests_mutants.py`, `MUTANTS`: both kept. #2529's S35 to S38 (handoff_push.sh push lines, merge_pr.sh merge line) come first, then this PR's `cloud_relay-1` onward. The docstring auto-merged to main's `S01..S38` plus this PR's per-file-id sentence. No id collides: this PR's mutants were already renamed off S35 to S38 in round 3.
- Semantic, with no textual conflict: after the merge, `orchestrator_tick.py`'s `relay_owed` (#2547) skips every log `OWED` line naming no PR as "an older writer's level lines". This PR's `logline OWED "handoff-hold-malformed <file>"` names no PR, so the tick stopped surfacing the refusal. Driving the merged handoff arm with a hold file of `41x`, then `Tick.relay_owed` on its log, printed only `cloud-relay log: 1 OWED line(s) naming no PR skipped (an older writer's level lines; the level file is the level)` and no `OWED:` line, unflagged. The refusal repeats every pass while the file stays malformed, which is #2547's definition of a level. So 929ee1607 writes it with `level_line handoff-hold-malformed <file> -` and `level_set`, and every pass that reads the file well-formed sets that kind empty, which clears it. The same probe at 929ee1607 prints a flagged `OWED: OWED <utc> handoff-hold-malformed <file> -` from the level file, and the log is empty. #2547's own checks are unchanged and pass. A refused pass returns before `level_set handoff-no-pr`, so it leaves those lines as they were, which is #2547's "unknown is not nothing owed".

## Mutation proof

Failing test first for 929ee1607: the self-test's three new malformed-file checks were written first and run against the merge commit 47a40f71f's production line. Result: `cloud_relay self-test: 189 checks, 27 failed`, 9 each (one per malformed variant) of `and owes handoff-hold-malformed in the level file`, `once after two passes (rewritten, never appended)` and `and the event log carries no refusal line`. The fourth new check, `a pass that reads the file well-formed drops the refusal from the level`, passed there vacuously, since nothing was written. `cloud_relay-11` is what pins it.

New mutants, each planted alone in `cloud_relay.sh` at the head and run on `--self-test` (189 checks unmutated):

- `cloud_relay-6`, no level line written on refusal: `18 failed`. Failing: `and owes handoff-hold-malformed in the level file`, `once after two passes (rewritten, never appended)`.
- `cloud_relay-10`, the pre-merge form (`logline OWED` to the event log): `27 failed`. Failing: the two above plus `and the event log carries no refusal line`.
- `cloud_relay-11`, the clearing `level_set` replaced by `rm -f`: `1 failed`. Failing: `a pass that reads the file well-formed drops the refusal from the level`.

`cloud_relay-1` to `-5` and `-7` to `-9` are unchanged from round 3. Their kills are re-taken below through the harness.

Through the finder's harness at the head (`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`, every mutant): M0 prints `0 seat step(s) red`. All 53 mutant rows are `KILLED`, which is every row main defines plus this PR's eleven. Main's rows are S01 to S38 (S35 to S38 included), S04U and W1 to W3. This PR's are `cloud_relay-1` to `cloud_relay-11`. It ends `RESULT survivors=0`, exit 0. At the merge commit 47a40f71f, before 929ee1607, the same harness gave 51 `KILLED` (main's 42 plus `cloud_relay-1` to `-9`) and `RESULT survivors=0`.

## Null control

- origin/main 5a755f53e, in a detached worktree: the harness prints 42 `KILLED` rows (S01 to S38, S04U, W1 to W3), `RESULT survivors=0`, exit 0, and `cloud_relay.sh --self-test` prints `81 checks, 0 failed`. Main's `cloud_relay.sh` has no `HELD`, so a listed PR is updated on every pass.
- A well-formed hold file owes no refusal: `a well-formed hold file owes no refusal (null control)` reads `<log>.level` and passes at the head. So the reds under `cloud_relay-6` and `-10` come from the mutated line.
- The tick probe has its own control: the same driver at 47a40f71f (log line) and at 929ee1607 (level line) differ only in that one production line.
- Each mutant's harness row runs the unmutated step first (NOT RUN otherwise).
- Round 2 and 3 in-head controls are kept: a #99 hold leaves #41 updating; #141 does not hold #41; empty, comment-only and missing files hold nothing; a newline-terminated `99\n41\n` holds #41.

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test | tail -1`: `189 checks, 0 failed` at the head, and `81 checks, 0 failed` at origin/main 5a755f53e. The rule is the script's own check count, which CI requires to be nonzero with 0 failed (`governance.yml` instrument-self-tests). The previous handoff's 163 was taken against an older main.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`, with no names so every mutant runs: 53 `KILLED` and `RESULT survivors=0`, exit 0, at the head. 42 `KILLED`, survivors 0, exit 0 at origin/main. The instrument is the harness. Its scope is every mutant it defines, M0, S04U and the W rows included. The count is `grep -c KILLED` over its output.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` with an empty `scope.run`. Key on the mode line. `PREPR_SKIP_CLOSURES=1`.
- Run at the head: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. With `/opt/hpo/venv-ci/bin/python` and `PYTHONPATH=tests/hastub`: `tests/entities.py` ends `ALL 2382 ENTITY CHECKS PASSED`, `tests/harness_headers.py` `ALL 109 HARNESS HEADER CHECKS PASSED` and `tests/layout.py` `layout self-test: ok`. `python3 -I tools/audit/seat/tmp_paths.py --check` prints `0 refused`. `python3 tests/throwaway_git.py --check` prints `0 raw git init or clone site(s) refused`. `python3 tools/audit/seat/selftest_wiring.py --check` prints `72 self-testing, 72 wired, 0 unwired`.
- `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json tests/golden` prints nothing (0 lines). That diff would list any of those files this branch touched.
- `git merge-tree --write-tree origin/main 929ee160731596b654d2c69afa1e278d5ca7ec40` exits 0 at origin/main 5a755f53e. At bc313e7c it named the two conflicts above.
- Class seams (step 8), for the semantic conflict. The seam is "a cloud_relay.sh writer of a log `OWED` line the tick would skip as naming no PR". The instrument is `grep -n 'logline OWED\|owed "\|>> "$(relay_log)"' tools/audit/seat/cloud_relay.sh` at the head. It returns `owed()` (PR first), `handoff-update $pr`, `approve-held-runs $pr`, two `dispatch $pr` lines and `OWED reviewer-fire <pr>`. Each has the PR in fields 2 to 4, where `relay_owed` looks for it, so each is already guarded. The former `handoff-hold-malformed` log line was the only one without a PR, and it is closed in this diff. The hold-file reader seams of round 3 (`grep -rn "cloud-handoff-hold\|hold_list" tools/ .github/ dev/`) are unchanged: `cloud_relay.sh`, `INSTRUMENTS.md` (its refusal sentence now names `<log>.level`) and the harness's `cloud_relay-2`, `-6`, `-10` and `-11` patterns.

## Red checks

At this head none is known: it has not run CI, because the code is a handoff ref, not yet the PR head. nightly-status grades main, not this head, so this diff neither caused it nor can clear it. Main's ci-ratchet red is runner-speed variance owned by R10-CI-LAYOUT. This diff touches no ratchet input (`tests/structure.py` passes at the head, and the gate scope above runs no script), so no cheaper detector here would have caught it. Carry: R10-CI-LAYOUT

## Forward-carry

- R10-ORCH-MACHINERY (issue #2505): its `handoff` job must read `<state>/cloud-handoff-hold` through `cloud_relay.sh held <pr>` (rc 0 held, 1 not held, 2 malformed, which refuses the job's pass), never re-parse it. Control: put the PR in the hold file with its handoff ahead; the job must not update it. Null control: the same pass with the line removed updates it. This seat writes only its return refs, so the orchestrator lands the line on that group's `carry` with `roster_edit.py`. Carry: R10-ORCH-MACHINERY
- R10-FLOW-ROSTER-FREEZE, which writes the hold automatically while a reviewer is live: it must write only valid lines, because a malformed file refuses the whole handoff pass and is owed in `<log>.level` until fixed. Carry: dismissed: group not yet registered on any roster; the orchestrator carries the hold-file grammar onto its brief when it registers (its pack brief already lists this group in `after`).

## Friction

none

## Notes

Not a stated design choice: `cloud_relay-7`'s malformed-file CLI check cannot kill that mutant, because usage exits 2 too. The rc 0 and rc 1 CLI arms are what kill it.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01N3YggrcPUPeCRB4jMLrbBN

