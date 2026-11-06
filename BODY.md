Part of #201. Hotfix topic r10-gate-busy-defer: two `gate` jobs at one head each deferred to the other, so neither judged. The cause, re-derived from the finder's logs (#3241 head 95c7e604, attempt 2 of runs 42192623509 and 42193153511): both were edit runs whose prelude had left `pr-contract` to a code run (C3), so each listed `pr-contract` skipped under the caller's bare name and never the `pr-contract / pr-contract` its title's workset owes. `prelude.judging` therefore read each as still adding a source, `gate.busy` named it, and `gate.deferring` set the wait bound to 0. Both published `FAIL run(s) [<the other>] ... their gate decides` within 9 s of starting (10:07:46Z to 10:07:55Z, and 10:07:47Z to 10:07:55Z).

The fix, in `tools/ci/gate.py`:
- `busy()` no longer waits on a LATER run whose `gate` job has started (`in_progress` or `completed`). A job starts only after its `needs` (`gate` needs `prelude` and `pr-contract`, which needs every unit), so such a run adds no source. Of two started gates the lower id decides and the higher waits on it, so waits run only downward in id and cannot cycle. An earlier run is still waited on, as before.
- In `judge()`, C3's zero bound now applies only when a code run (or an unreadable title, read as code the way `prelude.waits_on` reads it) is among the waited runs. That is C3's own premise: the code run's gate is the later verdict. A deferring edit gate that waits only on another edit run now waits on it like any other gate instead of publishing a red deferral at once.

Design choice: the tie-break keys on a *started* gate, not a *listed* one. GitHub lists a run's `gate` as `waiting` from the run's start (R3-2), so a listed gate is no proof that the run's units finished. The first commit on this branch keyed on a listed gate, and `r10_ci_gate_core.py sim` went red on it (REV3 arms rc 1, false-green max 108 s against 25 s at the base). Commit a83b95f9 corrected it. That is a disclosed self-correction; the final head reads identical to the reference.

Alternatives that lost:
- Teach `judging()` to read the skipped caller `pr-contract` as finished. A skipped caller is not distinguishable in the listing from one the platform has not expanded yet, and it leaves two concurrent gates both judging with no tie-break.
- The lowest unfinished id judges, the rest defer. A higher run whose gate is merely listed would still be adding sources, which reopens R3-2.

Merge order with #3243 (R10-GATE-LEASE-TOCTOU): that pull request changes only `tests/gate_lock.py` and its delivery row, and this one changes only `tools/ci/gate.py` and `dev/audit/harnesses/r10_ci_gate_core.py`. Neither depends on the other, so either may merge first.

## Head

621d7569692bf2246172edf3729f39ac11382b41, branch `fix/r10-gate-busy-defer`, cut from origin/main dc0a170b671814be196a54b1c71e29449f54d6d7. main had not moved at the `prepr.sh` run, so one run covers this head.

## Mutation proof

Run in-tree by `python3 -I dev/audit/harnesses/r10_ci_gate_core.py mutants` (M17-M20, added here). Each mutant is applied to `tools/ci/gate.py`, then the self-test and the replay run, then the file is restored. Result: 20 mutants, 0 survivors. The self-test cases each mutant turns red:

| mutant | what it reverts | red cases (`gate.py --self-test`) |
|---|---|---|
| M17 busy tie-break deleted | `busy()` back to main's predicate | `busy-defer: of two started gates at one head the lower id defers to none, the higher to the lower`; `busy-defer: the lower deferring edit gate judges at once beside the higher one` |
| M18 busy tie-break id inverted | `>` to `<` | both of the above, plus `busy-defer: the higher deferring edit gate waits on the lower ...` and `R3-2: a run whose gate is listed but an owed job is not still adds a source` |
| M19 tie-break on a listed gate | a started gate to a merely listed one | `busy-defer null (R3-2 EARLY): a later run whose gate is listed `waiting` beside running units is still deferred to` |
| M20 C3 at once beside any run | `judge()`'s code-run condition deleted | `busy-defer: the higher deferring edit gate waits on the lower (an edit run, not C3's code run), then judges, never a red deferral` |

Main's production code, with this branch's tests: the three `busy-defer` cases fail (63 checks, 3 failed). One of them prints the finder's own line: `got ('FAIL run(s) [42193153511] at this head are still being judged; their gate decides', [])`.

## Null control

- `null: no other run at the head, no wait` (existing) stays green: a single run still judges.
- `busy-defer null: a genuinely earlier run still adding sources is still deferred to` (code run 42192623509, units in progress, gate not listed, asked from 42193153511).
- `busy-defer null: a later run whose gate is not listed is still deferred to` and `busy-defer null (R3-2 EARLY): ... gate is listed `waiting` beside running units is still deferred to`.
- `C3: a deferring edit gate beside a busy code run publishes the deferral at once, holding no runner` (existing) stays green: C3's zero bound still applies beside a code run.
- At the merge base, `r10_ci_gate_core.py sim` and `replay` read identical to `1371a0a6:measure/rev/`. At this head both still read identical: the change moves no designed scenario. The race harness `r10_gate_defer_race.py` reads 0 UNDECIDED-RED, 0 MASKED, 0 DEADLOCK and 0 RESIDUAL-RED on every scenario at this head.

## Figures

- Finder's harness: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/127833303340/logs` and `.../jobs/127833295321/logs`. Line 7047 of each is the deferral `FAIL`, naming the other run. The brief's `--allow-escape-sequences` flag is unknown to this environment's `gh` (see Friction). Fetched copies: sha1 a93636b6d3dbbdb65355733c9e126e3438eb4a45 and da0168eade1217f44e56361f5ffc05e6979eb4e8.
- Both runs' jobs at attempt 2: `gh api "repos/tvofi/heatpump_optimizer/actions/runs/<id>/attempts/2/jobs?per_page=100"`. `pr-contract` is listed `completed/skipped` under the bare name, and no `pr-contract / pr-contract` is listed. This is the input `prelude.judging` reads as not judging.
- Self-test: `python3 -I tools/ci/gate.py --self-test`. Green at this head. With main's production code and this branch's cases, 3 cases fail (see Mutation proof).
- Mutants: `python3 -I dev/audit/harnesses/r10_ci_gate_core.py mutants` (its `RESULT` line).
- Designed replays: `python3 -I dev/audit/harnesses/r10_ci_gate_core.py replay` and `... sim` (each prints IDENTICAL or DIFFERS against its reference), at the merge base and at this head.
- Race scenarios: `python3 -I dev/audit/harnesses/r10_gate_defer_race.py`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL` (`tools/ci/gate.py changes the gate itself`). The full suite is CI's to run.
- Ratchets: `python3 tests/structure.py` (STRUCTURE RATCHET PASSED) and `PYTHONPATH=tests/hastub python3 tests/entities.py` (ALL ... ENTITY CHECKS PASSED).
- Seam enumeration (fixer step 8): `git grep -n "judging(\|wait_sources(\|waits_on(" -- tools .github` returns two readers of `judging()`. `gate.busy` is closed in this diff. `prelude.wait_sources` is already guarded: `prelude.waits_on` has a non-code run wait only on an earlier run or a code run, and code runs never call `wait_sources` (`prelude.main` guards it with `kind != "code"`), so its waits are acyclic by id and a deferring edit run it waits on still ends.

## Red checks

none: no check has run on a commit of this branch; no pull request exists yet.

## Forward-carry

none

## Friction

- PROMPT.md: stale: the brief's `gh api --allow-escape-sequences ...` fails with `unknown flag: --allow-escape-sequences` in this cloud seat's `gh`; the logs were read without the flag. Carry: dismissed: one-shot brief text, no standing instruction carries the flag
- PROMPT.md: contradiction: the payload says to pin git identity `seat` with the seat noreply address, and the snapshotted brief says `hpo-fixer`; the payload's command was followed. Carry: dismissed: the payload is the rendered instruction and names the exact command
