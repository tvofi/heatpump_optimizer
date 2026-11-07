Fix review: blocked b9b6af68683febf678907b19d7e73be453bc5bb7 ci-red: code run 42385084286 was cancelled at this head and no re-run came within 60 minutes, so merge_train classify reads RED on gate

bus-nonce: fc4e799764c94c5691ed9dc4be8b700a

This is round 5 of the fix review of #3262 (R10-OUTSIDE-INTAKE), at head b9b6af68683febf678907b19d7e73be453bc5bb7. It is the minimal re-cut owed past three rounds. I worked from a detached worktree at the head. The merge base is a37c58e5f32123b4028e90983799dc2aa81816f8. This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.

## Block

The round-4 block is cured. Only CI blocks this head.

- **The round-4 block is cured.** In my own re-run, with the finder's set widened to mutate every line but the `MUTANTS` table, `host_ident_dropped` (L67) and `main_rc0` (L233) are each KILLED by a named check:
  - `host_ident_dropped`: "the CLI over a scratch repository: a clean page is staged, rc 0".
  - `main_rc0`: "the CLI over a scratch repository: a page naming a home directory is refused, rc 1 and nothing written".
  - The full `--self-test` prints both `ok   mutant ... killed by:` lines.
- **CI at this head is RED.**
  - What happened: code run 42385084286 (attempt 1, triggered by `hpo-author[bot]`) ended `cancelled` at about 15:46:18Z, with the required jobs still running. Those jobs were `tests / fast (3.14)`, `tests / browser`, `tests / closures`, `tests / coverage`, `governance / instrument-self-tests` and `codeql / Analyze (python)`.
  - The gate: `gate` 128449147307 (KIND edit, 15:46:01Z-15:47:29Z) concluded `failure` with `FAIL tests / fast (3.14): cancelled (run 42385084286)`.
  - My wait: I watched for a re-run or a head move from 15:47Z to 16:48Z. Neither came.
  - Final read: `merge_train.py classify` at 16:48:35Z gives `RED b9b6af68683febf678907b19d7e73be453bc5bb7 pending: none red: gate` (rc 1).
  - Why it blocks: a red CI never carries a merge verdict, and the code jobs that would show this tree green have not concluded at this head.
  - Cure: re-run run 42385084286, or push a fresh head. Then let the head's runs conclude, and take the next review at a green classify.
- **`## Red checks` names the previous head's reds, not this head's.** The section reads aa5022f63's 160 runs. At b9b6af686 it names none of the 15 concluded non-success runs (`ev/reds.tsv`). This is owed with the cure: once the head's runs conclude, the body must name each concluded red across all check-run pages and answer it. `defect-root-cause.md`'s red-check trigger applies.

## Findings

- **Red checks are stale at the head.**
  - Claim: `## Red checks` does not name the concluded reds at b9b6af686:
    - `gate` 128449147307, failure.
    - `gate` 128449368751, cancelled.
    - `tests / nightly-status` 128443914073, failure. It grades main's cancelled Nightly 42369836867 at 08fd676, which this diff does not read.
    - The cancelled jobs of run 42385084286.
  - Evidence: `ev/check-runs.tsv`, `ev/reds.tsv`, `ev/gate-128449147307.txt` and `ev/nightly-status-128443914073.txt`.
  - Harness: the check-runs API with `filter=all`, two pages.
  - Metric: concluded reds not named. This head has 15; the body names 0 of them.
  - Perturbation: none applies; this is a read of state.

  Carry: R10-OUTSIDE-INTAKE
- **Docstring and workflow-header sentence still false.**
  - Claim: the "between rounds there is no state ref" sentence stays in `plan_public.py`'s docstring and in the `pages.yml` header. Nothing retires `handoff/audit-r<N>-plan` before `closeout.py --apply`. The body now names the sentence as carried rather than claiming it.
  - Evidence: the round-4 verdict, plus `git diff aa5022f63 HEAD -- .github/workflows/pages.yml`, which is empty.
  - Harness: `newest_round` over the remote's refs.
  - Metric: the round it would publish.
  - Perturbation: none applies.

  Carry: R10-OUTSIDE-INTAKE
- **Two `outside_intake.py` mutants still survive.** `scan_disc_kind` and `owed_reply_ge` SURVIVE the cases-only run at this head (`ev/reviewer-mutants-casesonly.txt`). They are unchanged since round 4. Carry: R10-OUTSIDE-INTAKE
- **`plan_public.py main()`'s `url` subcommand exit status is unpinned.**
  - Claim: the mutant `main_url_rc1` (L227 `return 0` made `return 1`, after `print(PLAN_URL)`) survives.
  - Evidence: `ev/reviewer-mutants-plan_public.txt`.
  - Severity: low. Only the usage line in the docstring calls `url`, and no workflow or tool does (`git grep 'plan_public.py url'`).
  - `main_print_stdout`, which sends the success message to stderr, is cosmetic and equivalent for the workflow, which reads only rc.

  Carry: R10-OUTSIDE-INTAKE
- **Edit-run gate reds recur.** The edit-run gate reds (`gate` failing on a deferral, or on another run's cancelled jobs) recur at this head, after R10-HOTFIX-GATE-BUSY-DEFER. Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Evidence

- Setup: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`. `review_packet.py render` gave rc 0, with Refusals none (`ev/review-packet.md`, `ev/packet.log`).
- Round-5 delta aa5022f6..b9b6af68, branch-own:
  - `78389d732`: the CLI case and two MUTANTS entries.
  - `22e1f930f`: the `throwaway_git_init` scratch repository.
  - The rest are main merges.
  - `outside_intake.py`, `outside_intake_selftest.py`, `pages.yml` and `dev/governance` are unchanged since aa5022f6 (`git diff --quiet` held).
  - Only `tools/audit/seat/plan_public.py` changed: 41 lines added, 4 removed.
- `plan_public.py` mutation proof (`ev/mut_pp.py`, `ev/reviewer-mutants-plan_public.txt`): the finder's 18-mutant round-4 set, widened to mutate code above and below the table, plus 2 new main() mutants. Cases-only.
  - Null control: NULL rc 0.
  - KILLED (15): `int_dropped`, `max_to_min`, `regex_no_end`, `html_check_off`, `leak_off`, `attribution_off`, `host_ident_dropped`, `refused_rc0`, `absent_rc1`, `noref_rc0`, `write_empty`, `dest_name`, `main_rc0`, `main_repo_cwd_ignored`.
  - SURVIVED, equivalent or near-equivalent as in round 4: `html_case_sensitive`, `rc_ignored_refs`, `show_rc_ignored`, `empty_text_published`.
  - SURVIVED, new: `main_print_stdout` (cosmetic) and `main_url_rc1` (finding above).
- Full `plan_public.py --self-test`: rc 0, 18 `ok` lines, of which 6 are mutant lines (`ev/selftest_pp.txt`). That matches the body's 12 cases and 6 mutants. The named kills for `host_ident_dropped` and `main_rc0` are printed there.
- Real CLI drive (`ev/drive_pp.sh`, `ev/drive_pp.txt`): the clean page gives rc 0 and is staged; the leaky page gives `REFUSED ... host-path in the page`, rc 1, and nothing is staged.
- `outside_intake.py` mutation proof, cases-only (`ev/mut.py`, `ev/reviewer-mutants-casesonly.txt`): NULL rc 0, with the same results as round 4.
  - `one_thread_pr_reviews_drop` is still KILLED by its named case.
  - Survivors: `mark_old_restored_EQUIV`, `scan_disc_kind`, `owed_reply_ge`, `has_disc_ignored` and `plan_live_200`.
- Cheap checks at the head (`ev/checks.txt`):
  - `ref_privacy`: 0 refused. `tmp_paths`: 0 refused.
  - `selftest_wiring`: 120 self-testing, 120 wired, 0 unwired, 0 index gaps.
  - `throwaway_git`: 0 refused.
  - `STRUCTURE RATCHET PASSED`. `ALL 2646 ENTITY CHECKS PASSED`. `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - `Architecture score: dS +0.0000 NULL`.
  - `outside_intake self-test: all checks passed`.
  - No budgets, VERSION, RELEASE_NOTES, manifest or claim file is in the three-dot diff (count 0), and `dev/programme/delivery/3262.md` is in it.
  - Every body figure re-derived equal.
- Merge: `git merge-tree --write-tree origin/main HEAD` against 1c1ae100b gives rc 0, tree b20199172aec2799b66623bceff6d333adc55591, with `LEDGER-MERGE: resolved tests/closures.json`.
- `## Head`: it names b9b6af686 merging f69a1caf9, which matches what I measured. The head did not move during the review.
- CI: `ev/check-runs.tsv` (55 runs, all pages) and `ev/classify.log`. The classify history ran WAIT from 15:35Z, then RED at 15:47Z and RED again at 16:48Z.
- The owner's 2026-11-06 ruling is quoted verbatim in the body. This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.
