# R10-FLY-STANDING-CONTRACTS design note, round 2, on design/r10-fly-standing-contracts (lowercase; the roster hint spells design/R10-FLY-STANDING-CONTRACTS)

Issue #3115.
- Base and code read: origin/main c3a279e3252a8b57bb00b5a677318cd4fe20387f. The group has no `after` edge, so there is no predecessor.
- Roster: origin/handoff/audit-r10-roster aa6b12a8e (25 carries, 0-24).
- Round 1: f21449444, verdict 221627f99 (`revise`, five points). This round answers those five only; each change is tagged [V1]..[V5].
- Size: L, five serial parts (§6). Orchestrator ruling s11: one L; P3 (hooks) is its own serial part; the seat-writer/session-lock arm is P5.
- Item numbering: item n is carry n-1. Items 23-25 are carries 22-24; items 26 and 27 are the verdict's two fixer notes (it labels them 25 and 26).

## 1. Owning seam

**Owner:** one new Python script beside beatd.py, the beat-jobs script, named in prose because it is absent at the base.
- It owns every job predicate.
- It is the only writer of `$HPO_STATE_DIR/digest/`, and writes nothing else under `$HPO_STATE_DIR` [V2].
- tests/seam_map.json maps no seat module, so step 17's one-owner rule applies.

**Called, not edited:**
- `beatd.py`;
- the `orchestrator_tick.py` board, `owed_unactioned.py`, `roster_queue.py`;
- tools/plan/replan.py, `state_docs.py`, tools/pr/cancel_superseded.py;
- tools/audit/worktree_gc.sh, `update_pr.sh`;
- `open_driver.py` [V1]: the opener row runs it and forwards what it prints. This group does not edit it.

**Edited:** `pulse.py`; `.claude/hooks/pre-bash.sh` (P3, [V4]); `roster_queue.py`, `bus.sh`, `merge_train.py` and `handover_prompt.py` at their write entry only (P5, [V3]).

**New in P5 [V3]:** a seat-generation script, tools/audit/seat/ seat_gen.py (absent at the base), the one owner of the `.gen` files and the session lock.

**Job table:** beatd's default jobs file, `beatd.jobs.json` (beatd.py:527 "--jobs"), absent at the base. It fits `load_table` (beatd.py:119) as it stands. [V5] R10-BEAT-JOB-TABLE, which round 1 named as the later owner of more rows, is `done` unbuilt (s10 instrument audit: "arms b and c below the improvement bar"), so this group is the table's only author.

**Policy:** one new contract, dev/governance/roles/standing.md (absent at the base). It holds the Wait, Reads, Autofix-hold and Recycle terms once, and each standing contract's opener cites it. `decision: owner`, kept as routed (§7).

## 2. Shape

**Digest files [V2].** All are under `$HPO_STATE_DIR/digest/`:
- `jobs/<row>`: each row's actionable lines, written atomically;
- `digest.txt`, `new.txt`, `gone.txt`, `new.stamp`: written by `fold()` only;
- `heads.tsv`: head-watch's last-seen head per open PR (its own state);
- `events.txt`: head-watch's `HEAD-MOVED` lines and the opener's STUCK lines.

`$HPO_STATE_DIR/events.tsv` stays ledger.py's store (ledger.py:119 `EVENTS`, written only by `record`, ledger.py:312). No job writes it; orchestrator_tick.py:4113 "writes no store" stays true.

**Digest flow:**
1. Each job writes its file under `digest/jobs/`.
2. It calls `fold()` under `flock digest/.lock`.
3. `fold()` concatenates the job files into `digest.txt` and normalises stamps and ages (the stand-in's rule).
4. It diffs the result into `new.txt` and `gone.txt`.
5. It touches `new.stamp` only when `new.txt` is non-empty.

The orchestrator's one wake reads only `new.stamp` and `events.txt`, so no job's output lives only in a private log (carry 19's naming of "the digest and event files").

**Invariants:**
- A null pass changes no byte.
- No job runs `git pull`, `merge`, `checkout` or `reset` in the checkout beatd, `tick_loop.sh` or `cloud_relay.sh` runs from. Jobs read main with `git -C <repo> show origin/main:`, asserted from `HPO_GIT_SHIM_LOG` (gap 4). P3's guard refuses the same class for a session (§6).
- No job touches a seat's alive file (gap 3).

**Job table rows.** Each row has `cwd: orch` and runs the script as `<job> --state $S`.

| row | s | writes to the digest |
|---|---|---|
| tick-digest | 240 | The board's actionable family (carry 20's list). A NOT REVIEWABLE or RED line counts only after two passes at one head (gap 2). |
| owed-check | sweep cadence | `owed_unactioned.py`, once per sweep (gap 1): UNACTIONED lines; UNREADABLE on rc 2. |
| roster-drain | 120 | `roster_queue.py` `run_queue` (roster_queue.py:93) per pending non-`#` line, then marks that exact line. On refusal, `roster: refused <reason>`, never retried. A hold line releases when its batch is on main, and is HOLD-STALE after 24 h (gap 6). |
| plan-beat | 1800 | replan.py `--out`, then `state_docs.py --push --mirror --plan`. PLAN UNAVAILABLE on exit 1. [V5] postmerge.py:48 already runs `state_docs.py --push` after every merge; plan-beat adds the `--plan --mirror` render and the idle-hours cadence, and calls the same writer, adding none. |
| pulse | 300 | `pulse.py` into the pulse file `beatd status` reads (beatd.py:435). STOPPED lines go to the digest. |
| cancel-sweep | 600 | `cancel_superseded.py sweep --repo R`. Failures only. |
| disk | 900 | `worktree_gc.sh` below `disk_floor_gib`. A line only if still below afterwards. |
| opener [V1] | 300 | Runs `open_driver.py --board <tick board>` (one pass). Its state stays its own, `$HPO_STATE_DIR/open-driver/` (open_driver.py:172). The row copies the pass's `OWED ... open-refused`, `NEEDS-TITLE`, `STARVED` and (once landed) `STUCK` lines to `jobs/opener`, and STUCK also to `events.txt`. Retry, seen-state and ordering are open_driver.py's (open_driver.py:63 `BACKOFF_S, BACKOFF_MAX_S = 300, 7200`). The handoff-update arm stays with `cloud_relay.sh`, as instruments/open_driver.py.md says. |
| head-watch | 120 | `HEAD-MOVED #<n> <old> <new>` lines to `digest/events.txt` [V2], diffed against `digest/heads.tsv`. |

**Before:** queue line → LLM seat → report → orchestrator turn.

**After:** beat → digest → wake. An LLM seat wakes only for a refusal, a STUCK line or a judgement.
- Merge, dispatch and triage stay LLM seats (carry 21).
- Tick and roster retire in P2. Their work never moves into the orchestrator's turns (tvofi 2026-10-24).

**Single writer (P5) [V3].** Carries 22 and 23, folded by carry 24.
- `seat_gen.py bump <seat>` writes `$HPO_STATE_DIR/<seat>.gen` (monotonic integer and epoch) and prints it; the orchestrator runs it when it starts a replacement, and the seat's prompt carries the number.
- `seat_gen.py check <seat> <gen>` exits 1 and prints SUPERSEDED when the file holds a higher number.
- Writers wired, measured at the base as the tracked code that applies a standing seat's queue lines: `run_queue` (roster_queue.py:93), `dispatch` (bus.sh:502), `train_add` (merge_train.py:1088). Each calls `check` with `HPO_SEAT_GEN` before its first write and stops on SUPERSEDED; unset, it behaves as today (the orchestrator's own calls carry none). The fixer re-measures this list at the merge base and wires only what it finds.
- The tick flag carry 22 asks for already exists: judge_alive prints `DUPLICATE seat` when two attributed ids are fresh (pulse.py:245). P5 adds a planted case, not code.
- `seat_gen.py lock` is the session lock: it records the session binary's pid (the first ancestor whose command is the session binary, never `$PPID`) and its start time in `$HPO_STATE_DIR/session.lock`. A live holder whose command is the session binary refuses, logging both pids; a gone pid or one naming another command is taken over. Liveness is read from `ps -p <pid> -o command=`.
- The resume steps name `lock` before the first dispatch: handover_prompt.py:114 "## Resume steps" and sweep_template.md's step (0).

## 3. Alternatives

- **One script per job, each appending to the digest.** Lost: nine writers of one file with no lock, nine normalisers and nine self-test wirings.
- **A `--digest` mode in `orchestrator_tick.py`.** Lost: the board is a reader that "writes no store" (orchestrator_tick.py:4113); a digest mode makes it a writer of state it reads.
- **head-watch through ledger.py's `record` [V2].** Lost: events.tsv's rows are OWED open/close pairs `fold` reduces (ledger.py:329); a head move is not owed work and would need a kind with no close.
- **The opener row as its own driver (round 1) [V1].** Lost: a second owner of opening and a second seen-state beside `$HPO_STATE_DIR/open-driver/`.
- **A copy of each term in all four contracts (carry 1's control).** Lost: every standing cap is at or within one line of its measure (`node tools/policy/policy_lint.mjs --budgets`; §6).
  - Four copies would mean four raised caps.
  - One file is one new cap, offset by two contracts falling to stubs.
  - finding-propagation.md says to write a rule "once".
- **The shared terms in `orchestrator.md` §5.** Lost: each seat would load the 294-line contract.
- **A tracked wait loop.** Refused by P51. Instead, each seat runs its own `run_in_background` loop.
- **The checkout guard as a separate hook file [V4].** Lost: it duplicates pre-bash.sh's command-position parser (pre-bash.sh:13-17, which reads `bash -c` and `eval` bodies); a second arm reuses it.
- **seat_gen inside pulse.py [V3].** Lost: pulse is a reader of liveness; the generation is written by the orchestrator and read by writers pulse never calls.

## 4. Sibling sites (enumerated at the base)

- `git grep -l -E "standing-(tick|merge|dispatch|roster)\.md" -- ':!dev/archive' ':!dev/programme'` finds:
  - CLAUDE.md, orchestrator.md, INSTRUMENTS.md, sweep_template.md and policy_budgets.json: edited in P2;
  - tests/closures.json: re-derived;
  - a policy-rot fixture: a recorded snapshot, out of scope.
- `git grep -n merge_pr.sh -- dev/governance/roles` finds standing-merge.md:12 "`merge_pr.sh` merges a budget-file or policy head directly." (carry 4) and nudge.md:89, which names it as a postmerge caller, not a route; out of scope [V5].
- `git grep -n -E "tick_brief|tick_alive" -- tools/audit/seat` finds sweep_template.md:41 and :43. `tick-owed` and "newest actionable" no longer appear; step (5) is sweep_template.md:75 "newest pass unfiltered" [V5].
- `grep -n "git " tools/audit/seat/sweep_template.md | grep -v -- "-C {{"` finds :61 only.
- `git grep -n STANDING -- tools/audit/seat/pulse.py` finds pulse.py:114, which loses tick and roster in P2, and the self-test at :577 that compares the standing-*.md glob to it.
- `seat_of` (pulse.py:256) routes by the oldest verdict only.
- [V5] standing-dispatch.md:15-16 "A beat job takes over once a cycle's log agrees; never inline" already states the relay's retirement condition; P2 cites standing.md beside it and adds nothing.

## 5. Evidence, by file

**No finder harness.** The owner's report and the orchestrator's ledger are the evidence. Every field figure is re-measured at the merge base; none is carried.

**The script's `--self-test`**, wired through `selftest_wiring.py`:
- Every row gets a null case (nothing owed: no write, no stamp) and a mutant on its predicate.
- Planted cases:
  - one OWED line gives exactly that line;
  - a timestamp-only change gives nothing;
  - a queue line drains and is marked;
  - a REFUSE line arrives in the digest;
  - a transient RED gives nothing, while a persistent one appears on the second pass;
  - a stub `open_driver.py` printing one `OWED ... open-refused` line puts exactly that line in `jobs/opener`, and one STUCK line also in `events.txt` [V1];
  - a head move writes one line to `digest/events.txt`, and `events.tsv` is absent afterwards (the [V2] null).
- Each planted case first fails against an empty jobs directory.

**A scrubbed recorded board** under tools/audit/seat/fixtures/ reproduces the stand-in's actionable set.

**`pulse.py --self-test`:**
- A blocked verdict older than a merge verdict names both PRs and both seats.
- Null: one verdict prints one line.
- Killed: the oldest-only mutant.

**`sweep_render.py` fixture:**
- Every rendered `git ` carries `-C`.
- Step (5) names the digest and both counts.
- Mutants: drop `-C`; restore "newest pass unfiltered".

**tests/entities.py, one new check:**
- Every standing-*.md and proposal-triage.md cites standing.md.
- standing.md has its four headings.
- Deleting any one turns the check red. The null control is the edited tree, which passes.

**Hooks (P3):**
- A planted dead job prints DEAD; a stale digest prints STALE.
- On a throwaway HOME, `--check` lists every user-level hook, then none after `--install`.
- A second `--install` changes no byte.
- A mutant that drops the backup or rewrites an unrelated entry is killed.
- [V4] `pre-bash.sh --self-test` gains rows: `git checkout`, `reset`, `pull`, `merge`, `rebase`, `stash`, `clean` with cwd (or `-C`) equal to the marked checkout refuse with exit 2; the same command in a worktree passes (null); `git fetch` and `git -C <checkout> show` pass; with no marker the arm is inert. Mutant: dropping the `-C` resolution lets `git -C <checkout> reset` through.

**seat_gen.py `--self-test` (P5) [V3]:**
- A lower generation's `check` exits 1; null: the current generation exits 0. Mutant: `>` to `>=` on the comparison.
- A wired writer given a superseded generation writes nothing (one case per writer wired).
- Lock: a live other holder refuses; nulls: a dead holder pid and a reused pid naming another command are both taken over, and the session's own pid is not a duplicate. Mutant: dropping the command match makes the reused-pid null refuse.
- A planted second fresh id prints `DUPLICATE seat` through pulse.py (existing arm, new case).

**Goldens and claim files:** none move.

## 6. Parts, policy, budget, hot files

**P1 (code).**
- New: the script, `beatd.jobs.json`, its instruments entry and the fixture.
- Edits:
  - `pulse.py` (carry 5);
  - `INSTRUMENTS.md`;
  - `sweep_template.md`: steps (2), (4b), (4e), (5) and (8) read the digest; (1b) (sweep_template.md:59) and the tick restart stay;
  - the `sweep_render.py` fixture.

**P2 (policy).**
- Gate: P1 has merged, and `beatd status` has shown every P1 row `ok` from main for one cycle beside the live seats. This is what "live and verified" means here.
- New: standing.md.
- Contract edits:
  - tick and roster become retirement stubs;
  - merge takes carry 4 inside its cap (standing-merge.md:12 gives way to the train route); carry 8 has already landed (standing-merge.md:9-12 "`train.sh add`") [V5];
  - dispatch cites the hold and pays for it by replacing its `git ls-remote` block (standing-dispatch.md:27-29) with `bus.sh orphans` (P95).
- Other edits:
  - `orchestrator.md` §5 (orchestrator.md:109-111, the "Four standing seats" sentence);
  - the CLAUDE.md index (the two retired rows merge into one);
  - proposal-triage.md's opener;
  - policy_budgets.json;
  - `pulse.py`'s STANDING and its self-test at :577, in the same commit (item 26);
  - (1b), the tick restart and the placeholders in `sweep_template.md`.

**P3 (hooks, after P1).**
- New: user-level hook scripts under tools/audit/seat/hooks/; one setup script under tools/audit/seat/ with `--check`, `--install` and `--self-test` (under `offline_spy.py`); a hooks entry under tools/audit/seat/instruments/.
- The SessionStart and PostCompact liveness hook runs `policy_reread_check.py`, then prints:
  - `beatd.py status` (the loop list is the job table);
  - fresh or STALE for each alive file and for `digest/digest.txt`;
  - the digest;
  - the line that re-arms the wake.
- The git-identity and seat-interpreter hooks are host-specific, so user-level. The seat-interpreter hook checks against seat_venv.sh.
- [V4] The main-checkout Bash guard is this group's, written as a second arm of `.claude/hooks/pre-bash.sh` (already the project-level `Bash` PreToolUse hook, .claude/settings.json:21-26). R10-BASH-KILL-HOOK is done and its arm refuses name-kills only.
  - It refuses (exit 2) a git command that moves HEAD or the working tree (`checkout`, `switch`, `reset`, `pull`, `merge`, `rebase`, `stash`, `clean`, `restore`) whose cwd or `-C` path resolves to the checkout named in `$HPO_STATE_DIR/orch-checkout` (gap 4's class).
  - With no `HPO_STATE_DIR` or no marker file it is inert, so it binds every session but bites only the orchestrator's host. It fails open on an unparseable payload, as pre-bash.sh:24-25 does.
  - Project-level, so the installer's `--check` reports it as present in the tree and installs nothing for it.
- Paths come from `$HPO_STATE_DIR`, so `tmp_paths.py` and `ref_privacy.py` pass.

**P4:** carry 18, once #3061 merges.

**P5 (single writer and session lock, after P2) [V3].** `seat_gen.py`, its wiring into the writers §2 lists, the `lock` step in handover_prompt.py's Resume steps and sweep_template.md's step (0), and its instruments entry. handover_prompt.py and sweep_template.md were R10-SEAT-SINGLE-WRITER's files; they join this group's `files` by a roster op (`decision: orchestrator`, routed to the roster seat).

**Policy files**, all in P2, under mandate 6329234399 or the owner's review: standing.md, the four standing-*.md, proposal-triage.md, orchestrator.md and CLAUDE.md.

**Budget [V5]** (`node tools/policy/policy_lint.mjs --budgets` at c3a279e3; P2 re-measures at its own base):
- per-file caps: standing-merge 36/37 lines, 504/507 tokens; standing-dispatch 39/39, 509/509; proposal-triage 36/36, 489/489; standing-roster 27/27, 368/368; standing-tick 26/26, 330/330. roles/orchestrator.md has no per-file key in policy_budgets.json.
- corpus ~66409 against cap 66434 + band 500: 25 tokens below the cap.
- So standing.md's tokens must be paid inside the corpus: the tick and roster stubs (698 tokens today) and dispatch's ls-remote block are the payment, and standing.md is cut until P2's corpus line is at or below 66434. No corpus raise.
- standing.md's new per-file cap is a raise under budget_raise_gate.py's `capfile` rule; the lowered tick and roster caps pay it, and P2's `## Raise justification` says so.
- No structure_budgets metric moves.

**Closure:** every new file under tools/audit/ or dev/governance/ sits under an INERT prefix (tests/closure.py:296 "tools/audit/", :273 "dev/governance/"). The pre-bash.sh edit and the new entities check select scripts; tests/closures.json is re-derived.

**Hot files** (roster aa6b12a8e, live groups only) [V3][V5]:
- standing-dispatch.md: R10-TICK-LEVELS, R10-DISPATCH-AT-HANDOFF.
- `open_driver.py`: not edited here; R10-TICK-LEVELS moves its `resolve` rule out unchanged, R10-HANDOFF-PATH owns its retry edit (§7, item 20).
- P5's writers: bus.sh (R10-DISPATCH-AT-HANDOFF, R10-LEDGER-RESIDUE, R10-PLANTED-DEFECT-AUDIT); merge_train.py (R10-FLY-GH-READ-RETRY, R10-CI-PRIORITY-PAUSE, R10-TRAIN-MERGE-LOOP, R10-RAISE-GATE-SHIM); roster_queue.py (R10-ROSTER-WRITE-SWEEP). Each edit is a three-line call at the write entry; P5 rebases over whichever lands first. No `after` edge is proposed.
- `INSTRUMENTS.md`: shared by several groups; append-only rows.
- `orchestrator.md`, `sweep_template.md`, `pulse.py`, `pre-bash.sh`: no live sharer. R10-SEAT-SINGLE-WRITER is absorbed into this group, so round 1's edge from it and its hot-file line are dropped.

## 7. Carries (all 25)

**`decision: owner`:** carry 1 wants a copy in each contract; this note writes it once (§3), ruled at P2. Carry: R10-FLY-STANDING-CONTRACTS (item 2)

- Carry: R10-FLY-STANDING-CONTRACTS (item 1): P51's Wait term goes in standing.md (P2). The loop touches the alive file and its own `FILE.d/<id>` entry only while the seat's pid answers `kill -0`, and exits when it dies (gap 3); see item 27.
- Carry: R10-FLY-STANDING-CONTRACTS (item 2): P95's Reads term goes in standing.md (P2).
- Carry: R10-FLY-STANDING-CONTRACTS (item 3): the autofix hold goes in standing.md's Reads (P2). bus.sh's refusal stays a triage proposal, as carry 2 says.
- Carry: R10-FLY-STANDING-CONTRACTS (item 4): the Recycle term goes in standing.md and §5 (P2), making tvofi's "Make that rule persistent" hold. During a recycle, work goes only to the incoming seat after HANDED (gap 5).
- Carry: R10-FLY-STANDING-CONTRACTS (item 5): standing-merge.md:12 "merge_pr.sh" gives way to the train route (P2).
- Carry: R10-FLY-STANDING-CONTRACTS (item 6): `pulse.py` names every owed verdict (P1).
- Carry: R10-FLY-STANDING-CONTRACTS (item 7): step (2) gets `-C` (P1).
- Carry: R10-FLY-STANDING-CONTRACTS (item 8): step (5) reads the digest and prints both counts (P1).
- Carry: dismissed: already landed at base (item 9): standing-merge.md:9-12 says `train.sh add` at c3a279e3 [V5].
- Carry: R10-FLY-STANDING-CONTRACTS (items 10, 11): the orchestrator reads only the plan page and the digest, stated in one line of §5 (P2). R10-ORCH-PLANPAGE is done.
- Carry: R10-FLY-STANDING-CONTRACTS (item 12): merge-seat retirement and the pitch job are unbuilt here and their routed owner, R10-BEAT-JOB-TABLE, is done unbuilt [V5]; they wait on the orchestrator's routing, and the body says so. Merge stays an LLM seat.
- Carry: R10-FLY-STANDING-CONTRACTS (items 13, 14): roster-drain is built in P1. The roster seat retires in P2, after the scratch-branch acceptance.
- Carry: R10-FLY-STANDING-CONTRACTS (items 15, 16, 17): the dispatch job (`bus.sh dispatch-owed`) is unbuilt here and waits on the orchestrator's routing for the same reason as item 12 [V5]. `decision: owner`: carry 21 keeps dispatch briefs as LLM work.
- Carry: R10-FLY-STANDING-CONTRACTS (item 18): steps (2), (4b), (4e) and (8) are built here (P1); steps (3) and (6) wait on the orchestrator's routing, as item 12 [V5].
- Carry: R10-FLY-STANDING-CONTRACTS (item 19): P4, with its harness under dev/audit/harnesses/.
- Carry: R10-HANDOFF-PATH (item 20): carry 19 (1)'s opener semantics (retry after 30 min, three tries at most, then one STUCK line) are an edit to open_driver.py, owned by R10-HANDOFF-PATH, whose seam is "update_pr.sh, open_pr.sh and pr_args.sh with open_driver.py"; R10-TICK-LEVELS only moves `resolve` out unchanged [V1]. Control there: a fourth failure prints STUCK and no fifth START; null: a success marks seen. This group's opener row forwards STUCK whenever it lands.
- Carry: R10-FLY-STANDING-CONTRACTS (item 20): the rest of carry 19. Part (1) is the P1 rows, with the head watcher writing `digest/events.txt` [V2]; the triage pass and merge watch loops become Wait loops; tick_loop.sh, cloud_relay.sh and state_docs.py are kept as is. Part (2) is P3, including the checkout guard [V4].
- Carry: R10-FLY-STANDING-CONTRACTS (item 21): tvofi's "tick seat ... replaced by a script within the sweep" is tick-digest (P1); the seat retires in P2.
- Carry: R10-FLY-STANDING-CONTRACTS (item 22): on tvofi's "necessary LLM tasks", the mechanical work is the P1 rows; dispatch, triage and merge stay LLM seats.
- Carry: R10-FLY-STANDING-CONTRACTS (item 23): P63's generation token, `seat_gen.py bump`/`check`, wired into the writers §2 measures (P5) [V3].
- Carry: R10-FLY-STANDING-CONTRACTS (item 24): P236's session lock, `seat_gen.py lock`, named in the resume steps (P5) [V3].
- Carry: R10-FLY-STANDING-CONTRACTS (item 25): carry 24's fold is items 23 and 24; its "measure first" binds P5's writer list.

## Notes for the fixer

- Carry: R10-FLY-STANDING-CONTRACTS (item 20): STEP 1's review comes first. It has one row per loop and per gap 1 to 6, each judged from its log. Get the stand-ins' paths from the orchestrator, and cite none of them in tracked text.
- Carry: R10-ROSTER-WRITE-SWEEP (item 13): R10-ROSTER-QUEUE is absorbed and R10-ROSTER-WRITE-SWEEP now lists `roster_queue.py` [V5]. If exact-line marking lands in `roster_queue.py` first, roster-drain calls it and deletes its own marker.
- Carry: R10-FLY-STANDING-CONTRACTS (item 21): `tick_alive` and `tick_brief` leave the placeholder table (sweep_template.md:41, :43) in P2, not P1.
- Carry: R10-FLY-STANDING-CONTRACTS (item 26): pulse.py:577's self-test requires the standing-*.md glob to equal STANDING; P2 keeps standing-tick.md and standing-roster.md as stubs while dropping them from STANDING, so that check changes in the same commit (to the non-stub contracts, or STANDING plus a retired set).
- Carry: R10-FLY-STANDING-CONTRACTS (item 27): the Wait loop writes no pid into the alive file; judge_alive (pulse.py:230) keeps judging the mtimes of FILE and `FILE.d/<id>` (read_alive, pulse.py:410) against cadence. The pid is read only by the loop itself (`kill -0`), so when the seat dies the touches stop and pulse prints STOPPED, as today.
- Carry: R10-FLY-STANDING-CONTRACTS (item 22): plan-beat and postmerge.py both call `state_docs.py --push`; measure whether a concurrent push rejects and retries. If it does not, plan-beat skips a pass that starts within one merge's docs run, read from postmerge's own log, not a new lock.
