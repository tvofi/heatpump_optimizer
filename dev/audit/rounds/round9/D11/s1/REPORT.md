# D11-s1 finder report, audit round 9 (rendered)

This file was rendered by the box B3 host from this seat's `report.json`, field by field and with no words added: the seat could not write a `.md` file on this host. `report.json` is the record; where the two differ, it wins.

- Dimension: D11
- Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1

## Exposure

GitHub API (read-only GETs): rulesets 22628467/23698884/23937752 and rules/branches/main; PR objects, reviews, issue comments and merged-head check-runs for the 253 first-parent PR merges since 2026-09-17T04:58Z (52 answer 404); HTTP status of issues #1040-#1175; last 5 releases; SLSA attestation for v6.7.1; /actions/secrets (403). git history of main (first-parent). Record read to compare with the live ruleset: docs/decisions/0008, 0009, 0011, 0013; greps of docs/HANDOVER.md. OpenSSF Scorecard docs/checks.md fetched from raw.githubusercontent.com. NOT fetched (egress refused/404): SLSA spec, OWASP LLM Top 10, NIST AI 100-1/600-1, ISO/IEC 42001, OpenSSF Best Practices - applied as unverified external references. Earlier-round evidence: listed file names of tools/audit/round8/D11/ once (ls); read none, cite none. REPORT.md could not be written: the host's file tool refuses a report .md from a sub-agent, so this JSON and the final message carry its content.

## Coverage

| step | depth | evidence |
|---|---|---|
| D11.M1 | deep | inventory.py (17 contexts -> jobs), live rulesets with both arms (rulesets endpoint vs rules/branches), policy_lint check classes (12, acceptance), hooks both arms, stamp.py rule 4 driven; D11-s1-01, -02 |
| D11.M2 | spot | Scorecard 10 checks hand-evaluated against fetched docs/checks.md; SLSA via the live attestation; NIST/OWASP/ISO/Best-Practices applied from memory (text unreachable); D11-s1-03, -04 |
| D11.M3 | deep | policy_lint --budgets, --stats (10 would-open, head-moved 18 PRs), policy_lint_mutants (22) + unmutated_checks.mjs; conformance over all 201 readable merges in the window (not a sample) |
| D11.M4 | deep | every finding carries an in-memory production perturbation that moves its number; ruleset read both arms (rulesets/<id> vs rules/branches/main); no live write |

## Findings

### D11-s1-01: A code-owned change pushed after the owner approval merges on that stale approval (dismiss_stale_reviews=false)

```json
{
  "id": "D11-s1-01",
  "scope": "D11-s1",
  "step": "D11.M1",
  "severity": "high",
  "title": "A code-owned change pushed after the owner approval merges on that stale approval (dismiss_stale_reviews=false)",
  "claim": "Ruleset 23698884's pull_request rule has dismiss_stale_reviews_on_push=false and require_last_push_approval=false, so 2 of 201 readable merges since the rule landed (#1621, #1623) merged a code-owned file changed after the owner's last approval, with no approval at the merged head from anyone, although decisions 0008 3(d)/0009 step 6 record the head-moved rule as enforced by GitHub.",
  "mechanism": "GitHub keeps an approval across later pushes when dismiss_stale_reviews_on_push is false; require_code_owner_review is then satisfied by an owner approval on an older head. The only in-tree approval-at-head check (budget_raise_gate.py:approval) runs only for budget raises.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/approvals_at_head.py",
    "harness_path": "tools/audit/round9/D11/s1/approvals_at_head.py",
    "value": 2,
    "unit": "merges (RESULT owned_change_after_owner_approval)",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B3, 4-CPU Linux container, CPython 3.14.0rc2 / node v22.22.2",
    "cpu_or_wall": "count",
    "contention_note": "shared box (1 heavy + 3 light seats); count, contention-immune",
    "tolerance": "exact",
    "load1": 4.57,
    "thread_factor": 1.0
  },
  "instrumented_symbol": ".claude/workflows/budget_raise_gate.py:approval (+ live ruleset 23698884 pull_request.parameters)",
  "perturbation": {
    "change": "--perturb commit-clause: one-line in-memory edit of approval(), `if last.get(\"commit_id\") != head:` -> `if False:`",
    "expected_direction": "to_zero",
    "observed_value": 0
  },
  "metric_definition": "Merges in the window whose owner's last APPROVED review is not on the merged head and whose branch changed a CODEOWNERS-owned file after that review.",
  "phenomenon_property": "No pull request may merge with a code-owned path changed after the code owner's last approval; an approval covers only the commit it was given on.",
  "seam_rule": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/approvals_at_head.py  (every first-parent PR merge since the rule landed; seams = merges printed under 'code-owned change after the owner's last approval')",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/approvals_at_head.py",
    "value": "app_approval_not_at_merged_head=0/128",
    "note": "the approver App, same predicate with its identity constants: 0 stale; the effect is specific to post-approval pushes"
  },
  "reproduction_steps": [
    "git log --format='%h %s' ecb7af8edd..99fcc3f2f3 -- tests/harness.py  (084c6a27 after the owner approval)",
    "git show --stat edf38de0  (tests/mutation_table.py after owner approval at 0a1424cc)",
    "curl -sS https://api.github.com/repos/tvofi/heatpump_optimizer/rulesets/23698884"
  ],
  "proposed_fix_scope": "Owner: set dismiss_stale_reviews_on_push=true (or require_last_push_approval=true) on ruleset 23698884; correct 0008/0009's status if the owner keeps false.",
  "files": [
    ".github/CODEOWNERS",
    ".claude/workflows/budget_raise_gate.py",
    "docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md"
  ],
  "stop_rule_class": "bug",
  "class_guess": "I3"
}
```

### D11-s1-02: A non-stamp direct push to main over the DeployKey bypass is reported by no enumerator

```json
{
  "id": "D11-s1-02",
  "scope": "D11-s1",
  "step": "D11.M4",
  "severity": "high",
  "title": "A non-stamp direct push to main over the DeployKey bypass is reported by no enumerator",
  "claim": "With main-protect-checks' bypass [{DeployKey, actor_id null, always}], a single-parent first-parent commit that is not a stamp's output passes stamp.py:rule4_problem whenever the window also holds one noted PR merge: 0 of 2 injected rows reported, while a two-parent direct merge is reported 1/1.",
  "mechanism": "blind_merges only considers parents>=2; enumeration_went_blind fires only when no PR at all was read; policy_lint.mjs's enumerator skips any first-parent with no PR as a stamp. Nothing compares a single-parent commit's files with STAMP_WRITES.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/direct_push_detectors.py",
    "harness_path": "tools/audit/round9/D11/s1/direct_push_detectors.py",
    "value": 0,
    "unit": "of 2 injected non-stamp direct pushes reported (RESULT nonstamp_direct_reported)",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B3, 4-CPU Linux container, CPython 3.14.0rc2 / node v22.22.2",
    "cpu_or_wall": "count",
    "contention_note": "shared box (1 heavy + 3 light seats); count, contention-immune",
    "tolerance": "exact",
    "load1": 5.05,
    "thread_factor": 1.0
  },
  "instrumented_symbol": "tools/release/stamp.py:rule4_problem (blind_merges, enumeration_went_blind); tests/env_drift.py:STAMP_WRITES; live rulesets 23698884/23937752",
  "perturbation": {
    "change": "--perturb parents-ge-1: in-memory edit of blind_merges, `if parents >= 2 and` -> `if parents >= 1 and`",
    "expected_direction": "up",
    "observed_value": 2
  },
  "metric_definition": "Injected single-parent non-stamp rows (plain subject; stamp-shaped subject) whose sha appears in rule4_problem's refusal for a window with one correctly-noted PR merge.",
  "phenomenon_property": "Every commit that reaches main without a pull request is either a stamp's output (files within STAMP_WRITES) or is named by a detector.",
  "seam_rule": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/direct_push_detectors.py  (rows d1,d2 + control d3; history line lists every single-parent first-parent commit since v6.5.0)",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/direct_push_detectors.py",
    "value": "two_parent_control_reported=1; history_nonstamp_direct=0 of 16",
    "note": "the detector does fire on a two-parent direct merge; the real history holds no instance, so severity is capability not incidence"
  },
  "proposed_fix_scope": "rule4_problem refuses a single-parent first-parent commit whose file set is not within STAMP_WRITES (stamp.py, ~5 lines, plus its self-test arm); optionally the same in delivery_status.collect.",
  "files": [
    "tools/release/stamp.py",
    ".claude/workflows/policy_lint.mjs"
  ],
  "stop_rule_class": "bug",
  "class_guess": "I3"
}
```

### D11-s1-03: Three pull_request jobs execute the PR's own code-owned scripts while holding contents:write + actions:write

```json
{
  "id": "D11-s1-03",
  "scope": "D11-s1",
  "step": "D11.M2",
  "severity": "medium",
  "title": "Three pull_request jobs execute the PR's own code-owned scripts while holding contents:write + actions:write",
  "claim": "tests.yml closures-autofix, claims-autofix and mutation-autofix check out head_ref with secrets.CLOSURES_PUSH_TOKEN || github.token (persisted) and then import the PR's own tests/closure.py (and tests/env_drift.py), so PR code runs with a write token before the owner review its code ownership requires.",
  "mechanism": "A pull_request run uses the PR's workflow and files; these jobs do not restore the executed scripts from the base as decision 0013 does for pinned graders, and actions/checkout persists the token in .git/config by default.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/privileged_pr_code.py",
    "harness_path": "tools/audit/round9/D11/s1/privileged_pr_code.py",
    "value": 3,
    "unit": "jobs (RESULT pr_jobs_with_write_running_pr_code)",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B3, 4-CPU Linux container, CPython 3.14.0rc2 / node v22.22.2",
    "cpu_or_wall": "count",
    "contention_note": "shared box (1 heavy + 3 light seats); count, contention-immune",
    "tolerance": "exact",
    "load1": 6.5,
    "thread_factor": 1.0
  },
  "instrumented_symbol": ".github/workflows/tests.yml:jobs.closures-autofix|claims-autofix|mutation-autofix",
  "perturbation": {
    "change": "--perturb restore: prepend `git checkout \"$BASE\" -- <executed paths>` to each such job (in memory)",
    "expected_direction": "to_zero",
    "observed_value": 0
  },
  "metric_definition": "Jobs on pull_request with a write permission that execute a repo script not restored from the base earlier in the same job.",
  "phenomenon_property": "No job holding a write token runs code the pull request controls before review.",
  "seam_rule": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/privileged_pr_code.py",
  "proposed_fix_scope": "Restore tests/closure.py, tests/env_drift.py, tests/mutation_table.py from pull_request.base.sha before the merge step of the three jobs; persist-credentials: false until the push step. Whether CLOSURES_PUSH_TOKEN is set is unknown (secrets API 403) and should be stated by the owner.",
  "files": [
    ".github/workflows/tests.yml"
  ],
  "stop_rule_class": "bug",
  "class_guess": "I3"
}
```

### D11-s1-04: Owner approvals given by the orchestrator are indistinguishable from the owner's in GitHub's record

```json
{
  "id": "D11-s1-04",
  "scope": "D11-s1",
  "step": "D11.M2",
  "severity": "medium",
  "title": "Owner approvals given by the orchestrator are indistinguishable from the owner's in GitHub's record",
  "claim": "Of 90 tvofi APPROVED reviews on readable merges since 2026-09-17, 29 state in their body that the orchestrator gave them and 46 are empty; budget_raise_gate.py:approval accepts the agent-given approvals as the owner's on 27/27 PRs, so the ruleset's only human-oversight point is not provable from the record.",
  "mechanism": "Delegated approvals are posted under the owner's own account; every owner-approval consumer keys on login/id/type.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/approvals_at_head.py",
    "harness_path": "tools/audit/round9/D11/s1/approvals_at_head.py",
    "value": "27/27",
    "unit": "PRs whose agent-declared owner approval at merged head the production predicate accepts (RESULT owner_gate_accepts_agent_declared)",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B3, 4-CPU Linux container, CPython 3.14.0rc2 / node v22.22.2",
    "cpu_or_wall": "count",
    "contention_note": "shared box (1 heavy + 3 light seats); count, contention-immune",
    "tolerance": "exact",
    "load1": 4.57,
    "thread_factor": 1.0
  },
  "instrumented_symbol": ".claude/workflows/budget_raise_gate.py:approval",
  "perturbation": {
    "change": "--perturb reattribute: reviews whose body says the orchestrator gave them carry a distinct identity (the fix's identity model)",
    "expected_direction": "down",
    "observed_value": "2/27"
  },
  "metric_definition": "PRs with an owner APPROVED review at merged head whose own body declares the orchestrator gave it, for which approval(reviews, head) returns True.",
  "phenomenon_property": "An approval that discharges a human-oversight obligation is attributable, from GitHub's record, to the human or to the delegate that gave it.",
  "seam_rule": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/approvals_at_head.py  (owner_agent_declared, owner_approval_empty_body, owner_gate_accepts_agent_declared)",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/approvals_at_head.py",
    "value": "owner_approval_empty_body=46/90",
    "note": "the self-declared count is a lower bound; 46 more carry no statement either way"
  },
  "proposed_fix_scope": "Owner decision: delegated approvals under a distinct code-owner identity (second account or a team), or a refusal in budget_raise_gate for delegated approvals; no change is proposed to the mandate itself.",
  "files": [
    ".github/CODEOWNERS",
    ".claude/workflows/budget_raise_gate.py"
  ],
  "stop_rule_class": "bug",
  "class_guess": "new"
}
```

## Non-findings

```json
{
  "claim": "Every required context of main-protect-checks is produced by exactly one workflow job (16/17 unpinned by integration_id, recorded in decision 0013; .github/workflows/ is code-owned; no job holds checks:write or statuses:write)",
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/inventory.py",
  "value": "required_contexts=17 unproduced=0 multi=0 without_integration_id=16; renamed-context perturbation -> unproduced=1"
}
```

```json
{
  "claim": "policy_lint corpus lint + acceptance clean",
  "command": "HPO_PLANDATA=$(mktemp -d) /opt/node22/bin/node .claude/workflows/policy_lint.mjs",
  "value": "rc 0; 0 errors across 40 policy files; FIXTURE ok 91 errors / 193 pins / 12 classes; KNOWN-BAD 7 of 7; required-contexts skipped locally (gh ENOENT)"
}
```

```json
{
  "claim": "Every policy_lint check class is alive: the mutation lane kills all 22 mutants; the three wired checks it does not enumerate (checkCitations, checkNoGh, checkSunset) are each refused by the acceptance when emptied",
  "command": "/opt/node22/bin/node .claude/workflows/policy_lint_mutants.mjs; HPO_PLANDATA=$(mktemp -d) /opt/node22/bin/node tools/audit/round9/D11/s1/unmutated_checks.mjs",
  "value": "MUTANTS ok (22); not_in_mutation_lane=3, of which acceptance refuses emptied=3; control checkIndex rc=1; --perturb enumerate -> 0"
}
```

```json
{
  "claim": "Hooks wired and self-testing; the failing-fixture arm refuses",
  "command": "node .claude/workflows/policy_lint.mjs --hooks; ... --hooks .claude/workflows/fixtures/policy-rot/hooks/self-test-fails.json",
  "value": "3 hooks ok (8/16/23 passed); fixture arm rc=1 'HOOKS REFUSED: 4 of 4'"
}
```

```json
{
  "claim": "Policy budgets: all five aggregates within cap+_band (all above the recorded cap)",
  "command": "node .claude/workflows/policy_lint.mjs --budgets",
  "value": "always-loaded 3461 vs 3349+500; corpus 55688 vs 55433+500; fixer 6029 vs 5852+500; record 7132 vs 6904+500; policy 9728 vs 9414+500"
}
```

```json
{
  "claim": "Scorecard Dangerous-Workflow: no pull_request_target, workflow_run checks out the default branch, untrusted contexts routed via env",
  "command": "grep -n 'github.event.pull_request.title|head_ref|pull_request_target' .github/workflows/*.yml",
  "value": "0 untrusted interpolations into run:; 0 pull_request_target"
}
```

```json
{
  "claim": "Scorecard Pinned-Dependencies",
  "command": "grep -h 'uses:' .github/workflows/*.yml | grep -c '@[0-9a-f]{40}'",
  "value": "79/79 SHA-pinned; pip --require-hashes everywhere; npm ci"
}
```

```json
{
  "claim": "Every direct push to main since v6.5.0 is stamp-shaped",
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/direct_push_detectors.py",
  "value": "history_single_parent=16, history_nonstamp_direct=0"
}
```

```json
{
  "claim": "Conformance on readable merges since the pull_request rule landed",
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/approvals_at_head.py",
  "value": "pr-contract first run green 187/201; red required check answered 23/23; Fix review: merge <head> by non-author 166/201 (20 by PR author's own login); App approvals at head 128/128; approval at head 199/201"
}
```

```json
{
  "claim": "SLSA provenance exists for the latest tag",
  "command": "curl .../attestations/sha256:$(git archive --format=tar v6.7.1 | sha256sum)",
  "value": "1 Sigstore bundle, predicate https://slsa.dev/provenance/v1, builder release.yml@refs/tags/v6.7.1 (Build ~L2; L3 needs isolated signing). Scorecard Signed-Releases: last 5 releases carry 0 assets"
}
```

## Unfinished

- **D11.M2**: SLSA/NIST AI 100-1 and 600-1/OWASP LLM/ISO 42001/Best-Practices text not fetched (proxy refused); Scorecard binary not run (absent).
- **D11.M3**: Conformance excludes the 52 merges whose PR the API 404s; docs/decisions and HANDOVER staleness is outside this seat's cells (leads). Lines added per line deleted across the corpus over the window not measured.
- **D11.M1**: prepr.sh, brief_lint.mjs and tests/structure.py rows not given their own positive control here (covered by required contexts briefs/fast).

## Harnesses

- `tools/audit/round9/D11/s1/approvals_at_head.py`
- `tools/audit/round9/D11/s1/direct_push_detectors.py`
- `tools/audit/round9/D11/s1/privileged_pr_code.py`
- `tools/audit/round9/D11/s1/inventory.py`
- `tools/audit/round9/D11/s1/unmutated_checks.mjs`

## Leads

- owner unknown, `docs/decisions/0011-app-authored-identity.md` `Context: 'about eleven of its merged pull requests now return 404'`: Measured 52 of 253 first-parent PR merges since 2026-09-17 answer 404 (61 of merged PRs >= #1000; 53 whose head commit is by tvofi-seat-author); the record undercounts the purge and conformance over those merges is unmeasurable from GitHub.
- owner unknown, `docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md` `step 3(d) dismiss_stale_reviews_on_push: true`: Status reads as enforced by GitHub; live ruleset 23698884 has false (see D11-s1-01). 0009 step 6 inherits the claim.
- owner unknown, `tests/delivery_status.py` `collect`: Docstring: 'nothing else reaches main with two parents under the ruleset' - false under the DeployKey bypass; single-parent direct pushes are skipped silently (same class as D11-s1-02).
