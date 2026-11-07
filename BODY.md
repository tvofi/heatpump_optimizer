Fold the 2026-11-06 out-of-tree sweep changes into the tracked sweep scripts the owner ruling names, so that one overlay renders the sweep and also feeds the beat rows. Repair round 5 for the `architecture-unsound` block on `verdict/3267` at `14a73c15`. This version re-takes the body only, for the `pr-contract` refusal on `tests / nightly-status`; no code changed.

Owner ruling (tvofi 2026-11-06), verbatim: "There should already be tracked sweep templates/scripts for these, update them if needed".

Review accepted these parts and this round leaves them unchanged:
- `sweep_runner.sh`, `sweep_runner_selftest.py` and `roster_drain.py` are gone.
- `gantt` and `verdict-audit` are `beat_jobs.py` rows with `beatd.jobs.json` entries.
- `PLAN MOVED` is in `plan-beat`.
- (4b) is the single owner.

This round makes only the four named repairs:

1. **The block.** `tools/audit/seat/sweep_template.md`'s `## Placeholders` table now declares the five overlay keys the new rows read: `gantt_roster`, `gantt_acks`, `fire_ledger`, `train_glob` and `unheld_skip`. (4b) cites `{{gantt_roster}}`, `{{fire_ledger}}` and `{{gantt_acks}}`. (4c) cites `{{fire_ledger}}`, `{{train_glob}}` and `{{unheld_skip}}`. `sweep_render.py` refuses a declared name that is never used, so each one is used.
   - All five are declared as required placeholders, not as `OPTIONAL_FLAGS`. `sweep_render.py`'s optional flags render as `pulse.py` flag text inside a command. (4b) and (4c) cite these keys as files in prose, so flag text would be wrong there.
   - A session running the beat has all five files, so requiring them costs nothing. `beat_jobs.py`'s own tolerance of an absent optional key is unchanged.
   - A new census in `beat_jobs_selftest.py` keeps the defect from returning unseen. It parses `beat_jobs.py`, reads every overlay key the file reads, and compares them with `sweep_render.declared()` of the tracked template. It counts `ctx.need(...)`, `.get(k)` and `[k]` on the overlay, plus a key bound by a `for` loop over a literal tuple. `need`'s own body is skipped, because its callers are the reads. Any read whose key it cannot resolve fails the census rather than being skipped.
2. **The four surviving gantt mutants, plus the fetch rc.** M3 to M12 are the reviewer's mutant numbers.
   - The `gantt` row's `git fetch` rc is now checked. On a failed fetch the row writes `gantt: UNREADABLE fetch rc=<n>: <last stderr line>` and returns. Before, it went on to `git show` the stale `refs/gantt/roster` left by the last pass, and to its handoff tips.
   - Five failing-first cases cover each guard and input, and each carries its null:
     - the `gh pr list` rc (M3)
     - the roster `git show` rc (M4)
     - the new fetch rc, the stale-roster case M4 exposed
     - the `handoff-wip/*` refspec (M11), with a fake `git` that lists only the tip namespaces the fetch named
     - the copied fire ledger (M12)
   - Each case is registered as a `MUTANTS` entry.
3. **The body**, re-taken whole from `.github/PULL_REQUEST_TEMPLATE.md`. `## Red checks` names every red from the reviewer's `filter=all` read.
4. **The gate checks** are re-run. Each is listed under `## Figures`.

## Head

`7bfd1bc5bbf0f0ec69e3ab5a193982ad78c1fb79`. It is `fix/r10-sweep-template-sync`: the code commit `e64e24a5` (repair round 5) plus four merges of `origin/main` that arrived after it (`a7223767`, `313862a9`, `e671c1bb`, `179c5403`) and the current merge `7bfd1bc5` of `main` at `4b5d771b`. The merges change no file this PR edits, and the PR's own files are byte-identical to `e64e24a5`. This re-take changes the body only; the head did not move.

Every figure below was measured on this tree. `git rev-list --count HEAD..origin/main` printed 12 at 2026-11-07T17:40Z, because `main` merged twelve commits after `4b5d771b` (the last is #3280). This round does not merge them, since the merge verdict stands at `a7223767` and the head must not move. The full `tools/pr/prepr.sh` run at `e64e24a5` refused only `figures`, and that was repaired (see `## Figures`). The checks that follow that run are the ones under `## Red checks`.

## Mutation proof

The in-tree harness is `beat_jobs_selftest.py` `MUTANTS`, run by `python3 -I tools/audit/seat/beat_jobs.py --self-test`. Each mutant plants one edit in a temporary copy and names the case that must fail. All five new mutants are killed:
- `gantt_gh_rc_ignored` (M3) is killed by `gantt: a failed gh pr list is UNREADABLE and runs no sweep_gantt (null: rc 0 runs it)`.
- `gantt_show_rc_ignored` (M4) is killed by `gantt: a failed roster git show is UNREADABLE and runs no sweep_gantt (null: rc 0 runs it)`.
- `gantt_fetch_rc_ignored` is killed by `gantt: a failed fetch is UNREADABLE, never the stale refs/gantt/ roster (null: rc 0 runs it)`.
- `gantt_wip_refspec_dropped` (M11) is killed by `gantt: a handoff-wip tip is fetched and reaches sweep_gantt beside the handoff tip`.
- `gantt_ledger_not_copied` (M12) is killed by `gantt: the fire ledger is copied whole for sweep_gantt (null: no fire_ledger copies nothing)`.

The earlier ten `MUTANTS` from this PR are still killed in the same run.

Failing first, with each file put back after its run:
- With `14a73c15`'s `sweep_template.md` restored, the self-test prints `FAIL census: every overlay key beat_jobs.py reads is declared in sweep_template.md's Placeholders` (2 failed: the census and its null).
- With only the `| `unheld_skip` |` row deleted from the fixed template, the same census FAILs (2 failed). This is the mutation proof the repair asked for: remove one declaration and the check fails.
- With `14a73c15`'s `beat_jobs.py` restored, the self-test prints `FAIL gantt: a failed fetch is UNREADABLE, never the stale refs/gantt/ roster (null: rc 0 runs it)`, and the fetch mutant's site is absent.

## Null control

- The new gantt cases share one null pass: `gh` rc 0, `git show` rc 0 and fetch rc 0 run `sweep_gantt.py` and write no digest. Each failure case asserts that null and also asserts that its own line was absent before the run.
- `census null: the template without its gantt_roster row is reported missing exactly gantt_roster` shows the census reads the template it is given.
- `census null: an overlay read by a computed key is unresolved, never skipped` shows that a read shape the census does not know fails it.
- The fire-ledger case's null is a run with no `fire_ledger`, which writes an empty `fired.txt`.
- The finder's render probe is under `## Figures`.

## Figures

- The finder's own harness, `python3 -I $EXPORT/ev/keys.py <tree>`, where `$EXPORT` is the export of `probe/rev-3267-0b9792ab` (`309cc955`) and the file's sha1 is `ceb1b40c5754939ef9e38081e983c307323069d8`. It prints the overlay keys `beat_jobs.py` reads that the template's placeholder table does not declare:
  - at the merge base `294a880d`: `[]`
  - at `14a73c15`: `['fire_ledger', 'gantt_acks', 'gantt_roster', 'train_glob', 'unheld_skip']`, so the metric is 5
  - at this head `7bfd1bc5`: `[]`, so the metric is 0 (re-run at this head, `ceb1b40c` sha1 unchanged)
- The render probe, from a scratch port of that harness: `python3 -I $EXPORT/ev/render_probe.py <tree>`, a scratch file with sha1 `9355ff86f6abd8b79a9b5f57ee725bdb66f0dfe1`, kept out of the tree.
  - At this head, the control render with only the declared keys prints `OK`, and each of the five keys renders `OK`.
  - Its null control, adding the undeclared `zz_undeclared_probe`, prints `REFUSED: unknown: zz_undeclared_probe not in the placeholder table`.
  - At `14a73c15`, each of the five keys printed `REFUSED: unknown`.
- The class rule: the census in `python3 -I tools/audit/seat/beat_jobs.py --self-test` enumerates every overlay read in `beat_jobs.py`. It returns 16 keys and 0 unresolved reads, and every key is declared. No other script reads the sweep overlay as `beat_jobs.py` does, since `Ctx` is its one reader.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test` prints `159 checks, 0 failed` at this head. The count is cases plus `MUTANTS`, so the instrument is named rather than a number.
- `python3 -I tools/audit/seat/sweep_render.py --self-test` prints `34 checks, 0 failed` on the edited template.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `120 self-testing, 120 wired, 0 unwired` and 0 index gaps.
- `python3 -I tools/audit/seat/sweep_gantt.py --self-test` prints `16 checks, 0 failed`, and `verdict_audit.py --self-test` prints `14 checks, 0 failed`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2645 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, with no re-record and no raise.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, namely `tests/entities.py` and `tests/harness_headers.py`. Both pass locally.
- Protected files: `git diff $(git merge-base origin/main HEAD)...HEAD` touches neither `VERSION`, the manifest, `RELEASE_NOTES.md` nor any `*_budgets.json`. `git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` exits 0, so both claim files are byte-identical to main. `dev/programme/delivery/3267.md` stays in the diff.

## Red checks

Source: `gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs?filter=all&per_page=100 --paginate` (every page) at each head in the chain, read at 2026-11-07T17:30Z to 17:45Z, plus `list_workflow_jobs` with `filter=all` for run 42369836867. Each red is named by its literal check-run name.

At `7bfd1bc5` (code run 42388515797, edit run 42388515874):
- `tests / nightly-status` failure 128451280114. Its log: `NIGHTLY FAILED: mutation-ledger (1), mutation-ledger (2), mutation-ledger (3), mutation-ledger (4), mutation-ledger-push, mutation-nightly, slow failed in the last verification dispatch.` Class: a red that grades `main`, not this diff. This diff does not cause it:
  - The dispatch it reads is Nightly run 42369836867 (workflow_dispatch, 2026-11-07T11:50Z, head `08fd676e`, conclusion cancelled). That head is `main`, which does not contain this PR, so no line of this diff ran in it.
  - Every failing lane is `cancelled`, none is `failure`. All seven stopped within five seconds (12:09:12Z to 12:09:17Z), 19 minutes after the 11:50 start, in the middle of their long steps (`Drive a slice of the unpinned stock`, `Drive the table over the whole package`, `Zone-sensitive scripts under Asia/Kolkata`). That is a whole-run cancel, not a test failure. `nightly-ha (2025.2.0)`, `nightly-ha (stable)` and `record-autofix` in the same run concluded success.
  - The diff reaches none of those lanes. Its one workflow edit is a new step in governance.yml's `instrument-self-tests` job, which `nightly.yml` does not call. `grep -nE 'sweep_gantt|verdict_audit|beat_jobs|sweep_template|beatd'` over `.github/workflows/nightly.yml`, `tests/nightly_status.py` and `.github/actions/*/action.yml` finds nothing. The six other files (`beat_jobs.py`, `beatd.jobs.json`, `sweep_gantt.py`, `verdict_audit.py`, `sweep_template.md`, the self-test) are read by no lane that failed.
  - Nightly has been green on `main` since: runs 636, 637, 638, 640, 641, 642 and 643 (the last at `aaaec212`) all concluded success. A later verification dispatch, run 42382408131 (run 639, head `a37c58e5`), was still `in_progress` at 17:40Z. It is the dispatch that will turn the check green when it concludes; nightly.yml's workflow_dispatch owns it. This PR dispatched none, and has no fix to prove, since it changes no lane.
  - Answer, in the error line's terms: the cheaper detector is this check itself, which already names the failing lanes in seconds (11 s at this head). Its standing cost is one unrequired seconds-long job per pull request, which is already paid. The remaining gap is that it cannot tell a cancelled lane from a failed one, so a whole-run operator cancel reads as seven reds. That is a finding for the check's owner, not for this change, and it is the root-cause record #3277 already opened for whole-run cancels at live heads.
- `pr-contract / pr-contract` failure 128463906157, step `Check the body against the contract`: the same missing answer for `tests / nightly-status`, which the section above now gives. The same failure occurred at `179c5403` (128443814748), `e671c1bb` (128421285272) and `313862a9` (128395187227). Class: a body gap, repeated by each earlier body. Answer: this body names the check; the detector is `tools/pr/prepr.sh --body-check`, which `body_push.sh` runs before every handoff, standing cost one local run per handoff. It passes only once a red check on `main` has been answered, so it was not predictive earlier, because `nightly-status` was not red when those bodies were checked locally.
- `gate` failure 128464173465 (code run): a consequence of the `pr-contract` failure above (`gate` lists it as the one required check failing). It clears when `pr-contract` does.
- `gate` failure 128454385359 (edit run 42388515874): the edit-run deferral, `FAIL run(s) [42388515797] at this head are still being judged; their gate decides`. R10-HOTFIX-GATE-BUSY-DEFER (#3246) owns it, and the code run's gate decides.

At `179c5403` (the head before the current merge):
- `governance / instrument-self-tests` cancelled 128446540557 and 128434097444, `gate` cancelled 128451291094: cancelled by the supersession of the run when the head moved. No detector is owed.
- `tests / nightly-status` failure 128446540238 and 128434097501: the same cross-check on `main`, answered above.
- `pr-contract / pr-contract` failure 128443814748, `gate` failure 128444916386 and 128434367320: as above (the contract failure, its gate, and the edit-run deferral).

At `e671c1bb`: `pr-contract / pr-contract` 128421285272, `gate` 128421455266 and 128412227251, `tests / nightly-status` 128411353740: as above.

At `313862a9`: `pr-contract / pr-contract` 128395187227, `gate` 128395361772 and 128386088181, `tests / nightly-status` 128385850147: as above; `governance / instrument-self-tests` cancelled 128385850174, superseded.

At `a7223767`:
- `governance / instrument-self-tests` cancelled 128378807832 (attempt at 08:54:51Z to 09:25:05Z): class A, the 30-minute job timeout. It is owned by R10-HOTFIX-SELFTEST-TIMEOUT, and the cure is R10-PROCESS-SLIM #3245. No cheaper detector exists: the timeout is a wall-clock limit on the whole job. The job concluded success at the next head (128451280171, 28 minutes 21 seconds), so it is cleared.
- `gate` failure 128378814076 (edit-run deferral): R10-HOTFIX-GATE-BUSY-DEFER, #3246.

Earlier heads `14a73c15`, `61f1ec71`, `0ae78ac1`, `aa680f8b`, as carried from the previous body (read from the reviewer's `filter=all` capture):
- `gate` failures 128312324401, 128279140047, 128285014276, 128290983518: edit-run deferral, R10-HOTFIX-GATE-BUSY-DEFER (#3246). The code-run gates concluded success.
- `arch-score / arch-score` cancelled 128324556485 and 128307712802, `gate` cancelled 128308899754 and 128288757875, `pr-contract / pr-contract` cancelled 128288387497, `refresh` cancelled 128219412787 and 128219395325, `prelude` cancelled 128219412437 and 128219395266, `gate` cancelled 128219559757 and 128219558260: all supersession by a newer run. No detector is owed.
- `pr-contract / pr-contract` failure 128231570697: round 1's body failed the contract. The cheaper detector is `tools/pr/prepr.sh --body-check`; its standing cost is one local run per handoff.
- `gate` failure 128231841950, 128221754844 and 128220043119: round 1's head. The re-cut cleared them; the scoped-gate selection run locally before handoff is the cheaper detector.
- `CodeQL` failure 128219897245 (code-scanning alert 51, py/overly-permissive-file): its site, `sweep_runner_selftest.py`, was deleted. `codeql / Analyze (python)` 128451280044 and `CodeQL` 128451838188 concluded success at the current head. No cheaper detector exists: building a local CodeQL database per seat costs what the Analyze leg already pays.

## Forward-carry

none

## Friction

none
