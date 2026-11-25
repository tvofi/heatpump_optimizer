# Class sweep I5 -- docs, comments or a checklist drift stale against the code

Round 11, PLAN phase D, D14 method steps 3-4. Baseline `handoff/audit-r11-register` at `28b864af6d`.
Class status in `dev/audit/config/bugclasses.json`: **barriered** (`tests/doc_claims.py` on the PR gate). Its
recorded unreached shapes include comment drift in code (D5-s2-51); this sweep measures that gap.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-I5/dangling_refs.py .` lists every comment, docstring or `.md`
line in a tracked file that names a repository file (`.py .sh .mjs .js .tsv .yaml .yml`) whose basename no
tracked file carries. History directories are out of scope: `dev/audit/rounds/`, `dev/audit/rca/`,
`dev/audit/harnesses/`, `dev/archive/`, `dev/programme/`, fixtures and golden files.
The baseline listing is `D14/sweep-I5/baseline.out`.

| control | result |
|---|---|
| baseline | `seams=176` over 73 files |
| null (clean fixture: a comment naming a file that exists) | `seams=0` |
| perturbation (one line `# see tools/never_existed_zz.py` appended to `tools/audit/seat/ledger.py`) | 176 -> 177; reverted |
| positive control | re-finds the dangling-name seams of D5-s6-02 (`replay_draws.py`), D5-s6-05 (`update_pr.sh`), D5-s6-06 (`roster_lib.py`), D5-s6-07 (`plan_table.py`), D5-s5-04 (`open_pr.sh`) and D5-s8-05 (`tests/card.mjs`) |

**The positive control is partial.** This enumerator covers one shape: a file name that does not resolve.
The other 33 findings have other shapes, and their finder harnesses under `round11/D5`, `D6`, `D10` and
`D11` measure them:
- a stated count or number against the code: D5-s10-03, D5-s2-08, D5-s6-01, D6-s1-01/02, D6-s2-01
- a behaviour claim against a run: D5-s2-09, D5-s3-02, D5-s6-04, D6-s5-*, D6-s7-*
- duplicated text: D5-s2-01, D11-s2-04
- checklist rows: D10-s1-06, D10-s3-01/02

No single mechanical enumerator lists all of them. That is the class's
`mechanism_note` ("stretched"). The barrier `doc_claims.py` covers the count and value shapes for the reader
corpus only (README, docs, blueprints), not `tools/` or `tests/` comments.

## Disposition of the 176 seams (by file)

**Instance, beyond the findings (1):**
- `tools/policy/check-wave-script.mjs:702-705` cites `yield_rounds.py` and
  `tools/audit/round7/D13/class_vocabulary.mjs`. Neither path exists. The harness is at
  `dev/audit/rounds/round7/D13/class_vocabulary.mjs`, and the tracked reader is `yield_rounds.mjs`.
  Probe: `test -e tools/audit/round7/D13/class_vocabulary.mjs` exits 1.

**Instance, judged finding sites (6):** `replay_draws.py:6`, `update_pr.sh:2`, `open_pr.sh:2`, `plan_table.py:205`,
`roster_lib.py:9,79,658`, `tests/card.mjs:501,3743,3794`. Each probe is in `sweep-I5.json`.

**Not applicable (the rest).** Each of these was read in context:
- **Another repository.** `modbus_prefill.py:6`, `device_prefill.py:151,154`, `docs/configuration.md:549-550`,
  `tests/config_flow_steps.py`, `tests/features.py` and `tools/devices/gen_device_fixtures.py` name files in
  the tuya_heat_pump repository, and say so.
- **Upstream Home Assistant paths.** The three `tests/hastub/` modules cite them.
- **Attributed history, with a SHA, a tag or the words "replaced/retired".**
  - `budget-raise-gate-rerun.yml` in `budget-raise-gate.yml:21`, `gate-sweep.yml:6`, `budget_raise_gate.py:57`
    and `round4/D11/governance_cost.py`
  - `record_status.py` in `tests/closure.py` and `tests/delivery_status.py`
  - `merge_train.py:108` (the round-9 scripts it replaced), `gate.py:9` (`@1371a0a6`), `debug_ingest.py:4` (`@eae236d66`)
  - `ci_critpath.py:12`, `family_splits.py:3`, `beat_jobs_selftest.py:609`, `cloud_relay.sh:84` and its `.md`
  - `daemonize.py:10`, `archscore/ABOUT.md:171,186,298` (owned by named round seats), `dev/audit/README.md:287`
    ("at SHA d5d8c4a"), the design note's spike script, `tests/features.py:695,71669`
- **Runtime or out-of-tree artifacts, documented as such.**
  - `events.tsv`: `ledger.py`, `beat_jobs.py`, `orchestrator_tick.py:1152`, the ledger instrument page
  - `merges.tsv` and `tokens.tsv`: `round_metrics.py`, `scorecard.py`
  - `ci-metrics-fast.tsv`, `provenance.tsv`, `INVENTORY.tsv`, `jobs.tsv`/`status.tsv`, `ROWS.tsv`, `FILE.tsv`
  - `scorecard.py:109`, `yield.py`: read from `../study/work/` at run time
  - `cloud-setup.sh:196` names plugin hooks
- **Fixture or example names in a test's own comment.**
  - `tests/entities.py`, `tests/layout.py`
  - `tools/audit/seat/mutant_run.py`, `r10_deeplink_mutants.py`, `tools/pr/prepr.sh` (`zz_planted*`, `lib.py`,
    `ev/midrun.sh`), `ci_predict.py`, `codeql_scope.py`, `app_push.sh`
  - `agreement*.mjs/py`, `check_scopes.py`, `text_ledger.py`, `tmp_paths.py`, `carry_audit.py`, `product_reads.py`,
    `bus.sh`, `ancestry_calls.sh`, `pr_args.sh`, `doc_claims.py:4203`, `governance.yml` (`subprocess.py`/`json.py`
    shadowing)
  - `brief_lint.mjs` (illustrative names), `docs/dashboard-card.md` (`Chart.js`, a library)

Guarded: none of the 176 are guarded. No gate script resolves file names cited in code comments
(`brief_lint.mjs` does this for wave briefs only).

## Barrier proposal

Promote `dangling_refs.py` to a `tests/` arm that runs on a PR's touched files and skips lines that carry a
history marker (a SHA, "replaced", "retired", "round N", or another repository's name). It is a pure file scan:
the whole tree takes under 2 s, and the touched-file mode takes milliseconds. It closes the "comment drift in code"
gap that `bugclasses.json` records as unreached, for the dangling-name shape only. Under the instrument freeze,
this goes to round-end proposal triage. It is not built mid-round.
