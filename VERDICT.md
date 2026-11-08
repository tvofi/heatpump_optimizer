Fix review: merge d17e43cf530c324acba0c6594256291a725b7023

bus-nonce: ff015eaa9fe5b5433985199dc214e417

Round 8 of the fix review of #3262 (R10-OUTSIDE-INTAKE), at head d17e43cf530c324acba0c6594256291a725b7023, from a detached worktree at the head. The scope is the past-three ruling s13: the cure of the round-7 block (`verdict/3262`, blocked at c95c3b4b, mutation-vacuous) plus the delta `git diff c95c3b4b2 d17e43cf5`. That delta is one authored commit, df0ffdf5e, adding 24 lines to `tools/audit/seat/beat_jobs_selftest.py`: two `plan_beat` cases and two `MUTANTS` entries. The merge d17e43cf5 has the same tree as df0ffdf5e. No production line moved. This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.

## Verdict

The round-7 block is cured:
- Both surviving mutants of the resolved `plan_beat` lines (`moved_early_return`, `moved_on_rc1`) are now killed by named cases, which I re-ran myself.
- The fail-first is shown: under the c95c3b4b self-test both mutants survive.
- The body's false "no new site" sentence is corrected.
- CI at the head is GREEN; I read every check run myself.
- The head merges cleanly with origin/main.

## Findings

- Follow-up, non-blocking: **three branch-own `plan_beat` dispatch mutants still survive** at the head.
  - Claim: these mutants of `if rc in (0, 1) and re.search(r"^pushed ", out, re.M)` (`beat_jobs.py:414`) leave `beat_jobs.py --self-test --no-mutants` at rc 0:
    - `dispatch_only_rc0`: becomes `rc == 0`. A landed push at rc 1 then no longer dispatches, against the docstring's "on rc 0 or 1".
    - `dispatch_rc012`.
    - `pushed_regex_unanchored`: becomes `re.search(r"pushed", out)`.
  - Round 7 carried them, and df0ffdf5e does not touch them. They predate the s13 delta, so they do not block.
  - Evidence: `ev/reviewer-mutants-head.txt`.
  - Harness: a mutated copy, then `beat_jobs.py --self-test --no-mutants`. Metric: rc. Perturbation: each edit as named. Null control: rc 0 on the unmutated copy.
  - `dispatch_rc012` may be near-equivalent, if `state_docs` never prints `pushed ` on rc 2. Carry: R10-OUTSIDE-INTAKE
- Follow-up, non-blocking: **`## Red checks` still describes the previous head.**
  - The body names reds at c95c3b4b2 and says "At this new head nothing has run yet". At d17e43cf, two checks concluded red and were then superseded:
    - `gate` 128634825177: an edit-run deferral, `FAIL run(s) [42449104484] at this head are still being judged; their gate decides`.
    - `governance / instrument-self-tests` 128634393148: cancelled at 05:13:34Z mid-step, before tvofi's 05:17Z re-run. It was not the 30-minute timeout.
  - Both now have green successors (`ev/checks-at-head.txt`). The body names neither.
  - Harness: `get_check_runs` across all pages, compared against the body. Perturbation: on the round-7 body it named both concluded reds of c95c3b4b, so this is not a reader artefact. Carry: R10-OUTSIDE-INTAKE
- Follow-up, non-blocking: **`## Head` names `cdf33cc1b6b925124315643b9c4320341ec29b72`, which is not in the head's history.**
  - cdf33cc1b is a sibling merge with the same parents as the head, c95c3b4b2 and df0ffdf5e.
  - Harness: `git merge-base --is-ancestor cdf33cc1b d17e43cf5` gives rc 1; the same check on d17e43cf5 itself gives rc 0.
  - A later seat could check out the wrong commit; the line should be dropped. Carry: R10-OUTSIDE-INTAKE

## Evidence

- **Setup:**
  - `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`.
  - `review_packet.py render --pr 3262 --head d17e43cf…` gave rc 0, with the refusal `required-red: required context gate concluded failure` at render time (05:05Z): the deferral red, since superseded (`ev/review-packet.md`).
- **Scope:** `git diff --stat c95c3b4b2 d17e43cf5` shows only `tools/audit/seat/beat_jobs_selftest.py | 24 +`. `git diff df0ffdf5e d17e43cf5` is empty.
- **Mutation proof at the head** (`ev/reviewer-mutants-head.txt`), using my own driver on `beat_jobs.py` with `--self-test --no-mutants`:
  - null: rc 0.
  - `moved_early_return`: KILLED, `FAIL plan-beat: a moved page whose push landed is PLAN MOVED and still dispatches Pages, once`.
  - `moved_on_rc1`: KILLED, `FAIL plan-beat: rc 1 with a re-rendered page is PLAN UNAVAILABLE alone, no PLAN MOVED, no page memory`.
  - Also KILLED: `pages_err_dropped`, `dispatch_ref_dropped`, `remember_dropped`, `moved_always`, `word_swapped`.
  - Survived: `dispatch_only_rc0`, `dispatch_rc012`, `pushed_regex_unanchored` (see Findings).
- **Fail-first** (`ev/fail-first-old-selftest.txt`): with the c95c3b4b `beat_jobs_selftest.py` swapped in at the head, both `moved_early_return` and `moved_on_rc1` give rc 0, so they survive. The new cases are what kill them.
- **Flake check, not reproduced:**
  - One null run under the old self-test once printed `FAIL plan-beat: state_docs rc 1 is PLAN UNAVAILABLE`. Five repeats of that null gave no FAIL.
  - 30 null runs at the head gave 0 FAIL (`ev/flake-head-30.txt`).
  - I could not move it, so it is not a finding.
- **Self-tests at the head:**
  - `python3 -I tools/audit/seat/beat_jobs.py --self-test`: rc 0, `beat_jobs self-test: 175 checks, 0 failed`, with both new mutants reported `killed by` their named cases. This matches the body's 175 (171 before, plus 2 cases and 2 mutants).
  - `outside_intake.py --self-test` and `plan_public.py --self-test`: rc 0 (`ev/selftest-*.txt`).
  - `tests/structure.py`: rc 0. `tests/entities.py` could not run locally (no `homeassistant` module here); it passed in CI.
- **Invariants** (`ev/invariants.txt`):
  - Merge base 7c9c4c154.
  - VERSION, RELEASE_NOTES.md, the manifest and both claim files: `BYTE-IDENTICAL`.
  - `budgets.json` in the three-dot diff: 0.
  - `dev/programme/delivery/3262.md` in the three-dot diff: 1.
  - `custom_components/` in the three-dot diff: 0.
  - `ref_privacy --check`: 0 refused.
- **Merge:** `git merge-tree --write-tree origin/main d17e43cf…` (origin/main 8aec35435) gave rc 0 with tree 894c25dbf. The only conflict, in `tests/closures.json`, was resolved by the ledger driver (`ev/merge-tree.txt`).
- **CI** (`ev/checks-at-head.txt`, `ev/classify-loop.txt`):
  - `merge_train.py classify` read RED or WAIT on the edit-run gate deferral until code run 42449104484 attempt 2 concluded. Then it read `05:51:03Z rc=0 GREEN d17e43cf… pending: none red: none`.
  - I read all 68 check runs (one page) myself. Every latest run is success or skipped.
  - Notably: `governance / instrument-self-tests` 128637530289 success (05:18-05:31Z), `gate` 128643695123, 128643899038 and 128643901917 success, `pr-contract / pr-contract` 128643483744 success.
  - The superseded reds of earlier attempts are listed in that file.
- **Approval:** this policy and developer-docs change merges only on tvofi's approving review at the head.
