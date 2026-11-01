# R10-FLY-STANDING-CONTRACTS design note on design/r10-fly-standing-contracts (lowercase; the roster hint spells design/R10-FLY-STANDING-CONTRACTS)

Issue #3115.
- Base and code read: origin/main ca6333333afc1ec7937b9792880458d190f4d4d2. The group has no `after` edge, so there is no predecessor.
- Roster: origin/handoff/audit-r10-roster 6d7759c90.
- Size: L, built in four serial parts (§6).

## 1. Owning seam

**Owner:** one new Python script beside beatd.py, the beat-jobs script. It is named in prose because it is absent at the base.
- It owns every job predicate.
- It is the only writer of `$HPO_STATE_DIR/digest/`.
- tests/seam_map.json maps no seat module, so step 17's one-owner rule applies.

**Called, not edited:**
- `beatd.py`;
- the `orchestrator_tick.py` board, `owed_unactioned.py`, `roster_queue.py`;
- tools/plan/replan.py, `state_docs.py`, tools/pr/cancel_superseded.py;
- tools/audit/worktree_gc.sh, `open_pr.sh`, `update_pr.sh`.

**Edited:** `pulse.py`. No live group lists it.

**Job table:** beatd's default jobs file (beatd.py:527 "--jobs"), absent at the base. It fits `load_table` as it stands.

**R10-BEAT-JOB-TABLE** runs after this group. Its brief says this group "creates the job table and its first jobs" and that it adds rows and reconciles the tick and state-docs rows. That is serial ownership, so this is not a two-owner stop.

**Policy:** one new contract, dev/governance/roles/standing.md (absent at the base). It holds the Wait, Reads, Autofix-hold and Recycle terms once, and each standing contract's opener cites it.

## 2. Shape

**Digest flow:**
1. Each job writes its actionable lines atomically to its own file under `digest/jobs`.
2. It calls `fold()` under `flock digest/.lock`.
3. `fold()` concatenates the job files into the digest and normalises stamps and ages (the stand-in's rule).
4. It diffs the result into the new and gone files.
5. It touches the new stamp only when the new file is non-empty.

head-watch appends to the events file. The orchestrator's one wake reads only the new stamp and the events file, so no job's output lives only in a private log.

**Invariants:**
- A null pass changes no byte.
- No job runs `git pull`, `merge`, `checkout` or `reset` in the checkout beatd, `tick_loop.sh` or `cloud_relay.sh` runs from. Jobs read main with `git -C <repo> show origin/main:`, asserted from `HPO_GIT_SHIM_LOG` (gap 4).
- No job touches a seat's alive file (gap 3).

**Job table rows.** Each row has `cwd: orch` and runs the script as `<job> --state $S`.

| row | s | writes to the digest |
|---|---|---|
| tick-digest | 240 | The board's actionable family (carry 21's list). A NOT REVIEWABLE or RED line counts only after two passes at one head (gap 2). |
| owed-check | sweep cadence | `owed_unactioned.py`, once per sweep (gap 1): UNACTIONED lines; UNREADABLE on rc 2. |
| roster-drain | 120 | `roster_queue.py` `run` per pending non-`#` line, then marks that exact line. On refusal, `roster: refused <reason>`, never retried. A hold line releases when its batch is on main, and is HOLD-STALE after 24 h (gap 6). |
| plan-beat | 1800 | replan.py `--out`, then `state_docs.py --push --mirror --plan`. PLAN UNAVAILABLE on exit 1. |
| pulse | 300 | `pulse.py` into the pulse file `beatd status` reads. STOPPED lines go to the digest. |
| cancel-sweep | 600 | `cancel_superseded.py sweep --repo R`. Failures only. |
| disk | 900 | `worktree_gc.sh` below `disk_floor_gib`. A line only if still below afterwards. |
| opener | 300 | The board's handoff-no-pr and handoff-update lines, via `open_pr.sh` or `update_pr.sh`. A (topic, sha) is done only on success; a failure retries after 1800 s, three times at most, then STUCK. Critical path first; an unlisted topic never starves (P350). b94-P337's driver is absent at the base, so this row is that driver. |
| head-watch | 120 | `HEAD-MOVED #<n> <old> <new>` lines, to the events file. |

**Before:** queue line → LLM seat → report → orchestrator turn.

**After:** beat → digest → wake. An LLM seat wakes only for a refusal, a STUCK line or a judgement.
- Merge, dispatch and triage stay LLM seats (carry 22).
- Tick and roster retire in P2. Their work never moves into the orchestrator's turns (tvofi 2026-10-24).

## 3. Alternatives

- **One script per job, each appending to the digest.** Lost: nine writers of one file with no lock, nine normalisers and nine self-test wirings.
- **A `--digest` mode in `orchestrator_tick.py`.** Lost: it couples the board's writer to its reader, and four open groups list that file (R10-FLY-RAISE-REVIEWABLE, R10-TICK-PR-BUCKETS, R10-TICK-GROUP-LINES, R10-ROSTER-LIB-SCHEMA).
- **A copy of each term in all four contracts (carry 1's control).** Lost: every per-file cap in dev/governance/config/policy_budgets.json sits at its measure or one line above (`node tools/policy/policy_lint.mjs --budgets`).
  - Four copies would mean four raised caps and would overrun the corpus band.
  - One file is one new cap, offset by three lowered caps.
  - finding-propagation.md says to write a rule "once".
- **The shared terms in `orchestrator.md` §5.** Lost: one line of headroom, the file is in flight in R10-FLY-RAISE-REVIEWABLE, and each seat would load 294 lines.
- **A tracked wait loop.** Refused by P51. Instead, each seat runs its own `run_in_background` loop.

## 4. Sibling sites (enumerated at the base)

- `git grep -l -E "standing-(tick|merge|dispatch|roster)\.md" -- ':!dev/archive' ':!dev/programme'` finds:
  - CLAUDE.md, orchestrator.md, INSTRUMENTS.md, sweep_template.md and policy_budgets.json: edited in P2;
  - tests/closures.json: re-derived;
  - a policy-rot fixture: a recorded snapshot, out of scope.
- `git grep -n merge_pr.sh -- dev/governance/roles` finds standing-merge.md:9 "merge_pr.sh" only.
- `git grep -n -E "tick_brief|tick-owed|tick_alive" -- tools/audit/seat` finds sweep_template.md:41, :43 and :75.
- `grep -n "git " tools/audit/seat/sweep_template.md | grep -v -- "-C {{"` finds :61 only.
- `git grep -n STANDING -- tools/audit/seat/pulse.py` finds pulse.py:114 "STANDING", which loses tick and roster in P2.
- `seat_of` routes by the oldest verdict only.

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
  - an opener's fourth failure gives STUCK.
- Each planted case first fails against an empty jobs directory.

**A scrubbed recorded board** under tools/audit/seat/fixtures/ reproduces the stand-in's actionable set.

**`pulse.py --self-test`:**
- A blocked verdict older than a merge verdict names both PRs and both seats.
- Null: one verdict prints one line.
- Killed: the oldest-only mutant.

**`sweep_render.py` fixture:**
- Every rendered `git ` carries `-C`.
- Step (5) names the digest and both counts.
- No `tick-owed` remains.
- Mutants: drop `-C`; restore "newest actionable lines".

**tests/entities.py, one new check:**
- Every standing-*.md and proposal-triage.md cites standing.md.
- standing.md has its four headings.
- Deleting any one turns the check red. The null control is the edited tree, which passes.

**Hooks (P3):**
- A planted dead job prints DEAD; a stale digest prints STALE.
- On a throwaway HOME, `--check` lists every hook, then none after `--install`.
- A second `--install` changes no byte.
- A mutant that drops the backup or rewrites an unrelated entry is killed.

**Goldens and claim files:** none move.

## 6. Parts, policy, budget, hot files

**P1 (code).**
- New: the script, the job table, its instruments entry and the fixture.
- Edits:
  - `pulse.py` (carry 6);
  - `INSTRUMENTS.md`;
  - `sweep_template.md`: steps (2), (4b), (4e), (5) and (8) read the digest; (1b) and the tick restart stay;
  - the `sweep_render.py` fixture.

**P2 (policy).**
- Gate: P1 has merged, and `beatd status` has shown every P1 row `ok` from main for one cycle beside the live seats. This is what "live and verified" means here.
- New: standing.md.
- Contract edits:
  - tick and roster become retirement stubs;
  - merge takes carries 5 and 9 inside its cap;
  - dispatch cites the hold and pays for it by replacing its `git ls-remote` block with `bus.sh orphans` (P95).
- Other edits:
  - `orchestrator.md` §5;
  - the CLAUDE.md index (the two retired rows merge into one);
  - proposal-triage.md's opener;
  - policy_budgets.json;
  - `pulse.py`'s STANDING;
  - (1b), the tick restart and the placeholders in `sweep_template.md`.

**P3 (hooks, after P1).**
- New: user-level hook scripts under tools/audit/seat/hooks/; one setup script under tools/audit/seat/ with `--check`, `--install` and `--self-test` (under `offline_spy.py`); a hooks entry under tools/audit/seat/instruments/.
- The SessionStart and PostCompact liveness hook runs `policy_reread_check.py`, then prints:
  - `beatd.py status` (the loop list is the job table);
  - fresh or STALE for each alive file and for the digest;
  - the digest;
  - the line that re-arms the wake.
- The git-identity and seat-interpreter hooks are host-specific, so user-level. The seat-interpreter hook checks against seat_venv.sh.
- The main-checkout Bash guard binds every session, so it is project-level. It belongs in R10-BASH-KILL-HOOK's `.claude/settings.json`, and that group adds its hook to this installer.
- Paths come from `$HPO_STATE_DIR`, so `tmp_paths.py` and `ref_privacy.py` pass.

**P4:** carry 19, once #3061 merges.

**Policy files**, all in P2, under mandate 6329234399 or the owner's review: standing.md, the four standing-*.md, proposal-triage.md, orchestrator.md and CLAUDE.md.

**Budget:**
- standing.md's new cap is a raise under budget_raise_gate.py's `capfile` rule.
- It is paid by the three lowered caps, so the corpus falls. P2's `## Raise justification` says so.
- No structure_budgets metric moves.

**Closure:** every new file sits under an INERT prefix: tools/audit/ (tests/closure.py:296 "tools/audit/") or dev/governance/ (:273). tests/closures.json is re-derived for the new entities check.

**Hot files:**
- `sweep_template.md`: shared with R10-SEAT-SINGLE-WRITER and R10-BEAT-JOB-TABLE.
- standing-dispatch.md: shared with R10-TICK-PR-BUCKETS and R10-DISPATCH-AT-HANDOFF.
- `orchestrator.md`: shared with R10-FLY-RAISE-REVIEWABLE, which is in progress.
- `worktree_gc.sh` (R10-CLOSEOUT-CLEANUP): only called here.
- `decision: orchestrator`: add `after` edges to this group from R10-DISPATCH-AT-HANDOFF and R10-SEAT-SINGLE-WRITER, or the later group of each pair rebases.

## 7. Carries (all 22)

**`decision: owner`:** carry 1 wants a copy in each contract; this note writes it once (§3), ruled at P2. Carry: R10-FLY-STANDING-CONTRACTS (item 1)

- Carry: R10-FLY-STANDING-CONTRACTS (item 1): P51's Wait term goes in standing.md (P2). The loop writes the seat's pid to the alive file and exits when that pid dies (gap 3).
- Carry: R10-FLY-STANDING-CONTRACTS (item 2): P95's Reads term goes in standing.md (P2).
- Carry: R10-FLY-STANDING-CONTRACTS (item 3): the autofix hold goes in standing.md's Reads (P2). bus.sh's refusal stays with R10-DISPATCH-AT-HANDOFF.
- Carry: R10-FLY-STANDING-CONTRACTS (item 4): the Recycle term goes in standing.md and §5 (P2), making tvofi's "Make that rule persistent" hold. During a recycle, work goes only to the incoming seat after HANDED (gap 5).
- Carry: R10-FLY-STANDING-CONTRACTS (item 5): standing-merge.md:9 "merge_pr.sh" gives way to the train route (P2).
- Carry: R10-FLY-STANDING-CONTRACTS (item 6): `pulse.py` names every owed verdict (P1).
- Carry: R10-FLY-STANDING-CONTRACTS (item 7): step (2) gets `-C` (P1).
- Carry: R10-FLY-STANDING-CONTRACTS (item 8): step (5) reads the digest and prints both counts (P1).
- Carry: R10-FLY-STANDING-CONTRACTS (item 9): `train.sh add` joins the live train (P2).
- Carry: R10-FLY-STANDING-CONTRACTS (items 10, 11): the orchestrator reads only the plan page and the digest, stated in one line of §5 (P2). R10-ORCH-PLANPAGE is done.
- Carry: R10-BEAT-JOB-TABLE (item 12): merge-seat retirement and the pitch job are that group's. Merge stays an LLM seat here.
- Carry: R10-FLY-STANDING-CONTRACTS (items 13, 14): roster-drain is built in P1. The roster seat retires in P2, after the scratch-branch acceptance.
- Carry: R10-BEAT-JOB-TABLE (items 15, 16, 17): the dispatch job (`bus.sh dispatch-owed`). The opener half is built here (P1). `decision: owner`: carry 22 keeps dispatch briefs as LLM work.
- Carry: R10-FLY-STANDING-CONTRACTS (item 18): steps (2), (4b), (4e) and (8) are built here (P1). Carry: R10-BEAT-JOB-TABLE (item 18) for steps (3) and (6).
- Carry: R10-FLY-STANDING-CONTRACTS (item 19): P4, with its harness under dev/audit/harnesses/.
- Carry: R10-FLY-STANDING-CONTRACTS (item 20): this carries tvofi's "folding every useful standing loop into the orchestrator machinery on main".
  - Part (1) is the P1 rows: the triage pass and merge watch loops become Wait loops; tick_loop.sh, cloud_relay.sh and state_docs.py are kept as is.
  - Part (2) is P3.
- Carry: R10-FLY-STANDING-CONTRACTS (item 21): tvofi's "tick seat ... replaced by a script within the sweep" is tick-digest (P1); the seat retires in P2.
- Carry: R10-FLY-STANDING-CONTRACTS (item 22): on tvofi's "necessary LLM tasks", the mechanical work is the P1 rows; dispatch, triage and merge stay LLM seats.

## Notes for the fixer

- Carry: R10-FLY-STANDING-CONTRACTS (item 20): STEP 1's review comes first. It has one row per loop and per gap 1 to 6, each judged from its log. Get the stand-ins' paths from the orchestrator, and cite none of them in tracked text.
- Carry: R10-ROSTER-QUEUE (item 13): if exact-line marking lands in `roster_queue.py` first, roster-drain calls it and deletes its own marker.
- Carry: R10-FLY-STANDING-CONTRACTS (item 21): `tick_alive` and `tick_stale_min` leave the placeholder table in P2, not P1.
