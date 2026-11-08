Fix review: blocked c95c3b4b2e5875103fd5944c766d9e954f5b8a90 mutation-vacuous: beat_jobs.py plan_beat resolution mutants moved_early_return and moved_on_rc1 survive the self-test

bus-nonce: 65a08d07985d3e88836905178f706405

Round 7 of the fix review of #3262 (R10-OUTSIDE-INTAKE), at head c95c3b4b2e5875103fd5944c766d9e954f5b8a90. It is limited to the resolution delta against 33c3dd99, per the orchestrator's past-three ruling s13. I worked from a detached worktree at the head. This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.

## Block

- **The resolution made a new control-flow site, and the shipped self-test does not pin it.** Before the merge:
  - Main's `plan_beat` wrote `PLAN MOVED` through an early `return write_job(...)` on rc 0.
  - The branch's version dispatched `pages.yml` after a push that landed.
  - The resolution at `tools/audit/seat/beat_jobs.py:392-418` folds both into one `lines` list with a single `write_job`.
  - The head behaves correctly. My probe shows it dispatches the Pages deploy on a pass where the page moved and the push landed.
  - The body says the resolution's added lines "are this branch's and main's already-killed lines … there is no new site". That is false. Two behavioural mutants of the resolved lines survive `python3 -I tools/audit/seat/beat_jobs.py --self-test --no-mutants`, which gives rc 0 under each (`ev/reviewer-mutants-resolution.txt`).
- **Mutant `moved_early_return`** (L412-413):
  - The edit: `lines.append(PLAN MOVED …)` becomes `return write_job(ctx, "plan-beat", [PLAN MOVED …])`. This is main's own pre-merge shape, the one a careless resolution would keep.
  - Effect: on every pass whose page changed, the Pages dispatch is skipped. Those are exactly the passes where the public page most needs republishing.
  - Why it survives: the `PLAN MOVED` case's fake `state_docs` prints no `pushed ` line, and the dispatch cases write no page. No case combines the two.
  - Proof it is not equivalent: `ev/reviewer-probe-moved-and-pushed.txt` makes that case's `state_docs` print `pushed …` and require exactly one `gh` call.
    - At the head: rc 0.
    - Under the mutant: rc 1, `FAIL plan-beat: a changed PLAN.html is PLAN MOVED once; an unchanged one is no line`.
- **Mutant `moved_on_rc1`** (L407):
  - The edit: `if rc == 0:` becomes `if rc in (0, 1):` before `page = read(`.
  - Effect: on a `state_docs` rc 1 the row also emits `PLAN MOVED` and advances `plan-page.json`. The docstring says `PLAN MOVED` is "on success".
  - On main 7c9c4c15 this mutant is KILLED (`ev/reviewer-mutants-at-main-7c9c4c15.txt`): main's rc-1 path lost its `PLAN UNAVAILABLE` line under it. The resolution moved the error line ahead of the page block, so main's pin no longer reaches it. The merge lost coverage that main had.
  - Proof it is not equivalent: `ev/reviewer-probe-rc1-page.txt` adds a case where rc 1 has a re-rendered page.
    - At the head: rc 0.
    - Under the mutant: rc 1, `FAIL probe: rc 1 with a re-rendered page is PLAN UNAVAILABLE alone`.
- **Null control:** the unmutated head passes both probe cases and the full self-test (`171 checks, 0 failed`, `ev/beat_jobs_selftest.txt`). Each kill belongs to its mutant.
- **Cure:**
  - Add the two cases my probes show: moved plus pushed dispatches once; rc 1 with a re-rendered page is `PLAN UNAVAILABLE` alone.
  - Add `moved_early_return` and `moved_on_rc1` to `beat_jobs_selftest.py`'s `MUTANTS`, each naming its case.
  - Show both fail first, at the head without the cases.
  - Correct the body's resolution claim.

## Findings

- Follow-up, non-blocking: **three branch-own `plan_beat` dispatch mutants survive.** Claim: these mutants of the dispatch predicate `if rc in (0, 1) and re.search(r"^pushed ", out, re.M)` (L414) survive the self-test at both 33c3dd99 and the head, so they predate this delta and fall outside round 7's scope:
  - `dispatch_only_rc0` (rc 1 with a landed push no longer dispatches; the docstring says "on rc 0 or 1").
  - `dispatch_rc012`.
  - `pushed_regex_unanchored` (`"pushed"` anywhere, so `already current … pushed` text would dispatch).

  Evidence: `ev/reviewer-mutants-resolution.txt` and `ev/reviewer-mutants-at-33c3dd99.txt`. Harness: `beat_jobs.py --self-test --no-mutants` on a mutated copy. Metric: rc. Null control: the unmutated copy gives rc 0. Perturbation: each edit as named. `dispatch_rc012` may be near-equivalent if `state_docs` never prints `pushed ` on rc 2; the other two are behavioural. Carry: R10-OUTSIDE-INTAKE
- Follow-up, non-blocking: **`## Red checks` names the reds of an older head.** The section names reds at b9b6af686 and says nothing has run at 0ac370fa2. At c95c3b4b, `gate` 128581122145 and `pr-contract / pr-contract` 128578752551 have concluded red (see Evidence), and the body names neither. Both must be named and answered at the next head. Carry: R10-OUTSIDE-INTAKE

## Evidence

- Setup:
  - `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`.
  - `review_packet.py render --pr 3262 --head c95c3b4b…` gave rc 0 (`ev/packet.log`, `ev/review-packet.md`).
- Scope check:
  - The three-dot branch-own diffs at 33c3dd99 (base 364353e6) and at the head (base 7c9c4c15) differ in exactly three files: `tools/audit/seat/beat_jobs.py`, `beat_jobs_selftest.py` and `instruments/beat_jobs.py.md` (`ev/own-old.stat`, `ev/own-new.stat`).
  - Nothing else in the patch moved.
- Both sides' behaviour survives at the head. Main's `PLAN MOVED` on rc 0 and the branch's `pages.yml` dispatch on a landed push (rc 0 or 1) both pass. The probe confirms the two together. The docstring and the instrument doc carry both sentences.
- `plan_rc1_silent` at the head targets `    if rc != 0:\n        said = `, as the body states (`ev/plan_rc1_silent-at-head.txt`), and is killed.
- `python3 tools/audit/seat/beat_jobs.py --self-test` at the head: rc 0, `171 checks, 0 failed`, 71 `killed by` lines.
- `outside_intake.py --self-test` and `plan_public.py --self-test` at the head: rc 0, all checks passed (`ev/selftest-*.txt`).
- My mutants on the resolved lines (`ev/reviewer-mutants-resolution.txt`):
  - KILLED: `remember_dropped`, `dispatch_ref_dropped`.
  - Equivalent: `lines_reset_after_err` (rc 0 never has an error line).
  - Survivors: as listed under Block and Findings.
- `git merge-tree --write-tree origin/main c95c3b4b…`: rc 0, no conflict (`ev/merge-tree.txt`).
- CI at the head (`ev/ci-reds.txt`, `ev/classify.log`):
  - `merge_train.py classify` at 00:50:20Z: `RED c95c3b4b2e5875103fd5944c766d9e954f5b8a90 pending: none red: gate` (rc 1).
  - Two check-runs concluded red:
    - `gate` 128581122145 (KIND edit): `FAIL run(s) [42424058362] at this head are still being judged; their gate decides`. This is an edit-run deferral to code run 42424058362, which was still running `tests / closures`, `governance / instrument-self-tests` and `codeql / Analyze (python)`.
    - `pr-contract / pr-contract` 128578752551: `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s`. This is a timing fail-close in `codescan_wait.py` while CodeQL python was still running. Its body lanes were clean: figure_lint `16 resolved, 2 not verified, 0 refused`, preflight `no refusal`, carry audit 0 items.
  - I did not wait out the code run. The block above is a code finding that CI cannot cure, so a green run would not change this verdict.
  - The next head owes both reds re-read, and `pr-contract` re-run once CodeQL has finished.
- Carry destinations on `handoff/audit-r10-roster`: R10-OUTSIDE-INTAKE is `in-progress`.
