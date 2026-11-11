# Proposal triage, session s14, batch 198 (P622)

Sources:
- origin/main `ee64358be7` and `0a2139b1dd`. Line numbers are at `0a2139b1dd`.
- Main's `governance / instrument-self-tests` job at `ee64358be7`: job 130489627879 of run 43010208881.
- The same job on earlier main pushes: 130415622883 (`cbd23f1c8b`), 130402966157 (`f24d107bd7`),
  130398921357 (`45a8b828a4`) and 130394909969 (`e67b79c9fc`).
- #3446 (R10-HOTFIX-SELFTEST-SCOPE-UNION part 1), head `4cc5d8b962`, read from `refs/pull/3446/head`.
- Main's own CI run at `0a2139b1dd` (43026321528) was still queued when read, so (1) below is measured
  locally and (2) by the tree diff.

## P622: HOTFIX-PUSHER-CENSUS-FOLD

Verdict: ACCEPT, folded into the live hotfix group R10-HOTFIX-PUSHER-CENSUS (not started) as items 3
and 4. No new group. A red on main takes the hotfix route, not the proposal bar.

Source: triage queue line 302, 2026-11-11T13:20:17Z, orchestrator s14: MAIN RED. These are the two reds
in main's `governance / instrument-self-tests` at `ee64358be7` that P621 left outside its ruling.

Instances:
- **(1) The sweep renderer persists at `0a2139b1dd`.** `python3 -I tools/audit/seat/sweep_render.py
  --self-test` at a detached `0a2139b1dd` raises ``Refused: unused: `plan_coordinator_cap` declared and
  never used by the sweep`` from `render()` (`sweep_render.py:171`). Job 130489627879 shows the same
  traceback at log line 11441. `git diff --stat ee64358be7 0a2139b1dd` changes 9 files, all delivery
  rows and none under `tools/`.
- **Introducing merge for (1).** It is #3425 (`ee64358be7`). Its commit `c6c04f21b5` ("beat: plan-beat
  hands the overlay's plan_coordinator_cap to replan.py") added the row `plan_coordinator_cap` to the
  placeholder table (`tools/audit/seat/sweep_template.md:38`). It also added the overlay read in
  `tools/audit/seat/beat_jobs.py:419`. The sweep body never uses the placeholder:
  `git grep plan_coordinator_cap` finds no use in `sweep_template.md` past line 38. `render()` refuses
  a declared name the sweep does not use (`sweep_render.py:169-171`). An overlay that omits a name not
  listed in `OPTIONAL_FLAGS` (`sweep_render.py:93`) is also refused, yet the table row says
  "replan's own default when absent".
- **(2) The drift check: `selftest_scope check: 111 gated step(s), 19 refusal(s)`** (job 130489627879,
  log lines 18805-18827). The 19, attributed:

  | refusals | steps | cause |
  |---|---|---|
  | 6 UNMEASURED | orchestrator-tick, selftest-wiring, throwaway-git-helper, merge-train, carry-check-and-the, train-launcher | (1). Each step's `if:` (`governance.yml:724`, `:746`, `:1243`, `:1257`, `:1271`, `:1283`) lacks `!cancelled()`, so each was skipped after the sweep-template step (`:707`) failed. |
  | 1 | sweep-template probes `<unknown>` | (1). The renderer crashed. This is not a read, so it is never recorded. |
  | 6 | verdict-bus and review-packet: `dev/governance/roles/fix-review.md`; prepr: 3 files; open-pr, pr-args, update-pr: probe `-c` | Pre-existing. These are the 6 the live R10-HOTFIX-SELFTEST-SCOPE-UNION part 1 adds (#3446, `tools/ci/selftest_closures.json` +9 lines). |
  | 4 | hooks-setup, open-pr, pr-args, update-pr: `tools/audit/seat/remerge_main_selftest.py` | #3425, which added that file. |
  | 2 | app-push: `tools/audit/seat/gh_read.py`; gh-call-log-shim: `tests/throwaway_git.py` | Run-to-run variance. Both are present at `45a8b828a4`, `cbd23f1c8b` and `ee64358be7`, and absent at `e67b79c9fc` and `f24d107bd7`. No group owns them. |

  The drift step runs only on a main push under strace (SELFTEST-SCOPE-UNION's brief:
  `governance.yml:297` and `:1496`). So no pull request measures any of these, and no local run
  can.
- **Null control.** Before #3425, at `cbd23f1c8b` (job 130415622883), the same check printed 8
  refusals. None was UNMEASURED, none was `<unknown>`, and none named `remerge_main_selftest.py`.
  The 11 that #3425 added are therefore its own, and the 8 are not.
- **Ownership.** The roster at `handoff/audit-r10-roster` `334095b9b6` has three live groups that
  touch `selftest_closures.json`, `selftest_scope` or `sweep_render`:
  - R10-HOTFIX-SELFTEST-SCOPE-UNION (in-progress, #3446 in review; the handoff freezes the branch).
  - R10-PRODUCT-PAGE-REDESIGN (product, unrelated).
  - R10-HOTFIX-PUSHER-CENSUS (not started, the other #3425 red in the same job).

Cost:
- Item 3: about 2 lines. One `OPTIONAL_FLAGS` entry in `tools/audit/seat/sweep_render.py`, and one
  placeholder use in step (4b) of `tools/audit/seat/sweep_template.md`.
- Item 4: 6 added read entries in `tools/ci/selftest_closures.json`.
- No new check, file, lane or group. The census fixer, a sonnet, already reads this job.
- The fold puts three more files in the group's set. It adds no review round of its own.

Binding: main's gating self-test job must be green before the stamp. Both reds share the census's job
and merge. Item 3 is the renderer's own documented remedy for a declared optional placeholder. Item 4
is union-only, and it leaves #3446 untouched.

The fold:
3. **SWEEP-RENDER-OVERLAY-KEY.**
   - Add `"plan_coordinator_cap": "--coordinator-cap"` to `OPTIONAL_FLAGS` (`sweep_render.py:93`).
   - Add `{{plan_coordinator_cap}}` after `--seats {{plan_seats}}` in step (4b)'s replan command
     (`sweep_template.md:76`).
   - Demonstration: `sweep_render.py --self-test` prints `0 failed`, rc 0.
   - Null control: with the placeholder use removed, the self-test raises the same `unused:` refusal,
     as it does at `0a2139b1dd`.
   - Do not loosen the unused-placeholder rule.
4. **SELFTEST-READS-3425.**
   - Add to `tools/ci/selftest_closures.json`, union only and never replacing an entry:
     - hooks-setup, open-pr, pr-args and update-pr files += `tools/audit/seat/remerge_main_selftest.py`;
     - app-push files += `tools/audit/seat/gh_read.py`;
     - gh-call-log-shim files += `tests/throwaway_git.py`.
   - Record no `<unknown>` probe.
   - Before the push, a python set check: for these 6 steps, the selftest-closures artifact of run
     43010208881 (artifact 13852641879) minus the table is empty, excluding `<unknown>`.
   - If #3446 has merged, rebase onto it. Its entries and these sit in different arrays or steps.
   - Proof: the first traced main push after the census and #3446 merge prints `0 refusal(s)`. A
     refusal it still prints for one of the 6 re-enabled steps is a new read those steps make. It goes
     back to the orchestrator as a main-red line, with no commitment made here.
5. **Red check.** Item 2's red-check answer also covers the sweep-template step. The fixer answers
   why #3425 merged with `sweep_render.py --self-test` red, given that `sweep_template.md` is in that
   step's committed read set.

Not ruled here: the class. This is at least the fourth `selftest_closures.json` hotfix
(R10-HOTFIX-MAIN-SELFTESTS, R10-HOTFIX-PREPR-READSET, SELFTEST-SCOPE-UNION part 1, and now this one).
Its barrier is already SELFTEST-SCOPE-UNION part 2: a record step that takes the union, a pre-merge
detector, and a measured decision on the pull-request trace. That group owns it.
