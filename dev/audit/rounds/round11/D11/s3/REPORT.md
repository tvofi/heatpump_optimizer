# D11-s3 — round 11, D11.M4 (perturbation) and D11.M5 (mechanise first)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B7 (4 vCPU container, shared during the fan-out; every number below is a count, so contention-immune). Harnesses run from the export root with `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3`.

## Method

The universe of both steps is the D11.M1 mechanism inventory, derived from the tree (and the captured ruleset list) by `inventory.py`: 229 rows in 12 families (ruleset 3, required-context 1, gate-required 21, policy_lint 25, policy-tool 17, gate-script 33, claim-file 2, pr-tool 20, plan-tool 2, ci-tool 12, seat-instrument 89, hook 4). For each examined row a committed harness applies a one-edit perturbation to the mechanism's input or its production code in a private worktree or in memory, reads the production check's own verdict, and carries a `--perturb` arm that moves its number. First work: C1 (round 10 had no denominator for M4) is answered by the enumerator and the closed coverage row; C2 (no perturbation for the main ruleset read with both arms, structure.py, brief_lint.mjs, the claim files, prepr.sh) is examined, each by its own harness.

Examined: 66 of 229 for M4 and M5 (all 3 rulesets, the `gate` context, all 21 gate-required contexts, all 25 policy_lint lane rows, 6 policy tools, structure.py and env_drift.py, both claim files, prepr.sh, gate.py, all 4 hooks). Not reached: 163 rows, listed in REPORT.json `coverage.not_reached` (every seat instrument, most pr/ci/plan tools and gate scripts).

## Findings

### D11-s3-01 — The tree's only ruleset reader never reads main-protect (deletion, non-fast-forward) or the release-tag ruleset (medium, bug)

- Claim: tools/policy/counts.mjs:liveRequiredContexts fetches only rulesets that contribute a required_status_checks rule, so 1 of the repository's 3 active rulesets is compared with its record: dropping main-protect 22628467's deletion and non_fast_forward rules, adding an always-bypass actor to it, disabling it, or emptying release-tags-protect 23937752 each leaves requiredContextsDrift at 0 errors, while the same class of edit on 23698884 yields 1-7.
- Mechanism: The reader builds `ids` from branch rules filtered to type required_status_checks (counts.mjs, the `if (r.type !== 'required_status_checks') continue` line precedes `ids.add`), and requiredContextsDrift compares only the fetched objects; tools/ci/ruleset_cutover.py pins RULESET_ID = 23698884 alone. No other tracked script reads 22628467 or 23937752. The fixture's _comment records the choice: 22628467 is described there ('carries deletion and non-fast-forward') but deliberately left out of `rulesets`, so its rules are stated and never compared. Live re-read 2026-11-16 20:3x: 22628467's rules equal the capture.
- Evidence: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/ruleset_arms.py` -> 1 rulesets read (of 3 on the repository); gap_arms_unmoved=4 of 4, controls_fired=3 of 3; instrumented `tools/policy/counts.mjs:liveRequiredContexts (and requiredContextsDrift)`
- Perturbation: counts.mjs:liveRequiredContexts: move `if (r.ruleset_id != null) ids.add(r.ruleset_id)` above the required_status_checks filter (harness --perturb) -> rulesets_read 1 -> 2; gap_22628467_bypass_added_errors 0 -> 1; gap_arms_unmoved 4 -> 2
- Null control: null arm 0 errors; control arms on 23698884: 7, 1, 4
- Property: Every active ruleset targeting main or release tags is read and compared field by field with a committed record, so a change to any of them turns a check red.
- Seams: `gh api repos/tvofi/heatpump_optimizer/rulesets --jq '.[].id' (each id not in the `read` list dev/audit/rounds/round11/D11/s3/ruleset_arms.py prints for the null arm)`
- Fix and mechanisation (M5): tools/policy/counts.mjs liveRequiredContexts also reads every other ruleset GET rulesets lists (main-protect 22628467, release-tags-protect 23937752) and compares each with a committed object in tools/policy/fixtures/required-contexts.json under a key of its own, beside ruleset_objects; the `rulesets` list keeps its #1300 meaning (the ids the required contexts are read out of), which the fixture's own _comment says must not name 22628467. bypass_actors stays token-hidden in CI as today. Mechanisation (D11.M5): extends an existing mechanical reader; cost about two API GETs per policy-docs run and about 20 lines, no policy line.

### D11-s3-02 — brief_lint's CI run never lints the live rosters in dev/programme/rosters/ (66 live groups; 3 rotted citations) (medium, bug)

- Claim: The no-argument run of tools/policy/brief_lint.mjs (tests.yml `briefs`) lints 1 roster file, .claude/workflows/wave-3l-groups.json (1 live group), and not dev/programme/rosters/wave-r10-groups.json (52 live groups) or wave-r9-groups.json (14): an unresolvable path appended to a live brief there leaves TOTAL at 0, the same edit in wave-3l moves it to 1, and the r10 roster already carries 3 path:line errors that only a named-file run prints.
- Mechanism: main() takes `files = workflowFiles(ROSTER_FILE_RE)`, which lists .claude/workflows/ and dev/programme/carries/ only; ROSTERS_DIR is read by rosterIssues (the issue index) but never linted. roster_edit.py's write gate lints the roster by name but demotes every error the base already has to `WARN pre-existing, re-pin owed`, so a citation that rots after its write is refused by nothing.
- Evidence: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/brief_arms.py` -> 2 live roster files in ROSTERS_DIR the CI run does not lint (gap_arms_unmoved=2 of 2; named_wave_r10_groups_errors=3; controls_fired=3 of 3); instrumented `tools/policy/brief_lint.mjs:main (workflowFiles roster list)`
- Perturbation: brief_lint.mjs main(): `? workflowFiles(ROSTER_FILE_RE)` -> also list ROSTERS_DIR's wave-*-groups.json (harness --perturb) -> rosters_linted 1 -> 3; null TOTAL 0 -> 3; gap_r10_path 0 -> 4, gap_r9_path 0 -> 4; live_rosters_in_rosters_dir_unlinted 2 -> 0
- Null control: null 0; control_3l_path 1, control_3l_count 1, control_playbook_path 1
- Property: Every roster file holding a live (non-done) group is linted by the required no-argument brief_lint run, so a citation that stops resolving in any live brief turns `briefs` red.
- Seams: `git ls-files '*wave-*-groups.json' | grep -v fixtures (each file not printed under `== ... ==` by `node tools/policy/brief_lint.mjs`)`
- Fix and mechanisation (M5): brief_lint.mjs main() lints ROSTERS_DIR rosters on the no-argument run (one line; a named r10 run measured about 5 s here, provisional), the 3 rotted R10-RELAY-NOBODY-STALL anchors re-pinned in the same pull request, and brief-citations.md's first sentence names the roster directory. Mechanisation (D11.M5): this replaces the manual 're-pin owed' WARN that roster_edit.py prints with a refusal; cost one line of code, no policy line.

### D11-s3-03 — policy_lint --hooks accepts a wired hook neutered to `exit 0`: it reads the self-test's exit status, never its tally (medium, bug)

- Claim: Inserting `exit 0` as line 2 of any of the four hooks .claude/settings.json wires (pre-bash, pre-edit, session-start, stop-selfcheck) makes the hook refuse nothing and its --self-test print nothing, yet tools/policy/policy_lint.mjs:cmdHooks reports it `ok` and prints `HOOKS ok: 4 wired hook(s) exist and pass their own --self-test` (4 of 4 neutered arms accepted), while gutting only the hook's refusal exit is refused (3 of 3).
- Mechanism: cmdHooks sets `verdict: code === 0 ? 'ok' : 'SELF-TEST FAILED'` from execFileSync('bash', [script, '--self-test']) and only prints the output's last line as `why`; an empty self-test exits 0. Every wired hook's self-test ends `printf '\n%s passed, %s failed\n'`, so the tally is available and unread. governance.yml (policy-docs) and prepr.sh's `hooks` step both run this check; it is the only CI read of the hooks.
- Evidence: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/hooks_arms.py` -> 4 neutered hooks (of 4 wired) cmdHooks reports ok (gap_noop_accepted); control_refused=3 of 3, null_ok=4; instrumented `tools/policy/policy_lint.mjs:cmdHooks`
- Perturbation: cmdHooks: `verdict: code === 0 ? 'ok'` -> `verdict: code === 0 && /^[1-9]\d* passed, 0 failed$/.test(tail) ? 'ok'` (harness --perturb, in a private worktree) -> gap_noop_accepted 4 -> 0; null_ok stays 4; control_refused stays 3
- Null control: null 4 of 4 ok; control_<hook>_decision_gutted refused 3 of 3 (pre-bash, pre-edit, stop-selfcheck)
- Property: A hook passes the hooks check only when its self-test demonstrably ran cases (a non-zero passed count and zero failed), so a hook that refuses nothing cannot read as wired and tested.
- Seams: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/hooks_arms.py (its gap_<hook>_noop lines; the hooks are those .claude/settings.json wires)`
- Fix and mechanisation (M5): tools/policy/policy_lint.mjs cmdHooks: require the tail to match `<n> passed, 0 failed` with n >= 1 (one line), plus a fixtures/policy-rot/hooks case whose self-test exits 0 silently, beside always-fails.sh. Mechanisation (D11.M5): already mechanical; the fix is one condition, about 0 s per merge, no policy line.

### D11-s3-04 — prepr.sh --self-test never drives main-flow step 5: `no version edit` wired to 0 still gives 553 passed, 0 failed (medium, bug)

- Claim: Replacing the main flow's `step "no version edit" $? "$STAMPED"` in tools/pr/prepr.sh with `step "no version edit" 0 "$STAMPED"` (prepr then reports ok on a branch that moves VERSION, the manifest version or a notes heading) leaves tools/pr/prepr.sh --self-test at 553 passed, 0 failed, identical to the unedited null arm, while gutting the version_edit() function it calls kills 9 cases.
- Mechanism: The self-test drives version_edit() through `ve`/`veco` and the `--version-edit` entry point pr-contract runs (exiting before the main flow), but no case runs the main flow over a VERSION-moving branch and reads step 5's verdict; the step's own comment calls it the cheaper detector for the same refusal, so its wiring has no live control. The refusal still exists later (pr-contract's --version-edit, the pre-edit hook, the stamp), which bounds the consequence to a slower detection.
- Evidence: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/prepr_arms.py` -> 0 self-test failures under step5_wiring_gutted (null 0; version_edit_gutted 9); mutants_killed=1 of 2; instrumented `tools/pr/prepr.sh:step (the main flow's step 5 call site) and its --self-test`
- Perturbation: the harness's two arms are the one-line production edits: step5_wiring_gutted (`$?` -> `0` at the step-5 call) and version_edit_gutted (`out=$(stamp_paths ...)` -> `out=""` in version_edit) -> failed: null 0 -> version_edit_gutted 9 (control fires); step5_wiring_gutted 0 (the gap)
- Null control: null arm 553 passed, 0 failed; version_edit_gutted 544 passed, 9 failed
- Property: Every refusal step of prepr.sh's main flow is driven by its --self-test end to end, so wiring a step's status to a constant turns the self-test red.
- Seams: `grep -nE '^\s*step "[^"]+" \$\?' tools/pr/prepr.sh (24 call sites; each one's `$?` -> `0` is a mutant prepr_arms.py's ARMS table can carry)`
- Fix and mechanisation (M5): tools/pr/prepr.sh --self-test: one end-to-end case running the main flow (PREPR_SKIP_CODE, a throwaway repo whose branch moves VERSION) and asserting `REFUSE no version edit`; then the other 23 step call sites measured by the same mutant (seam_rule). Mechanisation (D11.M5): a generic `step` wiring mutant lane, as policy_lint_mutants.mjs does for policy_lint, costs one script and about one self-test run per call site (about 15-25 min each here, provisional), so it fits a nightly lane, not a per-merge one.

## Non-findings

- tests/structure.py:ratchet refuses a one-unit rise on every budget key and every malformed budget; end to end a 210-line dead coordinator method trips 6 keys (D11.M4, C2 structure.py) — `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/structure_arms.py [--perturb]` — armA_keys_firing=18 of 18, armA_malformed_refused=3, armB_probe_new_fail_keys=6, null rc 0; --perturb (`current > budget + 1`) keys_firing 18 -> 0
- The claim-file validators (tests/env_drift.py claim_version_error, may_drift_error, may_drift_coverage_error; tests/card_rig.mjs claimVersionError) refuse every one-edit perturbation of both claim files (D11.M4, C2 claim files) — `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/claim_arms.py [--perturb]` — arms_refused=8 of 8, null_refusals=0; --perturb (version compared with itself) 8 -> 6
- rules_sync.mjs --check and fragments_sync.mjs --check refuse a one-character edit of every generated policy copy, an orphan .mdc and a deleted copy — `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/sync_arms.py [--perturb]` — rules_refused=32 of 32, fragment_refused=52 of 52, arms_not_applied=0, null rc 0/0; --perturb fragment_refused 52 -> 0
- The policy_lint mutation lane pins every enumerated corpus and record check (emptied -> acceptance red) and drives the exit status both ways — `node tools/policy/policy_lint_mutants.mjs` — 25 PIN lines (11 corpus, 13 record checks + record-known-bad), 0 survivors, `DRIVEN entry exit-status`, MUTANTS ok; wall 3m23s provisional (load ~8)
- tools/ci/gate.py:self_test refuses the removal of any one of the 21 gate-required contexts from REQUIRED — `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/gate_arms.py [--perturb]` — dropped_refused=21 of 21, null rc 0; --perturb (gate_required() returns the fixture) 21 -> 8
- budget_raise_gate.py:justified refuses a Raise justification whose last score line differs from the measured score.py line by one digit, a swapped verdict, a wrong trailing line or a missing payments line — `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/raise_body_arms.py [--perturb]` — digit_arms_refused=5 of 5, other_refusal_arms_refused=3 of 3, null accepted; --perturb (2-decimal compare) 5 -> 3
- counts.mjs:requiredContextsDrift is alive on the ruleset it reads (main-protect-checks 23698884), read through both the branch endpoint and the ruleset object — `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/ruleset_arms.py` — control arms 7 (bypass actor added), 1 (code-owner review off), 4 (`gate` dropped); null 0
- brief_lint.mjs's no-argument run refuses a rotted path or a literal count in the roster it reads and a renamed playbook path — `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/brief_arms.py` — control_3l_path 1, control_3l_count 1, control_playbook_path 1; null 0
- prepr.sh --self-test kills a gutted version_edit() (the function pr-contract's --version-edit shares) — `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/prepr_arms.py` — version_edit_gutted 544 passed, 9 failed vs null 553/0
- policy_lint --hooks refuses a wired hook whose refusal exit is gutted (its self-test then fails) — `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/hooks_arms.py` — control_refused=3 of 3 (pre-bash, pre-edit, stop-selfcheck); session-start refuses nothing and has no such arm

## Mechanisation (D11.M5)

All four findings are repairs to scripts that already exist; none needs a policy line. Ranked by cost per merge: D11-s3-03 (one condition in cmdHooks, ~0 s), D11-s3-02 (one line in brief_lint main(); a named r10 run took about 5 s here, provisional), D11-s3-01 (two extra API GETs per policy-docs run, ~20 lines), D11-s3-04 (one end-to-end self-test case now; a generic step-wiring mutant lane across prepr.sh's 24 call sites costs one self-test run per site, ~15-25 min each here, provisional, so it belongs in a nightly lane). The examined non-finding rows are already mechanical with a live control, so nothing further is proposed for them.

## Harnesses

- `dev/audit/rounds/round11/D11/s3/inventory.py`
- `dev/audit/rounds/round11/D11/s3/ruleset_arms.py`
- `dev/audit/rounds/round11/D11/s3/brief_arms.py`
- `dev/audit/rounds/round11/D11/s3/structure_arms.py`
- `dev/audit/rounds/round11/D11/s3/claim_arms.py`
- `dev/audit/rounds/round11/D11/s3/prepr_arms.py`
- `dev/audit/rounds/round11/D11/s3/sync_arms.py`
- `dev/audit/rounds/round11/D11/s3/hooks_arms.py`
- `dev/audit/rounds/round11/D11/s3/gate_arms.py`
- `dev/audit/rounds/round11/D11/s3/raise_body_arms.py`

## Not finished

- D11.M4: 163 of 229 inventory rows not perturbed: every seat-instrument (89), 19 pr-tools, 31 gate-scripts, 11 policy-tools, 11 ci-tools, 2 plan-tools (named in coverage.not_reached); and prepr.sh's other 23 `step ... $?` call sites (D11-s3-04's seam_rule).
- D11.M5: the same 163 rows carry no mechanisation verdict

## Leads

- D11-s2, `tools/policy/fixtures/required-contexts.json`, ruleset_objects.23698884.bypass_actors (live ruleset main-protect-checks): Two bypass actors with bypass_mode `always` (Integration 5094721, the hpo-ledger App, and DeployKey) on the ruleset carrying the `gate` context and the code-owner pull_request rule; read live 2026-11-16. D11.M2 Branch-Protection / NIST accountability: whether a merge to main can land with no review or a red `gate` through that App, and whether its use is provable from GitHub's records.
- D11-s1, `tools/policy/policy_lint_mutants.mjs`, CORPUS_CHECK_NAMES / LOOP_CHECK_NAMES enumeration: The mutation lane's universe is the two check lists; policy_lint's standalone modes (`--hooks` cmdHooks, and others the mode table names) are outside it, so the M1 inventory's control column for those rows is not this lane (D11-s3-03 measured one consequence).

## Exposure

GitHub's own records (D11's exception): GET repos/tvofi/heatpump_optimizer/rulesets and rulesets/22628467 read live 2026-11-16 ~20:30Z (gh api, read-only); rules/branches/main and rulesets/22628467, 23698884, 23937752 as captured by this seat's earlier run of the same day into data/. No pull request, check run or comment was read or written. Incidental: a `git grep` for the ruleset ids printed lines of dev/archive/carries/carry-1300.json, dev/archive/rosters/wave-d11-groups.json, dev/audit/harnesses/r10_carry_field_verdicts.json and dev/programme/rosters/wave-r10-groups.json (earlier-round carry and roster text), read only for whether another reader of the two rulesets exists.
