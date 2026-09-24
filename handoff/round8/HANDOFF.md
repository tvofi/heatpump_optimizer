# Round 8: hand-off to a local seat

Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82. 14 dimensions, 27 finder seats, 1 verifier per dimension, 1 common judge (the owner's panel shape).
43 findings -> judge: 29 verified, 10 weakened, 3 refuted, 1 merged. 39 survive; D0-s1-01 duplicates the owner's refusal #1293, so **38 are filed**.
Severity of the 38: 5 high, 12 medium, 21 low; 0 critical.

## Step 1: file the issues as tvofi
The cloud MCP files as claude[bot] (it filed #1511 that way). Run on the Mac with gh as tvofi:
`python3 handoff/round8/file_issues.py --dry-run` then without the flag. It refuses any other login, creates the `round-8` label, files `issues.json` (bodies already carry the dedup citations), writes `issues-filed.json`, and closes the bot copy #1511 pointing at its tvofi re-file.

## Step 2: the register PR (hpo-author via app_push.sh; fix review; approval; merge as tvofi --match-head-commit)
- `docs/audit-2026-09.md`: a round-8 section with the table below, the issue numbers from issues-filed.json, and the instrument notes.
- Evidence: `evidence/` here is the judge tree's merged `tools/audit/round8/` (finders, verifier, judge incl. JUDGE.json/JUDGE.md). Commit it under `tools/audit/round8/` following the round-7 precedent for harness classification (round 7 kept harness .py out of the tree because of closure classification; every new tracked file must be in a closure or on tests/closure.py's INERT list).
- One #201 comment and a docs/delivery row per the delivery-status rule.

## Verdicts
| id | verdict | severity | class | production | disposition |
|---|---|---|---|---|---|
| D0-s1-01 | verified | low | hygiene | yes | not filed: duplicate of #1293 (owner refusal, also #920/#826) |
| D1-s1-01 | verified | medium | bug | yes | file |
| D1-s1-02 | verified | low | bug | yes | file |
| D1-s2-01 | weakened | medium | bug | yes | file |
| D1-s3-01 | weakened | medium | bug | yes | file |
| D2-s1-01 | verified | medium | bug | yes | file |
| D2-s1-02 | verified | low | bug | yes | file |
| D2-s2-01 | verified | high | bug | yes | file |
| D2-s2-02 | verified | high | bug | yes | file |
| D3-s1-01 | verified | medium | bug | no | file |
| D3-s1-02 | weakened | low | bug | no | file |
| D3-s2-01 | weakened | low | hygiene | no | file |
| D3-s2-02 | verified | low | hygiene | no | file |
| D4-01 | verified | medium | bug | yes | file |
| D4-s2-01 | verified | low | hygiene | yes | file |
| D5-s1-01 | verified | low | hygiene | no | file |
| D5-s2-01 | verified | low | hygiene | yes | file |
| D6-s1-01 | verified | low | hygiene | no | file |
| D7-s1-01 | verified | medium | bug | yes | file |
| D7-s1-02 | verified | medium | bug | yes | file |
| D7-s1-03 | verified | medium | bug | yes | file |
| D7-s2-01 | verified | low | hygiene | yes | file |
| D7-s2-02 | verified | low | hygiene | no | file |
| D7-s2-03 | verified | low | hygiene | no | file |
| D8-s1-01 | weakened | low | bug | yes | file |
| D8-s2-01 | refuted | none | hygiene | no | not filed: A code-reading metric with no runtime consequence; refuted with a number. |
| D8-s2-02 | weakened | low | bug | yes | file |
| D9-s1-01 | verified | low | hygiene | yes | file |
| D9-s1-02 | refuted | none | hygiene | no | not filed: Re-taken on the idle box. The solve starves the loop less than any pure-Python executor job, and removing the yield rais |
| D9-s2-01 | weakened | low | hygiene | no | file |
| D10-s1-01 | verified | low | hygiene | yes | file |
| D10-s1-02 | verified | low | hygiene | yes | file |
| D10-s2-01 | refuted | none | hygiene | no | not filed: The 515 comes from running mypy against the untyped test double, which the repo's own ruler refuses; the pinned census i |
| D11-s1-01 | weakened | high | bug | no | file |
| D11-s1-02 | merged | medium | bug | no | merged into D11-s2-01 |
| D11-s1-03 | verified | low | bug | no | file |
| D11-s2-01 | verified | high | bug | no | file |
| D11-s2-02 | verified | high | bug | no | file |
| D11-s2-03 | verified | low | hygiene | no | file |
| D12-s1-01 | weakened | medium | bug | yes | file |
| D12-s1-02 | verified | medium | bug | yes | file |
| D13-s1-01 | weakened | low | hygiene | no | file |
| D13-s1-02 | verified | medium | bug | no | file |

## Instrument notes (judge)
Also in JUDGE.json (instrument_notes) and JUDGE.md. (1) orjson is not installed in the audit environment and is missing from BASELINE.md's pins. As a result, tools/audit/round8/D8/s1_finite_boundary.py silently falls back to a stub that counts every non-finite float as a serialisation failure, while real orjson 3.12.0 writes NaN/Inf as null. The judge installed orjson into a private --target dir (/home/claude/audit-r8/tmp/judge/pyorjson) to re-measure, and D8-s1-01 was weakened on that result. (2) Seat temp roots are hard-coded in D3/s1_claimkill.py, D3/v1_suite_mutants.py, D9/s2_gate_blind.py, D9/s2_cycle.py, the D9/s1_cycle.py and D9/v1_gil.py headers, and D3/s1_cachekey.py's HPO_PLANDATA arm. The judge ran sed-rewritten copies under /home/claude/audit-r8/tmp/judge/. The harness contract should require roots derived from TMPDIR. (3) Several perturbations edit production files on disk: D0 s1_budget_perturb.sh, the D3 claimkill/suite-mutant/s2 harnesses and the D4 CSS edit. A concurrent run in the same tree then imports the edited file. The judge's first D2-s1-01 run overlapped the judge's own D0 ftol edit; that run was discarded and a clean re-run gave identical numbers. The contract should prefer in-memory perturbation or require the gate lock for on-disk edits. (4) Some finder perturbations are inert or tautological. D10-s2-01's is inert (it adds an unused import: 515 -> 515, so the harness is void). D11-s1-02's and D9-s2-01's --make-perturbed edit the table the metric reads. D0-s1-01's turns production into the comparison arm. D2-s2-02's perturbation is an input attribute; the judge added tools/audit/round8/D2/judge_price_unit_fix.py. D8-s2-02's harness is a static read whose stated direction contradicts its own edit; the judge wrote tools/audit/round8/D8/judge_probe_default.py. Three observed values are stale: D7-s1-02 (2, not 1), the D7-s2-01 sentinel (14, not 12) and D1-s3-01 (the finder's guard gives 1, not 0). (5) Harness output breaks the contract in three places. D1/s3_openmeteo_hostile.py prints no load1, thread_factor or swapins. D1/s2_ledger_fuzz.py prints a hard-coded thread_factor. D9/s1_cycle.py does not subtract the deliberate executor thread's CPU, so its thread_factor reads 1.09-1.19 on the idle box. (6) The D8-s2 harnesses read source text instead of hooking a production symbol. D5/s1_stepnum.py's node regex truncates labels at <br/>, so it counts 3 mismatches where there are 4. (7) The D10-s2 finder ran mypy --strict with tests/hastub on the path, which is the exact setup tests/typing_ruler.py refuses. The baseline's pinned typing job (job 107333392110) passed against a recorded census of 0. (8) Live GitHub data moved between the panel and the judge: open PR #1508 appeared, and v1_latest_order.py's null went from 0 to 1. Unauthenticated api.github.com works for check-runs and rulesets, but /rate_limit returns 403 in agent sessions. (9) pip download writes into the cwd, so the judge's orjson probe left a wheel in the tree root. It was removed at once and git status is clean. (10) Finding ids use two shapes (D4-01 vs D4-s2-01) and were not validated against finding.schema.json. The judge could write .md files. Every production file is byte-identical to the baseline: git status shows only the deletions made by the round preparation, plus the untracked tools/audit/round8/.

Also: tools/audit prepare_baseline.sh strips round-4 files that tests/entities.py opens unguarded (round4/D11/*.py, round4/D6/claims.json), so its own finders_can_start check refuses its own output; seat-scoped ids (D1-s1-01) fail finding.schema.json's ^D[0-9]+-[0-9]{2}$ pattern.
