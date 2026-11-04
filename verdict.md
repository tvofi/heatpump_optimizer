Fix review: blocked 344feb6c1f273db37c90105407bf2f26fc0b6adb defect: seven of my own row mutants survive the self-test, including half of gap 2's transient rule (NOT REVIEWABLE) and the hold release's op handed to roster_queue

bus-nonce: 774a490e497e401272565849ea370fd6

## Block

This is round 2 of the fix review of #3197 (R10-FLY-STANDING-CONTRACTS P1), after verdict/3197 at fe2077441519. I measured head 344feb6c1f273db37c90105407bf2f26fc0b6adb.

Round 1's three blocking items are fixed at the head:
- The partial-line probe runs only the whole op.
- A truncate and re-queue gives `roster: QUEUE-SHRANK` and one run.
- All nine round-1 survivors are killed: `ev/r1_own_mutants.txt` shows every site KILLED. One site no longer exists verbatim, and its replacement mutant `event_dedupe_dropped` is killed.
- Both round-1 follow-ups are taken: A->B->A->B gives three events, and the same board returning clears UNREADABLE (`ev/r1_probes.txt`).

The brief asks for one mutant of my own per row, planted fresh against the self-test. I planted 24 (`ev/own_mutants2.py`, output in `ev/own_mutants2.txt`), and 11 survive. These seven are the blocking ones, each on a behaviour the docstring, the body or the design states:

1. **tick-digest, gap 2.** `TRANSIENT` narrowed to `RED unanswered` only survives. The design (design.md:60, "a NOT REVIEWABLE or RED line counts only after two passes") and the body's gap-2 disposition cover both texts, but only the RED half has a case. The code is right today: `ev/probes2.txt` Q1 shows a single-board NOT REVIEWABLE writes nothing. A regression would bring back the exact false wake gap 2 records.
2. **roster-drain, hold release.** Deleting `op = parts[2]` survives, so the released op handed to roster_queue would be `hold <path> <op>`. That op would be refused and marked done, and the held op would be lost. The hold case checks timing only, not which op ran. The code is right today: Q3 shows `['set-stage G1 done']`.
3. **plan-beat.** state_docs' `--mirror <state_mirror>` can be dropped. This is the same wiring class as round 1's replan-args survivor, which was fixed only for replan.
4. **pulse.** `--launch-ledger` can be dropped. This is the same wiring class as round 1's `--seat-alive` survivor.
5. **cancel-sweep.** The `truncated` alternative of the failure regex can be dropped.
6. **opener.** `NEEDS-TITLE ` can be dropped from `OPENER`.
7. **opener.** `STARVED ` can be dropped from `OPENER`. open_driver.py prints both on stdout (open_driver.py:282 via `log`→`out`, and :302), and the design's opener row (design.md:67) names both. No case feeds either line.

Each needs a planted case, plus an argv assertion where the arm is wiring. That is the same repair round 1 asked for. The other four survivors are low severity and are listed under Findings.

## Findings

- Follow-up: `fold_locked` leaves `new.txt` (and `gone.txt`) untouched on a changing fold that adds nothing (or drops nothing). `new.txt` then still names a line no longer in `digest.txt` (`ev/probes2.txt` Q2: digest `''`, new.txt `MERGE-READY: #9 9a8b7c6d`). The docstring says new.txt is "the lines the last changing fold added". The wake keys on new.stamp, which is correctly not touched, so this is a doc/behaviour mismatch for any reader of new.txt alone: either empty new.txt on such a fold or restate the docstring. Carry: R10-FLY-STANDING-CONTRACTS
- Follow-up: four further own mutants survive, each low severity. (a) head-watch keeps closed PRs in heads.tsv forever, unpinned. (b) fold's Counter can become a set with no case, so a duplicated line collapses. (c) `Ctx.need` can accept `""` with no case. (d) a malformed hold line can be left un-marked, so it re-prints every pass, with no case. Plant a case for each with the seven above. Carry: R10-FLY-STANDING-CONTRACTS
- Follow-up: the opener row's STUCK arm (to jobs/opener and events.txt) has no producer at this head. open_driver.py prints no `STUCK ` line. The design says STUCK lands "once landed" (design.md:67, 240), as an open_driver.py edit owned by R10-HANDOFF-PATH. The arm is forward-wired, as designed. The docstring states it as live, and the stage that lands STUCK must keep the `STUCK ` prefix the OPENER regex reads. Carry: R10-HANDOFF-PATH

## Evidence

- RESULT: head 344feb6c1f273db37c90105407bf2f26fc0b6adb (`refs/pull/3197/head` at review); merge base 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e; origin/main 62f94f3fbceb6acfbd3a79b42f300f091406c10c. No change under dev/governance/roles/ between the merge base and main. Round 2: the body and verdict/3197 agree. The brief's "first-round" is stale.
- RESULT: `beat_jobs.py --self-test` prints `beat_jobs self-test: 82 checks, 0 failed`. All 32 named mutants are killed, matching the body's count of 32 (16 + 16) (ev/beat_jobs.selftest.txt).
- RESULT: `pulse.py --self-test` prints 58 checks, 0 failed. `sweep_render.py --self-test` prints 34 checks, 0 failed. `selftest_wiring.py --check` prints `112 self-testing, 112 wired, 0 unwired` and `0 index gap(s)`. `closure.py select` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` `structure.py` prints `STRUCTURE RATCHET PASSED` (ev/checks.txt). Every body figure is re-derived.
- RESULT: VERSION, the manifest, RELEASE_NOTES.md, both claim files and every `*_budgets.json` are untouched in the three-dot diff.
- RESULT: `git merge-tree --write-tree origin/main HEAD` exits 0, with `LEDGER-MERGE: resolved tests/closures.json` on stderr (ev/checks.txt).
- RESULT: `beatd.load_table(tools/audit/seat/beatd.jobs.json)` loads 9 jobs with the docstring's intervals (240/1800/120/1800/300/600/900/300/120) and class_wait_s 60.0, with no refusal. beatd runs each job in its own sequential thread and holds a per-job lock (beatd.py:318-321, 365-384), so roster-drain cannot overlap itself. Only the orchestrator's unlocked append races it, and terminated-lines-only now covers that.
- Pulse row outside digest/: beatd.py writes no pulse.txt. It only reads `S/beatd/pulse.txt` in `status` (beatd.py:481-504), so the pulse row is its single writer, written atomically. The body states this exception.
- pulse.py, sweep_render.py, sweep_template.md, beatd.jobs.json and governance.yml are byte-identical to round 1's head fe2077441519. Round 1's checks on carry 5 (two owed verdicts name both PRs and both seats; one verdict stays one line), the git-cwd refusal (bare step (2) refused, tracked template renders) and the governance step stand. Their self-tests are re-run green above.
- Gaps: design.md at 21210036 has no gap table. Gaps 1-6 are inline (design.md:53-62). Gap 3 routes to P2 at :225, gap 4 to P3 at :194, gap 5 to P2 at :228, with P5's generation token at :244 as round 1 cited, so the destinations exist. Gap 7 (the body's "owed before P2's retirement gate") appears in no design line, so it is the body's own and I did not verify it. Gaps 1, 2 (RED half), 4 and 6 hold at the head through their self-test cases. Gap 2's NOT REVIEWABLE half holds in behaviour (probe Q1) but is unpinned (Block item 1).
- CI: `merge_train.py classify` was still `WAIT ... pending: gate red: none` at the time of writing (ev/classify.txt). A blocked verdict does not wait on it. `tests / nightly-status` is red, not required, and answered in the body as main's scheduled Nightly; the diff does not reach nightly.yml or tests/nightly_status.py.
- The instruments are my own, disclosed per fix-review.md 9: ev/own_mutants2.py and ev/probes2.py, plus round 1's ev/r1_own_mutants.py and ev/r1_probes.py re-run at this head. No committed finder's harness exists for this group.
