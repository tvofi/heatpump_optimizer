Fix review: blocked 1a9b90965c31c6fd0093f623ec623e319fd6d3be root-cause-unanswered: pr-contract went red, unanswered

bus-nonce: 591a7fc5da599b9806df0e7db9562ac7

Round 1. Measured at `1a9b90965c31c6fd0093f623ec623e319fd6d3be` from a detached worktree (`/Users/timmalmstrom/hpo-seats/r10s3/rev-2487`), merge base `76bb45628`. The body's `## Head` names `9e39a4718`; the measured head is one commit further, and `git diff --stat 9e39a471..1a9b90965` is exactly `dev/programme/delivery/2487.md | 1 +`, so every number below carries to the measured head. The requirements content is sound and merge-ready; the single blocker is a required check that is red on this head for a body defect.

## The block: `pr-contract` went red and the body does not answer it

`pr-contract` is a required context (ruleset 23698884). It is red twice at this head, both times on the current body: the push-time run (job 118654914880, started 13:29:04Z) and the follower run (job 118656817895, started 13:32:52Z). The failing step is `Every finding the body records names its destination`:

```
UNROUTED body item a3091a12 (## Friction) [section]: '- `fixer-brief: contradiction`: ...'
UNROUTED body item 6b7da52b (## Friction) [section]: '- `null-control: unenforced`: ...'
CARRY-AUDIT: 2 finding item(s): 0 routed, 2 unrouted, 0 bad destination(s)
```

Both `## Friction` bullets end with a `Carry: dismissed: <reason>` marker, but each marker sits inside a backtick code span, and `tools/audit/carry_audit.py` states and implements that a `Carry:` inside a code span is a quoted example, never a marker. Control: unbackticking only those two markers in a copy of the body changes the tool's answer from the failure above to `2 routed, 0 unrouted, rc=0`; nothing else in the body differs, so the defect is exactly the code span, not the wording or the destination.

The body's `## Red checks` says "No CI check has run on this branch yet; the orchestrator opens the pull request." That was true when written, but `pr-contract` has now gone red on the branch and the body names and answers no check. The cheaper detector is the body check itself, standing cost about one second: `python3 -I tools/audit/carry_audit.py check --body <body>`.

Fix: unbacktick `Carry: dismissed: ...` on both Friction lines (a body edit; `pr-contract` re-runs on `pull_request: [edited]`), and answer the red in `## Red checks` as the root-cause rule requires.

## The bump's claims, verified

The three GHSA ids the body and the typing header name are fixed in 3.14.4 and not before. `https://api.osv.dev/v1/vulns/<id>`, one call per id, returns for each `aiohttp` `[{'introduced': '0'}, {'fixed': '3.14.4'}]`: GHSA-2g87-pp6c-29x5, GHSA-494j-54xm-rwp3, GHSA-5wr8-gcqf-gqf3. The previous pin was `aiohttp==3.14.3` in both files at the merge base (`tests/requirements-ci.txt:30`, `tests/requirements-typing.txt:46`), inside `[0, 3.14.4)`.

The alert count matches the body: 6 open alerts, numbers 85-90, `state=open`, `fixed_at=null`, 85-87 on `tests/requirements-ci.txt` and 88-90 on `tests/requirements-typing.txt`; the enumerator returns no aiohttp pin outside those two manifests and no other package.

The two requirements files agree. `tests/requirements-ci.txt` pins `aiohttp==3.14.4` with 161 sha256 digests; `tests/requirements-typing.txt` pins `aiohttp==3.14.4` with 161; the two sets are equal, and each equals PyPI's complete published 161-file set for 3.14.4. The typing lock's `yarl==1.25.1` carries 138 digests, equal to PyPI's 138. No aiohttp pin remains at 3.14.3 in any tracked manifest: the only other `3.14.3` occurrences are `tests/typing_budgets.json`'s `census.environment.aiohttp` and two header/docstring sentences describing homeassistant's pin. `census.environment` is recorded provenance, not a constraint — `typing_ruler.py` emits `third_party_versions` as a `report.note` ("recorded, not asserted"), and `lock_disagreements` compares only the versioned `ruler` pins (mypy and homeassistant-stubs). `tests/requirements-build.txt`, `-coverage.txt` and `-nightly-ha.txt` do not name aiohttp.

Every changed line is explained by the resolver:

- CI lock, 282 changed lines: 2 version lines (aiohttp 3.14.3 to 3.14.4) and 280 hash lines (119 removed, 161 added).
- Typing lock, 540 changed lines: 4 version lines (aiohttp and yarl), 522 hash lines (aiohttp 119 to 161 = 280; yarl 104 to 138 = 242), and 14 header lines (13 comments and one blank).
- A block-level parse of both files at base and head returns no package added, none dropped, no package at an unchanged version whose hashes moved, and no constraint removed. There is no changed line without a path to aiohttp: the only moved packages are aiohttp and yarl.

yarl's move is forced, not incidental. aiohttp 3.14.4's `requires_dist` carries `yarl<2.0,>=1.25.1`; `homeassistant==2026.9.3` pins `aiohttp==3.14.3` and `yarl==1.24.5`; `homeassistant-stubs==2026.9.3` requires `homeassistant==2026.9.3`; and the typing job installs the lock `--require-hashes --no-deps` (`.github/workflows/tests.yml:680`), so the lock, not homeassistant, decides what is installed. The CI lock already carried yarl 1.25.1 at the base and is unchanged there.

The delivery row `dev/programme/delivery/2487.md` is the PR's own row, names `R10-DEPENDABOT-AIOHTTP`, and has `delivery_row.sh`'s `row_line` shape (`**open**`, title, group). The group appears twice because the PR title already ends with it and `row_line` appends it; the sibling rows #2480 and #2483 carry the same generated shape.

Every template heading is present (Head, Mutation proof, Null control, Figures, Red checks, Forward-carry, Friction); `pr-contract`'s own `PR-BODY: 0 error(s)` agrees.

`git merge-tree --write-tree origin/main <head>` exits 0, no conflicting path. `python3 tests/env_drift.py --claims-only <merge-base>` prints `claims hygiene: 76bb45628... ok`. VERSION, the manifest version and the notes heading are untouched (0 diff lines).

## CI at the head

Read through `/repos/tvofi/heatpump_optimizer/commits/1a9b90965c31c6fd0093f623ec623e319fd6d3be/check-runs` at 2026-10-20T13:50:12Z, 37 check runs. Success: `typing`, `Analyze` (all three), `arch-score`, `budget-raise-gate`, `briefs`, `closure-scope`, `delivery-status`, `hassfest`, `mutation`, `policy-docs`, `scope`, `validate-hacs`, `wave-script`, `browser`, `env-matrix`, `instrument-self-tests`. In progress: `fast (3.14)`, `coverage`. Red: `pr-contract` (this PR, above) and `nightly-status`. `nightly-status` is main's own scheduled failure: the check reads the last concluded scheduled Tests run, and runs 39387919507 (2026-10-20T07:39Z) and 39218718759 (2026-10-19T07:51Z) both concluded failure on `main`; this diff reaches none of what the check reads, so it is not this pull request's.

The full local gate was not run (the owner's ruling for this bump). I did not re-run the fixer's pip-install mutation proof; instead I established the stronger static property it tests — each version's hash list is exactly PyPI's complete published digest set (161/161 for aiohttp 3.14.4 in both files, 138/138 for yarl 1.25.1) — so no platform's artifact selection can escape the list.

## RESULT lines

```
RESULT ghsa=GHSA-2g87-pp6c-29x5 fixed_in=3.14.4 introduced=0
RESULT ghsa=GHSA-494j-54xm-rwp3 fixed_in=3.14.4 introduced=0
RESULT ghsa=GHSA-5wr8-gcqf-gqf3 fixed_in=3.14.4 introduced=0
RESULT dependabot_open=6 manifests=2 numbers=85-90 fixed_at=null_all
RESULT previous_pin=3.14.3 in=both_requirements_files
RESULT ci aiohttp=3.14.4 hashes=161 pypi=161 equal=True
RESULT typing aiohttp=3.14.4 hashes=161 pypi=161 equal=True ci_equals_typing=True
RESULT typing yarl=1.25.1 hashes=138 pypi=138 equal=True
RESULT ci yarl=1.25.1 hashes=138 unchanged_from_base=True
RESULT changed_lines ci=282 typing=540 all_explained=True
RESULT packages_added=0 dropped=0 same_version_hash_moves=0 constraints_removed=0
RESULT delivery_row=dev/programme/delivery/2487.md group=R10-DEPENDABOT-AIOHTTP disposition=open
RESULT template_headings=all_present pr_body_errors=0
RESULT merge_tree_exit=0 conflicts=0
RESULT env_drift_claims=ok version_edits=0
RESULT pr_contract=red carry_unrouted=2 control_unbackticked_routed=2
RESULT nightly_status=main_scheduled_failure not_this_pr=True
RESULT typing_check=success fast_check=in_progress at=2026-10-20T13:50:12Z
```
