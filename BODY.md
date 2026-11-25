Refs #3885

This PR leaves #3885 open.

## Summary

R11-CI-CASE-SELECT, part P1 of the approved design (`design/R11-CI-CASE-SELECT` 25fa1f76, verdict b7e7f57f). It adds the case splitter, the span runner, the per-span recorder, the per-span table and the table's merge arm. Nothing selects yet: `tests/run.sh` still runs each selected script whole. Selection, the fail-safes and the run.sh wiring are P2.

The branch started from `wip/r11-ci-case-sample` 9df0838b, by the owner's split ruling. Once #3893 merged, main deletes `tests/case_sample.py` after that commit, so this branch merges main (d3d66c40) and P1 depends on no part of case_sample. P2 composes with it from `wip/r11-ci-case-sample`.

- **Splitter** (`tests/case_select.py split`). A span is a top-level `R.section(<literal>)` statement up to the next one, cut from the AST. A `section` call inside a function, loop or branch is no boundary. Repeated titles get `#2`, `#3` and so on. Each span carries the sha1 of its source lines, and the header gets a hash of its own. The closing `sys.exit(R.close(...))` is the tail.
- **Runner** (`run <script> [--plan FILE]`). Runs the header, then each span compiled from its own AST slice into one `__main__` namespace (with the header's `__future__` flags), then the tail. It prints one key line, `CASES: FULL <script> -- ...` or `CASES: SCOPED <script> -- k of n spans`.
- **Recorder** (`record <script> [--union]`). Each span's `files` is the union of:
  - (a) `open` audit events;
  - (b) the files of code objects it starts (`sys.monitoring` PY_START, DISABLE, `restart_events` at each boundary);
  - (c) static references: the span's own names resolved in the live namespace, plus each started code object's names that its module binds by import, then one more hop through those modules' module-level imports;
  - (d) the repository paths in its subprocess argv.

  Each span's `needs` is the union of:
  - the static binders of the names it reads, from the AST. Assignment, def, class, import, `global`, attribute and item stores, in-place calls (`append`, `update` and the rest), and the effects of module-level functions it calls, transitively. A definite top-level rebinding resets a name's binders; anything else adds to them;
  - `@random`: every RNG draw both reads and moves it, in the AST and in the recorder's `random.getstate()` and `np.random.get_state()` fingerprints (carry rng-consume). So a drawing span needs the previous drawing span, back to the seeder, including draws inside production code;
  - dynamic moves: fingerprints of module-level globals and of every repository module's attributes at each boundary. A span that moves one is needed by a later span that reads that name, or whose `files` hold that module;
  - net moves of shared process state (environment, `sys.path`, logging root, warning filters, locale), which are needed by every later span.
- **Table** (`tests/case_closures.json`). It has the design's shape, `{"version", "recorded_at", "files", "scripts": {script: {"blob", "header_hash", "header", "spans": {id: {"hash", "files", "needs", "seconds"}}}}}`.
  - Each path is stored once and spans hold indices.
  - A re-recording keeps the previous path indices and appends new paths, and each span sits on its own line. So a re-recording moves only the changed spans' lines, and two branches touching different spans merge as text.
  - A full re-derivation compacts the path list.
- **Ledger arm.** `.gitattributes` routes the table to `ledgermerge`, and `tools/merge/ledger_merge.py` hands it to `case_select.merge_tables`. For each span, one side wins when only that side changed it. When both re-recorded it, `files` and `needs` are united. When both edited it differently, ours wins with the sets united. `blob` and `header_hash` follow the side that moved them.
- **`tests/derive_closures.sh --cases`**: records every case script and replaces its entries, on Linux only. Off Linux it exits 2 before planning or leasing anything. `--cases --single <script>` unions one script and is what an off-Linux host may run (`gate-scoping.md`).
- Classification: `tests/case_select.py` is on `NOT_A_TEST` and is a gate file, and so is `tests/case_closures.json`. `tests/run.sh` skips `case_select.py` in its wiring loops, and `tests/entities.py` runs its self-test.

Recorded at this head on Darwin with `tests/derive_closures.sh --cases --single <script>` (union into an empty entry):
- `tests/features.py`: 248 spans, `ALL 6170 FEATURE CHECKS PASSED`, `CASES: FULL tests/features.py -- recording, 248 spans`.
- `tests/entities.py`: 65 spans, `1 of 2763 ENTITY CHECKS FAILED`. The one failure is `a measured script's late-writing descendant is waited for, not recorded as nodata`. That timing check also failed under a plain `python3 tests/entities.py` at 387c44fa on this loaded host, so it does not separate the runner from the host.
- `python3 tests/case_select.py stats tests/features.py`: `248 spans; table 874588 bytes, 599 paths; files/span median 100.0 max 140; needs/span median 37.5 max 124; 225 spans read over half of the 108 custom_components files recorded; span seconds 1022.2`
- `python3 tests/case_select.py stats tests/entities.py`: `65 spans; ... files/span median 88 max 560; needs/span median 10 max 42; 31 spans read over half of the 121 custom_components files recorded; span seconds 1388.3`
- The table is 874,588 bytes (`wc -c tests/case_closures.json`). The design estimated about 200 KB.

## Head

`8e9f5a5b9af9abf8f2f5a37227c8bd1c95442201`, with `origin/main` `d3d66c4040` merged in. The table's `blob` for each script equals `git hash-object` of that script at this head (`04cc69a4` features.py, `5cd6e979` entities.py).

## Mutation proof

`python3 tests/case_select.py --self-test` runs 27 checks over a synthetic flat script and module it writes. `tests/entities.py` runs it as a check. Each mutant below was applied in place, run, and restored:
- Drop (c), the static references (`files` = opened plus started code only): 2 FAIL. `recorder (c): beta reads a constant of M and runs no M code, yet its files hold M`, and the count/bump check.
- Drop the module fingerprint moves (`moved_mods.add(u)` to `pass`): 1 FAIL, `recorder: a module global moved inside M's own code (no store the AST sees) gives count needs [bump]`.
- Drop the in-place binding (`L.append` binds `L`): 1 FAIL, `static: an in-place L.append binds L for a later reader (zeta needs eps)`.
- A draw does not bind `@random`: 1 FAIL, `static: every RNG draw binds @random, so a draw needs the previous draw and the seeder`.
- The ledger driver does not route the table (`if pathname in _TABLE_ARMS` to `if False`): 1 FAIL, `the ledgermerge driver routes tests/case_closures.json to merge_tables`. The plain driver left a conflicted file and rc 1.

Failing first: the recorder (c) check was red on the first implementation, because temp-path resolution dropped every file. It went green once paths were resolved.
Unmutated: `CASE-SELECT SELF-TEST: PASSED (27 checks)`.

## Null control

- Runner equivalence on the real script. The span-wise recording run of `tests/features.py` prints the same 6284 `ok`/`FAIL` lines, in order, as main's push run 45596992195's `tests / fast (3.14)` job on the same text less the case-sample hook. Both end in `ALL 6147 FEATURE CHECKS PASSED` (the recording at a3186421, compared before the merge moved the text). One line differs in text: a check that prints its checkout path (`/home/runner/...` against `/Users/...`). With numbers masked, the sequences are identical.
- Fixture: a plan naming one span drops exactly the other spans' section and check lines (`null control: a plan naming eps alone drops zeta's section and check lines`).
- Static against dynamic: the count span's need of bump comes from the recorder alone. The static rule gives it no such need, which the same check asserts.

## Figures

Run locally at this head: `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED`; `python3 tests/closure.py selftest` gives `ALL 118 closure shrink pins PASSED`; `python3 tools/merge/ledger_merge.py --self-test` gives `all passed`; `bash -n` passes on `tests/run.sh` and on `tests/derive_closures.sh`; and `bash tests/derive_closures.sh --cases` on Darwin exits 2 with the Linux-only message before planning or leasing.
Not run locally: a full `prepr.sh`. Linux recording (`--cases` without `--single`) also did not run, because this host is Darwin.

## Red checks

None known at the handoff. The only local red is the entities.py timing check named above, which also fails on a plain run on this host.

## Forward-carry

- R11-CI-CASE-SELECT P2: selectivity as recorded. Rule (i) will select most spans on a production diff:
  - features.py: files/span median 100, max 140, and 225 of 248 spans read over half of the 108 recorded custom_components files;
  - entities.py: files/span median 88, max 560, and 31 of 65 spans read over half of 121;
  - needs: median 37.5 (features) and 10 (entities).
  Enumerator: `python3 tests/case_select.py stats tests/features.py` and `... stats tests/entities.py`. P2 measures which of (b) started code and (c) the one-hop import closure carries the width, and narrows it before the measurement table. Carry: #3885, lands in dev/programme/carries/carry-3885.json
- R11-CI-CASE-SELECT P2: recorder overhead is not measured. Span seconds were 1022.2 (features) and 1388.3 (entities) on a loaded Darwin host, against `recorded` plain seconds of 1616.7 and 1338.1 in `tests/closures.json`. These are different hosts and loads, so the design's 10% budget is still to be measured on a FULL main run in CI. Enumerator: the same `stats` lines, and `python3 -c "import json;print(json.load(open('tests/closures.json'))['recorded'])"`. Carry: #3885, lands in dev/programme/carries/carry-3885.json
- R11-CI-CASE-SELECT P2: carry pin-count. The soundness replay derives the features.py and entities.py pin counts from `tests/mutation_ledger/` at run time and never writes a literal. Carry: #3885, lands in dev/programme/carries/carry-3885.json

## Friction

None.
