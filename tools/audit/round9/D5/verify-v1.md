# D5 round 9 — verifier V1 (reproduce)

Box G4-V1. Unit D5: D5-s1-01..06 and D5-s2-01..03.

## Environment
- Worktree: `handoff/audit-r9-evidence` at 6f51db2 (baseline 1936d5ca plus the round-9 evidence).
- Python: `/home/claude/venv/bin/python` (CPython 3.14.0rc2, the CI pins), run with `PYTHONPATH=tests/hastub`. It stands in for the headers' venv314.
- Node: v22, with a private `HPO_PLANDATA` from mktemp.
- Load: load1 0.41–2.03; thread_factor 1.000 on every run. Every metric is a count or a ratio, so contention does not affect it.
- No mutation work and no gh.

## Exposure
The first draft of `md_tables_marked.mjs` globbed `docs/*.md`. Its output incidentally printed rendered lines from `docs/audit-2026-09.md`, the register.
- None of that output was used.
- The harness was narrowed to the finder's 8 files before the number was taken.
- The judge should know the register was touched in this way.

## Harnesses (under `tools/audit/round9/D5/verify-v1/`)
- `indep.py`: independent cross-checks for s1-01, s1-02 and s2-03.
- `md_tables_marked.mjs`: a second GFM renderer (marked@14) for s1-04. Run it with:
  `T=$(mktemp -d); npm install --prefix "$T" marked@14; NODE_PATH=$T/node_modules node tools/audit/round9/D5/verify-v1/md_tables_marked.mjs`

## D5-s1-01: Initial setup describes the pre-v6.6.5 flow — verify, medium
- **Re-run (`setup_section.py`):** `stale_facts`=4, made of `menu_entries`=3, `named_in_section`=0, `first_screen_accepted_without_token`=1 and `doc_claims_token_required`=1.
- **Perturbation:** 1.
- **Entity count (`entity_counts.py`):** 75 entities constructed. configuration.md:196 says 74 while README:417 and architecture.md:37 say 75, so 1 claim disagrees. Dropping one sensor gives 74, and then 2 claims disagree.
- **Independent check:** choosing Tibber without a token returns the `user` form with `tibber_token_required`, so the token is required only for that price source. The three finish_setup labels from en.json appear 0 of 3 times in the section.
- **Attacks:**
  - FakeHass: the flow's return dicts are pure, so the stub does not decide the result.
  - The doc contradicts itself: :468 already says the token is not required.
  - Leave-one-out gives 3.

## D5-s1-02: Quick setup promises storage physics its answers cannot produce — verify, medium
- **Re-run:** 2. **Perturbation:** 0. **Null arm (valve set):** 0.
- **Independent check:** over `derive(buffer yes)`, `buffer_is_store` is True for the manual, smart_read and smart_write valve modes. It is False only for `none`, which is the mode derive leaves.
- **Gates:** both promised features depend on a throttling valve. setup.md never mentions the valve.
- **Caveat:** this is one scenario. An entry that already has a valve, going through the options-flow Quick setup, honours both promises.

## D5-s1-03: the card version is said to lag the integration — verify, low
- **Re-run:** share 1.00. **Perturbation:** 0.00.
- **Independent check:** CARD_VERSION equals VERSION on the last 8 stamped releases (8 of 8).
- **Why:** stamp.py:1466 calls `rewrite_card_version` unconditionally. RELEASE_NOTES.md:1416 records it (#265).
- **Doc:** dashboard-card.md:572-579 is stale.

## D5-s1-04: 9 misrendered lines in configuration.md — verify, low
- **Re-run (markdown-it@14.1.0):** 9 lines: rows 185-187 orphaned and 633-638 swallowed. **Perturbation:** 0.
- **Independent check:** marked@14 over the same 8 files gives the same 9 lines.

## D5-s1-05: 5 field labels the forms do not show — verify, low
- **Re-run:** 5. **Perturbation:** 4. **Null control:** 24 pages resolved.
- **Independent check:** grep of en.json:
  - "Inter-zone transfer" and "Solar forecast source" are absent.
  - "Radiator Power Fraction" appears only as an entity name (en.json:2035).
  - "floor return temperature" appears only inside a description.

## D5-s1-06: 5 wood fields no doc names — verify, low
- **Re-run:** 5 of 62 fields across 12 services. **Perturbation:** 0.
- **Independent check:** each `wood_*` key has 0 hits in the docs. The table says 16 fields; the prose lists 11.
- **Mitigation:** services.yaml and en.json describe all five fields, so the finding stays low.

## D5-s2-01: card comments cite 12 private members the card no longer has — verify, low
- **Re-run:** 12 names, 17 mentions. **Perturbation:** 5 names, 6 mentions.
- **Independent check (`grep -w`):** each name appears only on comment lines. 7 of them have a successor without the underscore.
- **Outside the stated property:** tests/card.mjs carries the same stale names in its comments.

## D5-s2-02: three comments cite a number the code does not deliver — verify, low
- **Re-run:** 3. **Hold controls:** 0 of 5 fail. **Perturbation:** 0.
- **Independent check:**
  - `DERATE_MIN` is 0.55 (defrost.py:112).
  - `DEFAULT_OPTIMIZATION_INTERVAL` is 30 (const.py:1321).
  - The interval selector is `_number(10,120,5)` in both flows, and no service writes the interval.
- **Attack:** the "15 minutes" row is the weakest, because a user can choose 15. Leave-one-out gives 2.

## D5-s2-03: the DHW_COLD_WATER_TEMP comment describes a coupling that does not exist — verify, low
- **Re-run:** 46 of 47. **Perturbation:** 0 of 47.
- **Independent check:** the cold end is 10.00 C at defaults, and 6.00 C with a live inlet sensor at 6.0 C. All three `dhw_coil_draw_reduction` call sites pass `p.dhw_inlet_reference`.
- **Attack:** the grid overstates reach, because at defaults the constant and the draw agree. The comment's claim is still false in code: the constant is only a default argument.
