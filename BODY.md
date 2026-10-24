Root-cause record for the red `tests / ci-ratchet` on `main` from `d5dc3e26a`: `tests/ci_ratchet.py` keyed push runs on `.name == "CI"`, which `ci.yml`'s `run-name:` rewrites. Process state (d); the cost test refuses a new countermeasure. Docs and register only (the class id is also in finding.schema.json's class_guess enum and the finder's generated block, via fold_ledger.py sync, so the agreement lane's finding-class-id readers agree; `python3 -I tools/policy/agreement_py.py --run`, which runs `tools/policy/agreement.mjs` on its output, prints AGREEMENT ok): `dev/audit/rca/R10-RCA-CI-RATCHET-RUN-NAME.md` and a `dev/audit/config/bugclasses.json` row for the P2b assembly class (total 0, 4 non_round_instances, barrier null; triage P52 rejected a barrier).

## Head

b7564b26d43153c8b5d094d6e73fae6f10294517

It adds one commit to the reviewed head `b5cf12dfe83705acaf5726b8e018e84174ac8883` (the authored code head `f5b2f4624` plus the orchestrator's merges of origin/main `0c3640761` and `145bfe197` and the delivery row `dev/programme/delivery/2696.md`). The commit changes only `dev/audit/rca/R10-RCA-CI-RATCHET-RUN-NAME.md`.

## Review answered (review/2696, round 1, blocked record-contradicts-diff)

- **Block: section 5 said the 4 assembly defects are not registered.** Fixed in b7564b26d. Section 5's bullet now says they are registered as one class, `N-p2b-assembly-reader`, listed and not counted, that triage P52 rejected a barrier, and that what I did not establish is a common cause past the shape. Section 4 now names the register row, says it is listed and not counted (its `non_round_note` records process incidents, not audit findings), and states triage P52's ruling (the 3-instance trigger has not fired for a listed-not-counted class; neither candidate catches the instance that shipped) and its reopen condition. Section 1's neighbours paragraph names the row's `total` 0, its 4 `non_round_instances` and its null `barrier`. These are read from the row: `python3 -c "import json;d=json.load(open('dev/audit/config/bugclasses.json'))['N-p2b-assembly-reader'];print(d['total'],d['barrier'],len(d['non_round_instances']),d['rca'])"` printed `0 None 4 ['R10-RCA-CI-RATCHET-RUN-NAME']`. `grep -n "not registered" dev/audit/rca/R10-RCA-CI-RATCHET-RUN-NAME.md` returns nothing at the head; at `b5cf12dfe` it returns line 141.
- **Finding: `pr-contract / pr-contract` red on the edit run 40089109084.** Named under `## Red checks` below, with the reviewer's dismissal.

## Mutation proof

n/a: one document and one register row, no code or check changed. `python3 tools/audit/fold_ledger.py check` printed UNKNOWN-RCA and DRIFT before the row's _rca entry and refresh, and 0 violations after. The reviewer reproduced the first (deleting the `_rca` entry gave `UNKNOWN-RCA: N-p2b-assembly-reader cites R10-RCA-CI-RATCHET-RUN-NAME`). Re-run at b7564b26d: `fold_ledger: 46 classes, 746 instances, 121 in-tree judge survivors (rounds [8, 10]), 121 rca entries`, `0 violation(s)`; `agreement_py.py --run` printed `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`; `tests/structure.py` printed `STRUCTURE RATCHET PASSED`. Scoped gate (`tests/closure.py select --diff $(git merge-base origin/main HEAD)`): `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, 5 changed files.

## Null control

n/a: no check proposed. The refused candidate (the job classifies its own run) was costed, not built.

## Figures

Re-derived at 2026-10-24 for this body.

- 5 red push runs on `main` (`d5dc3e26a`, `94bec976b`, `15f0b5924`, `88744e573`, `50af6174f`): `gh api 'repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?event=push&branch=main&created=2026-10-24T00:00:00Z..2026-10-24T11:00:00Z&per_page=100' --jq '.workflow_runs[]|[.head_sha[0:9],.created_at,.conclusion]|@tsv'`, counting `failure`. The same listing returns 7 `success` push runs in that window (4 before `d5dc3e26a`, 3 from `9fd5eb107`), so a green run would have shown.
- 6.0 h of red `main` (02:36 to 08:35Z) is a floor taken at the document's read time, 08:35Z, and the document says so. The same listing shows the red ended when `9fd5eb107`'s push run (created 09:47:14Z) finished `success` at 10:19:58Z, about 7.7 h. A larger cost(defect) lowers the break-even and does not change the cost test's verdict. I leave the document's floor as written: it is a measurement record of what was read at 08:35Z.
- 113 `ci.yml` runs in 24 h: `gh api 'repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?created=2026-10-23T06:00:00Z..2026-10-24T06:00:00Z&per_page=1' --jq .total_count` printed 113.
- 1.14 s per call and 129 runner-s/day come from job 120752118657's step timestamps, as the document states. I did not re-derive them here.

## Red checks

`pr-contract / pr-contract` on the `CI edit` run 40089109084 at `b5cf12dfe83705acaf5726b8e018e84174ac8883` is red, and it is not caused by this PR. Attempt 1 (job 120858180113) failed at 11:16:09Z and attempt 2 (job 120861590328) at 11:34:15Z, both in the step "Wait for code scanning and list its open alerts". Attempt 3 (job 120863615751) carried attempt 2's result over and did not re-run it. The code run 40089109480's `codeql / Analyze (python)` (job 120858024806) did not complete until 11:38:20Z, so `codescan_wait.py` found no finished codeql unit at this head and failed closed. The code run's own `pr-contract / pr-contract` (job 120863373662, 11:42:26Z to 11:42:58Z) is `success`. Times are from `gh api repos/tvofi/heatpump_optimizer/actions/runs/<run>/jobs?filter=all` and `.../actions/jobs/<id>`. The reviewer's dismissal applies: not this PR's; it is an instrument race between an edit run's `codescan_wait` and the code run's codeql. The instrument gap the reviewer noted, that the `FAIL closed` reason goes to stdout, which the step redirects to /tmp/pr-alerts.txt and so keeps out of the log, needs no PR here.

`tests / coverage` and `tests / coverage-ratchet` on `7ad01d0f183c531bb3e2d0bbe541222f12e3ab0a` (run 40085070047) are red, and neither is caused by this PR, which changes one document, one register row, `finding.schema.json` and the finder's generated block (no script, workflow or dependency). `tests / coverage` failed at its `Install pinned test dependencies` step: `pip install --require-hashes -r tests/requirements-ci.txt` got `ConnectionResetError(104, 'Connection reset by peer')` from the package index 1 s after it started, so every later step (`Measure the tree`, the save) was skipped. `tests / coverage-ratchet` then failed at `actions/download-artifact` with `Artifact not found for name: coverage-json`, because the coverage job that makes that artifact never reached its upload. Both are one transient network fault and its consequence, not a coverage or ratchet finding. The reviewer read both as green on the code run at `b5cf12dfe`.

Cheaper detector: none is worth building. A retry around `pip install` would cost a workflow edit and a policy-adjacent change for a fault seen once here; the standing countermeasure is a rerun of the failed jobs, which costs one click and is what the owner of the lane does. The codescan race is the instrument's and is dismissed above. Answered here, not by a new check.

## Forward-carry

none

## Friction

none
