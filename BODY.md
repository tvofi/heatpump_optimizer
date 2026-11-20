R11-HOTFIX: record the selftest reads the round-11 audit tree, currency.py triage directory and DX0.md added

main's required `governance / instrument-self-tests` has failed its drift step, *Refuse a self-test read set the committed table misses* (`selftest_scope.py check`), on every push since 5bc69f9b94 (last green 107988b792). Merges added directories or listings the committed `tools/ci/selftest_closures.json` did not carry: #3724 (5bc69f9b94) added `tests/mutation_ledger/survivor_triage/currency.py/`, #3723 (8fa10e00ce) added `dev/audit/rounds/round11/**`, #3739 (e893cd3d, DX0.md) made the `roster-library` step list `dev/governance/dimensions`, and #3809 (18a60ea5f6) added `dev/audit/rounds/round11/J/late-D3/top6/` and its `findings/`. None is a behaviour change: each is new data a tree-walking step reads. So this is a table re-record, not a revert.

The table committed here is `python3 -I tools/ci/selftest_scope.py absorb --from <run 44798542157's selftest-closures artifact>` over origin/main 6d7d52709f's table: main's own measurement at 18a60ea5f6 unioned over the live table, the route #3708 (merged at 6d7d52709f) gives the drift step's `selftest-absorb` half. Against origin/main's table it adds 595 reads to 4 steps: 198 dirs each for `prepr` and `dependency-graph-census`, 198 probes for `policy-lint-mutants`, and `dev/governance/dimensions` to `roster-library`'s dirs, whose three probes under it (`D12.md`, `D3.md`, `D99.md`) `compact_probes` drops because the listed directory answers for them. No run_sha or step set changes, so the table stays fresh and selection stays SCOPED.

The previous head's table was run 44451107719's artifact at 7ae05284d5, which predates #3739 and #3809. A plain textual merge of #3708 was not used: it kept probe entries `absorb_entries` refuses to carry (ignored or retired paths, e.g. `.cursor/**`, `tools/audit/round4/**`).

Closes: none

## Head

`6a97903775822deec5e988e75b78cefed07be173` is the measured head, over bd7eb6b2cd: f08eb4cdd0 merges origin/main 698eeeb2ab (clean); 3960d9d1a3 takes run 44677469341's artifact; 20c11516d3 takes run 44798542157's; 0764c77d6d merges origin/main 6d7d52709f (clean, textual); 6a97903775 replaces the merged table with absorb's output. origin/main tip at measurement: 6d7d52709f, 2026-11-20T21:10Z.

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

After, this head's table, against each of runs 44677469341 (698eeeb2ab), 44798542157 (18a60ea5f6) and 44807933952 (689f33e265):

```
head 0 refusal(s)
```

origin/main 6d7d52709f's table against each of the three gives 4 refusals, the four `UNDER-SCOPED` lines (`policy-lint-mutants`, `dependency-graph-census`, `roster-library`, `prepr`) of job 136092952034 and job 136504897866 (`selftest_scope check: 127 gated step(s), 4 refusal(s)`), so the emulation reproduces CI on main's table.

## Null control

The missing listing changes selection, not only the drift check's exactness: `select([('A', 'dev/governance/dimensions/DX1.md')])` picks `MODE: SCOPED -- 40 step(s) run` without `roster-library` on origin/main's table, and `MODE: SCOPED -- 41 step(s) run` with it on this head's. `selftest_scope.py select --change M:docs/x.md` prints `MODE: SCOPED -- 22 step(s) run` (not FULL: the table is not stale). At this head `selftest_scope.py static`: `127 gated step(s), 0 problem(s)`; `selftest_scope.py --self-test`: `153 checks, 0 failed`.

## Figures

- `drift_emulate.py` (instrument: `selftest_scope.drift` over a main run's `selftest-closures` artifact): 4 refusals on origin/main 6d7d52709f's table against runs 44677469341, 44798542157 and 44807933952; 1 at bd7eb6b2cd against 44677469341; 3 at 3960d9d1a3 against 44798542157; 0 at this head against all three.
- `selftest_scope.py absorb`: `595 read(s) added to 4 step(s)` over origin/main 6d7d52709f's table.

## Red checks

`governance / instrument-self-tests` is red on main (jobs 136092952034 at 698eeeb2ab and 136504897866 at 18a60ea5f6, 4 refusals each); this head is its fix. Main run 44813755126 at 6d7d52709f was in progress at measurement; a directory a later merge adds is not in this table, and its `selftest-absorbed` artifact is the next re-take if it names one.

Local gate (`GATE_SCOPE=auto`, merge base 698eeeb2ab) at 3960d9d1a3 was `MODE: FULL` (the table is a gate file) and reported `tests/optimality.py` and `node tests/card.mjs` FAILED on Darwin; this diff edits only selftest closure data, which neither script reads.

Inherited from main, not touched by this diff: `code-scanning alert 57 (py/overly-permissive-file)`, `code-scanning alert 58 (py/overly-permissive-file)`, `code-scanning alert 59 (js/insecure-temporary-file)`, `code-scanning alert 60 (js/file-system-race)`, `code-scanning alert 61 (py/insecure-temporary-file)`, `code-scanning alert 62 (py/insecure-temporary-file)`, `code-scanning alert 63 (py/insecure-temporary-file)`, `code-scanning alert 64 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 65 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 66 (py/overly-permissive-file)`, `code-scanning alert 67 (py/overly-permissive-file)`. Each is a CodeQL finding on a path this pull request does not change (tools/audit/seat/postmerge.py, roster_lib.py, dev/audit/rounds/round11/ finder scripts); no cheaper detector than CodeQL itself exists for them, and their disposition belongs to the owning seats.

`tests / fast (3.14)` was red at dc00fe134963ec57cc909b7123aa008ba718b101 (job 135591236733): `tests/features.py`'s lift-peak check failed on main's own code across BLAS kernels, which this diff does not touch. Hotfix #3815 (R11-CARRY-ROOM-LIFT), merged and carried by this head's main merges, answers it. No cheaper detector exists: the failure is a float tolerance that only the fast suite's solver run on the CI kernel reaches.

## Forward-carry

none

## Friction

none
