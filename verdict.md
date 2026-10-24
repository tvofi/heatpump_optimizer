Fix review: merge c98b1144ddd0dc5482ab823f049043e56a06ce29

bus-nonce: 204538179fec142a74e2153d45916d37

## Scope

Round 2 (a re-review after the fixer's repair). Measured head: c98b1144ddd0dc5482ab823f049043e56a06ce29. It was still the PR head when this verdict was written. Merge base: 87ecf385b. Code head: 9734cfabf. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.

## Findings

- The body's CodeQL 1 paragraph says "`node --check` fails on each (`SyntaxError: Illegal return statement`)". Given a path, on Node v22.22.0, all 8 `.claude/workflows/*.js` files pass `node --check` (rc 0). They fail only when fed on stdin with `--input-type=module` or `--input-type=commonjs` named. The pin in `tests/entities.py` uses the stdin form, and its own comment documents the difference. So the mechanism is sound, and only the body sentence does not re-derive as written. Carry: dismissed: wording in the PR body only; the committed pin and its comment are correct, and no gate reads this sentence
- The stand-in upload for skipped CodeQL legs is not exercised end to end on this PR: it touches `.github/`, so every leg analyzes. The body names the first prose-only PR after the merge as the check. Carry: dismissed: disclosed in the body as a post-merge observation; `tests/entities.py` pins the step wiring and `codeql_scope.py --self-test` pins the selection
- Removing the stale code-scanning configurations (D2) is owed after the merge, by hand, by tvofi. Carry: dismissed: the body records it as the owner's manual task, outside any seat's write access
- The cheaper detector for the `governance / wave-script` red (running the agreement lane after the wave-script restore inside prepr) is not built. The body hands it to the root-cause seat. Carry: dismissed: per defect-root-cause.md the countermeasure is the root-cause seat's call, and the body answers the red-check trigger
- Whether a github-actions bump also needs Workflows:write on the hpo-approver App is unverified. Carry: dismissed: disclosed in the body; the fail-soft path prints a notice and arms nothing

## Evidence

- Mutation proof, reproduced at the head with `node tools/policy/policy_lint.mjs`:
  - Baseline: rc=0, `FIXTURE ok: 93 error(s) hold 258 pins across 12 check classes`. The body's 263 re-derives at code head 9734cfabf (`ev/policy_lint_at_9734cfab.txt`). The 5-pin difference comes from origin/main 87ecf385b, merged in c98b1144, which edits `tools/policy/policy_lint.mjs` and removes `tools/policy/fixtures/required-contexts.json`. It is not this PR's.
  - M6 (prefix check deleted): rc=1, `FIXTURE VACUOUS: ... manifest in an unconfigured directory`.
  - M7 (`pip: () => true`): rc=1, `... non-manifest in a configured pip directory, non-manifest in a configured npm directory`.
  - M8 (`npm: () => true`): rc=1, `... non-manifest in a configured npm directory`.
  - All three are killed, matching the body (`ev/M6.txt`, `ev/M7.txt`, `ev/M8.txt`, `ev/baseline.txt`).
- Wave-script repair. I replayed `governance.yml`'s wave-script restore step verbatim (`ev/wave_script_restore_replay.sh`) with PINNED = the base 87ecf385b in a worktree at the head. That restored 4 paths. Then I ran the lane's two commands:
  - At the head: `RESULT divergent=0 unregistered=0`, `AGREEMENT ok`.
  - My own mutant M9 re-adds a regexp-escape export to `dependabot_contract.mjs` under the same replay. It prints `UNREGISTERED "[.*+?^${}()|[\\]\\\\]" in .claude/workflows/policy_lint.mjs, tools/policy/dependabot_contract.mjs` and `AGREEMENT REFUSED`, which is CI's red line on 9439a0948. So the repair is what turns the lane green.
- paths-ignore pin. `ev/codeql_pin_replica.py` is my own instrument: a replica of the `tests/entities.py` predicate, used for mutation only. It reads ok for the committed pattern. It refuses an added parseable pattern (`tools/policy/*.mjs`: 15 parseable) and an added pattern that matches nothing. The real check reads `ok codeql.yml ignores only files the JS parser refuses` in the full entities run at the head.
- Red history on the range (Actions jobs API, runs 40104897988 and 40104900986 at 9439a0948, the only earlier head with runs): `governance / wave-script`, `tests / closures`, `tests / closures-autofix`, `pr-contract / pr-contract` and `gate` failed. These are exactly the five the body's `## Red checks` names and answers, each with a cheaper detector or the finding that none exists.
- CI at the head, from the commit's check-runs API (`ev/check_runs_head.txt`): every completed check is success, skipped or neutral, with no failure.
  - `gate` concluded success at 19:34:15Z. A second `gate` run, from the edit run, was still in progress.
  - Two `pr-contract` runs concluded success (19:26:44Z and 19:33:11Z), both after every other workflow on the head had concluded.
  - `tests / closures` succeeded and `tests / closures-autofix` skipped.
  - `tests / mutation` is green. I did not read its log; this verdict does not turn on it.
- Merge: `git merge-tree --write-tree origin/main <head>` (origin/main 646dbaa65) exits 0. The only driver line is `LEDGER-MERGE: resolved tests/closures.json`, with no conflict on any other path.
- `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched in the three-dot diff.
- Figures re-derived at the head (`ev/figures_head.txt`):
  - `codeql_scope.py --self-test`: 63 checks, 0 failed.
  - `dependabot_merge.py --self-test`: 0 failure(s).
  - `field_coverage.mjs`: `blind=0 dead=0 refused=0`, `FIELD COVERAGE ok`.
  - `closure.py selftest`: `ALL 117 closure shrink pins PASSED`.
  - `structure.py`: `STRUCTURE RATCHET PASSED`.
  - `codeowners_gap.py --check`: `uncovered_files=0`.
  - `harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `env_drift.py --claims-only` against the base: ok.
- `tests/entities.py`: `2 of 2429` failed at the head and `2 of 2425` at the base 87ecf385b. The failing pair is identical (`gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status ...`), so neither comes from this diff. The new checks (both dependabot.yml agreement checks and the paths-ignore pin) read ok (`ev/entities_*_summary.txt`).
- INERT/closures movement is earned. All 7 `.claude/workflows/*.js` files moved out of INERT are read by the new paths-ignore pin through `glob` and `read_bytes`. `tests/closures.json` adds exactly those reads plus `.github/dependabot.yml`, `dependabot-automerge.yml` and `dependabot_contract.mjs`, and CI's `tests / closures` is green at the head.
- Not re-derived (403 or out-of-tree snapshots, dated in the body): the Actions leg census (22 runs), the python-leg minutes, the code-scanning alert count and the analyses-per-configuration tallies, and the live stand-in probe IDs.
- Forward-carry: the body says `none`. Nothing in this PR changes a later stage's brief.
