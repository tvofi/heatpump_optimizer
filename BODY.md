R10-FLOW-ROSTER-FREEZE, arm (b) only (triage `dev/programme/triage/s6-batch19.md#P89`, on `triage/s6-batch19`). Arm (a), the relay freeze, is out of scope and follows in its own PR.

Cause: `tools/audit/carry_audit.py`'s `Dests.check` returned "is not a group of the roster" for any group absent from the one roster it loaded, and `pr-contract.yml` runs `carry_audit.py check --body` with no `--roster-ref`, so it read only the tree's roster. `finding-propagation.md` (Enforcement) counts a carry to the round's roster as in the tree once it is on `handoff/audit-r<N>-roster`. The check was stricter than the rule, which refused the R10-GATE-DEFER opener twice (`R10-RCA-CODESCAN-WAIT is not a group of the roster`).

Change:
- `Dests` takes an optional `round_roster=(ref, roster)`. A group open on the tree's roster passes as before. A group open only on the round ref passes with the note `<group> resolved on <ref>`. A group on neither ref fails, and so does a group that is done wherever it appears.
- `load_dests`, when no `--roster-ref` is given, reads `roster_lib.round_ref` and loads that roster if this clone has the ref. A clone without the ref reads only the tree's roster, which can only narrow what passes. An explicit `--roster-ref` keeps its old single-ref meaning.
- `report` prints every destination note (before, only UNVERIFIED ones), so the resolving ref is shown.
- `pr-contract.yml`'s carry step fetches `refs/heads/handoff/audit-r*-roster` before the check. `roster_lib.py` is restored from the base, and this uses only `round_ref` and `git_in`, which the base already has.

Alternatives considered: passing `--roster-ref <round>` in the workflow would swap main's roster for the branch's, which drops a group that only main holds. A fixer PR that edits the roster directly is that case. Loading both rosters keeps main's answer and adds the branch's. Arm (a) (the opener queues a roster PR itself) was rejected at triage: it still costs one train cycle per carry.

## Head

`24b4399cfb3cb7ddb46c315c1ddfb0ec21f05343`, cut from `origin/main` at `eceef457a8e6d9b77494f459f4d464f56cbbb231` (which contains the dispatched base `93931ab2b275`). Round ref `origin/handoff/audit-r10-roster` at `d4d3f5a19a69` when measured.

## Mutation proof

Each mutant is applied to `tools/audit/carry_audit.py` with `sed`, and then `python3 -I tools/audit/carry_audit.py --self-test` is run. The file is restored from a copy after each one.
- M1, which drops the round-ref load in `load_dests` (`round_roster = (rref, ...)` becomes `pass`): `FAIL load_dests reads the round ref: a group only there passes, the note naming it`, then `196 checks, 1 failed`. This is the mutant the brief requires, and the first control kills it.
- M2, where `Dests` ignores `round_roster` (`if round_roster` becomes `if False`): `FAIL a group only on the round's roster ref is a destination, and the note names that ref` and `FAIL load_dests reads the round ref ...`, then `196 checks, 2 failed`.
- M3, where a done group on the round ref passes (`is_open(r)` is dropped): `FAIL a group done on main and on the round ref is a bad destination` and `FAIL a group done on the round ref alone is a bad destination`, then `196 checks, 2 failed`.

Failing test first: the new self-test rows ran against the unfixed `Dests` and stopped at `TypeError: Dests.__init__() got an unexpected keyword argument 'round_roster'`.

## Null control

- At the merge base `eceef457a8e6`, the finder's harness is a body whose `## Friction` item says `Carry: R10-RCA-CODESCAN-WAIT`, a group that is open on `origin/handoff/audit-r10-roster` and absent from main's roster. `python3 -I tools/audit/carry_audit.py check --body <it>` prints `BAD-DEST body item 107e3d85: R10-RCA-CODESCAN-WAIT: R10-RCA-CODESCAN-WAIT is not a group of the roster` and exits with rc=1. At the head, the same command prints `NOTE body item 107e3d85: R10-RCA-CODESCAN-WAIT: R10-RCA-CODESCAN-WAIT resolved on origin/handoff/audit-r10-roster` and `1 routed, 0 unrouted, 0 bad destination(s)`, with rc=0.
- A group on neither ref (`Carry: R10-NOWHERE-ZZ`) is refused at both ends: base rc=1 (`is not a group of the roster`), head rc=1 (`is not a group of the roster or of origin/handoff/audit-r10-roster`).
- A done group (`Carry: R10-FEEDS`, stage done) is refused at both ends: base rc=1 and head rc=1 (`R10-FEEDS is done (resume.stage done)`).
- Self-test nulls: the same round-only group without the round ref is bad (`... and without the round ref it is not`), and a scratch clone with the round ref deleted refuses it (`... and a clone without that ref refuses it`).

## Figures

- `python3 -I tools/audit/carry_audit.py --self-test`: `carry_audit self-test: 196 checks, 0 failed` at head, against `189 checks, 0 failed` at the merge base. The 7 new rows are the round-ref controls listed above.
- Which groups the harness can use: open on `origin/handoff/audit-r10-roster` and absent from `origin/main`'s roster, read with `roster_lib.groups_of`/`is_open` over `show_roster` at both refs. It returned six groups, `R10-RCA-CODESCAN-WAIT` among them. The figure is a function of both refs' tips at the head stated above.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out` and listed `tests/entities.py` and `tests/harness_headers.py`. Both were run with `PYTHONPATH=tests/hastub`, along with `tests/structure.py`; results are in Red checks.
- Scoped scripts at the head, run with `PYTHONPATH=tests/hastub`:
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `tests/entities.py`: `2 of 2425 ENTITY CHECKS FAILED`. The two are `gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step is red only when ...`. The same command at the merge base `eceef457a8e6`, in a detached worktree, printed the same two failures and `2 of 2425 ENTITY CHECKS FAILED`. Both are therefore in this seat's environment before the diff, not caused by it. Neither check reads `carry_audit.py` or `pr-contract.yml`, and CI decides them.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against eceef457a8e6`.
- The glob refspec in the workflow was checked in a fresh clone: `git fetch --no-tags origin '+refs/heads/handoff/audit-r*-roster:refs/remotes/origin/handoff/audit-r*-roster'` created `refs/remotes/origin/handoff/audit-r10-roster`.
- Class seams: `grep -rn "is not a group of the roster" tools/ .claude/ tests/` returned two sites:
  - `tools/audit/carry_audit.py` `Dests.check`, which is closed in this diff.
  - `tools/audit/seat/cloud_dispatch.py` `dispatch_group`, which is already guarded. It reads the roster at `roster_lib.reader_ref`, which defaults to the round's roster branch.
  `roster_drift` (the sweep's `ROSTER-DRIFT`) still reports a carry on the round ref that main lacks.

## Red checks

none

## Forward-carry

none

## Friction

none
