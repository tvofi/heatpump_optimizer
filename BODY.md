Closes the two open CodeQL `py/overly-permissive-file` alerts on main: 57 (`tools/audit/seat/postmerge.py`, `enqueue`'s `os.open(..., 0o644)` creating the state dir's `roster-drain.queue`) and 58 (`tools/audit/seat/roster_lib.py`, `writer_lease`'s `os.open(..., 0o644)` creating `roster-writer.lease`). Both are created `0o600` now.

Readers, by `rg -n "roster-drain\.queue|roster-writer\.lease|WRITER_LEASE|writer_lease|postmerge\.QUEUE"` over the tree: `beat_jobs.py` (the drain, and the lease) and `carry_fold.py` (the lease), both run by the operator against the same `HPO_STATE_DIR`. No reader runs as another user or needs group or world read, so owner-only loses nothing. `beatd.py`, `beat_jobs.py` and `hooks_setup.py` already create their own lock files `0o600` in the same state dir.

The class, swept over `tools/` and `custom_components/` with `rg -n "os\.open\(|os\.chmod\(|\.chmod\(|mktemp\(|0o6[0-7][0-7]|0o7[0-7][0-7]"`: these two are the only sites creating a non-executable file group- or world-readable. The rest create `0o600` or `0o700` files, set `0o755` on executables (hooks, `gh`/`ps`/`strace` stubs), or set modes on self-test fixtures (`tools/release/stamp.py`'s `push_key_problem` checks, which set `0o644` and `0o666` to prove the refusal). No `tempfile.mktemp` call exists; `tools/pr/prepr.sh`'s `mktemp` is a shell function.

## Head

036cb18339921f4c8fc408e4f6900660c4236370

## Mutation proof

Each self-test now pins the created mode under an explicit `umask 022`, so the pin does not depend on the caller's umask.

- `postmerge.py`: the new `MUTANTS` entry `queue_world_readable` reverts the mode to `0o644`. `python3 tools/audit/seat/postmerge.py --self-test` prints `ok   mutant queue_world_readable killed by: the queue enqueue creates is owner-only under umask 022`.
- Both sites through `tools/audit/seat/mutant_run.py --spec`, each spec reverting one site's `0o600` to `0o644`: `--cmd 'python3 tools/audit/seat/roster_lib.py --self-test'` prints `KILLED lease_world_readable`, and `--cmd 'python3 tools/audit/seat/postmerge.py --self-test --no-mutants'` prints `KILLED queue_world_readable`. Each run's unmutated copy prints `SURVIVED NULL`, so the pass is the tree's own.

## Null control

Main's code (the two pins added, the modes still `0o644`): `python3 tools/audit/seat/roster_lib.py --self-test` fails `writer_lease: the lease file is owner-only under umask 022 (got: 0o644)`, and `python3 tools/audit/seat/postmerge.py --self-test --no-mutants` fails `the queue enqueue creates is owner-only under umask 022 (got: 0o644)`. At the head, both self-tests report 0 failed.

## Figures

- `python3 tools/audit/machinery_ratchet.py --check --head HEAD --base origin/main --pr 99999` at the head, on `origin/main` 18a60ea5f6 (`99999` stands in for this PR's number): `ok   target nonproduction_merges 476 <= 478 + band 5 (121 merge(s) past anchor b3831ff64eca, 48 down per 290)`, rc 0. The target binds this candidate, a non-production change, and admits it.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` at the head, on Darwin with a load average of about 34: `tests/layout.py` passed and `tests/entities.py` printed `2 of 2735 ENTITY CHECKS FAILED`. The two are timing checks that read neither changed file. `hb:positive_control survives one hung py-spy sample` read a 600 ms spin as 790.7 ms. `a measured script's late-writing descendant is waited for, not recorded as nodata` failed its zero-bound arm. Another seat's branch on this host (`fix3734`) failed the same two checks in the same hour. The Linux `tests / *` runs decide them.

<!-- figure-block: scope-line mb=18a60ea5f66223c3948738a6be284f035c5f9bac head=036cb18339921f4c8fc408e4f6900660c4236370 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

- code-scanning alert 57 (py/overly-permissive-file) and code-scanning alert 58 (py/overly-permissive-file): this PR is their fix. The next CodeQL run on main closes them; neither is dismissed. Cheaper detector: the self-test pins added here, which each instrument's `--self-test` lane runs. Standing cost: one `os.stat` per run. Both sites are tooling run by the operator, not shipped in `custom_components/`, and no other site of the class exists in `tools/` or `custom_components/`. The pins guard these two sites and nothing else.

## Forward-carry

none

## Friction

none
