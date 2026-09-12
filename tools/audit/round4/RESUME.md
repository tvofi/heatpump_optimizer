# Round 4 — resume state

**What this file is.** The durable, continuously-updated state of audit round 4,
so a session that did not run it can pick it up cold. It is not the living
handover: `docs/HANDOVER.md` is that, one per tree, and `writing-for-agents.md`
forbids a second. It is not #201 either — #201 carries volatile state and a
pointer to this file, and nothing is written to both. This file carries what the
round knows; #201 carries which seats are alive right now.

**Where the round is.** Finder wave 1 has run. Wave 2 has not been dispatched.
Nothing is verified, nothing is judged, no issue is filed, no register section is
written.

## The fixed facts

| | |
|---|---|
| round | 4 — rounds 1-3 are closed and archived at `d5d8c4a` |
| baseline | `7dd68dd327fe3dbfb09f3bd0fe38910c58877697` (= `origin/main` at the round's start, v6.4.2) |
| dimensions | 13. `7dd68dd` added D12; `audit-find.js`'s `DIMS` already carries it |
| branch | `claude/13-dimension-audit-920935`, pushed — the round's evidence is committed here, not only on disk |
| repo definition of a round | `CLAUDE.md` → `tools/audit/README.md` → `.claude/workflows/audit-find.js`: finders → quiet window → dedup → `/audit-verify` panel → judge → issues → fix waves |

## The five finder trees

Prepared by `tools/audit/prepare_baseline.sh 4 7dd68dd`. They are **on disk and
not in git**; the evidence is copied into this branch under
`tools/audit/round4/` as each finder lands, and that copy is what survives.

| tree | dims | kind |
|---|---|---|
| `.claude/worktrees/audit-r4-baseline` | D1 D2 D4 D5 D6 D7 D8 D10 D12 | `git archive` export, no `.git` |
| `.claude/worktrees/audit-r4-D0` | D0 | detached worktree |
| `.claude/worktrees/audit-r4-D3` | D3 | detached worktree (commits its mutants, so its HEAD moves off the baseline) |
| `.claude/worktrees/audit-r4-D9` | D9 | detached worktree |
| `.claude/worktrees/audit-r4-D11` | D11 | detached worktree, `.git` and the API on purpose |

`tools/audit/worktree_gc.sh` does **not** threaten them: it deletes only a
worktree that is clean including untracked, and each carries an untracked
`round4/<dim>/BASELINE.md` plus the round-3 deletions. The export is not a
worktree at all.

## Environment, measured on this box

- python `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` — numpy 2.4.6, scipy 1.17.1. Always `PYTHONPATH=tests/hastub`, always from a tree root.
- node v20.10.0. Playwright 1.49.0 already at `/private/tmp/hpo-pw/node_modules`; Chromium `chromium-1148` under `$HOME/.cache/pw-browsers`. Do not install again.
- drift cache warm at `~/.cache/heatpump_optimizer/` (32 MB).
- gate lock free at the round's start; take it with `tests/gate_lock.py`, never `mkdir` and a shell pid.
- `gh` authenticated as `tvofi`.

## What has already been done, and must not be redone

**Two defects in the round's own instrument, fixed and committed** (`ea8c14b`),
both arms executed — see the commit body for the numbers:

- `prepare_baseline.sh` deleted `RELEASE_NOTES.md`, which `tests/entities.py:12140` reads unguarded at import. The export ran 0 of 1360 entity checks; repaired, it runs 1360.
- The same script put 116 round-3 files, `ledger/verdicts.tsv` among them, into every finder tree, against `COMMON.md`'s wall. `strip_earlier_rounds` removes every round but the new one.
- `finders_can_start` is the general refusal that would have caught the first, demonstrated failing and passing.

**Box hygiene.** Two orphaned busy-loop shells from an aborted round-3 D4 load
experiment (parent `launchd`, 25 h, ~98 % CPU each) were killed before dispatch.
Any timing number taken before that is contaminated.

**Coordination.** Intent and both instrument defects posted to #201
(`5645447877`), read back byte-identical.

## Known export artefacts — do not report these as findings

`PYTHONPATH=tests/hastub python3 tests/entities.py` in the export reports
`3 of 1360 ENTITY CHECKS FAILED`: the two handover checks and the `updated-for:`
ancestry check. All three need `.git`, which the export does not have. The same
command in a real checkout passes 1360 of 1360.

## Per-dimension status

`landed` = the finder returned its JSON and its report and harnesses are copied
into this branch. `written` = a REPORT.md exists in the finder tree but the
seat's JSON has not been received here.

<!-- STATUS TABLE START -->
| dim | subject | status | findings |
|---|---|---|---|
| D0 | price optimality | running (wave 1) | — |
| D1 | robustness and stability | **landed** | 2 high — `price_model.from_dict` accepts a non-finite shape bin, pricing 4 of 96 planning steps at 0.0 SEK/kWh (control 0.6018, null control 0); one corrupt scalar in the accuracy store raises in `_async_load_accuracy` and the next cycle overwrites 3 of 3 learned fields with zero log lines |
| D2 | mathematical and physical sanity | **landed** | 5 findings. 2 high — `tariff._smooth_topk_sum` bisects on a bracket not scaled by its own logistic temperature, charging up to 13.35x the top-k bill it approximates above 5.84 kW excess (null control: exact below the break point); `thermal_model.wood_share` is discontinuous at `hp_temp == flow_set` where its docstring claims continuity, 0.9985 of the emitter draw across 2e-6 degC, and one ulp of step-0 power moves 1.110 kWh. 2 medium — every DSO catalog row writes a peak-hours mask that discounts 0 of 672 windows because `apply_catalog` omits the off-peak factor; modelled COP goes below 1.0 in 51 of 328 cells and inverts with rising outdoor below -21 degC. 1 low — grid-fee decimal commas unreachable, `parse_rules` splits on the comma `_parse_rule` converts. sysid bias and DST not measured |
| D3 | test-suite gaps | written | — |
| D4 | UI/UX | not dispatched (wave 2) | — |
| D5 | docs structure, flow, comments | **landed** | 2 hygiene — `docs/configuration.md`, the reference README promises documents *every* field, names 15 of 200 shipped options fields nowhere (34 occurrences); `tests/README.md:356` says 48 stress combinations, `sweep_combinations()` returns 51. Seven claims tagged `for D6`. Clean with positive controls: 0 broken links, 0 duplicated paragraphs over 433, 0 dead ends over 337 tokens |
| D6 | documentation claim verification | **landed** | 125 claims extracted, 125 checked, 12 false, 1 unverifiable. 1 high — `docs/architecture.md` stale in ten claims including its HA boundary (21 modules import `homeassistant` at module level, 11 outside the ten it names). 1 medium — Sensor-Gap Euro Advisor documented `CUR`, publishes no unit. 1 low — `docs/automations.md` states a Power Headroom precondition the code does not enforce |
| D7 | architecture and maintainability | **landed** | 3 findings. 1 high — `_learning_frozen` never consults `_pump_signals.defrosting`, so 3 of 4 learners fold a defrost interval (perturbation drives it to 0; three other contaminants read 0). 2 medium — the sysid experiment is adopted in 0 of 18 cells because the identifier fits one state to a two-state plant (null control on a collapsed plant: adopted at 0.940); `_sizing_model` uses default slab constants for every house, breaching `max_excursion_c` in 6 of 18. Brief item 5 (this years train) not done |
| D8 | sensor verification and ordering | not dispatched (wave 2) | — |
| D9 | CPU and memory efficiency | not dispatched (wave 2) | — |
| D10 | HA quality scale | written | — |
| D11 | governance and policy | running (wave 1) | — |
| D12 | generalization | written | — |
<!-- STATUS TABLE END -->

## What the next session does, in order

1. **Collect wave 1.** For every dimension marked `written`, read its
   `REPORT.md` in this branch and record its findings in the table above. A
   finder's JSON is preferable but a report is sufficient.
2. **Dispatch wave 2 — D9, D4, D8.** `audit-find.js` puts them in their own wave
   for a reason: D9 measures timing and D4 drives Chromium, and
   `tools/audit/README.md` forbids the Chromium finder sitting beside the
   compute-heavy ones. D9 works in `audit-r4-D9`, D4 and D8 in the export. The
   dispatch prompt is `audit-find.js`'s `finder` template plus the tree, the
   interpreter, and the two lines about `BASELINE.md` and the known export
   artefacts above.
3. **Quiet window.** Nothing else on the box. `python3 tests/gate_lock.py take
   --label quiet-r4`. Re-execute every harness behind a `provisional` finding
   exactly as its header says, print `load1` and `swapins` beside every RESULT,
   and run the full `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=7dd68dd
   GATE_JOBS=1 ./tests/run.sh` for at most six of D3's prescreened survivors.
   Write `tools/audit/round4/QUIET.md`.
4. **Dedup** into a Round 4 section of `docs/audit-2026-09.md` — the register
   has Round 1 and Round 2 sections and **no Round 3 section**, which is itself
   worth a row somewhere. Classify each finding new / corroborates open issue #N
   / regression of a released D-id.
5. **Verify** (`/audit-verify`: three verifiers per finding, majority-refute
   kills) then the judge, who re-measures and voids any harness whose number
   does not move under its own perturbation.
6. **Only then** file. `CLAUDE.md`'s ruling binds every seat: fix it; if you
   cannot, verify it independently; only then file it. An issue enters the
   Delivery-status table and propagates further than a wrong pull request.

## Traps this round has already paid for

- A finder's tree must not carry an earlier round's ledger. Fixed in the script; check it, do not assume it.
- `tests/entities.py` reads `RELEASE_NOTES.md` unguarded at import. Any future export trimming must keep it.
- The D3 worktree's HEAD is **not** the baseline: it commits mutants so `env_drift.py` has a ref that is not `HEAD`. Compare against `7dd68dd`, never against that worktree's HEAD.
- Timing taken while ten finders share an 8-core box is provisional by contract, not by preference.

<!-- Update this file in the same commit as whatever it records. -->
