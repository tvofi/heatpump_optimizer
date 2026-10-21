Part of #201.

Group: R10-FLOW-RELAY-HOLD (registration pending: roster PR-B)

Pack file: dev/programme/flow-study/roster/groups/R10-FLOW-RELAY-HOLD.json at PACK_SHA f89bfb4e on branch claude/dazzling-gauss-7l3u2b.

`cloud_relay.sh`'s handoff arm updated every open PR whose `handoff/<topic>` tip was ahead of its head, with no way to exclude one. The roster PR's topic is `audit-r10-roster`, the branch every `roster_edit.py` push (forward-carries included) lands on, so a freeze had to stop all roster pushes (K13a). This adds the hold the study specifies:

- `<state>/cloud-handoff-hold` lists PR numbers, one per line (blank and `#` lines allowed). Only the orchestrator writes it.
- A listed PR whose handoff is ahead is not updated; the pass prints `cloud_relay: HELD #<pr> <handoff tip>` once. Removing the number resumes it.
- A missing or empty file holds nothing. Any line that is not a plain PR number (or a file that is not a readable regular file) refuses the whole handoff arm for that pass: rc 2, `refused: malformed hold file`, `OWED handoff-hold-malformed` in the log. It never holds all and never holds none.
- `cloud_relay.sh held <pr>` (rc 0 held, 1 not held, 2 malformed) reads the same file through the same parser, so R10-ORCH-MACHINERY's `handoff` job can honour it unchanged: same path, same grammar, same refusal.

Design choices a later seat should not read as bugs: the hold is checked after the "handoff already contained in the PR head" test (a held PR with nothing to apply prints nothing) and before the failed-update ledger (a hold outranks a recorded failure); a refusal stops the handoff arm only, the probe arm of `pass` still runs; the grammar is strict (no leading zeros, no trailing text) because a lenient parse is how "hold nothing" happens silently.

Code-owned: no. None of `tools/audit/seat/cloud_relay.sh`, `tools/audit/seat/INSTRUMENTS.md` or `dev/audit/harnesses/r10_seat_selftests_mutants.py` matches a `.github/CODEOWNERS` pattern (`grep -n "cloud_relay\|tools/audit/seat\|r10_seat" .github/CODEOWNERS` prints nothing).

## Head

0ddbc0c21b19f2a9e95b5d8c4ea810a3ab5eea0d, a merge of origin/main 49c222280d4650f4c608385cb95856e1a937a5b2 into the first handoff cfa89d24f (never a rebase); every figure below re-taken at this head (measured 2026-10-21T16:47Z).

The merge's one conflict: both sides added mutants S31 to S34 to `dev/audit/harnesses/r10_seat_selftests_mutants.py`. Main's (`tick_loop.sh`, ab41f4a0f) are kept byte for byte; this branch's `cloud_relay.sh` hold mutants are renumbered S35 to S38, and the docstring range reads S01..S38. `git grep -n 'S3[5-9]' -- dev/audit/harnesses/r10_seat_selftests_mutants.py tools/audit/seat/INSTRUMENTS.md tools/audit/seat/cloud_relay.sh .github/workflows/governance.yml` returns the docstring line and the four MUTANTS rows only; had another reference carried the old numbers, it would have been listed.

## Mutation proof

The new self-test checks were written first and failed against the unchanged arm (with the hold's production lines absent the self-test reads `134 checks, 31 failed`: no HELD line, no refusal). Mutants for each arm, planted in production lines outside the self-test function, run by the harness (`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py S35 S36 S37 S38`), each reddens the `cloud_relay.sh --self-test` step:

- S35 hold predicate inverted (`if ! grep -qxF "$pr" <<< "$held_prs"`): KILLED (the held PR is updated, then the stub path is absent).
- S36 malformed file read as hold-none (`hold_list || true`): KILLED, 18 checks fail.
- S37 grammar accepts a non-digit line: KILLED, 28 checks fail.
- S38 whole-line match dropped (`grep -qF`; #141 would hold #41): KILLED, 2 checks fail.
- Deleting every hold line from the arm at once (`grep -v 'held_prs=$(hold_list)\|HELD #'`): self-test `134 checks, 31 failed` (the grep also drops the three self-test checks that name `HELD #`, hence 134, not 137).

`RESULT survivors=0`.

## Null control

The unmodified tree (`origin/main` 49c222280): the self-test reports `74 checks, 0 failed` and `grep -c HELD` of its `cloud_relay.sh` is 0, so a listed PR is updated on every pass. In the new self-test the controls are: a hold listing another PR (#99) updates #41 as today and prints no HELD; `#141` does not hold #41; an empty file, a comment-only file and no file hold nothing; a held PR whose handoff tip moved is not updated and names the moved tip; removing the number resumes the update. Nine malformed variants (`41 99`, `abc`, `41x`, `0`, `-1`, `041`, `41,99`, ` 41`, `41 # c`) each refuse with rc 2, update nothing and print no HELD.

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test | tail -1`: `137 checks, 0 failed` at the head above (74 at the merge base; the rule is the script's own check count, which CI requires to be nonzero with 0 failed, `governance.yml` instrument-self-tests).
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` (every mutant, no names): M0 `0 seat step(s) red`, each S, W and S04U line `KILLED`, `RESULT survivors=0`, exit 0; main's S31 to S34 on `tick_loop.sh` are among them, killed at this head. Instrument is the harness; scope is every mutant it defines.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run` (key on the mode line); the diff touches three files, none in a measured closure. `PREPR_SKIP_CLOSURES=1`.
- Structure ratchet: `python3 tests/structure.py` ends `STRUCTURE RATCHET PASSED` at this diff (the diff adds no Python and no coordinator method).
- Run at this diff with `/opt/hpo/venv-ci/bin/python`, `PYTHONPATH=tests/hastub`: `python3 tests/entities.py` ends `ALL 2375 ENTITY CHECKS PASSED`; `python3 tests/harness_headers.py` ends `ALL 109 HARNESS HEADER CHECKS PASSED`; `python3 tests/layout.py` ends `layout self-test: ok`; `python3 -I tools/audit/seat/tmp_paths.py --check` prints `0 refused`.
- `git merge-tree --write-tree origin/main 0ddbc0c21` exits 0 (no conflict) at origin/main 49c222280.
- Class seams (step 8): the seam is "a reader of the hold file". Instrument: `grep -rn "cloud-handoff-hold\|hold_list" tools/ .github/ dev/`, which returns `cloud_relay.sh` (`hold_list`, `held`, `handoff_arm`, its self-test), the `INSTRUMENTS.md` paragraph and the mutant harness's S36 pattern; the beat's `handoff` job (R10-ORCH-MACHINERY) does not exist yet, so it is a carry, not a seam.

## Red checks

nightly-status (grades main): it grades main, not this head, so this diff neither caused nor can clear it.

## Forward-carry

n/a: the receiving group R10-FLOW-ROSTER-FREEZE registers with roster PR-B, so the orchestrator carries the finding there (see Notes).

## Friction

none

## Notes

Finding for the receiving group R10-FLOW-ROSTER-FREEZE (not yet on the roster): it writes the hold automatically while a reviewer is live, and must write only valid lines, since a malformed file refuses the whole handoff pass. Separately, R10-ORCH-MACHINERY's `handoff` job must read `<state>/cloud-handoff-hold` through `cloud_relay.sh held <pr>` (or the same grammar and refusal) rather than re-parse it.
