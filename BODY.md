Part of #201.

Group: R10-FLOW-RELAY-HOLD (registration pending: roster PR-B)

Pack file: dev/programme/flow-study/roster/groups/R10-FLOW-RELAY-HOLD.json at PACK_SHA f89bfb4e on branch claude/dazzling-gauss-7l3u2b.

`cloud_relay.sh`'s handoff arm updated every open PR whose `handoff/<topic>` tip was ahead of its head, with no way to exclude one. The roster PR's topic is `audit-r10-roster`, the branch every `roster_edit.py` push (forward-carries included) lands on, so a freeze had to stop all roster pushes (K13a). This adds the hold the study specifies:

- `<state>/cloud-handoff-hold` lists PR numbers, one per line (blank and `#` lines allowed). Only the orchestrator writes it. A final line without a trailing newline is read like any other.
- A listed PR whose handoff is ahead is not updated; the pass prints `cloud_relay: HELD #<pr> <handoff tip>` once. Removing the number resumes it.
- A missing or empty file holds nothing. Any line that is not a plain PR number (or a file that is not a readable regular file) refuses the whole handoff arm for that pass: rc 2, `refused: malformed hold file`, `OWED handoff-hold-malformed <file>` in the log. It never holds all and never holds none.
- `cloud_relay.sh held <pr>` (rc 0 held, 1 not held, 2 malformed) reads the same file through the same parser, so R10-ORCH-MACHINERY's `handoff` job can honour it unchanged: same path, same grammar, same refusal.

Design choices a later seat should not read as bugs, each now pinned by a check and a mutant: the hold is checked after the "handoff already contained in the PR head" test (a held PR with nothing to apply prints nothing; `cloud_relay-9`) and before the failed-update ledger (a hold outranks a recorded failure; `cloud_relay-8`); a refusal stops the handoff arm only, the probe arm of `pass` still runs; the grammar is strict (no leading zeros, no trailing text) because a lenient parse is how "hold nothing" happens silently.

Round 3 answers the review of a8a2778e: R6 (the unterminated-last-line check held #41 on line 1, so dropping `|| [ -n "$l" ]` survived), R3 (no check read the `OWED handoff-hold-malformed` log line) and R4 (the self-test called `held()` but never the `held` CLI arm). Each now has a check that goes red when its production line is removed. The review's notes R12 and R13 (the two orderings above) are pinned too. The hold mutants take per-file ids, `cloud_relay-1` to `cloud_relay-9`, never a new S number (the pack's P6 convention, in this group's own brief): the four formerly numbered S35 to S38 are `cloud_relay-1` to `cloud_relay-4`, and the harness docstring is back to main's `S01..S34` plus one sentence stating the convention.

Code-owned: no. None of `tools/audit/seat/cloud_relay.sh`, `tools/audit/seat/INSTRUMENTS.md` or `dev/audit/harnesses/r10_seat_selftests_mutants.py` matches a `.github/CODEOWNERS` pattern (`grep -n "cloud_relay\|tools/audit/seat\|r10_seat" .github/CODEOWNERS` prints nothing).

## Head

ce4d120851c5b8cf16ce515f46f549ef60de676c, which merges origin/main f2fb1b0e950ecd047b7f08b3adef93776a622540 into the previous handoff 0ddbc0c21 (a merge, never a rebase; it merged with no conflict) and adds two commits on top. Every figure below was re-taken at this head (measured 2026-10-21T17:27Z).

## Mutation proof

Failing test first: the five new mutants were planted in the previous handoff's `cloud_relay.sh` (0ddbc0c21) and its unchanged self-test was run. All five survived, each `137 checks, 0 failed`. At this head every hold mutant, run directly on `cloud_relay.sh --self-test` (163 checks unmutated), goes red. `cloud_relay-1` (inverted hold) crashes on the absent stub output after 25 distinct failing checks. `cloud_relay-2` (malformed read as hold-none) gives 27 failed, `cloud_relay-3` (grammar accepts non-digits) 42 failed and `cloud_relay-4` (substring match) 2 failed, among them `a held #141 does not hold #41 (whole-line match)`. The new ones:

- `cloud_relay-5`, unterminated last line dropped (`while IFS= read -r l; do`): `163 checks, 3 failed`. Failing: `a last line without a newline is read: it holds #41`, `and held says held for it`, `a one-line file without a newline holds #41`.
- `cloud_relay-6`, refusal log line deleted (`held_prs=$(hold_list) || { return 2; }`): 9 failed, one `and logs OWED handoff-hold-malformed` for each of the nine malformed variants.
- `cloud_relay-7`, CLI dispatcher line `held) shift; held "$@"; exit $?;;` deleted: 2 failed: `the CLI 'cloud_relay.sh held' says held (rc 0)` and `... says not held (rc 1)`. The malformed-file CLI check still passes under this mutant, because usage also exits 2. That is why the rc 0 and rc 1 arms carry the kill.
- `cloud_relay-8`, failed ledger before the hold: 1 failed: `a hold outranks a recorded failed update: still HELD`.
- `cloud_relay-9`, hold before the contained test: 1 failed: `a held PR whose handoff is already in its head prints no HELD (nothing to hold)`.

Through the finder's harness at this head (`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`, every mutant): M0 prints `0 seat step(s) red`. All 47 mutant rows are `KILLED`: S01 to S34, S04U, W1 to W3 and `cloud_relay-1` to `cloud_relay-9`. It ends `RESULT survivors=0` with exit 0

## Null control

- The unmodified tree at `origin/main` f2fb1b0e950ecd047b7f08b3adef93776a622540: the harness prints 38 `KILLED` rows (S01 to S34, S04U, W1 to W3), `RESULT survivors=0` and exit 0. Main's `cloud_relay.sh` contains no `HELD`, so a listed PR is updated on every pass.
- Unterminated last line: `printf '99\n41\n'`, the same file with a trailing newline, holds #41 at this head. It also holds #41 under `cloud_relay-5`, so the red belongs to the missing newline alone.
- Refusal log: a well-formed hold file logs no `handoff-hold-malformed`. That check passes, so the nine reds under `cloud_relay-6` come from the deleted line.
- Each mutant's harness row runs the unmutated step first (NOT RUN otherwise).
- In-head controls kept from round 2: a #99 hold leaves #41 updating; #141 does not hold #41; empty, comment-only and missing files hold nothing; nine malformed variants refuse with rc 2.

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test | tail -1`: `163 checks, 0 failed` at the head. The rule is the script's own check count, which CI requires to be nonzero with 0 failed (`governance.yml` instrument-self-tests). The previous handoff 0ddbc0c21 reads `137 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`, with no names so every mutant runs: M0 prints `0 seat step(s) red`. All 47 mutant rows are `KILLED`: S01 to S34, S04U, W1 to W3 and `cloud_relay-1` to `cloud_relay-9`. It ends `RESULT survivors=0` with exit 0 at the head, and 38 `KILLED` rows (S01 to S34, S04U, W1 to W3), `RESULT survivors=0` and exit 0 at origin/main. The instrument is the harness. Its scope is every mutant it defines, M0, the W rows and S04U included.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. Key on the mode line. The three changed files are in no measured closure. `PREPR_SKIP_CLOSURES=1`.
- Run at the head: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. With `/opt/hpo/venv-ci/bin/python` and `PYTHONPATH=tests/hastub`: `python3 tests/entities.py` ends `ALL 2381 ENTITY CHECKS PASSED`, `python3 tests/harness_headers.py` ends `ALL 109 HARNESS HEADER CHECKS PASSED` and `python3 tests/layout.py` ends `layout self-test: ok`. `python3 -I tools/audit/seat/tmp_paths.py --check` prints `0 refused`. `python3 tests/throwaway_git.py --check` prints `0 raw git init or clone site(s) refused`. `python3 tools/audit/seat/selftest_wiring.py --check` prints `0 unwired`. `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json tests/golden` prints nothing. That diff would list any of those files this branch touched.
- `git merge-tree --write-tree origin/main ce4d120851c5b8cf16ce515f46f549ef60de676c` exits 0 at origin/main f2fb1b0e950ecd047b7f08b3adef93776a622540.
- `git grep -n 'S3[5-9]' -- dev/audit/harnesses/r10_seat_selftests_mutants.py tools/audit/seat/` prints nothing, so no stale S35 to S38 reference remains.
- Class seams (step 8). The seam is "a reader of the hold file". The instrument is `grep -rn "cloud-handoff-hold\|hold_list" tools/ .github/ dev/`. It returns `cloud_relay.sh` (`hold_list`, `held`, `handoff_arm`, its self-test), the `INSTRUMENTS.md` paragraph and the harness's `cloud_relay-2` and `cloud_relay-6` patterns. Every seam it returns is closed in this diff. The only other automatic `update_pr.sh` driver is `tick_loop.sh`, which runs it through `cloud_relay.sh pass` and so inherits the hold. R10-ORCH-MACHINERY's `handoff` job does not exist yet, so it is a carry (below), not a seam.

## Red checks

nightly-status grades main, not this head, so this diff neither caused it nor can clear it.

## Forward-carry

- R10-ORCH-MACHINERY (issue #2505, a live group on `dev/programme/rosters/wave-r10-groups.json` at origin/handoff/audit-r10-roster): its `handoff` job must read `<state>/cloud-handoff-hold` through `cloud_relay.sh held <pr>` (rc 0 held, 1 not held, 2 malformed, which refuses the job's pass), never re-parse it. Control: put the PR in the hold file with its handoff ahead; the job must not update it. Null control: the same pass with the line removed updates it. This seat writes only its return refs, so it cannot write the roster branch. The orchestrator lands the line on that group's `carry` with `roster_edit.py`. Carry: R10-ORCH-MACHINERY
- R10-FLOW-ROSTER-FREEZE (not yet on the roster; it registers with roster PR-B): it writes the hold automatically while a reviewer is live, and must write only valid lines, because a malformed file refuses the whole handoff pass. Carry: dismissed: R10-FLOW-ROSTER-FREEZE is on no roster yet (`carry_audit.py` at origin/handoff/audit-r10-roster names it no group), so no destination resolves. Its pack brief (the group's JSON in the flow-study pack, branch claude/dazzling-gauss-7l3u2b) already lists this group in `after` and `tools/audit/seat/cloud_relay.sh` in its files. The orchestrator carries the hold-file grammar onto the brief when the group registers.

## Friction

none

## Notes

Not a stated design choice: `cloud_relay-7`'s malformed-file CLI check cannot kill that mutant, because usage exits 2 too. The rc 0 and rc 1 CLI arms are what kill it.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01ARdbaacBecT76SD4n2goBx
