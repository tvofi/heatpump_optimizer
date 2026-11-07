Fold the 2026-11-06 out-of-tree sweep changes into the tracked sweep scripts the owner ruling names, so that one overlay renders the sweep and also feeds the beat rows. Repair round 5 for the `architecture-unsound` block on `verdict/3267` at `14a73c15`.

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

`e64e24a5c7d97937bd8876817bf4e5d640611c19`. It is `fix/r10-sweep-template-sync` at `14a73c15`, with `origin/main` merged at `be813ecd4924865b75489f12c56600e9432d5727` (merge `c84911cc`), plus one repair commit. Every figure below was measured on this tree. At 2026-11-07T07:19Z, `git rev-list --count HEAD..origin/main` printed 0. The full `tools/pr/prepr.sh` run at this head refused only `figures`, because this body cited the finder's harness by a path that is not in the tree. The repair cites it as `$EXPORT` with its sha1. `tools/pr/prepr.sh --body-check` then ran clean, and before the push `git rev-list --count HEAD..origin/main` again printed 0. `main` had not moved, so no second full run was owed.

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
  - at this head: `[]`, so the metric is 0
- The render probe, from a scratch port of that harness: `python3 -I $EXPORT/ev/render_probe.py <tree>`, a scratch file with sha1 `9355ff86f6abd8b79a9b5f57ee725bdb66f0dfe1`, kept out of the tree.
  - At this head, the control render with only the declared keys prints `OK`, and each of the five keys renders `OK`.
  - Its null control, adding the undeclared `zz_undeclared_probe`, prints `REFUSED: unknown: zz_undeclared_probe not in the placeholder table`.
  - At `14a73c15`, each of the five keys printed `REFUSED: unknown`.
- The class rule: the census in `python3 -I tools/audit/seat/beat_jobs.py --self-test` enumerates every overlay read in `beat_jobs.py`. It returns 16 keys and 0 unresolved reads, and every key is declared. No other script reads the sweep overlay as `beat_jobs.py` does, since `Ctx` is its one reader.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test` prints 0 failed. The count is cases plus `MUTANTS`, so the instrument is named rather than a number.
- `python3 -I tools/audit/seat/sweep_render.py --self-test` prints 0 failed on the edited template.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints 0 unwired and 0 index gaps.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL ... ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, with no re-record and no raise.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run`, namely `tests/entities.py` and `tests/harness_headers.py`. Both pass locally.
- Protected files: `git diff $(git merge-base origin/main HEAD)...HEAD` touches neither `VERSION`, the manifest, `RELEASE_NOTES.md` nor any `*_budgets.json`. `git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` exits 0, so both claim files are byte-identical to main. `dev/programme/delivery/3267.md` stays in the diff.

## Red checks

Source: the reviewer's `filter=all` read, every page, in `probe/rev-3267-0b9792ab:ev/red-history-filter-all.txt`.
- This seat read the PR head's check runs and the job list of run 42352016707 with `filter=all`, all pages, through the MCP tools. Earlier heads' reds come from the reviewer's read above.
- For the same reason, `review_packet.py render`, whose check-run read is a `gh api` call, was not run here. Every red that read lists is answered below, so a `red-unanswered` refusal has nothing left to name.

At `a7223767`, the PR head (run 42352016707, read with `filter=all` through the job list):
- `governance / instrument-self-tests` cancelled 128358602803 (attempt 2, 08:54:51Z to 09:25:05Z): class A, the 30-minute `instrument-self-tests` timeout. It is owned by R10-HOTFIX-SELFTEST-TIMEOUT, and the cure is R10-PROCESS-SLIM #3245. No cheaper detector exists: the timeout is a wall-clock limit on the whole job, which only the job itself measures. No attempt at this head concluded green. Attempt 1, 128342095963, was cancelled at 07:49:49Z by the supersession that ended the run's other jobs, and attempt 2 is the timeout. So this is a concluded red that stays at the head.
- `governance / env-matrix` cancelled 128342096436, `codeql / Analyze (python)` cancelled 128342095898, `gate` cancelled 128344632834, and the `tests / ...` jobs 128343442060, 128343442066, 128343442076, 128344592291, 128344592450, 128344593000, 128344617027, 128344617193 and 128344617628: all attempt 1 of run 42352016707, cancelled at 07:49:40Z to 07:49:52Z by supersession. Attempt 2 concluded success for `env-matrix` 128358602969, `codeql / Analyze (python)` 128358602971, `tests / fast (3.14)` 128358603580, `tests / coverage` 128358603274 and `tests / closures` 128358603452, and the gate 128368923846 and 128368919784 concluded success. They are supersession, not a defect, so no detector is owed.
- Gate failures from the edit-run deferral (`run(s) [...] at this head are still being judged`): R10-HOTFIX-GATE-BUSY-DEFER, merged as #3246. The edit run is the one that defers, and the code run 42352016707 decides. Its gates concluded success at 128368923846, 128368919784 and 128368179798. Answer: the hotfix owns it.

At `14a73c15`, the reviewed head:
- `gate` failure 128312324401: this is the edit-run deferral, R10-HOTFIX-GATE-BUSY-DEFER, merged as #3246. Its log reads `FAIL run(s) [42340579795] at this head are still being judged; their gate decides`, and gate 128324519569 later concluded success. Answer: no cheaper detector is needed, because the hotfix already owns the deferral.
- `arch-score / arch-score` cancelled 128324556485 and 128307712802, and `gate` cancelled 128308899754: all three were cancelled with superseded edit run 42340579009. They are supersession, not a defect, so no detector is owed.

At `61f1ec71`:
- `gate` failure 128279140047, 128285014276 and 128290983518: the same edit-run deferral, R10-HOTFIX-GATE-BUSY-DEFER (#3246). The decisive code-run gates concluded success. Answer: the hotfix.
- `gate` cancelled 128288757875 and `pr-contract / pr-contract` cancelled 128288387497: both are supersession by a newer run. No detector is owed.

At `0ae78ac1`:
- `pr-contract / pr-contract` failure 128231570697: round 1's body failed the contract.
  - Answer: the cheaper detector is `tools/pr/prepr.sh --body-check`, which `body_push.sh` runs before every handoff. Its standing cost is one local run per handoff, already paid.
  - This body passed that check before its push.
- `gate` failure 128231841950, 128221754844 and 128220043119: the gate failures of round 1's head. The re-cut cleared them, and the later gates at `61f1ec71` and `14a73c15` concluded success. Answer: the scoped-gate selection and its scripts, run locally before the handoff (see `## Figures`).
- `CodeQL` failure 128219897245 (code-scanning alert 51, py/overly-permissive-file): its site, `sweep_runner_selftest.py`, has been deleted. `codeql / Analyze (python)` 128309715588 and `CodeQL` 128310823880 concluded success at `14a73c15`, and no helper in this diff sets a file mode.
  - No cheaper detector exists: there is no standing local CodeQL run, and building one would cost a CodeQL database build per seat, which the PR's Analyze leg already pays.

At `aa680f8b`:
- `gate` cancelled 128219559757 and 128219558260, `refresh` cancelled 128219412787 and 128219395325, and `prelude` cancelled 128219412437 and 128219395266: all six were superseded by the push of `0ae78ac1`. No detector is owed.

At this head `e64e24a5`, no run had concluded when it was handed off, because the orchestrator moves the pull request to it. The defect-root-cause trigger is answered at `14a73c15`'s `pr-contract` 128321564289, which passed after the last red.

## Forward-carry

none

## Friction

none
