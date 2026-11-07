Bound the process worker's reply. Before this change `_run_in_process` wrote the job and blocked in `pickle.load(stdout)` inside `with _PROCESS_LOCK:` with no deadline. A worker that is alive but silent never raises, so the #511 fallback never fired; every later solve queued on the lock, a reload did not help, and Home Assistant's stop ran into the supervisor timeout. The branch adds the reply deadline (`PROCESS_REPLY_TIMEOUT_S`, 1800 s; the contributor's change), the off-loop route's re-raise and held warning, the frame deadline (`_REPLY_FRAME_TIMEOUT_S`, 60 s), the frame size cap (`_REPLY_FRAME_MAX_BYTES`, 256 MiB), the stop path's bounded lock (`_SHUTDOWN_LOCK_TIMEOUT_S`, 5 s), and the diagnosis service's translated failure (`diagnose_interval_failed`). The worker checks live in `tests/worker_deadlines.py`, a module `tests/features.py` calls, so CodeQL extracts them as a separate small file (round 3).

This round (5) repairs the review block at `bba5b4d4` (verdict `mutation-vacuous: measure`). The mutant that deletes `left_bytes -= size` in `_frame_reader.read` (`coordinator.py`, the running count that makes `_REPLY_FRAME_MAX_BYTES` a bound on the whole frame rather than on each `read()`) survived every feature check, and the real reader then accepted a 1,200,044-byte frame over a 1,000,000-byte cap. The repair adds one check pair to `tests/worker_deadlines.py` and changes no production code.

**Trust boundary.** Unchanged by this round. The worker is the integration's own child process, launched by `_ensure_worker` from the installed package; its reply is unpickled in the parent as at base; `_frame_reader` feeds the same `pickle.load` under a time bound and a size bound. This round touches no file under `custom_components/`.

## Acknowledgements

Thanks to @Bankaifan for the original change in #3226: the bounded reply deadline on the process worker, and the field report and shutdown traces that found the hang. This pull request is a seat re-author of that contribution: decision 0011 gives an outside contributor no way to author a pull request here. His four commits (`61cec72ac`, `010534bbc`, `dd4416f1a`, `5088d3688`, author Bankaifan) are kept intact, no edit, squash or rebase; the seat's repairs are separate commits on top.

## Head

`dc8cbd06c1da1e258c082015bc10aa206f884780`: the round's one test commit merged with `origin/main` `80016a71f567d936450d8708abcbb79d9e8071d7` (a merge, no rebase), on top of the previous handoff `79f202f8e`. `origin/main` had not moved since that merge when the body was written. Every figure below was taken at this head unless it names another SHA.

## Mutation proof

The mutant `measure`: delete the line `        left_bytes -= size` in `_frame_reader.read` and run `PYTHONPATH=tests/hastub python3 tests/features.py`.
- At the head with the mutant: `1 of 4904 FEATURE CHECKS FAILED`. The one failure is the new check "a reply whose reads each fit the frame cap but whose total exceeds it is refused and the worker reaped" (`raised None after 0.00 s`, the whole oversized reply returned). The null control beside it still passes.
- With the line restored: `ALL 4904 FEATURE CHECKS PASSED`, and `git diff -- custom_components` is empty.
- The check drives the real worker: with `_REPLY_FRAME_MAX_BYTES` shortened to 1,000,000 it sends `tuple([bytes(600_000), bytes(600_000)])`, two reads that each fit the cap and total 1.2 MB, and requires a `ProcessWorkerUnavailable` saying `exceeds 1000000 bytes`, no returned value, the lock free and `_PROCESS_WORKER` reaped.
- No `killed_by` ledger row was added for this site, and none can be: `tests/mutation_table.py` generates no mutant that deletes an augmented assignment, and `completeness_problems` refuses a disposition naming a site the inventory does not generate, so a hand-written row would turn the driver red. The mutant is killed by a check, which is the proof; the 20 rows from earlier rounds are unchanged. The operator gap is the verdict's own Findings item, which the orchestrator routes.

## Null control

`null control: a reply of two reads whose total is under the frame cap returns whole` (two 400 kB strings under the same 1,000,000-byte cap) prints `ok` at the head and with the mutant. Base `9a54629e` has no cap, so it accepts both replies; the review measured that (`ALL 4898 FEATURE CHECKS PASSED`). The pin runs of earlier rounds recorded `null control ... NULL_COMMENT survived` against a comment-only edit.

## Figures

- `ALL 4876 FEATURE CHECKS PASSED` at base `origin/main` 80016a71f, and `ALL 4904 FEATURE CHECKS PASSED` at this head (+28 over base, of which 2 are this round's) — `PYTHONPATH=tests/hastub python3 tests/features.py`, run in each tree
- `ALL 2640 ENTITY CHECKS PASSED` at base and at this head — `PYTHONPATH=tests/hastub python3 tests/entities.py`
- `STRUCTURE RATCHET PASSED` — `python3 -I tests/structure.py`
- scope `MODE: FULL -- every test script runs, nothing is scoped out.` (reason: `tests/closure.py` is in the diff), then `ALL TEST SCRIPTS PASSED` before the final merge — `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`. After the final merge I re-ran `tests/arch_score.py` alone (`ALL 279 ARCHITECTURE SCORE CHECKS PASSED`), `structure.py` and `entities.py`; the full gate was not repeated, and the merge changed no file this diff touches
- `PRE-PR: dc8cbd06c1da1e258c082015bc10aa206f884780 ... rc=0` — `HPO_ALLOW_STALE_TOOLS=1 bash tools/pr/prepr.sh`; its `diff mutants` step is skipped there (`MUTANT_CMD unset`, report only)
- `tests/worker_deadlines.py` holds 27 `R.check(` call sites (two are this round's; a loop or two makes the printed `ok` lines more than the sites) — `grep -c "R.check(" tests/worker_deadlines.py`
- claim files, `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched — `git diff --stat origin/main...HEAD -- tests/golden VERSION RELEASE_NOTES.md`

## Red checks

`none`: no check has concluded at this head, which exists only as the handoff ref; the review classified the previous PR head `bba5b4d4` `GREEN ... red: none`. Two local reds were seen and cleared while preparing this head, neither a CI check: `tests/arch_score.py` read one failure (`a head edit to tests/structure.py is not what the gate loads`) because a 230 s timeout of my own had left `/opt/hpo/runner-temp/base` behind, and it passed once that directory was removed; `prepr.sh` read `REFUSE self-test 512 passed, 1 failed` on the `no-matcher` policy-lint null control while four jobs ran at once, and passed alone, as the comment at `tools/pr/prepr.sh` 1932–1934 describes for that row.

## Forward-carry

- `tests/mutation_table.py` draws no mutant that deletes an augmented assignment (`x -= n`), so any running-count bound can be unpinned while the mutation lane stays green. Carry: dismissed: instrument class outside this PR's diff; the orchestrator routes it to the mutation-tooling owner or refuses it
- `refs/heads/handoff-wip/r10-ext-3226` still holds round 4's lineage ending in its `BLOCKED` note `711f2719d` plus an earlier seat's later commit, neither an ancestor of this head, so this round could not fast-forward it and made no step push. Carry: dismissed: orchestrator's dispatch, not a finding

## Friction

- fixer-step-push: contradiction: the brief says to step-push fast-forward only to `handoff-wip/r10-ext-3226` and to delete it after the handoff, but that ref holds commits outside this head's ancestry, so neither was possible without discarding them. Carry: dismissed: orchestrator's dispatch, not a finding
