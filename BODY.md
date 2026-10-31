R10-FLY-BEAT-FETCH-RACE (size S). The detached `state_docs.py beat --apply` died three times on `roster_edit.Refuse` from `fetch_origin` ("cannot lock ref refs/remotes/origin/...: is at X but expected Y": another process sharing the repository moved a remote-tracking ref between the fetch's read and its write). The same race refused a roster op. Two defects, one seam:

1. `fetch_origin` (tools/audit/seat/roster_edit.py) treated that transient race as fatal. It now retries, at most `FETCH_ATTEMPTS`=4 attempts with 0.25/0.5/1.0 s sleeps, and only when git failed and every line it printed is exactly the lock-race line. Any other failure refuses at once; a race past the bound refuses with git's message. Chosen over a loop-survives-a-pass fix because every caller (beat, roster_sync, every roster op) shares this function, and a retry costs milliseconds where a skipped pass costs an interval.
2. The beat's loop did not survive a refusal even where it was meant to: `roster_sync.main` catches `roster_sync.Refuse`, but `fetch_origin` raises `roster_edit.Refuse`, a different class, which escaped as a traceback (the three tracebacks in the beat log). `roster_sync.main` now converts it, so a race outlasting the bound is a refused pass (rc 2), retried at the next interval.

Folded in, same file family: P315 / #3020 (triage batch 78). `roster_queue.py run_queue`: a deleted `--lint-clone` raised FileNotFoundError before any report line was written, so callers read the previous op's line as this op's result (12 roster ops falsely marked done on 2026-10-30/31). Now every op attempted writes exactly one report line; an exception becomes `roster: <op> <group> FAILED <ExceptionType>: <message>` and the run stops rc 1; a missing `--lint-clone` (or `--edit-checkout`) is refused by name before the first op, rc 2, with a report line. No re-clone (rejected in P315). Overlap only: P300's `--mark` (R10-ORCH-ROSTER-SCHEMA) touches `run_queue` too; the per-op body is now `_run_op`, the seams are distinct, and whichever lands second merges main.

Carry: R10-FLY-BEAT-FETCH-RACE

## Head

b7ac768450038eac0afb83ac841187bd8b408e1a

## Mutation proof

Each mutant applied to the committed head, the named self-test run, then restored (cmp against a backup); every mutant red:
- `FETCH_ATTEMPTS = 1`: `roster_edit.py --self-test` 2 failed ("fetch_origin: one lock race is retried and succeeds", "several raced refs in one fetch are one race"); `state_docs.py --self-test` fails "sync arm 4: the beat outlives one injected lock race" and "sync arm 4: the race was retried once, not skipped".
- race predicate `return rc != 0 and bool(lines) and all(...)` -> `return rc != 0`: `roster_edit.py --self-test` 2 failed ("a non-race failure refuses at once, unretried", "a race line beside another failure is not a race").
- `roster_sync.py` conversion `raise Refuse(str(e))` -> `raise`: `state_docs.py --self-test` fails "sync arm 4: a persistent race is a refused pass (rc 2), no crash" (got: raised Refuse).
- `roster_queue.py` `except Exception` -> `except ZeroDivisionError`: the self-test dies with the injected FileNotFoundError (no FAILED line).
- `roster_queue.py` clone guard `if not Path(d).is_dir()` -> `if False`: "a missing --lint-clone is refused by name, rc 2, before any op" fails.

## Null control

At the merge base the beat has no retry and no conversion: the same injected single race ends the beat with an uncaught `roster_edit.Refuse` (the sync arm 4 mutants above reproduce exactly that), and a run with a deleted lint clone writes no report line. Null controls in the self-tests: a clean fetch is one attempt with no sleep; a clean `roster_queue` queue writes `roster: set-stage <g> pushed <sha9>` for each op; a non-race failure is never retried.

## Figures

- Collision rate, rule: lines starting `roster_edit.Refuse:` containing `cannot lock ref` over lines starting `roster_sync: pull requests` (one per pass) in the beat log; at 2026-10-31 00:4xZ 11 over 1154 (about 0.95 per cent per pass; the log grows, so re-take it). Command: `grep -c "^roster_edit.Refuse: .*cannot lock ref" /Users/timmalmstrom/hpo-orch/r10s6/state-beat.log` and `grep -c "^roster_sync: pull requests" /Users/timmalmstrom/hpo-orch/r10s6/state-beat.log`. Null control: the same grep for a string absent from the log prints 0. One further `roster_edit.Refuse` line in the log is not a lock race and is not counted. At that rate and independent attempts, four attempts leave about 1e-8 per pass; the first sleep already exceeds the millisecond window of a race. Independence is an assumption; the bound caps the damage to a refused pass (item 2) if it fails.
- `python3 tools/audit/seat/roster_edit.py --self-test` -> 131 checks, 0 failed.
- `python3 tools/audit/seat/state_docs.py --self-test` -> all checks passed.
- `python3 -I tools/audit/seat/roster_queue.py --self-test` -> 17 checks, 0 failed.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> MODE: SCOPED, 1 script (tests/entities.py). Local run caveat: it ran to its heartbeat block (tests/entities.py line ~18393, `_hb_stdlib_reads`) and died there on macOS `PermissionError: Cannot get task port for PID` (no system-task-ports entitlement), a stall-sampler environment limit that touches none of the four changed files; no check before it named them. The Linux CI gate is the authority for the rest.
- `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED.
- Seams enumerated, `grep -rn "fetch_origin" tools`: roster_edit.py (the definition and its two callers), roster_sync.py (converted here). All share the fixed function.

## Red checks

none

## Forward-carry

none

## Friction

none

## Unpinned sites

none: `tools/pr/prepr.sh` step 6d reports "the diff adds no unpinned mutation site" (the four changed files are `tools/audit/seat/` scripts outside the mutation lane); the mutants in `## Mutation proof` were run by hand against the in-script self-tests.
