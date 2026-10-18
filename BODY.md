_Requested by **tvofi**_

O17 item 1 (tooling) and item 2(ii), from the roster-cost pre-study the orchestrator accepted on 2026-10-18. Part of #201. No roster group lists an issue for this work, so this body closes none. The policy half is `handoff/r10-roster-carry-policy`; CodeQL is #2405.

**Owner gate.** tvofi approves at merge. The code-owned files are `.github/workflows/tests.yml`, `.claude/hooks/stop-selfcheck.sh`, `tests/lane_skip.py`, `tests/closure.py`, `tests/card_rig.mjs` and `tests/card_browser.mjs`.

**The change.**
- **Roster ref.** `roster_lib.default_roster_ref(git)` answers the round's roster branch `origin/handoff/audit-r<N>-roster`, falling back to `origin/main` with a note. It warns when main carries roster changes the branch lacks, which happens after every squash until main is merged back. The tick, `plan_table.py`, `resume_doc.py`, `handover_prompt.py` and `state_docs.py` resolve through it. The state-docs beat also watches the roster ref.
- **Level 0** (`tests/lane_skip.py`). When every changed file is a roster or a canonical delivery row, `browser`, `coverage` and `typing` skip, with no recorded proof. `fast` never takes Level 0.
- **Changed-file lists keep both sides of a rename.**
  - **Round 1.** Porcelain `git diff --name-only` lists only a rename's destination, so renaming production onto a delivery row skipped lanes.
  - **The producer.** `tests/closure.py` `changed_between` / `changed` (`--no-renames`) now feeds the gate, lane_skip and all 6 `tests.yml` list sites.
  - **Round 2.** The JS twin `card_rig.mjs` `threeDotFiles` (the card claim gate's list), `card_browser.mjs` `gridScope` and `stop-selfcheck.sh` were still porcelain. So were `policy_lint.mjs`'s `mergeRecordClass` and its autofix-merge diff. All five now pass `--no-renames`. The `card.mjs` parity pin now reads `env_drift.py`'s `three_dot_files` commands, so the twins are held together, not copied.
  - **The census, in the closure self-test.** It refuses any `git diff ... --name-only` without `--no-renames`. It covers:
    - `.github/workflows/*.yml`;
    - `tests/*.py|sh|mjs|js`;
    - `tools/pr/*.py|sh|mjs`;
    - `tools/policy/*.mjs|js`;
    - `tools/audit/seat/*.py|sh`;
    - `.claude/hooks/*.sh|mjs`.

    It joins backslash continuations before matching. It exempts empty-tree diffs, `--cached` counts, comment lines and lines marked `# rename-null-control`. Four exact allow entries cover a fixture copy, a docstring, a message string and a `policy_lint.mjs` regex over workflow text.

## Head

`0a61981e08bc55307489edd732caf5e480578c61`: the reviewed head `89d2b9465` plus one commit. Merge base with origin/main is `003c3731c`. `git merge-tree --write-tree origin/main HEAD` (`be2d3676e`) merges clean.

## Mutation proof

Each mutant edits one file in place over a committed tree, runs the named check, and is restored with `git checkout --`.
- **MB5: Level 0's guard disabled.** `python3 tests/lane_skip.py self-test` prints `44/50 pins passed` (round 1).
- **MB8: `--no-renames` dropped from `changed_between`.** `closure.py selftest` fails `3 of 122` (round 2; the reviewer re-ran it): both sides, the 0-script scope, and the census. lane_skip prints `51/54`: three `runs on a rename from production onto a delivery row`.
- **MB11: `tests/*.mjs` dropped from the census globs.** `closure.py selftest` prints `1 of 124 ... FAILED`: `the census reads .mjs`.
- **MB12: the continuation join disabled.** `1 of 124 ... FAILED`: `the census joins a backslash continuation`.
- **MB13: `--no-renames` dropped from `card_rig.mjs`'s second command only.** The parity pin's logic, driven over the real `card_rig.mjs` and `env_drift.py`, prints `FAIL`.
- **MB14: dropped from both twins' first command.** It prints `FAIL` through the pin's `--no-renames` clause.

## Null control

- A throwaway repository renames `custom_components/heatpump_optimizer/__init__.py` onto `dev/programme/delivery/99999.md`. Porcelain lists only the row, and the pin asserts browser would skip on that list. The producer lists both sides, and the lanes run.
- Over a planted root, the census refuses exactly the porcelain line in each of `x.py`, `y.mjs` and a split `z.sh`. It passes the `--no-renames` twin beside each one, and the JS comment.
- Each Level 0 skip has a twin, one non-record file away, that runs.

## Figures

At `0a61981e0`, load1 above 80, so heavy suites are left to CI:
- `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`. The round-2 head had 122.
- `closure.rename_sites()`: `([], [])`.
- `python3 tests/lane_skip.py self-test`: `54/54 pins passed`.
- `roster_lib.py --self-test`: `18 checks, 0 failed`. `orchestrator_tick.py --self-test`: `104 checks, 0 failed`. `state_docs.py --self-test`: `all checks passed`.
- `python3 tests/layout.py --guard --base origin/main`: `GUARD: 0 refusal(s)`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `score.py --diff`: `dS +0.0000 NULL`.
- `node --check` passes on the four edited `.mjs` files, and `bash -n` on the hook.
- `node tests/card.mjs` needs the plan payload from `tests/plan_view.py`, so the card suite is CI's.
- **PROJECTION, not a measurement.** A roster or row PR saves about 6.4 runner-min per head: `browser` 4.0, `coverage` 0.8, `typing` 1.5, `coverage-ratchet` 0.15, from #2380's check-runs. Re-measure on the first record-only head after merge.

## Unpinned sites

- **The `tests.yml` wiring** (`typing`'s `needs` and `if:`). No local check drives a workflow. CI on this head runs every lane; the first record-only head after merge must show three `skipped`.

## Red checks

none

## Forward-carry

- Carry: R10-TICK-DRIVERS (`dev/programme/rosters/wave-r10-groups.json`). After #2406 merges, restart the state-docs beat on main's code with no `--roster-ref` and no `--watch-ref refs/heads/main`. It then watches `origin/handoff/audit-r10-roster` too. Check it: `state_docs.py`'s memo file holds two SHAs, main's and the roster branch's. Then a roster-only commit regenerates the plan within one beat.
- Carry: R10-TICK-DRIVERS (`dev/programme/rosters/wave-r10-groups.json`). After #2405 and #2406 both merge, make the `changed` subcommand of #2405's CodeQL scope script delegate to `tests/closure.py`'s `changed_between`, so CodeQL's list has one owner. Keep the script's rename probe. Check it: `python3 tests/closure.py selftest` still passes its census, which reads `tools/pr/*.py`, and the scope script's own self-test still prints `0 failed`.

## Friction

none
