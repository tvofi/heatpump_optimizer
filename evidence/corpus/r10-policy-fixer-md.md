R10-POLICY-FIXER-MD: disposes every line of #2378, the recurring `fixer.md` friction of round 10, and this group's roster carries 0 to 12. Closes #2378. Part of #201.

**This is policy. tvofi approves at merge under mandate 6175172275.** It edits `dev/governance/roles/fixer.md`, `dev/governance/roles/fix-review.md` and `dev/governance/rules/finding-propagation.md`, with the generated `.claude/rules` and `.cursor/rules` copies. No cap moves. Each file sat at zero or near-zero headroom, so every added line is paid by cutting motivation text in the same file (`fixer.md` step 9: "Delete on sight ... motivation"). `policy_budgets.json` is untouched.

Disposition per line of #2378. Each one is either a wording fix, a code countermeasure, or a refusal with the count:

1. **#2305, step 2 "pinned by `mutation-autofix`".** Wording fix. The lane mutates `custom_components/` only (`tests/mutation_table.py`'s `PKG`), so a `tools/` site needs an in-tree mutant harness. Step 2 also names where "a written triage" goes: `tests/mutation_ledger/survivor_triage/`, because the ratchet reads no body text (#2563's carry). It tells the seat to run the ledger's own mutant before claiming a kill (#2445's carry).
2. **#2316.** Wording fix in both files.
   - `fix-review.md` step 6: `<seam>` is "a site or a predicate's unguarded domain".
   - `fixer.md` step 6: `handoff_push.sh` is named as the orchestrator's instrument. It opens the PR and writes the row. The seat pushes `handoff/<topic>` and `body_push.sh` only.
   - The roster's "Identity and flow" boilerplate still says otherwise in 64 briefs. It is carried, not edited here, because the roster takes `roster_edit.py` ops only (`standing-roster.md`). The carry landed at R10-ORCH-ROSTER-SCHEMA carry[7] (`## Forward-carry`).
3. **#2344.** Wording fix in step 18. A one-off probe, or a reviewer's driver, stays in scratch or verdict evidence. Step 18 binds what a later seat reruns. The reviewer's answer stands.
4. **#2374.** Wording fix in step 18. A new harness is a predicted closures red, because `tests/harness_headers.py` reads the directory. `tools/pr/ci_predict.py --apply-inert` (#2376) repairs it before the handoff.
5. **#2345.** Wording fix with no added line: `#2345` joins `#1874` in step 17's spelling-list citation.
6. **#2365.** Wording fix in step 3. A fold that deletes a name the harness drives leaves only the count arm readable at the head. The fixer ports the rest, as its own instrument (`fix-review.md` step 9 disclosure).
7. **#2366.** Refused, no change. Step 8 already requires a rule that enumerates the class's seams. "Every field a clone publishes" is that rule for one seam family, the publish guard. It belongs in that instrument, not in a contract every fixer reads. Count: 1 instance (#2366) among the issue's 11 lines.
8. **#2368.** Wording fix in step 6. A delta re-applied to a branch cut from an older base is diffed line by line against its sibling's head.
9. **#2373.** Wording fix in `fix-review.md` step 14. The plant also runs on the counter's neighbouring rules, not only on the counter's own rule re-spelled.
10. **#2347.** Note only. The fix is out of this policy group's reach: it is a `tests/structure.py` counting-rule change. The budget section now says `max_class_loc` is a span, so a docstring line costs what a code line does. `tests/structure.py`'s own docstring documents it as "the largest class span".
11. **#2331's RCA, section 8: make step 8 unconditional.** Refused again, re-measured at this merge base (`## Figures`).
    - 27 `class-open` blocks fell on 18 of the 214 PRs with a `verdict/<pr>` ref, with a median of 119 min to the next verdict over the 25 that have one (`## Figures`; corrected from 98 at fix review round 1).
    - Step 8 already binds every block demonstrated with an instance, and that is the shape #2378's issues have.
    - Prevention is still not shown. #2283, which named a census, took 3 of the 27 blocks.
    - An unconditional step 8 adds only a rule to a fix whose finding was never an instance. This seat did not classify the 18 PRs' findings (no bodies read), so it does not claim how many of them that is.

Carries routed to this group (roster `carry`):
- **#2368, the label-triggered workflow.** Already fixed in code. `kernel-points` is the one `labeled` consumer in `ci.yml`, and `.github/workflows/kernel-points.yml`'s push arm gives an early label its run. No text added.
- **#2447, commit before prepr.** Step 5 says prepr runs on a committed tree, because step 6f reads `HEAD`.
- **#2447 and #2631, the `handoff_push.sh` contradiction.** Item 2 above.
- **#2445, a kill claimed without its mutant.** Item 1 above.
- **#2452, `BASH_ENV`.** Not `fixer.md`'s: the seat setup line is the cloud payload's and `tools/audit/seat/cloud-setup.sh`'s, owned by R10-FLY-CLOUD-SETUP-TOOLCHAIN. See `## Forward-carry`.
- **#2567, carry_audit.** Step 5 names `tools/audit/carry_audit.py check --body` beside prepr. `git grep carry_audit tools/pr/prepr.sh` returns nothing (rc=1), so prepr does not run it.
- **Lean K5.**
  - Step 6 now absorbs `origin/main` only when `git merge-tree --write-tree` reports a conflict or the head is `DIRTY`, as `nudge.md` step 9 already says.
  - `fix-review.md` step 11 treats a green `pr-contract` run started after the head's last red as the evidence, and never re-derives it. Step 1's mutation proof stays the reviewer's.
  - Steward S2 is unchanged because it already agrees: a `DIRTY` PR is merged with origin/main. Nudge step 9 is the source of the rule.
- **#2561.** Items 1 and 11 above.
- **#2563, where "a written triage" goes.** Item 1 above.
- **Carry 10, tvofi 2026-10-24 card 3** (roster `313643643aa6`). Applied. `fixer.md`'s preamble: a seat waits on CI through one `seat/ci-watch.sh` or `seat/proof_watch.py` (the 60 s API floor is theirs), woken once by its exit, never sleeping and polling; past the handoff a fixer does not wait. `fix-review.md`'s preamble points a reviewer's wait at the same sentence. This is the seat-side rule R10-ORCH-BEATD's after-edge (its carry 13) rests on.
- **Carry 11, tvofi 2026-10-24 card 2, amended twice** (roster `3454d6cc34dc`). Applied, one sentence per file. `fixer.md`: rotate to a fresh context between stages (rca, fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M) or ~300 k (L, XL). `fix-review.md`: between rounds, never mid-review, by ~150 k. The orchestrator's ~500 k cap stays `orchestrator.md`'s, as the card says.
- **Carry 12, #2709's `set -e` mutant** (roster `8ecacecb1`). Applied in step 2: `exit $?` to `exit 0` under `set -e` is equivalent, so write `|| true; exit 0`.
- **O11, the ledger marker.** `finding-propagation.md`'s Enforcement section now says a finding in the orchestrator's out-of-tree ledger carries the same `Carry:` marker. The proposed sentence is condensed, and it is paid by cutting two motivation clauses in the same file.

## Head

`e1af669109c862b1f7dbc7a8112b8c167123c973`: one commit on PR head `859b74ba8ab4d0020025895b73a53b3833b5e74c`, merge base `ac5788f2617755631f14e4d1a31efab0e47aa820`, origin/main `343fb2a2c23dbb1a78142ce869be495187b8d481` (2026-10-24T19:02Z, `date -u`). `git merge-tree --write-tree origin/main HEAD` exits 0, so origin/main was not merged (step 6). Round-3 figures (mutants A and B, budgets, gate, prepr) were taken at this head; item 11 and mutants 1 to 3 stand from rounds 1 and 2, because this commit touches only `fixer.md` and `fix-review.md` prose that none of them reads.

Round 3, after fix review round 2 (blocked `carry-undisposed` at `859b74ba8`): carries 10 and 11 were appended to the roster at 09:32Z, two minutes before round 1's handoff, and no earlier body read them. This head applies both, and carry 12 (appended 16:48Z), paid by cuts:
- `fixer.md` step 2: the `.claude/hooks/pre-edit.sh` instance of a vacuous tail mutant (its rule stays).
- `fixer.md` step 10: the "because a generator is rarely the only copy" clause (the grep it motivates stays).
- `fixer.md` step 15: #948's narrative, condensed to its figures; the production-width condition, the per-row scalar rule and the CPython 3.12+ `sum` rule stay.
- `fix-review.md`: the `preflight.sh` aside in the preamble and #1144's narrative in step 11 (the citation stays).

Round 2's findings: the `BASH_ENV` carry's destination R10-FLY-CLOUD-SETUP-TOOLCHAIN is in progress, so relaying carry[6] to its running seat is the orchestrator's (`finding-propagation.md`); this seat writes no other branch (`## Forward-carry`). Step 18's "reviewer's driver" was dismissed by the reviewer; no change.

## Mutation proof

Each mutant was run in a detached worktree of the head and restored with `git checkout -- .`.

Round 3, the payments for carries 10 to 12 are needed:
- A. `fixer.md` at `859b74ba8` (every round-3 cut and the step-2 rewrite reverted) plus only the four new preamble lines. `node tools/policy/policy_lint.mjs` reads `TOTAL: 2 error(s)`: `318 lines exceeds its cap of 315` and `about 5293 tokens ... exceeds its cap of 5216`; `--budgets` prints `fixer.md 318 315 5293 5216`.
- B. `fix-review.md` at `859b74ba8` plus only the new preamble sentence. `TOTAL: 1 error(s)`: `about 2482 tokens ... exceeds its cap of 2451`; `--budgets` prints `fix-review.md 140 140 2482 2451`.

Rounds 1 and 2:

1. **The generated copies are pinned.** Mutant: main's `dev/governance/rules/finding-propagation.md` source over the branch's, with the generated copies left as the branch has them. `node tools/policy/rules_sync.mjs --check` reads `RULES-SYNC: 2 file(s) out of date`, rc=1. At the head it reads rc=0.
2. **The payments are needed.**
   - Mutant: `fixer.md` step 9's cut `#386` sentence restored. `node tools/policy/policy_lint.mjs` reads `TOTAL: 1 error(s)`, and `--budgets` prints `fixer.md 315 315 5249 5216`.
   - Mutant: `finding-propagation.md`'s cut "adjective" clause restored, and regenerated. The reading depends on the mutant's shape, and both shapes were re-run at round 2:
     - Main's own two lines restored (`No "importance" threshold gates this, the adjective ... argues its way out of: if it changes what a later stage must do, it is carried.`). `policy_lint.mjs` reads `TOTAL: 1 error(s)`: `about 1348 tokens ... exceeds its cap of 1336`, at `101 101 1348 1336`. This is the reviewer's mutant.
     - The clause inserted ahead of the branch's wrap, making 3 lines. `TOTAL: 2 error(s)`: `102 lines exceeds its cap of 101` and the same token error, at `102 101 1348 1336`. This is the round-1 body's mutant, which it did not state.
     - Either shape is killed by the token cap alone.
3. **Step 6's example keeps the spelling #2561's detector pins.** Mutant: `fix-review.md` step 6's example re-spelled `blocked <sha> harness: class-open <seam>`. `node tools/policy/check-wave-script.mjs` reads `209 passed, 1 failed`: `FAIL fix-review.md teaches "class-open" as a reason under another class`.

No new check arm. No checker reads the new sentences, and none of them can be pinned in one line, because none is an example the wave grammar parses. The one sentence the grammar does read is step 6's example. Its placeholder gloss sits outside the backticks, and the existing arms pin it (item 3).

## Null control

- At the merge base `50af6174f`: `node tools/policy/policy_lint.mjs` reads `TOTAL: 0 error(s)`, `check-wave-script.mjs` reads `209 passed, 0 failed`, and `--budgets` prints `fixer.md 312/315 5169/5216`, `fix-review.md 139/140 2420/2451` and `finding-propagation.md 100/101 1335/1336`.
- The roster-boilerplate count has a null: the same scan for `the seat pushes refs only, through tools/pr/push.sh` returns 0 groups.
- `rounds.py`'s key has a null: `verdict/2675`, whose two blocks are `carry-missing`, contributes no `class-open` row.
- `git grep -n carry_audit tools/pr/prepr.sh` exits 1 with no output. The same `git grep -n ci_predict tools/pr/prepr.sh` finds its step 6d lines, so the search can find a call that is there.
- `python3 tools/audit/archscore/score.py --diff origin/main` prints `Architecture score: dS +0.0000 NULL`. No production line changed.

## Figures

- Budgets at the head: `node tools/policy/policy_lint.mjs --budgets` prints `fixer.md 314/315 5214/5216`, `fix-review.md 140/140 2448/2451` and `finding-propagation.md 101/101 1332/1336`; role fixer `~6283` against `6352`. At `859b74ba8` it printed `fixer.md 314/315 5215/5216`, `fix-review.md 140/140 2445/2451`. `policy_lint.mjs` reads `TOTAL: 0 error(s) across 50 policy file(s)`.
- Carries 10 and 11 present: `git grep -nE 'poll|150 k|ci-watch' HEAD -- dev/governance/roles/fixer.md dev/governance/roles/fix-review.md` returns `fixer.md` lines 7 to 10 and `fix-review.md` line 8. The null: the same grep at `859b74ba8` exits 1 with no output.
- Item 11, re-measured with `dev/audit/rca/harness-friction/rounds.py`.
  - Input: one TSV per `refs/heads/verdict/<pr>` (214 refs, fetched 2026-10-24). Each TSV holds the ref's commit times (UTC) and the `Fix review:` line of each commit subject, de-duplicated by line, keeping the earliest commit of a re-pushed line.
  - The verdict refs stand in for the PR comments that rounds.py's docstring names, because `gh` is unauthenticated in this seat. Rule: a commit's subject is the verdict `bus.sh` signed, and a re-push of the same line is one verdict.
  - Result: `SUM class-open 27 entries 6640 min`, on 18 PRs. #2283 has 3 of the 27. `harness:class-rule-missing` has 2.
  - Median, corrected at fix review round 1: 119 min over the 25 entries that have a next verdict. The round-1 body said 98, which counted the 2 entries with no next verdict (#2346, #2658) as 0 min.
  - Re-derived at round 2 against 227 refs, dropping #2706 and #2707 (refs pushed after the 214-ref fetch), with this command for each `verdict/<pr>`: `TZ=UTC git log --format='%cd%x09%s' --date=format-local:%Y-%m-%dT%H:%M:%SZ origin/verdict/<pr> | sed -E 's/\tverdict: #[0-9]+ /\t/' | grep -P '\tFix review:' | tac | sort -s -t$'\t' -k2,2 -u`. Then `python3 dev/audit/rca/harness-friction/rounds.py <dir>`. Result: 27 entries on 18 PRs, sum 6640, median 119 over 25 timed.
  - The sum depends on which commit of a re-pushed line is kept. Two PRs re-pushed a line: #2452's blocked line, at 14:54:58Z and 23:20:09Z, and #2571's next verdict. Keeping the latest commit (`sort -t$'\t' -k2,2 -u` with no `tac`) gives the reviewer's `6297 min` and a median of 126, and reproduces `review/2704`'s `evidence/item11-tsv/` row for row. The timestamp source does not matter: `%ad` and `%cd` give identical results on all 227 refs.
  - This body keeps the earliest commit. A verdict is in force from its first signature, and a re-push does not restart the wait. No reading changes 27, 18 or #2283 = 3, and the disposition rests on those counts.
- Roster boilerplate: a `python3` scan of `dev/programme/rosters/wave-r10-groups.json`'s `brief` strings for `the seat pushes refs only, through tools/audit/seat/handoff_push.sh`, in plain or backticked form. It finds 64 groups, 18 of them at a stage other than `done` or `absorbed`.
- The mutation lane's scope: `tests/mutation_table.py:104` `PKG = "custom_components/heatpump_optimizer/"`.
- Gate, at this head:
  - `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, naming `tests/entities.py`.
  - `env -u BASH_ENV python3 tests/entities.py` reads `ALL 2425 ENTITY CHECKS PASSED`. It ran with `BASH_ENV` unset for #2452's class (`## Friction`); round 2 showed the same 2 checks failing with it set at both ends.
  - `run_always`: `tests/env_drift.py --claims-only origin/main` reads `claims hygiene: origin/main ok`. `tests/closure.py selftest` reads `ALL 117 closure shrink pins PASSED`. `tests/layout.py` exits rc=0, and `tests/harness_headers.py` reads `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `python3 tests/structure.py` reads `STRUCTURE RATCHET PASSED`.
  - `node tools/policy/rules_sync.mjs --check` reads `RULES-SYNC ok`, and `node tools/policy/check-wave-script.mjs` reads `209 passed, 0 failed`.
  - `python3 -I tools/audit/seat/tmp_paths.py --check` reads `0 refused`.
  - `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` reads `no closures or fast red predicted against ac5788f26177`.
  - `python3 tools/audit/archscore/score.py --diff origin/main` prints `Architecture score: dS +0.0000 NULL`.
  - `env -u BASH_ENV bash tools/pr/prepr.sh <body> 2378` prints `PRE-PR: e1af669109c862b1f7dbc7a8112b8c167123c973 00000000000000000000000`, rc=0. It ran with `BASH_ENV` unset for the reason under `## Friction`. `python3 tools/audit/carry_audit.py check --body <body>` reads `4 routed, 0 unrouted, 0 bad destination(s)`.

## Red checks

none owed at `859b74ba8`: its two red `gate` jobs (120903782777, 120903766312) each log that run 40104542321 at that head decides, and that run's `gate` and `pr-contract` are green (fix review round 2, step 11). No CI has run at this head yet; `tools/pr/ci_predict.py` predicts no closures or fast red against `ac5788f26177`.

## Forward-carry

- **The roster's "Identity and flow" boilerplate.** 64 group briefs in `dev/programme/rosters/wave-r10-groups.json` (18 not done or absorbed) say the seat pushes "through `tools/audit/seat/handoff_push.sh`". That script opens or updates the PR through `app_push.sh`. `fixer.md` step 6, the newer copy, now says the script is the orchestrator's. The control is `python3 -c` over the roster's `brief` strings, counting `the seat pushes refs only, through tools/audit/seat/handoff_push.sh`, plain or backticked: 64 at this head, and 0 among live groups is the repaired state. A `roster_edit.py edit-brief` op per live group is owed. Landed in `dev/programme/rosters/wave-r10-groups.json`, stage R10-ORCH-ROSTER-SCHEMA carry[7], at `handoff/audit-r10-roster` `928ca213e7158b7b0747675c63097ca1ec6b54fd`. The text was read back with `git show 928ca213e715:dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-ROSTER-SCHEMA
- **`BASH_ENV` in the cloud seat's profile (#2452).** The toolchain profile `tools/audit/seat/cloud-setup.sh` installs (its `PROFILE`) exports `BASH_ENV` pointing at itself, so every `bash -c` puts the venv python back ahead of a test stub's PATH. Under `env -u BASH_ENV` all 2346 entity checks passed in #2452. The precondition is that the cloud setup's profile note or payload must not leave `BASH_ENV` set for a test that shadows PATH. Re-measure it with `tests/entities.py`'s graders-head-copy check under and without `BASH_ENV`. Landed in `dev/programme/rosters/wave-r10-groups.json`, stage R10-FLY-CLOUD-SETUP-TOOLCHAIN carry[6], at `handoff/audit-r10-roster` `928ca213e7158b7b0747675c63097ca1ec6b54fd`. That carry names `BASH_ENV`, the precondition and the re-measure, read back the same way. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN
  - Round 2 finding: that group is now `resume.stage: in-progress` (roster tip `8441dd7e6`), so its seat reads the out-of-tree brief it was handed. The relay of carry[6] to the running seat is the orchestrator's, by `finding-propagation.md`'s running-stage rule; this seat writes no branch but its return refs.

## Friction

- `fixer-env: cost`: `tests/entities.py` reads 2 of 2425 failed in this cloud seat at both the head and the merge base. The same two checks fail at both ends, and the diff touches neither. Under `env -u BASH_ENV` all 2425 pass, so both are #2452's `BASH_ENV` class (carried above), and it reaches `gate-sweep.yml`'s check as well as `graders-head-copy`'s. This seat ran under the toolchain profile, as the dispatch says. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN
- `fixer-instrument: cost`: `rounds.py` reads PR comments fetched with `gh`, which is unauthenticated in a cloud seat. The verdict refs' commit subjects reproduced its input with no GitHub call, and its docstring does not name that source. Carry: dismissed: one seat's substitution, stated under Figures with its rule; the RCA's record is closed and rounds.py is evidence, not an instrument a later stage runs

## Approval

Awaiting tvofi's approving review at the head, under mandate 6175172275. This diff edits policy: `fixer.md`, `fix-review.md` and `finding-propagation.md` with its generated copies. No owner approval has been given for this diff yet, and none is claimed.
