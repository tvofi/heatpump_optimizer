# Proposal triage, session s13, batch 134 (P419 onward)

The rolling batch after batch 133. It rules queue lines 96 and 97 of the orchestrator's triage queue (`s12-cloud-dispatch-rulings-preamble`, `s12-outside-first-priority`), and three items batch 133 left with the orchestrator and no roster op:
- P410's move of the roster drain onto `beat_jobs.py`'s `roster-drain` row (P421);
- P406 cause C, #3252's `codescan_wait` fail-closed (P422);
- P415's measurement (P423).

Facts were read at origin/main `53273de4d`, at the roster branch `badbae55a`, through the REST API, and in the orchestration logs. The logs are host-local, so another seat can re-run those commands only on the host that holds them.

The bar is the owner's ruling of 2026-11-05 (a measured improvement; over 10 % for a new mechanism). An owner directive keeps its route, and this seat rules only on its form and destination. A defect instance sent to its owning group is not a proposal: this seat rules only on the destination.

## P419: owner rulings reach a group-dispatched seat only through a session-local wrapper (queue line s12-cloud-dispatch-rulings-preamble)

Verdict: ACCEPT changed. A new S group, R10-FLY-DISPATCH-RULINGS, owns the rendered prompt of `tools/audit/seat/cloud_dispatch.py`. It takes two carries:
- **the queue line's `--preamble FILE` flag**, which the tree owes anyway: decision 0013 puts reusable instruments in the tree, and today the preamble is added by a scratch wrapper;
- **R10-TICK-LEVELS carry 17**, moved here. The tracked fixer prompt still tells every fixer to re-merge a moved main. That contradicts the owner's ruling of 2026-11-07 and `fixer.md` itself, and it is the reason the wrapper exists.

A tracked rulings file under `dev/governance/` is rejected. Each ruling has its own policy home, and a second copy would drift from it. The preamble is the interim channel that runs until that home lands.

Source: the orchestrator's queue line of 2026-11-07T19:22:24Z, and the 19:40Z note in the s12 resume log (host-local `s12/RESUME-s12.md`).

Instances:
- **The tracked prompt contradicts the policy it points at.** `tools/audit/seat/cloud_dispatch.py` line 247 renders, for every fixer: "when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` ...". `dev/governance/roles/fixer.md` lines 93 to 95 at `53273de4d` say to merge `origin/main` only when `git merge-tree --write-tree origin/main HEAD` reports a conflict or the head is `DIRTY`. The owner's ruling of 2026-11-07 says the same. R10-TICK-LEVELS carry 17 measures the cost: on f-3262-r6, three of four 12-minute `prepr.sh` runs were caused only by main moving.
- **The group path cannot take a preamble.** `GROUP_FLAGS` (line 1118) refuses `--brief` on `--group` ("the roster gives the brief"), and `dispatch_group` renders `group_brief(group)` alone (lines 412 and 504). So the only way in for a ruling is the scratch wrapper `s12/seat-dispatch/mint-group-brief.sh` (host-local). It concatenates `s11/owner-ruling-para.txt`, `s11/owner-ruling-nonreq-para.txt` and the group brief, and mints through a second scratch script.
- **Three rulings are in force, and each has a home:**
  - no re-merge: R10-TICK-LEVELS carry 17, which this ruling moves; `fixer.md` already agrees;
  - non-required reds never block: R10-HOTFIX-NONREQUIRED-REDS, not started;
  - fixers kill their own diff mutants: R10-FIXER-MD-SPELLING-CORPUS carry 0, not started, with a measure-first condition.
  None has landed, so the preamble carries all three until each does.
- **The slips.** The s12 resume log records the wrapper being missed twice: at 19:16Z, "SLIP (repeat): retry loops snapshot the brief at start, so the owner-ruling paragraphs missed p-3290-r3, which fired anyway"; and a mint-time read-back of the paragraph was added as a hold for R10-CI-SELFTEST-SCOPE (host-local `s12/dispatch-seat/STATE-HANDOFF.md` line 12).
- **The rule on each instance:**
  - With carry 17 built, the rendered fixer text says what `fixer.md` says, and the wrapper's no-remerge paragraph has nothing left to override.
  - With `--preamble`, p-3290-r3's prompt holds the paragraphs: they are read at render time from the file the flag names, not from a loop's snapshot.
  - The null control is a dispatch with no `--preamble`: it renders byte-identically to today's.

Cost:
- **The flag:**
  - `--preamble FILE`, repeatable (`action="append"`), accepted on both the flag path and the `--group` path.
  - Each file is rendered after the seat line and setup and before `Role:`, under one heading: "Owner rulings in force (where they differ, they outrank the role text and the brief)".
  - A file that is missing, empty or holds a host path refuses, with no publish. The host-path check is the one `_publish` already applies to the ref name, applied to the text.
  - About 25 lines plus self-test arms.
- **Carry 17,** as the carry states it: about 10 lines of prompt text, plus the reviewer arm and the `fix-review.md` sentence.
- **Ownership:** `fix-review.md` is policy and code-owned, so it merges under the mandate in force or on tvofi's review. `cloud_dispatch.py` is 1200 lines and is owned by no live group but R10-TICK-LEVELS. It is there only because carry 17 was added; its brief names one seam, `orchestrator_tick.py`.
- No `--budgets` row reads either file.
- **The move.** It takes cloud_dispatch.py back out of R10-TICK-LEVELS, an M group with 18 carries, where carry 17 sits last.

Binding:
- **New group** R10-FLY-DISPATCH-RULINGS (S, sonnet, opus reviewer), with files `tools/audit/seat/cloud_dispatch.py`, `tools/audit/seat/instruments/cloud_dispatch.py.md` and `dev/governance/roles/fix-review.md`. Its brief:
  "From triage batch 134 (triage: dev/programme/triage/s6-batch134.md#P419 at ROSTERSHA). Owner rulings reach a group-dispatched seat only through a session-local wrapper, because cloud_dispatch.py --group renders the roster brief alone and GROUP_FLAGS refuses --brief there. Add --preamble FILE, repeatable, on the flag and --group paths. Each file is rendered after the seat line and setup and before Role:, under one heading: Owner rulings in force (where they differ, they outrank the role text and the brief). A missing, empty or host-path file refuses with no publish. Self-test arms: two preamble files both appear in order in the published prompt at the pinned commit; a host-path preamble refuses and publishes nothing; null control: no --preamble renders byte-identically to the base; a mutant dropping the preamble on the --group path fails the first arm. Then build carry 0, moved from R10-TICK-LEVELS. Instrument doc tools/audit/seat/instruments/cloud_dispatch.py.md gains the flag. fix-review.md is code-owned: it merges under the mandate in force or on tvofi review."
- **Its carry 0** is R10-TICK-LEVELS carry 17's text, verbatim, with this prefix: "Moved from R10-TICK-LEVELS carry 17 (triage: dev/programme/triage/s6-batch134.md#P419 at ROSTERSHA): ".
- **Then** mark R10-TICK-LEVELS carry 17 `moved R10-FLY-DISPATCH-RULINGS`, by match, and drop `tools/audit/seat/cloud_dispatch.py` from R10-TICK-LEVELS's files.
- **Orchestrator, no roster op:** until the group merges, mint group fixers with the wrapper as today. After it merges, mint with `--preamble` and retire `mint-group-brief.sh`. Remove each ruling's paragraph from the preamble file once its home group merges.

## P420: outside submissions first, mechanically (queue line s12-outside-first-priority)

Verdict: ACCEPT changed, on form, because this is an owner directive. One roster field, read by the three orderers that exist. The queue line's three-valued enumeration and its policy sentence are rejected.
- **The field.** A group gets `"source": "outside"`; an absent field means internal. A `roster_lib.is_outside(group)` helper reads it, and a `roster_lib.group_for_pr` fallback maps a pull request to its group through `resume.pr`, for fork heads whose branch is not ours.
- **The three readers:**
  - `replan.py` `dispatch_tier`;
  - `open_driver.py` `default_class` and `order`;
  - `merge_train.py`'s spool drain key.
  Dispatch follows `replan.py`'s slot order, so a fourth reader is not owed.
- **Rejected: the `outside|owner|audit` enumeration.** The owner ranks owner and audit work equally, so two of its three values change nothing.
- **Rejected: the `orchestrator.md` sentence.** No policy file states the queue order today: it lives in `replan.py`'s tier docstring (lines 380 to 384). A sentence would be a second copy, policy-corpus growth under the ratchet, and a collision with #3262, which edits `orchestrator.md`.
- **The new group.** It is R10-OUTSIDE-FIRST. It is not a carry to R10-OUTSIDE-INTAKE, whose files (`state_docs.py`, two roles) share nothing with these and whose part 2 already waits on #3262.

Source: the owner's ruling, tvofi 2026-11-07T19:40Z, verbatim: "all accepted outside issues or contributions should be prioritized higher than audit or owner submitted ones unless i call the owner one a hotfix". Queue line 97.

Instances:
- **The outside groups on the roster at `badbae55a`** (author by `gh api repos/tvofi/heatpump_optimizer/issues/<n> --jq .user.login`):
  - R10-COMBI-TANK: issue 3225, Bankaifan; PR 3268, adopted by hpo-author;
  - R10-GENERIC-HEAT-CURVE: PR 3284, Bankaifan;
  - R10-GENERIC-HEAT-CURVE-PERSISTENT: the persistent kind of PR 3284;
  - R10-INPUT-REAPPEAR: PR 3292, Bankaifan, a fork head.
  None of the 381 groups carries any field that names an outside source. The roster's key set has no `source`, and `priority` is set on two groups and read by no tool (`git grep -n '"priority"' origin/main -- tools/plan tools/audit/seat/roster_lib.py` is empty).
- **The three orderers today:**
  - **`replan.py` `dispatch_tier`** (line 390). Tier 1 is main. Tier 2 is the critical path, a `kind` "bug", or a HOTFIX-named production group. Tier 3 is production, or an instrument saving 12 h or more. Tier 4 is everything else. An outside group lands in tier 3 or 4 unless it is on the critical path.
  - **`open_driver.py` `default_class`** (line 111). Critical is 0, `R10-HOTFIX-*` is 1, record topics are 2, the rest are 3. `order` keeps critical first, whatever `open-priority.txt` says.
  - **`merge_train.py` line 3261.** It drains `--priority` or `--front` entries first, then the critical path, then arrival order.
- **The rule on each instance.** The order becomes: main, then hotfix, then outside, then everything else as today.
  - Hotfix means an owner-called hotfix: an `R10-HOTFIX-*` name, or `kind` "bug".
  - Main stays first, because a red main blocks the outside merge too.
  - One consequence the ruling forces: hotfix now ranks above the critical path, where today the two share a tier (replan) or the critical path leads (open_driver). Outside must sit above the critical path and below a hotfix, so the two can no longer be equal.
  - Under the new order, R10-INPUT-REAPPEAR and R10-COMBI-TANK dispatch, open and drain ahead of every non-hotfix audit group, the critical path's included. R10-HOTFIX-NONREQUIRED-REDS stays ahead of them.
  - The null control is a roster with no `source` field, which orders exactly as today in all three.

Cost:
- **Size.** About 40 production lines across `roster_lib.py` (two helpers), `replan.py` (one tier), `open_driver.py` (one class and the fence) and `merge_train.py` (one key term). Each file gains self-test arms. M, sonnet, one review.
- **Hot files.** `merge_train.py` (8012 lines) is touched by R10-TRAIN-MERGE-LOOP-2, R10-HOTFIX-TRAIN-DEFER-WAIT and others. `replan.py` and `roster_lib.py` are touched by R10-FLOW-TOOLKIT-MODEL. These are distinct seams with a one-line touch each, so the overlap is allowed by seam.
- **Self-test pins.** `replan.py` pins `dispatch_tier`'s signature by source match (lines 1870 to 1883). The signature does not change.
- **Writing the field.** It costs nothing new: append-group JSON for future groups, and one record commit for the four existing groups.
- No `--budgets` row reads these files.

Binding:
- **New group** R10-OUTSIDE-FIRST (M, sonnet, opus reviewer), with files `tools/audit/seat/roster_lib.py`, `tools/plan/replan.py`, `tools/audit/seat/open_driver.py`, `tools/audit/seat/merge_train.py`, `tools/audit/seat/instruments/open_driver.py.md` and `tools/audit/seat/instruments/merge_train.py.md`. Its brief:
  "From triage batch 134 (triage: dev/programme/triage/s6-batch134.md#P420 at ROSTERSHA), owner ruling tvofi 2026-11-07T19:40Z, quote it verbatim in the body: all accepted outside issues or contributions should be prioritized higher than audit or owner submitted ones unless i call the owner one a hotfix. Add roster_lib.is_outside(group), true when the group field source is the string outside, and roster_lib.group_for_pr(roster, pr), which maps a pull request to its group through resume.pr for fork heads. The order everywhere becomes main, then hotfix (an R10-HOTFIX- name or kind bug), then outside, then today's order. (1) replan.py dispatch_tier: an outside group gets its own tier after hotfix and before the critical path; the critical path and the rest keep their relative order; keep the signature its self-test pins. (2) open_driver.py default_class and order: hotfix, outside, critical, record, rest; the fence that keeps critical first, whatever the opener priority file says, covers hotfix, outside and critical in that order. (3) merge_train.py spool drain key (line 3261 at 53273de4d): priority or front, then outside, then critical, then arrival; an entry maps to its group by branch, else by group_for_pr. Failing test first in each self-test: an outside group or entry ranks ahead of a critical-path one and behind a hotfix one. Null control: a roster with no source field orders byte-identically to the base in all three. One mutant per reader, removing the outside term, fails its arm. No policy file states the order: write no policy sentence; the docstrings cite the ruling."
- **Orchestrator, no roster op:**
  - Set `"source": "outside"` on R10-COMBI-TANK, R10-GENERIC-HEAT-CURVE, R10-GENERIC-HEAT-CURVE-PERSISTENT and R10-INPUT-REAPPEAR by one record commit on the roster branch. `roster_edit.py` has no op that writes a group field, and the readers ignore the field until the group lands.
  - Until then, order by hand with the knobs that exist: `open-priority.txt` for the opener, `train add --front` for an outside entry, and dispatch ahead of the critical path.
  - The critical path's exemption from the open-PR cap is an orchestrator practice, not in `pr_cap.py`. Under this ruling it applies to outside groups first.

## P421: move the roster drain onto the beat row and retire the local drain (orchestrator-owed, from P410)

Verdict: DEFER the move until R10-ROSTER-WRITE-SWEEP carry 17 (P409) merges. The owning group is R10-ROSTER-WRITE-SWEEP. Today the tracked row would lose the ops that P409's stale-ref refusal hits, because it never retries. The re-queue that P410 ordered is owed for nothing: every mispaired op was read back as applied.

Source: triage P410's binding (`dev/programme/triage/s6-batch133.md#P410`), handed on by the orchestrator's s13 brief.

Instances:
- **The tracked row.** `tools/audit/seat/beat_jobs.py` `roster_drain` (lines 301 to 349 at `53273de4d`) runs each op through `roster_queue.py run 1 1`, and marks it done "applied or refused: never retried past the lint gate". It fetches nothing before an op.
- **The local script** (host-local `s9/sweep-runner/roster_drain.py`, 56 lines) fetches `handoff/audit-r10-roster` before each op, and leaves an "is on no origin ref" refusal pending for the next pass. Those are the two behaviours that keep P409's stale tracking ref from losing an op. On 2026-11-07 about 13:40Z, 48 ops stalled on that refusal (P409's instance).
- **The rule on that instance.** Through the beat row today, those 48 would be marked done and refused, and never re-run. After P409's fetch-and-recheck lands in `roster_edit.py`, the refusal cannot arise, and the row is safe.
- **The mispair, measured.** In `s7/roster-queue-s7.txt` (3119 lines, host-local), 621 `#done` lines carry a sweep-runner `#note`. In 35 of them, the note names another op's verb or group. That is the `zip(pend, new)` mispair at line 41. Read back against the roster at `badbae55a`, by a script that checks each op's effect by its verb, all 35 effects are present or superseded:
  - each appended group exists, R10-GENERIC-HEAT-CURVE among them;
  - each appended carry's text is in its group;
  - each mark is on its index;
  - the issue wires match;
  - each set-files path is in its group;
  - and `set-stage R10-FLY-RELAY-REVIEW-FF in-progress` has since been superseded by `done`.
  So the mispair corrupted only the marks and notes. No op was lost, and no re-queue is owed.

Cost:
- **Moving now** trades a cosmetic mispair (0 lost of 35) for a lossy refusal path.
- **Waiting costs nothing** beyond the local script running as it does.
- **The interim fix** of the local marks is host-local: mark each op from its own report delta, inside the loop. It is not a roster op.

Binding: no roster op; this is for the orchestrator.
- Now, optionally: in `s9/sweep-runner/roster_drain.py`, mark each op right after its own `roster_queue.py` call, from the report lines that call added.
- When R10-ROSTER-WRITE-SWEEP's P409 carry merges:
  - replace line 15 of `sweep_runner.sh` with the `beat_jobs.py roster-drain` row (`--state`, `--repo`), and provision `roster-drain.queue` and `roster-lint` under its state;
  - carry the unmarked tail of `s7/roster-queue-s7.txt` over once;
  - retire `roster_drain.py`.

## P422: #3252's codescan_wait fail-closed is never re-run once its source finishes (orchestrator-owed, from P406 cause C)

Verdict: ACCEPT, as a defect instance for R10-HOTFIX-GATE-BUSY-DEFER, the owner of the gate sweep.
- **The defect.** P406 recorded this instance's cause as the deferral path. The run history shows a narrower defect. The code run that owned the codeql unit was cancelled and later re-run. The edit run's `pr-contract` had already failed closed, correctly, and nothing re-ran it. `gate-sweep.yml` re-runs only `gate` jobs. So the head stayed red for 3 h 10 min, until a new edit event.
- **Not a barrier.** One measured instance does not make a class barrier. The fixer measures the frequency with the existing harness, and may record a refusal.

Source: triage P406, cause C (`dev/programme/triage/s6-batch133.md#P406`), handed on by the orchestrator's s13 brief.

Instances (`gh api repos/tvofi/heatpump_optimizer/actions/runs?head_sha=3134798017b1d26994c410206349b06d187559a0` and each run's `jobs?filter=all`, read 2026-11-07 about 20:05Z):
- **Code run 42385416529** was created at 15:14:36Z. In attempt 1, `prelude` was `cancelled` at 15:27:40Z, so `codeql` was skipped. Attempt 2 ran `prelude` at 16:10:22Z, and the `codeql / Analyze (*)` legs completed by 16:20:08Z.
- **Edit run 42385417686** was created at 15:14:37Z. Its `pr-contract / pr-contract` (job 128446411039) ran from 15:34:33Z to 15:44:09Z and failed with `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s`. Its attempt 2 carried that same job (same stamps) and was never re-run. Edit run 42387066581's `pr-contract` (job 128449815767) failed the same way, at 15:59:14Z.
- **The red cleared** only with edit run 42403200941, created at 18:49:39Z for a new edit event: the gate turned `success` at 18:53:55Z. The `pr-contract` red was open from 15:44:09Z to 18:53:55Z.
- **Why nothing re-ran it.** `tools/ci/gate.py --sweep` (line 303) re-runs only a sibling run's `gate` job. Re-running the gate re-reads a red `pr-contract` and stays red.
- **Not the RCA's shape.** `dev/audit/rca/R10-RCA-CODESCAN-WAIT.md` section 5 covers the inverted pair: an edit run below its code run, closed by M1's wait in `prelude.wait_sources`. This pair was ordered: the code run's id is lower. Its source went away by cancellation, a shape the record does not cover.
- **The rule on the instance.** When a run that owns a finished codeql unit completes at a head, the sweep re-runs a sibling edit run's failed `pr-contract / pr-contract` whose log holds `codescan_wait`'s no-source refusal, then that run's gate. At #3252, that is at 16:20Z, after the code run's last leg, about 2.5 h before the red actually cleared.

Cost:
- **The change.** One more job class in the sweep's re-run set, keyed on a log line the job already prints. That is one log read and one re-run call per matching red: no new standing cost, and a pr-contract job of about 10 runner-minutes per re-run.
- **The benefit.** 3 h 10 min of red on one critical-path head. The frequency is unmeasured, so the carry asks for it. `dev/audit/harnesses/r10_codescan_wait_race.py` already reads this class.
- **Ownership.** `gate.py` is R10-HOTFIX-GATE-BUSY-DEFER's only file, and its part 3 (#3287) merged at `5c1fa41fb`. No `--budgets` row reads it.

Binding: append-carry R10-HOTFIX-GATE-BUSY-DEFER, with this text: "From triage batch 134 (triage: dev/programme/triage/s6-batch134.md#P422 at ROSTERSHA), the P406 cause C instance: at PR 3252 head 31347980, code run 42385416529 attempt 1 was cancelled (prelude 15:27:40Z), so edit run 42385417686 pr-contract job 128446411039 failed closed at 15:44:09Z with codescan_wait no run at this head owns a finished codeql unit after 600 s. The code run re-ran and its codeql legs finished by 16:20:08Z, but gate.py --sweep re-runs only gate jobs, so the pr-contract red stood until a new edit event at 18:53:55Z (3 h 10 min). This pair was ordered, not the inverted pair R10-RCA-CODESCAN-WAIT section 5 closes. Fix: when a run owning a finished codeql unit completes, the sweep re-runs a sibling edit run whose pr-contract failed on that no-source refusal (keyed on the log line), then its gate. Measure first with dev/audit/harnesses/r10_codescan_wait_race.py over the 7 days before your merge base: count ordered-pair no-source reds whose source later finished. Build only if it is 3 or more; otherwise record the refusal with the count. Arms: the 3252 shape is re-run once the code run finishes; null control: a pr-contract red on any other line is not re-run; a mutant dropping the log-line key re-runs every red pr-contract and fails the null."

## P423: P415's measurement has no live owner; it is the coverage half of the owner's mutant ruling (orchestrator-owed, from P415)

Verdict: ACCEPT changed. P415's binding sent the measurement to the owner of `dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md` section 6, but that record's writer, R10-FRICTION-RECORDS, is `done`, and section 6 is the family-spelling cause, not population T (section 2). The open question is now the owner's own. On 2026-11-07 tvofi ruled that fixers set `MUTANT_CMD` and kill their diff's survivors before handoff, "if that will improve throughput". That ruling is R10-FIXER-MD-SPELLING-CORPUS carry 0, whose measure-first compares mutant-run wall time against repair hours. That comparison is sound only if the diff mutants would have caught the reviewer's survivor. P415's measurement answers exactly that, so it goes to that carry as its coverage term.

Source: triage P415's binding (`dev/programme/triage/s6-batch133.md#P415`), handed on by the orchestrator's s13 brief, and the owner's mutant ruling (host-local `s11/owner-ruling-para.txt`, second paragraph).

Instances:
- **No live owner.** `git log origin/main --format=%h -- dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md` names `6f27eefb7` and `d9bf18c42` (2026-11-06), both R10-FRICTION-RECORDS work. That group is `done` at `badbae55a`, and no live group lists `dev/audit/rca/`.
- **Carry 0.** R10-FIXER-MD-SPELLING-CORPUS carry 0 (at `badbae55a`, stage `not-started`) reads: "Land (a) and (b) only if the saving exceeds the added time". Its saving is the repair-round hours of mutation-vacuous blocks. That is a saving only for the blocks whose survivor `mutant_run.py --diff` would have produced.
- **The operators.** `tools/audit/seat/mutant_run.py` line 65 applies `GUARD_OFF`, `RETURN_DEL`, `CMP_BOUND`, `CALL_DEL` and `CONST_SWAP`. The reviewer's mutant is chosen by hand.
- **The rule on the instance.** With the coverage term, the saving becomes (blocks whose survivor the diff run reproduces) x (repair hours per block). Without it, every block counts.
- **The window.** The prototype checker's 11 blocks in 24 h (host-local `s12/proto-plan/live-check.txt`) is the population. A cloud fixer cannot read it, so it re-derives the window from the `review/*` bus verdicts of class `mutation-vacuous`.

Cost:
- **The term.** A `mutant_run.py --diff` run at each blocked head, capped by `--max-mutants`: a few minutes of the group's self-test per head, on the fixer's own seat, inside a measurement the carry already owes.
- **What it saves.** No new seat, and no RCA re-take with no owner.

Binding: append-carry R10-FIXER-MD-SPELLING-CORPUS, with this text: "From triage batch 134 (triage: dev/programme/triage/s6-batch134.md#P423 at ROSTERSHA), the coverage term of carry 0 measure-first (P415 re-routed: its RCA owner is done). For each mutation-vacuous blocked verdict in the review/* bus over the 7 days before your merge base, record whether MUTANT_CMD was set at that handoff (the prepr log or the body Figures), and whether mutant_run.py --diff with the group self-test, run at that head under the --max-mutants cap, reports the surviving mutant the reviewer named, or one on the same line. Count only the reproduced blocks in carry 0 saving; print reproduced against total as sets, not totals. Null control: a merged head with no block, whose diff run must report no survivor the reviewer would have named. If fewer than half are reproduced, say so: then carry 0 (b), the prepr refusal, does not pay, whatever the wall time."
