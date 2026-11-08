Two merge-train changes on one seam, under the owner's waste-study rulings (tvofi, 2026-11-07, cards 1 and 5, both accepted). The ruling's lead-time and recarry figures are the brief's (the waste-study scripts live in the orchestrator's s12 directory, outside the tree), and this seat did not re-take them.

Card 1, the rejoin. Under `--skip-bad`, an entry the train skips on a head red that includes `gate` now rejoins the same train. `at_head` and `admit` raise a new `HeadRed` (a `Stop` carrying the head and the red names), and `Train.rejoin_candidate` queues that skip. After the batch's own merges and serial entries, `Train.rejoin` reads each queued head through `classify_at` (the reading the `classify` CLI prints, deferral and sweep settle included). On GREEN the entry runs the serial path (`one`), with no `add` and no merge seat. On RED it stays skipped: a real red never rejoins. It also stays skipped if the head is still WAIT `wait_cap_s` after its skip, or if the branch moved off the skipped head (a new head owes a new verdict). Each outcome is logged as `REJOIN #<pr>: ...`. A rejoined merge is `CURED` by the existing `skip_report` rule, and a refused rejoin replaces its earlier skip row. `wait_cap_s` is `polls x (REVIEW_POLL_SECONDS + POLL_SECONDS)`, the review-run wait's ceiling, 7320 s at the default 24 polls. It is now one method, read by `review_settle`'s log and by the rejoin.

Card 5, no recarry. `Train.recarry` now asks `Train.merges_as_is` before it recarries a head that lacks origin/main. Recarry still happens in four cases:
- `main-protect-checks` requires an up-to-date branch: `strict_update`, read live, where unreadable counts as required. This is the brief's "behave as today wherever the ruleset forces an up-to-date branch".
- git's merge of origin/main and the head conflicts (`merge_tree`, the train's driver-free text merge). This is the one content reason.
- The head is a GITHUB_TOKEN tip, whose cure is the recarry's App push.
- A graded red holds the car (`grade_held`), so its recarry and CI are still owed.
Otherwise the head merges as it stands. The train logs `#<pr> no recarry: ...` and records the merge base as `nr_base`. `one`, the MainMoved recovery in `serial` and `--overlap`'s up-front loop hand that base to `at_head` as `rb`. So `grade_merge` grades the tree about to land, origin/main merged with the proven head, at the merge and again in its guard, as R10-TRAIN-OVERLAP-GRADE already does for an overlap car. A batch's proved entries never recarried, so card 5 changes the serial path only.

Carry f7d2bf7c (from #3288): remerge_main.sh printed `MERGE CONFLICT` for any failure of its fetch, reset and merge chain. Now it prints `MERGE CONFLICT <pr>` only when the merge left unmerged paths. Any other failure prints `REMERGE FAILED <pr> at <fetch|reset|merge> (rc=N)` under git's own words. `recarry` stops on that line as a git failure, never as "main does not merge without a resolution".

Design choices:
- The rejoin runs after the batch's own merges rather than as a re-spool. A re-spool would need the next drain to wait on a classify, and nothing drains while a train idles. Running in-train keeps the "no add" property and holds none of this batch's merges (test (b), WAIT).
- No recarry grades against the merge base rather than main's tip. With main's tip as `rb`, `grade_merge` returns ungraded whenever the batch itself moved nothing, and a foreign main would land unread. M14 kills that form.
- The live ruleset needs no change today (below), so the strict read is the "until it is applied" arm and costs two ruleset reads per recarry decision.

## Ruleset change

Live read at 2026-11-08T20:08Z: `gh api repos/tvofi/heatpump_optimizer/rulesets/23698884 --jq '{updated_at, rules: [.rules[] | {type, parameters}]}'` returned `updated_at` 2026-10-27T22:36:19.629Z, a `required_status_checks` rule with `required_status_checks: [{"context":"gate","integration_id":15368}]` and `strict_required_status_checks_policy: false`, and a `pull_request` rule (one approving review, code-owner review required, `dismiss_stale_reviews_on_push: false`).

The exact change that lets a proven batch merge without a per-PR rerun is none. `strict_required_status_checks_policy` is already `false`, so GitHub does not require a branch to be up to date with main. The one required context, `gate`, is the one the head's own CI already concluded at the verdicted head. With `dismiss_stale_reviews_on_push: false`, no recarry is needed to keep an approval either. tvofi has nothing to apply. If `strict_required_status_checks_policy` is ever set to `true`, `strict_update` reads it at the next recarry decision and the train recarries every head that lacks main, as before this change. The null control under `NO RECARRY null control: under a strict policy` pins that.

## Head

1dae7f1c96b548cfc35292209d0e4076a0abcc18, cut from origin/main 17e621f08c4feec724478573741fbd8b596ceaba. 5358f7b1 was the first prepr-clean head. 1dae7f1c adds only tests and harness entries, pinning step 6d's survivors, with no production line. origin/main stood at 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a at 2026-11-08T20:40Z, with `git merge-tree --write-tree origin/main HEAD` clean with the ledger driver and without it (the same tree, 1faf4d8d). It stood at 661d26a5d2e655f32391048605db5970d133db1d at 2026-11-08T22:27Z, again clean (tree 5ca0cada). The brief's owner ruling (2026-11-07) is to merge origin/main only on a merge-tree conflict, so nothing was merged, and the dispatch's merge-when-moved step yields to it. prepr's `merged structure` step graded the merged tree (`STRUCTURE RATCHET PASSED`). Every figure below was taken at this head, except the failing-first runs, taken at the tests-only tree before the fix.

## Mutation proof

Failing first. The tests were added with production unchanged, at the tree before the fix commit (folded into fcdfb82b): `python3 tools/audit/seat/merge_train.py --self-test` printed these FAIL lines:
- `NO RECARRY (c) --overlap: a clean merge tree against origin/main and an unchanged proven head merge with no recarry ...`
- `NO RECARRY (c): ...`
- `NO RECARRY null control (d): a merge-tree conflict against origin/main still recarries ...`
- `REJOIN (a): an entry SKIPped on a red gate whose head turns GREEN within the cap rejoins the train ...`
- `REJOIN null control (b): a head whose classify reads RED stays SKIPped ...` (at the base no `REJOIN` line exists)
The run then stopped on a TypeError in my own WAIT check (`rj and ...` handed a list to `check`), corrected to `bool(rj)`.

`bash tools/audit/seat/pr_args.sh --self-test` at the same point printed `pr_args self-test: 185 checks, 1 failed`, the failing check being `null control: a fetch git rejected is not fetched again ..., and is named REMERGE FAILED at fetch, never MERGE CONFLICT (carry f7d2bf7c)`.

Mutants: `python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py` (in this diff: one exact single-occurrence span per mutant, run through `merge_train.py --self-test`) printed `MUTANTS: 20 run, 0 not as required` at the head:
- M0, the unmutated head: PASS.
- M1, the rejoin fires on RED (`if state == "green":` -> `if state in ("green", "red"):`): fails `REJOIN null control (b): a head whose classify reads RED stays SKIPped`.
- M2, the batch's `self.rejoin(rejoin, head_req)` deleted: fails REJOIN (a), (a) serial and both (b) cases.
- M3, every `HeadRed` a candidate, GATE or not: fails `REJOIN null control: a skip on a red that is not GATE is no rejoin candidate at all`.
- M4, cap 0: fails REJOIN (a).
- M5, cap x100: fails REJOIN (b) WAIT. That check bounds the check-run reads at the skipped head by the cap.
- M6, the moved-head guard off: fails `REJOIN: a skipped head the branch moved off does not rejoin`.
- M7, the serial loop's `rejoin_candidate` deleted: fails `REJOIN (a), serial`.
- M8, a recarry on every main move (`and not self.merges_as_is(item, h)` dropped): fails NO RECARRY (c) both, the merge-base grade, and (d).
- M9, the strict read ignored: fails four of today's recarry checks, among them `--overlap: every serial entry is re-carried UP FRONT` (the world's ruleset reads strict, as today's tests assume).
- M10, the conflict ignored: fails (d).
- M11, a bot tip ignored: fails `NO RECARRY keeps a bot head's cure`.
- M12, `grade_held` ignored: fails `NO RECARRY never skips the recarry a graded red holds`.
- M13, `one` passes `rb` None: fails NO RECARRY (c) and REJOIN (a) serial.
- M14, `--overlap` uses main's tip as `rb`: fails `NO RECARRY grades the un-recarried car against its merge base even when the batch moved nothing`.
- M15, `strict_update` always False: fails the same four checks as M9.
- M16, the `REMERGE FAILED` stop off: fails `carry f7d2bf7c: a remerge that failed before any conflict stops as a git failure`. With the stop off, the moved head reads as a push that landed and the entry would merge.
- M17, the rejoin's re-skip deleted: fails `REJOIN: a rejoin refused again (red at its own CI wait) is skipped again, its row replaced`.
- M18 and M19, the rejoin's sleep guard off or its sleep deleted: both fail REJOIN (b) WAIT, which pins one poll-grain sleep per WAIT read.

remerge_main.sh's `# mut:remergeconflict` line is pinned in pr_args.sh's own self-test. Its arm `mutant mut:remergeconflict (its line deleted): a rejected fetch is misreported as MERGE CONFLICT` passes at the head, where pr_args prints `185 checks, 0 failed`.

## Null control

- `REJOIN null control (b)`, RED: merged [1], one SKIP line for #2, no recarry, `skipped.json` still names #2.
- `REJOIN null control (b)`, WAIT: #1 merged before the rejoin's first read, #2 stopped at the cap, `TRAIN DONE`.
- `REJOIN null control`: a non-GATE red is never a candidate.
- `NO RECARRY null control: under a strict policy` and `... under an unreadable policy`: every serial head that lacks main is recarried, as today.
- `NO RECARRY null control (d)`: a merge-tree conflict still reaches remerge_main.sh.
- pr_args `null control: remerge_main on a clean merge keeps that merge`, and the conflicting-main arm still prints `MERGE CONFLICT 7`.
- Every pre-existing merge_train check passes unchanged: 564 checks at the base and 580 at the head, 0 failed at both.

## Figures

- merge_train at the base: `python3 tools/audit/seat/merge_train.py --self-test` at 17e621f0 prints `merge_train self-test: 564 checks, 0 failed`. At the head the same command prints `merge_train self-test: 580 checks, 0 failed`.
- pr_args at the head: `bash tools/audit/seat/pr_args.sh --self-test` prints `pr_args self-test: 185 checks, 0 failed`.
- Mutants: `python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py` prints `MUTANTS: 20 run, 0 not as required`.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Architecture: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, naming tests/entities.py. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2668 ENTITY CHECKS PASSED`, and the run_always scripts pass: `tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`, `tests/closure.py selftest` prints `ALL 118 closure shrink pins PASSED`, and `tests/layout.py` and `tests/env_drift.py --claims-only` pass. A first `closure.py selftest` read `1 of 118 ... FAILED` while the mutant harness's `_mutant_M*.py` copies stood untracked in tools/audit/seat; it passed once they were gone.
- CI prediction: `python3 tools/pr/ci_predict.py --apply-inert` wrote the harness's INERT READS entry (tests/closures.json) and then printed `CI PREDICT: no closures, fast, governance or instrument red predicted against 17e621f08c4f`.
- The rejoin's bound: `wait_cap_s` is `polls x 305` s, 7320 s at the CLI's default `polls` 24 (`Train.__init__`).
- Class enumeration, the rule `git grep -n "self\.recarry(" -- tools/audit/seat/merge_train.py`. It returns four call sites, all closed in this diff, because each hands `nr_base` on:
  - `one`;
  - `serial`'s MainMoved recovery;
  - `one_overlap`;
  - `_batch`'s `--overlap` up-front loop.
- Class enumeration, the rule `git grep -n "self\.skip(" -- tools/audit/seat/merge_train.py`. It returns five sites:
  - the admission skip and the serial skip, which can carry a `HeadRed`, closed (`rejoin_candidate`);
  - the up-front recarry skip and the merge-loop skip, which can carry no `HeadRed` (no CI read there), no candidate by construction;
  - the rejoin's own re-skip, which is final.
- Class enumeration, the rule `git grep -n "MERGE CONFLICT" -- tools/`, outside tests and docs. It returns remerge_main.sh (closed here) and handoff_push.sh's main merge. handoff_push.sh's chain is the merge alone, with no fetch or reset in it, so the transport misdiagnosis carry f7d2bf7c names cannot occur there.
- prepr: `bash tools/pr/prepr.sh` printed `PRE-PR: 5358f7b1fd67fbcf57be5c125d0f438c92e027e3 ... rc=0` (no body). At the head, with this body, `bash tools/pr/prepr.sh <body>` passes, its body check included (rc 0). Its diff-mutant step was run on its own, because a body run that included it passed the container's 30-minute background bound: `python3 -I tools/audit/seat/mutant_run.py --diff 17e621f08c4f...HEAD --cmd "python3 tools/audit/seat/merge_train.py --self-test" --max-mutants 40 --report-only`, at 5358f7b1, 21:20:55Z to 22:15:37Z. It listed 8 distinct survivors. M16 to M19 kill four of them, and `## Unpinned sites` answers the other four.

## Unpinned sites

The rule is the step 6d survivors at 5358f7b1 that no test added after them kills. Production lines are unmoved at 1dae7f1c.
- `tools/audit/seat/merge_train.py:2343 CALL_DEL` (`item.pop("nr_base", None)` in `recarry`). A real recarry left holding an earlier no-recarry base hands `at_head` that merge base as `rb` instead of None. `grade_merge` then grades the merge of main's tip and the recarried head, which contains main, so it grades tree(h) with a superset of touched files. The outcome is the same grade. The pop is kept so `rb` names the tree the head's CI read. Carry: dismissed: outcome-equivalent, a stale base widens the grade's file set and never narrows it
- `tools/audit/seat/merge_train.py:3550 GUARD_OFF` (`if s.step == "main": raise` in `rejoin`). The same rule as the batch's serial loop, `if s.step == "main" or not self.skip_bad: raise`. Inside a rejoin, a step "main" Stop is reached only through a MainMoved past `--main-moved-tries` at `at_head`'s contains-main guard, and no fixture world moves main during a rejoin's CI wait. Carry: dismissed: mirrors the serial loop's global-stop rule; reached only past --main-moved-tries
- `tools/audit/seat/merge_train.py:3556 CMP_BOUND` (`>= cap` -> `> cap`). A one-tick boundary. It is equivalent unless a read lands exactly on the cap second, and the cap is a bound, not a promise to the second. Carry: dismissed: boundary-equivalent at the train's poll grain
- `tools/audit/seat/merge_train.py:3562 CALL_DEL` (`self.hold_refresh()` before the rejoin's sleep). The record-beat hold refresh, the idiom `wait_ci` uses before each sleep. The batch world's hold API answers a refused commit (`NOT held`), so a count of refreshes would read only the refusal path. Carry: dismissed: the hold refresh is the train's standing idiom before every wait; its own arms are pinned in R10-TRAIN-HOLD's tests

## Red checks

none. This head's own CI starts at the handoff push.

## Forward-carry

- Carry 1 and Carry 3 (the review packet's numbering; from #3288 item 23779576), the measure-first count of BOT_HEAD stops in the train logs since 2026-10-20: not taken. This cloud seat holds no train log: `git ls-files | grep -cE '(^|/)train[^/]*\.log$|queue\.seen\.json|skipped\.json$'` printed 0, and no `~/.local/state/hpo` exists. The null control `git ls-files | grep -c merge_train` printed 2. The count, its re-measure command and its null control are written into dev/programme/carries/carry-201.json, last entry, for the orchestrator seat that holds the logs. Carry: #201
- Carry 2 and Carry 4 (from #3288 item f7d2bf7c), remerge_main.sh's misreported conflict: closed in this diff. Carry: dismissed: closed here, pinned by pr_args.sh's REMERGE FAILED arm and mut:remergeconflict
- Residual: the rejoin's wait (at most `wait_cap_s` after the skip) delays the next spooled batch's drain, never a merge of its own batch. Carry: dismissed: bounded by the train's own cap and the owner's card 1 asks for exactly that bound

## Friction

none
