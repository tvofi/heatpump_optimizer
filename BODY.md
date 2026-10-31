Triage batch 78 rules the orchestrator s8's slip proposal of 2026-10-31. `tools/audit/seat/roster_queue.py run` raised `FileNotFoundError` on a deleted `--lint-clone` before it wrote any report line. A caller then read the previous op's line as this op's result, and 12 ops were marked `#done (already)` that never landed. It is the next rolling batch under V182, after batch 77. It holds one ruling and one held roster op.

- **P315: ACCEPT narrowed, a carry on R10-FLY-BEAT-FETCH-RACE**, the orchestrator's named host, which adds `roster_queue.py` to its files.
  - `run_queue` writes exactly one report line per op attempted. Any exception becomes `roster: <op> <group> FAILED <ExceptionType>: <message>`, and the run stops nonzero.
  - A missing lint clone is refused by name before the first op, with rc 2.
  - REJECTED: having the runner re-clone. The clone is the caller's to provision, and a re-clone would hide a misconfigured path.
  - Order with P300's `--mark` (R10-ORCH-ROSTER-SCHEMA): distinct seams in the same function. A FAILED line marks `#refused`.
  - The carry is held until the host group is on the roster branch. Its own append-group was one of the 12 ops the slip falsely marked done, and it is re-queued.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`d4ba408d01b596396059d8320abdd7bfe9185974`; the file is the whole diff against `5d4e0bcfb`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P315 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch78.md#P315`: it returns None.
- With `Verdict: ACCEPT narrowed` changed to `Verdict: REJECT narrowed`, the same carry is refused: `dev/programme/triage/s6-batch78.md#P315 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- `git show origin/main:tools/audit/seat/roster_queue.py` at `5d4e0bcfb`: `def run_queue` at line 93, `_git("fetch", "-q", "origin", cwd=a.lint_clone)` at line 123, and `_git` at lines 45-46 a bare `subprocess.run` with `cwd=`.
- `grep -c 'no report line written'` over the orchestrator's `seat-ledger.md` gives 5 (lines 2765-2769). `grep -c 'refused exception FileNotFoundError'` gives 17.
- `grep -n 'BEAT-FETCH-RACE'` over the orchestrator's roster queue gives line 520 `#done (already) append-group R10-FLY-BEAT-FETCH-RACE` and line 532, its re-queue.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
