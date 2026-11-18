# Proposal triage, session s12, batch 132 (P403 to P405)

The rolling batch after batch 131. It rules the eight queue lines `s12-stamp-rows-window`, `s12-nightly-supersede`, `s12-stamp-flush-fast-path`, `s12-cancel-superseded-widen`, `s12-stamp-freeze-train`, `s12-red-checks-autolist`, `s12-stale-head-note` and `s12-stamp-flush-dispatch-cost`. The orchestrator merged them into three rulings:
- **P403** takes the stamp trio: rows-window, flush-fast-path and freeze-train.
- **P404** takes cancel-superseded-widen, with nightly-supersede and stamp-flush-dispatch-cost folded into it.
- **P405** takes red-checks-autolist together with stale-head-note.

Facts were read at origin/main `630bf533d`, at the roster branch `407404d39`, through the REST API (about 30 calls), and in the orchestration logs. The logs are host-local, so another seat can re-run those commands only on the host that holds them.

The bar is the owner's ruling of 2026-11-07. An instrument change ranks by the wall-clock it saves over the rest of the round, which closes about 2026-11-13. A change that saves 12 h or more is in the production tier. A CI-machinery bug that blocks every merge is in the hotfix tier.

## P403: the stamp trio (queue lines s12-stamp-rows-window, s12-stamp-flush-fast-path, s12-stamp-freeze-train)

Verdict: ACCEPT narrowed. Only the rows-window part passes.
- **rows-window: ACCEPT, changed.** The fix is not "pin a main sha at the start of the run". The flush moves the checkout on purpose. Instead, the disposition instrument enumerates at the one head that the stamp's rule 4 reads.
- **freeze-train: REJECT.**
- **flush-fast-path: (a), where the stamp writes the rows itself, is REJECTED. (b), a light CI path for record-only heads, is DEFERRED** until P404's change has been measured.

The destination is a new fly-in group, R10-FLY-STAMP-FLUSH-COST. It is shared with P404 and specified below. It is not taken on the >10 % exemption.

Source: the orchestrator's queue lines, 2026-11-07, about 11:00Z to 12:00Z.

Instances:
- **The v7.1.5 stamp, in three runs** (orchestration logs `s12/stamp-715.log`, `stamp-715b.log` and `stamp-715c.log`):
  - Run 1 printed `record flush: no record merge landed within 7200s of 2 dispatch(es)`. That is batch 131's train-hold case, P402. It was then refused with `stamp refused (rule rows): the disposition instrument lists #3271 without a row, but rule 4's window does not name that pull request; the two enumerations disagree`.
  - Run 2 flushed `#3281` after 1 dispatch. It was then refused at rule 4 on `#3250, #3251, #3259, #3260`, merges that run 1's window did not yet hold.
  - Run 3 flushed `#3282` after 2 dispatches.
  - The first dispatch of the stamp went out at 05:52Z (run 42344537787, below). At 12:00Z v7.1.5 is still untagged: `git tag -l v7.1.5` prints nothing.
- **Why rows refused (origin/main `tools/release/stamp.py`):**
  - Rule 4 reads `window_log_args(last_tag)`, which is `<tag>..HEAD` (line 476, called at line 2698).
  - `disposition_gate` (line 2160, called at line 2715) runs `tests/delivery_status.py --require-rows --since <tag>`. That reads `<tag>..origin/main` (`tests/delivery_status.py` line 557).
  - The flush's `record_merges_since` runs `git fetch origin` on every poll (line 2386). So after a flush that times out, origin/main is ahead of the HEAD the stamp stands on. A merge in that gap makes the two enumerations disagree by construction.
  - After a timeout, `deferred` is set, and `rows_gate_decision` gets `allow_rowless=... or bool(deferred)` (line 2744). So the only thing that stopped run 1 was the cross-check at lines 2730 and 2735.
  - The tag closes `<tag>..HEAD`, so HEAD is the right sha for both enumerations. A merge past HEAD belongs to the next window.
- **The rule on the instance:** with both enumerations at HEAD, run 1's rowless list holds no `#3271`, and the cross-check passes. Run 1 had already passed rule 4, so it goes on to the rows gate with `deferred` set.
  - The stamp would have finished at about 07:55Z, not after the run 2 and run 3 re-runs.
  - That is more than 4 h of stamp wall-clock on 11-07, measured to 12:00Z. The rule-2 gate wait still applies.
- **freeze-train, measured:**
  - Record PR #3281 opened at 09:21:42Z. Its first code run, 42359420576, ran from 09:21Z and was cancelled at 10:01Z, when the record beat re-pushed the head from `78e05a3b` to `896b110b`.
  - Its second set of runs ran from 10:00Z to 10:30Z, and it merged at 10:31:17Z. That costs 40 min, once.
  - Main took train pushes at 09:40Z, 09:49Z and 09:59Z, and only the last re-push cancelled the CI. So the queue line's "each merge" is one re-push in 40 min.
  - Commands: `gh api repos/tvofi/heatpump_optimizer/actions/runs?branch=record/autofix`, and the Nightly listing below.
- **fast-path, measured:**
  - The two flushes that landed took 70 min (#3281: 09:21Z to 10:31Z) and 35 min (#3282: 11:16:02Z to 11:50:54Z), by `gh api repos/tvofi/heatpump_optimizer/pulls/<n>`.
  - #3282's three runs were all running inside 11:16Z to 11:49Z, so their CI was about 33 min.
  - The record PR's runs queue behind the stamp's own Nightly lanes, which is P404. Until that is fixed, a light CI path cannot be measured apart from it.

Cost:
- **rows-window:**
  - `tests/delivery_status.py` gets a `--head <rev>` argument, defaulting to `origin/main` so its other callers are unchanged, used in the `span` at line 557. That is about 5 lines.
  - `disposition_gate` and `disposition_gate_argv` pass the stamp's `head`, about 4 lines.
  - A self-test arm in `stamp.py`'s rows block: origin/main is one record merge ahead of HEAD, the run is not refused as rows, and the window is cross-checked at HEAD. A mutant that drops `--head` must refuse as rows. The null control: HEAD equal to origin/main behaves exactly as today.
  - A `delivery_status.py` self-test arm for `--head`.
  - Both files are code-owned (`.github/CODEOWNERS`: `/tools/release/` and `/tests/delivery_status.py`).
  - `stamp.py` had 7 commits on origin/main since 2026-10-24, and `delivery_status.py` had 1 (`git log --since=2026-10-24 --format=%h origin/main -- <file> | wc -l`). Neither is a `policy_lint.mjs --budgets` row. No `tests/structure_budgets.json` metric reads `tools/` or `tests/`.
- **Benefit and tier:**
  - On the 11-07 instance the saving is more than 4 h.
  - The gap exists after every flush that times out, and after any merge between the flush's last checkout move and rule 5.
  - With P402's fix the timeouts become rarer. Estimate 1 or 2 more instances in the 6 to 9 stamps left this round. The stamp rate is v7.1.3 and v7.1.4 on 11-06 and v7.1.5 on 11-07, from `git for-each-ref --sort=creatordate refs/tags/v7*`. At 2 to 4 h each, that is **2 to 8 h**.
  - **Tier: instrument.**
- **freeze-train, the binding cost:**
  - Holding the train for the flush stalls every merge for 35 to 120 min per stamp, which is 4 to 18 h of train time over the round. That saves one CI restart, 40 min once.
  - It would also add a second cross-tool hold beside the train-hold that P402 now names.
- **fast-path (a), the binding cost:**
  - The stamp's tag push is `main-protect-checks`'s only bypass (`stamp.py`, the rule-5 comment). Writing delivery rows into the stamp commit lands rows that no `pr-contract` or `delivery-status` run has checked, so it widens what the deploy key writes unchecked.
  - That widens governance surface for at most 35 to 70 min per stamp, and it is the owner's question, not an instrument fix.
- **fast-path (b), what would change it:**
  - Measure the flush wait over the 3 stamps after R10-FLY-STAMP-FLUSH-COST lands. If the p50 from the record PR's open to its merge is still above 45 min, re-file (b) with those figures. The record PR's own CI was 33 min on #3282.
  - The owner is R10-CI-SLIM's seam (`ci.yml`, `tools/ci/prelude.py`), which is done now.

Binding: the shared new group R10-FLY-STAMP-FLUSH-COST is specified under P404's `Binding:`. Item 2 of its brief is this ruling's.

## P404: cancel-superseded-widen, with nightly-supersede and stamp-flush-dispatch-cost folded in (queue lines s12-cancel-superseded-widen, s12-nightly-supersede, s12-stamp-flush-dispatch-cost)

Verdict: ACCEPT changed. The runners are held because the stamp's flush dispatches the whole of Nightly to run a beat that takes one minute.
- **The fix: dispatch the beat alone.** `nightly.yml` gets a `workflow_dispatch` input that skips the heavy lanes, and `stamp.py` sends it. This is s12-stamp-flush-dispatch-cost's first option, the nightly.yml input. Its second option, a separate record workflow, is not taken: the input moves no job and keeps `record-autofix`'s `environment: record-writer` and its `tests/entities.py` pins where they are.
- **s12-stamp-flush-dispatch-cost's other arm, "never re-dispatch while its own dispatch is still running": REJECT.** Once the dispatch is beat-only, the run lasts as long as `record-autofix`, which has `timeout-minutes: 10` (line 591). That is under `FLUSH_REDISPATCH_S = 900`, so a re-dispatch can no longer overlap a running one of its own. A run-status read would add REST calls on every poll and guard against a case that cannot happen after the change.
- **cancel_superseded.py arm 1, cancelling superseded Nightly dispatches: REJECT.**
- **arm 2, duplicate Gate sweeps: REJECT.**
- **nightly.yml `concurrency` with `cancel-in-progress`: REJECT.**

The destination is the new fly-in group R10-FLY-STAMP-FLUSH-COST, below. It is not taken on the >10 % exemption.

Source: the orchestrator's queue lines, 2026-11-07, and the owner's hand-cancel order that the queue line records. `s12-stamp-flush-dispatch-cost` was appended at about 12:10Z as queue line 80. It says each dispatch held "up to four runners". The jobs read below show 6 long jobs per dispatch: `mutation-nightly`, four shards and `slow`.

Instances:
- **Nightly runs on 11-07,** by `gh api "repos/tvofi/heatpump_optimizer/actions/workflows/nightly.yml/runs?created=>=2026-11-06T18:00:00Z&per_page=60"`:
  - There are 7 `workflow_dispatch` runs, all with actor `tvofi`: 42344537787 and 42346251204 at `be813ecd` (05:52Z, 06:16Z), 42353878060 at `0e9c508c` (08:04Z), 42357667261 at `62bcca76` (08:57Z), 42364230438 at `c9c88336` (10:30Z), and 42367391498 and 42369836867 at `08fd676e` (11:15Z, 11:50Z).
  - The first four were hand-cancelled at 09:38Z to 09:43Z. The last three were `in_progress` at 12:05Z.
  - The three stamp logs account for 5 of them: 2, 1 and 2 dispatches.
  - Each push run on main finished in about 1 min, because every heavy job has `if: github.event_name != 'push'`.
- **What one dispatch costs,** by `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs?per_page=100`, summing started-to-completed minutes per job, with running jobs counted to 12:05Z:
  - **Jobs and lines:** each dispatch starts `mutation-nightly`, four `mutation-ledger` shards, `slow` and two `nightly-ha` arms, which are lines 51, 157, 420 and 512 of `.github/workflows/nightly.yml`. The one job a flush needs is `record-autofix` (line 583), and it ran in 1 min in every run.
  - **Runner-minutes:** 42344537787 took 1053 runner-min, a full run. The cancelled runs 42346251204, 42353878060 and 42357667261 took 943, 410 and 187. The running 42364230438, 42367391498 and 42369836867 have taken 516, 284 and 94 so far. The 00:47Z scheduled run, 42320317707, took 903.
  - **Total:** that is 3487 runner-min, or 58 runner-h, by noon. 7 of those minutes did the flush's work.
  - **Concurrency:** each dispatch holds 6 runners for 2 to 3.5 h, and three were doing so at 12:05Z.
- **The code admits it.** `stamp.py` line 2335 says "each dispatch also runs every nightly lane". `dispatch_record_beat` (line 2365) posts `{"ref": "main"}` with no inputs.
- **Cancelling destroys finished work.** 42344537787's lanes all concluded `success`, but its `mutation-ledger-push` concluded `cancelled` under the hand cancel. About 1000 runner-min of ledger shards were finished and never landed. The other three cancelled runs lost their shards the same way.
- **The rule on the instances:**
  - With `lanes=beat` on the stamp's dispatches, the 5 stamp dispatches run `record-autofix` alone, about 5 runner-min against roughly 3000. None holds a runner past its 10-min timeout, and no hand cancel is owed.
  - Hand dispatches keep the default and run every lane, as today.
  - R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT measures its change "on a workflow_dispatch nightly", so its probe is unaffected.
- **arm 2, the Gate sweeps:**
  - On 11-07, 100 `gate-sweep.yml` runs took p50 0.5 min, p90 11.1 min and max 22.0 min across 10 main shas, with up to 30 at one sha. This is by `gh api "repos/tvofi/heatpump_optimizer/actions/workflows/gate-sweep.yml/runs?created=>=2026-11-07T00:00:00Z&per_page=100"`, using `updated_at` minus `created_at`.
  - A sweep job has `timeout-minutes: 15`, so the queue line's "up to ~3 h" is the Nightly runs, not the sweeps.
- **`nightly-status` is unaffected.** `tests/nightly_status.py` grades only `schedule` runs (its docstring, lines 2 and 39). A beat-only dispatch therefore changes no grade.

Cost:
- **The code:**
  - In `nightly.yml`, `on.workflow_dispatch.inputs.lanes` is a choice of `all` or `beat`, with the default `all`. About 6 lines.
  - `&& inputs.lanes != 'beat'` is added to the `if:` of `mutation-nightly`, `mutation-ledger`, `mutation-ledger-push`, `slow` and `nightly-ha`, five lines. On `schedule` and `push`, `inputs.lanes` is empty, so those events are unchanged.
  - In `stamp.py`, `dispatch_record_beat` posts `inputs: {lanes: beat}`, one line.
  - A self-test arm asserts the payload, with a mutant that drops the input.
  - `tests/entities.py` evaluates nightly lanes' `if:`, from line 26984. The fixer keeps those pins true and adds one: every heavy job skips on `lanes=beat`, and `record-autofix` does not.
- **Ownership and overlap:**
  - Both files are code-owned (`/.github/workflows/`, `/tools/release/`).
  - `nightly.yml` had 8 commits since 2026-10-24.
  - R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT (PR 3269, in progress) edits the `mutation-ledger` drain steps of the same file. This change touches only the five `if:` lines and the trigger block, a distinct seam, so it is admitted as overlap by seam.
  - No `--budgets` row reads either file.
- **Benefit and tier:**
  - 6 to 9 stamps are left, at 1 or 2 flush dispatches each, which is 8 to 15 dispatches. At about 950 runner-min each, that frees **125 to 240 runner-h**.
  - The concurrency peak that the R10-FLY-CANCEL-SWEEP carry measured is 40 jobs. When that limit binds, the freed time is **3 to 6 h** of fleet-wide queue time. On top of that, the stamp's own record PR no longer queues behind the lanes of its own dispatch.
  - That totals **4 to 8 h**, so **tier: instrument**.
  - Shared with P403's 2 to 8 h, the group saves **6 to 16 h, central 10 h**. That is the top of the instrument tier, below the 12 h production line on the central estimate.
- **arm 1, the binding cost:**
  - Once beat dispatches skip the lanes, a full-lane Nightly is a deliberate run: the schedule, or a hand `gh workflow run nightly.yml`.
  - Cancelling one at a superseded sha discards finished `mutation-ledger` shards before `mutation-ledger-push` lands them. That is ~1000 runner-min lost on 42344537787 alone.
  - It also adds a main-ref cancel arm to a code-owned tool whose `never_cancel` keeps main by design (R10-FLY-CANCEL-SWEEP item 2).
- **arm 2, the binding cost:** the sweeps are measured at p50 0.5 min and bounded at 15 min. Cancelling duplicates saves minutes and touches the gate's re-judge path. That path is R10-RCA-GATE-BUSY-DEFER-2's seam: its carry already asks why the sweep did not re-judge a deferring gate. No carry is sent there, because this measurement is not a finding of that race.
- **`cancel-in-progress` per branch, the binding cost:** every event on main shares the one branch. A beat dispatch would cancel the scheduled run, and a hand dispatch would cancel a probe run.

Binding:
- New fly-in group R10-FLY-STAMP-FLUSH-COST: lane F, kind instrument, class instrument, size S.
  - Files: `tools/release/stamp.py`, `.github/workflows/nightly.yml`, `tests/delivery_status.py` and `tests/entities.py`.
  - Fixer sonnet, reviewer opus, effort medium.
  - It runs after R10-FLY-STAMP-FLUSH-HOLD, because both edit `stamp.py`'s flush and that group's PR 3280 is open.
  - Overlap with R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT is admitted by seam.
  - Code-owned: it merges on tvofi's approving review, or under a mandate in force.
- The brief text: `From triage batch 132 (triage: dev/programme/triage/s6-batch132.md#P404 and #P403 at <roster sha>), savings estimate 6 to 16 h (central 10 h; instrument tier). (1) Beat-only dispatch (P404): every stamp record-flush dispatch of nightly.yml runs all nightly lanes (mutation-nightly, four mutation-ledger shards, slow, two nightly-ha), about 950 runner-min, to run the one-minute record-autofix job; on 2026-11-07 seven dispatches held 58 runner-h by noon and four were hand-cancelled, losing finished ledger shards. Add nightly.yml on.workflow_dispatch.inputs.lanes (choice all or beat, default all) and append "&& inputs.lanes != 'beat'" to the if of mutation-nightly, mutation-ledger, mutation-ledger-push, slow and nightly-ha; record-autofix keeps its if. stamp.py dispatch_record_beat posts inputs lanes=beat. Keep tests/entities.py pins on nightly lanes true and add one: every heavy job skips on lanes=beat and record-autofix does not. Self-test arm: the dispatch payload carries lanes=beat; a mutant dropping it fails; null control: a dispatch with no input (a hand probe) runs every lane, and schedule and push evaluate as today. Measure before and after on one beat-only dispatch: its jobs and runner-minutes by the runs jobs API. Name the hand form (gh workflow run nightly.yml -f lanes=beat) where stamp.py documents the flush. (2) One window (P403): rule 4 enumerates tag..HEAD (window_log_args) but disposition_gate runs tests/delivery_status.py over tag..origin/main, and the flush fetches origin every poll, so after a flush timeout any merge past HEAD makes rule rows refuse (v7.1.5 run 1, #3271). Add delivery_status.py --head REV (default origin/main) used in its span, and pass the stamp head from disposition_gate. Self-test arms: origin/main one record merge ahead of HEAD is not refused as rows; a mutant dropping --head refuses as rows; null control: HEAD equal to origin/main is unchanged; delivery_status.py --head selects its window. No cancel_superseded.py change, no train hold, no rows written by the stamp.`
- The fixer re-measures the line numbers and the runner-minutes at its own base and does not carry them.

## P405: red-checks-autolist with stale-head-note (queue lines s12-red-checks-autolist, s12-stale-head-note)

Verdict: ACCEPT narrowed. Only the head-note part passes.
- **head-note: ACCEPT, changed.** The packet's `head-note` rule takes `pr-contract`'s own answer, `autofixChain` included, instead of a substring test of its own. `update_pr` and recarry already prefix the new head.
- **red-checks-autolist: REJECT.** The handoff read it asks for is already in the tree. Every measured instance concluded after the handoff, so no handoff-time read can see it.

The destination is a carry on R10-DISPATCH-AT-HANDOFF (carries-open, PR 3249 merged 2026-11-07T08:55:42Z), which owns `tools/audit/seat/review_packet.py`. It is not taken on the >10 % exemption.

Source: the orchestrator's queue lines, 2026-11-07.

Instances:
- **The body-only fires of 11-07** (orchestration log `s10/gantt/fired-recent.txt`):
  - There are 13 fires whose names end in `-body`. Their briefs are the `PROMPT.md` files at the commits that `s11/f-<name>.json` names.
  - Eight of the briefs were read. Each one's `THE REFUSAL` line classifies it:
    - **Class A, `governance / instrument-self-tests` `cancelled` at its 30-min timeout:** 3 of them. These are f-3244-body2 at `4ee05dcd`, f-3265-body3 at `c7c5cef5` and f-3267-body at `a7223767`, each refused by the review packet's `red-unanswered`.
    - **Autofix chain, refused as `head-note`:** 2 of them. f-3273-body at `fe40be98` is `ci: pin killed mutants` on top of `a46e4d02`. f-3278-body at `4839ac95` is `ci: merge main` on top of `fbf55e8f`.
    - **Real reds that pr-contract or prepr refused:** 3 of them. f-3268-body is `tests / mutation`, failed at `d95f6b7a`. f-3262-body is `tests / nightly-status`, which the diff's own inputs touch. f-3244-body is the literal check name of `code-scanning alert 50`.
  - A third head-note instance is #3184, on 2026-11-04. `git log -3 c34999c1d` shows `ci: pin killed mutants` (github-actions[bot]) on top of `913e74e87 record: the delivery row for #3184`.
- **The handoff read exists.** `body_push.sh` line 153 passes `--pr-branch fix/<topic>` when origin holds it. `prepr.sh --body-check` then runs `reds_arm` (line 1761) over every commit in `<base>..origin/fix/<topic>` (`ancestry_reds`, P351), and it refuses on an unnamed failure.
  - The three real-red instances were each refused by that arm or by pr-contract before review.
  - The three class-A ones concluded about 30 min after the head they were on was pushed, which is after any handoff.
- **Why class A refuses the packet and not the contract:**
  - `review_packet.py` line 134 counts `cancelled`, `timed_out`, `action_required` and `startup_failure` as red at the head.
  - `prepr.sh` `REDS_JQ` (line 1337) and `policy_lint.mjs` `failingCheckNames` count only `failure`.
  - The class itself is R10-HOTFIX-SELFTEST-TIMEOUT's (PR 3275, in progress), and its fix removes it. Whether a cancelled required job is a red is already a carry on R10-HOTFIX-GATE-BUSY-DEFER, the #3262 one.
- **The head-note mismatch:**
  - `review_packet.py` line 204 has `head_note_ok = head in section(body, "Head")`: the full sha, and no autofix chain.
  - `policy_lint.mjs`'s pr-body check (line 6975) accepts a 7-character name, and from line 6978 it accepts an `autofixChain` on top of a named head. That chain is a bot-authored commit with an exact autofix message and the expected paths, or git's own merge of main.
- **The rule on both 11-07 instances, run here.** Each live body was rebuilt as the kept body (`handoff-body/r10-rca-gate-busy-defer-2` `27a26d64`, `handoff-body/r10-clone-2238` `71254a7b`) with `update_pr.sh`'s body-only note prefixed through `tools/pr/head_note.py` `prefix`. Then `node tools/policy/policy_lint.mjs --pr-body <body> --head <head>` was run on each:
  - #3278 printed `HEAD: ## Head names fbf55e8; accepted autofix commit(s) on top of it: 4839ac9 (ci: merge main)`.
  - #3273 printed `... names a46e4d0; accepted autofix commit(s) on top of it: fe40be9 (ci: pin killed mutants)`.
  - `review_packet.head_note_ok` on the same two bodies returned `False` both times.
  - **Null controls:** on #3278's body, the seat commit `fccc86af3` as the head gives `Head does not name fccc86a ... is not authored and committed as github-actions[bot]`. On #3273's body, `7dba286df` gives 1 head error.
  - **The change:** the packet agrees with the contract on all four, so the two fixer fires and their re-dispatch waits are not owed.

Cost:
- **The code:**
  - `head_note_ok` delegates to `policy_lint.mjs --pr-body --head <head>`. It refuses only on the contract's own `` `## Head` does not name `` error. `review_packet.py` already runs that tool in `unanswered_reds`, so it adds no new tool.
  - About 15 lines, with self-test arms in the existing block (line 674): a body naming a parent under a planted `ci: merge main` or `ci: pin killed mutants` commit passes; a seat-authored commit on top refuses; a mutant restoring the substring test refuses the chain case.
  - The null control: a body that names the head passes, as today.
- **Ownership and size:**
  - `review_packet.py` had 15 commits since 2026-10-24 and is 1057 lines. It is not a `--budgets` row and not in `HOT_FILES`.
  - An S carry, sonnet, one review.
- **Benefit and tier:**
  - Each head-note instance cost a sonnet body-only fire, 4 to 7 min of fixer time: f-3267-body was fired at 10:16:20Z and its body was at 10:20:45Z, and f-3244-body2 was fired at 07:40:16Z and its body was at 07:47:09Z. On top of that come the update, the pr-contract re-run and the re-dispatch, about 30 to 60 min on that PR's path.
  - At 3 instances in 11-04 to 11-07, two of them on 11-07, expect 4 to 10 in the 6 days left. That is **2 to 10 h, central 4 h. Tier: instrument.**
- **red-checks-autolist, the binding cost:**
  - Its handoff read is `ancestry_reds`, and it is on main.
  - Its measured instances are class A, which concludes after the handoff and has its own fix in flight, or real reds whose answer needs a seat's judgement: a class and a cheaper detector.
  - Pre-filling those answers by script would write the text that `fix-review.md` step 11 makes the fixer's own, and it saves nothing a handoff read can see.
  - It is not a barrier for an audit class. The three instances are three distinct causes, and the class-A cause has its owner.

Binding:
- Carry for R10-DISPATCH-AT-HANDOFF. The carry text: `From triage batch 132 (triage: dev/programme/triage/s6-batch132.md#P405 at <roster sha>), savings estimate 2 to 10 h (central 4 h; instrument tier): review_packet.py head_note_ok is a substring test of the full head in ## Head, while pr-contract (policy_lint.mjs pr-body, the autofixChain walk) accepts a 7-character name and an autofix chain (bot-authored ci: merge main, ci: pin killed mutants, ci: re-record closures, ci: drop inherited claims) on top of a named head. The packet refused #3278 at 4839ac95 and #3273 at fe40be98 (and #3184 at c34999c1 on 11-04) where the contract accepts, and each cost a body-only fixer. Make head-note ask policy_lint.mjs --pr-body --head <head> and refuse only on its own ## Head does not name error, so one rule decides. Self-test arms in the existing block: a body naming the parent of a planted bot merge-main or pin commit passes; a seat-authored commit on top refuses; a mutant restoring the substring test refuses the chain case; null control: a body naming the head passes. No change to red-unanswered and no handoff auto-fill of ## Red checks.`
