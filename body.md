The round-11 audit record. It holds the round's evidence under `dev/audit/rounds/round11/` and the register section in `dev/programme/register/audit-2026-09.md`. It also carries the folded class ledger `dev/audit/config/bugclasses.json`, with the classes the fold minted in `finding.schema.json` and in `.claude/workflows/audit-find.js`'s generated `CLASS_GUESS`, the round-11 rotation entries in `dev/audit/config/rotation.json`, and the draft roster `.claude/workflows/wave-r11-groups.json`. No production code changes. Every new file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix.

On top of the fold and the record, this head carries:
- **The P2 class sweep** (`sweep-P2.json`/`.md`, cloud box SW8), which returned after the fold. `fold_ledger.py fold --round 11` was re-run with it: P2 gains 8 `beyond_finding` seams, judged 23 + beyond 8 = N 31. The P2 draft in `ISSUES.json` lists the sweep and its `n` reads 31. A seam has one class. `config_flow.async_step_reauth_confirm` is already in N-entry-data-placement, so it moves to `sweep-P2.json`'s `notes`, just as `sweep-P11.json`'s valve seam stays in N-stale-step-actuation.
- **Two plan deviations** against `plan/r11` at `819aa2e354`, recorded in the register under "Plan deviations — round 11": (a) the P2 sweep seams, each an arm of the plan group that owns the judged finding it mirrors; (b) the late D3 intake under `J/late-D3/` (D3-s1-01, weakened, low, I2). Its verifier and judge ran in one seat, so an independent re-judge is owed before it dispatches. Until then it stays out of `JUDGE.json`, the fold and `ISSUES.json`.
- **Root-cause records for the 27 OWED classes** that `fold_ledger.py check` refused: `dev/audit/rca/R11-<class>.md` each, with an `_rca` entry of level `class` cited from the class, and the 27 `class_rca_on_record` triggers re-derived by `fold_ledger.py refresh`. Each record names a cause, a process state, a cost test with numbers and either a proposed class barrier (17) or a recorded refusal (10). No barrier is built here; each proposed one is owned by its class's fix PR. N-step-grid also carries a `barrier_refusal` for `tests/config_flow_steps.py`, which names the class and pins one selector only.

To let the record pass its own gates, it also carries:
- host paths scrubbed from 86 evidence files (`ref_privacy.py scrub`, plus four cloud-box spans by hand);
- the canonical `repo_root` in nine round-11 harnesses that walked `parents[N]` (one, `D15/s3/m9_costs.py`, resolved `dev/` instead of the root);
- the draft roster at `dev/audit/rounds/round11/wave-r11-groups.draft.json`, not `.claude/workflows/`. There the wave script reads it as a live roster, and its 57 `not-started` stages fail `wave-script`. `plan/r11` edits and cites the old path, so the plan's landing follows the rename;
- `tests/layout.json`: `dev/programme/register/` in `historical`, because a register row quotes a stale path as the finder saw it;
- the round-11 reports named by policy_lint's `named-docs` check in `dev/governance/config/corpus_excluded.json`, as round 10's were.

- two `policy_known_bad.json` entries (`SCREAMING_SNAKE`, `min_ink_gap`) removed by orchestrator decision under mandate 6893738184. They stopped firing because `D6/s5/units.tsv` quotes the symbols.

Issues are drafted in `ISSUES.json` and not filed; this PR closes none.

Owed to the owner from the root-cause records, not landed here:
- 26 of the 27 round-11 sweep files cite an enumerator that never reached origin (`git log --all` finds no commit touching any of the paths), so those class searches cannot be re-run from the tree.
- N-comment-style's proposed ratchet would be a new `*_budgets.json` key (0013).
- N-copy-style's proposed lint needs a written house style in `D4-criteria.md`.
- A sentence in `tools/audit/seat/INSTRUMENTS.md` (N-instrument-locator) and one in `fixer.md`'s test-first step (N-inverted-aggregate) are proposed, not written.
- 12 of the 27 classes hold one or two instances and are owed only because `_group_counts` pools classes minted in one round with one nearest class.

## Head

`1d727a29e14ec06e1547703c4a6d94bb7fc20fd9` adds the 27 root-cause records and their ledger entries onto `0a7ea717c6`. `0a7ea717c6` merges the `closures-autofix` bot's `8051ce8710` ("ci: re-record closures") into `5c3b0cbeeb`. `5c3b0cbeeb` adds the CI-red repairs onto `0ec3cdcbfe`: the two stale known-bad entries dropped, and the draft roster moved out of `.claude/workflows/`. The merge was automatic, with no conflict resolution.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim. `fold_ledger.py check` gave the same 27 violation lines (the OWED trigger lines) before and after the P2 fold; only its instance total moved, from 1218 to 1226. With the root-cause records it gives 0 violations, and the instance total stays 1226.

## Figures

none

## Red checks

- `governance / wave-script`, at `0a7ea717c6` (run 44308132697): `fold_ledger.py check` refused 27 OWED classes. Fixed at this head by the root-cause records. Cheaper detector: `python3 tools/audit/fold_ledger.py check`, under a second.
- `governance / policy-docs`, `governance / env-matrix`, `governance / instrument-self-tests` and `tests / fast (3.14)` (the template arm in `tests/entities.py`), at `0ec3cdcbfe`: one cause. policy_lint's `known-bad` check refused two `policy_known_bad.json` entries that stopped firing once `D6/s5/units.tsv` quoted their symbols. Fixed at `5c3b0cbeeb` by dropping both entries. Cheaper detector: `node tools/policy/policy_lint.mjs`, about 1 min locally. Scoped prepr skips it under `PREPR_SKIP_CODE`, which is the standing cost of the scoped run.
- `governance / wave-script`, at `0ec3cdcbfe`: the draft roster in `.claude/workflows/` carries 57 `not-started` stages, which the wave script does not branch on. Fixed at `5c3b0cbeeb` by moving the draft out of the roster directory. Cheaper detector: `node tools/policy/check-wave-script.mjs`, under a minute; skipped under `PREPR_SKIP_CODE` likewise.
- `tests / closures`, at `0ec3cdcbfe`: under-scoped. The round-11 harness files that `tests/harness_headers.py`'s header scan opens from a child process were missing from its `inert_reads`. The `closures-autofix` bot repaired this in `8051ce8710`, which this head carries unchanged. Cheaper detector: none on a Darwin seat box. Only CI's Linux `strace` sees a child's reads, and this repair costs one CI run.
- `tests / nightly-status`: inherited from main. It reports main's slow-run red, and no file of this PR reaches it. Cheaper detector: none, since the job reads main's own run.
- `code-scanning alert 57 (py/overly-permissive-file)` and `code-scanning alert 58 (py/overly-permissive-file)`: open on main in `tools/audit/seat/postmerge.py` and `tools/audit/seat/roster_lib.py`. This PR does not touch either file. Cheaper detector: none runs before push; CodeQL runs only in CI.

## Forward-carry

none

## Friction

none
