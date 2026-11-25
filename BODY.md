Refs #3885

This PR leaves #3885 open.

## Summary

Two cuts to the fast job's time on a pull request.

1. **`tests/stress.py` does not run on a pull request.** `tests/run.sh`'s `lane_stress` skips it by name when CI's fast job names the event `pull_request` (`HPO_CI_EVENT`, set in `.github/workflows/tests.yml`) and the gate is not `GATE_SCOPE=full`. It still runs on the push to main, which forces `full`, and in a local run, which sets no event. `nightly.yml`'s `slow` job did not run it, so this PR adds it there as its own step. `tests/harness_headers.py` still runs alone at the end of the run.
2. **`tests/features.py` and `tests/entities.py` run a seeded sample of their sections on a pull request.** `tests/case_sample.py` is the one shared helper. Each script calls `case_sample.engage(__file__, name)` once, right after its imports. On a pull request the fast job sets `HPO_CASE_SAMPLE=0.3`, with the head SHA as `HPO_CASE_SAMPLE_SEED`, so a rerun at the same head repeats the same subset. Every other event leaves both empty, and `GATE_SCOPE=full` forces the full set whatever the knobs say. Each run prints one line, so a sampled run cannot be read as a full one: `CASE-SAMPLE: <script> ran k/n (seed <sha8>)`, or `CASE-SAMPLE: <script> FULL n/n`.

How the cases are found, and which ones stay whole. These scripts are flat modules. A case is an `R.section(...)` block, run top to bottom in one namespace, and later sections read names that earlier ones bind. The sampler parses the script, keeps the header (everything before the first section) and the closing `sys.exit(R.close(...))`, and walks the sections from last to first, tracking the names that a section that will run reads before binding them itself. A section always runs when:
- it binds a name such a later section reads (comprehension targets and function parameters are scoped out);
- it stores into an object hung off such a name, off a name the header binds, or off a name no section binds (a module, a builtin). A store is an attribute or item assignment, `del`, an augmented assignment, or a call of a mutating method at module scope (`append`, `extend`, `update`, `setdefault`, `add`, `pop`, `seed`, `shuffle`, `putenv` and the rest of `_MUTATORS`), so `L.append(1)` stores into `L` and `os.environ.update(...)` into `os`;
- it calls `exec`, `eval`, `globals`, `vars`, `locals`, `setattr` or `delattr`.

Every other section is drawn, and kept with probability 0.3. Because the walk runs backward, a section whose only reader the draw dropped can then be drawn as well. What this rule does not see: a side effect inside a function the section calls, such as a helper that appends to a module-level list or reseeds `random`. It also misses a mutating method whose name is not on the list. The backstop for that residue is the push to main, which runs every section.

Measured estimate. Enumerator commands: `python3 tests/case_sample.py --plan tests/features.py` and `--plan tests/entities.py` (20 seeds, fraction 0.3), and the `recorded` seconds in `tests/closures.json`.
- stress.py: 928.7 s recorded, saved on every pull request's fast run. It runs alone at the end, so the saving is wall-clock.
- features.py: a draw drops 58 to 72 of 248 sections, on average 10.7% of 100,459 section lines. At its recorded 1616.7 s, that is about 173 s.
- entities.py: a draw drops 12 to 24 of 65 sections, on average 6.2% of 43,527 section lines. At its recorded 1338.1 s, that is about 83 s.
- These two figures read line share as time share. They are an estimate, not a timing.
- A blind 30% sample would save 70% of the two scripts' 2954.8 s, about 2068 s. This rule saves about 256 s, because most sections feed later ones. A statement-level unit measured about 27% of features.py's lines and 21% of entities.py's under the same rule. That is R11-CI-CASE-SELECT's ground, not this PR's.

Safety net. The push to main always runs FULL: `GATE_SCOPE=full`, no event knob, stress.py included and every section run. A merge that turns main red is reverted first.

## Head

`9df0838b1d5adf8b7990557699f9cb24618b0b4d` on `origin/main` `34c7a3f610`.

## Mutation proof

`tests/case_sample.py --self-test` (26 checks over a fixture script it writes and runs) fails under each mutant:
- `choose()` with the binds-a-live-name rule switched off (`elif held and False:`) gives 4 FAIL lines, among them `over 40 seeds every sampled run exits 0, keeps the order-dependent section, and never runs a reader without the section it reads`.
- `fraction()` with the `GATE_SCOPE=full` guard switched off (`if False:`) gives `CASE-SAMPLE SELF-TEST: 2 FAILED`: `GATE_SCOPE=full forces the full set` and `... runs the full set even with a sample asked for  [CASE-SAMPLE: fx ran 1/10 (seed 01234567)`.

- The review's fixture, a section that appends to a list another section built and one that updates `os.environ`, each followed by a reader, is red before the mutating-method rule (`FAIL a section that mutates through a method call (L.append, os.environ.update) a later reader sees always runs  [{... 'mut': 'free to draw', 'env': 'free to draw' ...}]`) and green after it.

Unmutated: `CASE-SAMPLE SELF-TEST: PASSED`. tests/entities.py runs the self-test as a check, so the gate carries it.

## Null control

- With the knobs empty, the fixture runs `FULL 10/10`, every section in order (self-test).
- With `GATE_SCOPE=full` and a sample asked for, it still runs `FULL 10/10`.
- On the stress side, `lane_stress` keeps its `run` line for every event but `pull_request`, so a push to main runs stress.py as before.

## Figures

`python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc 0 at this head. `node tools/policy/brief_lint.mjs`: this diff touches no brief, roster or carry file; its run was still in progress at the handoff, on a loaded host.
Not run locally, by the owner's expedite ruling (#3394): a full `prepr.sh`, and full runs of `tests/features.py` and `tests/entities.py` under a sample. CI's fast job on this PR is the first sampled run of each.

## Red checks

None known at the handoff. CI is not awaited on this PR (#3394).

## Forward-carry

none

## Friction

None.
