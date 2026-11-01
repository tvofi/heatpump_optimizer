Fix review: blocked 67cc0e0a15100eef34848203fdb2bc5c370a830e root-cause-unrecorded: code-scanning alert 47 (py/clear-text-logging-sensitive-data) still fires at tools/replay/export.py:459 at this head, is not dismissed, and pr-contract refuses the live body for not naming it, so the required gate is red

bus-nonce: 419e55bb48829bb682b9858a1204dbd6

## Round

Round 4, reviewed at live head 67cc0e0a15100eef34848203fdb2bc5c370a830e. The code head is e46ff0a75 and the merge base with origin/main is 407eb0cb3. The contract is dev/governance/roles/fix-review.md at origin/main, and dev/governance/roles/ and dev/governance/rules/ show no drift between the merge base and origin/main. I measured from detached worktrees at the head and at 18bdd5c88 (round 3's head). The finder's harness is round 3's: `tests/replay.py --one tests/replay/owner-2026-10-30-away.json --step-minutes 60` with HASTUB_TZ=Europe/Stockholm OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub, summarised by round 3's summ_finder.py (ev/summ_finder.py, ev/run_one.sh). The round-3 block (mutation-vacuous) is answered. The block below is new: it comes from this head's own CI. This is the fourth round, so fixer.md owes a re-cut, not a repair. The body calls itself a re-cut.

## Block

1. **CodeQL alert 47 is neither gone nor dismissed, and the body no longer names it (step 11; brief item 2).**
   - The `CodeQL` check run 124943331889 at this head concluded failure: "1 new alert including 1 high severity security vulnerability". Its only annotation is at tools/replay/export.py:459, "Clear-text logging of sensitive information" on `print(f"reading the recorder {rec.label}", ...)` (ev/codeql_annotations.json).
   - So e46ff0a75 did not clear the alert. The body's "Alert 47, real in part, repaired in code" is stronger than the check supports.
   - On reading, the remaining flow is path-insensitive. In `open_recorder`, `db` is assigned from the URL in the `if url:` branch, and the f-string `f"SQLite {db}"` still sits in `label or f"SQLite {db}"`. CodeQL does not prove `label` truthy on that path. At runtime the URL-derived path is never printed, and `recorder:sqlite_db_url_named_by_kind_not_path` shows that.
   - The PR body was edited at 19:04:03Z. The live `## Red checks` has the sub-bullet "Alert 47, real in part ..." and no longer carries the literal check name `code-scanning alert 47 (py/clear-text-logging-sensitive-data)`. It also still says "This head has not run CI".
   - Every pr-contract run at this head after the last red concluded refuses the body with exactly that error: runs 124953435208, 124955617340 and 124956390233. The last started 19:39:54Z, after CodeQL concluded at 18:48:45Z and after every other workflow had concluded (ev/pr_contract_124956390233.log). The message is: "check `code-scanning alert 47 (py/clear-text-logging-sensitive-data)` is red and `## Red checks` does not name it".
   - `gate` is red on that refusal (runs 124954513944, 124956009449, 124956590647). `merge_train.py classify` exited 1: `RED ... pending: none red: gate`.
   - The cheapest detector of a CodeQL alert is CodeQL itself, so the class is root-cause-unrecorded.
   - Cheapest repair, either of two:
     - (a) Build the SQLite Recorder with no format string reachable from the URL. For example, return `Recorder(..., SQLITE_URL_LABEL, ...)` inside the `if url:` branch and keep `f"SQLite {db}"` only on the `--db`/default path. Then show CodeQL green at the new head.
     - (b) Keep the code and have the owner dismiss alert 47 as a false positive.
   - Either way, restore the literal check name in `## Red checks` with an honest account: the e46ff0a75 change did not clear the alert at 67cc0e0a1. Also drop "This head has not run CI".

## Findings

- CodeQL alert 47 is still reported at tools/replay/export.py:459 at this head, is not dismissed, and is unanswered by name in the live body, so pr-contract and gate are red (Block 1). Carry: R10-REPLAY-REAL-DAY
- The new away-coverage guard depends on a literal file name, and nothing checks that the name exists. `AWAY_COVERED = frozenset({"owner-2026-10-30-away.json"})` is never checked against the committed fixtures, and the `controls()` pairs take `next(iter(AWAY_COVERED))` without asking that the name exists.
  - With that one literal misspelt, the FAST tier stays green (ev/my_mutants.txt).
  - With the misspelling and the fixture's `controls.away` emptied, the FAST tier also stays green (ev/my_double_fast.txt).
  - With the misspelling and `recorded_away = []` in run_fixture, the finder's replay reads `away` 0 with 0 commanded cycles (ev/one60_head_typo_empty.summary). That is the round-3 vacuity again.
  - A rename of the fixture file itself is loud, because the COST_BUDGETS key goes missing ("no recorded budget"). The silent route is a typo or rename in `AWAY_COVERED` alone.
  - Cheap pin: a sanitiser check that `AWAY_COVERED` is a subset of the committed fixture names, paired with its control. Since the re-cut is owed anyway, it belongs in it.
  - Carry: R10-REPLAY-REAL-DAY
- The unsupported-scheme refusal in `open_recorder` changed in 2042aefb7: "the recorder URL is neither SQLite nor MySQL/MariaDB" no longer prints `redacted(url)`. No check pins that it prints no URL text. The mutant `raise SystemExit(f"the recorder {url} is neither SQLite nor "` survives every FAST check (ev/my_mutants.txt). For a `postgresql://user:pass@host/db` recorder that would put the credential on stderr. The line is in the diff and is the same class as alert 47 (db_url text in a message), but neither the body nor the harness dispositions it. Cheap pin: a recorder_checks entry passing a credentialed non-MySQL URL and asserting neither the user nor the password is in the SystemExit text. Carry: R10-REPLAY-REAL-DAY
- R10-REPLAY-COST-BUDGET's only carry at roster tip 341a2cc3a still quotes the round-1 "Not recorded locally ..." text. The body's `## Forward-carry` asks the orchestrator to restate it as "re-centre the recorded 355.7 / 3740.0 / 0.249 on the second CI class's reading", with its control. That restatement is still owed before dispatch (unchanged from round 3). Carry: R10-REPLAY-COST-BUDGET
- The widened `not_frozen` rule has a blind spot: an input idling at zero that meets one non-zero value and then freezes is not judged. The comment and body disclose it, and `control:not_frozen` still fires on the two-value case. This is unchanged since round 3. Carry: dismissed: disclosed design trade with its control; no defect at this head

## Evidence

- RESULT round-3 block re-derived with the finder's harness at both ends. The mutant is `recorded_away = list(...)` -> `recorded_away = []` in run_fixture.
  - At 18bdd5c88: `away` 0, commanded 0, every other invariant count 0. The mutant SURVIVED (ev/one60_old_mutempty.summary).
  - At this head: `away` 2, "the fixture declares away coverage but the replay carried no commanded cycle" and "owner-2026-10-30-away.json declares away coverage but records no active command". The mutant was KILLED (ev/one60_head_mutempty.summary).
  - In that run `cycle_cost` 1 (loop_cpu_ratio 0.1182, below the band's floor) is timing noise from four concurrent replays on 4 cores, not the mutant.
- RESULT round-2 mutant `commanded = None` at this head: `away` 4 offenders (the coverage line plus 3 cycles at 60-minute steps), commanded 0. KILLED (ev/one60_head_mutnone.summary).
- RESULT null at this head: 4 cycles, every invariant count 0, 3 commanded cycles, views [(True, True, False, 15.0, 15.0)] (ev/one60_head_null.summary).
- The fixer's in-tree harness, FAST tier, run by me at the head: `RESULT killed=33 mutants=33 null_red=0` (ev/fixer_harness_fast.txt), matching the body. Its REPLAY rows were not re-run as a set. My own REPLAY runs above cover the two away rows.
- My own FAST mutants at the head (ev/my_mutants.txt): null green.
  - `expect_commanded` inverted: KILLED (control:away:coverage_needs_a_commanded_cycle).
  - SQLite label falling back to the path: KILLED (recorder:sqlite_db_url_named_by_kind_not_path).
  - `AWAY_COVERED` typo: SURVIVED (see Findings).
  - Non-MySQL refusal printing the URL: SURVIVED (see Findings).
  - Coverage accepting an inactive-only event list: SURVIVED. At the REPLAY tier that case is still caught by `expect_commanded` (no commanded cycle), so it is defence in depth, not a gap.
  - The sanitiser coverage line forced green: SURVIVED alone, as a check-off mutant with nothing to catch. The harness's fixture-twin row is what pins it, and that row is KILLED (ev/my_double_fast.txt, first line).
- Delta (brief item 1): the merges 8d222b4ff, 67cc0e0a1 and a8f48032e each re-merge to exactly their recorded tree (ev/merges_clean.txt). The tree of merge(18bdd5c88, origin/main) differs from the head only in tools/replay/export.py, tests/replay.py and dev/audit/harnesses/r10_replay_real_day_mutants.py (ev/delta_vs_old_plus_main.txt). Those changes are the fixer's three commits 2042aefb7, 0030d8c04 and e46ff0a75. 80c6fa40a..e46ff0a75 is e46ff0a75 alone, which touches export.py, one check plus the `shutil` import in tests/replay.py, and one harness row, as `## Head` says. That delta reaches only the recorder label and recorder_checks, nothing `run_fixture` reads, so the round-3 replay figures taken at 80c6fa40a cannot move.
- Head (brief item 3): `## Head` names 67cc0e0a15100eef34848203fdb2bc5c370a830e and the code head e46ff0a75, and says the round-3 figures were taken at 80c6fa40a. Its merge-tree sentence cites origin/main d052f80f7 while the head merges 407eb0cb3. The head was 67cc0e0a1 at render time and still was when this verdict was written (refs/pull/3078/head).
- Carries (brief item 4): the body cites origin/handoff/audit-r10-roster with no SHA, so I read the tip 341a2cc3a (ev/roster_carries.txt).
  - R10-LIVE-BUNDLE-READS is not-started, `after: R10-REPLAY-REAL-DAY`, and holds the live-bundle reads, including the verbatim "R10-REPLAY-REAL-DAY carry 4" item.
  - R10-REPLAY-COST-BUDGET is not-started, `after: R10-REPLAY-REAL-DAY`.
  - The mold-guard carry is item 5 of R10-USER-DOCS-VERIFY.
  - carry_audit at the head: 5 routed, 0 unrouted, 0 bad destinations.
- Privacy (brief item 5), reported by location only:
  - The fixture is byte-identical between 18bdd5c88 and this head.
  - The 90 lines added beyond main were grepped for street words, postal shapes, UUIDs, credentialed URLs, IPs, coordinate-shaped numbers and raw `e_<hex>`, person, device_tracker and zone ids. The hits are the owner fixture's two away-event timestamps in the harness row (data already in the committed fixture, no location) and the invented canary credential in tests/replay.py, renamed only.
  - RESULT privacy: nothing found.
- Disclosure: the docstring of `away_offenders` now claims only what the check delivers (events non-empty, or `expect_commanded`). "Regression guard" stays the title's claim, and round 2 already showed that pre-fix passes too.
- Gate:
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (ev/structure.txt).
  - Both claim files are byte-identical to origin/main (ev/claims.txt).
  - VERSION, the manifest and RELEASE_NOTES.md are untouched.
  - The three-dot diff from the merge base holds only dev/programme/delivery/3078.md among those paths, so the delivery row is present.
  - CI tests / fast (3.14) prints `MODE: SCOPED -- 14 script(s) run, 19 scoped out.` (ev/gate_mode.txt).
- Merge: `git merge-tree --write-tree origin/main 67cc0e0a1` exits 0 (tree 436556a0f) with origin/main at 407eb0cb3, so there is no conflict (ev/merge_tree.txt).
- CI at this head (ev/ci_checks.txt, ev/ci_classify.txt, all pages):
  - `tests / replay`: success, "ALL 173 replay checks PASSED", lane wall time 912.3 s, owner fixture `cpu_ratio=302.6 peak_kib=3744 loop_cpu_ratio=0.2104` (ev/ci_replay.txt).
  - `tests / mutation`: success, "MUTATION TABLE PASSED", scope changed over 1 production file (ev/ci_mutation.txt).
  - `tests / fast (3.14)`, coverage and closures: success.
  - `CodeQL`: failure. pr-contract: failure, 3 runs. gate: failure, 3 runs.
  - classify: rc 1, RED (red: gate).
- I could not read code-scanning alerts directly: the alert API returns 403 to this seat. The alert's state rests on the CodeQL check run's annotation and on pr-contract's red list, which names alert 47.
- Not re-derived: the body's 15-minute REPLAY counts (`away` 2 / 13, `no_default` 14). I re-took the away rows at 60-minute steps, as above. The warm-up claim, the export-side masking figures and the pump-draw comparison need the owner's untracked export, as in every earlier round.
