# Class sweep — I3 (round 9, thread S4)

**Property:** a required governance/CI check is skipped, runs a stale ref, or has a
bypassable boundary.

**Enumerator:** `tools/audit/round9/D14/sweep/I3/enumerate.py` (plus each finding's own
whole-package harness, re-run below). `PYTHONPATH=tests/hastub python3
tools/audit/round9/D14/sweep/I3/enumerate.py [--perturb hooks|budgets] [--null-control]`

## Positive control

| Finding | Command | Recorded value | This sweep |
|---|---|---|---|
| D11-s1-01 | `approvals_at_head.py` | 2 stale merges (#1621, #1623) | **cited** — needs `GITHUB_TOKEN` + 253 live REST GETs; a cloud sweep seat runs no `gh` and does not re-fetch a 253-merge window. Value taken from `tools/audit/round9/D11/s1/REPORT.md`. |
| D11-s1-02 | `direct_push_detectors.py` | 2 of 2 injected non-stamp pushes unreported | reproduced: `nonstamp_direct_injected=2`, `nonstamp_direct_reported=0` |
| D11-s1-03 | `privileged_pr_code.py` | 3 jobs (closures-autofix, claims-autofix, mutation-autofix) | reproduced exactly |
| D11-s1-04 | `approvals_at_head.py` | owner_gate_accepts_agent_declared | **cited** (same network reason as D11-s1-01) |
| D11-s2-01 | grep + `policy_budgets.json` | every entry of `files{}` is a seam (41) | reproduced (41 entries; disposition below) |
| D11-s2-02 | `.claude/settings.json` hooks | `--hooks` never reads `matcher` | reproduced + perturbation confirms |
| D13-s1-03 | `yield_rounds.mjs` | m3_body_answer_blocks=8 vs m3_max_engineering_class=1 | reproduced exactly |

## Null control / perturbation

- **D11-s2-02**: `--perturb hooks` sets `PreToolUse.matcher` to `"Bash"` (matches no edit
  tool) and re-runs the production `node .claude/workflows/policy_lint.mjs --hooks`. It
  still prints `HOOKS ok: 3 wired hook(s) exist and pass their own --self-test` — the
  checker moves from "correct" to "silently wrong" and never notices. There is no healthy
  fixture on which this probe reads zero (the checker draws no distinction at all between
  a matcher that fires and one that cannot) — recorded as an **exposure**, not a null
  control.
- **D11-s2-01**: `--perturb budgets` widens `.claude/rules/gate-scoping.md`'s body lines
  to 400 characters each **while holding the line count and the YAML frontmatter exactly
  fixed** (a naive per-line pad that also corrupts the `paths:` block reclassifies the
  file as always-loaded and produces a false "guard" — verified and discarded; see the
  script's `budgets_probe`). With the frontmatter intact: `role fixer` rises from
  ~6029→~9773 tokens against a cap+band of 6352 (over — because `gate-scoping.md`'s
  `paths:` glob matches the `fixer` role's representative `tests/entities.py` and
  `coordinator.py`), while the **per-file** check on `gate-scoping.md` itself
  (`r.lines > cap`, 61 unchanged) stays green throughout. This is the finding's exact
  mechanism, demonstrated moving.

## Every seam, dispositioned

**D11-s2-02** (1 seam — the repo's one `PreToolUse` hook group):

| path | disposition | note |
|---|---|---|
| `.claude/settings.json:hooks.PreToolUse` (matcher `Edit\|Write\|MultiEdit\|NotebookEdit`) | **instance** | probe above |
| `.claude/settings.json:hooks.SessionStart` | not applicable | event has no `matcher` field to game |
| `.claude/settings.json:hooks.Stop` | not applicable | event has no `matcher` field to game |

**D11-s2-01** (41 seams — `policy_budgets.json:files`):

| path | disposition | why |
|---|---|---|
| `.claude/workflows/fixtures/policy-rot/budgets.md` | not applicable | policy_lint's own self-test fixture, not a governed policy doc |
| `CLAUDE.md` | guarded | the one file in the `always_loaded_tokens` set (cap 3349+500); its own per-file cap is still line-only, but this aggregate is designed around exactly this file |
| 10 `.claude/rules/*.md` files (`brief-citations`, `ci-autofix`, `claim-files`, `comment-readback`, `defect-root-cause`, `delivery-status-tracking`, `finding-propagation`, `gate-scoping`, `ratchet-budgets`, `writing-for-agents`) | **instance** | each contributes to `corpus_tokens` (pooled, ~245 tokens of headroom at baseline) and, where its `paths:` glob matches a role's representative file, to that role's aggregate (also pooled: `fixer` 6352, `record` 7404, `policy` 9914). Both are pooled sums that never attribute growth to the file that caused it — a reviewer who sees "corpus/role over cap" can silence it by trimming *any other* capped file in the same PR, or none of them notice at all while headroom exists in other files. No check reads this file's own bytes/tokens as a standalone gate. |
| remaining 29 files (`.claude/skills/steward/SKILL.md`, `.claude/workflows/web-fragments.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `AGENTS.md`, `tests/README.md`, `tools/audit/README.md`, all 21 `tools/audit/briefs/*.md`, `tools/audit/harnesses/README.md`) | **instance** | not `RULE_FILE`-shaped, so never counted toward any role aggregate; only the pooled `corpus_tokens` (same near-zero-headroom caveat as above) can ever catch growth here, and it never says which file to fix |

**D11-s1-02** (direct-push detector): 1 seam — the detector's own coverage; both injected
non-stamp pushes (`d1`, `d2`) go unreported by every rule (`rule4 -> None`); the control
(`d3`, a merge-into-main subject) IS reported. **instance**.

**D11-s1-03** (privileged PR code): 3 seams, one per job — `tests.yml:closures-autofix`,
`tests.yml:claims-autofix`, `tests.yml:mutation-autofix`, each holding `contents: write`
+ `actions: write` on `pull_request` and executing `tests/closure.py` /
`tests/env_drift.py` from the PR's own checkout with the token persisted to disk.
**instance** ×3.

**D11-s1-01 / D11-s1-04** (approval-at-head staleness): seams are the two named merges
(#1621, #1623) and the owner-agent-declared approvals; **instance** (cited, not re-run —
see above).

**D13-s1-03** (body-answer-block miscount): 1 seam — `policy_lint.mjs`'s block-class
bucketing (`.claude/rules/defect-root-cause.md`, `.github/workflows/pr-contract.yml`).
Reproduced exactly: 8 body-answer blocks vs 1 for the largest taught engineering class.
**instance**.

## Count

N = 7 (all seven round-9 findings verified/weakened, all reproduced or cited). The
sweep's widening inside D11-s2-01 (39 additional files sharing the *same* mechanism the
finding's own seam_rule already claims — "every entry of `files{}` is a seam") is treated
as full disposition of that one finding's own scope, not as new class members: the
finding is already stated at whole-package level. No genuinely distinct new mechanism
surfaced. **N = 7, rca = true** (already ≥ 3; matches the judge).

## Barrier proposal

Two independent, cheap barriers, one per surviving gap:
1. **`--hooks` reads `matcher`.** Add a fixed table of `(event, required-tool-substring)`
   (e.g. `PreToolUse` must match at least one of `Edit|Write|MultiEdit|NotebookEdit`) and
   fail if the wired hook's matcher does not intersect it. Gate cost: milliseconds (pure
   string check against an already-parsed JSON), no new process.
2. **Per-file budget checks a byte/token delta, not only a line count**, OR the pooled
   `corpus_tokens`/`role` bands are tightened to zero (`_band: 0`) so *any* growth in a
   capped file — even one line's worth of characters — is attributed and refused at the
   PR that caused it, with the offending file named. The cheaper of the two: read
   `Buffer.byteLength` per file against a *second*, per-file byte cap recorded alongside
   the existing line cap (mirrors the existing `sizes()` row, which already computes
   `bytes` and discards it for this comparison).

`gate_seconds`: both are pure static analysis over already-loaded JSON/YAML; well under 1s
added to `policy_lint.mjs --hooks --budgets`.

## Exposure

- D11-s1-01, D11-s1-04, D13-s1-01(shared with I4)'s network-dependent enumerators were
  not re-run (no `GITHUB_TOKEN`/`gh` for a cloud sweep seat per this thread's brief); their
  recorded values are cited from REPORT.md rather than re-measured.
- `enum_gap.mjs`/`--stats` mode resolves its window end at the *live* `origin/main` ref
  (`policy_lint.mjs:mainRef()`), not at the pinned baseline SHA, so it cannot be run
  offline against 1936d5ca without temporarily rewriting `refs/remotes/origin/main`
  locally (done, then restored, for the local reproduction attempt in I4's sweep;
  reverted before this sweep exits).
