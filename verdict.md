Fix review: merge 72ee6a18a606fa25d5469a051ecdc43a99b87c97

bus-nonce: ab412545f3839740f7d4d8f0dce377f0

## Summary

PR #2779 (R10-FLOW-ROSTER-FREEZE arm b), review round 2, measured at head `72ee6a18a606fa25d5469a051ecdc43a99b87c97` from a detached worktree; the head was re-read before return and is unchanged. Role contract at main matches the merge base (`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty).

## Findings

- `report` now prints a `NOTE` line for every valid destination, not only notes that carry text: `audit` appends the bare token for a destination whose check returns no note, so every routed group, `#N` and `dismissed:` destination prints `NOTE body item <id>: <tok>` (`ev/note-noise.txt`: base prints none, head prints `NOTE body item 7ee09676: R10-RATIO-ANCHOR`), and the round-ref note repeats its token (`R10-ONLYROUND: R10-ONLYROUND resolved on ...`). Nothing parses these lines and the pass/fail outcome is unchanged, but the mutant restoring the old `UNVERIFIED` filter survives the self-test (`ev/mutant-report-filter.txt`, 196 checks, 0 failed), so the changed line is unpinned. Fix: print only notes with text, and pin the printed round-ref note in the self-test. Carry: R10-FLOW-ROSTER-FREEZE
- A group open on the tree's roster but done on the round's roster ref still passes, because `Dests.check` returns on the tree's open answer before it looks at the round ref. The round ref is the newer record (finding-propagation.md), so a carry can land on a group the round has already closed. This is not a regression (the base passed it too), and this PR does not widen it, but it is the same class. Carry: R10-FLOW-ROSTER-FREEZE

## Evidence

- RESULT self-test at head: `carry_audit self-test: 196 checks, 0 failed` (`ev/self-test-head.txt`); at `c176ee55de7c`: `189 checks, 0 failed` (`ev/self-test-c176ee55.txt`). That matches the body's 196/189 and its 7 new rows.
- RESULT drop-mutant (the round-ref branch removed from `Dests.check`) is killed: 2 failed, `a group only on the round's roster ref is a destination ...` and `load_dests reads the round ref ...` (`ev/mutant-drop-round-branch.txt`).
- RESULT further mutants, all killed: `no-load` (the body's M1, 1 failed), `round-done-ok` (the body's M3, 2 failed), `revparse-inverted` (crash plus 1 failed), `skip-revparse` (RosterNotFound crash), `main-open-first` (27 failed). The only survivor is `report-filter`, which is listed under Findings.
- RESULT P89 controls via the CLI, in a scratch clone at the head with a synthetic `origin/handoff/audit-r10-roster` (main's roster plus R10-ONLYROUND open and R10-RDONE done) (`ev/controls.txt`). Each control gave the expected result:
  - A group only on the round ref passes with rc=0 and `NOTE ... resolved on origin/handoff/audit-r10-roster`.
  - A group on neither ref fails with rc=1.
  - A group done on both refs fails with rc=1, and so does a group done on the round ref alone.
  - A clone without the round ref refuses the round-only group with rc=1, while a main-open group still passes, so the change only narrows.
  - An explicit `--roster-ref origin/main` refuses the round-only group, and `--roster-ref <round ref>` passes it, so the old single-ref meaning holds.
- The body's harness group: `R10-FLY-LEDGER-SAMPLE` is absent from the roster at `c176ee55de7c` and open on the round ref, as the body says. It has since reached main at the merge base `0d1385e2f`, so at current tips that group no longer exercises the arm and the synthetic controls above stand in. The real round ref at `4937d60fea5c` currently holds no group absent from main.
- `throwaway_git`: `from throwaway_git import throwaway_git_init` and its `sys.path.insert` sit inside `_self_test` only (lines 681-682); `python3 -I tests/throwaway_git.py --check` at head prints `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD` (`ev/throwaway-check-head.txt`).
- `pr-contract.yml`: the diff touches only the carry step's `run:`, adding `set -euo pipefail` and a read-only `git fetch --no-tags` of `refs/heads/handoff/audit-r*-roster` into remote-tracking refs. `on: workflow_call`, `permissions` (contents: read) and the step order are unchanged, and the step is still the job's last. `origin/main`, which `roster_lib.round_ref` lists, is fetched by the earlier version-refusal step in the same job.
- Merge: `git merge-tree --write-tree origin/main 72ee6a18a606fa25d5469a051ecdc43a99b87c97` exit 0, tree `b3aaf10f943a`, with no conflict and no claim-driver line (`ev/merge-tree.txt`). VERSION, the manifest, RELEASE_NOTES.md and the golden claim files are untouched.
- CI on this head, read from the check-runs API while it was still in flight: `budget-raise-gate`, `closure-scope`, `delivery-status`, `nightly-status`, `hassfest` and `prelude` succeeded. `mutation`, `briefs`, `codeql` and `prelude` (run 40143542723) were in progress, and `closures`, `fast`, `coverage`, `typing`, `browser`, `arch-instrument`, `arch-score`, `wave-script`, `instrument-self-tests`, `env-matrix`, `policy-docs` and `validate-hacs` were queued. No check was red, so the body's `## Red checks: none` holds so far, and the BASH_ENV effect the fixer reports (two `tests/entities.py` checks failing in the cloud container) explains no CI red, because none exists. I did not re-run `tests/entities.py` under BASH_ENV, so that container-only claim is the fixer's figure, not re-derived here.
- Figures not re-derived: the scoped-gate line (`MODE: SCOPED -- 2 script(s) run, 31 scoped out`), the harness_headers, structure and layout passes, and `ci_predict`. Per the contract, CI's heavy runs are cited, not re-run, and they had not concluded.
