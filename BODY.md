R10-FLOW-ROSTER-FREEZE, arm (b) only (triage `dev/programme/triage/s6-batch19.md#P89`, on `triage/s6-batch19`). Arm (a), the relay freeze, is out of scope and follows in its own PR.

Cause: `tools/audit/carry_audit.py`'s `Dests.check` returned "is not a group of the roster" for any group absent from the one roster it loaded, and `pr-contract.yml` runs `carry_audit.py check --body` with no `--roster-ref`, so it read only the tree's roster. `finding-propagation.md` (Enforcement) counts a carry to the round's roster as in the tree once it is on `handoff/audit-r<N>-roster`. The check was stricter than the rule, which refused the R10-GATE-DEFER opener twice (`R10-RCA-CODESCAN-WAIT is not a group of the roster`).

Change:
- `Dests` takes an optional `round_roster=(ref, roster)`. A group open on the tree's roster passes as before. A group open only on the round ref passes with the note `<group> resolved on <ref>`. A group on neither ref fails, and so does a group that is done wherever it appears.
- `load_dests`, when no `--roster-ref` is given, reads `roster_lib.round_ref` and loads that roster if this clone has the ref. A clone without the ref reads only the tree's roster, which can only narrow what passes. An explicit `--roster-ref` keeps its old single-ref meaning.
- `report` prints every destination note (before, only UNVERIFIED ones), so the resolving ref is shown.
- `pr-contract.yml`'s carry step fetches `refs/heads/handoff/audit-r*-roster` before the check. `roster_lib.py` is restored from the base, and this uses only `round_ref` and `git_in`, which the base already has.

- The self-test's scratch clone for `load_dests` is built with `tests/throwaway_git.py`'s `throwaway_git_init`, imported inside `_self_test` only (as `tools/pr/merge_main_bot.py` does), with its git calls under the returned env; the round-1 head's raw `git("init", "-q")` was refused by prepr's throwaway-git arm.

Alternatives considered: passing `--roster-ref <round>` in the workflow would swap main's roster for the branch's, which drops a group that only main holds. A fixer PR that edits the roster directly is that case. Loading both rosters keeps main's answer and adds the branch's. Arm (a) (the opener queues a roster PR itself) was rejected at triage: it still costs one train cycle per carry.

## Head

`3d526a7f3a0e6842b893dca76add3b0f9218dcfd`: the round-1 handoff `24b4399cfb3c`, plus `f8ba958d9` (the throwaway-git repair) and a merge of `origin/main` at `c176ee55de7c658b0b870182c5dd55d0843ad8f7`. Round ref `origin/handoff/audit-r10-roster` at `4937d60fea5c`; figures below measured at 2026-10-24T22:41:32Z.

## Mutation proof

Each mutant is applied to `tools/audit/carry_audit.py` by an exact one-occurrence string replacement, then `python3 -I tools/audit/carry_audit.py --self-test` is run; the file is restored from a copy after each.
- M1, which drops the round-ref load in `load_dests` (`round_roster = (rref, ...)` becomes `pass`): `FAIL load_dests reads the round ref: a group only there passes, the note naming it`, then `196 checks, 1 failed`. This is the brief's required mutant, killed by the throwaway_git-built scratch clone.
- M2, where `Dests` ignores `round_roster` (`if round_roster` becomes `if False`): `FAIL a group only on the round's roster ref is a destination, and the note names that ref` and `FAIL load_dests reads the round ref ...`, then `196 checks, 2 failed`.
- M3, where a done group on the round ref passes (`is_open(r)` dropped): `FAIL a group done on main and on the round ref is a bad destination` and `FAIL a group done on the round ref alone is a bad destination`, then `196 checks, 2 failed`.
- Restored: `196 checks, 0 failed`.

Failing test first (round 1): the new self-test rows ran against the unfixed `Dests` and stopped at `TypeError: Dests.__init__() got an unexpected keyword argument 'round_roster'`.

## Null control

The finder's harness is a body whose `## Friction` item carries `Carry: <group>`, checked with `python3 -I tools/audit/carry_audit.py check --body <it>` in a detached worktree at the merge base and at the head. The round-1 group `R10-RCA-CODESCAN-WAIT` has since reached main's roster, so the harness uses the one group the rule below returns, `R10-FLY-LEDGER-SAMPLE`.
- `Carry: R10-FLY-LEDGER-SAMPLE` (open on the round ref, absent from main): base rc=1, `BAD-DEST ... R10-FLY-LEDGER-SAMPLE is not a group of the roster`; head rc=0, `NOTE ... R10-FLY-LEDGER-SAMPLE resolved on origin/handoff/audit-r10-roster`, `1 routed, 0 unrouted, 0 bad destination(s)`.
- `Carry: R10-NOWHERE-ZZ` (on neither ref): base rc=1; head rc=1, `is not a group of the roster or of origin/handoff/audit-r10-roster`.
- `Carry: R10-FEEDS` (done): base rc=1 and head rc=1, `R10-FEEDS is done (resume.stage done)`.
- Self-test nulls: the same round-only group without the round ref is bad (`... and without the round ref it is not`), and the scratch clone with the round ref deleted refuses it (`... and a clone without that ref refuses it`).

## Figures

- `python3 -I tests/throwaway_git.py --check` at the repair commit: `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`; at `24b4399cfb3c` prepr reported `REFUSE tools/audit/carry_audit.py:684: git("init", "-q")`.
- `python3 -I tools/audit/carry_audit.py --self-test`: `196 checks, 0 failed` at head, against `189 checks, 0 failed` at `origin/main` `c176ee55de7c`. The 7 new rows are the round-ref controls above.
- Which groups the harness can use: open on `origin/handoff/audit-r10-roster` and absent from `origin/main`'s roster, read with `roster_lib.groups_of`/`is_open` over `show_roster` at both refs: `['R10-FLY-LEDGER-SAMPLE']`. A function of both tips as stated in Head.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, naming `tests/entities.py` and `tests/harness_headers.py`; run with `PYTHONPATH=tests/hastub` along with `tests/structure.py` and `tests/layout.py`:
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `tests/layout.py`: `layout self-test: ok`.
  - `tests/entities.py`: `ALL 2425 ENTITY CHECKS PASSED` run as `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`. With this container's `BASH_ENV` (a toolchain profile) left set it printed `2 of 2425 ENTITY CHECKS FAILED` (`gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`), and the same at `origin/main`: that profile resolves `python` to the venv ahead of the checks' stub `python` on PATH (`bash -c 'type python'` with a stub first on PATH printed the venv path, and with `BASH_ENV` unset printed the stub). prepr was run the same way.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against c176ee55de7c`.
- The workflow's glob refspec, checked in a fresh clone in round 1: `git fetch --no-tags origin '+refs/heads/handoff/audit-r*-roster:refs/remotes/origin/handoff/audit-r*-roster'` created `refs/remotes/origin/handoff/audit-r10-roster`.
- Class seams: `grep -rn "is not a group of the roster" tools/ .claude/ tests/` (source files) returned two sites:
  - `tools/audit/carry_audit.py` `Dests.check`: closed in this diff.
  - `tools/audit/seat/cloud_dispatch.py` `dispatch_group`: already guarded; it reads the roster at `roster_lib.reader_ref`, which defaults to the round's roster branch.
  `roster_drift` (the sweep's `ROSTER-DRIFT`) still reports a carry on the round ref that main lacks.

## Red checks

none

## Forward-carry

none

## Friction

none
