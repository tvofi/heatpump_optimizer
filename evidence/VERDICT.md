Fix review: merge 1a9b90965c31c6fd0093f623ec623e319fd6d3be

bus-nonce: 591a7fc5da599b9806df0e7db9562ac7

Round 1, re-issued after a body-only repair at the unchanged head. Measured from a detached worktree at `~/hpo-seats/r10s3/rev-2487`, merge base `76bb45628`. The prior `blocked` verdict named `pr-contract` red on the two `## Friction` `Carry:` markers being held in code spans. The live body now carries both markers bare and `## Red checks` names the check with its cause and cheaper detector. The tree did not move, so the earlier measurements stand, and the load-bearing ones were re-taken at this head.

## The prior block is cleared

The live PR body (read 2026-10-20T13:52:12Z) carries both Friction markers as bare text: `Carry: dismissed: same group, same two files; ...` and `Carry: dismissed: group-local technique, ...`. My own run, `python3 -I ~/hpo-seats/r10s3/orch-wt/tools/audit/carry_audit.py check --body <live body>`, prints `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc=0. The body ref `handoff-body/r10-dependabot-aiohttp` at `9d6f4dfa` differs from the live body only by a trailing blank line.

`## Red checks` now names `pr-contract`, states the cause (the markers sat inside a code span, which `carry_audit.py` reads as a quoted example), and names the cheaper detector `python3 -I tools/audit/carry_audit.py check --body <body>` — under a second and wired into `prepr.sh`. It also states `nightly-status` is main's own scheduled failure and not this tree's.

My re-run of the body check at this head: `node tools/policy/policy_lint.mjs --pr-body <live body> --head 1a9b90965c31c6fd0093f623ec623e319fd6d3be --title <live title> --author app/hpo-author --paths-file <pr files> --existing-file <base-existing files> --red nightly-status` prints `PR-BODY: 0 error(s)`; the local run prints `skip red-history` because it has no token, and CI's run carries one.

The body edit fired a new `pr-contract` run at this head: job 118666566977, started 2026-10-20T13:52:09Z, concluded **success** at 13:52:30Z. The two earlier red `pr-contract` runs at the same head are superseded; the red derivation excludes its own name by construction.

## The bump, re-verified at the unchanged head

The three GHSA ids are fixed in 3.14.4 and not before: `https://api.osv.dev/v1/vulns/<id>` returns for each `aiohttp` `[{'introduced': '0'}, {'fixed': '3.14.4'}]` for GHSA-2g87-pp6c-29x5, GHSA-494j-54xm-rwp3 and GHSA-5wr8-gcqf-gqf3. The previous pin in both files at the merge base was `aiohttp==3.14.3`.

The six open Dependabot alerts match the body: numbers 85-90, `state=open`, `fixed_at=null`, 85-87 on `tests/requirements-ci.txt` and 88-90 on `tests/requirements-typing.txt`, and no aiohttp pin outside those two manifests.

Both files pin `aiohttp==3.14.4` with 161 sha256 digests each; the two sets are equal and each equals PyPI's complete published 161-file set for 3.14.4. The typing lock's `yarl==1.25.1` carries 138, equal to PyPI's 138. No aiohttp pin remains at 3.14.3 in any tracked manifest; `tests/typing_budgets.json`'s `census.environment` value is recorded provenance, not an asserted pin.

Every changed line is resolver-explained. CI lock, 282 changed lines: 2 version lines and 280 hash lines (119 removed, 161 added). Typing lock, 540: 4 version lines, 522 hash lines (aiohttp 280, yarl 104 to 138 = 242), and 14 header lines (13 comments, one blank). A block-level parse at base and head returns no package added, none dropped, no hash move at an unchanged version, and no constraint removed. The only moved packages are aiohttp and yarl, and yarl's move is forced: aiohttp 3.14.4's `requires_dist` carries `yarl<2.0,>=1.25.1`, `homeassistant==2026.9.3` pins `aiohttp==3.14.3`/`yarl==1.24.5`, and the typing job installs the lock `--require-hashes --no-deps` (`.github/workflows/tests.yml:680`), so the lock decides.

`~/hpo-seats/r10s3/rev-2487-ev/VERDICT.md`'s predecessor records the remaining checks at this unchanged head: delivery row `dev/programme/delivery/2487.md` names `R10-DEPENDABOT-AIOHTTP`; all template headings present; `git merge-tree --write-tree origin/main <head>` exits 0; `env_drift.py --claims-only` prints "claims hygiene ... ok"; VERSION, the manifest version and the notes heading are untouched.

## CI at the head

Read through `/repos/tvofi/heatpump_optimizer/commits/1a9b90965c31c6fd0093f623ec623e319fd6d3be/check-runs` at 2026-10-20T13:54:27Z. `pr-contract` success (job 118666566977). `typing` success, so the typing lock installed with the new pins and the ruler passed. All CodeQL, arch-score, budget-raise-gate, briefs, closure-scope, delivery-status, hassfest, mutation, policy-docs, scope, validate-hacs, wave-script, browser, env-matrix and instrument-self-tests runs are green. `fast (3.14)` and `closures` were still in progress at that read. `nightly-status` is red and is main's own scheduled failure (scheduled Tests runs 39387919507 and 39218718759 both concluded failure on `main`); this diff reaches none of what that check reads.

## RESULT lines

```
RESULT pr_contract_latest=success job=118666566977 started=13:52:09Z completed=13:52:30Z
RESULT carry_audit routed=2 unrouted=0 rc=0
RESULT pr_body_errors=0 local_red_history=skip_no_token
RESULT ghsa=GHSA-2g87-pp6c-29x5 fixed_in=3.14.4 introduced=0
RESULT ghsa=GHSA-494j-54xm-rwp3 fixed_in=3.14.4 introduced=0
RESULT ghsa=GHSA-5wr8-gcqf-gqf3 fixed_in=3.14.4 introduced=0
RESULT dependabot_open=6 manifests=2 numbers=85-90 fixed_at=null_all
RESULT ci aiohttp=3.14.4 hashes=161 pypi=161 equal=True
RESULT typing aiohttp=3.14.4 hashes=161 pypi=161 equal=True ci_equals_typing=True
RESULT typing yarl=1.25.1 hashes=138 pypi=138 equal=True
RESULT changed_lines ci=282 typing=540 all_explained=True
RESULT packages_added=0 dropped=0 same_version_hash_moves=0 constraints_removed=0
RESULT merge_tree_exit=0 conflicts=0
RESULT nightly_status=main_scheduled_failure not_this_pr=True
RESULT head_unchanged_since_block=True
```
