# Design: R11-OWNER-FEATURES-SPLIT (revision 3)

Answers `Design review: revise` f4c840caf0 at `design-verdict/R11-OWNER-FEATURES-SPLIT` cc2c99c10e (V1-V3, N6). Base and code read at `origin/main` ef797d794017c98f7fb2d8a168d7de63d435ef3b; no predecessor handoff. Owner order, no finder harness: owner report. Owning seam: tests/features.py. Sections 0, 1 steps A-B, 5's test-id null and 6 stand as revision 2 states them; this note repeats what a fixer needs and changes only what V1-V3 move.

**Spike** (never merges): `swap_run.py`, `diff.py`, `linereach.py`, `refclass.py` and the planted control, at the comms snapshot dab20b60ec0681e4d53b1dce3d9c028c4e4ecd51, reachable from `handoff-wip/r11-owner-features-split-comms` (`git fetch origin handoff-wip/r11-owner-features-split-comms && git show dab20b60ec0681e4d53b1dce3d9c028c4e4ecd51:spike-r11-owner-features-split/<file>`). Every figure below is printed by one of them at the base; `## Figures` names the command.

## 0. Order (D1, orchestrator ruling, unchanged)

After R11-CI-CASE-SELECT P2 and P3 merge. Unit = a `case_select.split` span (252 at the base; the 4 the table lacks are recorded by `tests/derive_closures.sh --cases` on Linux first). The partition reads the table's `needs` and `case_select.Recorder` in process; each part is a `case_select.SCRIPTS` entry re-recorded by `--cases`; drives use `case_select run <part> --plan`.

## 1. Partition, and the gate (V1)

**Step A** (seam by distinct production modules a span names, tie to the first of inputs, model, plan, dhw, actuation, surface; none to cycle; revision 1's module table) and **step B** (edge types T0-T5) are unchanged; `swap_run.py partition` reproduces step A's counts. Step C places T1-T4 as revision 2 does (imports per part header; T2/T3 to one helper module; T4 bindings copied ahead of the first consumer per part). **T5 is no longer refused by edge.**

**The gate is the swap run's difference set.** One `case_select.run` of the monolith in source order with a span-boundary hook (`swap_run.Swapper`, passed where `run` takes a recorder) that keeps one copy per part of every state family and swaps the entering span's part's copy in: every repository module's attributes (an attribute a part never had is deleted, a module object kept), the contents of their module-level dicts, lists and sets (the stub store's `_DISK`, `_VERSIONS`, `SAVE_COUNTS`, the process-worker and off_restore registries among them), the attributes of every class a repository module or the script defines, `random` and `np.random` state, `os.environ`, `sys.path`. Script-namespace names (T1-T4) stay shared by design. Each part starts from the state the header leaves. A span whose sorted `ok`/`FAIL` lines differ from a plain run of the same harness is load-bearing; the difference set is the list of them. **`--check` passes iff that set is empty over the whole split; `--port` iff it is empty for the branch's monolith under main's manifest plus the branch's new rows.** The T5 edge list is printed beside it as advisory. Non-load-bearing cross-part T5 edges remain by design: the `np.sort(...)` reading of `np` as mutated, a store key that a P0-seeded consumer no longer reads, any of the 72 store producers whose saves no other part's check reads. After the port window no such gate is owed: parts are separate processes, so a new section in one cannot read another's state.

**Measured at the base (spike, step A's partition):** 2 of 252 spans differ, both in the v5.1.10 legionella group: *a due cycle actually reaches the disinfection temperature* (plan; a check raises `TypeError` on a `None` step) and *a cycle the tank cannot reach is not parked at the end* (dhw; 3 checks read `placed at step None`). The same 2 differ with the stub store left unswapped (`--drop store`), so the family is a class patch: the model span *the charge limit is the charge limit, every ordinary day* sets `DhwPlanner._build_dhw_requirements = _lg_build_spy` at features.py:40855 and never restores it, and both readers call `_lg_step`, which reads what the spy recorded. **P0 at the base is one edit**: the same assignment as the first statement after the `R.section` line of each of the two readers (`_lg_build_spy` is T3 and goes to the helper module). **`--check` then passes**: on a copy carrying exactly those two lines, under the base's step-A partition (`--parts`, no span moves), the swap run against the copy's plain run prints 0 of 252 spans differing, and the copy's plain run equals the base's (6409 lines, no test id moves). This is the measured partition's whole P0 work list, against revision 2's 7199 crossing T5 edges, which stay as advisory.

**Controls**, each run: the one-part null (`run one`, every span one part, so no boundary swaps) against `run plain`: 0 of 252 spans differ, 6409 lines each. Planted positive (`planted/planted.py`: a stub-store save, a `random.seed`, and a module attribute patch each made in part A and read by a check in part B): the swap run lists exactly the three readers, the one-part run none. That control first found a hook miss (a patch adding a new attribute was not undone) which the deletion rule above fixed; a module first imported inside a span is swapped only from the next boundary, and on-disk files and subprocess state are never swapped: both are caught by the split null (section 5), which is the swap run's control.

## 2. The splitter and its manifest (V1 applied)

One committed instrument under `dev/audit/harnesses/`, the spike's shape: `--measure` prints step A-C tables and the advisory edge list; `--check` refuses a non-empty difference set, an unclassified module, a span missing from the manifest, and a reference line `refclass` leaves unclassified (section 3); `--write` writes the parts, the helper module and the manifest; `--port` regenerates a branch's parts under main's manifest, adds rows for its new spans only, and runs the gate. The manifest (`{span id: {"part", "hash"}}`, shared names, copied bindings) is the only source of a span's part after `--write`; no rule is re-run over existing spans. Gate cost: one plain and one swap run of the monolith, about 850 s wall each on this seat, run side by side (the swap hook's boundary copies cost no measurable time over the plain run). Port of an open branch is revision 2's (merge main's last pre-split commit, then `--port`); 18 of 21 open pull requests touched tests/features.py at the base.

## 3. Every reference, classified (V3)

Enumerator: `git grep -n 'features\.py' -- ':!dev/audit/rounds' ':!tests/mutation_ledger' ':!tests/features.py' | python3 refclass.py`; it prints 1151 lines in 199 files at the base, each in exactly one class, and exits 1 on a line in none. Python comments and docstrings are told from data literals by `tokenize` and `ast`, not by pattern.

| class | lines | files | disposition |
|---|---|---|---|
| R runner or opener | 34 | 9 | retargeted: `tests/run.sh:580` and nightly.yml's Kolkata step run every part; `tests/README.md:346` names the parts; `verify_eight.py:92` runs the part list; `features_block.py:195` takes the manifest and finds a marker across the parts (so the 4 B-class harnesses keep working unchanged); `prepr.sh:2848/2870` plants into a part (its clone is the real tree); `shards.py:339-340` reads the real `run.sh`, so it names a part; `tests/entities.py` `_P2_CENSUSES` rows (4396-4475) read the named script's text, so each names the part holding its phrase; `host_zone_features.py` default `--script` and its script list (nightly.yml:535 cites it as the live sweep) |
| T table or census row | 15 | 7 | re-recorded or follows the parts: `tests/closures.json`, `tests/case_closures.json`, `tools/ci/selftest_closures.json` (`tools/ci/selftest_scope.py record`), `case_select.py:55` `SCRIPTS`, `closure.py:220` `DRIVEN_BY_OTHERS`, `shards.py:93` `READERS`, and `tests/entities.py:22931/23794`, which assert the real `DRIVEN_BY_OTHERS` and `closure.affected` output |
| L live citation | 185 | 53 | rewritten one-for-one to the owning part (the part the cited check sits in, from the manifest): comments and docstrings in tests/, tools/, the 23 lines in 16 `custom_components/heatpump_optimizer` files, `.github/workflows/codeql.yml` and `tests.yml` comments, `tools/coverage/coverage_tree.sh`, `docs/architecture.md`, `dev/audit/README.md`, `tests/README.md`'s cost table, `dev/governance/dimensions/D12.md:62` (policy: the owner's review covers it), `dev/programme/HANDOVER.md`, `dev/programme/carries/carry-3881.json`, `dev/audit/config/bugclasses.json` detector strings, the instrument guides, and briefs of `wave-r11-groups.json` groups not `done` at the fixer's merge base (done groups' briefs are records and stay) |
| S data in code | 55 | 8 | left: a literal a self-test feeds itself (`merge_train.py` approval fixtures, `shards.py:332-363`, `closure.py:4717-4720`, the `tests/entities.py` mutation fixtures, `mutation_table.py` `SELFTEST_COST`), or a check name (`manual_plan.py:1643`, a test id); the split head, where tests/features.py is absent, is the check that none reads the tree |
| H closed-group harness | 55 | 12 | left: each reads tests/features.py's text at its group's pinned SHA; at a post-split tree its `open()` raises, so it exits non-zero, never green |
| B through features_block | 4 | 4 | left: works once `features_block.py` resolves the marker (class R) |
| P prose in a harness | 13 | 10 | left: comments in dated harnesses |
| D dated record | 790 | 112 | left and dropped from the `--check` enumerator by the same path rule: `dev/archive/`, `dev/audit/rca/`, `dev/audit/waves/`, recorded harness data, delivery/triage/register/round state, the r9/r10 rosters, `docs/design/<date>-*`, decisions, `rotation.json`, `card_claimed_drift.txt`, policy fixtures |

**Production comments are in this group**, as a last commit of one-for-one line rewrites: nightly.yml already puts `.github/` in the diff, so the push to main runs `full` with or without them, and no budget moves because no line is added or removed. Check at the head: for each edited production file, `ast.dump` with docstrings stripped equals the base's, and `wc -l` is unchanged; a mutation ledger `old` text is never a comment line, so no row's anchor moves.

## 4. Mutation re-key (V2: option a)

4313 rows name tests/features.py. Reach is by line (`linereach.py record`: per span, the production lines `sys.monitoring` LINE events saw; a row's lines are its anchor file's lines equal to `old`; a module-level line reaches every span whose recorded `files` hold its module). At the base (`HEAD_S=6.9 linereach.py cost`, the header's 6.9 s measured by `case_select run tests/features.py --plan <empty>`; span seconds from `tests/case_closures.json`): 747 rows are reached by one part, 3565 by several, 1 by none. Revision 2 also counted a copied T4 binding's producer as reaching the consuming part, which this monolith reading omits; the splitter measures reach by a LINE run of the written parts, which is exact, so the fixer's counts are its own.

1. **One reaching part (rule 1): driven, not re-keyed blind.** `case_select run <X> --plan <the reaching spans and their in-part needs closure>` under the mutant, killed by `mutation_table.killed` against the same plan's baseline. Cost: a ceiling of 86892 CPU-s for the 747 rows (mean 116.3, max 399.5: a plan carries its spans' in-part needs closure, which is dense), before the fail-fast stop that ends a killed drive at its first `FAIL`. A rule-1 row the drive does not kill is a **lost kill** (the monolith's kill came through another part's state): it is never re-keyed; the fixer moves or copies the reading check into X, or reports the row, and the count goes in the body.
2. **Several reaching parts:** driven per part, cheapest first, stopping at the first kill: a ceiling of 100948 CPU-s if the first candidate kills every row, 2166480 if every candidate part is driven.
3. **None:** driven against every part: 1071 CPU-s.

A fail-fast hook in the splitter's drive ends a run at the first `FAIL` (the baseline has none). `mutation_table.drive_spec` has no `--plan` form, so the drive is the splitter's, not `mutation_table --drain`. The fixer drives a seeded 200-row sample of rules 1 and 2 first, prints its CPU-s and kill shares, and extrapolates; above 100000 CPU-s extrapolated it reports to the orchestrator before the full drive (both ceilings together are 187840 CPU-s, about 1.6 h of wall-clock over 32 cores); sharding is `--shard K/N` over N = 8 four-core runners. **Perturbation, by construction:** the base's one load-bearing pair (section 1) runs through test code, so the fixer plants one in the spike's `planted/planted.py`: a span in part X calls a production function, saves its result to the stub store and checks only that a save happened; a span in part Y checks the saved value. A mutant on that function's value line (executed under X's spans only) is killed by the monolith with its `FAIL` under Y's `@@SPAN`; the rule-1 drive in X must print not killed, and the row is reported as a lost kill. N6's case (a section passing on an empty store) is the same instrument's: the drive, not the line diff, catches it.

## 5. Null controls

- Test ids: two base runs diff empty, then base against the concatenated parts, empty, `ALL N` summing; drop one span from `--write` and the diff prints it.
- Split null: each span's lines in its part equal its lines in the monolith. A span that differs here but not in the swap run is a hook miss, a defect of the instrument.
- Pins and kills: the ledger diff is `M` only and changes only `killed_by`/`reason`; per-script counts unchanged outside the parts, parts summing to the base's less the lost kills, each named.

## 6. Budgets, scopes, carries

`tests/structure_budgets.json` and `tests/mutation_budgets.json` do not move; `tests/ci_budgets.json` `script_runs_per_push` and `script_runs_full_case_pr` grow by one per added script: a raise asked of the owner before the branch is pushed, fewer parts the payment tried.

## Alternatives

- **Refuse every cross-part T5 edge** (revision 2): `--check` could never pass, since edges such as `np.sort(...)` on `np` carry no load and are never removed.
- **Join instead of sever**: a union over T5 collapses to one part of 250 spans.
- **Re-key rule-1 rows without a drive** (revision 2): a kill delivered through another part's state would be recorded against a part that does not kill it.
- **Per-span scripts; line-range or tag split**: revision 1's reasons (script-run budgets ×250; no deterministic home for a new test).

## Notes for the fixer

- D5 cells (N1): narrow s7's `tests/fe*` glob to its parts and give the rest a new seat; `python3 tools/audit/check_scopes.py --repo . --ref HEAD` prints `ok D5`. Carry: R11-OWNER-FEATURES-SPLIT (item N1)
- RNG (N4): `_rng948`/`_rng948t` and the two module seeders are swap families; the swap run shows a shifted draw before P0 edits anything. Carry: R11-OWNER-FEATURES-SPLIT (item N4)
- `np.sort(...)` reads as a mutation of `np`; it is advisory only now. Carry: R11-OWNER-FEATURES-SPLIT (item static-ceiling)
- N6: an unchanged line set can hide a check now reading an empty store; section 4's drive is its instrument. Carry: R11-OWNER-FEATURES-SPLIT (item N6)
- Swap-hook limits: a module first imported inside a span, files on disk and subprocess state are not swapped; the split null catches each. Carry: R11-OWNER-FEATURES-SPLIT (item swap-limits)

## Figures

Run from the repository root at the base, `S` the spike directory, `PYTHONPATH=tests/hastub:tests`:
- step A counts: `python3 $S/swap_run.py partition | head -1`
- difference set, before and after P0: `python3 $S/swap_run.py run plain > p.log; python3 $S/swap_run.py run swap > s.log; python3 $S/diff.py p.log s.log` (with `--script <copy> --parts $S/parts.json` for the P0-edited copy; `--drop store` for the store-unswapped run)
- one-part null: `run one`, diffed against `run plain`
- planted control: `run plain|swap|one --script $S/planted/planted.py --parts $S/planted/parts.json`
- reference classes: section 3's enumerator
- reach and drive ceilings: `python3 $S/linereach.py record lines.json; HEAD_S=<measured header s> python3 $S/linereach.py cost lines.json`
