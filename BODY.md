_Requested by **tvofi**_

O17 item 1 (tooling) and item 2(ii), from the roster-cost pre-study the orchestrator accepted on 2026-10-18. Part of #201. No roster group lists an issue for this work, so this body closes none. The policy half is `handoff/r10-roster-carry-policy`.

**Owner gate.** tvofi approves at merge. The code-owned files are `.github/workflows/tests.yml`, `.claude/hooks/stop-selfcheck.sh`, `tests/lane_skip.py`, `tests/closure.py`, `tests/card_rig.mjs`, `tests/card_browser.mjs` and `tools/pr/codeql_scope.py`.

**The change.**
- **Roster ref.** `roster_lib.default_roster_ref(git)` answers the round's roster branch `origin/handoff/audit-r<N>-roster`, falling back to `origin/main` with a note. It warns when main carries roster changes the branch lacks, which happens after every squash until main is merged back. The tick, `plan_table.py`, `resume_doc.py`, `handover_prompt.py` and `state_docs.py` resolve through it. The state-docs beat also watches the roster ref.
- **Level 0** (`tests/lane_skip.py`). When every changed file is a roster or a canonical delivery row, `browser`, `coverage` and `typing` skip, with no recorded proof. `fast` never takes Level 0.
- **One changed-file list that keeps both sides of a rename.**
  - **The producer.** `tests/closure.py` `changed_between` / `changed` (`--no-renames`) feeds the gate, lane_skip and all 6 `tests.yml` list sites. Since this round it also feeds CodeQL: `tools/pr/codeql_scope.py` `changed_files` delegates to it.
  - **Twins.** Every twin passes `--no-renames`:
    - `card_rig.mjs` `threeDotFiles`, held to `env_drift.py` by the `card.mjs` parity pin;
    - `card_browser.mjs` `gridScope`;
    - `stop-selfcheck.sh`;
    - `policy_lint.mjs` `mergeRecordClass`, and since this round its twin `stamp.py` `merge_is_record_class`, held together by policy_lint's stamp-copy arm;
    - the seat and pr scripts.
  - **The census, in the closure self-test.** It refuses any `git diff ... --name-only` without `--no-renames`, after joining backslash continuations. It covers:
    - `.github/workflows/*.yml`;
    - `tests/*.py|sh|mjs|js`;
    - `tools/pr/*.py|sh|mjs`;
    - `tools/policy/*.mjs|js`;
    - `tools/audit/seat/*.py|sh`;
    - `tools/release/*.py`;
    - `.claude/hooks/*.sh|mjs`.

    It exempts:
    - empty-tree diffs;
    - comment lines;
    - lines marked `# rename-null-control`;
    - four exact allow entries;
    - `--cached`. A `--cached` diff does detect renames in the index. The exemption stands because each of the 6 porcelain `--cached --name-only` sites in the census globs today (`git grep` over them; all in workflows) only counts lines for an echo after a pinned restore. A new `--cached` list site would pass unseen.

## Head

`dc6cda7a2003d095e2901fc396d8fa0838054818`: the reviewed head `af391637b` plus one commit. origin/main is `55dc8d9c2` (#2405), and it is the merge base, so the branch is current.

## Mutation proof

Each mutant edits one file in place over a committed tree, runs the named check, and is restored with `git checkout --`. Rounds 1 to 3 are as reviewed: MB5, MB8, MB11 to MB14.

**This round:**
- **MB15: `--no-renames` dropped from `stamp.py` `merge_is_record_class`.** The census refuses `tools/release/stamp.py:1708`. `node tools/policy/policy_lint.mjs` exits 1 with `FIXTURE VACUOUS: recordClassPaths ["the stamp's merge_is_record_class and mergeRecordClass must both diff with --no-renames; ..."]`.
- **MB16: the same edit with `tools/release/*.py` dropped from the census.** The census gives `([], [])`, so the new glob is what reads the stamp.
- **MB17: `codeql_scope.changed_files` reverted to its own porcelain diff.** `codeql_scope.py --self-test` fails `a rename lists its source too` and `so the python leg analyzes the rename`.
- **MB18: `codeql_scope.changed_files` as a correct private `--no-renames` copy.** It prints `47 checks, 1 failed`: `the list is closure.changed_between's, not a copy`.

## Null control

- The rename probes (`closure._rename_probe_lists`, and codeql_scope's `git mv lib.py lib.md`) read the same commit two ways. Porcelain lists the destination alone, and the producer lists both sides.
- Over a planted root, the census refuses exactly the porcelain line in each of `x.py`, `y.mjs` and a split `z.sh`. It passes the `--no-renames` twin beside each one.
- MB16 is the census's own control: the stamp's porcelain line passes until `tools/release/` is read.

## Figures

All at `dc6cda7a2`:
- `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`.
- `closure.rename_sites()`: `([], [])`.
- `python3 tests/lane_skip.py self-test`: `54/54 pins passed`.
- `python3 -I tools/pr/codeql_scope.py --self-test`: `47 checks, 0 failed`. The same run under `python3.11 -I` gives `47 checks, 0 failed`; the scope job has no setup-python.
- `roster_lib.py --self-test`: `18 checks, 0 failed`. `orchestrator_tick.py --self-test`: `104 checks, 0 failed`. `state_docs.py --self-test`: `all checks passed`.
- `python3 tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`, no `VACUOUS`.
- `python3 tests/layout.py --guard --base origin/main`: `GUARD: 0 refusal(s)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/throwaway_git.py --check`: `0 ... refused`.
- The codeowners gap check (`--check`): `uncovered_files=0`.
- `score.py --diff`: `dS +0.0000 NULL`.
- The card parity pin's predicate, driven over the real `card_rig.mjs` and `env_drift.py`: `PASS`. `node tests/card.mjs` needs a Home Assistant payload, so the card suite is CI's.
- **PROJECTION, not a measurement.** A roster or row PR saves about 6.4 runner-min per head: `browser` 4.0, `coverage` 0.8, `typing` 1.5, `coverage-ratchet` 0.15, from #2380's check-runs. Re-measure on the first record-only head after merge.

## Unpinned sites

- **The `tests.yml` wiring** (`typing`'s `needs` and `if:`) and **the CodeQL scope job's import of `tests/closure.py`**. No local check drives a workflow. CI on this head runs every lane and the `scope` job; the first record-only head after merge must show three `skipped`.

## Red checks

none

## Forward-carry

- Carry: R10-TICK-DRIVERS (`dev/programme/rosters/wave-r10-groups.json`). After this merges, restart the state-docs beat on main's code with no `--roster-ref` and no `--watch-ref refs/heads/main`. Check it: the memo holds two SHAs, main's and the roster branch's, and a roster-only commit regenerates the plan within one beat. The CodeQL delegation carry is done in this PR, so the orchestrator drops it from that group.

## Friction

none
