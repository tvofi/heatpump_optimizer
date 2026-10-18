R10-OPENPR-SILENT. `tools/audit/seat/open_pr.sh` runs under `set -eo pipefail`. Twice on 2026-10-18 the orchestrator passed the handoff-BODY sha where the CODE sha belongs. `git merge-base --is-ancestor` returned non-zero and printed nothing, so the script exited silently: the daemonize log showed only its banner, and the stop read as a hang for 40 minutes. The orchestrator then added five tick items to this group and later dropped one of them. Each item is its own commit (`## Head`).

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
- `orchestrator_tick.py` imports the same module and prints two lines every pass:
  - `OPEN-PR CAP: N/CAP`, flagged when N >= CAP;
  - `coordinator.py PRs: K/2`, counting the counted PRs whose three-dot diff touches the coordinator. It is flagged when K > 2, and when a diff is unreadable, since K is then only a floor.

**Design choice on "bot" (fixer.md step 11).** Every seat PR is authored by the hpo-author App, which GitHub flags as a bot: all 17 PRs open at the first read had `app/hpo-author is_bot=true`. Excluding every bot would count nothing, so here a bot is any flagged bot other than `AUTHOR_APP`. At the time of writing the board counts 12, over the default cap of 6. `open_pr.sh` will refuse until the board drains or `--over-cap` is passed, and the orchestrator should know that before this merges.

**3. Tick level lines.** These print state every pass, not events (the round-10 orchestrator, 2026-10-18).

- **`MERGE-READY: #N <head8>` and `BLOCKED-UNFIXED: #N <head8>`**, read from the approver App's newest `Fix review:` comment. The App's identity comes from `app_approve.sh`'s `VERDICT_AUTHORS` and `VERDICT_AUTHOR_ID`, through `proof_watch.verdict_allowlist`, their one reader; the grammar is `bus.sh`'s `verdict_sha`.
  - MERGE-READY: a merge verdict at the current head, on a CLEAN or UNSTABLE PR.
  - BLOCKED-UNFIXED: a blocked verdict at the current head, with no `handoff/<topic>` tip committed after the verdict.
  - A verdict at a stale head prints neither.

  Why: #2401 sat merge-ready and #2399 sat blocked, unacted, because only events reached the orchestrator. Cost: one comments read per open PR per pass.
- **Queue entries.** An entry counts as unmerged only when its PR is OPEN, decided by one `gh pr list --state open` per pass that TRAIN and REPLAN share. Both sections used to compare `pulls/<n>` `.state` to `"merged"`, a value REST never returns (a merged PR reads `closed`). That is how t16's queue of three merged PRs (#2379, #2394, #2416) read as a dead train's. The self-test stub returned `"merged"`, so the stub encoded the bug (fixer.md step 13's class).
- **`OWED: <line>`** for each OWED entry in `cloud_relay.sh`'s log (its default path, `$HPO_STATE_DIR/cloud-relay.log`) that has no later POSTED for the same PR. No log yet means no OWED line.
- **`HANDOFF-AHEAD`** was asked for and landed in `d5207784`. The orchestrator then dropped it (tvofi approved) because the #2419 fixer is folding it into the tracked cloud_relay, and `05744ce7` reverts it.

**4. `tools/audit/seat/tick_loop.sh`, the tick's driver loop.** Each pass runs `cloud_relay.sh pass`, guarded by a file-exists check so the loop also runs before #2419 lands. It then runs the tick, writes the whole board to `--out`, and prints one `TICK-PASS` banner. A failing relay pass or tick is reported, and the loop carries on. No tracked driver existed before: the watcher seat looped the tick by hand. The tick stays read-only, and the driver is what acts.

**Why this shape (fixer.md step 17).**
- One library holds the checks and the trap; copying them into each script would put one concept in two places.
- The trap instead of a `|| { echo; exit; }` on every line: the per-line form is #1874's enumerated-cases shape, where the next line written is silent again. `set -x` was also rejected: it buries the one line that matters.
- One cap module for both readers, loaded the way the tick already loads production modules (`_module`). A jq count in the shell and a second count in the tick would hold the concept twice.
- One open-set read for TRAIN and REPLAN, replacing N `.state` reads that were also wrong.
- The relay call sits in a driver, not in the tick, whose contract is "it does NOT act".

**Two deviations from the asks.**
- MERGE-READY, the queue fix and OWED were each asked for "same commit as MERGE-READY". They are separate commits. The MERGE-READY commit already sits behind a merge of origin/main, so folding them in would rewrite history across that merge. Separate commits also made the HANDOFF-AHEAD drop a clean revert.
- `--self-test` is chained rather than given a new flag. `open_pr.sh --self-test` and `update_pr.sh --self-test` run `delivery_row.sh --self-test` (unchanged), then `pr_args.sh --self-test`, which also requires `pr_cap.py --self-test` to report 0 failed. The command that already ran the row checks now runs all of them, with no second flag to remember.

## Head

`ee93af58ae94e93ab9e197b0a66e3d7e291644aa`, on origin/main `07a09406a1cc97076a6f28581f87f313b322a6b6`, which `0670b9cea290` merged in. That merge had one conflict, in `tools/audit/seat/INSTRUMENTS.md`: main's new `policy_reread_check.py` entry and this PR's `pr_args.sh`/`pr_cap.py` entries landed at the same spot. Both were kept, in alphabetical order.

Commits, in order:
- `fb46dfc7`: the failing test, first.
- `0522a2d4`: the fix and the cap.
- `06e41c39`: their INSTRUMENTS entries.
- `c2366b1e`: MERGE-READY and BLOCKED-UNFIXED; `a088da38`: their entry.
- `0670b9ce`: the merge of main.
- `ddb670d8`: the open-set queue fix; `a5cc7961`: its entry.
- `d5207784` and `05744ce7`: HANDOFF-AHEAD and its revert.
- `b31e4a45`: OWED.
- `7fa628e6`: `tick_loop.sh`, with the entries for it and for OWED.
- `ee93af58`: one reader of the approver allowlist. The tick had copied `proof_watch.py`'s two `VERDICT_AUTHORS`/`VERDICT_AUTHOR_ID` patterns, and prepr's agreement lane refused the grammar written twice (`UNREGISTERED ... in tools/audit/seat/orchestrator_tick.py, tools/audit/seat/proof_watch.py`). Both now call `proof_watch.verdict_allowlist`. `python3 tools/audit/seat/proof_watch.py --self-test` prints `34 checks, 0 failed`, the same as at the merge base. `python3 -I tools/policy/agreement_py.py --out $J && node tools/policy/agreement.mjs --py-json $J` prints `RESULT divergent=0 unregistered=0 dead=0 refused=0`.

Every figure below was measured at this head unless it names another commit.

## Mutation proof

**Built-in mutants (`pr_args.sh`).** A line ending in `# mut:<name>` is the predicate one arm pins. The self-test runs each refusal arm twice on copies of the scripts in a scratch repository: once intact, then with that line deleted (`grep -v`). The arm must pass the first time and fail the second, so every run proves its arms are not vacuous. At this head, `bash tools/audit/seat/open_pr.sh --self-test` prints `pr_args self-test: 46 checks, 0 failed`, and all 22 mutant rows say `ok`:

    mut:arity mut:hex mut:body mut:ancestor mut:noref mut:trap   (each on open_pr and update_pr)
    mut:resolve mut:nobody mut:cap mut:capcall mut:capreadrc      (open_pr)
    mut:overcap mut:caprecord mut:capbot                          (open_pr, "refuses at the cap instead")
    mut:prtopic                                                   (update_pr)

**Hand mutants, `orchestrator_tick.py`.** Python lines cannot be dropped one at a time like the shell lines, so each mutant was applied to a committed tree, run with `python3 tools/audit/seat/orchestrator_tick.py --self-test`, and restored with `git checkout --`. Every mutant failed at least one check:

- **Cap.**
  - T1 `flag=n >= cap` -> `False`: "six counted: OPEN-PR CAP: 6/6, flagged".
  - T2 the K>2 test dropped: "three counted PRs touch the coordinator: 3/2, flagged".
  - T3 the unread test dropped: "a diff it cannot read flags the coordinator count as a floor".
  - T4 `counted(prs)` -> `prs`: 2 checks.
  - T5 the call deleted: 6 checks.
- **Verdicts.**
  - V1 the head test dropped from MERGE-READY: "null control: a merge verdict at a stale head prints no MERGE-READY".
  - V2 the same for BLOCKED-UNFIXED: "null control: blocked at a stale head prints no BLOCKED-UNFIXED".
  - V3 `elif not newer` -> `elif True`: "a handoff tip committed after the blocked verdict: no BLOCKED-UNFIXED".
  - V4 the first verdict taken instead of the newest: "the newest verdict wins, and UNSTABLE is merge-ready".
  - V5 both identity keys dropped: "a verdict not from the approver App is ignored". My first V5 dropped only the login and survived, because the id still excludes a forged comment: the filter has two keys.
  - V6 UNREADABLE replaced by `pass`: "comments it cannot read are UNREADABLE, never silence".
  - V7 the CLEAN/UNSTABLE test dropped: "a merge verdict at the head while DIRTY prints none".
- **Queue.**
  - Q1 `stale = []`, which counts every entry unmerged, the old outcome: 5 checks, among them "null control: a queue whose entries are all merged prints no train-not-alive line".
  - Q2 REPLAN's open-set test -> `False`: "REPLAN: a queued PR not OPEN is to prune; an OPEN one is not".
  - Q3 an unread set treated as empty: "an open set it cannot read counts every entry unmerged, and says so".
  - Q4 the no-train line dropped: "and says no train runs with no OPEN entry, unflagged".
- **OWED.**
  - W1 POSTED no longer clears an OWED: 2 checks, among them "null control: an OWED followed by a POSTED prints nothing".
  - W2 the flag dropped: "each OWED with no later POSTED prints OWED: <line>, flagged".
  - W3 only the last OWED per PR kept: this mutant survived at first, so I added "two OWED for one PR with no POSTED print both, each entry", which kills it.
  - W4 a missing log reported UNREADABLE: "no log yet is no OWED and no flag".

**Hand mutants, `tick_loop.sh`** (`bash tools/audit/seat/tick_loop.sh --self-test`):
- L1 relay not called: 2 checks.
- L2 the file-exists guard -> `true`: "null control: no cloud_relay.sh in the tree (before #2419) skips the relay and still ticks".
- L3 two passes under `--once`: 2 checks.
- L4 the interval check disabled: "a non-numeric --interval refuses".
- L5 a failing relay stops the pass: 2 checks.

My first L4 run had no stubs and no `--once` in that arm. The mutant looped the real tick until I stopped it, and it left a zero-byte `tick.txt.part.<pid>` in the state directory, which I removed. That arm now runs `--once` over stubs, so no mutant reaches the network.

## Null control

**Failing first.**
- At `fb46dfc7`, the self-test against main's unchanged scripts printed `pr_args self-test: 31 checks, 17 failed`.
- The final `pr_args.sh` and `pr_cap.py`, run beside the merge base's own `open_pr.sh` and `update_pr.sh`, print `pr_args self-test: 46 checks, 27 failed`. Method: `git archive 07a09406a1cc tools/audit/seat tests/throwaway_git.sh` into a scratch directory, copy those two files in, then run `bash <scratch>/tools/audit/seat/pr_args.sh --self-test`.
- With `a088da38`'s `train()` and `replan()` bodies spliced into this head, the tick prints `orchestrator_tick self-test: 121 checks, 5 failed`, and the 5 are the new queue arms. The original "TRAIN" arm still passed there, because its stub said `"merged"`.

**No over-firing at the head.**
- `open_pr.sh` with the code sha, and `update_pr.sh` with the code sha or `-`, pass every check. Each stops only at the absent push, which names its log, with no argument REFUSE and no STOPPED line.
- Five counted PRs plus a `record:` PR and a dependabot PR: the open passes.
- A merge or blocked verdict at a stale head prints nothing.
- A queue of merged entries prints no train-not-alive line.
- An OWED followed by a POSTED prints nothing.
- With no cloud_relay.sh, the loop still ticks.
- The tick's all-clear null control (zero findings) passes. It reads `os.devnull` as its relay log, never the host's.

## Figures

- `bash tools/audit/seat/open_pr.sh --self-test`: `delivery_row self-test: 5 checks, 0 failed` and `pr_args self-test: 46 checks, 0 failed`.
- `python3 -I tools/audit/seat/pr_cap.py --self-test`: `12 checks, 0 failed`.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `126 checks, 0 failed`. The same command on origin/main's copy prints `100 checks, 0 failed`. The 26 new checks are the blocks `open-PR cap` (6), `verdict levels` (10), `TRAIN queue: OPEN is the only unmerged` (5) and `relay OWED` (5).
- `bash tools/audit/seat/tick_loop.sh --self-test`: `4 checks, 0 failed`.
- Gate scope: `python3 tests/closure.py select --diff 07a09406a1cc --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`, `ref_privacy.py --check` and `python3 -I tests/throwaway_git.py --check` each report 0 refused. The self-tests' origins are plain repositories with no push site, built with `throwaway_git_init` and `throwaway_git_clone`.
- **Merge-tree against the open siblings** (the orchestrator asked for #2406). Command: `git merge-tree --write-tree --name-only HEAD <head>` at this head. Each exited 0 with no conflicted file:
  - #2406 `d1becac2b308`: tree `0898f8c4278d`.
  - #2406's newer `handoff/r10-roster-fastpath` `42a8c31a8540`: tree `09ea004bd77c`.
  - #2419 `b54a2f2e5573`: tree `9535c5461a82`.
  - #2390 `5f6d8fbd7141`: tree `e5291f75ab1f`. The ledger driver noted that it merged #2390's inert-reads entry for the harness-headers test as a set.

  #2406 adds `--no-renames` to the three-dot `diff` argv. This PR's `cap_board` stub keys on `argv[:1] == ["diff"]` and `argv[-1]`, so it reads either form.
- **A live tick.** `python3 tools/audit/seat/orchestrator_tick.py --only TRAIN,PRS` against origin/main `07a09406a1cc`, 2026-10-18T19:45Z. These lines depend on the board, so re-derive them with the same command. It printed:
  - `OPEN-PR CAP: 12/6` and `coordinator.py PRs: 3/2 (#2368, #2391, #2411)`, both flagged;
  - `BLOCKED-UNFIXED` for #2391, #2399 and #2408;
  - `no train running (the queue holds no OPEN entry)`, with no `--queue` given.

  That run still carried HANDOFF-AHEAD, which listed #2368, #2390, #2404, #2406 and #2417. #2368 and #2406 are absent from BLOCKED-UNFIXED, which fits: their handoffs postdate their verdicts.

  Two lines checked by hand:
  - #2399: its newest approver verdict (19:06:26Z) is `Fix review: blocked acf14d8f2267... carry-missing:` at its head, and `handoff/r10-diag-replay`'s tip `f32ad0272f84` was committed earlier, at 16:26:38Z. So BLOCKED-UNFIXED is true.
  - #2404: `handoff/r10-carry-enforce` `6f20f78a3e1d` is not an ancestor of its head `312f31923884` (`merge-base --is-ancestor` rc=1).

  This host has no relay log yet, and the tick says so (`cloud-relay log: none yet`).
- **The class, every seam.** The class is a stop errexit makes without a word. The ERR trap fires on exactly the commands errexit acts on (bash applies the same exceptions to both), and `mut:trap` on each script checks it. The stops outside errexit are explicit `exit`s, enumerated by `grep -n 'exit' tools/audit/seat/open_pr.sh tools/audit/seat/update_pr.sh`:
  - the `--self-test` exits print a tally;
  - the cap's `exit 1` follows `pr_cap.py`'s own line;
  - update_pr's "checked out elsewhere", "no open pull request" and "author wrong" exits each echo first;
  - the push-failure exits are now `pr_push_failed`.

  One seam is outside that rule: a substitution inside a command argument. `git show <ref>:tools/audit/seat/<f>.sh | grep -nF '$(gh'` over both scripts found:
  - at origin/main, update_pr's `N=${PR_N:-$(gh ...)}`, which is an assignment and stops, and the title read inside `ensure_row`'s argument, which is silent;
  - at this head, the same `N=` line and `TTL=$(gh ...)`, both of which stop.

## Unpinned sites

The self-test's own mutant rows pin the `# mut:` lines. The tick's new flags are pinned by its new checks, with T/V/Q/W above as evidence, and `tick_loop.sh` by its 4 checks, with L1-L5. At the previous head, prepr step 6d listed no unpinned site; any it lists now is left to `mutation-autofix`.

## Red checks

none. No check has run on this head yet.

## Forward-carry

- **CI wiring.** No workflow runs the self-tests of `pr_args.sh`, `pr_cap.py`, `tick_loop.sh`, `orchestrator_tick.py` or `delivery_row.sh`. Adding a `governance.yml` step changes `.github/workflows/`, which tvofi owns, so it is for the orchestrator to dispatch as its own group. The step would run `bash tools/audit/seat/open_pr.sh --self-test`, `python3 tools/audit/seat/orchestrator_tick.py --self-test` and `bash tools/audit/seat/tick_loop.sh --self-test`, each with the tally grep the other steps use.
- **Runbook.** `dev/governance/roles/nudge.md` and `orchestrator.md` name `open_pr.sh` without `--over-cap`, and name a watcher seat looping the tick rather than `tick_loop.sh`. Both are policy files (CODEOWNERS `dev/governance/roles/`), so they are left unedited; the INSTRUMENTS.md entries are where this PR records the contract.
- **#2419.** `tick_loop.sh` calls the relay script's `pass` subcommand, but the relay script #2419 adds has `--watch --once` and no `pass` at `b54a2f2e5573`. The orchestrator says that fixer is adding `pass`. Until it lands, the loop will report a non-zero `relay=rc=N` (not measured against that version) and still tick.

## Friction

- fixer.md-step-5: cost: the main checkout's `.git/info/exclude` lists `seat/`, so a new file under `tools/audit/seat/` needs `git add -f`; a plain add prints only a hint.
- fixer.md-step-6: unclear: four scope additions arrived mid-task, one replacing another, each marked "before completing". The body and evidence were re-taken three times; one bundled brief would have saved two re-takes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
