R11-HOTFIX: record the selftest reads the round-11 audit tree, currency.py triage directory and DX0.md added

main's required `governance / instrument-self-tests` has failed its drift step, *Refuse a self-test read set the committed table misses* (`selftest_scope.py check`), on every push since 5bc69f9b94 (last green 107988b792). Merges added directories or listings the committed `tools/ci/selftest_closures.json` did not carry: #3724 (5bc69f9b94) added `tests/mutation_ledger/survivor_triage/currency.py/`, #3723 (8fa10e00ce) added `dev/audit/rounds/round11/**`, #3739 (e893cd3d, DX0.md) made the `roster-library` step list `dev/governance/dimensions`, #3809 (18a60ea5f6) added `dev/audit/rounds/round11/J/late-D3/top6/` and its `findings/`, and #3810 (053c33bcc6) added `dev/audit/rounds/round11/D3/s1/**`. Main's tip since, 0ae95e4c9b (`ci: record nightly kills`), adds 13 files and no directory (`git ls-tree -r -d` lists the same directories at 053c33bcc6 and 0ae95e4c9b), and its job 136736442388 refuses the same four steps. None is a behaviour change: each is new data a tree-walking step reads. So this is a table re-record, not a revert.

The table committed here is `python3 -I tools/ci/selftest_scope.py absorb --from <run 44826216706's selftest-closures artifact>` over origin/main 053c33bcc6's table: main's own measurement at 053c33bcc6 unioned over the live table, the route #3708 (merged at 6d7d52709f) gives the drift step's `selftest-absorb` half. It is byte-identical (`cmp`) to run 44826216706's own `selftest-absorbed` artifact, whose step printed `selftest_scope absorb: 694 read(s) added to 4 step(s)`. Those 694 reads are `prepr`'s and `dependency-graph-census`'s dirs and `policy-lint-mutants`' probes under the round-11 directories above, and `dev/governance/dimensions` to `roster-library`'s dirs, whose three probes under it (`D12.md`, `D3.md`, `D99.md`) `compact_probes` drops because the listed directory answers for them. No run_sha or step set changes, so the table stays fresh and selection stays SCOPED.

The first head's table was run 44451107719's artifact at 7ae05284d5, which predates #3739, #3809 and #3810. A plain textual merge of #3708 was not used: it kept probe entries `absorb_entries` refuses to carry (ignored or retired paths, e.g. `.cursor/**`, `tools/audit/round4/**`).

Closes: none

## Head

`06acb5b574a2c4b2f9491d8e8fb43447be22c264` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`c52cd51ace3c1c8026882130ef37fc15abf5a6b6` is the measured head, over the previous head 248c33b40a (which carried 6a97903775: the table absorbed from run 44798542157 over main 6d7d52709f): 94aa289b5b merges origin/main 053c33bcc6 (clean), and c52cd51ace replaces the table with absorb's output over 053c33bcc6's table. origin/main tip at measurement: 0ae95e4c9b, 2026-11-21T10:45Z; `git merge-tree --write-tree origin/main c52cd51ace` is clean (tree 58eda7d2b7), and the table in that merged tree is byte-identical to this head's. The orchestrator holds every land PR but #3818 out of the train until this merges.

## Mutation proof

The drift step is skipped on pull requests (`SELFTEST_TRACE` unset), so the replay is the proof: `drift_emulate.py` runs `selftest_scope.drift(table, artifact["steps"], workflow_steps)` with the measurement taken as a main run's `selftest-closures` artifact.

Before, bd7eb6b2cd's table merged with main 698eeeb2ab, against run 44677469341 (main 698eeeb2ab):

```
head 1 refusal(s)
   UNDER-SCOPED step roster-library: dirs misses ['dev/governance/dimensions']
```

Before, 3960d9d1a3's table, against run 44798542157 (main 18a60ea5f6):

```
head 3 refusal(s)
   UNDER-SCOPED step policy-lint-mutants: probes misses ['dev/audit/rounds/round11/J/late-D3/top6/.gitattributes', 'dev/audit/rounds/round11/J/late-D3/top6/findings/.gitattributes']
   UNDER-SCOPED step dependency-graph-census: dirs misses ['dev/audit/rounds/round11/J/late-D3/top6', 'dev/audit/rounds/round11/J/late-D3/top6/findings']
   UNDER-SCOPED step prepr: dirs misses ['dev/audit/rounds/round11/J/late-D3/top6', 'dev/audit/rounds/round11/J/late-D3/top6/findings']
```

Before, 248c33b40a's table merged with main 053c33bcc6, against run 44826216706 (main 053c33bcc6); 0 against each of the three earlier runs:

```
head 3 refusal(s)
   UNDER-SCOPED step policy-lint-mutants: probes misses ['dev/audit/rounds/round11/D3/s1/.gitattributes', 'dev/audit/rounds/round11/D3/s1/findings/.gitattributes', ...
   UNDER-SCOPED step dependency-graph-census: dirs misses ['dev/audit/rounds/round11/D3/s1', 'dev/audit/rounds/round11/D3/s1/findings', ...
   UNDER-SCOPED step prepr: dirs misses ['dev/audit/rounds/round11/D3/s1', 'dev/audit/rounds/round11/D3/s1/findings', ...
```

After, this head's table, against each of runs 44677469341 (698eeeb2ab), 44798542157 (18a60ea5f6), 44807933952 (689f33e265) and 44826216706 (053c33bcc6), and against run 44868101509 (main 0ae95e4c9b, job 136736442388) with this head merged with 0ae95e4c9b:

```
head 0 refusal(s)
```

origin/main 053c33bcc6's table against each of the four gives 4 refusals, the four `UNDER-SCOPED` lines (`policy-lint-mutants`, `dependency-graph-census`, `roster-library`, `prepr`) of jobs 136092952034, 136504897866 and 136601192942 (`selftest_scope check: 127 gated step(s), 4 refusal(s)`), so the emulation reproduces CI on main's table. Against run 44868101509, 0ae95e4c9b's table gives the four lines of job 136736442388: three byte-identical, and `policy-lint-mutants`' probe line with the same first eight paths and `(+221 more)` where CI prints `(+224 more)`, because the artifact writes the probes under `dev/audit/rounds/round11/sweep/N-table-value/D14/` as one collapsed `D14/**` entry. `selftest_scope.py absorb --from` run 44868101509's `selftest-closures` artifact over this head's table prints `selftest_scope absorb: 0 read(s) added to 0 step(s)`: the table already holds everything main measured at 0ae95e4c9b.

## Null control

The missing listing changes selection, not only the drift check's exactness: `select([('A', 'dev/governance/dimensions/DX1.md')])` picks `MODE: SCOPED -- 40 step(s) run` without `roster-library` on origin/main's table, and `MODE: SCOPED -- 41 step(s) run` with it on this head's. `selftest_scope.py select --change M:docs/x.md` prints `MODE: SCOPED -- 22 step(s) run` (not FULL: the table is not stale). At this head `selftest_scope.py static`: `127 gated step(s), 0 problem(s)`; `selftest_scope.py --self-test`: `153 checks, 0 failed`.

## Figures

- `drift_emulate.py` (instrument: `selftest_scope.drift` over a main run's `selftest-closures` artifact): 4 refusals on origin/main 053c33bcc6's table against runs 44677469341, 44798542157, 44807933952 and 44826216706, and on 0ae95e4c9b's against 44868101509; 1 at bd7eb6b2cd against 44677469341; 3 at 3960d9d1a3 against 44798542157; 3 at 248c33b40a against 44826216706; 0 at this head against all five.
- `selftest_scope.py absorb`: `694 read(s) added to 4 step(s)` over origin/main 053c33bcc6's table (run 44826216706's `selftest-absorbed` step printed the same line); `0 read(s) added to 0 step(s)` over this head's table from run 44868101509's artifact.

## Red checks

`governance / instrument-self-tests` is red on main (jobs 136092952034 at 698eeeb2ab, 136504897866 at 18a60ea5f6 and 136601192942 at 053c33bcc6 and 136736442388 at 0ae95e4c9b, 4 refusals each); this head is its fix. A directory a later merge adds is not in this table.

Local gate (`GATE_SCOPE=auto`, merge base 698eeeb2ab) at 3960d9d1a3 was `MODE: FULL` (the table is a gate file) and reported `tests/entities.py`, `tests/typing_ruler.py` (mypy 2.3.1 installed against the 2.4.1 pin), `tests/optimality.py` and `node tests/card.mjs` FAILED on Darwin; no measured closure in `tests/closures.json` lists `tools/ci/selftest_closures.json`, the one file this diff edits.

Inherited from main, not touched by this diff: `code-scanning alert 57 (py/overly-permissive-file)`, `code-scanning alert 58 (py/overly-permissive-file)`, `code-scanning alert 59 (js/insecure-temporary-file)`, `code-scanning alert 60 (js/file-system-race)`, `code-scanning alert 61 (py/insecure-temporary-file)`, `code-scanning alert 62 (py/insecure-temporary-file)`, `code-scanning alert 63 (py/insecure-temporary-file)`, `code-scanning alert 64 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 65 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 66 (py/overly-permissive-file)`, `code-scanning alert 67 (py/overly-permissive-file)`. Each is a CodeQL finding on a path this pull request does not change (tools/audit/seat/postmerge.py, roster_lib.py, dev/audit/rounds/round11/ finder scripts); no cheaper detector than CodeQL itself exists for them, and their disposition belongs to the owning seats.

`tests / fast (3.14)` was red at dc00fe134963ec57cc909b7123aa008ba718b101 (job 135591236733): `tests/features.py`'s lift-peak check failed on main's own code across BLAS kernels, which this diff does not touch. Hotfix #3815 (R11-CARRY-ROOM-LIFT), merged and carried by this head's main merges, answers it. No cheaper detector exists: the failure is a float tolerance that only the fast suite's solver run on the CI kernel reaches.

## Forward-carry

none

## Friction

none

