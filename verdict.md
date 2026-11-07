Fix review: merge a7223767403bf172f99216e3082d4fc5fc793935

bus-nonce: 15fc2416afbed7946637a1a0c24b94a9

## Summary

Round 3 of #3267 (R10-SWEEP-TEMPLATE-SYNC), first review at head `a7223767403bf172f99216e3082d4fc5fc793935`, merge base `be813ecd4924865b75489f12c56600e9432d5727`. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the role file is current. Fourth round would owe a re-cut; this is the third.

The four defects that round 2 named (verdict/3267 `29529ba6`, blocked at `14a73c15`) are cured at this head:
- The block: the five overlay keys are declared. The finder's harness metric goes 0 → 5 → 0 (base, `14a73c15`, head).
- M3, M4, M11 and M12 are each killed by a behaviour case at this head.
- `## Red checks` is re-read with `filter=all`. It names every red of the earlier heads that round 2 listed.
- `review_packet.py render` reports `Refusals: none`.

What round 2 accepted is not reopened. The scope stays the tracked sweep instruments (`beat_jobs.py` rows, `sweep_template.md`, the self-tests and the governance step), so the owner ruling is met by updating the tracked template and scripts.

## Findings

- Follow-up: the five keys are required placeholders now (`gantt_roster`, `gantt_acks`, `fire_ledger`, `train_glob`, `unheld_skip`). So once this merges, an orchestrator sweep overlay that lacks any of them is refused `unfilled: the overlay omits ...` by `sweep_render.py`. My render probe shows this at the head: the declared-minus-one runs in `ev/render-probe.txt`. The overlay lives out of tree, on the orchestrator's machine, so whoever renders the sweep owes adding the five files to it at the merge. The body discloses the tradeoff, and it is the sound side of round 2's two outcomes: a loud refusal, never a silent `gantt: UNREADABLE`. Carry: R10-SWEEP-TEMPLATE-SYNC
- Defect (body, minor): `## Red checks` groups the head's gate failures as "edit-run deferral". Gate `128345268997` is not a deferral. Its log reads `FAIL tests / fast (3.14): cancelled (run 42352016707)` (`ev/gate-128345268997-fail.txt`): it is the supersession cancellation of `tests / fast` `128343442060`. The body names that cancellation and answers it as supersession, so the trigger is answered in substance. Gate `128378814076` (10:30:26Z) is a real deferral to run 42364179195, which concluded success. It ran after the body edit at 10:29Z, so no body could have named it by id. Carry: dismissed: the red's cause is named and answered in the same section, and a later `pr-contract` (128379228816, 10:32:45Z, success) checked the body after the last red concluded

## Evidence

- RESULT: The reviewed head is `a7223767403bf172f99216e3082d4fc5fc793935` (`ev/HEAD.txt`). `git ls-remote` shows `refs/heads/fix/r10-sweep-template-sync` at it when the verdict was written. The three-dot diff is `ev/three-dot.diff`: 13 files, +894/-20.
- RESULT: CI. `merge_train.py classify a7223767403bf172f99216e3082d4fc5fc793935 --pr 3267` printed `GREEN a7223767403bf172f99216e3082d4fc5fc793935 pending: none red: none` (rc 0) at 2026-11-07T10:40:10Z (`ev/ci-log.txt`).
- RESULT: Merge. `git merge-tree --write-tree origin/main a7223767403bf172f99216e3082d4fc5fc793935` exits 0 against origin/main `08fd676e`, with `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge-tree.txt`).
- RESULT: The finder's harness (round 2's `keys.py`, copied unchanged into `ev/keys.py`) counts the undeclared overlay keys `beat_jobs.py` reads:
  - at the base `be813ecd`: `[]`
  - at `14a73c15`: `['fire_ledger', 'gantt_acks', 'gantt_roster', 'train_glob', 'unheld_skip']`
  - at the head: `[]`

  So the metric goes 0 → 5 → 0 (`ev/keys-finder.txt`).
- RESULT: The render probe is reviewer-built, `ev/render_probe.py`, because round 2's probe was not committed. Output is in `ev/render-probe.txt`.
  - At `14a73c15`, adding the five keys is `REFUSED: unknown`.
  - At the head, the overlay with all declared keys plus the five renders `OK`, and omitting any one is `REFUSED: unfilled`.
  - The null control, `zz_undeclared_probe`, is `REFUSED: unknown` at both heads.
- RESULT: Round 2's mutants were re-run with round 2's `mut.py` (`ev/mut.py`, `ev/mutants-r2-at-head.txt`). All 12 are killed. The four former survivors:
  - M3 is killed by `gantt: a failed gh pr list is UNREADABLE ...`
  - M4 is killed by `gantt: a failed roster git show is UNREADABLE ...`
  - M11 is killed by `gantt: a handoff-wip tip is fetched ...`
  - M12 is killed by `gantt: the fire ledger is copied whole ...`

  Each is a behaviour case, not only a site-anchor check.
- RESULT: My mutants on every PR line the repair commit `e64e24a5` changes (`ev/mut2.py`, `ev/mutants-repair.txt`). All 8 are killed:
  - N1 (the fetch rc guard turned off) and N2 (the fetch UNREADABLE line dropped) are killed by `gantt: a failed fetch is UNREADABLE, never the stale refs/gantt/ roster`.
  - N3 and N4 delete a template row. Each is killed by the census and also by sweep_render's `the tracked template renders from a complete overlay`.
  - N5, N6 and N7 add an undeclared `.get` read, `need` read and for-loop key read. Each is killed by the census. For N6 the census FAIL was confirmed separately.
  - N8 drops the `{{train_glob}}` citation and is killed by sweep_render's `unused` refusal.
- RESULT: Failing first. With `14a73c15`'s `sweep_template.md` restored, `beat_jobs.py --self-test` prints `159 checks, 2 failed`: the census and its null (`ev/failing-first-and-class.txt`). This matches the body.
- RESULT: The class rule. `git grep 'sweep-overlay|sweep_overlay' -- tools .github tests` finds one reader, `beat_jobs.py:172` (`Ctx`), plus the self-test fixture and the docs. This matches the body's claim that `Ctx` is the one overlay reader. The census enumerates its reads, and N5, N6 and N7 show it moves for each read shape.
- RESULT: Self-tests (`ev/selftests.txt`).
  - At the base: beat_jobs 124 checks, sweep_render 34, beatd 119, all 0 failed. selftest_wiring prints `118 self-testing, 118 wired, 0 unwired` and 0 gaps.
  - At the head: beat_jobs 159, sweep_gantt 16, verdict_audit 14, sweep_render 34, beatd 119, all 0 failed. selftest_wiring prints `120 self-testing, 120 wired, 0 unwired` and 0 gaps.
  - The beat_jobs count rises by the new cases and `MUTANTS` (146 at `14a73c15` → 159). The body names the instrument, not a count. The sweep_render count is unchanged at 34.
- RESULT: CodeQL alert 51 (item 1). Its site, `sweep_runner_selftest.py`, is not in the tree at this head, as accepted in round 2, so no 0o700 mutation site exists. `codeql / Analyze (python)` 128378807847 and `CodeQL` 128342932571 conclude success at the head.
- RESULT: Protected files and classification. In the three-dot diff, VERSION, the manifest, RELEASE_NOTES.md, every `*_budgets.json` and both claim files are untouched. `sweep_gantt.py` and `verdict_audit.py` are in `tests/closures.json`. `dev/programme/delivery/3267.md` is in the diff.
- RESULT: The red history, read with `filter=all` over all pages (`ev/red-history-filter-all.txt`).
  - The head has 226 runs on 3 pages. `e64e24a5` and `c84911cc` have 0 runs, since neither was ever pushed as a head. `14a73c15` has 94 runs.
  - Reds at the head:
    - `instrument-self-tests` cancelled 128342095963 (supersession), and 128358602803 / 128378807832 (one job, suite 114747442245, with two check-run ids, at the 30-min timeout). The body names it as class A, R10-HOTFIX-SELFTEST-TIMEOUT.
    - The attempt-1 supersession cancellations, all named.
    - Gate failures 128344779516 (deferral), 128345268997 (cancelled `tests / fast`, see Findings) and 128378814076 (deferral, decided by edit run 42364179195, success).
  - Reds at `14a73c15`, `61f1ec71`, `0ae78ac1` and `aa680f8b` are named as round 2 listed them.
  - `pr-contract / pr-contract` 128379228816 started 10:32:45Z, after the last red concluded at 10:30:56Z, and succeeded. So the defect-root-cause trigger is answered.
- RESULT: The timeout is not this PR's step. In job 128358602803, the added step `Show the beat's Gantt and verdict-audit instruments` started and completed within 09:23:32Z. The job was in `ci_predict`'s step when it was cancelled at 09:25:04Z (`ev/selftests-job-steps.txt`). The same job took 24.5 min at `14a73c15` (128309715613, success).
- RESULT: `## Head` names `a7223767` as the head, which is current. The paragraph about `e64e24a5` describes the repair commit, which this merge contains.
- Figures not re-derived:
  - `entities.py`, `structure.py` and the `MODE: SCOPED -- 2 script(s) run` line. These are cited from CI's green `tests / closure-scope` 128378808039, `tests / closures` and gate 128379738365, per "cite CI's heavy runs".
  - The body's sha1s of the finder's files. The copy here is round 2's `keys.py` read from `origin/verdict/3267` (`29529ba6`), not `probe/rev-3267-0b9792ab`.
