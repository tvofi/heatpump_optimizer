# D11 round 8, seat s2: public-standards scorecard and per-merge conformance

Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`. The tree is a detached worktree at `/home/claude/audit-r8/seats/D11-s2`.
The artifact of record is `report-s2.json`. Every harness runs from the tree root with
`PYTHONPATH=tests/hastub`, the 5 BLAS thread variables set to 1, and `TMPDIR=/home/claude/audit-r8/tmp/D11-s2`.
Every number here is a count, so none is contention-sensitive. load1 was quoted at 7.8 to 16.8.

## Method
1. Standards text was fetched, not remembered: SLSA v1.0 levels (slsa.dev/spec/v1.0/levels), and Scorecard's
   docs/checks.md plus docs/checks/internal/checks.yaml. The Pinned-Dependencies bar is: "a dependency
   explicitly set to a specific hash". The Token-Permissions bar is: "read-only at the top level".
2. The Scorecard checks were evaluated by hand over the parsed workflow YAML (`s2_scorecard.py`), because the
   Scorecard tool cannot see this repository from the seat.
3. The owner surface of the required checks was derived from the recorded required-context fixture, the
   workflow jobs and a transitive import walk, then checked against CODEOWNERS (`s2_owner_closure.py`).
   pr-contract's own command was then driven under a one-line edit.
4. The release path was run by executing release.yml's own step scripts in a scratch clone, with `gh`
   stubbed (`s2_release_gate.py`).
5. Conformance was sampled per merge (`s2_conformance.py` over `s2_conformance_snapshot.json`).
   The sample rule is `git log --first-parent --merges cdf82da | head -40 | every 7th`, which gives n=6.

## Findings
| id | severity | number | perturbation |
|---|---|---|---|
| D11-s2-01 | high | 8 unowned files executed by required jobs from the PR checkout. Appending 1 line to any of the 3 that policy_lint.mjs loads turns pr-contract's refusal (rc 1) into a pass (rc 0). Null control: the same append to an unloaded file leaves rc at 1. | owning the 8 files -> 0 |
| D11-s2-02 | high (provisional: tag rulesets unreadable here) | release.yml publishes and attests an unmerged commit in 2/2 event paths (a main commit: 2/2) | 1-line ancestry guard -> 0/2 off-main, 2/2 on-main |
| D11-s2-03 | low | 12 CI install commands not hash-pinned | --require-hashes on 1 line -> 11 |

Root of D11-s2-01: CODEOWNERS says its surface is "DERIVED" by R6's `codeowners_gap.py`, whose rule
counts only scripts called through an interpreter and never follows an import. That misses:
- `./tests/run.sh` (the `fast` job)
- `./tests/derive_closures.sh` (the `closures` job)
- `counts.mjs`, `render_md.mjs` and `vendor/markdown-it.min.js`, which run inside pr-contract, briefs and
  policy-docs' self-test steps.

Unlike policy-docs (#1403), pr-contract and briefs grade the pull request with the pull request's own
copies of these files.

## Standards scorecard
| criterion | standard | executed check | result | gap |
|---|---|---|---|---|
| Pinned-Dependencies (actions) | Scorecard | s2_scorecard.py `uses_unpinned` | 0 unpinned | none |
| Pinned-Dependencies (packages) | Scorecard | `pinned_deps_unpinned` | 12 | D11-s2-03 |
| Token-Permissions | Scorecard ("read-only at the top level") | `token_permissions_top_level_write` | 2 (codeql.yml security-events, release.yml contents) | move both writes to job level (release already restates them at job level) |
| Dangerous-Workflow | Scorecard | untrusted contexts in run: / pull_request_target | 0 / 0 | none |
| SAST | Scorecard | CodeQL analyze workflows; required Analyze contexts | 1 workflow; 3 required contexts | none |
| Security-Policy | Scorecard / Best Practices vulnerability_report_process | SECURITY.md contact | private-advisory URL present | none |
| Signed-Releases | Scorecard ("*.sig, *.sigstore, *.intoto.jsonl ... in release assets") | list_releases: releases carry no assets; attestation lives in the attestations API | fails the check's letter (documented PARTIAL in release.yml) | attach the attestation bundle as a release asset |
| Code-Review | Scorecard | O1 over the sample | 6/6 approved at the merged head by a non-author identity | see NIST row |
| CI-Tests | Scorecard | O2, plus all required contexts green at head in the listing | 6/6 | filter=latest only |
| Maintained | Scorecard | release cadence | 100 releases 2026-08-26..09-23 | none |
| Branch-Protection | Scorecard | not evaluated (no rulesets endpoint in the MCP tools; s1's row) | n/a | unfinished |
| Build track | SLSA v1.0 | release.yml: hosted runner plus attest-build-provenance (Sigstore-signed) | Build L2 for the source-tree subject | L3 needs the signing step isolated from user steps (a reusable workflow). Independent of the level, D11-s2-02: the provenance attests unreviewed commits too. |
| change control / test policy / release notes | Best Practices badge | public VCS, required test contexts, RELEASE_NOTES.md sectioned per tag (release.yml extracts it) | met | none |
| accountability (reviewer != author provable from records) | NIST AI RMF GOVERN 2.1 / AI 600-1 | review logins over the sample | author hpo-author[bot], approver hpo-approver[bot] (5/6) or tvofi (1/6) | Both Apps are keyed by the orchestrator (decision 0011). Fix-review verdicts post as `tvofi` (app_approve.sh `VERDICT_AUTHORS="tvofi"`, whose header says it "cannot prove WHICH seat's word a tvofi verdict carries"). #1426's dismissed review as tvofi reads "Approved as codeowner (owner mandate, session-only, 12h)". GitHub's records therefore cannot tell the human code-owner oversight point apart from a session using the owner's login. |
| human oversight points | NIST AI 600-1 | CODEOWNERS plus require_code_owner_review | exists | weakened by D11-s2-01 (the surface is not fully owned) and by the row above |
| excessive agency | OWASP LLM06 (2025) | `write_jobs_executing_pr_checkout` | 2 (closures-autofix, claims-autofix: contents+actions write over PR-head code) | same-repo PRs only; the PR author already holds write, so this adds no escalation |
| prompt injection / improper output handling | OWASP LLM01 / LLM05 | PR body read from the API into a file, title via env: | 0 shell interpolations | none |
| continual improvement | ISO/IEC 42001 10.1 | codeowners_gap.py (the R6 countermeasure) re-derived against this seat's closure | 37/37 by its own rule, 8 missed by an import-aware rule | the countermeasure's rule is narrower than the property it claims |

## Conformance table (s2_conformance.py)
| PR | merge | head | O1 approval@head, non-author | O2 first pr-contract green | O3 delivery row | reds@head |
|---|---|---|---|---|---|---|
| #1489 | cdf82da | 3c7856cb | yes | yes | no (the baseline merge itself) | 0 |
| #1485 | ec202e0 | 486b2b04 | yes | yes | yes | 0 |
| #1483 | 9de8fe2 | 2f83ef8e | yes | yes | yes | 0 |
| #1426 | 43dd4c3 | 612bce49 | yes (tvofi) | yes | yes | 0 |
| #1429 | 06ec54b | f15767f7 | yes | yes | yes | 0 |
| #1431 | 5b83e36 | bb1a7602 | yes | yes | yes | 0 |

Totals: O1 6/6, O2 6/6 (an upper bound: the check-runs listing is filter=latest), O3 5/6, O4 0/0 (vacuous).
Perturbation: keying O1 on the merge's first parent instead of the PR head gives 0/6.

## Ranked changes
1. pr-contract and briefs restore `.claude/workflows/{*.mjs,*.py,vendor}` from the base SHA before grading.
   The step already exists in policy-docs. Cost: about 6 lines and about 1 s per merge. Moves: Code-Review,
   NIST oversight (D11-s2-01).
2. An ancestry guard in release.yml, plus a v* tag ruleset limited to the deploy key. Cost: 1 line plus one
   ruleset, 0 s per merge. Moves: SLSA provenance meaning, Branch-Protection (D11-s2-02).
3. CODEOWNERS for tests/run.sh, tests/derive_closures.sh, counts.mjs, render_md.mjs and vendor/, and extend
   codeowners_gap.py with bare `./` invocations and an import walk. Cost: 5 lines plus about 30 lines.
4. Top-level `permissions: contents: read` in release.yml and codeql.yml. Cost: 2 lines. Moves: Token-Permissions.
5. Hashed lock files for CI installs. Cost: about 30 lines. Moves: Pinned-Dependencies (D11-s2-03).
6. Attach the Sigstore bundle as a release asset. Cost: about 5 lines. Moves: Signed-Releases.

## Harness gaps
- finding.schema.json's id pattern rejects the `D11-s2-NN` ids this round mandates. It is the only schema
  error in report-s2.json.
- The MCP get_check_runs method has no `filter=all`.
- The local clone lacks objects for tags before v6.6.6.

## Exposure
GitHub API through the MCP tools, read-only:
- list_releases and list_tags
- #1489: get and get_reviews
- #1485, #1483, #1426, #1429, #1431: get_reviews and get_check_runs; get_check_runs also for #1489

Git history: `git show cdf82da:tools/audit/round6/D11/fix/codeowners_gap.py`.
Standards pages: the three fetched in Method step 1.

No audit register or earlier findings were read.
