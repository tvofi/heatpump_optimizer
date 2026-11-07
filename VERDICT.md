Fix review: blocked 14a73c15e5f060069f0fd4831eb46a436bd14f1d architecture-unsound: the gantt and verdict-audit rows read five overlay keys the sweep template does not declare, so sweep_render refuses any overlay that can feed them

bus-nonce: 0b9792ab011dd72ab3a3d5cf4d413916

## Block

Round: second review of #3267 (R10-SWEEP-TEMPLATE-SYNC), at head `14a73c15e5f060069f0fd4831eb46a436bd14f1d`, merge base `294a880dae608502b62055775e34a5db93217b98`. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/fix-review.md` is empty.

The re-cut answers round 1's architecture finding. `sweep_runner.sh`, `sweep_runner_selftest.py` and `roster_drain.py` are gone. Gantt and verdict audit are now `beat_jobs.py` rows with `beatd.jobs.json` entries. `PLAN MOVED` is in `plan-beat`. (4b+) is gone, and (4b) has one owner. `git grep "sweep_runner|roster_drain.py" -- tools .github tests` finds only one history comment, in `beat_jobs_selftest.py`.

The re-cut does not keep the rows in sync with the tracked template, though. `Ctx` reads its overlay from `S/sweep-overlay.json`, which its own docstring calls "the same JSON `sweep_render.py` fills the sweep from" (`beat_jobs.py:34`, `:172`). `sweep_render.render` refuses any overlay key that is not in the template's `## Placeholders` table: `unknown: ... not in the placeholder table`. The new rows read `gantt_roster`, `gantt_acks`, `fire_ledger`, `train_glob` and `unheld_skip`. `sweep_template.md` declares none of them. That leaves the orchestrator two outcomes:
- If the overlay leaves the keys out, every gantt pass writes `gantt: UNREADABLE overlay lacks gantt_roster, gantt_acks` (`Ctx.need`), and the verdict audit runs without its ledger, train glob or skip file.
- If the overlay adds the keys, the sweep render is refused.

The owner ruling is to update the tracked templates and scripts, and this updates the script half without the template half.

Harness: `ev/keys.py` lists every overlay key `beat_jobs.py` reads (`ctx.need` and `overlay.get`/`[...]`) and subtracts `sweep_render.declared(sweep_template.md)`. The render probe in `ev/overlay-keys.txt` renders the head's template with only the declared keys, then adds one new key at a time. Metric: the number of undeclared beat keys. It is 0 at the merge base and 5 at the head (`ev/overlay-keys.txt`). Perturbation: add `gantt_roster`, `gantt_acks` or `fire_ledger` to the overlay. The control render with declared keys only prints `OK`. Each single addition prints `REFUSED: unknown: <key> not in the placeholder table`. The harness moves under its own perturbation.

Repair, in this PR: declare the five keys in the `## Placeholders` table and use them in (4b)/(4c). `sweep_render` refuses a declared but unused name, so the sweep text has to cite them. Add a check, in `beat_jobs_selftest.py` or `sweep_render`'s self-test, that every overlay key `beat_jobs.py` reads is a declared placeholder, so this cannot recur unseen.

## Findings

- Defect: `beat_jobs.py` reads five overlay keys (`gantt_roster`, `gantt_acks`, `fire_ledger`, `train_glob`, `unheld_skip`) that `sweep_template.md` does not declare, while `sweep_render.py` refuses an overlay that holds them. The new rows therefore cannot be fed and the sweep rendered from one overlay. The claim, harness, metric (0 at the base, 5 at the head) and perturbation are under `## Block`. Carry: R10-SWEEP-TEMPLATE-SYNC
- Defect: four mutants on changed `gantt` lines survive `beat_jobs.py --self-test`, which prints 146 checks, 0 failed under each (`ev/mutants-mine.txt`, harness `ev/mut.py`):
  - M3 drops the `gh pr list` rc guard.
  - M4 drops `rc != 0` from the roster `git show` guard.
  - M11 drops the `handoff-wip/*` refspec from the fetch.
  - M12 replaces the copied fire ledger with `""`.
  No case drives a `gh` failure, a roster `git show` failure, a `handoff-wip` tip or a gantt ledger line. M3 and M4 are partly masked, because an empty file then fails `sweep_gantt` and that prints `UNREADABLE sweep_gantt`. M4 is not masked when the fetch fails but an earlier `refs/gantt/roster` exists: the stale roster is read silently. That failed fetch's rc is also unchecked. Repair: one case per guard and input, each with a null. Carry: R10-SWEEP-TEMPLATE-SYNC
- Defect: `## Red checks` misstates the red history. It says `61f1ec71` had "68 runs (`total_count` 68), all on one page. None concluded `failure`, `cancelled` or `timed_out`". That reading used the API default `filter=latest`. With `filter=all`, `61f1ec71` has 147 runs on 2 pages and 5 reds:
  - `gate` failure 128279140047, 128285014276 and 128290983518
  - `gate` cancelled 128288757875
  - `pr-contract / pr-contract` cancelled 128288387497

  At the head, `gate` failure 128312324401 is unnamed. Its log reads `FAIL run(s) [42340579795] at this head are still being judged; their gate decides`, the edit-run deferral R10-HOTFIX-GATE-BUSY-DEFER, and gate 128324519569 later concluded success. `arch-score / arch-score` cancelled 128324556485 and 128307712802 are also unnamed: both sit in edit run 42340579009, which was cancelled. Also unnamed are the `pr-contract` failure 128231570697 at `0ae78ac1`, which round 1's body named and this body dropped, and the 6 `gate`/`refresh`/`prelude` cancellations at `aa680f8b` (`ev/red-history-filter-all.txt`). The head's `pr-contract` 128321564289 started at 06:06:36Z, after the last red concluded at 05:22:16Z, and passed. So `defect-root-cause.md`'s trigger is answered by that run, and this is not the block. The brief requires the section to name every red that a later push cleared. Carry: R10-SWEEP-TEMPLATE-SYNC
- Defect: `review_packet.py render` refuses `red-unanswered: concluded red check arch-score / arch-score is not named in ## Red checks`. The body's "This head's own runs ... Any red there is the next round's to answer" does not answer it, because this head is the head under review. Carry: R10-SWEEP-TEMPLATE-SYNC

## Evidence

- RESULT: HEAD reviewed is `14a73c15e5f060069f0fd4831eb46a436bd14f1d` (ev/HEAD.txt). `git ls-remote` shows `fix/r10-sweep-template-sync` still at it when this verdict was written. The three-dot diff is ev/three-dot.diff: 13 files, +749/-20.
- RESULT: CI is `merge_train.py classify 14a73c15... --pr 3267`, which printed `GREEN 14a73c15e5f060069f0fd4831eb46a436bd14f1d pending: none red: none` (rc 0) at 06:23:16Z (ev/ci-log.txt).
- RESULT: `git merge-tree --write-tree origin/main HEAD` exits 0 (ev/merge-tree.txt).
- RESULT: self-tests at the head (ev/selftests.txt):
  - beat_jobs: 146 checks, 0 failed
  - sweep_gantt: 16 checks, 0 failed
  - verdict_audit: 14 checks, 0 failed
  - beatd: 119 checks, 0 failed
  - sweep_render: 34 checks, 0 failed
  At the base, beat_jobs prints 124 checks, 0 failed. The count rises by the new cases and mutants. The body names the instrument rather than a count, which is consistent.
- RESULT: `selftest_wiring.py --check` prints `118 self-testing, 118 wired, 0 unwired; 0 index gap(s)` at the base and `120 self-testing, 120 wired, 0 unwired; 0 index gap(s)` at the head. That fits the two added self-testing files, `sweep_gantt.py` and `verdict_audit.py`.
- RESULT: CodeQL alert 51 (item 1): the site file `sweep_runner_selftest.py` is deleted in this re-cut, so the 0o700 mutation proof has no site at this head. `codeql / Analyze (python)` 128309715588 and `CodeQL` 128310823880 both conclude success at the head. No added helper sets a file mode. I re-derived that by reading the diff: `atomic()` and `mkdir` use default modes.
- RESULT: my mutants on the changed lines (ev/mutants-mine.txt):
  - Killed by behaviour cases: M5 (wrong `--fired` flag), M5b (verdict-audit flags dropped), M10 (`gantt` removed from ROWS), M13 (gantt UNREADABLE line dropped), M14 (empty page hashed as a move) and M15 (CASCADE line dropped).
  - Killed only by the in-tree mutant's site-anchor check: M7 and M7b. Their lines are the sites of `roster_noop_marked` and `roster_cascade_marked`, which the self-test kills.
  - Survived: M3, M4, M11 and M12 (see `## Findings`).
  The body's ten in-tree `MUTANTS` are all killed inside the 146-check run.
- RESULT: VERSION, manifest, RELEASE_NOTES.md and every `*_budgets.json` are untouched in the three-dot diff. The new tracked `sweep_gantt.py` and `verdict_audit.py` are in `tests/closures.json`. `dev/programme/delivery/3267.md` is in the diff. The scope is the sweep instruments plus their governance step, and no production code is touched.
- RESULT: consumers checked (item 3). `beatd.jobs.json`'s new rows call `beat_jobs.py gantt|verdict-audit --state $S`, which matches `RUN`. The `--fired` flag the rows pass exists in both `sweep_gantt.py` and `verdict_audit.py`'s argparse. `sweep_template.md`'s (4b)/(4c) placeholders `plan_page`, `digest` and `plan_json` are declared. The overlay keys are not (Block).
- RESULT: `## Head` names `14a73c15` as the head, which is current. Body figures re-derived: the beat_jobs/gantt/verdict_audit/beatd/sweep_render self-tests print 0 failed, and selftest_wiring prints 0 unwired and 0 gaps. Two figures were not re-derived: entities, structure and the `MODE: SCOPED -- 2 script(s) run` line, which come from CI's green `tests / closure-scope` and the gate, as cited; and the fixer's failing-first count of nine cases failing at the base with stubs, because I did not rebuild their stubs.
- Finder's harness: the packet names none. For round 1's architecture finding I re-ran round 1's harness (runner steps duplicating a beat row): the runner does not exist at the head, so the count is 0 of 0, against 6 of 9 at round 1's head.
