Fix review: merge f24eed01d7bb6249f0c2ac66841ffc87dc58fe24

bus-nonce: a3dd063a22d721a615ae92b7db674f59

## Findings

- Follow-up: the body's `## Red checks` cites runs that are not on this branch's history. Run 43004573627 (jobs 130469580446 `tests / fast (3.14)` and 130468964323 `tests / mutation`) has head_branch `fix/r10-outside-disinfection-setpoint` and workflow `CI code pr=3452`. d2ab2743, 0aed6ccb, ef579d9b, 4aa62003, e099eff6 and 49a45dd8 are main commits after this branch's base b737e88ee. fbbf3efd is on neither. None of them is an ancestor of f24eed01 (`ev/redcheck_ancestry.txt`). So "reached through a main merge into the branch" does not describe this branch, which is one commit pair on b737e88ee with no main merge. This does not block: no pull request or CI exists on this head, and the red-check rule reads the PR's own checks once it opens. Before opening, the body should replace those entries with the branch's own reds (none yet) so the delivery record does not inherit another PR's reds. Carry: R10-HOTFIX-MAIN-IST-PREPR-SCOPE
- Follow-up (unchanged from round 1, still unsettled): `selftest_scope.py record` measures the recording seat's per-clone merge-driver config, and the countermeasure (record in a driver-free scratch clone, or refuse while drivers are set) is unbuilt. The body carries both this and the prepr/ci_predict `check` countermeasure. Carry: R10-HOTFIX-PREPR-WC-PAD

## Evidence

- Round 2, a delta review of 361040baf232..f24eed01d7bb (`fix-review.md` step 12). The delta is `tools/ci/selftest_closures.json` only, +3/-0. It touches no `custom_components/` path, so scope does not widen. Head reviewed: f24eed01d7bb6249f0c2ac66841ffc87dc58fe24 (`ev/HEAD.txt`). The body BODY.md at handoff-body eb042ec02 names the same head.
- Round-1 block resolved: the prepr entry now keeps `.gitattributes`, `tests/env_drift.py` and `tools/merge/ledger_merge.py`. Against main's b737e88ee entry, files gain `dev/audit/harnesses/mutant_guard.py`, `tools/audit/seat/mutant_run.py` and `tools/pr/figure_block.py` and lose nothing. dirs, probes, git, run_sha, index and objects equal main's. This is exactly the cure round 1 named: the union.
- Independent re-record: a fresh `git clone --no-local` at f24eed01 with all `merge.*` config removed (`git config --get-regexp 'merge\.'` rc=1) ran `python3 -I tools/ci/selftest_scope.py record --step prepr --out <scratch>`. Result: `OK 991.7s prepr`, 0 failed, 0 broken traces (`ev/record.log`). The body reports 896.7 s; wall time differs per machine and is not a closure figure. The recorded entry equals the head's on files (both set differences empty), dirs, probes, run_sha, index and objects. On `git` the head entry is a strict superset: it also lists `branch`, which this record did not observe. The head is wider there, not narrower, and drift reports no prepr refusal (`ev/git_key_diff.txt`). All six disputed files appear in the recording.
- The mutation proof and null control reproduce with my recording: `selftest_scope.drift`, prepr lines only (`ev/drift_cmp.txt`):
  - main b737e88ee gives `UNDER-SCOPED step prepr: files misses ['dev/audit/harnesses/mutant_guard.py', 'tools/audit/seat/mutant_run.py', 'tools/pr/figure_block.py']`
  - the prior head 361040baf gives `UNDER-SCOPED step prepr: files misses ['.gitattributes', 'tests/env_drift.py', 'tools/merge/ledger_merge.py']`
  - this head gives no prepr line
  - Only prepr was passed to drift, so the other steps print UNMEASURED. That is an artifact of the harness and I drop those lines.
- `selftest_scope.py static` at the head prints 112 gated step(s), 0 problem(s), matching the body. The table parses as JSON.
- Merge check: `git merge-tree --write-tree origin/main f24eed01` rc=0 (tree d4e178a4a2d1) against origin/main 2ced371c1af5, so it merges cleanly. The three-dot diff from merge-base b737e88ee is the same single file, +3. VERSION, the manifest and RELEASE_NOTES.md are untouched.
- CI: there is no pull request yet, so there is no review packet and no CI on this head to read or wait on. `merge_train.py owed-reds` is coverage-ratchet, fast (3.14), mutation, typing and validate-hacs (`ev/owed-reds.txt`). `instrument-self-tests` is not in that set. No red on this head is owed an answer yet.
- The full `check --traces` over CI's whole-job traces was not run because it needs CI's traces. I cannot re-derive "0 refusals" beyond prepr. The body states the same limit.
- Disclosure: the re-record uses the finder's instrument (`selftest_scope.py record`/`drift`) in my own driver-free clone, not the fixer's.
