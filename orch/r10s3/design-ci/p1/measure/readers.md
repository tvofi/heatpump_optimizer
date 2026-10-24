# Readers of `.github/workflows/tests.yml` job names

Tree: `origin/main` at `07a09406a` (Merge pull request #2401). Read-only survey; nothing in the repo was modified.

## Ground facts about the job names

- **No job in tests.yml has a `name:` key.** Each check-run name is the job id. Matrix jobs add a suffix: `fast (3.14)` (matrix `python-version: ["3.14"]`), `mutation-pins (N)` (matrix `shard` from `needs.mutation-pin-plan.outputs.shards`), `nightly-ha (2025.2.0)` / `nightly-ha (stable)` (matrix `image`). tests.yml:224-229 notes that a matrix job skipped by a job-level `if:` reports as plain `fast`.
- Workflow name: `Tests` (tests.yml:1).
- The id `cancel-superseded` is **also a job id in `.github/workflows/codeql.yml:100`**. Both workflows produce a check run with that name.
- `.claude/rules/*.md` and `.cursor/rules/*.mdc` are generated copies of `dev/governance/rules/*.md`. Each hit in one appears in all three; this report lists the canonical one and marks it "(+ .claude/.cursor copies)".

Legend for each reader: **asserts** (a test or lint fails if the name or its structure is missing or changed), **keys** (runtime behaviour branches on the literal name), **doc** (prose or comment only). "fixture" means a self-test fixture string that does not read the real workflow.

## Exact commands used (reproducible)

```sh
cd <repo checkout>
S="tools tests .github dev/governance .claude CLAUDE.md AGENTS.md .cursor/rules dev/programme/HANDOVER.md"
X=(':!.github/workflows/tests.yml' ':!tests/mutation_ledger/survivor_triage')

# 1. distinctive ids: word-boundary aware, with hyphen counted as a word char so that
#    `mutation` does not match `mutation-pins` and `closures` does not match `closures-autofix`
for j in cancel-superseded recheck-gate coverage-ratchet mutation-pin-plan mutation-pins mutation-nightly \
         mutation-ledger mutation-ledger-push nightly-ha nightly-status graders-head-copy lane-proofs \
         closure-scope composed-proof ci-ratchet closures-autofix claims-autofix mutation-autofix record-autofix; do
  echo "=== $j"; git grep -nP "(?<![\w-])$j(?![\w-])" -- $S "${X[@]}"
done

# 2. ambiguous ids: only quoted / backticked / needs. / jobs. / matrix-suffixed / dict-key forms
for j in fast browser briefs typing coverage mutation slow closures; do
  echo "=== $j"
  git grep -nP "([\"'\`]$j( \([^)]*\))?[\"'\`]|needs\.$j\b|jobs\.$j\b|\[\"$j\"\]|\b$j \(3\.1[34]\)|\b$j \(\*\)|'$j':|\"$j\":)" -- $S "${X[@]}"
done   # then filtered by hand: dropped "closures" JSON-key hits (tests/closures.json table key), ast "typing" module, policy_lint check names, etc.

# 3. targeted greps
git grep -n 'governance-workflow-jobs'
git grep -nE 'autofix_allowed|loop_subject'
git grep -nE "ci: (re-record closures|drop inherited claims|pin killed mutants|merge main|record nightly kills|record delivery rows)" -- ':!*.json'
git grep -n 'required-contexts'
git grep -nw 'recheck' -- tools tests .github .claude dev/governance ':!.github/workflows/tests.yml'
git grep -n 'recheck=true'
git grep -ln '_TESTS_YML\|workflows/tests.yml\|tests_workflow' -- tests tools .claude dev/governance
grep -nE 'workflow_run|workflows:|Tests|tests\.yml' .github/workflows/{budget-raise-gate-rerun,pr-contract-rerun,merge-main,budget-raise-gate,release,pages,arch-score,codeql,hassfest,validate,governance}.yml
grep -noE '_workflow_job\((_TESTS_YML|_tests_workflow|_AH_TESTS_YML)[^,]*, *"[a-z-]+"\)' tests/entities.py | sort | uniq -c
python3 -c "import json;d=json.load(open('tests/closures.json'));print({k:sorted(s for s,v in d[k].items() if '.github/workflows/tests.yml' in v) for k in ('closures','inert_reads')})"
```

Count of raw hits from command 1/2, before hand filtering (lines / files): cancel-superseded 6/3, recheck-gate 6/5, coverage-ratchet 4/2, mutation-pin-plan 9/2, mutation-pins 30/8, mutation-nightly 24/7, mutation-ledger 29/6, mutation-ledger-push 18/4, nightly-ha 40/9, nightly-status 51/18, graders-head-copy 16/4, **lane-proofs 0/0**, closure-scope 29/11, composed-proof 20/6, ci-ratchet 15/3, closures-autofix 55/13, claims-autofix 33/15, mutation-autofix 53/16, record-autofix 21/9.

### A structural hazard that applies to every `_workflow_job` reader

`tests/entities.py:1636` `_workflow_job(text, name)` runs `text.index(f"\n  {name}:\n")`. If a job is renamed, this raises **ValueError at module level**, so `tests/entities.py` dies rather than failing one check. Jobs read this way (count of call sites with a literal name): ci-ratchet 1, closure-scope 2, closures 2, coverage-ratchet 1, fast 1, mutation 2, mutation-ledger 2, mutation-ledger-push 2, mutation-nightly 2, mutation-pin-plan 1, mutation-pins 1, nightly-ha 4, nightly-status 1, record-autofix 1, slow 3. Plus calls through variables or loops: closures-autofix, claims-autofix and mutation-autofix (lines 20146, 20198, 27399-27402, 32164 via `_MA`), and the derived loops at 24796, 24882 and 32599 over every job id.

---

## Per-job readers

### cancel-superseded
- `.github/workflows/codeql.yml:100`: `cancel-superseded:`. A **different job with the same id** in CodeQL, which makes a same-name check run. Not a reader, but a check-name collision.
- `tests/entities.py:24852`: `_NS_OVERRIDES == ["cancel-superseded", "ci-ratchet", "claims-autofix", "closures", "closures-autofix", "mutation-autofix", "nightly-status"]`. **asserts** the exact set of tests.yml job ids that carry a job-level `permissions:` block (derived by regex over tests.yml at 24846-24849).
- `tests/entities.py:24851`: check title naming it. doc.
- `tests/entities.py:28350-28351`: `_PRW_SUBJECTS == ["tests.yml:cancel-superseded", "tests.yml:claims-autofix", ...]`. **asserts** that the null control (tests.yml with its restores undone) is refused on exactly these four `tests.yml:<job>` ids.
- `tests/closure.py:566`: comment saying entities.py opens the cancel-superseded job's program (`tools/pr/cancel_superseded.py`). doc.

### recheck-gate
- `tests/entities.py:32477`: `"needs.recheck-gate.outputs.recheck": _rc`. **asserts**: it evaluates the `if:` of mutation-ledger and mutation-ledger-push with that literal context key, so a rename leaves the token unsubstituted and `eval` raises (caught; becomes a red check).
- `tools/audit/seat/ci-watch.sh:112,128`: `recheck-gate`, a check-run name in self-test fixture head lists. fixture.
- `dev/governance/rules/ci-autofix.md:81`: "`recheck-gate` treats `ci:` as PR-like (not `slow`)" (+ .claude/.cursor copies). doc.
- Related, the input rather than the job: `tools/audit/seat/merge_train.py:288-290` dispatches `tests.yml` with `-f recheck=true` (**keys** on the `recheck` workflow_dispatch input). `.github/workflows/release.yml:71` comment on tests.yml's `recheck` input. doc.

### fast
- `tools/policy/fixtures/required-contexts.json:41,71`: `"fast (3.14)"`. The recorded required context. **asserts**: policy_lint and counts.mjs compare it with the live ruleset, and entities.py maps it to a producer job (see (g)).
- `tests/entities.py:1665,1684`: `_py_versions(_workflow_job(_tests_workflow, "fast"))`. **asserts** that the README's stated Python versions equal fast's matrix.
- `tests/entities.py:27629-27631`: `not ({"fast", "browser", "closures"} & _GOV_MOD.GOV)`. **asserts** fast is not a governance job (null control for (a)).
- `tests/entities.py:29595`: `{"closures", "closures-autofix", "delivery-status", "fast", "closure-scope", "typing", "coverage"} & set(_CFR_EXCL)` must be empty. **asserts** these names are not CFR-excluded.
- `tests/entities.py:29620,29644,29689,29704,29712`: `"fast (3.14)"` in the D13 CFR-rate fixtures. fixture/asserts (measured rates keyed on that name).
- `tests/entities.py:24928,24957`: `_ns_job("fast", "skipped")`, the nightly_status fixture. fixture.
- `tests/entities.py:19097,19101`: `lane_skip.decide("fast", ...)`. **asserts** lane_skip behaviour for lane `fast`.
- `tests/lane_skip.py:87`: `CLOSURE_LANES = ("fast", "coverage")`. **keys**: tests.yml passes `--lane fast` explicitly (tests.yml:2283). The value is a string literal, not derived from the job id. Self-test at 319, 403-417.
- `tests/ci_ratchet.py:128`: `for lane in ("fast", *LANES)` maps the artifact `ci-metrics-fast.tsv` to a lane. **keys** (artifact basename set at tests.yml:438,467). `:211`: `x["lane"] == "fast" and x["class"] == "full"`. **keys**.
- `tools/audit/seat/merge_train.py:288`: comment "PR-like `fast` needs tests.yml's recheck input". doc. `:1734-1810, 2356, 2392, 2430` `"fast"` / `R0 = "fast (3.14)"`. fixture.
- `tools/audit/seat/record_row.py:1332-1413`: `"fast (3.14)"` in failed_required/not_green self-tests. fixture (the real required set comes from the ruleset).
- `tools/audit/seat/ci-watch.sh:71,86`: `fast (3.14)` in the REQ17/PRESENT12 fixture. fixture.
- `tools/pr/merge_main_bot.py:332`: `{"name": "fast (3.14)", ...}`. fixture (shows it is not a pin-chain job).
- `tools/policy/policy_lint.mjs:3754,4088-4101`: `'fast (3.14)'` red-history fixtures. fixture. `:5950` comment. doc.
- `tools/policy/fixtures/red-ancestry/{green,red}/*.json:5`: `"name": "fast (3.14)"`. fixture. `tools/policy/fixtures/policy-rot/prepr/red-answered.md:19`. fixture.
- `tools/pr/prepr.sh:1283,1448`: `--red 'fast (3.14)'` in self-tests. fixture. `:260,268,2637` comments. doc.
- `tools/pr/ci_predict.py:250`: `("fast", f"UNCLASSIFIED {f}: ...")`. **keys** the predicted job label (rc 1 when a non-`mutation` job is predicted, :325). `:35` doc.
- docs: `dev/governance/rules/ci-autofix.md:14,44,65` (+copies); `.claude/skills/steward/SKILL.md:18`; `.github/CODEOWNERS:127`; `dev/governance/decisions/0013-…:216`; `dev/governance/dimensions/D13.md:75` (``fast (3.14)``, matrix-suffix note); `dev/programme/HANDOVER.md:120,319`; `tests/closure.py:125,206,2235-2237`; `tests/entities.py:1629-1632,19957-19959,24779,24921,25008,26579,27574,27604,30645,33167,33192,34023`; `tests/mutation_table.py:3172-3236` (strings in a refusal message); `tests/nightly_status.py:144`; `tests/run.sh:110-111`; `tests/stress.py:2174,4041`; `tests/features.py:34182`; `tests/requirements-coverage.txt:4`; `tools/audit/seat/{INSTRUMENTS.md:349,cloud-setup.sh:13,seat_venv.sh:24}`; `tools/coverage/coverage_tree.sh:25`.

### browser
- `tools/policy/fixtures/required-contexts.json:36,74`: `"browser"`. Required context (see (g)). **asserts**.
- `tests/entities.py:27629`: null control, not in GOV. **asserts**.
- `tests/lane_skip.py:22,393-396`: `d(lane="browser", ...)`. **asserts** the self-test (tests.yml:2303 passes `--lane browser` as a string).
- `tools/audit/seat/ci-watch.sh` REQ17/PRESENT12. fixture.
- docs: `.github/CODEOWNERS:128`; `dev/governance/decisions/0013-…:217`; `tests/README.md:455`; `tests/closure.py:125,374,378`; `tests/entities.py:24772,27604`; `tests/nightly_status.py:144`; `tools/policy/brief_lint.mjs:8`.

### briefs
- `tools/policy/fixtures/required-contexts.json:35,77`: `"briefs"`. Required context. **asserts**.
- `tools/audit/round4/D11/governance_cost.py:61-64`: `GOV = {..., "briefs", ...}`. **keys**: it counts `briefs` check-run seconds as governance.
- `tools/policy/agreement_py.py:106`: `pin = {"briefs"}`. **asserts**: the agreement pair (see (a)).
- `tools/policy/agreement.mjs:186,212`: reader label and SHARED_GRAMMARS disposition naming the 'briefs' null control. **asserts**/doc.
- `tests/entities.py:27630`: `"briefs" in _GOV_MOD.GOV`. **asserts**.
- `tools/audit/seat/orchestrator_tick.py:1917,1931`: `run_obj("briefs", ...)`. fixture.
- `tools/audit/seat/ci-watch.sh` REQ17/PRESENT12. fixture.
- docs: `.github/workflows/governance.yml:8,119,604`; `dev/governance/decisions/0013-…:66`; `tests/entities.py:27599-27600,27631`; `tools/audit/round4/D11/governance_cost.py:11,47`; `tools/policy/brief_lint.mjs:8`.
- False positives dropped: `tools/policy/check-wave-script.mjs:857` (roster field `briefs`); `tools/policy/counts.mjs:231` (dimension-briefs count rule).

### typing
- `tools/policy/fixtures/required-contexts.json:46,86`: `"typing"`. Required context. **asserts**.
- `tests/entities.py:29596`: must not be CFR-excluded. **asserts**.
- `tools/policy/policy_lint.mjs:4089-4162`: `'typing'` red-history and MAIN_STATE_REPORTERS fixtures. fixture.
- `tools/policy/fixtures/red-ancestry/*/d01ba036….json:10`. fixture. `tools/audit/seat/ci-watch.sh` REQ17. fixture.
- docs: `dev/programme/HANDOVER.md:421`; `tests/entities.py:20233`; `tests/nightly_status.py:144`; `tests/requirements-typing.txt:1`; `tests/run.sh:521`; `tests/typing_budgets.json:16`; `tests/typing_ruler.py:5,34,261,680,884,968` (message strings); `tools/audit/seat/{cloud-setup.sh:10,15,seat_venv.sh:19}`.
- False positives dropped: `tests/ha_floor.py:173,185`, `tools/audit/archscore/**` (the Python `typing` module).

### coverage
- `tests/entities.py:28046`: `.get("jobs").get("coverage")`. **asserts** the coverage cache-trust steps `covtrust` and "Stage this commit's per-script coverage" (#1822).
- `tests/entities.py:26682,26688`: `needs.coverage.result != 'skipped'`. **asserts** the canonical text of the graders-head-copy step.
- `tests/entities.py:29596`: not CFR-excluded. **asserts**.
- `tests/ci_ratchet.py:79`: `LANES = ("closures", "coverage")`. **keys** the artifact lane (`ci-metrics-coverage.tsv`, tests.yml:848,928).
- `tests/lane_skip.py:87`: `CLOSURE_LANES`. **keys** (tests.yml:2293 passes `--lane coverage`). Self-test at :415.
- `tools/audit/seat/orchestrator_tick.py:1966`: `run_obj("coverage", ...)`. fixture.
- docs: `dev/governance/decisions/0013-…:181,197`; `dev/programme/HANDOVER.md:314`; `tests/closure.py:125`; `tests/entities.py:26678,30625`; `tests/requirements-coverage.txt:1`.
- **Not** a required context (absent from required-contexts.json).
- False positives dropped: `tools/policy/policy_lint.mjs` `check: 'coverage'` (its own lint class), `.claude/workflows/audit-find.js:176`.

### coverage-ratchet
- `tests/entities.py:30627`: `_COV_JOB = _workflow_job(_TESTS_YML, "coverage-ratchet")`. **asserts** it runs on pull_request, invokes `tests/coverage_ratchet.py`, and never passes `--record` (:30629-30643).
- `tests/entities.py:26687`: step name "…as `coverage-ratchet` runs it" in the graders-head-copy canonical text. **asserts** (literal comparison).
- docs: `dev/governance/decisions/0013-…:196,226`.

### mutation
- `tools/policy/fixtures/required-contexts.json:43,116`: `"mutation"`. Required context. **asserts**.
- `tools/pr/merge_main_bot.py:146`: `PIN_CHAIN = re.compile(r"^(?:mutation|mutation-pin-plan|mutation-pins(?: \(.*\))?|mutation-autofix)$")`. **keys**: the merge-main bot skips a head while any such job of an in-flight run is not completed (`pins_running`, :149-176). Self-test at :340-363 asserts the chain set equals these four, `and not renamed`.
- `tests/entities.py:30623`: `_MUT_JOB`. **asserts** `--scope changed`, not `--scope full`, `fetch-depth: 0`, and no `--record`. `:32162`: `_ma_mut`. **asserts** the measure step. `:32185,32191`: `"needs.mutation.result == 'failure'" in _ma_pins / _ma_fix`. **asserts** the gating of mutation-pins and mutation-autofix.
- `tests/entities.py:29701-29801`: `"mutation"` in CFR fixtures, plus `"mutation" in _CFR_NOT_EXCL` / `not in _CFR_EXCL_NOW`. **asserts** it is deliberately not excluded.
- `dev/governance/config/cfr_exclusions.json:13`: `"not_excluded": {"mutation": …}`. **keys** (the CFR harness reads it).
- `tools/audit/seat/ci_predict_replay.sh:36`: `awk -F'\t' '$1=="mutation"'` over check runs. **keys**.
- `tools/pr/ci_predict.py:261-384`: `("mutation", ...)` predictions. **keys**: `j != "mutation"` decides the rc.
- `tests/closure.py:2252`: comment by `AUTOFIX_QUIET["mutation-autofix"]`. doc.
- fixtures: `tools/audit/seat/failure_logs.sh:68`, `tools/policy/policy_lint.mjs:4091`, ci-watch.sh REQ17.
- docs: `dev/governance/rules/ci-autofix.md:14` (+copies); `dev/governance/rules/defect-root-cause.md:63` (+copies); `.claude/skills/steward/SKILL.md:19`; `dev/governance/roles/fix-review.md:68`; `dev/programme/HANDOVER.md:312` ("**`mutation` is a required check**"); `tests/mutation_table.py:1120,1144,1357,3172`; `tests/entities.py:24767,31989,33189,33192,33363`; `tools/pr/prepr.sh:443`.
- False positive: `tools/policy/policy_lint.mjs:2684,5608` (friction-family name).

### mutation-pin-plan
- `tests/entities.py:34726`: `_MUT_PLAN = _workflow_job(_TESTS_YML, "mutation-pin-plan")`. **asserts** `mutation_table.pin_shard_count(`. `:34732-34733` **asserts** `fromJSON(needs.mutation-pin-plan.outputs.shards)` and `SHARDS: ${{ needs.mutation-pin-plan.outputs.count }}` inside mutation-pins.
- `tools/pr/merge_main_bot.py:146`: PIN_CHAIN. **keys**. `:28` doc. `:346-363` fixture/assert.

### mutation-pins
- `tools/pr/merge_main_bot.py:146`: `mutation-pins(?: \(.*\))?`. **keys** (matrix suffix). `:29,307` doc. `:312-430` fixtures (`"mutation-pins (2)"` and so on).
- `tests/entities.py:32163`: `_ma_pins = _workflow_job(_TESTS_YML, "mutation-pins")`. **asserts** the steps. `:32165` matches steps containing `"mutation-pins"`. `:32196-32197`: `"pattern: mutation-pins*" in _ma_fix` and `"needs: [mutation, mutation-pins]" in _ma_fix`. **asserts** the artifact pattern and needs of mutation-autofix. `:34249-34260`: required strings (`--budget-minutes 260`, `timeout-minutes: 340/350`). **asserts**.
- `tests/mutation_table.py:1024,1072`: docstrings on shard folding. doc (the artifact dir naming is in tests.yml).

### mutation-nightly
- `tests/nightly_status.py:158`: `REQUIRED_LANES = ("mutation-ledger", "mutation-ledger-push", "mutation-nightly", "nightly-ha", "slow")`. **keys**: a lane missing or skipped in the scheduled run turns it red (see (i)).
- `tests/entities.py:24925`: `_ns_job("mutation-nightly", "success")`. fixture. `:30624` `_MUTN_JOB`. **asserts** `--scope full` and no `--record`. `:32502` **asserts** `"github.event.schedule" not in _MUTN_JOB`. `:34114-34116,34247` **asserts** wiring strings. `:34968` **asserts** the seed rotation and `PIN NOT REPRODUCED`. `:30760-30766` **asserts** HANDOVER deferral parsing keyed on the text "mutation-nightly is on main".
- `tools/pr/merge_main_bot.py:331`: fixture (not in PIN_CHAIN).
- docs: `dev/governance/decisions/0011-…:80`; `dev/programme/HANDOVER.md:310-314`; `tests/entities.py:24763,24920,30722`; `tests/harness_headers.py:203`; `tests/mutation_table.py:1350`.

### mutation-ledger
- `tests/nightly_status.py:158`: REQUIRED_LANES. **keys**.
- `tests/entities.py:32424`: `_ml_meas`. **asserts**. `:32430,34134`: `"needs.mutation-ledger.result == 'success'"` in mutation-ledger-push. **asserts**. `:32480-32482`: `if:` evaluation context key. **asserts**. `:34117-34122,34248`: wiring strings. **asserts**. `:24926`: fixture.
- docs: `dev/governance/decisions/0011-…:82,102`; `tests/entities.py:31909,32248,33486,34111`; `tests/harness_headers.py:184`; `tests/mutation_table.py:2281,2288,2952,3745`; `tools/audit/seat/tmp_paths.py:324`.

### mutation-ledger-push
- `tests/nightly_status.py:158`: REQUIRED_LANES. **keys**.
- `tests/entities.py:32425`: `_ml_push`. **asserts**. `:32604`: `_LEDGER_JOBS == ["mutation-ledger-push"]` (the only job whose block mentions `HPO_LEDGER_`, derived over every tests.yml job id) plus `environment: ledger`. **asserts**. `:34123`: `_rca_push_job`. **asserts** there is no cache save in it. `:24927`: fixture.
- docs: `dev/governance/decisions/0011-…:83,102`; `tests/mutation_table.py:1354,1398,1532,3297`.

### slow
- `tests/nightly_status.py:159`: REQUIRED_LANES. **keys**. `:6,11` doc.
- `tests/entities.py:32502`: `"github.event.schedule" not in _workflow_job(_TESTS_YML, "slow")`. **asserts**. `:35513-35516`: **asserts** `run: python3 tests/replay.py` is in the slow job (and reads its steps). `:24924,24956`: fixture.
- docs: `dev/governance/rules/ci-autofix.md:82` (+copies); `dev/programme/HANDOVER.md:314`; `tests/README.md:444`; `tests/closure.py:133`; `tests/run.sh:437`; `tests/features.py:34182`; `tests/harness_headers.py:182`; `tests/mutation_table.py:2280`.
- False positives dropped: `tests/stress.py:2044-3802`, `tests/debug_collect.py:510-515`.

### nightly-ha
- `tests/nightly_status.py:159`: REQUIRED_LANES; `:310` `missing_lanes` strips the ` (` suffix. **keys**.
- `tests/entities.py:20239`: `_NHA_JOB`. **asserts** the installs (requirements and py-spy) and the floor-names snapshot (:20245-20265). `:32503`: **asserts** no `github.event.schedule` in it. `:32517`: `_NHA_IF = _gh_if(...)` evaluated. **asserts** "runs on schedule, on dispatch, and on a pull request whose diff …" (:32532), and **asserts** `^    needs: \[[^\]]*\bclosure-scope\b` (:32535). `:24922-24970`: fixtures `nightly-ha (stable)` / `(2025.2.0)`.
- docs: `tests/closure.py:183`; `tests/config_flow_steps.py:5657,6507,6611`; `tests/entities.py:8748,20060-20064,20222,24745-24749,24875`; `tests/features.py:36555`; `tests/finite_boundary.py:2426`; `tests/nightly_ha.py:116`; `tests/requirements-nightly-ha.txt:1,3`; `tests/run.sh:423,535`; `tools/policy/fixtures/figures/prose-only.md:12` (fixture).

### nightly-status
- `tools/policy/policy_lint.mjs:6096`: `MAIN_STATE_REPORTERS = new Set(['nightly-status', 'delivery-status'])`. **keys**: pr-contract exempts these reds from `## Red checks` unless the diff touches REPORTER_INPUTS (which **includes `.github/workflows/tests.yml`**, :6097-6102). Self-tests at :4092,4127-4138.
- `tools/audit/seat/merge_train.py:3097`: `ignore = ... else ("nightly-status",)`. **keys**: the default ignore-red. `:3057` help text. `:1735-1773,2491,2609,2782` fixtures. `:33` doc.
- `dev/governance/roles/nudge.md:23,52`: `--ignore-red nightly-status --ignore-red delivery-status`. Doc that drives an operator command.
- `tests/entities.py:24812`: `_NS_JOB`. **asserts** it runs on pull_request with exactly one invocation, `python -I -S tests/nightly_status.py`, and read-only perms (:24816-24864). `:24854` in `_NS_OVERRIDES`. **asserts**. `:29647`: `("nightly-status", "delivery-status")` CFR signature. **asserts**.
- `tests/nightly_status.py:626`: writes the summary heading `### nightly-status: {state}`. doc/output.
- `tools/audit/seat/record_row.py:654`: docstring. doc.
- docs: `dev/governance/rules/defect-root-cause.md:142` (+copies); `.github/workflows/governance.yml:737,949`; `.github/workflows/pr-contract.yml:56`; `dev/governance/config/cfr_exclusions.json:4`; `dev/governance/decisions/0013-…:198,226`; `dev/governance/roles/fix-review.md:60`; `dev/governance/roles/nudge.md:57`; `dev/programme/HANDOVER.md:314`; `tests/closure.py:138`; `tests/entities.py:24751,24773,25225,25835,29615-29670`; `tests/run.sh:444`; `tools/policy/policy_lint.mjs:6067,6078`; `tools/pr/prepr.sh:910,1937`.

### graders-head-copy
- `tests/entities.py:26782,26847,26949`: `_wf["jobs"]["graders-head-copy"]` via YAML. **asserts** the whole job equals a canonical literal (`_PT_JOB_CANON`, `_pt_first_diff`) and that every base-restoring token-bearing grader has a step there or a reason in `_PT_EXEMPT` (:26566-26580). `:26837-26839` `_pt_spec(..., "tests.yml", "graders-head-copy", ...)`. **asserts**. `:26974` title. doc.
- docs: `.github/workflows/governance.yml:1021`; `dev/governance/decisions/0013-…:204`; `tools/pr/prepr.sh:111,205`.

### lane-proofs
- **No reader anywhere outside tests.yml** (0 hits for `lane-proofs`, and 0 for the `lane-proof-` artifact prefix). Not in required-contexts.json, REQUIRED_LANES, PIN_CHAIN, GOV, `_NS_OVERRIDES` or any regex class below (orchestrator_tick's NIGHTLY_CLASS/BOT_LANE do not match it).

### closure-scope
- `tools/policy/fixtures/required-contexts.json:38,80`: required context. **asserts**.
- `tools/audit/seat/merge_train.py:286` and `tools/audit/seat/orchestrator_tick.py:120`: `PR_ONLY = ("closure-scope", "pr-contract", "budget-raise-gate")`. **keys**: removed from the required set that the batch proof and the tick wait on (it is written only by a PR event).
- `tests/entities.py:20039`: `_CS_JOB`. **asserts** it runs on workflow_dispatch (a1) and keeps nightly-ha false on dispatch (:20042-20064). `:32530`: `_NHA_SCOPE`. **asserts** the nightly_ha output. `:24879,32523,32535`: `needs.closure-scope.outputs.*` regex and context key. **asserts**. `:29596`: not CFR-excluded. **asserts**.
- `tools/audit/seat/a1_dispatch_arms.sh:67,135`: `doc["jobs"]["closure-scope"]["steps"][2]["run"]`. **keys on structure**: a hard-coded step index of 2.
- `tools/audit/seat/ci-watch.sh:68,84`: fixture.
- docs: `.github/CODEOWNERS:149`; `tests/README.md:178`; `tests/derive_closures.sh:168`; `tests/entities.py:20032-20035,20078,20234`; `tests/nightly_ha.py:116`; `tests/nightly_status.py:145`; `tools/audit/seat/a1_dispatch_arms.sh:3,12,105`.

### closures
- `tools/policy/fixtures/required-contexts.json:39,83`: required context. **asserts**.
- `tests/entities.py:20018`: step "Fail if tests/closures.json under-approximates" must tee check.txt twice. **asserts**. `:20067`: `_CLOSURES_JOB` `DOCS_ONLY_FAST` covers workflow_dispatch. **asserts**. `:24853` `_NS_OVERRIDES`. **asserts**. `:27629` not GOV. **asserts**. `:29595` not CFR-excluded. **asserts**.
- `tests/ci_ratchet.py:79`: `LANES = ("closures", "coverage")`. **keys** (`ci-metrics-closures.tsv`).
- `tools/audit/seat/autofix_statuses.sh:56`: `select(.name == "closures")` over a run's jobs. **keys**.
- `tools/audit/seat/ci_predict_replay.sh:35`: `$1=="closures"`. **keys**.
- `tools/audit/seat/orchestrator_tick.py:168`: `NIGHTLY_CLASS = re.compile(r"autofix|record|nightly|closures", re.I)`. **keys** (regex, see (d)).
- `tools/pr/ci_predict.py:197,224,371-384`: `("closures", ...)`. **keys** the predicted job label and rc.
- `tools/pr/prepr.sh:2650-2656`: `say skip "closures"` / `step "closures"`. prepr's own step label mirroring the job. doc/keys locally.
- fixtures: `tools/audit/seat/orchestrator_tick.py:1745-2677` (`required_names=("tests", "closures")`), `tools/audit/seat/record_row.py:1381,1390`, `tools/audit/seat/failure_logs.sh:59,62`, ci-watch.sh REQ17.
- docs: `dev/governance/rules/ci-autofix.md:13,40,49` (+copies); `.claude/skills/steward/SKILL.md:18`; `tests/README.md:77,140,171,178,181`; `tests/closure.py:547,731,1055,2427,2582,3072,3081,3353`; `tests/entities.py:15906,19463,19690,19761,20033,24840,25944,27604`; `tools/audit/seat/{INSTRUMENTS.md:104,autofix_statuses.sh:8,ci_predict_replay.sh:3,8,failure_logs.sh:54}`; `tools/coverage/coverage_tree.sh:150`; `tools/policy/policy_lint.mjs:5948`; `tools/pr/ci_predict.py:6,15,46,155`; `tools/pr/prepr.sh:260,435,2642`.
- False positives dropped: every `["closures"]` / `"closures":` JSON table key (tests/closure.py, entities.py, lane_skip.py, mutation_table.py:347, tools/merge/ledger_merge.py, tools/pr/ci_predict.py:312, merge_train.py:1363).

### composed-proof
- `tools/audit/seat/merge_train.py:2494,2952` and `tools/audit/seat/orchestrator_tick.py:2534,2545`: fixtures showing a non-required lane that never concludes does not hold a landing. fixture/asserts behaviour (not the name).
- `tests/entities.py:33146-33184`: comments plus check titles about the proof driver. doc.
- docs: `tests/composed_closures.json:4`; `tools/audit/seat/merge_train.py:1081,1282,2493`; `tools/coverage/composed_proof.sh:4` (and its `echo "composed-proof: ..."` message prefixes, :92-136); `tools/coverage/coverage_tree.sh:156,216`.

### ci-ratchet
- `tests/entities.py:32938`: `_CIR_JOB = _workflow_job(_TESTS_YML, "ci-ratchet")`. **asserts**. `:24852` `_NS_OVERRIDES`. **asserts**.
- `tests/ci_ratchet.py:50` usage doc; `:131-296` message prefixes `ci-ratchet:`. doc/output. `:185` `r.get("name") != "Tests"`. **keys** on the **workflow** name.
- `tests/run.sh:439`: doc.

### closures-autofix
- `tests/closure.py:2241,2290`: `AUTOFIX_QUIET["closures-autofix"]` and `_AUTOFIX_REMEDY["closures-autofix"]`. **keys**: `autofix-report --job closures-autofix` (tests.yml:3222) looks the job up here, and an unknown job fails closed (`autofix_repair_failed`). `:2397,2451` message prefix. doc/output.
- `tests/entities.py:19609-19817,19932` (`_AFJ`): **asserts** `autofix_repair_failed("closures-autofix", ...)`. `:20146` loop: **asserts** `--job closures-autofix` and `steps.autofix.outputs.status` in its report step, under `if: always()`. `:20198` loop: **asserts** it dispatches exactly `_AF_DISPATCHED` from the Push step only. `:24853` `_NS_OVERRIDES`. `:27399` **asserts** that `git commit -m "ci: re-record closures"`, its `git add` paths, mayAdd and bot identity agree with policy_lint's AUTOFIX_BOT_COMMITS. `:28352,28362` `_PRW_SUBJECTS` / `_PRW_PULLED`. **asserts**. `:29595` not CFR-excluded. **asserts**.
- `tools/audit/seat/autofix_statuses.sh:41,55`: `select(.name == "mutation-autofix" or .name == "closures-autofix")` and `[ "$name" = closures-autofix ]`. **keys**.
- `tools/audit/seat/orchestrator_tick.py:168,180`: `NIGHTLY_CLASS` / `BOT_LANE` regexes (`autofix`). **keys** (regex).
- docs: `dev/governance/rules/ci-autofix.md:22,73` (+copies; job/subject/function table); `tests/README.md:188,198`; `tests/closure.py:548,567,2018,2236,2427,2473,4918`; `tests/entities.py:19690,19706,19761,19780,20027,20402,21039,21761,24780,27194`; `tests/env_drift.py:1923`; `tests/stress.py:777`; `tools/audit/seat/INSTRUMENTS.md:103`; `tools/policy/policy_lint.mjs:5932`; `tools/pr/ci_predict.py:12`; `tools/pr/prepr.sh:260,428,2650`.

### claims-autofix
- `tests/closure.py:2250,2296`: AUTOFIX_QUIET and _AUTOFIX_REMEDY. **keys** (`autofix-report --job claims-autofix`, tests.yml:3483).
- `tests/entities.py:19993-19996`, `:20146`, `:20198`, `:24852`, `:27400,27407` (`mayAdd is (_job != "claims-autofix")`), `:28351,28362`. **asserts**.
- `tools/audit/seat/ci-watch.sh:111,127`: fixture.
- docs: `dev/governance/rules/ci-autofix.md:42,74` (+copies); `dev/governance/rules/claim-files.md:52` (+copies); `.github/workflows/merge-main.yml:16,107`; `tests/README.md:188`; `tests/closure.py:2233`; `tests/entities.py:19955,27195`; `tests/env_drift.py:21`; `tests/issue996_count.py:37`; `tools/policy/policy_lint.mjs:5933`; `tools/pr/prepr.sh:260,286`.

### mutation-autofix
- `tools/pr/merge_main_bot.py:146`: PIN_CHAIN. **keys**. Self-test at :333-426.
- `tests/closure.py:2259,2299`: AUTOFIX_QUIET and _AUTOFIX_REMEDY. **keys** (tests.yml:3770).
- `tests/entities.py:32137` (`_MA`), `:32139-32150` statuses classified, `:32164` `_ma_fix` (**asserts** `needs: [mutation, mutation-pins]`, `pattern: mutation-pins*`, `needs.mutation.result == 'failure'`), `:20146`, `:20198`, `:24853`, `:27401`, `:28352,28362`. **asserts**.
- `tools/audit/seat/autofix_statuses.sh:41`: `.name == "mutation-autofix"`. **keys**.
- `tools/pr/app_approve.sh:602,1106`: carry rule for its bot commit (keyed on the subject, see (b)). doc/fixture.
- docs: `dev/governance/rules/ci-autofix.md:75,84` (+copies); `dev/governance/roles/fixer.md:24`; `tests/README.md:189`; `tests/entities.py:24837,31989,32037`; `tests/guard_pins.py:292`; `tests/mutation_table.py:1074,1146,1357`; `tools/audit/seat/INSTRUMENTS.md:102`; `tools/policy/policy_lint.mjs:5933`; `tools/pr/ci_predict.py:37,288,369`; `tools/pr/prepr.sh:444,465,2098-2127`.

### record-autofix
- `tests/entities.py:26403`: `_RAF_JOB_RAW = _workflow_job(_TESTS_YML, "record-autofix")`. **asserts** "main-only, its own environment, …" (:26483), finding its own open PR (:26541), and `git commit -q -m "ci: record delivery rows"` appearing exactly twice (:26466,26502).
- `tools/audit/seat/orchestrator_tick.py:168,180`: regexes (`autofix|record`). **keys**. `:2189-2197,2471-2491` fixtures.
- `tools/audit/seat/merge_train.py:2971-2975`: reads tests.yml text and **asserts** `--automerge-check --repo "$REPO" --pr "$NUM" --head "$HEAD"` and `guard --require-green` (the record beat's guard).
- docs: `dev/governance/rules/delivery-status-tracking.md:33` (+copies); `tests/closure.py:728`; `tests/entities.py:26081,26085,26390,29334`; `tools/audit/seat/{INSTRUMENTS.md:284,record_row.py:2,12,463,roster_lib.py:227}`.

---

## (a) wave-script's governance-workflow-jobs agreement pair

- **Where it runs:** the `wave-script` job in `.github/workflows/governance.yml:598`, step "Refuse two readers of one concept that disagree" (:684-694). It runs `python3 -I tools/policy/agreement_py.py --out …`, then `node tools/policy/agreement.mjs --py-json …`. `tests/entities.py` and `tools/audit/round4/D11/governance_cost.py` are restored from the **base** first (:624-668). So the readers are the base's copies, while the workflow files read are the PR head's.
- **Concept:** `tools/policy/agreement.mjs:178` `concept: 'governance-workflow-jobs'`, "which workflow jobs are governance: tests/entities.py's pinned file list against governance_cost.py's GOV derivation, D11-s1-72".
- **What it compares (`tools/policy/agreement_py.py:89-112`):**
  - Corpus: the union of job ids over **every** `.github/workflows/*.y*ml`. The regex is `^  ([A-Za-z][\w-]*):` after the last `\njobs:\n`, a disclosed copy of `entities.py _workflow_job_ids`. The corpus includes all 27 tests.yml ids.
  - Reader 1, `governance_cost.py GOV`: `j in GOV`.
  - Reader 2, `tests/entities.py _GOV_FILES (+ the 'briefs' null control)`: `j in pin`, where `pin = {"briefs"} ∪ job_ids(each file in entities.py's _GOV_FILES list)`. Those files are `_GOV_WF` (governance.yml), `pr-contract.yml`, `budget-raise-gate.yml`, `budget-raise-gate-rerun.yml` and `pr-contract-rerun.yml`, parsed out of entities.py source by the regex `_GOV_FILES = \[(.*?)\]`.
  - The pair is refused if, for any job id, the two booleans differ.
- **Hard-coded job names:**
  - `tools/audit/round4/D11/governance_cost.py:61-64`: `GOV = {"policy-docs", "env-matrix", "wave-script", "pr-contract", "record", "delivery-status", "delivery-status-publish", "briefs", "instrument-self-tests", "budget-raise-gate", "rerun-stale-verdict", "rerun-stale-contract"}`.
  - `tools/policy/agreement_py.py:106`: `pin = {"briefs"}`.
  - The only tests.yml job named is **`briefs`**. Every other tests.yml id must be in **neither** set, so renaming or adding a tests.yml job is neutral unless the new id collides with a GOV member or with a job id in the five governance files.
- **Sibling pin in entities.py (`tests/entities.py:27576-27636`):** asserts `GOV ⊆ all job ids` and `_GOV_FILE_JOBS ⊆ GOV`. It also asserts the null control `not ({"fast","browser","closures"} & GOV) and "briefs" in GOV`.
- **Discovery arm:** `agreement.mjs:212` registers the grammar `"  ([A-Za-z][\\w-]*):"` as `identical:` (the shared job-id scan).
- Not in this pair, but in the same job: `node tools/policy/check-wave-script.mjs` (:681). It reads wave scripts and rosters, not tests.yml job names.

## (b) ci-autofix loop-guard subjects

- **Definition:** `tests/closure.py:2210-2218`:
  ```python
  def autofix_allowed(*, event_name, closures_result, head_repo, repo, commit_subject,
                      loop_subject="ci: re-record closures") -> bool:
      return (event_name == "pull_request" and closures_result == "failure"
              and head_repo == repo and commit_subject != loop_subject)
  ```
  It keys on **no job name**. The job identity enters through the `closures_result` argument, which the caller wires from `needs.<job>.result` in tests.yml:
  - `closures-autofix`: `CLOSURES_RESULT: ${{ needs.closures.result }}` (tests.yml:3005,3014-3020). Default loop subject.
  - `claims-autofix`: `FAST_RESULT: ${{ needs.fast.result }}` → `closures_result=`, `loop_subject="ci: drop inherited claims"` (:3275,3286-3292).
  - `mutation-autofix`: `MUTATION_RESULT` → `loop_subject="ci: pin killed mutants"` (:3565-3571).
  - The job-level `if:` lines also key on `needs.closures.result == 'failure'` (:2958), `needs.fast.result == 'failure'` (:3233) and `needs.mutation.result == 'failure'` (mutation-pin-plan :1098, mutation-pins :1136).
- **The status tables keyed by job name:** `tests/closure.py:2240-2263` `AUTOFIX_QUIET = {"closures-autofix": …, "claims-autofix": …, "mutation-autofix": …}` and `:2290-2304` `_AUTOFIX_REMEDY`. They are read via `closure.py autofix-report --job <job>` (tests.yml:3222,3483,3770; argparse at closure.py:4967-4968). An unknown `--job` fails closed.
- **The subject allowlists (keyed on subject, not job):**
  - `tools/policy/policy_lint.mjs:5959-5976` `AUTOFIX_BOT_COMMITS.messages`: `'ci: re-record closures'` → `tests/closures.json`, mayAdd. `'ci: drop inherited claims'` → the two claim files, remove-only. `'ci: pin killed mutants'` → `tests/mutation_budgets.json`, `tests/mutation_ledger/`, mayAdd. `'ci: merge main'` → `{merge: true}`. Used by pr-contract to excuse bot commits after the body.
  - `tools/pr/app_approve.sh:124-139` `bot_author()` / `bot_paths()`: the same three `ci:` subjects plus `"claims: drop the claims main already carries after the main merge"`.
  - `tests/entities.py:27399-27413`: the **job↔subject mapping** `(("closures-autofix","ci: re-record closures"), ("claims-autofix","ci: drop inherited claims"), ("mutation-autofix","ci: pin killed mutants"))`. It **asserts** each job's block has `git commit -m "<subject>"`, a `git add` path set equal to policy_lint's, mayAdd equal to `(_job != "claims-autofix")`, and the bot `user.name`/`user.email`.
  - `tests/entities.py:19473-19495,19923-19925`: `autofix_allowed` unit checks, including the loop subject `ci: re-record closures` and the separate guard for `ci: drop inherited claims`. `:27268-27347`: pr-contract acceptance of bot commits, including `ci: merge main` (R9-CI-2b).
- **The `ci:` prefix, any subject:** `recheck-gate` in tests.yml:215-218, `case "$SUBJECT" in ci:*) recheck=true`. It is internal to tests.yml; no external reader. Documented at `dev/governance/rules/ci-autofix.md:81-82`.
- **Other `ci:` subjects:**
  - `ci: record nightly kills`: tests.yml:1599, `tests/mutation_table.py:1359 DRAIN_SUBJECT`. `tests/entities.py:32446` asserts `DRAIN_SUBJECT.startswith("ci: ")`. Decision 0011:112,159.
  - `ci: record delivery rows`: tests.yml:4024,4146 (record-autofix). `tests/entities.py:26466,26502` assert it occurs exactly twice.
  - `ci: merge main`: `tools/pr/merge_main_bot.py` SUBJECT, `.github/workflows/merge-main.yml:4`, policy_lint:5974.
- **Readers of bot subjects as head state:** `tools/audit/seat/merge_train.py:475-489` treats any tip authored by `github-actions[bot]` as a bot head, whatever the subject. `tools/audit/seat/queue_pre_flight.py:347-362` has fixtures with `ci: pin killed mutants`. `tools/policy/agreement_py.py:39` has a merge-subject corpus fixture including `ci: re-record closures`.

## (c) pr-contract: which Tests job/check names it reads

- `.github/workflows/pr-contract.yml:246-254`, step "List the red checks at this head": it calls `gh api --paginate repos/…/commits/$PR_HEAD/check-runs`, keeps `status=="completed" and conclusion=="failure"`, and drops `.name != "pr-contract"`. **No tests.yml job name is hard-coded**: every red check-run name, Tests jobs included, is passed as one `--red <name>` each (:274-292) to `policy_lint.mjs --pr-body`.
- `tools/policy/policy_lint.mjs:6077` `PR_CONTRACT_CHECK = 'pr-contract'` (the self-exclusion). `:6096` `MAIN_STATE_REPORTERS = {'nightly-status','delivery-status'}`: these two reds are exempt unless `reporterInputsTouched()` finds a REPORTER_INPUTS path (`tests/delivery_status.py`, `tests/nightly_status.py`, **`.github/workflows/tests.yml`**, `.github/workflows/governance.yml`, the plan, HANDOVER) or a pre-existing delivery row (:6097-6112). `nightly-status` is the only tests.yml job keyed by name here.
- The red-history union (#1144/#2028) reads every branch commit's check runs by name (`failingCheckNames`, :6123-6131). No job names are hard-coded.
- AUTOFIX_BOT_COMMITS (see (b)) keys on the commits that tests.yml's three autofix jobs push, by subject, not by job name.
- Self-test fixtures name `fast (3.14)`, `typing`, `mutation` and `nightly-status` (policy_lint.mjs:3754,4088-4162).
- `pr-contract.yml:16-17` comment: "`tests.yml` must not carry `edited`". **Asserted** by `tests/entities.py:27650-27688` (a workflow listing `edited` holds one unguarded job) and by `:27689-27752` (`_RC_SKIPPED`: no required context's producing job is skippable under `pull_request: edited`).
- `tools/pr/contract_rerun.py` (via pr-contract-rerun.yml): see (h). It keys on workflow paths and run ids, not job names.

## (d) "the tick"

- The tick is `tools/audit/seat/orchestrator_tick.py` ("The heartbeat's dispatch list"). `dev/governance/roles/nudge.md` describes the turn but never says "tick". `gate-scoping.md` ("not the tick's count") and `ci-autofix.md` ("read the summary line, not the tick") use "tick" for the green check mark.
- Check names it reads:
  - **Required set, live:** `required()` at :994-1010 reads ruleset `RULESET = "main-protect-checks"` (:118) through `gh api repos/…/rulesets` → `.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context`, **minus `PR_ONLY`**.
  - **Hard-coded:** `PR_ONLY = ("closure-scope", "pr-contract", "budget-raise-gate")` (:120), used at :531 and :902 (absent-at-head exclusion) and :1005.
  - **Regex classes keyed on names:** `NIGHTLY_CLASS = re.compile(r"autofix|record|nightly|closures", re.I)` (:168). On main's tip, non-required reds matching it are flagged "non-required red (nightly/record class)" (:921-925). In tests.yml it matches `closures` (but `closures` is required, so the `n not in req` filter excludes it), `closures-autofix`, `claims-autofix`, `mutation-autofix`, `record-autofix`, `mutation-nightly`, `nightly-ha (…)` and `nightly-status`. `BOT_LANE = re.compile(r"autofix|nightly|record", re.I)` (:180, used :1046) adds the ci-autofix "read the bot's job summary" text to a main-red dispatch brief.
  - Per PR: the latest check run per name at the head (`commits/{sha}/check-runs`, :301), GREEN = `("success","skipped","neutral")`.
  - `tests/ci_budgets.json` `critical_path_minutes` for the stuck threshold (:179,313-341). It reads a number, not names.
- Self-test fixtures: `"tests"`, `"closures"`, `"briefs"`, `"coverage"`, `"record-autofix"`, `"composed-proof"`.

## (e) tools/audit/seat/merge_train.py

- `RULESET = "main-protect-checks"`, `PR_ONLY = ("closure-scope", "pr-contract", "budget-raise-gate")` (:285-286). `required()` (:1245-1253) reads the ruleset contexts live, minus PR_ONLY, and fails closed with Stop if unreadable. `wait_ci(h, only=req)` (:635-664) waits on those names with GREEN = success/skipped/neutral (:254).
- `--ignore-red` defaults to `("nightly-status",)` (:3057,3097). This is the **only tests.yml job hard-coded to change behaviour**. nudge.md:23,52 tells the operator to pass both `nightly-status` and `delivery-status`.
- `DISPATCH = (("tests.yml", ("-f", "recheck=true")), ("governance.yml", ()), ("codeql.yml", ()), ("hassfest.yml", ()), ("validate.yml", ()))` (:290). It keys on the workflow file and the `recheck` input, not on job names. Self-test :2855-2856 asserts each file exists and takes `workflow_dispatch`.
- `culprit()` (:1345-1360): for each red name it fetches the job log and greps `>>> FAILED: (tests/…)` (`FAILED_SCRIPT`, :292). The names are generic.
- Bot head: the tip authored by `github-actions[bot]` (:475-489), any subject.
- Self-test (:2971-2975) reads tests.yml text and asserts the record-autofix guard strings (see record-autofix).
- Fixtures: `"fast"`, `"fast (3.14)"`, `"nightly-status"`, `"composed-proof"`, `"tests"`, `"pr-contract"`.

## (f) tests/closures.json, the INERT list and the tests.yml parsers

- **`.github/workflows/tests.yml` is NOT in INERT.** It is in **`GATE_FILES`** (`tests/closure.py:453-488`, entry at :476, comment :462-475: "`tests.yml` ALONE … a change to it can alter how every script behaves"), so touching it forces the FULL suite. The other workflow files are measured closures (closure.py:360-410 comments; governance.yml and release.yml moved out of INERT).
- **Closures that include tests.yml** (`tests/closures.json`): `closures["tests/entities.py"]` and `closures["tests/harness_headers.py"]`. It is in no `inert_reads` entry.
- **Tests that parse tests.yml job structure:**
  - **`tests/entities.py`** (the main one). By regex block (`_workflow_job`, :1636, hard ValueError on a missing id) and by YAML (`_RC_DOCS`, `_PRW_TEXTS`, `_PT_DOCS`). What it asserts about job ids, needs and `if:`:
    - `_NS_OVERRIDES` = exactly `[cancel-superseded, ci-ratchet, claims-autofix, closures, closures-autofix, mutation-autofix, nightly-status]` carry job-level `permissions:` (:24846-24856).
    - `_NS_SCHEDULE_ONLY` = the jobs whose pre-steps head has `'schedule'` but no `'push'`/`'pull_request'` (closure-scope diff gates stripped) must equal `nightly_status.REQUIRED_LANES` (:24880-24894).
    - `_DEPTH_JOBS`: every job (all ids by `^  ([a-z][\w-]*):$`) that drives mutation_table.py, run.sh, entities.py or env_drift.py must carry `fetch-depth: 0` (:24794-24810).
    - `_LEDGER_JOBS == ["mutation-ledger-push"]` (:32599-32605).
    - The ledger `if:` reach matrix: evaluates `if:` with `needs.recheck-gate.outputs.recheck` and `needs.mutation-ledger.result` (:32452-32495). One cron, `17 2 * * *` (:32496-32503).
    - nightly-ha `if:` and `needs: [... closure-scope ...]` (:32517-32536).
    - mutation-pins/mutation-autofix wiring: `needs: [mutation, mutation-pins]`, `needs.mutation.result == 'failure'`, `pattern: mutation-pins*`, `fromJSON(needs.mutation-pin-plan.outputs.shards)` (:32183-32197, :34726-34735).
    - Every required context maps to a producing job by `name:`, by id, or by id + ` (…)` (`_rc_producer`, :27706-27715). Under `pull_request: edited` no producer is skippable (:27738-27752). Every producer runs on `merge_group`, with a tests.yml null control (:28003-28036).
    - No job-level `if:` leads with `always()`, and at least 14 use `!cancelled()` across all workflows (:27979-27991).
    - Write-grant jobs on pull_request restore their program and don't persist the token (`_prw_defects`), with null control subjects `tests.yml:{cancel-superseded,claims-autofix,closures-autofix,mutation-autofix}` (:28295-28365).
    - The three autofix jobs' report step (`--job <job>`, `if: always()`) and their dispatch set (:20146-20215).
    - The autofix job↔subject↔paths agreement (:27399-27413).
    - graders-head-copy equals its canonical literal (:26775-26849).
    - record-autofix wiring (:26403-26541).
    - The closures check-step tee (:20018-20027), DOCS_ONLY_FAST (:20067-20076), the closure-scope dispatch arm (:20039-20064), the nightly-ha installs (:20239-20265), `slow` runs replay.py (:35513-35516), the mutation, mutation-nightly and coverage-ratchet scope/`--record` checks (:30623-30660), the RCA-1565 and budget wiring strings (:34110-34135, :34245-34265), the mutation-nightly seed (:34968-34973), and `fast`'s matrix → README Pythons (:1665-1686). Hash-pinned installs (`_pin_unhashed_installs`, :35398) iterate over all jobs.
  - `tests/ci_*.py`: only `tests/ci_ratchet.py`. It does not parse tests.yml. It keys lanes by artifact basename (`fast`, `closures`, `coverage`) and runs by workflow name `Tests`.
  - `tools/policy/policy_lint.mjs`: does **not** parse tests.yml jobs. It lists tests.yml in REPORTER_INPUTS (:6099) and checks required-context literals and the fixture (:1052-1090).
  - `tools/policy/field_coverage.mjs`: does not read tests.yml. It registers the required-contexts ruleset input (:140-160).
  - `tools/policy/counts.mjs:136`: `d.jobs = countMatches('.github/workflows/tests.yml', /^ {2}[a-z0-9-]+:$/gm)`. This gives **29** at this tree: 27 jobs plus the `push:` and `schedule:` lines under `on:`. **No COUNT_RULE uses `jobs`**, so it is dead.
  - `tools/policy/agreement_py.py:89-112`: the job-id scan over every workflow (see (a)).
  - `dev/audit/rounds/round6/D11/fix/codeowners_gap.py:669-680` (run by governance.yml): `self_test_only_required()` refuses any workflow job whose block is self-test-only and whose **id is a required context** (required-contexts.json). It iterates over all jobs of all workflows.
  - `tools/audit/seat/a1_dispatch_arms.sh:67,135`: hard-codes `jobs.closure-scope.steps[2].run`.
  - `tests/lane_skip.py` and `tests/card.mjs:10766` only treat the path `.github/workflows/tests.yml` as a gate file or delta entry. They don't parse jobs.

## (g) Required-check lists in the tree, and what verifies them against GitHub

- **The recorded list:** `tools/policy/fixtures/required-contexts.json` (readers locate it under the old path `.claude/workflows/fixtures/` too). `"rulesets": [23698884]`, `"branch_endpoint": "repos/tvofi/heatpump_optimizer/rules/branches/main"`, `"contexts"` (17): `Analyze (actions)`, `Analyze (javascript-typescript)`, `Analyze (python)`, **`briefs`**, **`browser`**, `budget-raise-gate`, **`closure-scope`**, **`closures`**, `env-matrix`, **`fast (3.14)`**, `hassfest`, **`mutation`**, `policy-docs`, `pr-contract`, **`typing`**, `validate-hacs`, `wave-script`. Seven come from tests.yml (bold). It also has `ruleset_objects` with the per-context integration ids (e.g. "context": "closure-scope" :80).
- **Verified against GitHub:**
  - `tools/policy/counts.mjs:283-…` `liveRequiredContexts()` reads both `rules/branches/main` and the ruleset objects (they must agree). `requiredContextsDrift()` reddens on any name, ruleset id or field difference (:368-492). Bypass-hidden fields print an UNCHECKED skip.
  - It is wired in `tools/policy/policy_lint.mjs:1052-1090` `requiredContextsOverTree()` (class `required-contexts`, in the `policy-docs` job, with GITHUB_TOKEN per governance.yml:174,587). An unreachable API is a printed skip, not a finding. It also checks the corpus's stated **count** literals at REQUIRED_CONTEXT_SITE files (workflow comments, plan, decisions, HANDOVER).
  - `tools/policy/field_coverage.mjs:140-160,206,322,453`: the `ruleset` artifact registration for that check.
- **Verified against the workflow files (not GitHub):** `tests/entities.py:27701-27752` (every context has a producer; none is skippable on `edited`) and `:28003-28036` (every producer runs on `merge_group`). `codeowners_gap.py:669-680` (no self-test-only job is required).
- **Live readers with no list of their own:** `merge_train.py:1245`, `orchestrator_tick.py:994`, `record_row.py failed_required/not_green` (required set passed in), `nudge.md:57,101` ("Read that ruleset every turn … Do not trust a remembered list").
- **Hard-coded snapshots in self-tests only:** `tools/audit/seat/ci-watch.sh:57-88` `REQ17`/`PRESENT12`/`ABSENT5`, "read from the API 2026-10-09" (fixture). `dev/audit/rounds/round5/D11/governance_drift.mjs:64` (an audit harness).

## (h) workflow_run / check_suite triggers referencing "Tests" or its jobs

- **`.github/workflows/pr-contract-rerun.yml:30-32`:** `workflow_run: workflows: ["Architecture score", "Budget raise gate", "CodeQL", "Governance", "Hassfest", "Tests", "Validate"]`, `types: [completed]`. The job `rerun-stale-contract` has `if: contains(fromJSON('["failure","timed_out","cancelled"]'), github.event.workflow_run.conclusion)` and runs `tools/pr/contract_rerun.py --rerun $RUN_ID`. It keys on the **workflow name `Tests`**, not on job names. `tests/entities.py:28511-28575` derives the watched list as the `name:` of every workflow listing `pull_request`/`pull_request_review`, less "PR contract", and asserts equality. Renaming the workflow `Tests` would be caught there. `contract_rerun.py` keys on the workflow path (`.github/workflows/pr-contract.yml`) and run ids, and its self-test uses the path `.github/workflows/tests.yml` (:121).
- **`.github/workflows/budget-raise-gate-rerun.yml:30-31`:** `workflow_run: workflows: ["Budget raise gate"]` only. It does not reference Tests. `tools/policy/budget_raise_gate.py:1156` has only a self-test fixture with the tests.yml path.
- **`.github/workflows/merge-main.yml`:** `on: push: branches: [main]` plus `workflow_dispatch` (:22-30). There is no workflow_run or check_suite. It **dispatches** `tests.yml hassfest.yml validate.yml codeql.yml` after a GITHUB_TOKEN push (:100) and approves held runs. Its program `tools/pr/merge_main_bot.py` keys on the Tests job names through **PIN_CHAIN** (`mutation`, `mutation-pin-plan`, `mutation-pins (…)`, `mutation-autofix`; :146), reading `actions/runs?head_sha=` and each in-flight run's `jobs`.
- No `check_suite` or `check_run` triggers exist in any workflow. `release.yml`, `pages.yml`, `arch-score.yml`, `codeql.yml`, `hassfest.yml` and `validate.yml` reference tests.yml only in comments. `codeql.yml:71` says the three autofix jobs dispatch it.
- **Other "Tests" workflow-name readers:** `tools/release/stamp.py:173-174,547` (`TESTS_WORKFLOW = "Tests"`, `TESTS_WORKFLOW_FILE = "tests.yml"`; the stamp requires the latest Tests run green, via `gh run list --workflow Tests` at :1415) and `tests/ci_ratchet.py:185` (`r.get("name") != "Tests"`).

## (i) nightly-status: what it reads, and the grading scripts

- **Job:** tests.yml `nightly-status` (:1834), `if: github.event_name == 'pull_request'`, read-only `actions: read` + `contents: read`. It runs `python -I -S tests/nightly_status.py` (asserted at entities.py:24812-24864), restored from the base.
- **What `tests/nightly_status.py` reads:** `DEFAULT_WORKFLOW = "tests.yml"` (:128). The Actions API `repos/{repo}/actions/workflows/tests.yml/runs` (:516) gives the newest run with event in `VERIFYING_EVENTS = {"schedule", "workflow_dispatch"}` on `DEFAULT_BRANCH = "main"` (:174-175), then that run's jobs.
  - `failing_jobs()` (:296-303): **any** job of that run with a conclusion outside `OK_CONCLUSIONS = {"success","skipped","neutral"}` is red. All tests.yml job names are read generically.
  - `missing_lanes()` (:306-318): `REQUIRED_LANES = ("mutation-ledger", "mutation-ledger-push", "mutation-nightly", "nightly-ha", "slow")` (:158-159). Each must have *run* (not skipped or absent). Matrix arms are matched by `name.split(" (")[0]`. A rename gives MISSING, which is red (fails closed by design, :152-157).
  - `MAX_AGE_NIGHTS = 2` (:141). States: FAILED, PASSED, RUNNING, ABSENT, UNREADABLE (exit 0/1/2). The red report tells the reader to run `gh workflow run tests.yml --ref main` (:209).
  - The summary heading is `### nightly-status: {state}` (:626).
- **Coupling pinned:** `tests/entities.py:24880-24894` asserts `sorted(REQUIRED_LANES) == schedule-only jobs derived from tests.yml job heads`. `:24921-24970` has fixtures over `nightly-ha (stable)`, `nightly-ha (2025.2.0)`, `slow`, `mutation-nightly`, `mutation-ledger`, `mutation-ledger-push` and `fast` (skipped).
- **How its red is graded elsewhere:**
  - pr-contract exemption: `policy_lint.mjs:6096` MAIN_STATE_REPORTERS (see (c)).
  - merge_train's default `--ignore-red nightly-status` (:3097).
  - orchestrator_tick's NIGHTLY_CLASS on main (:168,921).
  - record_row.py:654 (not in the required set, so `failed_required` ignores it).
  - CFR: `tests/entities.py:29615-29670` (reported, deliberately not added to `cfr_exclusions.json`, whose `excluded_jobs` is `['record']` and `not_excluded` is `['mutation']`).
  - fix-review.md:60 and defect-root-cause.md:142: no body answer is owed unless the diff touches its inputs.
- **delivery-status grader:** `tests/delivery_status.py` runs in governance.yml's `delivery-status`/`record` jobs. It grades rowless merges and **reads no tests.yml job names** (grep: only a comment at :172 citing nightly_status's shape). It is paired with nightly-status in MAIN_STATE_REPORTERS, merge_train's documented ignore list and record_row.
- **record-autofix** (tests.yml, main-only) is the bot that writes delivery rows (`ci: record delivery rows`), driven by `tools/audit/seat/record_row.py`. It is not in REQUIRED_LANES. The tick's NIGHTLY_CLASS/BOT_LANE regexes cover it by the substring `record`.
