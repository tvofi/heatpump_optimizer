Fix review: blocked a7d97f55b44182545c5b5b199dfd1151113123de other: level-0-rename-hole: lane_skip Level 0 reads closure.changed_files, a rename-detecting name-only diff, so a source file renamed onto a delivery row reads as a record-only diff and browser, coverage and typing skip
bus-nonce: ac87f27f09739a0623f3eca85fb08a2e

Round 1 (no earlier `Fix review:` comment on #2406). Reviewed from a detached worktree at `a7d97f55b44182545c5b5b199dfd1151113123de`. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` was empty, so the contract copy is current. Evidence: `~/hpo-seats/r10s3/review-2406/evidence/`.

## The blocking finding

Level 0's safety argument is that every file in the PR's diff is a roster or a canonical delivery row. `_decide_cmd` gets that list from `closure.changed_files`, which runs `git diff --name-only <base>...HEAD`. That diff detects renames (`diff.renames` defaults on), so a renamed file shows only its destination. The deleted source path never reaches `is_record_file`.

Probe (local commit, never pushed): on the head, `git mv custom_components/heatpump_optimizer/__init__.py dev/programme/delivery/99999.md`, then run the shipped `lane_skip.py decide` against `HEAD~1`:

```
name-only:              dev/programme/delivery/99999.md
name-only --no-renames: custom_components/heatpump_optimizer/__init__.py
                        dev/programme/delivery/99999.md
LANE: typing -- SKIP (level 0)
LANE: coverage -- SKIP (level 0)
LANE: browser -- SKIP (level 0)
LANE: fast -- RUN
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
```

So a diff that deletes the integration's `__init__.py` skips all three lanes, with no proof. Typing never skipped on a pull request before this PR, so for `typing` the hole is new. Push to main still forces every lane, so main goes red one merge later. That backstop is the same one the gate already relies on, and it is not the argument the body makes for Level 0. The body says the match is anchored and exact. The pattern is, but its input is not.

The fix belongs in this PR: build the Level 0 list with `--no-renames` (or name-status, both sides of each rename), and pin it beside the existing twins: "`<lane>` runs when a non-record file is renamed onto a delivery row".

**The class is wider than this PR (step 6).** The same `closure.changed_files` feeds `closure.select`, and the probe's last line shows the gate scoping that rename to `SCOPED -- 0 script(s) run`. That is a hole in gate scoping that predates this PR. `tests/closure.py` is not in this diff. Other `git diff --name-only BASE...HEAD` consumers in `tests.yml` (`graders-head-copy`'s changed step, `composed-proof`'s arm step) have the same shape, and I did not enumerate them all. The orchestrator owes this a fold or a dispatch (out-of-scope findings get fixed). Fixing it in `changed_files` would close both seams at once, but that is a gate-scoping change to a code-owned file.

## RESULT lines

- RESULT self-tests at head (`evidence/selftests-head.txt`): `roster_lib` 18/0 failed, `orchestrator_tick -W error` 104/0, `state_docs` all passed, `plan_table` 25/0, `resume_doc` 14/0, `handover_prompt` 13/0, `lane_skip` 50/50. These match the body.
- RESULT mutation proof (step 1), my own re-runs (`evidence/mutants.txt`), each restored afterwards:
  - Level 0 guard set to `False`: `lane_skip` 44/50 (the six level-0 skip pins). Matches the body's MB5.
  - Absent-branch check removed: `roster_lib` 18 checks, 1 failed. Matches MB1.
  - Beat memo set to main's tip alone: `state_docs` 8 checks failed, including arm 2b. Matches MB3.
  - My own extra mutant, the WARNING (main-ahead) check removed: `roster_lib` 1 failed (`main moved the roster past the branch`). Not vacuous.
- RESULT harness (steps 2, 8, 9): this work has no finder harness. It is an O17 tooling item, and its one quantified claim is the body's `jq | diff` pipeline, which lives only in the body and not in the tree. That is itself a finding (step 9). Re-derived under the body's rule at `63816b857` against `07ba56db1`: main vs branch has 10 `>` lines (4 changed stages plus 6 groups main lacks), and main vs main has 0. The count is confirmed.
- RESULT null control (step 3): live, at origin/main `413944b67` with branch `07ba56db1`, `default_roster_ref(git_in(wt))` returns `('origin/handoff/audit-r10-roster', '')`. That matches the body's live arm. The absent-branch arm is pinned by the mutants above.
- RESULT claims (step 4): neither claim file nor any golden fixture is in the diff. `env_drift` was not run, because there are no fixtures to drift.
- RESULT version (step 5): `VERSION`, the manifest and the `RELEASE_NOTES.md` heading are untouched.
- RESULT head (steps 7, 12): the body names `a7d97f55b…`, and `gh pr view` reports the same head at verdict time.
- RESULT conflict (step 13): `git merge-tree --write-tree origin/main(413944b67) a7d97f55b` returned rc 0 with no conflict.
- RESULT checks (step 11; `evidence/checkruns-head.tsv`, check-runs API): 37 runs and no red so far, but `coverage`, `fast (3.14)` and `Analyze (python)` were still `in_progress`. The head's workflows have not all concluded, so step 11's posting condition was not met when I wrote this.
- RESULT metrics (step 14): no budget, closures, ledger or calibration file is moved. The tick's self-test count 100→104 is the four new checks. Nothing here is gamed.
- RESULT architecture (step 15): `roster_lib` is the single owner of which ref the roster is read at, and the readers delegate to it. That is sound. The finding above is a correctness hole, not a design breach.

## Not blocking, to fold into the same repair round

- **The projection overstates its saving.** `graders-head-copy` has `if: !cancelled() && github.event_name == 'pull_request'` and no `needs.coverage.result != 'skipped'` guard, so it still runs when `coverage` skips (only its coverage step skips). The ~6.6 runner-min figure should drop its 0.2. `coverage-ratchet` does skip.
- **A false-positive WARNING after a squash landing.** `default_roster_ref` warns on `git diff --quiet <branch>...origin/main -- rosters/`. After a roster PR squash-lands, that three-dot diff is non-empty until main is merged back into the branch, even when the branch already holds the same content. It clears on the action the warning names, so it is not wrong, but it fires after every landing.
- **The live beat restart is a later-stage action** that so far exists only in this body's "Unpinned sites" section. It should go wherever the orchestrator's post-merge beat brief lives (`finding-propagation.md`).
