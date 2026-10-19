R10-OPENPR-SILENT. `tools/audit/seat/open_pr.sh` runs under `set -eo pipefail`. Twice on 2026-10-18 the orchestrator passed the handoff-BODY sha where the CODE sha belongs. `git merge-base --is-ancestor` returned non-zero and printed nothing, so the script exited silently, and the stop read as a hang for 40 minutes. The orchestrator then added tick items to this group, and in the recarry pass four more folds (`5` to `8` below), and one repair after a merge of main (`9`).

**1. No silent stop in `open_pr.sh` and `update_pr.sh`.** Both scripts now source a new library, `tools/audit/seat/pr_args.sh`, which gives them two layers.

- **Up-front argument checks.** Each failure prints an `open_pr: REFUSE: ...` or `update_pr: REFUSE: ...` line naming what is wrong:
  - the argument count;
  - a code sha that is not 40-hex, or does not resolve;
  - a code sha that is not an ancestor of `origin/handoff/<topic>`. The line also says whether the sha is the tip of `handoff-body/<topic>` ("that is the BODY sha; pass the CODE sha");
  - a missing `handoff/<topic>`, or, for `open_pr.sh`, a missing `handoff-body/<topic>`;
  - no BODY.md at the body ref (`open_pr.sh`), or no body file (`update_pr.sh`).

  `update_pr.sh` takes its body as a file, so a missing body ref does not refuse there. Its topic is `HANDOFF_TOPIC` if set; otherwise the branch less `fix/`, then less `-pr`, taking the first that origin holds.
- **An ERR trap** (`set -Eeo pipefail`, installed before the first command that can fail). Every other stop errexit makes prints `<name>: STOPPED: line N exited S: <command>` once, from the top-level shell.

Two more silent shapes are also fixed:
- A refused push whose log held no `REFUSE` line used to exit on `grep`'s own status and print nothing. It now names its log (`pr_push_failed`).
- `update_pr.sh` read the PR title through `gh` inside a command argument, where a failure stops nothing and leaves an empty title in the row. It is now an assignment.

**2. Open-PR soft cap** (tvofi, 2026-10-18, relayed by the round-10 orchestrator). `tools/audit/seat/pr_cap.py` holds the one counting rule: open PRs, drafts included, excluding `record:`-titled PRs and bots other than `app/hpo-author`.

- `open_pr.sh` runs `pr_cap.py gate` before it creates the worktree, so before any push. At or above `${HPO_OPEN_PR_CAP:-6}` it refuses: `open_pr: REFUSE: open-PR cap: N open >= CAP; drain before opening (HPO_OPEN_PR_CAP, --over-cap <reason>)`.
- A leading `--over-cap "<reason>"` overrides the cap and logs `open_pr: OVER-CAP: N open >= CAP, overridden: <reason>`.
- A count it cannot read refuses: gh failing, output that is not JSON, or a list at gh's 200 limit.
- `orchestrator_tick.py` imports the same module and prints two lines every pass: `OPEN-PR CAP: N/CAP`, flagged when N >= CAP; and `coordinator.py PRs: K/2`, the counted PRs whose three-dot diff touches the coordinator, flagged when K > 2 and when a diff is unreadable (K is then only a floor).

**Design choice on "bot" (fixer.md step 11).** Every seat PR is authored by the hpo-author App, which GitHub flags as a bot, so excluding every bot would count nothing; here a bot is any flagged bot other than `AUTHOR_APP`. The board is over the default cap now (`## Figures`), so `open_pr.sh` refuses until it drains or `--over-cap` is passed; the orchestrator should know that before this merges.

**3. Tick level lines.** These print state every pass, not events (the round-10 orchestrator, 2026-10-18).

- **`MERGE-READY: #N <head8>` and `BLOCKED-UNFIXED: #N <head8>`**, read from the approver App's newest `Fix review:` comment. The App's identity comes from `app_approve.sh`'s `VERDICT_AUTHORS` and `VERDICT_AUTHOR_ID`, through `proof_watch.verdict_allowlist`, their one reader; the grammar is `bus.sh`'s `verdict_sha`. MERGE-READY: a merge verdict at the current head, on a CLEAN or UNSTABLE PR. BLOCKED-UNFIXED: a blocked verdict at the current head, with no `handoff/<topic>` tip committed after the verdict. A verdict at a stale head prints neither. Cost: one comments read per open PR per pass.
- **Queue entries.** An entry counts as unmerged only when its PR is OPEN, decided by one `gh pr list --state open` per pass that TRAIN and REPLAN share. Both sections used to compare `pulls/<n>` `.state` to `"merged"`, a value REST never returns (a merged PR reads `closed`); the self-test stub returned `"merged"`, so the stub encoded the bug (fixer.md step 13's class).
- **`OWED: <line>`** for each OWED entry in `cloud_relay.sh`'s log (its default path, `$HPO_STATE_DIR/cloud-relay.log`) that has no later POSTED for the same PR. No log yet means no OWED line.
- **`HANDOFF-AHEAD`** landed in `d5207784` and was dropped by the orchestrator (tvofi approved), because the #2419 fixer folds it into the tracked cloud_relay; `05744ce7` reverts it.

**4. `tools/audit/seat/tick_loop.sh`, the tick's driver loop.** Each pass runs `cloud_relay.sh pass`, guarded by a file-exists check so the loop also runs before #2419 lands, then the tick, writes the whole board to `--out`, and prints one `TICK-PASS` banner. A failing relay pass or tick is reported, and the loop carries on. The tick stays read-only; the driver is what acts.

**5. The tick's missing-row and closes checks see a `<title> (#N)` merge** (the orchestrator's fold, 2026-10-19). Both enumerated `git log --merges` with the tick's own `Merge pull request #(\d+)`, so a single-parent title-form merge (the record-autofix merges #2413, #2412, #2407) was never checked. A new `Tick.merged_prs` reads main's first-parent line through `tests/delivery_status.py`'s own `parse_log` and `collect` (loaded with the tick's `_module`), and the tick's copy of the grammar is deleted. A log it cannot read is now UNREADABLE; the STATE arm used to skip it silently.

**6. The tick's OWED-handoff arm sees a PR behind its own handoff** (the same fold: #2411's handoff sat unapplied from 19:49Z). Two defects, both on the live board:
- `bus.sh orphans` discharged a handoff by its exact `fix/<t>` or `fix/<t>-pr` name alone. The name now discharges only a head that carries the tip; a named head behind it reaches the existing repair word, `update` (`review` when diverged), which the exact-name arm had made unreachable.
- The tick read `bus.sh orphans`' exit 1, which means "a ref is stranded", as "unavailable", so it never printed a live orphan; with none stranded it would have printed the summary line as an orphan. It now keys on the run's summary line: each `ORPHAN` line prints as `OWED handoff: <line>`, flagged; `SUPERSEDED` lines print as unflagged prune lines; a run with no summary, or an exit that contradicts its lines, prints one `bus.sh orphans unavailable ... UNCHECKED this pass` line.
- **Design choice (fixer.md step 11): no age window.** The tick passes `--min-age-h 0` (`BUS_ORPHANS_ARGV`). bus.sh's default spares a ref younger than 2 hours as in flight, but a handoff whose body ref exists is complete, and a level line that waits two hours is how #2411's sat.

**7. `--only CARRY`: the weekly and closure carry sweep** (the orchestrator's carry, 2026-10-19). #2404's reviewer routed it to R10-TICK-DRIVERS, and #2390 merged without it. The section runs `tools/audit/carry_audit.py --roster-ref origin/main [--roster-ref <the tick's roster ref>] sweep --last N --issues`, with `N` from `--carry-last` (default `CARRY_LAST`, 20).
- Exit 1 prints one flagged dispatch line naming the command, then the sweep's unowned lines, capped at `CAP_CARRY`.
- Exit 0 prints the `CARRY-SWEEP:` summary, unflagged.
- Any other exit, or no summary line, is UNREADABLE.
- The refs are origin/main first and then the tick's roster ref (`--roster-ref`, else `roster_lib.DEFAULT_ROSTER_REF`), passed once when they are equal. `roster_drift` then reports a carry main holds that the ref roster pull requests are cut from lacks.
- `carry_audit.py` lands with #2404. Until then the section prints `UNREADABLE: carry sweep (tools/audit/carry_audit.py absent (it lands with #2404))`.
- **Design choice (fixer.md step 11): opt-in, never in the default pass.** The sweep reads the body and comments of every one of N merged pull requests, which the four-minute tick cannot carry. The orchestrator runs `--only CARRY` weekly and at closure. Putting it in the default pass is mutant C3, which the all-clear null control refuses.

**8. The unrecorded-merge check counts a `<title> (#N)` merge too** (the orchestrator's ruling, 2026-10-19: every merge owes a #201 comment, a record merge included, and the orchestrator writes one after each). `unrecorded()` used to list `git log --merges -10 origin/main`. That read had two faults: it never saw a single-parent squash merge, and, not being first-parent, it filled its ten slots with merges of main into branches, which are no merge to main. It now reads the newest `CAP_MERGES` merges among main's last `UNRECORDED_SCAN` (4 x `CAP_MERGES`) first-parent commits, through the same `merges()` path as fold 5. The four-to-one window leaves room for direct pushes such as stamps, which owe no comment.

**9. A disclosed self-correction: fold 7 after #2406 (O17).** The orchestrator merged main `dd27e7c1` onto `0b5c9b24`, and that brought #2406, which replaces `roster_lib.DEFAULT_ROSTER_REF` with `default_roster_ref(git)`: the round's roster branch, else main. Fold 7's `carry_sweep` still read the removed constant. The merge was textually clean, but at `01e08685` `--self-test` raised `AttributeError`, so the earlier body's "142 checks, 0 failed" was false there (the blocked verdict at `01e08685`). The fix:
- PLAN and CARRY now share one `Tick._roster_ref`: `--roster-ref` if given, else `default_roster_ref` through the tick's own git, with its note printed in the section. The sweep's refs are `rl.MAIN_REF` and that answer, passed once when they are equal.
- A missing `roster_lib.py` is UNREADABLE, never a guessed ref.
- A new arm drives the sweep with no `--roster-ref`, with the round branch present and absent, and reports a raise as a failed check.
- Every call into the CARRY section in the self-test now runs guarded. A raise there fails "no call into the section raises" and no longer aborts the self-test, so this regression (mutant R1) fails 8 named checks instead of printing no tally.

**Why this shape (fixer.md step 17).**
- One library holds the argument checks and the trap; copying them into each script would put one concept in two places. The trap instead of a `|| { echo; exit; }` on every line, which is #1874's enumerated-cases shape.
- One cap module for both readers, loaded the way the tick loads production modules (`_module`).
- One open-set read for TRAIN and REPLAN, replacing N `.state` reads that were also wrong.
- The relay call sits in a driver, not in the tick, whose contract is "it does NOT act".
- Fold 5 imports the registered reader of `merge-subject-pr` instead of widening the tick's own regex, which would have been a fifth copy for `agreement.mjs` to hold. Fold 6 fixes the discharge rule in `bus.sh`, the one instrument; a second ancestry test in the tick would have held the concept twice. Fold 7 calls `carry_audit.py` as a subprocess, the way the tick calls `bus.sh`, rather than importing its parser, so the tick keeps no copy of the `Carry:` grammar.

**Two deviations from the asks.** MERGE-READY, the queue fix and OWED were each asked for "same commit as MERGE-READY"; they are separate commits, because the MERGE-READY commit sits behind a merge of origin/main. And `--self-test` is chained rather than given a new flag: `open_pr.sh --self-test` and `update_pr.sh --self-test` run `delivery_row.sh --self-test`, then `pr_args.sh --self-test`, which also requires `pr_cap.py --self-test` to report 0 failed.

## Head

`9863f753f7be8dd8bcc860f016437a7de4e805bb`, on origin/main `fa16596c3438ba7010a19138d293d4b6a4379375`. Merges of main: `62d7e1e43c5f` (main `b87e8f19`: #2423, #2424, #2420), `3bf31b82768e` (main `06c6f3cf`: #2390, #2425) and `3fe49467f` (main `fa424fd9`: #2419, #2426, #2408) by this seat, each with no conflict; then the orchestrator's `7635793e` (onto `0b5c9b24`) and `6ad3b1bb` (main `dd27e7c1`: #2411, #2417, #2406), and its delivery row `01e08685`; then this seat's `9863f753` (main `fa16596c`: #2399, #2427, #2421), with no conflict.

Commits, in order:
- `fb46dfc7`: the failing test, first. `0522a2d4`: the fix and the cap. `06e41c39`: their INSTRUMENTS entries.
- `c2366b1e`: MERGE-READY and BLOCKED-UNFIXED; `a088da38`: their entry.
- `0670b9ce`: a merge of main (one INSTRUMENTS.md conflict, both entries kept).
- `ddb670d8`: the open-set queue fix; `a5cc7961`: its entry.
- `d5207784` and `05744ce7`: HANDOFF-AHEAD and its revert.
- `b31e4a45`: OWED. `7fa628e6`: `tick_loop.sh`. `ee93af58`: one reader of the approver allowlist (`proof_watch.verdict_allowlist`).
- `62d7e1e4`: the merge of origin/main `b87e8f19`.
- `d4f47f04`: folds 5 and 6, with their INSTRUMENTS lines. `3adda66d`: one more arm for fold 6 (see M4b).
- `5c729de5`: fold 7. `3bf31b82`: the merge of origin/main `06c6f3cf`. `d41ec9d2`: fold 7's argv checks read `calls[:1]`, so a sweep never called fails them instead of crashing the self-test.
- `3fe49467`: the merge of origin/main `fa424fd9`. `0b5c9b24`: fold 8, with its INSTRUMENTS line.
- `7635793e`, `6ad3b1bb`, `01e08685`: the orchestrator's merges and row (above).
- `86a488dc`: fold 9's fix and its arm. `9cc10cd0`: the CARRY section's self-test calls guarded. `9863f753`: the merge of origin/main `fa16596c`, which changes `proof_watch.py`, a module the tick imports; every figure below was re-taken after it.

Every figure below was measured at this head unless it names another commit.

## Mutation proof

**Built-in mutants (`pr_args.sh`).** A line ending in `# mut:<name>` is the predicate one arm pins. The self-test runs each refusal arm twice on copies of the scripts in a scratch repository: once intact, then with that line deleted. The arm must pass the first time and fail the second. `bash tools/audit/seat/open_pr.sh --self-test` prints `pr_args self-test: 46 checks, 0 failed`.

**Hand mutants, folds 5 to 9, at this head.** Each applied to the committed tree, run with its script's `--self-test`, and restored with `git checkout --`; `git status --short` was empty after the run.
- M1, `merges()` returns the `Merge pull request #(\d+)` matches (the old grammar): 5 failed, among them "STATE missing rows: a squash `<title> (#N)` merge with no row is named; ...", "closes squash: a squash merge's declared-vs-closed mismatch is flagged" and "unrecorded single-parent: ...".
- M2, an unreadable log returns `[]`: "STATE missing rows: a log it cannot read is UNREADABLE, never a clean zero".
- M3, `rc != 0` is unavailable (the old reading): 3 failed, among them "OWED handoffs: a stranded ref at bus.sh's rc 1 is OWED, flagged, never 'unavailable'".
- M4, the summary requirement dropped: the self-test crashes with `IndexError` at `summary[0]` in the refusal arm, so no tally prints and it exits non-zero.
- M4b, the exit/lines consistency clause dropped: unpinned at `d4f47f04`, where no arm drove an exit that contradicts its lines. I added "OWED handoffs refused: an exit that contradicts its lines (rc 0 beside an ORPHAN) is unavailable" in `3adda66d`, which kills it.
- M5, `BUS_ORPHANS_ARGV = ("orphans",)`: "OWED handoffs: the read carries no age window (a complete handoff is owed now)".
- M6, OWED handoff lines unflagged: "OWED handoffs: a stranded ref at bus.sh's rc 1 is OWED, flagged, never 'unavailable'".
- C1, the sweep call removed: 7 failed, the arm's argv, dispatch, refusal and opt-in checks among them ("the sweep runs --last N --issues over origin/main, then the tick's roster ref").
- C2, the CARRY dispatch removed from `run()`: "CARRY sweep: opt-in: the default pass never sweeps; --only CARRY does".
- C3, CARRY in the default pass: 4 failed, that arm and three of the all-clear board's ("null control: zero findings", "null control: empty list line printed" and "null control: all eight sections measured").
- C4, the second roster ref dropped: 3 failed, "the sweep runs --last N --issues over origin/main, then the tick's roster ref" and both "CARRY default roster ref" arms.
- C5, `--issues` dropped: 4 failed.
- C6, exit 1 unflagged: "exit 1 prints one dispatch line, then each unowned line, flagged".
- C7, a refusal read as clean (`if False:`): 2 failed, "no call into the section raises" and "a refusal (exit 2) is UNREADABLE, never a clean zero".
- U1, `unrecorded()` restored to its old `git log --merges --format=%H %s -10` read: "unrecorded single-parent: a single-parent `(#N)` merge with no #201 comment is named; a recorded merge and a direct push are not". The self-test's git stub answers `--merges` with the two-parent lines only, as git does.
- U2, `--merges` added to the first-parent read: the same check.
- R1, `carry_sweep` reads `rl.DEFAULT_ROSTER_REF` again (the regression): 8 failed, among them "no call into the section raises" and "CARRY default roster ref: with no --roster-ref the sweep runs without raising".
- R2, the default ref ignored (main twice): 2 failed, both "CARRY default roster ref" ref checks.
- R3, `_roster_ref` drops the note: 2 failed, "PLAN default roster ref: and the note says the branch is absent" and the CARRY null control.
- M7, in `bus.sh`, the exact name alone discharges (the old arm): `bus self-test: 70 checks, 1 failed`, "an exact-name pull request behind its newer handoff is repair=update, not discharged".

**Hand mutants from the earlier head, re-applied at this head.** The same mutants, by the same descriptions, each killed:
- Cap: T1 `flag=n >= cap` -> `False` (1 failed); T2 the K>2 test dropped (1); T3 the unread test dropped (1); T4 `counted(prs)` -> `prs` (2); T5 the call deleted (6).
- Verdicts: V1 and V2 the head test dropped (1 each); V3 `elif not newer` -> `elif True` (1); V4 the first verdict instead of the newest (1); V5 both identity keys dropped (1); V6 UNREADABLE replaced by `pass` (1); V7 the CLEAN/UNSTABLE test dropped (1).
- Queue: Q1 `stale = []` (5); Q2 REPLAN's open-set test -> `False` (1); Q3 an unread set treated as empty (1); Q4 the no-train line dropped (1).
- OWED: W1 POSTED no longer clears (2); W2 the flag dropped (2); W3 only the last OWED per PR kept (1); W4 a missing log reported UNREADABLE (1).
- `tick_loop.sh`: L1 relay not called (2); L2 the guard -> `true` (1); L3 two passes under `--once` (2); L4 the interval check disabled (1); L5 a failing relay stops the pass (1).

## Null control

**Failing first.** M1, M3 and M7 restore the old production behaviour line for line, and each fails the new arms (above). At `fb46dfc7`, the `pr_args.sh` self-test against main's unchanged scripts printed `pr_args self-test: 31 checks, 17 failed`.

**Fold 6, before and after on the live board.** `python3 <tree>/tools/audit/seat/orchestrator_tick.py --checkout <this worktree> --only REPLAN,STATE`, against origin/main `b87e8f19`, 2026-10-19T01:06Z, once from a `git archive` of `62d7e1e4` (before the fold) and once at `3adda66d` (the fold-6 code is unchanged since):
- before: `-> bus.sh orphans unavailable (exit 1): the subcommand depends on #2112, unmerged -- fold its refs when it lands`, and no ref;
- after: 10 `-> OWED handoff:` lines, one unflagged `superseded handoff ref` line, and the summary `orphans: 10 stranded, 1 superseded; skipped no-body=25 named=13 ancestor=57 young=0; origin main b87e8f1`. One of the ten is the #2411 class, live: `audit-r10-roster ... repair=review`. `fix/audit-r10-roster` (#2417) exists, and `merge-base --is-ancestor` gives rc=1 in both directions against `handoff/audit-r10-roster`, so the old name arm had discharged it.

**Fold 7, live.** `python3 tools/audit/seat/orchestrator_tick.py --only CARRY` against origin/main `06c6f3cf`, 2026-10-19T02:09Z-02:10Z, with fold 7's code (committed as `5c729de5`):
- in this tree, which has no `carry_audit.py`: `-> UNREADABLE: carry sweep (tools/audit/carry_audit.py absent (it lands with #2404))`;
- with #2404's `carry_audit.py` (`b419463b`) copied into the tree untracked for the run and deleted after it (`git status --short` then listed only the uncommitted tick file): a flagged `carry sweep found unowned findings (CARRY-SWEEP: 20 pull request(s), 2 other unowned finding(s); refs origin/main)` dispatch line, 20 flagged `UNROUTED` lines (among them #2390, #2424, #2423 and #2401 items) and `... 56 more`.

These lines depend on the board, so re-derive them with the same command.

**Fold 5, before and after on main's history.** A one-off scratch probe loads the tick from the `62d7e1e4` archive and from `3adda66d` and enumerates `3126b86e7~1..b87e8f19b`. Before: `MERGE_PR` over `git log --merges --format=%s`. After: `Tick.merged_prs`. Result: before 16 PRs, after 19. `after - before` is `['2407', '2412', '2413']`, and `before - after` is `[]`. As a null control, the PRs the after side adds that are not single-parent `(#N)` subjects: `[]`. Single-parent `(#N)` subjects the after side misses: `[]`. Rows for #2413/#2412/#2407 are at main now, through #2420, so the live STATE arm prints no missing row at either end.

**Fold 8, on main.** A one-off scratch probe loads the tick at `0b5c9b24` (`merges()` and `unrecorded()` are unchanged since) and compares, over origin/main `fa424fd9`, the shas the old read (`git log --merges --format=%H -10 origin/main`) and `Tick.merges` (first 10 of the last 40 first-parent commits) would search for:
- old only, 5 shas, each `Merge remote-tracking branch 'origin/main' into ...` or `Merge commit '<sha>' into ...`: merges of main into branches, which can never carry a #201 comment, so the old read could report them as owed;
- new only, 5 shas: #2420, #2424, #2423, #2401 and #2379, main's own merges.

There is no single-parent merge in this window; the squash merges #2413/#2412/#2407 are older, and the self-test arm drives that shape.

**No over-firing at this head.**
- `open_pr.sh` with the code sha, and `update_pr.sh` with the code sha or `-`, pass every argument check.
- Five counted PRs, plus a `record:` PR and a dependabot PR: the open passes.
- A merge or blocked verdict at a stale head prints nothing.
- A queue of merged entries prints no train-not-alive line.
- An OWED followed by a POSTED prints nothing.
- With no cloud_relay.sh, the loop still ticks.
- `0 stranded` prints its summary and flags nothing.
- A carry sweep at exit 0 prints its summary and flags nothing; the default pass never runs it.
- Every merge with a #201 comment names no owed record beat.
- The exact-name PR at the handoff tip is discharged by name.
- A rowed merge, a direct push and a numberless merge name no missing row.
- The tick's all-clear board passes.

## Figures

- `bash tools/audit/seat/open_pr.sh --self-test`: `delivery_row self-test: 5 checks, 0 failed` and `pr_args self-test: 46 checks, 0 failed`.
- `python3 -I tools/audit/seat/pr_cap.py --self-test`: `12 checks, 0 failed`.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `150 checks, 0 failed`.
- `bash tools/audit/seat/tick_loop.sh --self-test`: `4 checks, 0 failed`.
- `bash tools/audit/seat/bus.sh --self-test`: `70 checks, 0 failed`.
- `python3 tools/audit/seat/proof_watch.py --self-test`: `34 checks, 0 failed`.
- `python3 -I tools/policy/agreement_py.py --out $J && node tools/policy/agreement.mjs --py-json $J`: `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`.
- `python3 -I -S tests/delivery_status.py --check`: `DELIVERY STATUS OK -- 0 overdue`, at origin/main `fa16596c`.
- `python3 -I tools/audit/seat/pr_cap.py gate --repo tvofi/heatpump_optimizer`, 2026-10-19T01:25Z: `open-PR cap: 14 open >= 6`, rc=1.
- Gate scope: `python3 tests/closure.py select --diff fa16596c3 --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. Each `run_always` line (`tests/env_drift.py --claims-only fa16596c`, `tests/closure.py selftest`, `tests/harness_headers.py`, `tests/layout.py`) exits 0 under `PYTHONPATH=tests/hastub`.
- `env -u BASH_ENV python3 tests/entities.py`: `ALL 2349 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`, `python3 -I tools/audit/seat/ref_privacy.py --check` and `python3 -I tests/throwaway_git.py --check` each report 0 refused.
- **Merge-tree against the open siblings.** `git merge-tree --write-tree --name-only HEAD <head>` at this head, #2406 `22803f99bd8b`, #2421 `1e6e79caa3b2` and #2417 `954a7b20ffb3` each rc=0 with no conflicted file. #2404 `b419463b18a2` gives rc=1 on the three `finding-propagation` rule files. This diff touches none of them, and `git merge-tree --write-tree --name-only origin/main b419463b18a2` gives rc=1 as well, so it is main's conflict (#2408), not this PR's.
- **Fold 5's class, every seam.** The rule: `git grep -nE 'Merge pull request #\(|"--merges"' <ref> -- tools/audit/seat/orchestrator_tick.py`, excluding the self-test.
  - At `62d7e1e4` it returns 4 sites: the `MERGE_PR` constant, STATE's missing-row log, `unrecorded()`'s log and `closes()`'s log.
  - At this head it returns none outside the self-test, whose git stub models `--merges`. All four are closed in this diff, `unrecorded()`'s by fold 8.
  - The same rule over the rest of `tools/audit/seat/` returns no file.
- **Fold 6's class.** The rule is every `continue` in `bus.sh orphans`' loop, which is a discharge. There are six: excluded topic, no body, name, ancestry, young and superseded. The name arm is the one that discharged without asking whether the tip is carried, and it is closed here. Ancestry asks exactly that. Young is turned off by the tick's `--min-age-h 0` (design choice above). No-body, superseded and the exclusions are bus.sh's own dispositions, and the tick prints superseded ones.

## Unpinned sites

The `# mut:` lines are pinned by the self-test's own mutant rows. The tick's flags are pinned by its checks, with M1-M7, T, V, Q and W above as evidence; `tick_loop.sh` is pinned by its 4 checks, with L1-L5. Any site prepr step 6d lists is left to `mutation-autofix`.

## Red checks

The latest CI is on the PR head `01e08685` (the 03:36Z run). It has seven reds, and each job's log names the GitHub App installation's API rate limit, not this diff:
- `arch-score` (two runs) and `pr-contract` (two runs): `gh: API rate limit exceeded for installation` while reading the pull request.
- `validate-hacs`: `GitHubRatelimitException: API rate limit exceeded for installation`.
- `nightly-status`: `NIGHTLY UNREADABLE: ... HTTP 403` reading the last scheduled run.
- `env-matrix`: `FAIL pr / nothing skipped in a full clone -- ... the GitHub API is unreachable`, the same window.

The cheaper detector already exists: each of these lanes refuses loudly when its read fails, rather than passing. The cost is a re-run once the quota resets. The cause is the hourly quota every seat draws on; no change in this diff answers it.

The reds on the earlier head `ee93af58` (`wave-script`, `delivery-status` and `pr-contract`) were main's. The merge of main `b87e8f19` cleared them, through #2423, #2424 and #2420. At this head, the agreement lane prints `AGREEMENT ok`, and `delivery_status.py --check` reports 0 overdue.

The regression the verdict at `01e08685` blocked on is fold 9, above. CI could not have seen it: no workflow runs `orchestrator_tick.py --self-test` (Forward-carry, CI wiring).

## Forward-carry

- **Delivered here: the weekly and closure carry sweep** (fold 7). #2404's reviewer routed it to R10-TICK-DRIVERS, which merged as #2390 without it. The #2404 seat is appending the matching roster carry to R10-OPENPR-SILENT. Until #2404 lands the sweep tool, the section prints its absence as UNREADABLE (fold 7 above).

- **CI wiring.** No workflow runs the self-tests of `pr_args.sh`, `pr_cap.py`, `tick_loop.sh`, `orchestrator_tick.py` or `delivery_row.sh`. Adding a `governance.yml` step changes `.github/workflows/`, which tvofi owns, so it is for the orchestrator to dispatch as its own group. Fold 9's regression is this gap's cost: the orchestrator's merge of main broke `--self-test`, and nothing ran it before review.
- **Runbook.** `dev/governance/roles/nudge.md` and `orchestrator.md` name `open_pr.sh` without `--over-cap`, and a watcher seat looping the tick rather than `tick_loop.sh`. Both are policy files (CODEOWNERS `dev/governance/roles/`), so they are left unedited. `tools/audit/seat/INSTRUMENTS.md` holds the contract.

## Friction

- fixer.md-step-5: cost: the checkout's `.git/info/exclude` lists `seat/`, so `git add <path>` under `tools/audit/seat/` refuses with a hint even for a tracked file; `git add -u` works.
- fixer.md-step-5: unenforced: `tests/entities.py`'s check "the lease has one winner, a dead gate is stolen, a live one is not, and run.sh runs unleased" failed with `grandchild_alive=True` inside prepr's closures step and in one standalone run (`env -u BASH_ENV`), then passed on an unchanged tree (`ALL 2349 ENTITY CHECKS PASSED`). The diff touches no gate-lease file, so this reads as a host-timing flake in that check.
- fixer.md-step-6: cost: the main-checkout guard hook judges a bash call by the shell's persisted cwd, not by a `cd` inside the command, so a `git merge` after `cd <seat worktree>` was refused until written as `git -C <seat worktree> merge`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
