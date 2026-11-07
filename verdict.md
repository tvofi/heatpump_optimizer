Fix review: blocked aa5022f63cac715abe871d168d2ed250997261e7 mutation-vacuous: plan_public.py stage's host identity default and main() exit status survive the self-test

bus-nonce: 12c068280c43c713581f87cd2d691a8d

This is round 4 of the fix review of #3262 (R10-OUTSIDE-INTAKE), at head aa5022f63cac715abe871d168d2ed250997261e7. It is the past-three round the orchestrator granted under mandate 6624093439. I worked from a detached worktree at the head and used a second worktree for the mutants. The merge base is 62bcca76ee043e68544a7f7042e9bb3ff5502aa7. This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.

## Block

The round-3 block is cured. In my own cases-only run, `one_thread_pr_reviews_drop` (L227 `if r["kind"] == "pr":` made `if False:`) is KILLED by "refuse: a pull request whose only outside activity is a review comment is refused, marked (#3240)".

The brief asks for the mutation proof on every changed line, and for a judgement of the `plan_public.py` design. `tools/audit/seat/plan_public.py` is new in this PR, so every line of it is a changed line. Its self-test carries 4 mutants. I ran 16 of my own with its cases only (`self_test(False)`) and drove the real CLI in a scratch repository (`ev/drive_pp.sh`). Two mutants are non-equivalent and survive the full `--self-test`. `tests/entities.py` does not catch them either: it runs the workflow's stage step over a stub `python3` (entities.py L40935-40947), so it never runs `plan_public.py`.

- **`host_ident_dropped` (L67).** The mutant changes `ident or ref_privacy.Identity.of_host()` to `ident`.
  - Full `--self-test`: rc 0. The self-test passes an `ident` on every call.
  - CLI: `main()` calls `stage(a.repo, a.out)` with no ident. At the head, the clean page stages with rc 0. Under the mutant, the same command dies with `AttributeError: 'NoneType' object has no attribute 'homes'`.
  - Effect: every Pages dispatch would go red, and no plan page would ever publish.
- **`main_rc0` (L196).** The mutant changes `return rc` to `return 0`.
  - Full `--self-test`: rc 0.
  - CLI: at the head, a page naming another account's home directory gives `REFUSED: ... host-path in the page`, rc 1. Under the mutant, the message prints but the exit is rc 0.
  - Effect: the workflow's "refused page (rc 1) is red" is lost silently. The no-page warning (rc 2) is lost too. The body states both as behaviour.

Evidence: `ev/reviewer-mutants-plan_public.txt` and `ev/drive_pp.txt`. Null control: the unmutated self-test gives rc 0, and the head's CLI gives rc 0 for the clean page and rc 1 for the leaky one.

Cure: one case that runs `main(["stage", "--out", D, "--repo", R])` (or the script as a subprocess) over a scratch repository holding a state ref. It should assert rc 0 and a staged page for a clean page, and rc 1 and nothing staged for a page with a host path. Add MUTANTS entries on L67 and L196.

## Findings

- **`plan_public.py` CLI path unpinned.** This is the block above.
  - Claim: `stage`'s host-identity default (L67) and `main`'s exit status (L196) are pinned by no check.
  - Evidence: `ev/reviewer-mutants-plan_public.txt` and `ev/drive_pp.txt`.
  - Harness: `plan_public.py --self-test`, plus my drive of the CLI in a scratch repository.
  - Metric: self-test rc, and the CLI's rc and staged file.
  - Perturbation: `ident` for `ident or ref_privacy.Identity.of_host()`, and `return 0` for `return rc`. The self-test stays rc 0. The CLI moves from rc 0 with a staged page to an AttributeError, and from rc 1 to rc 0 for a refused page.

  Carry: R10-OUTSIDE-INTAKE
- **"Between rounds there is no state ref" is false as the tree stands.**
  - Claim: the body and the `pages.yml` header say that between rounds there is no state ref, so the site deploys without a plan and warns (rc 2). Nothing deletes `handoff/audit-r<N>-plan` when a round ends. The only path that does is `tools/audit/seat/closeout.py --apply` through `prune_refs.py` (archive tag, then delete), at programme closure.
  - Evidence: `git ls-remote origin 'refs/heads/handoff/audit-r*-plan'` still lists `handoff/audit-r9-plan` (e98b9f9a) beside `audit-r10-plan` (03976c47), long after round 9 closed.
  - Harness: `plan_public.newest_round` over the remote's refs.
  - Metric: the round it would publish.
  - Perturbation: none applies; this is a read of state. After round 10 closes, and until closeout runs, the public page keeps serving round 10's PLAN.html as if it were the ongoing round's. The ruling's subject is "the plan html for an ongoing round".
  - Cure: either retire the state ref at round close, or stage only while the round's roster is open. Then fix the body and header sentences.

  Carry: R10-OUTSIDE-INTAKE
- **Gate edit-run deferral reds recur at this head after R10-HOTFIX-GATE-BUSY-DEFER merged.**
  - Claim: these concluded `failure`, each with the single line `FAIL run(s) [42361045445] at this head are still being judged; their gate decides` (`KIND: edit`):
    - `gate` 128369699756 (09:47:09Z-09:59:21Z)
    - `gate` 128382850917 (10:49:53Z-11:01:53Z)
    - `gate` 128382978616 (10:50:30Z-11:02:29Z)
  - The base 62bcca76 already contains #3276 (`cc100c275`, "a deferring edit gate waits like any other"). The body says the reds it names "are not the busy-deferral red R10-HOTFIX-GATE-BUSY-DEFER (merged) removed". These three are exactly that red, after a roughly 12-minute wait.
  - Evidence: `ev/red-details.txt` and `ev/check-runs.tsv`.
  - Harness: the check-runs and job-log API.
  - Metric: the conclusion and the FAIL line.
  - Perturbation: none applies; this is a read of state. The later `gate` runs 128388861998, 128389118396 and 128389122431 concluded success.

  Carry: R10-HOTFIX-GATE-BUSY-DEFER
- **`## Red checks` is incomplete at the head.**
  - Claim: the section names 55 check runs on one page. The `filter=all` read now holds 160 runs on two pages.
  - It does not name the three `gate` reds above, or the second `tests / nightly-status` failure, 128382846793 (10:49:52Z-10:50:04Z). That failure has the same cause as 128369432665, main's cancelled Nightly 42357667261.
  - Evidence: `ev/check-runs.tsv`.
  - Harness: the check-runs API.
  - Metric: concluded reds not named.
  - Perturbation: none applies; this is a read of state.

  Carry: R10-OUTSIDE-INTAKE
- **Stale line citation.** The body cites the review-comment read as L210 in `one_thread`. At this head, and already at 0fd9bc6d, it is L227 (`grep -n 'if r\["kind"\] == "pr"' tools/audit/seat/outside_intake.py`). Carry: R10-OUTSIDE-INTAKE
- **Round-3 plausible findings still unpinned.** `scan_disc_kind` and `owed_reply_ge` still SURVIVE the cases-only run (`ev/reviewer-mutants-casesonly.txt`). The body leaves them to the round-3 verdict, and they are carried again here so that the next seat sees them. Carry: R10-OUTSIDE-INTAKE

## Evidence

- Setup: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`. `review_packet.py render` gave rc 0 (`ev/packet.log`). I re-read the live checks afterwards.
- Round-4 delta 0fd9bc6d..aa5022f6, branch-own: only `b83f2f43c`, which adds 6 lines to `tools/audit/seat/outside_intake_selftest.py`. The rest are main merges. `git diff --quiet 28f9f11bb aa5022f63` printed TREES-IDENTICAL. `outside_intake.py`, `plan_public.py` and `pages.yml` are unchanged since 0fd9bc6d (the diff is 0 lines).
- `outside_intake.py` mutation proof, cases only, 47 mutants (`ev/reviewer-mutants-casesonly.txt`, runner `ev/mut.py`): NULL rc 0, 43 KILLED, 4 SURVIVED.
  - `one_thread_pr_reviews_drop`: now KILLED by its named case.
  - `mark_old_restored_EQUIV`: declared equivalent.
  - `has_disc_ignored`: equivalent in output.
  - `plan_live_200`: near-equivalent, network-only.
  - `scan_disc_kind` and `owed_reply_ge`: see `## Findings`.
- Full `outside_intake.py --self-test` at the head: `all checks passed`, rc 0, 48 `ok` lines, of which 21 are mutant lines. That matches the body's 27 cases and 21 mutants (`ev/selftest.txt`).
- `plan_public.py` mutation proof, cases only, 16 applied (`ev/reviewer-mutants-plan_public.txt`, runner `ev/mut_pp.py`). The runner's "first FAIL line" column shows the first failing case in output order, not necessarily the named one. I confirmed `absent_rc1` against its named case in a full run.
  - KILLED: `int_dropped`, `max_to_min`, `regex_no_end`, `html_check_off`, `leak_off`, `attribution_off`, `refused_rc0`, `absent_rc1`, `noref_rc0`, `write_empty` and `dest_name`.
  - SURVIVED and non-equivalent: `host_ident_dropped`, the block.
  - SURVIVED and equivalent or near-equivalent:
    - `rc_ignored_refs`: a failed `for-each-ref` prints nothing.
    - `show_rc_ignored`: a failed `git show` prints nothing on stdout.
    - `empty_text_published`: an empty page goes from rc 2 to rc 1, refused either way.
    - `html_case_sensitive`: `plan_page.py` writes a lowercase `<!doctype html>`, at L980 and L568.
  - `main_rc0` lies outside the code section the runner mutates, so I ran it separately: it survives the full self-test (the block).
- Pages workflow design (`.github/workflows/pages.yml`):
  - The plan is staged from the dispatched ref's tree before the newest `v*` tag is checked out, and copied into `_site/plan/` only when a page was staged. The markdown guard still runs last.
  - `entities.py` pins the order, the tag-skip and the rc mapping (2 warns and passes, 1 is red) over a stub.
  - The trigger set is unchanged (tag push plus dispatch). The `push:` route on the state ref is rightly rejected, since an orphan ref carries no `.github/`.
  - The page is linked only from `dev/programme/HANDOVER.md` (developer documentation).
  - `PLAN_URL` is spelled once.
- Privacy on the runner: `Identity.of_host()` there is the runner's own account, so the account-name and home checks read the runner, not the orchestrator. The generic `host-path` class (`/home/<x>`, `/Users/<x>`) and the scratch-root class do not depend on identity. My drive confirms a page naming another account's home directory is refused (rc 1). Nothing scans for secrets or tokens. The PLAN.html source is the orchestrator's own generated page, so I record that gap here and not as a finding.
- CI on this head, read job by job across all pages (`ev/check-runs.tsv`, 160 runs). Concluded reds:
  - `gate` 128369699756, 128378686810, 128378835497, 128382850917 and 128382978616.
  - `pr-contract / pr-contract` 128378515649.
  - `tests / nightly-status` 128369432665 and 128382846793.
  - `governance / instrument-self-tests` 128369432606, cancelled at the 30-minute timeout (owner's standing line, cure R10-PROCESS-SLIM, #3245).

  Each is superseded:
  - `governance / instrument-self-tests` 128382846790 concluded success (10:49:52Z-11:17:08Z), so the self-tests pass at this head.
  - `pr-contract` 128382814711, 128389122891 and 128388623658 concluded success.
  - `gate` 128388861998, 128389118396 and 128389122431 (11:18Z-11:20Z) concluded success.
  - `tests / nightly-status` is unrequired, and grades main's cancelled Nightly 42357667261, which this diff does not read.
- `merge_train.py classify aa5022f6... --pr 3262`: `GREEN aa5022f63cac715abe871d168d2ed250997261e7 pending: none red: none` (rc 0, `ev/classify.log`). I agree on the required checks. The block does not depend on CI.
- Merge: `git merge-tree --write-tree origin/main HEAD` against 08fd676e gives rc 0, tree 056d03ccabd02e17d68092f5666ab4c4993b8913, with `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge.txt`).
- Cheap checks at the head (`ev/checks.txt`):
  - `ref_privacy --check`: 0 refused. `tmp_paths`: 0 refused.
  - `selftest_wiring`: 120 self-testing, 120 wired, 0 unwired, 0 index gaps.
  - `plan_public self-test: all checks passed`. `beat_jobs self-test: 136 checks, 0 failed`.
  - `STRUCTURE RATCHET PASSED`. `ALL 2643 ENTITY CHECKS PASSED`, so the new tracked files are classified. `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - The three-dot diff touches no `*budgets.json`, `VERSION`, `RELEASE_NOTES.md` or manifest, and `dev/programme/delivery/3262.md` is in it.
- `## Head`: it names aa5022f63 as the PR head and 28f9f11bb as the measured, tree-identical code head, which matches what I measured. The head did not move during my review.
- Round 4 is past three. `fixer.md` owes a re-cut, but the block above needs only one added `plan_public.py` self-test case and two mutants, not a redesign.
- The owner's 2026-11-06 ruling is quoted verbatim in the body. Policy part: it merges only on tvofi's approving review at the head.
